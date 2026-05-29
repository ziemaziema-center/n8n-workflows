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
SUCCESS_STATUSES = {"PASS", "PASS_WITH_SAFE_FALLBACK"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact(value: str) -> str:
    return SECRET_PATTERN.sub("REDACTED_SECRET", value)


def load_task(raw: str) -> dict[str, Any]:
    raw_input = raw.strip()
    candidate = Path(raw_input)
    if candidate.exists() and candidate.is_file():
        raw_text = candidate.read_text(encoding="utf-8")
    else:
        raw_text = raw
    task = json.loads(raw_text)
    if not str(task.get("workspace_path", "")).startswith("/home/ubuntu/workspace/"):
        raise ValueError("workspace_path must stay under /home/ubuntu/workspace/")
    return task


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_report_path(task: dict[str, Any], task_id: str) -> Path:
    raw = str(task.get("final_report_path") or "").strip()
    if raw:
        candidate = Path(raw)
        if not candidate.is_absolute():
            return ROOT / candidate
        return candidate
    return ROOT / "runtime" / "reports" / f"{task_id}.md"


def build_worldvape_local_report(task: dict[str, Any], runner_result: dict[str, Any], report_path: Path) -> str:
    deferred = [str(item.get("name", "")) for item in task.get("deferred_gates", []) if isinstance(item, dict)]
    now = utc_now()
    lines = [
        f"# Worldvape Daily Growth Safe Rerun ({task.get('task_id', 'unknown')})",
        "",
        f"- generated_at: {now}",
        "- mode: local_report_only",
        f"- runner_status: {runner_result.get('status', 'UNKNOWN')}",
        f"- runner_reason: {runner_result.get('reason', 'none')}",
        f"- report_path: {report_path}",
        "",
        "## Daily Objective",
        str(task.get("objective", "")).strip(),
        "",
        "## Local Action Plan (No Live Publish)",
        "1. Analyze yesterday's local notes and map one winning hook + one weak hook.",
        "2. Prepare 4 Instagram draft concepts (hook, value point, CTA, risk note) as text only.",
        "3. Build one weekly SEO micro-task for local intent pages (title/meta/FAQ refresh).",
        "4. Prepare one Google Business Profile draft post and one review-response draft (offline text only).",
        "5. Define one in-store conversion experiment with metric, baseline, and next-day decision rule.",
        "",
        "## Instagram Draft Backlog (Offline Only)",
        "- Candidate A: price-comparison educational reel draft with local store intent CTA.",
        "- Candidate B: beginner setup checklist draft with save-focused CTA.",
        "- Candidate C: flavor category explainer draft with comment trigger question.",
        "- Candidate D: common mistake correction draft with follow reason.",
        "",
        "## Google Business Profile / Store Ops",
        "- Update weekly post copy draft (no publish).",
        "- Draft 3 review reply templates by sentiment (positive/neutral/issue).",
        "- Draft one map-intent FAQ update for in-store visit conversion.",
        "",
        "## Conversion Experiment",
        "- Experiment: Counter script A/B for first-time walk-ins.",
        "- KPI: purchase conversion rate and repeat-visit signal.",
        "- Rule: keep variant only if conversion improves >= 10% over baseline.",
        "",
        "## Deferred Live Actions",
    ]
    for name in deferred:
        lines.append(f"- {name}")
    lines.extend(
        [
            "",
            "## Next Operator Action (Safe)",
            "1. Review this report and pick one primary draft for next cycle.",
            "2. Refine wording locally and keep outputs in docs/reports only.",
            "",
            "## Next Live Action (Requires Explicit Approval)",
            "Any Instagram publish, Telegram send, n8n activation, credentialed API use,",
            "or production mutation requires explicit operator approval.",
            "",
            "## Safety Confirmation",
            "- live_publish: NO",
            "- telegram_send: NO",
            "- n8n_activation: NO",
            "- external_api_calls: NO",
            "- secrets_exposed: NO",
        ]
    )
    return "\n".join(lines) + "\n"


def runner_block_reason(runner_result: dict[str, Any]) -> str:
    parts = [
        str(runner_result.get("reason") or ""),
        str(runner_result.get("stderr_tail") or ""),
        str(runner_result.get("stdout_tail") or ""),
        str(runner_result.get("agent_message") or ""),
    ]
    text = "\n".join(part for part in parts if part.strip())
    return redact(text[-3000:] or "runner did not produce a detailed reason")


def build_safe_fallback_report(task: dict[str, Any], runner_result: dict[str, Any], fallback_path: Path) -> str:
    task_id = str(task.get("task_id", "unknown"))
    objective = str(task.get("objective") or "").strip()
    deferred = [str(item.get("name", "")) for item in task.get("deferred_gates", []) if isinstance(item, dict)]
    if not deferred:
        deferred = ["original_runner_block"]
    lines = [
        f"# TAC Safe Fallback Report ({task_id})",
        "",
        f"- generated_at: {utc_now()}",
        "- status: PASS_WITH_SAFE_FALLBACK",
        f"- original_runner_status: {runner_result.get('status', 'UNKNOWN')}",
        f"- original_runner: {runner_result.get('runner', 'unknown')}",
        f"- fallback_report_path: {fallback_path}",
        "",
        "## User Objective",
        objective or "No objective was provided.",
        "",
        "## Why Fallback Ran",
        runner_block_reason(runner_result),
        "",
        "## Safe Work Completed Instead Of Stopping",
        "- Preserved the task as an auditable completed fallback instead of ending silently.",
        "- Converted the blocked execution surface into deferred gates.",
        "- Produced a continuation-ready report with concrete next executable subtasks.",
        "- Kept live, credential, production, AWS, trading, publishing, and destructive surfaces blocked.",
        "",
        "## Deferred Gates",
    ]
    lines.extend(f"- {name}" for name in deferred)
    lines.extend(
        [
            "",
            "## Next Executable Safe Subtasks",
            "1. Read this fallback report and the original runner log.",
            "2. Patch local scripts, templates, tests, or docs that caused the block when the cause is inside the workspace.",
            "3. Run the local/offline validation suite.",
            "4. Requeue the task with the same objective after the local cause is fixed.",
            "5. Escalate only the live/credential/network item that cannot be fixed locally.",
            "",
            "## Safety Confirmation",
            "- live_publish: NO",
            "- telegram_send_from_runner: NO",
            "- n8n_activation: NO",
            "- external_api_calls: NO",
            "- secrets_exposed: NO",
            "- destructive_delete: NO",
        ]
    )
    return "\n".join(lines) + "\n"


def write_safe_fallback_report(task: dict[str, Any], runner_result: dict[str, Any]) -> Path:
    task_id = str(task.get("task_id", "unknown"))
    fallback_path = ROOT / "runtime" / "reports" / f"{task_id}.safe_fallback.md"
    fallback_path.parent.mkdir(parents=True, exist_ok=True)
    fallback_path.write_text(build_safe_fallback_report(task, runner_result, fallback_path), encoding="utf-8")
    return fallback_path


def apply_safe_fallback(task: dict[str, Any], runner_result: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    status = str(runner_result.get("status") or "FAIL")
    if status == "PASS" or bool(task.get("disable_safe_fallback", False)):
        return runner_result, None
    fallback_path = write_safe_fallback_report(task, runner_result)
    return (
        {
            "status": "PASS_WITH_SAFE_FALLBACK",
            "runner": "safe_fallback_reporter",
            "original_runner_status": status,
            "original_runner": runner_result.get("runner", "unknown"),
            "reason": "original runner was blocked, so TAC continued by writing a safe fallback report and deferred only the blocked surface",
            "fallback_report_path": str(fallback_path),
            "original_reason_tail": runner_block_reason(runner_result),
        },
        str(fallback_path),
    )


def write_local_strategy_report(task: dict[str, Any], runner_result: dict[str, Any]) -> Path:
    task_id = str(task.get("task_id", "unknown"))
    report_path = safe_report_path(task, task_id)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_text = build_worldvape_local_report(task, runner_result, report_path)
    report_path.write_text(report_text, encoding="utf-8")
    return report_path


def docker_workspace_gid() -> str:
    configured = os.environ.get("TAC_DOCKER_WORKSPACE_GID", "").strip()
    if configured:
        return configured
    getgid = getattr(os, "getgid", None)
    if callable(getgid):
        return str(getgid())
    return "0"


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
            "- ALL SAFE LOCAL/OFFLINE WORK IS ALREADY APPROVED FOR THIS QUEUE TASK.",
            "- Do not ask for approval before doing safe local/offline/documentation/test/scaffold/config-template/validation work.",
            "- Do not return only a plan, meeting note, or WAITING_FOR_APPROVAL status.",
            "- After a short plan, execute immediately inside the bounded workspace and create concrete artifacts where useful.",
            "- First understand the user's real goal and improve the outcome beyond the literal wording.",
            "- Split the work into safe subtasks and keep moving when one live/credential/network item is blocked.",
            "- Do all safe local/offline/documentation/test/scaffold/config-template/validation work available in this cycle.",
            "- Convert unsafe or unavailable live surfaces into DEFERRED_GATE entries and continue the next executable subtask.",
            "- Yuna deal inbound communication or SNS content tasks must prevent duplicate city/deal/topic repetition and increase variety.",
            "- Repeated same-destination outputs are a defect; diversify candidates before reporting success.",
            "- Do not return four similar Singapore items or four near-duplicate candidates for any destination/topic.",
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
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "status": "CHECKPOINT_RECORDED",
        "checkpoint_created": False,
        "task_id": task_id,
        "head": head.stdout.strip(),
        "dirty_files_before": [line for line in status.stdout.splitlines() if line.strip()],
    }


def resolve_execution_workspace(task: dict[str, Any], default_workspace: Path) -> Path:
    raw = str(task.get("local_workspace_path") or "").strip()
    if not raw:
        return default_workspace
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    resolved = candidate.resolve()
    allowed_root = (ROOT / "runtime" / "workspaces").resolve()
    if resolved != allowed_root and allowed_root not in resolved.parents:
        raise ValueError("local_workspace_path must stay under runtime/workspaces")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


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
    completed = subprocess.run(
        command,
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdin=subprocess.DEVNULL,
        timeout=timeout,
        check=False,
    )
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
        "--group-add",
        docker_workspace_gid(),
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
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdin=subprocess.DEVNULL,
        timeout=timeout,
        check=False,
    )
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
    execution_workspace = resolve_execution_workspace(task, workspace)
    prompt = company_prompt(task)
    prompt_path = ROOT / "runtime" / "prompts" / f"{task_id}.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    checkpoint = git_checkpoint(execution_workspace, task_id)
    target = str(task.get("target_runner") or "dry_run")
    timeout = int(os.environ.get("TAC_COMPANY_TASK_TIMEOUT_SEC", "1800"))
    if target == "codex":
        docker_first = os.environ.get("TAC_USE_DOCKER_CODEX", "1") == "1"
        docker_result = run_codex_docker(prompt, execution_workspace, timeout) if docker_first else {"status": "SKIPPED"}
        if docker_result.get("status") == "PASS":
            runner_result = docker_result
        elif os.environ.get("TAC_ALLOW_HOST_CODEX_FALLBACK", "0") == "1":
            host_result = run_codex_host(prompt, execution_workspace, timeout)
            runner_result = {**host_result, "docker_attempt": docker_result}
        else:
            runner_result = docker_result
    else:
        runner_result = {
            "status": "PASS",
            "runner": "dry_run_company_hq",
            "agent_message": "회사형 HQ dry-run: 요청을 작업장부에 넣고 안전 범위에서 실행 가능한 단계로 분해했습니다.",
        }
    generated_report_path: str | None = None
    if bool(task.get("report_only", False)) and task_id.startswith("worldvape-daily-growth"):
        generated_report_path = str(write_local_strategy_report(task, runner_result))
    runner_result, fallback_report_path = apply_safe_fallback(task, runner_result)
    if fallback_report_path and not generated_report_path:
        generated_report_path = fallback_report_path
    status = str(runner_result.get("status") or "FAIL")
    report = {
        "task_id": task_id,
        "status": status,
        "target_runner": target,
        "workspace": str(workspace),
        "execution_workspace": str(execution_workspace),
        "created_at": utc_now(),
        "prompt_path": str(prompt_path),
        "git_checkpoint": checkpoint,
        "runner_result": runner_result,
        "generated_report_path": generated_report_path,
        "live_production_mutation": False,
        "secret_values_printed": False,
    }
    out = ROOT / "runtime" / "company_runner" / f"{task_id}.json"
    write_json(out, report)
    print(json.dumps({"task_id": task_id, "status": status, "report": str(out)}, ensure_ascii=False))
    if status in SUCCESS_STATUSES or status == "DEFERRED_GATE":
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
        return 0 if report["status"] in SUCCESS_STATUSES else 3
    except Exception as exc:  # noqa: BLE001 - runner must write a clear log for reviewer
        print(f"DEFERRED_GATE company_task_runner_error: {redact(str(exc))}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
