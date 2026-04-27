import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "http://43.201.227.194:5678"
APP_ID = "i6T6ke3ltKNQzaCl"


def load_api_key() -> str:
    text = Path("add_reel_pipeline_minimal.py").read_text(encoding="utf-8")
    return re.search(r'API = "([^"]+)"', text).group(1)


API = load_api_key()


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


def main():
    wf = req(f"/api/v1/workflows/{APP_ID}")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"clean_02_approval_backup_phase3c_status_fix_{ts}.json"
    Path(backup_name).write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")

    node = next(n for n in wf["nodes"] if n.get("name") == "Phase 3C Scheduler Execute")
    params = node.setdefault("parameters", {})
    code_key = "jsCode" if "jsCode" in params else "code"
    code = params[code_key]

    old_reel = """      item.publish_status = 'published';
      item.published_at = new Date().toISOString();
      item.publisher_workflow = 'clean_03_publisher';
      item.publisher_response = typeof res === 'object' ? res : { response: String(res || '') };
      summary.published.push({ test_id: item.test_id, post_type: postType, publisher: 'clean_03_publisher' });"""

    new_reel = """      item.publish_status = 'triggered';
      item.triggered_at = new Date().toISOString();
      item.publisher_workflow = 'clean_03_publisher';
      item.publisher_execution_confirmed = false;
      item.publisher_response = typeof res === 'object' ? res : { response: String(res || '') };
      summary.triggered = Array.isArray(summary.triggered) ? summary.triggered : [];
      summary.triggered.push({ test_id: item.test_id, post_type: postType, publisher: 'clean_03_publisher' });"""

    if old_reel not in code:
        raise RuntimeError("Reel published-status block not found; aborting without patch")
    code = code.replace(old_reel, new_reel, 1)

    old_error = """    item.publish_status = 'failed';
    item.failed_reason = String(e.message || e);
    item.failed_at = new Date().toISOString();
    summary.errors.push({ test_id: item.test_id, post_type: postType, error: item.failed_reason });"""

    new_error = """    const response = e && e.response ? e.response : {};
    const responseBody = response.body || e.body || {};
    const graphError = responseBody && responseBody.error ? responseBody.error : {};
    item.publish_status = 'failed';
    item.failed_reason = String(e.message || e);
    item.failed_at = new Date().toISOString();
    item.graph_error_message = String(graphError.message || responseBody.message || '');
    item.graph_error_code = graphError.code !== undefined ? graphError.code : '';
    item.graph_error_subcode = graphError.error_subcode !== undefined ? graphError.error_subcode : '';
    item.graph_error_type = String(graphError.type || '');
    item.graph_error_body_present = !!(graphError.message || responseBody.message);
    summary.errors.push({
      test_id: item.test_id,
      post_type: postType,
      error: item.failed_reason,
      graph_error_message: item.graph_error_message,
      graph_error_code: item.graph_error_code,
      graph_error_subcode: item.graph_error_subcode
    });"""

    if old_error not in code:
        raise RuntimeError("Error logging block not found; aborting without patch")
    code = code.replace(old_error, new_error, 1)

    old_summary_line = """    `published: ${summary.published.length}`,"""
    new_summary_line = """    `published: ${summary.published.length}`,
    `triggered: ${(summary.triggered || []).length}`,"""
    if old_summary_line in code:
        code = code.replace(old_summary_line, new_summary_line, 1)

    old_text_block = """    '[PUBLISHED]',
    summary.published.map(x => `- ${x.post_type} / ${x.test_id} / ${x.media_id || x.publisher || ''}`).join('\\n') || '없음',
    '',
    '[BLOCKED]',"""
    new_text_block = """    '[PUBLISHED]',
    summary.published.map(x => `- ${x.post_type} / ${x.test_id} / ${x.media_id || x.publisher || ''}`).join('\\n') || '없음',
    '',
    '[TRIGGERED]',
    (summary.triggered || []).map(x => `- ${x.post_type} / ${x.test_id} / ${x.publisher || ''}`).join('\\n') || '없음',
    '',
    '[BLOCKED]',"""
    if old_text_block in code:
        code = code.replace(old_text_block, new_text_block, 1)

    params[code_key] = code
    put_workflow(wf)

    print(json.dumps({
        "backup": backup_name,
        "workflow": wf["name"],
        "node": node["name"],
        "patched": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
