from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runtime" / "docker_container_smoke_2026-05-18.json"


def run(cmd: list[str]) -> dict[str, object]:
    completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False, timeout=120)
    return {
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def main() -> int:
    checks = [
        run([sys.executable, "--version"]),
        run([sys.executable, "-m", "json.tool", "reports/hq_continuation_ledger_2026-05-18.json"]),
        run([sys.executable, "scripts/hq_phase3_orchestrator.py"]),
    ]
    report = {
        "status": "PASS" if all(check["returncode"] == 0 for check in checks) else "FAIL",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "container_network_required": False,
        "secret_mount_required": False,
        "production_mutation_performed": False,
        "checks": checks,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "out": str(OUT)}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
