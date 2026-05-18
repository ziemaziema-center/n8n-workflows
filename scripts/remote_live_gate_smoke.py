from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/ubuntu/workspace/true-autonomous-controller")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def filter_queue(queue: Path) -> int:
    if not queue.exists():
        return 0
    backup = queue.with_name(queue.name + ".bak_20260518_live_gate")
    backup.write_text(queue.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    good: list[str] = []
    bad = 0
    for line in queue.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            json.loads(line)
        except Exception:
            bad += 1
        else:
            good.append(line)
    queue.write_text(("\n".join(good) + "\n") if good else "", encoding="utf-8")
    return bad


def append_queue() -> dict:
    queue_dir = ROOT / "runtime" / "queue"
    queue_dir.mkdir(parents=True, exist_ok=True)
    queue = queue_dir / "pending.jsonl"
    bad_removed = filter_queue(queue)
    task = {
        "task_id": "hq-live-ssh-dispatch-smoke-20260518",
        "created_at": utc_now(),
        "requested_by": "codex_live_gate",
        "source_channel": "manual",
        "priority": "normal",
        "objective": "Live SSH dispatch smoke writes queue item only.",
        "allowed_scope": ["local_files", "dry_run", "no_secrets", "no_production_mutation"],
        "deferred_gates": [
            {
                "name": "production_activation",
                "reason": "smoke only",
                "required_approval": "separate",
            }
        ],
        "target_runner": "dry_run",
        "tmux_session": "tac-live-gate-smoke",
        "workspace_path": str(ROOT),
        "validation_commands": ["echo live ssh dispatch smoke"],
        "expected_artifacts": ["runtime/queue/pending.jsonl"],
        "status": "QUEUED",
        "retry_count": 0,
        "max_retries": 1,
        "continuation_ledger_path": "reports/hq_continuation_ledger_2026-05-18.json",
        "final_report_path": "reports/hq_runtime_orchestration_live_gate_report_2026-05-18.md",
    }
    with queue.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(task, sort_keys=True) + "\n")
    json.loads(queue.read_text(encoding="utf-8").splitlines()[-1])
    return {"queue_append": "PASS", "bad_lines_removed": bad_removed, "queue": str(queue)}


def tmux_smoke() -> dict:
    session = "tac-live-gate-smoke"
    log_dir = ROOT / "runtime" / "logs"
    state_dir = ROOT / "runtime" / "state"
    log_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    marker = log_dir / "tmux_live_gate_smoke.txt"
    subprocess.run(["tmux", "kill-session", "-t", session], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    command = f"date -Iseconds > {marker}; sleep 30"
    subprocess.run(["tmux", "new-session", "-d", "-s", session, "bash", "-lc", command], check=True)
    has_session = subprocess.run(["tmux", "has-session", "-t", session], check=False).returncode == 0
    marker_exists = marker.exists()
    subprocess.run(["tmux", "kill-session", "-t", session], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {
        "tmux_session_creation": "PASS" if has_session and marker_exists else "FAIL",
        "session": session,
        "marker": str(marker),
        "left_running": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["queue", "tmux", "all"])
    args = parser.parse_args()
    result: dict[str, object] = {"root": str(ROOT)}
    if args.action in {"queue", "all"}:
        result.update(append_queue())
    if args.action in {"tmux", "all"}:
        result.update(tmux_smoke())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
