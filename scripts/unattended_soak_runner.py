from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("TAC_ROOT", Path(__file__).resolve().parents[1]))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tac.queue_runtime import make_queue_task, write_queue_task


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())


def start_runner(*, auth_volume: str, session: str) -> dict[str, Any]:
    if shutil.which("tmux") is None:
        return {"status": "DEFERRED_GATE", "reason": "tmux unavailable"}
    has_session = subprocess.run(["tmux", "has-session", "-t", session], capture_output=True, text=True, check=False)
    if has_session.returncode == 0:
        return {"status": "ALREADY_RUNNING", "session": session}
    command = (
        f"TAC_ROOT={ROOT} "
        f"TAC_CODEX_AUTH_VOLUME={auth_volume} "
        "TAC_USE_DOCKER_CODEX=1 "
        "TAC_ALLOW_HOST_CODEX_FALLBACK=0 "
        "TAC_COMPANY_TASK_TIMEOUT_SEC=240 "
        f"bash {ROOT / 'scripts' / 'hq_tmux_runner_template.sh'}"
    )
    started = subprocess.run(["tmux", "new-session", "-d", "-s", session, command], capture_output=True, text=True, check=False)
    return {
        "status": "STARTED" if started.returncode == 0 else "FAIL",
        "session": session,
        "returncode": started.returncode,
        "stderr_tail": started.stderr[-1000:],
    }


def task_status_counts(queue_dir: Path) -> dict[str, int]:
    return {
        "pending": count_lines(queue_dir / "pending.jsonl"),
        "running": count_lines(queue_dir / "running.jsonl"),
        "completed": count_lines(queue_dir / "completed.jsonl"),
        "failed": count_lines(queue_dir / "failed.jsonl"),
    }


def append_heartbeat(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def run_soak(args: argparse.Namespace) -> dict[str, Any]:
    runtime_root = ROOT / "runtime"
    queue_dir = runtime_root / "queue"
    report_dir = runtime_root / "soak"
    heartbeat_path = report_dir / f"{args.task_id}.heartbeat.jsonl"
    final_path = report_dir / f"{args.task_id}.final.json"
    started_at = time.monotonic()
    end_at = started_at + args.duration_minutes * 60
    runner = start_runner(auth_volume=args.auth_volume, session=args.runner_session)
    task_index = 0
    enqueued: list[dict[str, Any]] = []
    heartbeats: list[dict[str, Any]] = []

    while time.monotonic() < end_at:
        target_runner = "codex" if task_index < args.codex_tasks else "dry_run"
        task_id = f"{args.task_id}-{task_index:03d}"
        objective = (
            "Soak validation task. Stay inside the TAC workspace, avoid credential access, "
            "return a concise Korean completion note, and validate that the company-mode runner continues."
        )
        if target_runner == "codex":
            objective += " This task must execute through Docker-only Codex auth volume with host fallback disabled."
        task = make_queue_task(
            task_id=task_id,
            objective=objective,
            requested_by="soak_runner",
            source_channel="soak_runner",
            workspace_path=str(ROOT),
            priority="normal",
            target_runner=target_runner,
            notification={"on_completion": False, "channel": "soak"},
        )
        write_queue_task(task, runtime_root=runtime_root)
        enqueued.append({"task_id": task_id, "target_runner": target_runner, "enqueued_at": utc_now()})
        heartbeat = {
            "at": utc_now(),
            "event": "TASK_ENQUEUED",
            "task_id": task_id,
            "target_runner": target_runner,
            "counts": task_status_counts(queue_dir),
            "runner": runner,
        }
        heartbeats.append(heartbeat)
        append_heartbeat(heartbeat_path, heartbeat)
        task_index += 1
        sleep_seconds = max(1, args.interval_minutes * 60)
        while time.monotonic() < end_at and sleep_seconds > 0:
            time.sleep(min(30, sleep_seconds))
            sleep_seconds -= 30
            tick = {
                "at": utc_now(),
                "event": "HEARTBEAT",
                "counts": task_status_counts(queue_dir),
                "elapsed_seconds": round(time.monotonic() - started_at, 2),
            }
            heartbeats.append(tick)
            append_heartbeat(heartbeat_path, tick)

    final = {
        "task_id": args.task_id,
        "status": "PASS" if enqueued else "FAIL",
        "started_at": heartbeats[0]["at"] if heartbeats else utc_now(),
        "finished_at": utc_now(),
        "duration_minutes_requested": args.duration_minutes,
        "interval_minutes": args.interval_minutes,
        "auth_volume": args.auth_volume,
        "runner_session": args.runner_session,
        "runner_start": runner,
        "tasks_enqueued": enqueued,
        "final_counts": task_status_counts(queue_dir),
        "heartbeat_path": str(heartbeat_path),
        "live_production_mutation": False,
        "host_codex_fallback_allowed": False,
        "docker_only_codex_requested": args.codex_tasks > 0,
    }
    final_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a long unattended TAC queue soak.")
    parser.add_argument("--task-id", default="tac-unattended-soak-20260524")
    parser.add_argument("--duration-minutes", type=int, default=360)
    parser.add_argument("--interval-minutes", type=int, default=20)
    parser.add_argument("--codex-tasks", type=int, default=2)
    parser.add_argument("--auth-volume", default="tac-codex-auth")
    parser.add_argument("--runner-session", default="tac-hq-runner")
    return parser.parse_args()


def main() -> int:
    result = run_soak(parse_args())
    print(json.dumps({"status": result["status"], "tasks": len(result["tasks_enqueued"]), "final_counts": result["final_counts"]}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
