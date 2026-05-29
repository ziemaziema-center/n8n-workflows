from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("TAC_ROOT", Path(__file__).resolve().parents[1]))
QUEUE_ROOT = ROOT / "runtime" / "queue"
HISTORY_PATH = QUEUE_ROOT / "history.jsonl"
PENDING_PATH = QUEUE_ROOT / "pending.json"
RUNNING_PATH = QUEUE_ROOT / "running.json"
DONE_PATH = QUEUE_ROOT / "done.json"
FAILED_PATH = QUEUE_ROOT / "failed.json"
DEFERRED_PATH = QUEUE_ROOT / "deferred.json"
VALID_STATUSES = {"QUEUED", "RUNNING", "PASS", "FAIL", "DEFERRED_GATE", "PASS_WITH_SAFE_FALLBACK", "PASS_WITH_AUTO_REPAIR"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, payload: Any) -> None:
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


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        atomic_write_json(path, default)
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def queue_paths(queue_root: Path = QUEUE_ROOT) -> dict[str, Path]:
    return {
        "pending": queue_root / "pending.json",
        "running": queue_root / "running.json",
        "done": queue_root / "done.json",
        "failed": queue_root / "failed.json",
        "deferred": queue_root / "deferred.json",
        "history": queue_root / "history.jsonl",
    }


def ensure_queue(queue_root: Path = QUEUE_ROOT) -> dict[str, str]:
    queue_root.mkdir(parents=True, exist_ok=True)
    for name, path in queue_paths(queue_root).items():
        if name == "history":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
        else:
            read_json(path, [])
    return {name: str(path) for name, path in queue_paths(queue_root).items()}


