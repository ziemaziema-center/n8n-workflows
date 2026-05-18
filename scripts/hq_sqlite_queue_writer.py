from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "runtime_queue.schema.json"
DEFAULT_DB = ROOT / "runtime" / "controller_state.sqlite3"
DEFAULT_QUEUE_DIR = ROOT / "runtime" / "queue"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_task(task: dict, schema: dict) -> None:
    missing = [key for key in schema["required"] if key not in task]
    if missing:
        raise ValueError(f"missing required queue fields: {missing}")
    props = schema["properties"]
    for field in ("source_channel", "priority", "target_runner", "status"):
        enum = props[field].get("enum")
        if enum and task[field] not in enum:
            raise ValueError(f"{field} not allowed: {task[field]}")
    if not str(task["workspace_path"]).startswith("/home/ubuntu/workspace/"):
        raise ValueError("workspace_path must stay under /home/ubuntu/workspace/")
    if "no_secrets" not in task["allowed_scope"]:
        raise ValueError("allowed_scope must include no_secrets")
    if "no_production_mutation" not in task["allowed_scope"]:
        raise ValueError("allowed_scope must include no_production_mutation")
    if int(task["retry_count"]) > int(task["max_retries"]):
        raise ValueError("retry_count cannot exceed max_retries")


def ensure_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS tasks (
          task_id TEXT PRIMARY KEY,
          source TEXT NOT NULL DEFAULT 'unknown',
          workspace TEXT,
          status TEXT NOT NULL DEFAULT 'RECEIVED',
          requested_at TEXT NOT NULL,
          started_at TEXT,
          finished_at TEXT,
          summary TEXT,
          risk_level TEXT NOT NULL DEFAULT 'bounded',
          approvals_json TEXT NOT NULL DEFAULT '{}',
          metadata_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS task_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          task_id TEXT NOT NULL,
          ts TEXT NOT NULL,
          event_type TEXT NOT NULL,
          actor TEXT NOT NULL,
          message TEXT NOT NULL,
          metadata_json TEXT NOT NULL DEFAULT '{}'
        );
        """
    )


def write_task(task: dict, db_path: Path, queue_dir: Path) -> dict:
    schema = load_json(DEFAULT_SCHEMA)
    validate_task(task, schema)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    queue_dir.mkdir(parents=True, exist_ok=True)
    task_path = queue_dir / f"{task['task_id']}.json"
    pending_path = queue_dir / "pending.jsonl"

    task_text = json.dumps(task, ensure_ascii=False, sort_keys=True)
    task_path.write_text(json.dumps(task, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    with pending_path.open("a", encoding="utf-8") as handle:
        handle.write(task_text + "\n")

    with sqlite3.connect(db_path) as conn:
        ensure_db(conn)
        conn.execute(
            """
            INSERT INTO tasks(task_id, source, workspace, status, requested_at, summary, risk_level, approvals_json, metadata_json)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
              source=excluded.source,
              workspace=excluded.workspace,
              status=excluded.status,
              summary=excluded.summary,
              risk_level=excluded.risk_level,
              metadata_json=excluded.metadata_json
            """,
            (
                task["task_id"],
                task["source_channel"],
                task["workspace_path"],
                task["status"],
                task.get("created_at") or utc_now(),
                task["objective"],
                "bounded_local_orchestration",
                json.dumps({"safe_local_work_approved": True}, sort_keys=True),
                json.dumps({"queue_file": str(task_path), "target_runner": task["target_runner"]}, sort_keys=True),
            ),
        )
        conn.execute(
            """
            INSERT INTO task_events(task_id, ts, event_type, actor, message, metadata_json)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                task["task_id"],
                utc_now(),
                "QUEUED",
                "hq_sqlite_queue_writer",
                "validated queue task and appended to pending queue",
                json.dumps({"pending_jsonl": str(pending_path)}, sort_keys=True),
            ),
        )

    return {
        "ok": True,
        "task_id": task["task_id"],
        "task_path": str(task_path),
        "pending_jsonl": str(pending_path),
        "db_path": str(db_path),
        "live_dispatch_performed": False,
    }


def default_task(task_id: str) -> dict:
    return {
        "task_id": task_id,
        "created_at": utc_now(),
        "requested_by": "local_hq",
        "source_channel": "local_hq",
        "priority": "normal",
        "objective": "Validate SQLite-backed TAC queue writer without live dispatch.",
        "allowed_scope": [
            "local_files",
            "offline_tests",
            "docs",
            "templates",
            "scaffold",
            "dry_run",
            "no_live_network",
            "no_secrets",
            "no_production_mutation",
        ],
        "deferred_gates": [
            {
                "name": "live_ssh_dispatch_test",
                "reason": "Queue writer only creates local queue artifacts.",
                "required_approval": "Explicit live SSH gate approval.",
            }
        ],
        "target_runner": "dry_run",
        "tmux_session": "tac-hq-runner",
        "workspace_path": "/home/ubuntu/workspace/true-autonomous-controller",
        "validation_commands": ["python -m unittest discover -s tests", "python scripts/run_offline_validations.py"],
        "expected_artifacts": ["runtime/queue"],
        "status": "QUEUED",
        "retry_count": 0,
        "max_retries": 3,
        "continuation_ledger_path": "reports/hq_continuation_ledger_2026-05-18.json",
        "final_report_path": "reports/hq_runtime_orchestration_live_gate_report_2026-05-18.md",
        "notification": {
            "on_completion": False,
            "channel": "none",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and enqueue a TAC runtime task.")
    parser.add_argument("--task-json", type=Path)
    parser.add_argument("--task-id", default="hq-local-queue-writer-smoke-20260518")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--queue-dir", type=Path, default=DEFAULT_QUEUE_DIR)
    args = parser.parse_args()

    task = load_json(args.task_json) if args.task_json else default_task(args.task_id)
    result = write_task(task, args.db, args.queue_dir)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
