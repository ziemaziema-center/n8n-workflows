import json
import re
import urllib.request
from datetime import datetime

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
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_name = f"clean_01_generator_backup_carousel_fallback_{ts}.json"
with open(backup_name, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

gen = next(n for n in wf["nodes"] if n.get("name") == "Generate Carousel Images")
gen["continueOnFail"] = True
gen.setdefault("parameters", {}).setdefault("options", {})
gen["parameters"]["options"]["continueOnFail"] = True

media = next(n for n in wf["nodes"] if n.get("name") == "Build Carousel Media Array")
media["parameters"]["jsCode"] = r"""
const FALLBACK_URL = 'https://n8n.mykindredai.com/images/fallback.png';
const responses = $input.all().map(i => i.json || {});
const promptItems = $items('Build Carousel Prompts') || [];
if (!promptItems.length) return [];

const out = [];
const groupStats = new Map();

for (let i = 0; i < promptItems.length; i++) {
  const p = (promptItems[i] && promptItems[i].json) ? promptItems[i].json : {};
  const r = responses[i] || {};
  const position = Number(p.carousel_slide_index || 0);
  if (!(position > 0)) continue;

  const testIdRaw = String(p.test_id || Date.now());
  const testId = testIdRaw.replace(/[^a-zA-Z0-9_-]/g, '_');
  const sourceUrl = String(r?.data?.[0]?.url || r?.image_url || '').trim();
  const b64 = String(r?.data?.[0]?.b64_json || '').trim();
  const hasError = Boolean(r.error || r.code || String(r.status || '').toLowerCase() === 'error');
  const sourceForSave = sourceUrl || (b64 ? `data:image/png;base64,${b64}` : '');

  let image_url = '';
  let usedFallback = false;

  if (sourceForSave && !hasError) {
    const rand = Math.random().toString(36).slice(2, 10);
    const filename = `carousel_${testId}_${String(position).padStart(2, '0')}_${rand}.png`;
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
  }

  if (!image_url) {
    image_url = FALLBACK_URL;
    usedFallback = true;
  }

  const stat = groupStats.get(testIdRaw) || { total: 0, fallback: 0 };
  stat.total += 1;
  if (usedFallback) stat.fallback += 1;
  groupStats.set(testIdRaw, stat);

  out.push({
    json: {
      ...p,
      carousel: {
        ...(p.carousel || {}),
        media: [{ position, image_url }]
      },
      position,
      image_url,
      carousel_image_status: usedFallback ? 'fallback_due_to_generation_error' : 'success',
      carousel_image_error: usedFallback ? String(r.error || r.message || 'missing_or_failed_image') : '',
    }
  });
}

return out.map(item => {
  const testId = String(item.json.test_id || '');
  const stat = groupStats.get(testId) || { total: 1, fallback: 0 };
  return {
    json: {
      ...item.json,
      carousel_image_count: stat.total,
      carousel_fallback_count: stat.fallback,
      carousel_image_collection_status: stat.fallback > 0 ? (stat.fallback === stat.total ? 'fallback_all' : 'fallback_filled') : 'success',
    }
  };
});
""".strip()

body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf.get("connections", {}),
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", {}),
    "pinData": wf.get("pinData", {}),
}
req(f"/api/v1/workflows/{WID}", "PUT", body)
print(json.dumps({
    "backup": backup_name,
    "workflow": "clean_01_generator",
    "nodes": ["Generate Carousel Images", "Build Carousel Media Array"],
}, ensure_ascii=False, indent=2))
