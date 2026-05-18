from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_queue_task(
    *,
    task_id: str,
    objective: str,
    requested_by: str = "telegram",
    source_channel: str = "telegram",
    workspace_path: str = "/home/ubuntu/workspace/true-autonomous-controller",
    priority: str = "normal",
    target_runner: str = "codex",
    notification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not workspace_path.startswith("/home/ubuntu/workspace/"):
        raise ValueError("workspace_path must stay under /home/ubuntu/workspace/")
    return {
        "task_id": task_id,
        "created_at": utc_now(),
        "requested_by": requested_by,
        "source_channel": source_channel,
        "priority": priority,
        "objective": objective.strip() or "Queued TAC runtime task.",
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
                "name": "production_activation",
                "reason": "Queue task stays bounded until production route promotion is approved.",
                "required_approval": "Explicit production route promotion approval.",
            }
        ],
        "target_runner": target_runner,
        "tmux_session": "tac-hq-runner",
        "workspace_path": workspace_path,
        "validation_commands": [
            "python -m unittest discover -s tests",
            "python scripts/run_offline_validations.py",
        ],
        "expected_artifacts": ["runtime/queue", "runtime/reviewer_feedback", "runtime/reports"],
        "status": "QUEUED",
        "retry_count": 0,
        "max_retries": 3,
        "continuation_ledger_path": "reports/hq_continuation_ledger_2026-05-18.json",
        "final_report_path": "reports/phase4_runtime_operating_report_2026-05-18.md",
        "notification": notification or {"on_completion": False},
    }


def validate_queue_task(task: dict[str, Any]) -> None:
    required = {
        "task_id",
        "created_at",
        "requested_by",
        "source_channel",
        "priority",
        "objective",
        "allowed_scope",
        "deferred_gates",
        "target_runner",
        "tmux_session",
        "workspace_path",
        "validation_commands",
        "expected_artifacts",
        "status",
        "retry_count",
        "max_retries",
        "continuation_ledger_path",
        "final_report_path",
        "notification",
    }
    missing = sorted(required - set(task))
    if missing:
        raise ValueError(f"missing queue task fields: {missing}")
    if not str(task["workspace_path"]).startswith("/home/ubuntu/workspace/"):
        raise ValueError("workspace_path must stay under /home/ubuntu/workspace/")
    if "no_secrets" not in task["allowed_scope"]:
        raise ValueError("allowed_scope must include no_secrets")
    if "no_production_mutation" not in task["allowed_scope"]:
        raise ValueError("allowed_scope must include no_production_mutation")
    if int(task["retry_count"]) > int(task["max_retries"]):
        raise ValueError("retry_count cannot exceed max_retries")
    notification = task.get("notification")
    if not isinstance(notification, dict):
        raise ValueError("notification must be an object")
    if notification.get("on_completion") and not notification.get("chat_id"):
        raise ValueError("completion notification requires chat_id")


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


def write_queue_task(task: dict[str, Any], *, runtime_root: Path) -> dict[str, Any]:
    validate_queue_task(task)
    queue_dir = runtime_root / "queue"
    queue_dir.mkdir(parents=True, exist_ok=True)
    db_path = runtime_root / "controller_state.sqlite3"
    task_path = queue_dir / f"{task['task_id']}.json"
    pending_path = queue_dir / "pending.jsonl"
    task_line = json.dumps(task, ensure_ascii=False, sort_keys=True)
    task_path.write_text(json.dumps(task, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    with pending_path.open("a", encoding="utf-8") as handle:
        handle.write(task_line + "\n")
    conn = sqlite3.connect(db_path)
    try:
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
                task["created_at"],
                task["objective"],
                "bounded_queue",
                json.dumps({"safe_runtime_queue_approved": True}, sort_keys=True),
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
                "tac_service_queue_endpoint",
                "validated task and appended to runtime queue",
                json.dumps({"pending_jsonl": str(pending_path)}, sort_keys=True),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "ok": True,
        "status": "QUEUED",
        "task_id": task["task_id"],
        "task_path": str(task_path),
        "pending_jsonl": str(pending_path),
        "db_path": str(db_path),
        "live_dispatch_performed": False,
    }
