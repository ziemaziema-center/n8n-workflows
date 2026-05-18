from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("TAC_ROOT", Path(__file__).resolve().parents[1]))
SECRET_PATTERN = re.compile(r"(sk-proj-[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{20,}|AA[A-Za-z0-9_-]{20,}:[A-Za-z0-9_-]{20,})")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact(value: str) -> str:
    return SECRET_PATTERN.sub("REDACTED_SECRET", value)


def load_task(raw: str) -> dict[str, Any]:
    task = json.loads(raw)
    if not str(task.get("workspace_path", "")).startswith("/home/ubuntu/workspace/"):
        raise ValueError("workspace_path must stay under /home/ubuntu/workspace/")
    return task


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def company_prompt(task: dict[str, Any]) -> str:
    objective = str(task.get("objective") or "").strip()
    workspace = str(task.get("workspace_path") or "")
    return "\n".join(
        [
            "TRUE AUTONOMOUS CONTROLLER - COMPANY HQ MODE",
            "",
            "You are Codex operating as a company-style HQ with internal agents.",
            "Use these roles internally: HQ, Planner, Builder, Reviewer, Debugger, QA, Documentation Writer, Safety Reviewer, Final Reporter.",
            "",
            "Operating rules:",
            "- First understand the user's real goal and improve the outcome beyond the literal wording.",
            "- Split the work into safe subtasks and keep moving when one live/credential/network item is blocked.",
            "- Do all safe local/offline/documentation/test/scaffold/config-template/validation work available in this cycle.",
            "- Convert unsafe or unavailable live surfaces into DEFERRED_GATE entries and continue the next executable subtask.",
            "- Run relevant validations before reporting success.",
            "- Do not read or print secrets.",
            "- Do not run sudo, force push, destructive deletion, AWS mutation, live trading, live publishing, or production mutation.",
            "- Keep writes inside the bounded workspace.",
            "- Write or update clear artifacts so the user can leave the computer and read the final outcome later.",
            "- Final answer must be Korean, plain language first, with completed work, validation, blocked work, remaining work, and how to use it.",
            "",
            f"Bounded workspace: {workspace}",
            "",
            "User objective:",
            objective,
        ]
    )


def extract_agent_message(stdout: str) -> str:
    messages: list[str] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") if isinstance(event, dict) else None
        if isinstance(item, dict) and item.get("type") == "agent_message" and item.get("text"):
            messages.append(str(item["text"]).strip())
    return "\n\n".join(message for message in messages if message)


def git_checkpoint(workspace: Path, task_id: str) -> dict[str, Any]:
    try:
        has_git = (workspace / ".git").exists()
    except OSError as exc:
        return {"status": "GIT_CHECK_SKIPPED", "checkpoint_created": False, "reason": str(exc)}
    if not has_git or shutil.which("git") is None:
        return {"status": "NO_GIT_REPO", "checkpoint_created": False}
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=workspace, capture_output=True, text=True, check=False)
    status = subprocess.run(["git", "status", "--short"], cwd=workspace, capture_output=True, text=True, check=False)
    return {
        "status": "CHECKPOINT_RECORDED",
        "checkpoint_created": False,
        "task_id": task_id,
        "head": head.stdout.strip(),
        "dirty_files_before": [line for line in status.stdout.splitlines() if line.strip()],
    }


def run_codex_host(prompt: str, workspace: Path, timeout: int) -> dict[str, Any]:
    if shutil.which("codex") is None:
        return {"status": "DEFERRED_GATE", "reason": "codex cli unavailable on host"}
    command = [
        "codex",
        "--ask-for-approval",
        "never",
        "exec",
        "--sandbox",
        os.environ.get("TAC_CODEX_SANDBOX", "danger-full-access"),
        "--json",
        "--skip-git-repo-check",
        prompt,
    ]
    completed = subprocess.run(command, cwd=workspace, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=timeout, check=False)
    stdout = redact(completed.stdout)
    stderr = redact(completed.stderr)
    return {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "runner": "host_codex_fallback",
        "returncode": completed.returncode,
        "agent_message": extract_agent_message(stdout),
        "stdout_tail": stdout[-8000:],
        "stderr_tail": stderr[-4000:],
    }


