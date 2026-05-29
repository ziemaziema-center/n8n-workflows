from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("TAC_ROOT", Path(__file__).resolve().parents[1]))
DEFAULT_TELEMETRY_PATH = ROOT / "runtime" / "telemetry" / "events.jsonl"
ALLOWED_EVENT_TYPES = {
    "task_enqueued",
    "task_claimed",
    "task_started",
    "task_heartbeat",
    "task_validation_pass",
    "task_validation_fail",
    "task_deferred_gate",
    "task_safe_fallback",
    "task_auto_repair",
    "task_completed",
    "runner_recovered",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def telemetry_event(
    *,
    event_type: str,
    task_id: str | None,
    phase: str,
    status: str,
    message: str,
    artifacts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"unsupported telemetry event_type: {event_type}")
    return {
        "event_type": event_type,
        "timestamp": utc_now(),
        "task_id": task_id,
        "phase": phase,
        "status": status,
        "message": message,
        "artifacts": artifacts or {},
        "live_operations_performed": False,
        "secret_values_included": False,
    }


def append_event(path: Path = DEFAULT_TELEMETRY_PATH, **kwargs: Any) -> dict[str, Any]:
    event = telemetry_event(**kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def read_events(path: Path = DEFAULT_TELEMETRY_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Append TAC runtime telemetry events.")
    parser.add_argument("--event-type", default="task_heartbeat")
    parser.add_argument("--task-id")
    parser.add_argument("--phase", default="manual")
    parser.add_argument("--status", default="INFO")
    parser.add_argument("--message", default="manual telemetry event")
    parser.add_argument("--path", type=Path, default=DEFAULT_TELEMETRY_PATH)
    args = parser.parse_args()
    event = append_event(
        args.path,
        event_type=args.event_type,
        task_id=args.task_id,
        phase=args.phase,
        status=args.status,
        message=args.message,
        artifacts={},
    )
    print(json.dumps({"status": "PASS", "event": event, "path": str(args.path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
