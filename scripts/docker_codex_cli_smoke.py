from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runtime" / "docker_codex_cli_smoke_2026-05-18.json"


def main() -> int:
    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--memory",
        "2g",
        "--cpus",
        "2",
        "--entrypoint",
        "codex",
        "tac-codex-runner:codex",
        "--version",
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, timeout=60)
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if completed.returncode == 0 and "0.130.0" in completed.stdout else "FAIL",
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr_tail": completed.stderr[-1000:],
        "network": "none",
        "secret_mount": False,
        "live_codex_task_executed": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(OUT)}, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
