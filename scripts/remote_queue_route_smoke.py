from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone


BASE = "http://127.0.0.1:8765"


def request(method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8")
            return {"ok": True, "status": response.status, "body": json.loads(body)}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "body": body}


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    task_id = f"hq-live-queue-route-smoke-{stamp}"
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "health": request("GET", "/health"),
        "queue": request(
            "POST",
            "/queue",
            {
                "task_id": task_id,
                "objective": "Live queue endpoint route smoke; no dispatch.",
                "workspace_path": "/home/ubuntu/workspace/true-autonomous-controller",
                "target_runner": "dry_run",
                "dispatch": True,
            },
        ),
        "handoff": request("POST", "/handoff", {}),
        "live_dispatch_performed": False,
        "production_mutation_performed": False,
    }
    result["live_dispatch_performed"] = bool(
        result["queue"].get("body", {}).get("dispatch", {}).get("live_dispatch_performed")
    )
    result["status"] = (
        "PASS"
        if result["health"]["ok"]
        and result["queue"]["ok"]
        and result["queue"]["body"].get("status") == "QUEUED"
        and result["queue"]["body"].get("dispatch", {}).get("status") in {"STARTED", "ALREADY_RUNNING"}
        and result["handoff"]["ok"]
        and result["handoff"]["body"].get("status") == "HANDOFF_READY"
        else "FAIL"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
