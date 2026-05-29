from __future__ import annotations

import argparse
import json
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.hq_runtime_handoff import build_handoff, write_handoff
from scripts.hq_runtime_queue_manager import claim_next_task, enqueue_task, ensure_queue, mark_task
from scripts.hq_runtime_state_manager import ensure_runtime_dirs, heartbeat, load_state, mark_task_status
from scripts.hq_runtime_telemetry import append_event, read_events


def simulate(root: Path) -> dict[str, object]:
    ensure_runtime_dirs(root)
    queue_root = root / "runtime" / "queue"
    state_path = root / "runtime" / "state" / "current_state.json"
    telemetry_path = root / "runtime" / "telemetry" / "events.jsonl"
    handoff_json = root / "runtime" / "handoff" / "current_handoff.json"
    handoff_md = root / "runtime" / "handoff" / "current_handoff.md"
    ensure_queue(queue_root)
    task = {
        "task_id": "hq-runtime-persistence-sim",
        "objective": "Simulate enqueue, claim, interruption, recovery, handoff, and completion.",
        "workspace_path": "/home/ubuntu/workspace/true-autonomous-controller",
        "deferred_gates": [],
    }
    enqueue = enqueue_task(task, queue_root)
    append_event(
        telemetry_path,
        event_type="task_enqueued",
        task_id=task["task_id"],
        phase="queue",
        status="QUEUED",
        message="simulation enqueued task",
        artifacts={"queue_path": enqueue["queue_path"]},
    )
    claimed = claim_next_task(queue_root)
    if not claimed:
        raise RuntimeError("simulation failed to claim queued task")
    append_event(
        telemetry_path,
        event_type="task_claimed",
        task_id=claimed["task_id"],
        phase="queue",
        status="RUNNING",
        message="simulation claimed task",
        artifacts={},
    )
    heartbeat(
        task_id=claimed["task_id"],
        runner_status="RUNNING",
        phase="simulate_interruption",
        log_path=str(root / "runtime" / "logs" / "hq-runtime-persistence-sim.log"),
        state_path=state_path,
    )
    reloaded = load_state(state_path)
    handoff = build_handoff(
        active_task=claimed,
        completed_items=["enqueued task", "claimed task", "persisted running heartbeat", "reloaded state after simulated interruption"],
        pending_items=["mark completed"],
        deferred_gates=[],
        last_validation_result={"status": "NOT_RUN", "command": None, "checked_at": None},
        next_executable_actions=["mark recovered task completed"],
        exact_resume_prompt="Continue hq-runtime-persistence-sim from runtime/state/current_state.json.",
    )
    handoff_paths = write_handoff(handoff, json_path=handoff_json, md_path=handoff_md)
    completed = mark_task(claimed["task_id"], "PASS", queue_root, reason="simulation completed after recovery")
    mark_task_status(
        task_id=claimed["task_id"],
        status="PASS",
        validation_result={"status": "PASS", "command": "python scripts/simulate_runtime_persistence.py", "checked_at": None},
        blocked_gates=[],
        safe_next_actions=["claim next queued task"],
        retry_count=0,
        state_path=state_path,
    )
    append_event(
        telemetry_path,
        event_type="task_completed",
        task_id=claimed["task_id"],
        phase="simulation",
        status="PASS",
        message="simulation completed task after recovery",
        artifacts=handoff_paths,
    )
    return {
        "status": "PASS",
        "root": str(root),
        "active_task_before_completion": reloaded["active_task_id"],
        "completed_task_status": completed["status"],
        "state_path": str(state_path),
        "queue_path": str(queue_root / "pending.json"),
        "telemetry_path": str(telemetry_path),
        "handoff_path": handoff_paths["handoff_json_path"],
        "event_count": len(read_events(telemetry_path)),
        "live_operations_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate TAC runtime persistence and restart recovery.")
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if args.root:
        result = simulate(args.root)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            result = simulate(Path(tmp))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
