from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PASS = "PASS"
FAIL = "FAIL"
DEFERRED_GATE = "DEFERRED_GATE"
HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"


def classify(log_text: str, max_retries: int, retry_count: int) -> dict[str, object]:
    lowered = log_text.lower()
    if "deferred_gate" in lowered:
        return {
            "decision": DEFERRED_GATE,
            "retry_allowed": False,
            "reason": "log contains DEFERRED_GATE",
        }
    if "secret" in lowered or "credential" in lowered:
        return {
            "decision": HUMAN_APPROVAL_REQUIRED,
            "retry_allowed": False,
            "reason": "credential/secret surface requires human approval",
        }
    if "traceback" in lowered or "failed" in lowered or "error" in lowered:
        return {
            "decision": FAIL,
            "retry_allowed": retry_count < max_retries,
            "reason": "failure marker found in log",
        }
    return {
        "decision": PASS,
        "retry_allowed": False,
        "reason": "no failure marker found",
    }


def write_review(
    log_path: Path,
    out_path: Path,
    max_retries: int = 3,
    retry_count: int = 0,
    ledger_path: Path | None = None,
) -> dict[str, object]:
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    result = {
        "log_path": str(log_path),
        "max_retries": max_retries,
        "retry_count": retry_count,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        **classify(log_text, max_retries=max_retries, retry_count=retry_count),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if ledger_path is not None:
      ledger_path.parent.mkdir(parents=True, exist_ok=True)
      ledger_update = {
          "last_reviewer_result": result,
          "safe_next_action": "retry if retry_allowed else update deferred gate or final report",
          "live_operations_performed": False,
      }
      ledger_path.write_text(json.dumps(ledger_update, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: hq_reviewer_loop_template.py <log_path> <out_path> [max_retries] [retry_count] [ledger_update_path]", file=sys.stderr)
        return 2
    max_retries = int(argv[3]) if len(argv) > 3 else 3
    retry_count = int(argv[4]) if len(argv) > 4 else 0
    ledger_path = Path(argv[5]) if len(argv) > 5 else None
    result = write_review(Path(argv[1]), Path(argv[2]), max_retries=max_retries, retry_count=retry_count, ledger_path=ledger_path)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["decision"] in {PASS, DEFERRED_GATE, HUMAN_APPROVAL_REQUIRED} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
