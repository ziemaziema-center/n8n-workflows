from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tac.queue_runtime import make_queue_task
from src.tac.runtime_engine import (
    append_jsonl,
    build_continuation_handoff,
    record_heartbeat,
    retry_decision,
    runtime_event,
    transition_task,
    write_json,
)


OUT = ROOT / "runtime" / "runtime_engine_smoke_2026-05-19.json"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        task = make_queue_task(
            task_id="hq-runtime-engine-smoke-20260519",
            objective="Validate runtime engine state transitions and telemetry.",
            requested_by="local_hq",
            source_channel="local_hq",
            target_runner="dry_run",
        )
        running = transition_task(task, "RUNNING", actor="runtime_engine_smoke", reason="start bounded task")
        passed = transition_task(running, "PASS", actor="runtime_engine_smoke", reason="validation passed")
        state = {
            "active_task_id": None,
            "runner_status": "IDLE",
            "current_phase": "runtime_engine_smoke",
            "last_heartbeat_at": None,
            "last_log_path": None,
            "last_validation_result": {"status": "NOT_RUN", "command": None, "checked_at": None},
            "blocked_gates": [],
            "safe_next_actions": ["continue queued dry-run work"],
            "kill_switch_status": {"enabled": True, "last_triggered_at": None, "command": "/killall"},
        }
        state = record_heartbeat(
            state,
            runner_status="RUNNING",
            phase="runtime_engine_smoke",
            log_path="runtime/logs/hq-runtime-engine-smoke-20260519.log",
        )
        review = retry_decision(
            {"decision": "FAIL", "retry_allowed": True, "reason": "forced smoke retry"},
            retry_count=0,
            max_retries=3,
        )
        event = runtime_event(
            task_id=task["task_id"],
            event_type="TASK_STARTED",
            actor="runtime_engine_smoke",
            status="RUNNING",
            message="bounded runtime engine smoke started",
        )
        events_path = tmp_root / "runtime_events.jsonl"
        append_jsonl(events_path, event)
        handoff = build_continuation_handoff(
            task_id=task["task_id"],
            completed_items=["runtime engine state transition smoke"],
            deferred_gates=[],
            next_actions=["run long queue soak"],
            validation_commands=["python scripts/runtime_engine_smoke.py"],
            final_report_path="reports/autonomous_runtime_buildout_report_2026-05-19.md",
        )
        result = {
            "status": "PASS",
            "task_status": passed["status"],
            "lifecycle_count": len(passed["lifecycle"]),
            "runner_status": state["runner_status"],
            "retry_next_status": review["next_status"],
            "event_count": len(events_path.read_text(encoding="utf-8").splitlines()),
            "handoff_next_actions": handoff["next_executable_subtasks"],
            "live_operations_performed": False,
        }
    write_json(OUT, result)
    print(json.dumps({"status": result["status"], "out": str(OUT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
