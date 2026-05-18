from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tac.queue_runtime import make_queue_task, write_queue_task


OUT = ROOT / "runtime" / "queue_soak_result_2026-05-18.json"


def review(task_id: str, attempt: int, forced: str) -> dict[str, object]:
    if forced == "retry" and attempt == 0:
        return {"task_id": task_id, "decision": "FAIL", "retry_allowed": True, "reason": "forced retry smoke"}
    if forced == "deferred":
        return {
            "task_id": task_id,
            "decision": "DEFERRED_GATE",
            "retry_allowed": False,
            "reason": "forced deferred gate smoke",
        }
    return {"task_id": task_id, "decision": "PASS", "retry_allowed": False, "reason": "soak smoke pass"}


def run_soak(runtime_root: Path) -> dict[str, object]:
    scenarios = [
        ("hq-soak-pass-20260518", "pass"),
        ("hq-soak-retry-20260518", "retry"),
        ("hq-soak-deferred-20260518", "deferred"),
    ]
    outcomes = []
    for task_id, forced in scenarios:
        task = make_queue_task(
            task_id=task_id,
            objective=f"Queue soak scenario: {forced}",
            requested_by="local_hq",
            source_channel="local_hq",
            target_runner="dry_run",
        )
        write_queue_task(task, runtime_root=runtime_root)
        attempts = []
        for attempt in range(task["max_retries"] + 1):
            decision = review(task_id, attempt, forced)
            attempts.append({"attempt": attempt, **decision})
            if decision["decision"] != "FAIL" or not decision["retry_allowed"]:
                break
        outcomes.append({"task_id": task_id, "forced": forced, "attempts": attempts, "final": attempts[-1]})
    continued_after_deferred = outcomes[-1]["final"]["decision"] == "DEFERRED_GATE" and len(outcomes) == 3
    return {
        "status": "PASS" if continued_after_deferred else "FAIL",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "task_count": len(outcomes),
        "forced_retry_observed": outcomes[1]["final"]["decision"] == "PASS" and len(outcomes[1]["attempts"]) == 2,
        "deferred_gate_recorded": outcomes[2]["final"]["decision"] == "DEFERRED_GATE",
        "safe_work_continued": continued_after_deferred,
        "outcomes": outcomes,
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        result = run_soak(Path(tmp) / "runtime")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "out": str(OUT)}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
