import json
import re
import time
import uuid
import urllib.error
import urllib.request

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
        raise RuntimeError(e.read().decode("utf-8", errors="ignore")) from e


def raw_post(url):
    req = urllib.request.Request(url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


api_key = read_api_key()
generator_json = request("GET", f"/workflows/{GENERATOR_WORKFLOW_ID}", api_key)
webhook_path = f"run-generator-now-{uuid.uuid4().hex[:8]}"

trigger_name = "When Executed by Another Workflow"
if not any(node.get("name") == trigger_name for node in generator_json.get("nodes", [])):
    generator_json["nodes"].append({
        "id": str(uuid.uuid4()),
        "name": trigger_name,
        "type": "n8n-nodes-base.executeWorkflowTrigger",
        "typeVersion": 1.1,
        "position": [-3400, 240],
        "parameters": {"inputSource": "passthrough"},
    })
generator_json.setdefault("connections", {})[trigger_name] = {
    "main": [[{"node": "RSS Read1", "type": "main", "index": 0}]]
}
filtered_nodes = [
    node for node in generator_json["nodes"]
    if node.get("name") not in {"Schedule Trigger", "Manual Run Webhook"}
]
generator_workflow_min = {
    "name": generator_json["name"],
    "nodes": filtered_nodes,
    "connections": {
        key: value
        for key, value in generator_json["connections"].items()
        if key not in {"Schedule Trigger", "Manual Run Webhook"}
    },
    "settings": {},
}

helper = {
    "name": "run_generator_bridge",
    "nodes": [
        {
            "id": "webhook",
            "name": "Webhook Trigger",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [240, 160],
            "parameters": {
                "httpMethod": "POST",
                "path": webhook_path,
                "options": {},
            },
        },
        {
            "id": "exec",
            "name": "Execute Generator",
            "type": "n8n-nodes-base.executeWorkflow",
            "typeVersion": 1.2,
            "position": [520, 160],
            "parameters": {
                "source": "parameter",
                "workflowJson": generator_workflow_min,
                "options": {
                    "waitForSubWorkflow": True,
                },
                "mode": "all",
            },
        },
        {
            "id": "wrap",
            "name": "Wrap Result",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [800, 160],
            "parameters": {
                "jsCode": "return items.map(item => ({ json: item.json }));"
            },
        },
    ],
    "connections": {
        "Webhook Trigger": {"main": [[{"node": "Execute Generator", "type": "main", "index": 0}]]},
        "Execute Generator": {"main": [[{"node": "Wrap Result", "type": "main", "index": 0}]]},
    },
    "settings": {},
}

created = request("POST", "/workflows", api_key, helper)
helper_id = created["id"]
version_id = created.get("versionId") or created.get("version_id")
activate_body = {"versionId": version_id} if version_id else {}
request("POST", f"/workflows/{helper_id}/activate", api_key, activate_body)

raw_post(f"http://43.201.227.194:5678/webhook/{webhook_path}")

latest = None
for _ in range(30):
    time.sleep(2)
    execs = request("GET", f"/executions?workflowId={GENERATOR_WORKFLOW_ID}&limit=5&includeData=true", api_key)
    data = execs.get("data", [])
    if data:
        latest = sorted(data, key=lambda x: x["id"], reverse=True)[0]
        if latest.get("status") in {"success", "error", "crashed", "canceled"}:
            break

if not latest:
    raise RuntimeError("No generator execution found")

details = request("GET", f"/executions/{latest['id']}?includeData=true", api_key)
run_data = details.get("data", {}).get("resultData", {}).get("runData", {})

summary = {
    "helper_workflow_id": helper_id,
    "generator_execution_id": latest["id"],
    "generator_execution_status": latest.get("status"),
    "append_content_queue_status": run_data.get("Append Content Queue", [{}])[0].get("executionStatus") if run_data.get("Append Content Queue") else None,
    "setup_status": run_data.get("Run Sheet Setup", [{}])[0].get("executionStatus") if run_data.get("Run Sheet Setup") else None,
}

print(json.dumps(summary, ensure_ascii=False))
