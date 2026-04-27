import json
import re
import time
import urllib.request

BASE_URL = "http://43.201.227.194:5678/api/v1"
SETUP_WORKFLOW_ID = "FipYh2cg4CXocUu5"
GENERATOR_WORKFLOW_ID = "DGMQEgFXqzeS3sJ5"
API_KEY_PATH = "build_queue_system.ps1"


def read_api_key():
    with open(API_KEY_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.search(r'\[string\]\$ApiKey = "([^"]+)"', text)
    if not m:
        raise RuntimeError("API key not found")
    return m.group(1)


def req(method, path, api_key, body=None):
    url = f"{BASE_URL}{path}"
    headers = {"X-N8N-API-KEY": api_key}
    data = None
    if body is not None:
      data = json.dumps(body).encode("utf-8")
      headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=60) as resp:
        payload = resp.read().decode("utf-8")
        if not payload:
            return None
        return json.loads(payload)


def trigger(url):
    request = urllib.request.Request(url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=60) as resp:
        return resp.read().decode("utf-8")


api_key = read_api_key()
setup = req("GET", f"/workflows/{SETUP_WORKFLOW_ID}", api_key)

connections = {
    "When Executed by Another Workflow": {
        "main": [[{"node": "Store Setup Input", "type": "main", "index": 0}]]
    },
    "Store Setup Input": {
        "main": [[{"node": "Switch Setup State", "type": "main", "index": 0}]]
    },
    "Switch Setup State": {
        "main": [
            [{"node": "Create content_queue", "type": "main", "index": 0}],
            [{"node": "Restore Setup Input", "type": "main", "index": 0}],
        ]
    },
    "Create content_queue": {
        "main": [[{"node": "Seed content_queue headers", "type": "main", "index": 0}]]
    },
    "Seed content_queue headers": {
        "main": [[{"node": "Append content_queue headers", "type": "main", "index": 0}]]
    },
    "Append content_queue headers": {
        "main": [[{"node": "Create publish_log", "type": "main", "index": 0}]]
    },
    "Create publish_log": {
        "main": [[{"node": "Seed publish_log headers", "type": "main", "index": 0}]]
    },
    "Seed publish_log headers": {
        "main": [[{"node": "Append publish_log headers", "type": "main", "index": 0}]]
    },
    "Append publish_log headers": {
        "main": [[{"node": "Create telegram_actions", "type": "main", "index": 0}]]
    },
    "Create telegram_actions": {
        "main": [[{"node": "Seed telegram_actions headers", "type": "main", "index": 0}]]
    },
    "Seed telegram_actions headers": {
        "main": [[{"node": "Append telegram_actions headers", "type": "main", "index": 0}]]
    },
    "Append telegram_actions headers": {
        "main": [[{"node": "Create improvement_log", "type": "main", "index": 0}]]
    },
    "Create improvement_log": {
        "main": [[{"node": "Seed improvement_log headers", "type": "main", "index": 0}]]
    },
    "Seed improvement_log headers": {
        "main": [[{"node": "Append improvement_log headers", "type": "main", "index": 0}]]
    },
    "Append improvement_log headers": {
        "main": [[{"node": "Restore Setup Input", "type": "main", "index": 0}]]
    },
}

body = {
    "name": setup["name"],
    "nodes": setup["nodes"],
    "connections": connections,
    "settings": setup.get("settings") or {},
}

updated = req("PUT", f"/workflows/{SETUP_WORKFLOW_ID}", api_key, body)

trigger("http://43.201.227.194:5678/webhook/factory-run-now")

latest = None
for _ in range(20):
    time.sleep(5)
    execs = req("GET", f"/executions?workflowId={GENERATOR_WORKFLOW_ID}&limit=5&includeData=true", api_key)
    data = execs.get("data", [])
    if data:
        latest = sorted(data, key=lambda x: x["id"], reverse=True)[0]
        if latest.get("status") in {"success", "error", "crashed", "canceled"}:
            break

if not latest:
    raise RuntimeError("No generator execution found")

details = req("GET", f"/executions/{latest['id']}?includeData=true", api_key)
run_data = details.get("data", {}).get("resultData", {}).get("runData", {})

summary = {
    "setup_workflow": updated.get("name"),
    "latest_execution_id": latest["id"],
    "latest_execution_status": latest.get("status"),
    "append_content_queue_status": run_data.get("Append Content Queue", [{}])[0].get("executionStatus") if run_data.get("Append Content Queue") else None,
    "setup_node_status": run_data.get("Run Sheet Setup", [{}])[0].get("executionStatus") if run_data.get("Run Sheet Setup") else None,
}

print(json.dumps(summary, ensure_ascii=False))
