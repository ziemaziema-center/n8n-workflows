from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_TRANSITIONS: dict[str, set[str]] = {
    "QUEUED": {"RUNNING", "CANCELLED", "DEFERRED_GATE"},
    "RUNNING": {"PASS", "FAIL", "DEFERRED_GATE", "CANCELLED"},
    "FAIL": {"QUEUED", "DEFERRED_GATE", "CANCELLED"},
    "DEFERRED_GATE": {"QUEUED", "CANCELLED"},
    "PASS": set(),
    "CANCELLED": set(),
}

RUNNER_TRANSITIONS: dict[str, set[str]] = {
    "IDLE": {"RUNNING", "PAUSED", "STOPPING", "ERROR"},
    "RUNNING": {"IDLE", "PAUSED", "STOPPING", "ERROR"},
    "PAUSED": {"IDLE", "RUNNING", "STOPPING"},
    "STOPPING": {"STOPPED", "IDLE"},
    "STOPPED": {"IDLE"},
    "ERROR": {"IDLE", "STOPPING"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_transition(current: str, next_status: str, transitions: dict[str, set[str]]) -> None:
    if current not in transitions:
        raise ValueError(f"unknown state: {current}")
    if next_status not in transitions[current]:
        raise ValueError(f"invalid transition: {current} -> {next_status}")


def transition_task(task: dict[str, Any], next_status: str, *, actor: str, reason: str) -> dict[str, Any]:
    current = str(task.get("status", "QUEUED"))
    validate_transition(current, next_status, TASK_TRANSITIONS)
    updated = dict(task)
    updated["status"] = next_status
    lifecycle = list(updated.get("lifecycle", []))
    lifecycle.append(
        {
            "from": current,
            "to": next_status,
            "actor": actor,
            "reason": reason,
            "at": utc_now(),
        }
    )
    updated["lifecycle"] = lifecycle
    if next_status == "RUNNING":
        updated["started_at"] = updated.get("started_at") or utc_now()
    if next_status in {"PASS", "FAIL", "DEFERRED_GATE", "CANCELLED"}:
        updated["finished_at"] = utc_now()
    return updated


def record_heartbeat(state: dict[str, Any], *, runner_status: str, phase: str, log_path: str | None) -> dict[str, Any]:
    current = str(state.get("runner_status", "IDLE"))
    if current != runner_status:
        validate_transition(current, runner_status, RUNNER_TRANSITIONS)
    updated = dict(state)
    updated["runner_status"] = runner_status
    updated["current_phase"] = phase
    updated["last_heartbeat_at"] = utc_now()
    updated["last_log_path"] = log_path
    return updated


def retry_decision(review: dict[str, Any], *, retry_count: int, max_retries: int) -> dict[str, Any]:
    decision = str(review.get("decision", "FAIL"))
    retry_allowed = bool(review.get("retry_allowed")) and retry_count < max_retries
    next_status = "QUEUED" if decision == "FAIL" and retry_allowed else decision
    if next_status == "HUMAN_APPROVAL_REQUIRED":
        next_status = "DEFERRED_GATE"
    return {
        "decision": decision,
        "retry_allowed": retry_allowed,
        "retry_count": retry_count,
        "max_retries": max_retries,
        "next_status": next_status,
        "reason": str(review.get("reason", "")),
    }


def runtime_event(
    *,
    task_id: str,
    event_type: str,
    actor: str,
    status: str,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    created_at = utc_now()
    return {
        "event_id": f"{task_id}:{event_type}:{created_at}",
        "task_id": task_id,
        "event_type": event_type,
        "actor": actor,
        "status": status,
        "message": message,
        "metadata": metadata or {},
        "created_at": created_at,
        "live_operation": False,
        "secret_values_included": False,
    }


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def build_continuation_handoff(
    *,
    task_id: str,
    completed_items: list[str],
    deferred_gates: list[dict[str, Any]],
    next_actions: list[str],
    validation_commands: list[str],
    final_report_path: str,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "updated_at": utc_now(),
        "completed_items": completed_items,
        "deferred_gates": deferred_gates,
        "next_executable_subtasks": next_actions,
        "validation_commands": validation_commands,
        "final_report_path": final_report_path,
        "resume_prompt": (
            "Read AGENTS.md, SESSION_BOOT.md, agent_memory files, and this handoff. "
            "Continue the next executable subtask without stopping on a single deferred gate."
        ),
        "live_operations_performed": False,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
