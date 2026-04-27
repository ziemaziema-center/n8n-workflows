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
backup_name = f"clean_02_approval_backup_phase3c_feed_full_response_{ts}.json"
Path(backup_name).write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")

node = next(n for n in wf["nodes"] if n.get("name") == "Phase 3C Scheduler Execute")
params = node.setdefault("parameters", {})
code_key = "jsCode" if "jsCode" in params else "code"
code = params[code_key]

start = code.index("async function publishFeed(item) {")
end = code.index("\n}\n\nconst summary", start) + 3
old = code[start:end]
new = """async function publishFeed(item) {
  const imageUrl = String(item.image_url || item.media_url || '').trim();
  const caption = String(item.caption || '').trim();
  if (!imageUrl || !caption) throw new Error('missing_feed_asset');

  function getStatus(resp) {
    return Number(resp?.statusCode || resp?.status || 200);
  }
  function getBody(resp) {
    return resp && Object.prototype.hasOwnProperty.call(resp, 'body') ? resp.body : resp;
  }
  function throwGraph(stage, resp) {
    const status = getStatus(resp);
    const body = getBody(resp);
    const err = new Error(`${stage}_failed_${status}`);
    err.graphBody = body;
    err.httpStatus = status;
    throw err;
  }

  const createResp = await this.helpers.httpRequest({
    method: 'POST',
    url: `${GRAPH}/${IG_USER_ID}/media`,
    body: { image_url: imageUrl, caption, access_token: ACCESS_TOKEN },
    json: true,
    timeout: 60000,
    returnFullResponse: true,
    ignoreHttpStatusErrors: true,
  });
  if (getStatus(createResp) >= 400) throwGraph('feed_container_create', createResp);
  const create = getBody(createResp);
  const creationId = String(create?.id || '').trim();
  if (!creationId) throw new Error('feed_container_missing_id');
  await new Promise(resolve => setTimeout(resolve, 3000));

  const publishResp = await this.helpers.httpRequest({
    method: 'POST',
    url: `${GRAPH}/${IG_USER_ID}/media_publish`,
    body: { creation_id: creationId, access_token: ACCESS_TOKEN },
    json: true,
    timeout: 60000,
    returnFullResponse: true,
    ignoreHttpStatusErrors: true,
  });
  if (getStatus(publishResp) >= 400) throwGraph('feed_media_publish', publishResp);
  const published = getBody(publishResp);
  const mediaId = String(published?.id || '').trim();
  if (!mediaId) throw new Error('feed_publish_missing_media_id');
  return { media_id: mediaId, creation_id: creationId };
}"""

code = code[:start] + new + code[end:]
code = code.replace(
    "const rawCandidate = response.body || response.data || e.body || e.data || e.description || (e.cause && (e.cause.body || e.cause.data || e.cause.message)) || '';",
    "const rawCandidate = e.graphBody || response.body || response.data || e.body || e.data || e.description || (e.cause && (e.cause.body || e.cause.data || e.cause.message)) || '';",
)
code = code.replace(
    "item.graph_error_type = String(graphError.type || '');",
    "item.graph_error_type = String(graphError.type || '');\n    item.graph_error_http_status = e.httpStatus || response.statusCode || response.status || '';",
)
params[code_key] = code
put_workflow(wf)
print(json.dumps({"backup": backup_name, "patched": True}, ensure_ascii=False, indent=2))
