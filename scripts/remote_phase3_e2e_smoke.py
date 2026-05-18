from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/ubuntu/workspace/true-autonomous-controller")
TASK_ID = "hq-phase3-e2e-smoke-20260518"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=check)


def ensure_dirs() -> None:
    for rel in ("runtime/queue", "runtime/logs", "runtime/reports", "runtime/reviewer_feedback", "runtime/state", "runtime/handoff"):
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def task_payload() -> dict:
    return {
        "task_id": TASK_ID,
        "created_at": utc_now(),
        "requested_by": "phase3_e2e_smoke",
        "source_channel": "n8n_webhook",
        "priority": "normal",
        "objective": "Phase 3 dry-run E2E smoke: queue -> tmux -> wrapper -> reviewer -> report.",
        "allowed_scope": ["local_files", "dry_run", "no_secrets", "no_production_mutation"],
        "deferred_gates": [],
        "target_runner": "dry_run",
        "tmux_session": "tac-phase3-e2e-smoke",
        "workspace_path": str(ROOT),
        "validation_commands": ["python3 --version"],
        "expected_artifacts": [
            f"runtime/logs/{TASK_ID}.log",
            f"runtime/reviewer_feedback/{TASK_ID}.json",
            f"runtime/reports/{TASK_ID}.md",
        ],
        "status": "QUEUED",
        "retry_count": 0,
        "max_retries": 3,
        "continuation_ledger_path": "reports/hq_continuation_ledger_2026-05-18.json",
        "final_report_path": f"runtime/reports/{TASK_ID}.md",
    }


def write_queue(task: dict) -> Path:
    queue_path = ROOT / "runtime/queue/phase3_e2e_pending.jsonl"
    queue_path.write_text(json.dumps(task, sort_keys=True) + "\n", encoding="utf-8")
    return queue_path


def write_runner_script(queue_path: Path) -> Path:
    script = ROOT / "runtime/phase3_e2e_runner.sh"
    script.write_text(
        f"""#!/usr/bin/env bash
set -euo pipefail
cd {ROOT}
TASK_LINE="$(head -n 1 {queue_path})"
TASK_ID="$(printf '%s' "$TASK_LINE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["task_id"])')"
LOG="runtime/logs/${{TASK_ID}}.log"
REVIEW="runtime/reviewer_feedback/${{TASK_ID}}.json"
REPORT="runtime/reports/${{TASK_ID}}.md"
STATE="runtime/state/phase3_e2e_state.json"
printf '%s\\n' "$TASK_LINE" > "runtime/queue/${{TASK_ID}}.json"
python3 - <<'PY' "$STATE" "$TASK_ID" "$LOG"
import json, sys, datetime
path, task_id, log = sys.argv[1:]
json.dump({{"active_task_id": task_id, "runner_status": "RUNNING", "current_phase": "wrapper", "last_heartbeat_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "last_log_path": log, "last_validation_result": {{"status": "NOT_RUN", "command": None, "checked_at": None}}, "blocked_gates": [], "safe_next_actions": ["run reviewer"], "kill_switch_status": {{"enabled": True, "last_triggered_at": None, "command": "/killall"}}}}, open(path, "w"), indent=2)
PY
bash scripts/hq_safe_agent_wrapper_template.sh "$TASK_LINE" > "$LOG" 2>&1
python3 scripts/hq_reviewer_loop_template.py "$LOG" "$REVIEW" 3 0
DECISION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["decision"])' "$REVIEW")"
cat > "$REPORT" <<EOF
# Phase 3 E2E Smoke Report

- task_id: $TASK_ID
- decision: $DECISION
- log_path: $LOG
- reviewer_feedback: $REVIEW
- live_operation: false
EOF
python3 - <<'PY' "$STATE" "$TASK_ID" "$LOG" "$REVIEW" "$DECISION"
import json, sys, datetime
path, task_id, log, review, decision = sys.argv[1:]
json.dump({{"active_task_id": None, "runner_status": "IDLE", "current_phase": "reported", "last_heartbeat_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "last_log_path": log, "last_validation_result": {{"status": decision, "command": "phase3_e2e_runner", "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}}, "blocked_gates": [], "safe_next_actions": ["send Telegram summary"], "kill_switch_status": {{"enabled": True, "last_triggered_at": None, "command": "/killall"}}}}, open(path, "w"), indent=2)
PY
cat > runtime/handoff/phase3_e2e_latest.json <<EOF
{{"task_id":"$TASK_ID","report_path":"$REPORT","log_path":"$LOG","review_path":"$REVIEW","decision":"$DECISION"}}
EOF
""",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def tmux_run(script: Path) -> dict:
    session = "tac-phase3-e2e-smoke"
    run(["tmux", "kill-session", "-t", session], check=False)
    run(["tmux", "new-session", "-d", "-s", session, "bash", str(script)])
    handoff = ROOT / "runtime/handoff/phase3_e2e_latest.json"
    for _ in range(60):
        if handoff.exists():
            payload = json.loads(handoff.read_text(encoding="utf-8"))
            run(["tmux", "kill-session", "-t", session], check=False)
            return {"tmux_phase3_e2e": "PASS", **payload, "left_running": False}
        time.sleep(1)
    run(["tmux", "kill-session", "-t", session], check=False)
    return {"tmux_phase3_e2e": "FAIL", "reason": "handoff timeout", "left_running": False}


def main() -> int:
    ensure_dirs()
    task = task_payload()
    queue_path = write_queue(task)
    script = write_runner_script(queue_path)
    result = {
        "root": str(ROOT),
        "queue_path": str(queue_path),
        "runner_script": str(script),
        **tmux_run(script),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("tmux_phase3_e2e") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
