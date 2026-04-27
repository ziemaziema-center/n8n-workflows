import json
import re
import time
import uuid
import urllib.request
import urllib.error

BASE_URL = "http://43.201.227.194:5678/api/v1"
GENERATOR_WORKFLOW_ID = "DGMQEgFXqzeS3sJ5"


def read_api_key():
    text = open("build_queue_system.ps1", "r", encoding="utf-8").read()
    m = re.search(r'\[string\]\$ApiKey = "([^"]+)"', text)
    if not m:
        raise RuntimeError("API key not found")
    return m.group(1)


def request(method, path, api_key, body=None):
    headers = {"X-N8N-API-KEY": api_key}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} -> {e.code} {e.reason}: {body}") from e


def raw_post(url):
    req = urllib.request.Request(url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


api_key = read_api_key()
gen = request("GET", f"/workflows/{GENERATOR_WORKFLOW_ID}", api_key)

path_nodes = {
    "RSS Read1",
    "Limit1",
    "RSS Read2",
    "Limit2",
    "RSS Read3",
    "Limit3",
    "Merge RSS",
    "Normalize Articles",
    "Read articles sheet",
    "Deduplicate + Filter",
    "OpenAI Generate Draft",
    "Parse Draft JSON",
    "Choose 4 Reels + 1 Feed",
    "Normalize Content Unit",
    "Run Sheet Setup",
    "Append Content Queue",
}

webhook_path = f"run-queue-path-{uuid.uuid4().hex[:8]}"

helper_nodes = [
    {
        "id": "webhook",
        "name": "Webhook Trigger",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [-3400, 240],
        "parameters": {
            "httpMethod": "POST",
            "path": webhook_path,
            "options": {},
        },
    }
]

for node in gen["nodes"]:
    if node.get("name") in path_nodes:
        helper_nodes.append(node)

helper_connections = {}
for key, value in gen["connections"].items():
    if key in path_nodes:
        helper_connections[key] = value

helper_connections["Webhook Trigger"] = {"main": [[{"node": "RSS Read1", "type": "main", "index": 0}]]}

helper = {
    "name": "queue_path_bridge",
    "nodes": helper_nodes,
    "connections": helper_connections,
    "settings": {},
}

created = request("POST", "/workflows", api_key, helper)
helper_id = created["id"]
request("POST", f"/workflows/{helper_id}/activate", api_key, {})

raw_post(f"http://43.201.227.194:5678/webhook/{webhook_path}")

latest = None
for _ in range(30):
    time.sleep(2)
    execs = request("GET", f"/executions?workflowId={helper_id}&limit=5&includeData=true", api_key)
    data = execs.get("data", [])
    if data:
        latest = sorted(data, key=lambda x: x["id"], reverse=True)[0]
        if latest.get("status") in {"success", "error", "crashed", "canceled"}:
            break

if not latest:
    raise RuntimeError("No helper execution found")

details = request("GET", f"/executions/{latest['id']}?includeData=true", api_key)
run_data = details.get("data", {}).get("resultData", {}).get("runData", {})

summary = {
    "helper_workflow_id": helper_id,
    "helper_execution_id": latest["id"],
    "helper_execution_status": latest.get("status"),
    "append_content_queue_status": run_data.get("Append Content Queue", [{}])[0].get("executionStatus") if run_data.get("Append Content Queue") else None,
    "setup_status": run_data.get("Run Sheet Setup", [{}])[0].get("executionStatus") if run_data.get("Run Sheet Setup") else None,
}

print(json.dumps(summary, ensure_ascii=False))
