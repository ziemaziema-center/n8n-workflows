import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "http://43.201.227.194:5678"
ROOT = Path.cwd()

WORKFLOWS = {
    "clean_01_generator": "KPa5tncCc87z2ZsE",
    "clean_02_approval": "i6T6ke3ltKNQzaCl",
    "clean_03_publisher": "TiD7fxWCuAX9mpt6",
    "clean_04_carousel_publisher": "w9e3wiyca6qZUS4r",
    "actual_07_auto_debugger_collector": "potLIY8EREC9hXYl",
}

GITHUB_OWNER = "ziemaziema-center"
GITHUB_REPO = "n8n-workflows"
GITHUB_CREDENTIAL = {"githubApi": {"id": "O7eKphCyetHxJPQk", "name": "GitHub account"}}


def load_api_key() -> str:
    text = (ROOT / "add_reel_pipeline_minimal.py").read_text(encoding="utf-8")
    return re.search(r'API = "([^"]+)"', text).group(1)


API = load_api_key()


def req(path: str, method: str = "GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=60) as res:
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
    return req(f"/api/v1/workflows/{wf['id']}", "PUT", body)


SECRET_KEY_RE = re.compile(r"(access[_-]?token|api[_-]?key|authorization|bearer|password|credential|secret|token)", re.I)
SECRET_VALUE_RES = [
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.I),
    re.compile(r"EAAR[A-Za-z0-9_\-]+"),
    re.compile(r"sk-proj-[A-Za-z0-9_\-]+"),
    re.compile(r"[0-9]{8,12}:[A-Za-z0-9_\-]{25,}"),
    re.compile(r"[A-Za-z0-9_\-]{90,}"),
]


def redact_string(value: str) -> str:
    out = value
    for rx in SECRET_VALUE_RES:
        out = rx.sub("REDACTED", out)
    out = re.sub(r"(access_token=)[^&\s]+", r"\1REDACTED", out, flags=re.I)
    return out


def sanitize(obj, key=""):
    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            if k == "credentials":
                clean[k] = "REDACTED"
            elif SECRET_KEY_RE.search(str(k)):
                clean[k] = "REDACTED"
            else:
                clean[k] = sanitize(v, k)
        return clean
    if isinstance(obj, list):
        return [sanitize(v, key) for v in obj]
    if isinstance(obj, str):
        if SECRET_KEY_RE.search(key):
            return "REDACTED"
        return redact_string(obj)
    return obj


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def repo_setup_and_exports():
    for d in [
        "workflows",
        "backups",
        "logs/executions",
        "logs/errors",
        "debug-reports/auto_debugger",
        "meta",
    ]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)

    date_dir = ROOT / "backups" / datetime.now().strftime("%Y-%m-%d")
    exported = []
    backups = []
    for name in ["clean_01_generator", "clean_02_approval", "clean_03_publisher", "clean_04_carousel_publisher"]:
        wf = req(f"/api/v1/workflows/{WORKFLOWS[name]}")
        safe = sanitize(wf)
        workflow_path = ROOT / "workflows" / f"{name}.json"
        backup_path = date_dir / f"{name}_backup.json"
        write_json(workflow_path, safe)
        write_json(backup_path, safe)
        exported.append(str(workflow_path.relative_to(ROOT)))
        backups.append(str(backup_path.relative_to(ROOT)))

    meta = {
        "generated_at": datetime.now().isoformat(),
        "n8n_base": BASE,
        "github_repo": f"{GITHUB_OWNER}/{GITHUB_REPO}",
        "active_workflows": {k: WORKFLOWS[k] for k in ["clean_01_generator", "clean_02_approval", "clean_03_publisher", "clean_04_carousel_publisher"]},
        "security": "workflow exports/backups are sanitized; credentials and token-like values are redacted",
    }
    write_json(ROOT / "meta" / "backup_manifest.json", meta)
    return exported, backups


def github_file_node(name, position, path_expr, content_expr, commit_expr, continue_on_fail=False):
    node = {
        "id": name.lower().replace(" ", "-"),
        "name": name,
        "type": "n8n-nodes-base.github",
        "typeVersion": 1,
        "position": position,
        "parameters": {
            "resource": "file",
            "owner": {"__rl": True, "value": GITHUB_OWNER, "mode": "list"},
            "repository": {"__rl": True, "value": GITHUB_REPO, "mode": "list"},
            "filePath": path_expr,
            "fileContent": content_expr,
            "commitMessage": commit_expr,
        },
        "credentials": GITHUB_CREDENTIAL,
    }
    if continue_on_fail:
        node["continueOnFail"] = True
    return node


