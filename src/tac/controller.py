from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HARD_LIMITS = {
    "max_iterations": 10,
    "max_runtime_sec": 1800,
    "retry_limit": 3,
    "cost_ceiling_usd": 5,
}

ALLOWED_EXECUTABLES = {
    "echo",
    "python",
    "python3",
    "py",
    "codex",
    sys.executable.lower(),
    Path(sys.executable).name.lower(),
}

DENIED_EXECUTABLES = {
    "aws",
    "curl",
    "docker",
    "kubectl",
    "rm",
    "scp",
    "ssh",
    "sudo",
}

DEFAULT_LIMITS = {
    "max_iterations": 10,
    "max_runtime_sec": 1800,
    "retry_limit": 3,
    "cost_ceiling_usd": 5,
}

DEFAULT_CODEX_SANDBOX = "workspace-write"
ALLOWED_CODEX_SANDBOXES = {"read-only", "workspace-write", "danger-full-access"}

WORKSPACE_ALIASES = {
    "02_업비트_자동화": "/home/ubuntu/workspace/02_업비트_자동화",
    "업비트": "/home/ubuntu/workspace/02_업비트_자동화",
    "upbit": "/home/ubuntu/workspace/02_업비트_자동화",
    "02_upbit_automation_clean": "/home/ubuntu/workspace/02_upbit_automation_clean",
}


class ControllerError(Exception):
    """Base error for controlled failures."""


class RiskBlocked(ControllerError):
    """Raised when a task must not run automatically."""


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_*\\-]{8,}"),
]


