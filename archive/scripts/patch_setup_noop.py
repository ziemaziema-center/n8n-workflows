import json
import re
import urllib.request

BASE_URL = "http://43.201.227.194:5678/api/v1"
SETUP_WORKFLOW_ID = "FipYh2cg4CXocUu5"


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
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None


api_key = read_api_key()
wf = request("GET", f"/workflows/{SETUP_WORKFLOW_ID}", api_key)

store = next(node for node in wf["nodes"] if node["name"] == "Store Setup Input")
store["parameters"]["jsCode"] = """const store = $getWorkflowStaticData('global');\nstore.pending_content_items = JSON.stringify(items.map((item) => item.json));\nstore.sheet_setup_done = true;\n\nreturn [{ json: { sheet_setup_state: 'continue' } }];"""

body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": {},
}

updated = request("PUT", f"/workflows/{SETUP_WORKFLOW_ID}", api_key, body)
print(json.dumps({"setup_workflow": updated.get("name"), "noop_enabled": True}, ensure_ascii=False))