def build_actual_08():
    code = r"""
const input = $json.body && typeof $json.body === 'object' ? $json.body : $json;
const now = new Date();
function pad(n) { return String(n).padStart(2, '0'); }
function stamp(d) {
  return `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}_${String(d.getMilliseconds()).padStart(3, '0')}`;
}
function redact(value) {
  let s = typeof value === 'string' ? value : JSON.stringify(value ?? '');
  s = s.replace(/Bearer\s+[A-Za-z0-9._\-]+/gi, 'Bearer REDACTED');
  s = s.replace(/(access_token=)[^&\s]+/gi, '$1REDACTED');
  s = s.replace(/("access_token"\s*:\s*")[^"]+/gi, '$1REDACTED');
  s = s.replace(/("Authorization"\s*:\s*")[^"]+/gi, '$1REDACTED');
  s = s.replace(/(sk-proj-[A-Za-z0-9_\-]+)/g, 'REDACTED');
  s = s.replace(/([0-9]{8,12}:[A-Za-z0-9_\-]{25,})/g, 'REDACTED');
  s = s.replace(/([A-Za-z0-9_\-]{90,})/g, 'REDACTED');
  return s;
}
const isError = input.is_error === true || input.status === 'error' || !!input.error;
const ts = stamp(now);
const payload = {
  captured_at: now.toISOString(),
  source: input.source || 'n8n',
  workflow_name: input.workflow_name || input.workflowName || '',
  workflow_id: input.workflow_id || input.workflowId || '',
  execution_id: input.execution_id || input.executionId || '',
  status: input.status || (isError ? 'error' : 'success'),
  is_error: isError,
  data: input,
};
const sanitized = JSON.parse(redact(payload));
return [{
  json: {
    ...sanitized,
    github_execution_path: `logs/executions/${ts}_${sanitized.workflow_name || 'workflow'}_${sanitized.execution_id || 'execution'}.json`.replace(/[^A-Za-z0-9_./-]/g, '_'),
    github_error_path: `logs/errors/${ts}_${sanitized.workflow_name || 'workflow'}_${sanitized.execution_id || 'execution'}.json`.replace(/[^A-Za-z0-9_./-]/g, '_'),
    github_content: JSON.stringify(sanitized, null, 2),
    commit_message: `debug: github_logger - stored ${isError ? 'error' : 'execution'} log`
  }
}];
"""
    wf = {
        "name": "actual_08_github_logger",
        "nodes": [
            {
                "id": "github-log-intake",
                "name": "GitHub Log Intake",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [0, 0],
                "parameters": {"path": "github-log-intake", "httpMethod": "POST", "responseMode": "lastNode", "options": {}},
                "webhookId": "actual-08-github-log-intake",
            },
            {
                "id": "prepare-github-log",
                "name": "Prepare GitHub Log",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [260, 0],
                "parameters": {"jsCode": code},
            },
            github_file_node(
                "Save Execution Log",
                [520, 0],
                "={{$json.github_execution_path}}",
                "={{$json.github_content}}",
                "={{$json.commit_message}}",
                continue_on_fail=False,
            ),
            {
                "id": "if-error-log",
                "name": "If Error Log",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [760, 0],
                "parameters": {
                    "conditions": {
                        "options": {"caseSensitive": True, "typeValidation": "strict", "version": 2},
                        "conditions": [
                            {
                                "leftValue": "={{$json.is_error}}",
                                "rightValue": True,
                                "operator": {"type": "boolean", "operation": "true", "singleValue": True},
                            }
                        ],
                        "combinator": "and",
                    },
                    "options": {},
                },
            },
            github_file_node(
                "Save Error Log",
                [1000, -80],
                "={{$json.github_error_path}}",
                "={{$json.github_content}}",
                "={{$json.commit_message}}",
                continue_on_fail=False,
            ),
        ],
        "connections": {
            "GitHub Log Intake": {"main": [[{"node": "Prepare GitHub Log", "type": "main", "index": 0}]]},
            "Prepare GitHub Log": {"main": [[{"node": "Save Execution Log", "type": "main", "index": 0}]]},
            "Save Execution Log": {"main": [[{"node": "If Error Log", "type": "main", "index": 0}]]},
            "If Error Log": {"main": [[{"node": "Save Error Log", "type": "main", "index": 0}], []]},
        },
        "settings": {
            "executionOrder": "v1",
            "timezone": "Asia/Seoul",
            "saveExecutionProgress": True,
            "saveDataSuccessExecution": "all",
            "saveDataErrorExecution": "all",
            "callerPolicy": "workflowsFromSameOwner",
            "availableInMCP": False,
        },
        "staticData": {},
    }
    existing = req("/api/v1/workflows?limit=100").get("data", [])
    current = next((x for x in existing if x.get("name") == "actual_08_github_logger"), None)
    if current:
        old = req(f"/api/v1/workflows/{current['id']}")
        write_json(ROOT / "backups" / datetime.now().strftime("%Y-%m-%d") / "actual_08_github_logger_backup.json", sanitize(old))
        body = {**wf, "staticData": old.get("staticData", {})}
        body.pop("id", None)
        updated = req(f"/api/v1/workflows/{current['id']}", "PUT", body)
        workflow_id = updated.get("id", current["id"])
    else:
        created = req("/api/v1/workflows", "POST", wf)
        workflow_id = created["id"]
    req(f"/api/v1/workflows/{workflow_id}/activate", "POST", {})
    exported = sanitize(req(f"/api/v1/workflows/{workflow_id}"))
    write_json(ROOT / "workflows" / "actual_08_github_logger.json", exported)
    return workflow_id


