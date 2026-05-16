from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .controller import ControllerError, run_controller, task_from_prompt, utc_now, validate_task_shape, write_result


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

    def run_task(self, task: dict[str, Any]) -> dict[str, Any]:
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
    if shutil.which("tmux") is None:
        return {"killed_sessions": [], "message": "tmux unavailable on this host"}
    listed = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"], capture_output=True, text=True, check=False)
    if listed.returncode != 0:
        return {"killed_sessions": [], "message": "no tmux server or no sessions"}
    sessions = [line.strip() for line in listed.stdout.splitlines() if line.strip().startswith("tac-task-")]
    killed: list[str] = []
    for session in sessions:
        subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True, text=True, check=False)
        killed.append(session)
    return {"killed_sessions": killed, "message": "scoped tmux kill completed"}


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
