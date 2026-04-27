import json
import re
import uuid
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


api_key = read_api_key()
gen = request("GET", f"/workflows/{GENERATOR_WORKFLOW_ID}", api_key)

trigger_name = "When Executed by Another Workflow"
if not any(node["name"] == trigger_name for node in gen["nodes"]):
    gen["nodes"].append({
        "id": str(uuid.uuid4()),
        "name": trigger_name,
        "type": "n8n-nodes-base.executeWorkflowTrigger",
        "typeVersion": 1.1,
        "position": [-3248, 160],
        "parameters": {"inputSource": "passthrough"},
    })

connections = gen["connections"]
connections[trigger_name] = {"main": [[{"node": "RSS Read1", "type": "main", "index": 0}]]}

body = {
    "name": gen["name"],
    "nodes": gen["nodes"],
    "connections": connections,
    "settings": {},
}

updated = request("PUT", f"/workflows/{GENERATOR_WORKFLOW_ID}", api_key, body)
print(json.dumps({"generator_workflow": updated.get("name"), "trigger_added": True}, ensure_ascii=False))
