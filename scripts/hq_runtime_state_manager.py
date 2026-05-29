from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("TAC_ROOT", Path(__file__).resolve().parents[1]))
DEFAULT_STATE_PATH = ROOT / "runtime" / "state" / "current_state.json"
VALID_TASK_STATUSES = {"PASS", "FAIL", "DEFERRED_GATE", "PASS_WITH_SAFE_FALLBACK", "PASS_WITH_AUTO_REPAIR"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def runtime_dirs(root: Path = ROOT) -> dict[str, Path]:
    runtime_root = root / "runtime"
    return {
        "runtime": runtime_root,
        "queue": runtime_root / "queue",
        "state": runtime_root / "state",
        "logs": runtime_root / "logs",
        "reports": runtime_root / "reports",
        "telemetry": runtime_root / "telemetry",
        "handoff": runtime_root / "handoff",
        "locks": runtime_root / "locks",
    }


def ensure_runtime_dirs(root: Path = ROOT) -> dict[str, str]:
    dirs = runtime_dirs(root)
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return {name: str(path) for name, path in dirs.items()}


def default_state() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "active_task_id": None,
        "runner_status": "IDLE",
        "current_phase": "idle",
        "retry_count": 0,
        "last_heartbeat_at": None,
        "last_log_path": None,
        "last_validation_result": {"status": "NOT_RUN", "command": None, "checked_at": None},
        "blocked_gates": [],
        "safe_next_actions": ["claim next queued task"],
        "kill_switch_status": {"enabled": True, "last_triggered_at": None, "command": "/killall"},
        "last_task_status": None,
        "updated_at": utc_now(),
        "recovered_from_corrupt_state": False,
        "live_operations_performed": False,
        "secret_values_included": False,
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_name, path)
    finally:
        tmp_path = Path(tmp_name)
        if tmp_path.exists():
            tmp_path.unlink()


def backup_corrupt_state(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup = path.with_suffix(path.suffix + f".corrupt.{utc_now().replace(':', '').replace('+', 'Z')}.bak")
    shutil.copy2(path, backup)
    return backup


def load_state(path: Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        state = default_state()
        atomic_write_json(path, state)
        return state
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("state root is not an object")
        state = {**default_state(), **loaded}
        return state
    except (json.JSONDecodeError, OSError, ValueError):
        backup = backup_corrupt_state(path)
        state = default_state()
        state["recovered_from_corrupt_state"] = True
        state["corrupt_state_backup_path"] = str(backup) if backup else None
        atomic_write_json(path, state)
        return state


def save_state(state: dict[str, Any], path: Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    updated = {**state, "updated_at": utc_now(), "live_operations_performed": False, "secret_values_included": False}
    atomic_write_json(path, updated)
    return updated


def update_state(path: Path = DEFAULT_STATE_PATH, **changes: Any) -> dict[str, Any]:
    state = load_state(path)
    state.update(changes)
    return save_state(state, path)


def heartbeat(
    *,
    task_id: str | None,
    runner_status: str,
    phase: str,
    log_path: str | None = None,
    state_path: Path = DEFAULT_STATE_PATH,
) -> dict[str, Any]:
    return update_state(
        state_path,
        active_task_id=task_id,
        runner_status=runner_status,
        current_phase=phase,
        last_heartbeat_at=utc_now(),
        last_log_path=log_path,
    )


def mark_task_status(
    *,
    task_id: str,
    status: str,
    validation_result: dict[str, Any] | None = None,
    blocked_gates: list[dict[str, Any]] | None = None,
    safe_next_actions: list[str] | None = None,
    retry_count: int | None = None,
    state_path: Path = DEFAULT_STATE_PATH,
) -> dict[str, Any]:
    if status not in VALID_TASK_STATUSES:
        raise ValueError(f"unsupported task status: {status}")
    runner_status = "IDLE" if status in {"PASS", "PASS_WITH_SAFE_FALLBACK", "PASS_WITH_AUTO_REPAIR"} else "ERROR"
    return update_state(
        state_path,
        active_task_id=None if runner_status == "IDLE" else task_id,
        runner_status=runner_status,
        current_phase=f"task_{status.lower()}",
        retry_count=retry_count if retry_count is not None else load_state(state_path).get("retry_count", 0),
        last_validation_result=validation_result
        or {"status": "NOT_RUN", "command": None, "checked_at": None},
        blocked_gates=blocked_gates or [],
        safe_next_actions=safe_next_actions or ["claim next queued task"],
        last_task_status=status,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage TAC runtime state.")
    parser.add_argument("--state-path", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    ensure_runtime_dirs(ROOT)
    state = load_state(args.state_path)
    if args.init:
        state = save_state(state, args.state_path)
    print(json.dumps({"status": "PASS", "state_path": str(args.state_path), "state": state}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
