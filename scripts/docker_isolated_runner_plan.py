from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runtime" / "docker_runner_plan_2026-05-18.json"


PLAN = {
    "status": "PLAN_READY",
    "live_container_started": False,
    "image_name": "tac-codex-runner:dry-run",
    "workspace_mount": {
        "host": "/home/ubuntu/workspace/<project>",
        "container": "/workspace",
        "mode": "rw",
    },
    "secret_policy": "no .env, key, token, credential, private key, or home directory mount",
    "network_policy": "disabled by default; enable only per approved task",
    "limits": {
        "max_runtime_sec": 1800,
        "max_retries": 3,
        "memory": "2g",
        "cpus": "2",
    },
    "runner_command_shape": [
        "docker",
        "run",
        "--rm",
        "--network=none",
        "--memory=2g",
        "--cpus=2",
        "-v",
        "/home/ubuntu/workspace/<project>:/workspace",
        "tac-codex-runner:dry-run",
        "codex",
        "--ask-for-approval",
        "never",
        "exec",
        "--sandbox",
        "danger-full-access",
        "--json",
        "<prompt>",
    ],
}


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(PLAN, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "plan": str(OUT), "live_container_started": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
