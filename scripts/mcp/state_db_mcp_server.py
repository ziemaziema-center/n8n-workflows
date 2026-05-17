#!/usr/bin/env python3
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


ROOT = Path(os.environ.get("TAC_STATE_ROOT", Path.cwd())).resolve()
DB_PATH = Path(os.environ.get("TAC_STATE_DB", ROOT / "runtime" / "controller_state.sqlite3")).resolve()


def ensure_inside_root(path):
    resolved = Path(path).resolve()
    if resolved != ROOT and ROOT not in resolved.parents:
        raise ValueError(f"path outside TAC_STATE_ROOT: {resolved}")
    return resolved


def connect():
    ensure_inside_root(DB_PATH)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.executescript(
            """
            PRAGMA journal_mode=WAL;
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
              metadata_json TEXT NOT NULL DEFAULT '{}',
              FOREIGN KEY(task_id) REFERENCES tasks(task_id)
            );
            CREATE INDEX IF NOT EXISTS idx_task_events_task_ts ON task_events(task_id, ts);
            CREATE TABLE IF NOT EXISTS artifacts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              task_id TEXT NOT NULL,
              path TEXT NOT NULL,
              artifact_type TEXT NOT NULL DEFAULT 'file',
              sha256 TEXT,
              created_at TEXT NOT NULL,
              metadata_json TEXT NOT NULL DEFAULT '{}',
              FOREIGN KEY(task_id) REFERENCES tasks(task_id)
            );
            CREATE INDEX IF NOT EXISTS idx_artifacts_task ON artifacts(task_id);
            CREATE TABLE IF NOT EXISTS telemetry (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts TEXT NOT NULL,
              severity TEXT NOT NULL,
              category TEXT NOT NULL,
              message TEXT NOT NULL,
              metadata_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry(ts);
            """
        )
    return {"ok": True, "db_path": str(DB_PATH)}


def json_text(value):
    return json.dumps(value if value is not None else {}, ensure_ascii=False, sort_keys=True)


def row_to_dict(row):
    return dict(row) if row else None


