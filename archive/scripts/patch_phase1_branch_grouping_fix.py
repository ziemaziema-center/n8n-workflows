import json
import re
import urllib.request

BASE = "http://43.201.227.194:5678"
API = re.search(r'API = "([^"]+)"', open("add_reel_pipeline_minimal.py", encoding="utf-8").read()).group(1)
WID = "KPa5tncCc87z2ZsE"


def req(path, method="GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


wf = req(f"/api/v1/workflows/{WID}")

def node(name):
    return next(n for n in wf["nodes"] if n["name"] == name)

node("Normalize Reel Image Output")["parameters"]["jsCode"] = r'''const items = $input.all();
const promptItems = $items('Build Reel Scene Prompts') || [];

return items.map((item, idx) => {
  const source = (promptItems[idx] && promptItems[idx].json) ? promptItems[idx].json : {};
  const j = { ...source, ...(item.json || {}) };
  const hasB64 = !!String(j?.data?.[0]?.b64_json || '').trim();
  const hasUrl = !!String(j.image_url || j?.data?.[0]?.url || '').trim();
  const failed = !!j.error || !!j.code || String(j.status || '').toLowerCase() === 'error' || (!hasB64 && !hasUrl);
  const FALLBACK_URL = "https://n8n.mykindredai.com/images/fallback.png";

  if (failed) {
    return { json: { ...j, image_generation_status: "fallback_due_to_generation_error", image_generation_error: String(j.error || j.message || "unknown"), image_url: FALLBACK_URL } };
  }

  return { json: { ...j, image_generation_status: "success" } };
});'''

node("Build Carousel Media Array")["parameters"]["jsCode"] = r'''const responses = $input.all().map(i => i.json || {});
const promptItems = $items('Build Carousel Prompts') || [];
if (!responses.length || !promptItems.length) return [];

const out = [];
for (let i = 0; i < responses.length; i++) {
  const r = responses[i] || {};
  const p = (promptItems[i] && promptItems[i].json) ? promptItems[i].json : {};
  const position = Number(p.carousel_slide_index || 0);
  if (!(position > 0)) continue;

  const sourceUrl = String(r?.data?.[0]?.url || r?.image_url || '').trim();
  const b64 = String(r?.data?.[0]?.b64_json || '').trim();
  const sourceForSave = sourceUrl || (b64 ? `data:image/png;base64,${b64}` : '');
  if (!sourceForSave) continue;

  const testId = String(p.test_id || Date.now()).replace(/[^a-zA-Z0-9_-]/g, '_');
  const rand = Math.random().toString(36).slice(2, 10);
  const filename = `carousel_${testId}_${String(position).padStart(2, '0')}_${rand}.png`;

  let image_url = '';
  try {
    const saveRes = await this.helpers.httpRequest({
      method: 'POST',
      url: 'http://43.201.227.194:8000/save-image',
      body: { image_url: sourceForSave, filename },
      json: true,
      timeout: 30000,
    });
    image_url = String((saveRes && saveRes.permanent_url) || '').trim();
  } catch (e) {
    image_url = '';
  }

  if (image_url) {
    out.push({
      json: {
        ...p,
        carousel: {
          ...(p.carousel || {}),
          media: [{ position, image_url }]
        },
        position,
        image_url
      }
    });
  }
}
return out;'''

# Remove old side branch Build Carousel Content -> Generate Vape Image.
conns = wf.get("connections", {})
conns["Build Carousel Content"] = {"main": [[{"node": "Build Carousel Prompts", "type": "main", "index": 0}]]}
wf["connections"] = conns

body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf.get("connections", {}),
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", {}),
    "pinData": wf.get("pinData", {}),
}
req(f"/api/v1/workflows/{WID}", "PUT", body)
print(json.dumps({"updated": ["Normalize Reel Image Output", "Build Carousel Media Array", "Build Carousel Content connections"]}, ensure_ascii=False))
