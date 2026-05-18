from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> dict[str, object]:
    completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def main() -> int:
    checks = [
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests"]),
        run([sys.executable, "-m", "json.tool", "reports/hq_continuation_ledger_2026-05-18.json"]),
        run([sys.executable, "-m", "json.tool", "workflows/tac_telegram_commands.json"]),
        run([sys.executable, "-m", "json.tool", "workflows/tac_controller_webhook.json"]),
    ]
    report = {
        "status": "PASS" if all(check["returncode"] == 0 for check in checks) else "FAIL",
        "checks": checks,
        "live_operations_performed": False,
    }
    out = ROOT / "runtime" / "offline_validation_latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(out)}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