@dataclass(frozen=True)
class Review:
    status: str
    reasons: list[str]
    retry_allowed: bool
    escalation_required: bool

    def to_json(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reasons": self.reasons,
            "retry_allowed": self.retry_allowed,
            "escalation_required": self.escalation_required,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_task(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        task = json.load(handle)
    validate_task_shape(task)
    return task


def validate_task_shape(task: dict[str, Any]) -> None:
    required = {
        "task_id",
        "requested_phase",
        "source",
        "prompt",
        "workspace",
        "execution_mode",
        "risk_level",
        "limits",
        "commands",
    }
    missing = sorted(required - set(task))
    if missing:
        raise ControllerError(f"task spec missing required fields: {', '.join(missing)}")

    if not isinstance(task["commands"], list) or not task["commands"]:
        raise ControllerError("task spec must include at least one command")

    if task["requested_phase"] < 0 or task["requested_phase"] > 3:
        raise ControllerError("local scaffold supports requested_phase 0 through 3")

    limits = task["limits"]
    for key, hard_limit in HARD_LIMITS.items():
        if key not in limits:
            raise ControllerError(f"limits missing {key}")
        if limits[key] > hard_limit:
            raise ControllerError(f"{key} exceeds hard limit {hard_limit}")


def safe_task_id(seed: str | None = None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    digest = hashlib.sha256(f"{seed or ''}|{time.time_ns()}".encode("utf-8")).hexdigest()[:10]
    return f"tac-{stamp}-{digest}"


def codex_sandbox_mode() -> str:
    mode = os.environ.get("TAC_CODEX_SANDBOX", DEFAULT_CODEX_SANDBOX).strip()
    if mode not in ALLOWED_CODEX_SANDBOXES:
        return DEFAULT_CODEX_SANDBOX
    return mode


def extract_requested_workspace(prompt: str) -> str:
    text = str(prompt or "")
    for line in text.splitlines():
        match = re.match(r"^\s*(?:WORKSPACE|workspace)\s*[:=]\s*(\S+)\s*$", line)
        if match:
            return match.group(1)
    path_match = re.search(r"(/home/ubuntu/workspace/[^\s]+)", text)
    if path_match:
        return path_match.group(1)
    lowered = text.lower()
    for alias, workspace in WORKSPACE_ALIASES.items():
        if alias.lower() in lowered:
            return workspace
    return "."


def build_codex_prompt(user_prompt: str, workspace: str) -> str:
    return "\n".join(
        [
            "TRUE AUTONOMOUS CONTROLLER task.",
            "",
            "Operating rules:",
            "- Work only inside the bounded workspace shown below.",
            "- Read project memory first when present: agent_memory/KNOWN_FAILURES.md, agent_memory/VALIDATED_PATTERNS.md, agent_memory/PATCH_HISTORY.md, SESSION_BOOT.md.",
            "- Do not read or print secret values from .env, key, credential, token, or private-key files.",
            "- Do not run sudo, force push, destructive deletion, live trading, AWS mutation, Docker restart, or production mutation.",
            "- For Upbit/trading projects, stay dry-run/read-only unless the prompt explicitly approves live exchange mutation.",
            "- Validate before reporting success. If validation cannot run, say exactly what blocked it.",
            "- Do not stop the whole task because one live/credential/network item is blocked.",
            "- Continue all safe local, offline, documentation, test, scaffold, wrapper, config-template, and validation work.",
            "- Convert blocked items into explicit DEFERRED_GATE entries, then proceed to the next executable subtask.",
            "- Use the full bounded cycle intelligently when safe work remains; do not end early after one small item.",
            "- Maintain or update continuation ledger / handoff notes when the task is broader than one bounded cycle.",
            "- Return the final report in Korean, in plain non-technical language first.",
            "- Avoid English operational labels unless they are command names, file names, task ids, or unavoidable product names.",
            "- Explain code or automation terms in simple Korean when they matter.",
            "- Do not dump raw logs unless they are short and necessary.",
            "- If the user asks for multi-hour work, do not only say the cycle is bounded. Do all safe work possible now, record deferred gates, and leave a concrete continuation handoff.",
            "- Use this exact Korean report shape: 결론, 예상 시간/실제 소요, 이번에 한 일, 검증 결과, deferred gates, 남은 일, 다음 실행 가능한 작업, 사용 방법, 실제 live operation 여부.",
            "",
            f"Bounded workspace: {workspace}",
            "",
            "User request:",
            user_prompt,
        ]
    )


def task_from_prompt(prompt: str, *, task_id: str | None = None, source: str = "n8n", executor: str = "dry_run") -> dict[str, Any]:
    clean_prompt = str(prompt or "").strip()
    if not clean_prompt:
        clean_prompt = "Phase 3 smoke run"
    workspace = extract_requested_workspace(clean_prompt)
    if executor == "codex":
        execution_mode = "local_command"
        codex_prompt = build_codex_prompt(clean_prompt, workspace)
        commands = [
            {
                "id": "codex-executor",
                "argv": [
                    "codex",
                    "--ask-for-approval",
                    "never",
                    "exec",
                    "--sandbox",
                    codex_sandbox_mode(),
                    "--json",
                    "--skip-git-repo-check",
                    codex_prompt,
                ],
            }
        ]
    else:
        execution_mode = "dry_run"
        commands = [
            {
                "id": "planner-executor-reviewer-smoke",
                "argv": ["echo", clean_prompt[:500]],
            }
        ]
    return {
        "task_id": task_id or safe_task_id(clean_prompt),
        "requested_phase": 3,
        "source": source if source in {"telegram", "n8n", "manual", "test"} else "n8n",
        "prompt": clean_prompt,
        "workspace": workspace,
        "execution_mode": execution_mode,
        "risk_level": "read_only",
        "limits": dict(DEFAULT_LIMITS),
        "commands": commands,
        "metadata": {
            "generated_from_prompt": True,
            "executor": executor,
            "telegram_summary": True,
            "reviewer_required": True,
            "telegram_followup": clean_prompt.startswith("FOLLOWUP_TASK: true"),
        },
    }


def resolve_workspace(root: Path, workspace: str) -> Path:
    workspace_text = str(workspace or ".").strip()
    raw_candidate = Path(workspace_text).expanduser()
    root_resolved = root.resolve()
    if not raw_candidate.is_absolute():
        candidate = (root / raw_candidate).resolve()
        if candidate == root_resolved or root_resolved in candidate.parents:
            return candidate
        raise RiskBlocked(f"relative workspace escapes project root: {candidate}")

    candidate = raw_candidate.resolve()
    allowed_roots = [root_resolved]
    configured_roots = os.environ.get("TAC_ALLOWED_WORKSPACE_ROOTS", "")
    if configured_roots:
        allowed_roots.extend(Path(path).expanduser().resolve() for path in configured_roots.split(os.pathsep) if path.strip())
    elif Path("/home/ubuntu/workspace").exists():
        allowed_roots.append(Path("/home/ubuntu/workspace").resolve())
    for allowed_root in allowed_roots:
        if candidate == allowed_root or allowed_root in candidate.parents:
            return candidate
    raise RiskBlocked(f"workspace escapes allowed roots: {candidate}")


def executable_name(argv0: str) -> str:
    return Path(argv0).name.lower()


def redact_sensitive_text(text: str) -> str:
    redacted = str(text or "")
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("sk-REDACTED", redacted)
    return redacted


def ensure_codex_ready() -> None:
    if shutil.which("codex") is None:
        raise RiskBlocked("codex cli is not installed or not on PATH")
    status = subprocess.run(
        ["codex", "login", "status"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    combined = f"{status.stdout}\n{status.stderr}".strip()
    if status.returncode != 0 or "not logged in" in combined.lower():
        raise RiskBlocked("codex cli is not logged in; run codex login --with-api-key or codex login")


def guard_task(task: dict[str, Any], project_root: Path) -> Path:
    workspace = resolve_workspace(project_root, task["workspace"])
    risk_level = task["risk_level"]
    if risk_level in {"risky", "blocked"}:
        raise RiskBlocked(f"risk_level requires escalation: {risk_level}")

    for command in task["commands"]:
        argv = command.get("argv", [])
        if not argv:
            raise ControllerError(f"command {command.get('id', '<unknown>')} has empty argv")
        exe = executable_name(argv[0])
        if exe in DENIED_EXECUTABLES:
            raise RiskBlocked(f"denied executable requested: {exe}")
        if task["execution_mode"] == "local_command" and exe not in ALLOWED_EXECUTABLES:
            raise RiskBlocked(f"executable is not allowlisted: {exe}")
        if task["execution_mode"] == "local_command" and exe == "codex":
            ensure_codex_ready()

    return workspace


def run_command(command: dict[str, Any], workspace: Path, timeout_sec: int, dry_run: bool) -> dict[str, Any]:
    started = time.monotonic()
    argv = [str(part) for part in command["argv"]]
    if dry_run:
        stdout = f"DRY_RUN would execute: {' '.join(argv)}"
        stderr = ""
        exit_code = 0
    else:
        completed = subprocess.run(
            argv,
            cwd=str(workspace),
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout_sec,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode

    return {
        "id": command["id"],
        "argv": argv,
        "exit_code": int(exit_code),
        "duration_sec": round(time.monotonic() - started, 3),
        "agent_text": redact_sensitive_text(extract_codex_agent_text_from_output(stdout)),
        "stdout_tail": redact_sensitive_text(stdout[-20000:]),
        "stderr_tail": redact_sensitive_text(stderr[-5000:]),
    }


def codex_auth_error(result: dict[str, Any]) -> str | None:
    if result.get("id") != "codex-executor":
        return None
    combined = f"{result.get('stdout_tail', '')}\n{result.get('stderr_tail', '')}".lower()
    auth_markers = [
        "invalid_api_key",
        "incorrect api key",
        "missing bearer or basic authentication",
        "401 unauthorized",
    ]
    if any(marker in combined for marker in auth_markers):
        return "codex authentication failed; refresh EC2 Codex login with a valid OpenAI API key or device auth"
    return None


def extract_codex_agent_text_from_output(output: str) -> str:
    messages: list[str] = []
    for line in str(output or "").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") if isinstance(event, dict) else None
        if not isinstance(item, dict):
            continue
        if item.get("type") == "agent_message" and item.get("text"):
            messages.append(str(item["text"]).strip())
    return "\n\n".join(message for message in messages if message).strip()


def extract_codex_agent_text(result: dict[str, Any]) -> str:
    if result.get("id") != "codex-executor":
        return ""
    if result.get("agent_text"):
        return str(result["agent_text"]).strip()
    return extract_codex_agent_text_from_output(str(result.get("stdout_tail", "")))


def korean_review_reason(reason: str) -> str:
    normalized = str(reason or "").strip()
    translations = {
        "all commands completed within local scaffold bounds": "허용된 작업 범위 안에서 모든 명령이 끝났습니다.",
        "ok": "검토 기준을 통과했습니다.",
    }
    return translations.get(normalized, normalized)


def review_attempt(task: dict[str, Any], command_results: list[dict[str, Any]]) -> Review:
    reasons: list[str] = []
    retry_allowed = False
    for command, result in zip(task["commands"], command_results):
        auth_reason = codex_auth_error(result)
        if auth_reason:
            return Review("BLOCKED", [auth_reason], retry_allowed=False, escalation_required=True)
        if result["exit_code"] != 0 and not command.get("allow_failure", False):
            reasons.append(f"{result['id']} exited {result['exit_code']}")
            retry_allowed = True

    if reasons:
        return Review("FAIL", reasons, retry_allowed=retry_allowed, escalation_required=False)
    return Review("PASS", ["all commands completed within local scaffold bounds"], False, False)


def blocked_result(task: dict[str, Any], workspace: str, started_at: str, reason: str) -> dict[str, Any]:
    finished_at = utc_now()
    review = Review("BLOCKED", [reason], retry_allowed=False, escalation_required=True)
    return {
        "task_id": task.get("task_id", "unknown"),
        "status": "BLOCKED",
        "attempts": 1,
        "started_at": started_at,
        "finished_at": finished_at,
        "workspace": workspace,
        "summary": "\n".join(
            [
                "결론: 막힘",
                f"작업번호: {task.get('task_id', 'unknown')}",
                f"막힌 이유: {reason}",
            ]
        ),
        "commands": [],
        "review": review.to_json(),
    }


def run_controller(task: dict[str, Any], project_root: Path) -> dict[str, Any]:
    started_at = utc_now()
    try:
        workspace = guard_task(task, project_root)
    except RiskBlocked as exc:
        return blocked_result(task, task.get("workspace", ""), started_at, str(exc))

    retry_limit = int(task["limits"]["retry_limit"])
    timeout_sec = int(task["limits"]["max_runtime_sec"])
    dry_run = task["execution_mode"] == "dry_run"
    final_commands: list[dict[str, Any]] = []
    final_review = Review("FAIL", ["not executed"], retry_allowed=False, escalation_required=False)

    for attempt in range(1, retry_limit + 2):
        command_results = [
            run_command(command, workspace, timeout_sec=timeout_sec, dry_run=dry_run)
            for command in task["commands"]
        ]
        final_commands = command_results
        final_review = review_attempt(task, command_results)
        if final_review.status == "PASS":
            break
        if not final_review.retry_allowed:
            break

    finished_at = utc_now()
    status = final_review.status
    return {
        "task_id": task["task_id"],
        "status": status,
        "attempts": attempt,
        "started_at": started_at,
        "finished_at": finished_at,
        "workspace": str(workspace),
        "summary": make_result_summary(task, status, final_review, final_commands),
        "commands": final_commands,
        "review": final_review.to_json(),
    }


def make_result_summary(task: dict[str, Any], status: str, review: Review, command_results: list[dict[str, Any]]) -> str:
    status_label = {
        "PASS": "완료",
        "BLOCKED": "막힘",
        "FAIL": "실패",
    }.get(status, status)
    reason = "; ".join(korean_review_reason(reason) for reason in review.reasons)
    header = "\n".join(
        [
            f"결론: {status_label}",
            f"작업번호: {task['task_id']}",
            f"판정 이유: {reason}",
        ]
    )
    agent_text = "\n\n".join(
        text for text in (extract_codex_agent_text(result) for result in command_results) if text
    ).strip()
    if agent_text:
        return f"{header}\n\n상세 보고:\n{agent_text}"
    return header


def write_result(result: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local Phase 0-3 controller loop.")
    parser.add_argument("task_spec", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        task = load_task(args.task_spec)
        result = run_controller(task, args.project_root.resolve())
        write_result(result, args.out)
        print(result["summary"])
        return 0 if result["status"] == "PASS" else 2
    except (ControllerError, subprocess.TimeoutExpired, OSError, json.JSONDecodeError) as exc:
        fallback = {
            "task_id": "unknown",
            "status": "FAIL",
            "attempts": 1,
            "started_at": utc_now(),
            "finished_at": utc_now(),
            "workspace": str(args.project_root),
            "summary": f"[FAIL] controller error: {exc}",
            "commands": [],
            "review": {
                "status": "FAIL",
                "reasons": [str(exc)],
                "retry_allowed": False,
                "escalation_required": False,
            },
        }
        write_result(fallback, args.out)
        print(fallback["summary"], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
