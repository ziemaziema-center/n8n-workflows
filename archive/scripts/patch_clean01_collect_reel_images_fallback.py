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
backup_name = f"clean_01_generator_backup_collect_reel_fallback_{ts}.json"
with open(backup_name, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

node = next(n for n in wf["nodes"] if n.get("name") == "Collect Reel Images")
node["parameters"]["jsCode"] = r"""
const FALLBACK_URL = 'https://n8n.mykindredai.com/images/fallback.png';
const MIN_IMAGES = 5;

async function fetchFallbackBase64() {
  const buf = await this.helpers.httpRequest({
    method: 'GET',
    url: FALLBACK_URL,
    encoding: 'arraybuffer',
    timeout: 15000,
  });
  return Buffer.from(buf).toString('base64');
}

const fallbackBase64 = await fetchFallbackBase64.call(this);
const all = $input.all().map(i => i.json || {});
const groups = new Map();
for (const item of all) {
  const id = String(item.test_id || '');
  if (!id) continue;
  if (!groups.has(id)) groups.set(id, []);
  groups.get(id).push(item);
}

const out = [];
for (const [testId, scenes] of groups.entries()) {
  scenes.sort((a,b) => Number(a.scene_index||0) - Number(b.scene_index||0));
  const realImages = scenes.map(x => String(x?.data?.[0]?.b64_json || '')).filter(Boolean);
  const fallbackCount = Math.max(0, MIN_IMAGES - realImages.length);
  const images_base64 = realImages.concat(Array(fallbackCount).fill(fallbackBase64));

  const base = { ...scenes[0] };
  delete base.data;
  out.push({
    json: {
      ...base,
      reel_scene_count: images_base64.length,
      reel_real_image_count: realImages.length,
      reel_fallback_count: fallbackCount,
      reel_fallback_url: fallbackCount > 0 ? FALLBACK_URL : '',
      reel_image_collection_status: fallbackCount > 0 ? 'fallback_filled' : 'success',
      reel_duration_sec: 9.6,
      images_base64,
      durations: Array(images_base64.length).fill(9.6 / images_base64.length)
    }
  });
}

if (!out.length) {
  const base = ($items('Build Simulation Content', 0, 0)?.[0]?.json) || {};
  const testId = String(base.test_id || `fallback-${Date.now()}`);
  const images_base64 = Array(MIN_IMAGES).fill(fallbackBase64);
  out.push({
    json: {
      ...base,
      test_id: testId,
      reel_scene_count: images_base64.length,
      reel_real_image_count: 0,
      reel_fallback_count: MIN_IMAGES,
      reel_fallback_url: FALLBACK_URL,
      reel_image_collection_status: 'fallback_all',
      reel_duration_sec: 9.6,
      images_base64,
      durations: Array(images_base64.length).fill(9.6 / images_base64.length)
    }
  });
}

return out;
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
print(json.dumps({"backup": backup_name, "workflow": "clean_01_generator", "node": "Collect Reel Images"}, ensure_ascii=False, indent=2))
