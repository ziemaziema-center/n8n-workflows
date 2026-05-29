from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("TAC_ROOT", Path(__file__).resolve().parents[1]))
DEFAULT_HANDOFF_JSON = ROOT / "runtime" / "handoff" / "current_handoff.json"
DEFAULT_HANDOFF_MD = ROOT / "runtime" / "handoff" / "current_handoff.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    finally:
        tmp_path = Path(tmp_name)
        if tmp_path.exists():
            tmp_path.unlink()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def build_handoff(
    *,
    active_task: dict[str, Any] | None,
    completed_items: list[str],
    pending_items: list[str],
    deferred_gates: list[dict[str, Any]],
    last_validation_result: dict[str, Any],
    next_executable_actions: list[str],
    exact_resume_prompt: str,
) -> dict[str, Any]:
    return {
        "updated_at": utc_now(),
        "active_task": active_task,
        "completed_items": completed_items,
        "pending_items": pending_items,
        "deferred_gates": deferred_gates,
        "last_validation_result": last_validation_result,
        "next_executable_actions": next_executable_actions,
        "exact_resume_prompt": exact_resume_prompt,
        "live_operations_performed": False,
        "secret_values_included": False,
    }


def render_handoff_markdown(handoff: dict[str, Any]) -> str:
    active = handoff.get("active_task") or {}
    lines = [
        "# TAC Runtime Handoff",
        "",
        f"- updated_at: {handoff.get('updated_at')}",
        f"- active_task_id: {active.get('task_id') if isinstance(active, dict) else None}",
        f"- last_validation_status: {handoff.get('last_validation_result', {}).get('status')}",
        "",
        "## Completed Items",
    ]
    lines.extend(f"- {item}" for item in handoff.get("completed_items", []))
    lines.extend(["", "## Pending Items"])
    lines.extend(f"- {item}" for item in handoff.get("pending_items", []))
    lines.extend(["", "## Deferred Gates"])
    gates = handoff.get("deferred_gates", [])
    if gates:
        for gate in gates:
            if isinstance(gate, dict):
                lines.append(f"- {gate.get('name', 'unknown')}: {gate.get('reason', '')}")
            else:
                lines.append(f"- {gate}")
    else:
        lines.append("- none")
    lines.extend(["", "## Next Executable Actions"])
    lines.extend(f"- {item}" for item in handoff.get("next_executable_actions", []))
    lines.extend(["", "## Exact Resume Prompt", "", "```text", str(handoff.get("exact_resume_prompt", "")), "```", ""])
    return "\n".join(lines)


def write_handoff(
    handoff: dict[str, Any],
    *,
    json_path: Path = DEFAULT_HANDOFF_JSON,
    md_path: Path = DEFAULT_HANDOFF_MD,
) -> dict[str, str]:
    atomic_write_json(json_path, handoff)
    atomic_write_text(md_path, render_handoff_markdown(handoff))
    return {"handoff_json_path": str(json_path), "handoff_md_path": str(md_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Write TAC runtime handoff files.")
    parser.add_argument("--json-path", type=Path, default=DEFAULT_HANDOFF_JSON)
    parser.add_argument("--md-path", type=Path, default=DEFAULT_HANDOFF_MD)
    args = parser.parse_args()
    handoff = build_handoff(
        active_task=None,
        completed_items=["initialized runtime handoff writer"],
        pending_items=["claim next task"],
        deferred_gates=[],
        last_validation_result={"status": "NOT_RUN", "command": None, "checked_at": None},
        next_executable_actions=["continue runtime persistence work"],
        exact_resume_prompt="Read AGENTS.md and SESSION_BOOT.md, then continue the next runtime persistence task.",
    )
    paths = write_handoff(handoff, json_path=args.json_path, md_path=args.md_path)
    print(json.dumps({"status": "PASS", **paths}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