def record_task(args):
    init_db()
    task_id = str(args["task_id"]).strip()
    if not task_id:
        raise ValueError("task_id is required")
    now = utc_now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO tasks(task_id, source, workspace, status, requested_at, started_at, finished_at, summary, risk_level, approvals_json, metadata_json)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
              source=excluded.source,
              workspace=excluded.workspace,
              status=excluded.status,
              started_at=COALESCE(excluded.started_at, tasks.started_at),
              finished_at=COALESCE(excluded.finished_at, tasks.finished_at),
              summary=COALESCE(excluded.summary, tasks.summary),
              risk_level=excluded.risk_level,
              approvals_json=excluded.approvals_json,
              metadata_json=excluded.metadata_json
            """,
            (
                task_id,
                str(args.get("source", "unknown")),
                args.get("workspace"),
                str(args.get("status", "RECEIVED")),
                str(args.get("requested_at", now)),
                args.get("started_at"),
                args.get("finished_at"),
                args.get("summary"),
                str(args.get("risk_level", "bounded")),
                json_text(args.get("approvals")),
                json_text(args.get("metadata")),
            ),
        )
    return {"ok": True, "task_id": task_id}


def record_event(args):
    init_db()
    task_id = str(args["task_id"]).strip()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO task_events(task_id, ts, event_type, actor, message, metadata_json)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                str(args.get("ts", utc_now())),
                str(args.get("event_type", "NOTE")),
                str(args.get("actor", "controller")),
                str(args.get("message", "")),
                json_text(args.get("metadata")),
            ),
        )
    return {"ok": True, "task_id": task_id}


def get_task(args):
    init_db()
    task_id = str(args["task_id"]).strip()
    with connect() as conn:
        task = row_to_dict(conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone())
        events = [dict(row) for row in conn.execute("SELECT * FROM task_events WHERE task_id = ? ORDER BY ts, id", (task_id,))]
        artifacts = [dict(row) for row in conn.execute("SELECT * FROM artifacts WHERE task_id = ? ORDER BY created_at, id", (task_id,))]
    return {"task": task, "events": events, "artifacts": artifacts}


def list_recent_tasks(args):
    init_db()
    limit = int(args.get("limit", 10))
    limit = max(1, min(limit, 100))
    with connect() as conn:
        rows = [dict(row) for row in conn.execute("SELECT * FROM tasks ORDER BY requested_at DESC LIMIT ?", (limit,))]
    return {"tasks": rows}


def record_artifact(args):
    init_db()
    task_id = str(args["task_id"]).strip()
    artifact_path = str(args["path"]).strip()
    sha256 = args.get("sha256")
    if not sha256 and artifact_path:
        candidate = Path(artifact_path)
        if candidate.exists() and candidate.is_file():
            sha256 = hashlib.sha256(candidate.read_bytes()).hexdigest()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO artifacts(task_id, path, artifact_type, sha256, created_at, metadata_json)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                artifact_path,
                str(args.get("artifact_type", "file")),
                sha256,
                str(args.get("created_at", utc_now())),
                json_text(args.get("metadata")),
            ),
        )
    return {"ok": True, "task_id": task_id, "path": artifact_path, "sha256": sha256}


def record_telemetry(args):
    init_db()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO telemetry(ts, severity, category, message, metadata_json)
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                str(args.get("ts", utc_now())),
                str(args.get("severity", "INFO")),
                str(args.get("category", "general")),
                str(args.get("message", "")),
                json_text(args.get("metadata")),
            ),
        )
    return {"ok": True}


TOOLS = [
    {
        "name": "init_state_db",
        "description": "Create or migrate the controller SQLite state database.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "db_status",
        "description": "Return controller state database path and table counts.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "record_task",
        "description": "Create or update a controller task state row.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "source": {"type": "string"},
                "workspace": {"type": "string"},
                "status": {"type": "string"},
                "started_at": {"type": "string"},
                "finished_at": {"type": "string"},
                "summary": {"type": "string"},
                "risk_level": {"type": "string"},
                "approvals": {"type": "object"},
                "metadata": {"type": "object"},
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "record_event",
        "description": "Append a deterministic event to a task timeline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "event_type": {"type": "string"},
                "actor": {"type": "string"},
                "message": {"type": "string"},
                "metadata": {"type": "object"},
            },
            "required": ["task_id", "message"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_task",
        "description": "Fetch a task with events and artifacts.",
        "inputSchema": {
            "type": "object",
            "properties": {"task_id": {"type": "string"}},
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_recent_tasks",
        "description": "List recent controller tasks.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 10}},
            "additionalProperties": False,
        },
    },
    {
        "name": "record_artifact",
        "description": "Record a task artifact path and optional SHA-256.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "path": {"type": "string"},
                "artifact_type": {"type": "string"},
                "sha256": {"type": "string"},
                "metadata": {"type": "object"},
            },
            "required": ["task_id", "path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "record_telemetry",
        "description": "Append controller telemetry to the state database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "severity": {"type": "string"},
                "category": {"type": "string"},
                "message": {"type": "string"},
                "metadata": {"type": "object"},
            },
            "required": ["message"],
            "additionalProperties": False,
        },
    },
]


def db_status(_args):
    init_db()
    with connect() as conn:
        counts = {}
        for table in ("tasks", "task_events", "artifacts", "telemetry"):
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return {"ok": True, "db_path": str(DB_PATH), "counts": counts}


CALLS = {
    "init_state_db": lambda args: init_db(),
    "db_status": db_status,
    "record_task": record_task,
    "record_event": record_event,
    "get_task": get_task,
    "list_recent_tasks": list_recent_tasks,
    "record_artifact": record_artifact,
    "record_telemetry": record_telemetry,
}


def send(message):
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def result(request_id, value):
    send({"jsonrpc": "2.0", "id": request_id, "result": value})


def error(request_id, code, message, data=None):
    payload = {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
    if data is not None:
        payload["error"]["data"] = data
    send(payload)


def text_result(value):
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}


def handle(message):
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
        return
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}
    try:
        if method == "initialize":
            result(
                request_id,
                {
                    "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "tac-state-db-mcp", "version": "0.1.0"},
                },
            )
        elif method == "tools/list":
            result(request_id, {"tools": TOOLS})
        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            if name not in CALLS:
                raise ValueError(f"unknown tool: {name}")
            result(request_id, text_result(CALLS[name](args)))
        elif method == "ping":
            result(request_id, {})
        elif request_id is not None:
            error(request_id, -32601, f"method not found: {method}")
    except Exception as exc:
        error(request_id, -32000, str(exc))


def main():
    buffer = b""
    while True:
        chunk = sys.stdin.buffer.read1(4096)
        if not chunk:
            break
        buffer += chunk
        while True:
            header_end = buffer.find(b"\r\n\r\n")
            sep_len = 4
            if header_end < 0:
                header_end = buffer.find(b"\n\n")
                sep_len = 2
            if header_end < 0:
                break
            header = buffer[:header_end].decode("utf-8", "replace")
            length = None
            for line in header.splitlines():
                if line.lower().startswith("content-length:"):
                    length = int(line.split(":", 1)[1].strip())
                    break
            if length is None:
                buffer = buffer[header_end + sep_len :]
                continue
            body_start = header_end + sep_len
            body_end = body_start + length
            if len(buffer) < body_end:
                break
            body = buffer[body_start:body_end]
            buffer = buffer[body_end:]
            handle(json.loads(body.decode("utf-8")))


if __name__ == "__main__":
    main()