def patch_actual_07():
    wf = req(f"/api/v1/workflows/{WORKFLOWS['actual_07_auto_debugger_collector']}")
    write_json(ROOT / "backups" / datetime.now().strftime("%Y-%m-%d") / "actual_07_auto_debugger_collector_backup.json", sanitize(wf))
    code_node = next(n for n in wf["nodes"] if n.get("name") == "Run Auto Debugger v3")
    code = code_node["parameters"].get("jsCode") or code_node["parameters"].get("code")
    if "github_error_hash: event.error_hash" not in code:
        code = code.replace(
            "token_redaction_confirmed: true\n}} }}];",
            "token_redaction_confirmed: true,\n  github_error_hash: event.error_hash,\n  github_report_content: JSON.stringify(logItem, null, 2)\n}} }}];",
        )
        code_node["parameters"]["jsCode"] = code
    names = {n.get("name") for n in wf["nodes"]}
    if "Push Debug Report to GitHub" not in names:
        wf["nodes"].append(
            github_file_node(
                "Push Debug Report to GitHub",
                [640, 100],
                "=debug-reports/auto_debugger/{{$json.github_error_hash}}.json",
                "={{$json.github_report_content || JSON.stringify($json, null, 2)}}",
                "=debug: auto_debugger - stored error report",
                continue_on_fail=True,
            )
        )
        wf.setdefault("connections", {}).setdefault("Run Auto Debugger v3", {"main": [[]]})
        wf["connections"]["Run Auto Debugger v3"]["main"][0].append({"node": "Push Debug Report to GitHub", "type": "main", "index": 0})
    put_workflow(wf)
    req(f"/api/v1/workflows/{wf['id']}/activate", "POST", {})
    exported = sanitize(req(f"/api/v1/workflows/{wf['id']}"))
    write_json(ROOT / "workflows" / "actual_07_auto_debugger_collector.json", exported)


def main():
    exported, backups = repo_setup_and_exports()
    actual_08_id = build_actual_08()
    patch_actual_07()
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "exported": exported + ["workflows/actual_07_auto_debugger_collector.json", "workflows/actual_08_github_logger.json"],
        "backups": backups + [
            f"backups/{datetime.now().strftime('%Y-%m-%d')}/actual_07_auto_debugger_collector_backup.json"
        ],
        "actual_08_workflow_id": actual_08_id,
        "github_repo": f"{GITHUB_OWNER}/{GITHUB_REPO}",
    }
    write_json(ROOT / "meta" / "github_backup_logging_setup.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