def run_codex_docker(prompt: str, workspace: Path, timeout: int) -> dict[str, Any]:
    if shutil.which("docker") is None:
        return {"status": "DEFERRED_GATE", "reason": "docker unavailable on host"}
    image = os.environ.get("TAC_CODEX_IMAGE", "tac-codex-runner:codex")
    auth_volume = os.environ.get("TAC_CODEX_AUTH_VOLUME", "").strip()
    if not auth_volume:
        return {
            "status": "DEFERRED_GATE",
            "reason": "container-specific Codex auth volume is not configured",
            "required_action": "Create/login a Docker-only Codex auth volume, then set TAC_CODEX_AUTH_VOLUME.",
        }
    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        os.environ.get("TAC_CODEX_NETWORK", "bridge"),
        "--memory",
        os.environ.get("TAC_CODEX_MEMORY", "2g"),
        "--cpus",
        os.environ.get("TAC_CODEX_CPUS", "2"),
        "-v",
        f"{workspace}:/workspace",
        "-v",
        f"{auth_volume}:/home/tacrunner/.codex",
        "-w",
        "/workspace",
        "--entrypoint",
        "codex",
        image,
        "--ask-for-approval",
        "never",
        "exec",
        "--sandbox",
        "danger-full-access",
        "--json",
        "--skip-git-repo-check",
        prompt,
    ]
    completed = subprocess.run(command, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=timeout, check=False)
    stdout = redact(completed.stdout)
    stderr = redact(completed.stderr)
    return {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "runner": "docker_codex",
        "returncode": completed.returncode,
        "agent_message": extract_agent_message(stdout),
        "stdout_tail": stdout[-8000:],
        "stderr_tail": stderr[-4000:],
    }


def run_task(task: dict[str, Any]) -> dict[str, Any]:
    task_id = str(task["task_id"])
    workspace = Path(str(task["workspace_path"]))
    prompt = company_prompt(task)
    prompt_path = ROOT / "runtime" / "prompts" / f"{task_id}.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    checkpoint = git_checkpoint(workspace, task_id)
    target = str(task.get("target_runner") or "dry_run")
    timeout = int(os.environ.get("TAC_COMPANY_TASK_TIMEOUT_SEC", "1800"))
    if target == "codex":
        docker_first = os.environ.get("TAC_USE_DOCKER_CODEX", "1") == "1"
        docker_result = run_codex_docker(prompt, workspace, timeout) if docker_first else {"status": "SKIPPED"}
        if docker_result.get("status") == "PASS":
            runner_result = docker_result
        elif os.environ.get("TAC_ALLOW_HOST_CODEX_FALLBACK", "1") == "1":
            host_result = run_codex_host(prompt, workspace, timeout)
            runner_result = {**host_result, "docker_attempt": docker_result}
        else:
            runner_result = docker_result
    else:
        runner_result = {
            "status": "PASS",
            "runner": "dry_run_company_hq",
            "agent_message": "회사형 HQ dry-run: 요청을 작업장부에 넣고 안전 범위에서 실행 가능한 단계로 분해했습니다.",
        }
    status = str(runner_result.get("status") or "FAIL")
    report = {
        "task_id": task_id,
        "status": status,
        "target_runner": target,
        "workspace": str(workspace),
        "created_at": utc_now(),
        "prompt_path": str(prompt_path),
        "git_checkpoint": checkpoint,
        "runner_result": runner_result,
        "live_production_mutation": False,
        "secret_values_printed": False,
    }
    out = ROOT / "runtime" / "company_runner" / f"{task_id}.json"
    write_json(out, report)
    print(json.dumps({"task_id": task_id, "status": status, "report": str(out)}, ensure_ascii=False))
    if status in {"PASS", "DEFERRED_GATE"}:
        message = str(runner_result.get("agent_message") or runner_result.get("reason") or "작업 결과가 저장되었습니다.")
        print(message)
    return report


def main() -> int:
    if len(sys.argv) < 2:
        print("missing task json", file=sys.stderr)
        return 2
    try:
        task = load_task(sys.argv[1])
        report = run_task(task)
        return 0 if report["status"] == "PASS" else 3
    except Exception as exc:  # noqa: BLE001 - runner must write a clear log for reviewer
        print(f"DEFERRED_GATE company_task_runner_error: {redact(str(exc))}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
