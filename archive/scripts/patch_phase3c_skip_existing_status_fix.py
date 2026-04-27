import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "http://43.201.227.194:5678"
APP_ID = "i6T6ke3ltKNQzaCl"


API = re.search(
    r'API = "([^"]+)"',
    Path("add_reel_pipeline_minimal.py").read_text(encoding="utf-8"),
).group(1)


def req(path: str, method: str = "GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=60) as res:
        raw = res.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def put_workflow(wf: dict):
    body = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData", {}),
        "pinData": wf.get("pinData", {}),
    }
    if wf.get("meta") is not None:
        body["meta"] = wf["meta"]
    return req(f"/api/v1/workflows/{wf['id']}", method="PUT", payload=body)


wf = req(f"/api/v1/workflows/{APP_ID}")
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_name = f"clean_02_approval_backup_phase3c_skip_status_fix_{ts}.json"
Path(backup_name).write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")

node = next(n for n in wf["nodes"] if n.get("name") == "Phase 3C Scheduler Execute")
params = node.setdefault("parameters", {})
code_key = "jsCode" if "jsCode" in params else "code"
code = params[code_key]

old = """  const guardReason = finalContentGuard(item);
  if (guardReason) {
    summary.blocked.push(block(item, guardReason));
    continue;
  }"""

new = """  const guardReason = finalContentGuard(item);
  if (guardReason) {
    if (guardReason.startsWith('already_')) {
      summary.skipped.push({ test_id: item.test_id, post_type: postType, reason: guardReason });
    } else {
      summary.blocked.push(block(item, guardReason));
    }
    continue;
  }"""

if old not in code:
    raise RuntimeError("Guard handling block not found; aborting")
params[code_key] = code.replace(old, new, 1)

store = wf.setdefault("staticData", {}).setdefault("global", {})
q = store.setdefault("daily_publish_queue", {})

if "phase3c-reel-test-1777118333" in q:
    item = q["phase3c-reel-test-1777118333"]
    item["publish_status"] = "published"
    item.pop("blocked_reason", None)
    item.setdefault("publisher_workflow", "clean_03_publisher")

if "phase3c-feed-test-1777118333" in q:
    item = q["phase3c-feed-test-1777118333"]
    item["publish_status"] = "failed"
    item["failed_reason"] = item.get("failed_reason") or "Request failed with status code 403"
    item.pop("blocked_reason", None)

if "phase3c-carousel-block-1777118333" in q:
    item = q["phase3c-carousel-block-1777118333"]
    item["publish_status"] = "blocked"
    item["blocked_reason"] = "carousel_rate_limit_pending"

put_workflow(wf)
print(json.dumps({"backup": backup_name, "patched": True}, ensure_ascii=False, indent=2))
