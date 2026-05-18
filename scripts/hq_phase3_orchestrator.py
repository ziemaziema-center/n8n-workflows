from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "runtime" / "phase3_orchestrator_result_2026-05-18.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_task() -> dict:
    return {
        "task_id": "hq-phase3-orchestrator-local-20260518",
        "objective": "Validate planner-executor-reviewer retry loop locally.",
        "workspace_path": str(ROOT),
        "max_retries": 2,
        "validation_commands": [
            [sys.executable, "-m", "json.tool", "reports/hq_continuation_ledger_2026-05-18.json"],
            [sys.executable, "-m", "unittest", "tests.test_hq_queue_renderer_20260518"],
        ],
        "deferred_gates": [],
    }


def load_task(path: Path | None) -> dict:
    if path is None:
        return default_task()
    return json.loads(path.read_text(encoding="utf-8"))


def plan(task: dict) -> list[dict]:
    commands = task.get("validation_commands") or []
    subtasks = []
    for index, command in enumerate(commands, start=1):
        if isinstance(command, str):
            argv = command.split()
        else:
            argv = [str(part) for part in command]
        subtasks.append({"id": f"validation-{index}", "argv": argv})
    if not subtasks:
        subtasks.append({"id": "noop-plan", "argv": [sys.executable, "--version"]})
    return subtasks


def allowed(argv: list[str]) -> bool:
    if not argv:
        return False
    exe = Path(argv[0]).name.lower()
    return exe in {"python", "python3", "py", Path(sys.executable).name.lower()}


def execute_subtask(subtask: dict, cwd: Path) -> dict:
    argv = subtask["argv"]
    if not allowed(argv):
        return {
            "id": subtask["id"],
            "argv": argv,
            "status": "DEFERRED_GATE",
            "exit_code": None,
            "reason": f"executable not allowed in Phase 3 local loop: {argv[0]}",
        }
    completed = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False, timeout=120)
    return {
        "id": subtask["id"],
        "argv": argv,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def review(results: list[dict], retry_count: int, max_retries: int) -> dict:
    deferred = [result for result in results if result["status"] == "DEFERRED_GATE"]
    failed = [result for result in results if result["status"] == "FAIL"]
    if deferred:
        return {
            "decision": "DEFERRED_GATE",
            "retry_allowed": False,
            "reason": "one or more subtasks require a gated executable or live boundary",
        }
    if failed:
        return {
            "decision": "FAIL",
            "retry_allowed": retry_count < max_retries,
            "reason": "one or more validation commands failed",
        }
    return {"decision": "PASS", "retry_allowed": False, "reason": "planner/executor/reviewer loop passed"}


def run(task: dict) -> dict:
    workspace = Path(task.get("workspace_path") or ROOT).resolve()
    if not (workspace == ROOT or ROOT in workspace.parents):
        return {
            "task_id": task.get("task_id", "unknown"),
            "status": "DEFERRED_GATE",
            "reason": "workspace outside local controller root",
            "live_operations_performed": False,
        }
    max_retries = int(task.get("max_retries", 0))
    subtasks = plan(task)
    attempts = []
    for retry_count in range(max_retries + 1):
        results = [execute_subtask(subtask, workspace) for subtask in subtasks]
        reviewer = review(results, retry_count=retry_count, max_retries=max_retries)
        attempts.append({"retry_count": retry_count, "results": results, "review": reviewer})
        if reviewer["decision"] != "FAIL" or not reviewer["retry_allowed"]:
            break
    final = attempts[-1]["review"]
    return {
        "task_id": task.get("task_id", "unknown"),
        "status": final["decision"],
        "started_at": utc_now(),
        "finished_at": utc_now(),
        "planner": {"subtasks": subtasks},
        "attempts": attempts,
        "final_review": final,
        "live_operations_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-json", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = run(load_task(args.task_json))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "out": str(args.out)}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
