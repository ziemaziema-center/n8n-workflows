from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .controller import ControllerError, run_controller, safe_task_id, task_from_prompt, utc_now, validate_task_shape, write_result
from .queue_runtime import make_queue_task, write_queue_task


class ControllerState:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.runtime_root = self.project_root / "runtime" / "tasks"
        self.runtime_root.mkdir(parents=True, exist_ok=True)

    def result_path(self, task_id: str) -> Path:
        return self.runtime_root / task_id / "result.json"

    def task_path(self, task_id: str) -> Path:
        return self.runtime_root / task_id / "task.json"

    def save_task(self, task: dict[str, Any]) -> None:
        task_dir = self.runtime_root / task["task_id"]
        task_dir.mkdir(parents=True, exist_ok=True)
        with self.task_path(task["task_id"]).open("w", encoding="utf-8") as handle:
            json.dump(task, handle, indent=2, ensure_ascii=True)
            handle.write("\n")

    def latest_result(self, exclude_task_id: str = "") -> dict[str, Any] | None:
        result_paths = sorted(
            self.runtime_root.glob("tac-*/result.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for path in result_paths:
            if exclude_task_id and path.parent.name == exclude_task_id:
                continue
            try:
                with path.open("r", encoding="utf-8-sig") as handle:
                    return json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue
        return None

    def apply_followup_workspace(self, task: dict[str, Any]) -> None:
        metadata = task.get("metadata") if isinstance(task.get("metadata"), dict) else {}
        if not metadata.get("telegram_followup") or task.get("workspace") != ".":
            return
        latest = self.latest_result(str(task.get("task_id") or ""))
        workspace = str((latest or {}).get("workspace") or "")
        if workspace.startswith("/home/ubuntu/workspace/") or workspace.startswith(str(self.project_root)):
            task["workspace"] = workspace
            metadata["followup_workspace_from_task"] = str((latest or {}).get("task_id") or "unknown")
            task["metadata"] = metadata

    def run_task(self, task: dict[str, Any]) -> dict[str, Any]:
        self.apply_followup_workspace(task)
        validate_task_shape(task)
        self.save_task(task)
        result = run_controller(task, self.project_root)
        write_result(result, self.result_path(task["task_id"]))
        return result

    def load_result(self, task_id: str) -> dict[str, Any] | None:
        path = self.result_path(task_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)

    def enqueue(self, body: dict[str, Any]) -> dict[str, Any]:
        task = body.get("queue_task") if isinstance(body.get("queue_task"), dict) else None
        if task is None:
            objective = str(body.get("objective") or body.get("prompt") or body.get("text") or "Queued TAC runtime task.")
            task = make_queue_task(
                task_id=str(body.get("task_id") or safe_task_id(objective)).replace("tac-", "hq-", 1),
                objective=objective,
                requested_by=str(body.get("requested_by") or "telegram"),
                source_channel=str(body.get("source_channel") or body.get("source") or "telegram"),
                workspace_path=str(body.get("workspace_path") or "/home/ubuntu/workspace/true-autonomous-controller"),
                priority=str(body.get("priority") or "normal"),
                target_runner=str(body.get("target_runner") or "codex"),
                notification={
                    "on_completion": bool(str(body.get("chat_id") or "").strip()),
                    "chat_id": str(body.get("chat_id") or "").strip(),
                    "webhook_url": str(body.get("notify_webhook_url") or "https://n8n.mykindredai.com/webhook/tac-controller").strip(),
                    "channel": "telegram",
                },
            )
        result = write_queue_task(task, runtime_root=self.project_root / "runtime")
        dispatch_requested = str(body.get("dispatch") or "").strip().lower() in {"1", "true", "yes"}
        dispatch_requested = dispatch_requested or str(body.get("source") or body.get("source_channel") or "") == "telegram"
        if dispatch_requested:
            result["dispatch"] = self.dispatch_runner()
        else:
            result["dispatch"] = {"requested": False, "live_dispatch_performed": False}
        return result

    def dispatch_runner(self) -> dict[str, Any]:
        if shutil.which("tmux") is None:
            return {
                "requested": True,
                "status": "DEFERRED_GATE",
                "reason": "tmux unavailable on this host",
                "live_dispatch_performed": False,
            }
        session = "tac-hq-runner"
        has_session = subprocess.run(["tmux", "has-session", "-t", session], capture_output=True, text=True, check=False)
        if has_session.returncode == 0:
            return {"requested": True, "status": "ALREADY_RUNNING", "session": session, "live_dispatch_performed": True}
        command = f"TAC_ROOT={self.project_root} bash {self.project_root / 'scripts' / 'hq_tmux_runner_template.sh'}"
        started = subprocess.run(
            ["tmux", "new-session", "-d", "-s", session, command],
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "requested": True,
            "status": "STARTED" if started.returncode == 0 else "FAIL",
            "session": session,
            "returncode": started.returncode,
            "stderr_tail": started.stderr[-1000:],
            "live_dispatch_performed": started.returncode == 0,
        }

    def handoff(self) -> dict[str, Any]:
        ledger_path = self.project_root / "reports" / "hq_continuation_ledger_2026-05-18.json"
        if not ledger_path.exists():
            return {"ok": False, "status": "MISSING_LEDGER", "ledger_path": str(ledger_path)}
        with ledger_path.open("r", encoding="utf-8-sig") as handle:
            ledger = json.load(handle)
        return {
            "ok": True,
            "status": "HANDOFF_READY",
            "current_phase": ledger.get("current_phase"),
            "next_executable_subtasks": ledger.get("next_executable_subtasks", []),
            "final_report_path": ledger.get("final_report_path"),
            "resume_instruction": ledger.get("resume_instruction"),
        }


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, indent=2, ensure_ascii=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode("utf-8-sig"))


def kill_scoped_tmux_sessions() -> dict[str, Any]:
    killed_processes: list[str] = []
    current_uid = str(os.getuid()) if hasattr(os, "getuid") else ""
    for pattern in ("codex", "claude"):
        command = ["pkill"]
        if current_uid:
            command.extend(["-u", current_uid])
        command.extend(["-f", pattern])
        killed = subprocess.run(command, capture_output=True, text=True, check=False)
        if killed.returncode == 0:
            killed_processes.append(pattern)
    if shutil.which("tmux") is None:
        return {"killed_sessions": [], "killed_process_patterns": killed_processes, "message": "tmux unavailable on this host"}
    listed = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"], capture_output=True, text=True, check=False)
    if listed.returncode != 0:
        return {"killed_sessions": [], "killed_process_patterns": killed_processes, "message": "no tmux server or no sessions"}
    sessions = [line.strip() for line in listed.stdout.splitlines() if line.strip().startswith("tac-task-")]
    killed: list[str] = []
    for session in sessions:
        subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True, text=True, check=False)
        killed.append(session)
    return {"killed_sessions": killed, "killed_process_patterns": killed_processes, "message": "scoped tmux kill completed"}