def append_history(event: dict[str, Any], queue_root: Path = QUEUE_ROOT) -> None:
    path = queue_paths(queue_root)["history"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def normalize_task(task: dict[str, Any]) -> dict[str, Any]:
    if "task_id" not in task or not str(task["task_id"]).strip():
        raise ValueError("task_id is required")
    if str(task.get("workspace_path", "")).strip() and not str(task["workspace_path"]).startswith("/home/ubuntu/workspace/"):
        raise ValueError("workspace_path must stay under /home/ubuntu/workspace/")
    normalized = {
        "task_id": str(task["task_id"]),
        "created_at": task.get("created_at") or utc_now(),
        "objective": str(task.get("objective") or "Runtime persistence task"),
        "status": task.get("status") or "QUEUED",
        "retry_count": int(task.get("retry_count", 0)),
        "max_retries": int(task.get("max_retries", 3)),
        "priority": task.get("priority") or "normal",
        "workspace_path": task.get("workspace_path") or "/home/ubuntu/workspace/true-autonomous-controller",
        "deferred_gates": task.get("deferred_gates") or [],
        "history": task.get("history") or [],
        "updated_at": utc_now(),
    }
    if normalized["status"] not in VALID_STATUSES:
        raise ValueError(f"unsupported queue status: {normalized['status']}")
    return {**task, **normalized}


def all_known_task_ids(queue_root: Path = QUEUE_ROOT) -> set[str]:
    ids: set[str] = set()
    ensure_queue(queue_root)
    for name, path in queue_paths(queue_root).items():
        if name == "history":
            continue
        for task in read_json(path, []):
            if isinstance(task, dict) and task.get("task_id"):
                ids.add(str(task["task_id"]))
    return ids


def enqueue_task(task: dict[str, Any], queue_root: Path = QUEUE_ROOT) -> dict[str, Any]:
    ensure_queue(queue_root)
    normalized = normalize_task(task)
    if normalized["task_id"] in all_known_task_ids(queue_root):
        return {"status": "DUPLICATE", "task": normalized, "queue_path": str(queue_paths(queue_root)["pending"])}
    pending = read_json(queue_paths(queue_root)["pending"], [])
    pending.append(normalized)
    atomic_write_json(queue_paths(queue_root)["pending"], pending)
    append_history({"event": "task_enqueued", "task_id": normalized["task_id"], "at": utc_now()}, queue_root)
    return {"status": "QUEUED", "task": normalized, "queue_path": str(queue_paths(queue_root)["pending"])}


def list_pending(queue_root: Path = QUEUE_ROOT) -> list[dict[str, Any]]:
    ensure_queue(queue_root)
    return read_json(queue_paths(queue_root)["pending"], [])


def claim_next_task(queue_root: Path = QUEUE_ROOT) -> dict[str, Any] | None:
    ensure_queue(queue_root)
    paths = queue_paths(queue_root)
    pending = read_json(paths["pending"], [])
    if not pending:
        return None
    task = pending.pop(0)
    task = normalize_task({**task, "status": "RUNNING", "claimed_at": utc_now(), "updated_at": utc_now()})
    running = read_json(paths["running"], [])
    running.append(task)
    atomic_write_json(paths["pending"], pending)
    atomic_write_json(paths["running"], running)
    append_history({"event": "task_claimed", "task_id": task["task_id"], "at": utc_now()}, queue_root)
    return task


def _remove_from_list(path: Path, task_id: str) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    tasks = read_json(path, [])
    remaining: list[dict[str, Any]] = []
    found: dict[str, Any] | None = None
    for task in tasks:
        if isinstance(task, dict) and str(task.get("task_id")) == task_id and found is None:
            found = task
        else:
            remaining.append(task)
    return remaining, found


def mark_task(task_id: str, status: str, queue_root: Path = QUEUE_ROOT, reason: str = "") -> dict[str, Any]:
    if status not in {"PASS", "FAIL", "DEFERRED_GATE", "PASS_WITH_SAFE_FALLBACK", "PASS_WITH_AUTO_REPAIR"}:
        raise ValueError(f"unsupported final status: {status}")
    ensure_queue(queue_root)
    paths = queue_paths(queue_root)
    running, task = _remove_from_list(paths["running"], task_id)
    if task is None:
        pending, task = _remove_from_list(paths["pending"], task_id)
        atomic_write_json(paths["pending"], pending)
    if task is None:
        task = {"task_id": task_id, "objective": "Recovered task record", "retry_count": 0, "max_retries": 3}
    task = normalize_task({**task, "status": status, "finished_at": utc_now(), "updated_at": utc_now()})
    if reason:
        task["reason"] = reason
    atomic_write_json(paths["running"], running)
    target_path = paths["done"] if status in {"PASS", "PASS_WITH_SAFE_FALLBACK", "PASS_WITH_AUTO_REPAIR"} else paths["deferred"] if status == "DEFERRED_GATE" else paths["failed"]
    completed = read_json(target_path, [])
    completed.append(task)
    atomic_write_json(target_path, completed)
    append_history({"event": f"task_{status.lower()}", "task_id": task_id, "at": utc_now(), "reason": reason}, queue_root)
    return task


def increment_retry(task_id: str, queue_root: Path = QUEUE_ROOT) -> dict[str, Any]:
    ensure_queue(queue_root)
    paths = queue_paths(queue_root)
    running, task = _remove_from_list(paths["running"], task_id)
    if task is None:
        raise KeyError(f"running task not found: {task_id}")
    task = normalize_task({**task, "retry_count": int(task.get("retry_count", 0)) + 1, "status": "QUEUED"})
    pending = read_json(paths["pending"], [])
    pending.append(task)
    atomic_write_json(paths["running"], running)
    atomic_write_json(paths["pending"], pending)
    append_history({"event": "task_retry_incremented", "task_id": task_id, "retry_count": task["retry_count"], "at": utc_now()}, queue_root)
    return task


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage TAC runtime queue persistence.")
    parser.add_argument("--queue-root", type=Path, default=QUEUE_ROOT)
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    paths = ensure_queue(args.queue_root)
    print(json.dumps({"status": "PASS", "paths": paths}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
