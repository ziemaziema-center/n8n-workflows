import json
import re
import time
import urllib.error
import urllib.request

BASE_URL = "http://43.201.227.194:5678/api/v1"
DOC_ID = "17pM1TO62U8wklrpmC5ZDPHNeNMNUT18hsOP9GJQ-d4Q"


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


def raw_post(url):
    req = urllib.request.Request(url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def header_schema(fields):
    return [
        {
            "id": f,
            "displayName": f,
            "required": False,
            "defaultMatch": False,
            "display": True,
            "type": "string",
            "canBeUsedToMatch": True,
            "removed": False,
        }
        for f in fields
    ]


def create_sheet_node(name, title, x, y):
    return {
        "id": name.replace(" ", "_") + "_create",
        "name": name,
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4,
        "position": [x, y],
        "credentials": {"googleApi": {"id": "0qLoNOqd9HAUAPaN", "name": "Google Sheets account"}},
        "parameters": {
            "authentication": "serviceAccount",
            "resource": "sheet",
            "operation": "create",
            "documentId": {"__rl": True, "value": DOC_ID, "mode": "id"},
            "title": title,
        },
    }


def append_headers_node(name, sheet_name, x, y, fields):
    return {
        "id": name.replace(" ", "_") + "_append",
        "name": name,
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4,
        "position": [x, y],
        "credentials": {"googleApi": {"id": "0qLoNOqd9HAUAPaN", "name": "Google Sheets account"}},
        "parameters": {
            "authentication": "serviceAccount",
            "resource": "sheet",
            "operation": "append",
            "documentId": {"__rl": True, "value": DOC_ID, "mode": "id"},
            "sheetName": {"__rl": True, "value": sheet_name, "mode": "name"},
            "columns": {
                "mappingMode": "autoMapInputData",
                "value": {},
                "matchingColumns": [],
                "schema": header_schema(fields),
                "attemptToConvertTypes": False,
                "convertFieldsToString": False,
            },
            "options": {},
        },
    }


api_key = read_api_key()

manual_setup = {
    "name": "00_Sheet_Setup_runtime_manual",
    "nodes": [
        {
            "id": "webhook_trigger",
            "name": "Webhook Trigger",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [240, 160],
            "parameters": {
                "httpMethod": "POST",
                "path": "sheet-setup-runtime",
                "options": {},
            },
        },
        create_sheet_node("Create content_queue", "content_queue", 520, 80),
        {
            "id": "seed_content_queue",
            "name": "Seed content_queue headers",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [760, 80],
            "parameters": {
                "jsCode": "return [{ json: { content_id: 'content_id', platform: 'platform', title: 'title', body: 'body', subtitles: 'subtitles', source_url: 'source_url', hashtags: 'hashtags', image_url: 'image_url', video_url: 'video_url', time_slot: 'time_slot', status: 'status', telegram_message_id: 'telegram_message_id' } }];"
            },
        },
        append_headers_node(
            "Append content_queue headers",
            "content_queue",
            980,
            80,
            ["content_id", "platform", "title", "body", "subtitles", "source_url", "hashtags", "image_url", "video_url", "time_slot", "status", "telegram_message_id"],
        ),
        create_sheet_node("Create publish_log", "publish_log", 520, 240),
        {
            "id": "seed_publish_log",
            "name": "Seed publish_log headers",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [760, 240],
            "parameters": {
                "jsCode": "return [{ json: { content_id: 'content_id', publish_id: 'publish_id', platform: 'platform', success: 'success', error: 'error', timestamp: 'timestamp' } }];"
            },
        },
        append_headers_node(
            "Append publish_log headers",
            "publish_log",
            980,
            240,
            ["content_id", "publish_id", "platform", "success", "error", "timestamp"],
        ),
        create_sheet_node("Create telegram_actions", "telegram_actions", 520, 400),
        {
            "id": "seed_telegram_actions",
            "name": "Seed telegram_actions headers",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [760, 400],
            "parameters": {
                "jsCode": "return [{ json: { content_id: 'content_id', action: 'action', timestamp: 'timestamp' } }];"
            },
        },
        append_headers_node(
            "Append telegram_actions headers",
            "telegram_actions",
            980,
            400,
            ["content_id", "action", "timestamp"],
        ),
        create_sheet_node("Create improvement_log", "improvement_log", 520, 560),
        {
            "id": "seed_improvement_log",
            "name": "Seed improvement_log headers",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [760, 560],
            "parameters": {
                "jsCode": "return [{ json: { period: 'period', suggestion: 'suggestion', approved: 'approved', applied_version: 'applied_version' } }];"
            },
        },
        append_headers_node(
            "Append improvement_log headers",
            "improvement_log",
            980,
            560,
            ["period", "suggestion", "approved", "applied_version"],
        ),
    ],
    "connections": {
        "Webhook Trigger": {"main": [[{"node": "Create content_queue", "type": "main", "index": 0}]]},
        "Create content_queue": {"main": [[{"node": "Seed content_queue headers", "type": "main", "index": 0}]]},
        "Seed content_queue headers": {"main": [[{"node": "Append content_queue headers", "type": "main", "index": 0}]]},
        "Append content_queue headers": {"main": [[{"node": "Create publish_log", "type": "main", "index": 0}]]},
        "Create publish_log": {"main": [[{"node": "Seed publish_log headers", "type": "main", "index": 0}]]},
        "Seed publish_log headers": {"main": [[{"node": "Append publish_log headers", "type": "main", "index": 0}]]},
        "Append publish_log headers": {"main": [[{"node": "Create telegram_actions", "type": "main", "index": 0}]]},
        "Create telegram_actions": {"main": [[{"node": "Seed telegram_actions headers", "type": "main", "index": 0}]]},
        "Seed telegram_actions headers": {"main": [[{"node": "Append telegram_actions headers", "type": "main", "index": 0}]]},
        "Append telegram_actions headers": {"main": [[{"node": "Create improvement_log", "type": "main", "index": 0}]]},
        "Create improvement_log": {"main": [[{"node": "Seed improvement_log headers", "type": "main", "index": 0}]]},
        "Seed improvement_log headers": {"main": [[{"node": "Append improvement_log headers", "type": "main", "index": 0}]]},
    },
    "settings": {},
}

created = request("POST", "/workflows", api_key, manual_setup)
manual_workflow_id = created["id"]

request("POST", f"/workflows/{manual_workflow_id}/activate", api_key, {})

raw_post("http://43.201.227.194:5678/webhook/sheet-setup-runtime")

execution_id = None
execution = None
for _ in range(30):
    time.sleep(2)
    execs = request("GET", f"/executions?workflowId={manual_workflow_id}&limit=5&includeData=true", api_key)
    data = execs.get("data", [])
    if data:
        execution = sorted(data, key=lambda x: x["id"], reverse=True)[0]
        execution_id = execution["id"]
        if execution.get("status") in {"success", "error", "crashed", "canceled"}:
            break

if not execution_id:
    raise RuntimeError("No setup execution found")

details = request("GET", f"/executions/{execution_id}?includeData=true", api_key)
run_data = details.get("data", {}).get("resultData", {}).get("runData", {})

print(json.dumps({
    "manual_setup_workflow_id": manual_workflow_id,
    "execution_id": execution_id,
    "create_content_queue": run_data.get("Create content_queue", [{}])[0].get("executionStatus") if run_data.get("Create content_queue") else None,
    "append_improvement_log": run_data.get("Append improvement_log headers", [{}])[0].get("executionStatus") if run_data.get("Append improvement_log headers") else None,
}, ensure_ascii=False))