class ControllerHandler(BaseHTTPRequestHandler):
    state: ControllerState

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            json_response(self, 200, {"ok": True, "service": "true-autonomous-controller", "time": utc_now()})
            return
        if parsed.path == "/status":
            task_id = parse_qs(parsed.query).get("task_id", [""])[0]
            if not task_id:
                json_response(self, 400, {"ok": False, "error": "missing task_id"})
                return
            result = self.state.load_result(task_id)
            if not result:
                json_response(self, 404, {"ok": False, "error": "task not found", "task_id": task_id})
                return
            json_response(self, 200, {"ok": True, "result": result})
            return
        if parsed.path == "/handoff":
            json_response(self, 200, self.state.handoff())
            return
        json_response(self, 404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            body = read_json_body(self)
            if parsed.path == "/run":
                task = body.get("task") if isinstance(body.get("task"), dict) else None
                if task is None:
                    prompt = body.get("prompt") or body.get("text") or body.get("message") or "Phase 3 smoke run"
                    executor = str(body.get("executor") or "dry_run").strip().lower()
                    task = task_from_prompt(str(prompt), task_id=body.get("task_id"), source=str(body.get("source") or "n8n"), executor=executor)
                result = self.state.run_task(task)
                json_response(self, 200 if result["status"] == "PASS" else 202, {"ok": result["status"] == "PASS", "result": result})
                return
            if parsed.path == "/killall":
                outcome = kill_scoped_tmux_sessions()
                json_response(self, 200, {"ok": True, **outcome})
                return
            if parsed.path == "/queue":
                result = self.state.enqueue(body)
                json_response(self, 200, result)
                return
            if parsed.path == "/handoff":
                json_response(self, 200, self.state.handoff())
                return
            if parsed.path == "/status":
                task_id = str(body.get("task_id") or "").strip()
                if not task_id:
                    json_response(self, 400, {"ok": False, "error": "missing task_id"})
                    return
                result = self.state.load_result(task_id)
                if not result:
                    json_response(self, 404, {"ok": False, "error": "task not found", "task_id": task_id})
                    return
                json_response(self, 200, {"ok": True, "result": result})
                return
            json_response(self, 404, {"ok": False, "error": "not found"})
        except (ControllerError, OSError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
            json_response(self, 500, {"ok": False, "error": str(exc), "time": utc_now()})


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TRUE Autonomous Controller HTTP service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ControllerHandler.state = ControllerState(args.project_root)
    server = ThreadingHTTPServer((args.host, args.port), ControllerHandler)
    print(f"tac_service_listening host={args.host} port={args.port} project_root={args.project_root}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
