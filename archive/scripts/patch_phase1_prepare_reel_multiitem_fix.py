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
node = next(n for n in wf["nodes"] if n["name"] == "Prepare Reel Preview Payload")
node["parameters"]["jsCode"] = """const collectItems = $items('Collect Reel Images') || [];
const base = (collectItems[$itemIndex] && collectItems[$itemIndex].json) ? collectItems[$itemIndex].json : {};
const videoUrl = String($json.video_url || '');
const videoBase64 = String($json.video_base64 || '');
if (!videoUrl) throw new Error('FFmpeg service did not return video_url');
if (!videoBase64) throw new Error('FFmpeg service did not return video_base64');
const cleanBase = { ...base };
delete cleanBase.images_base64;
delete cleanBase.durations;
return {
  json: {
    ...cleanBase,
    video_url: videoUrl,
    video_base64: videoBase64,
    reel_service_ok: !!$json.ok,
    reel_scene_count: base.reel_scene_count || 6,
    reel_duration_sec: base.reel_duration_sec || 9.6
  }
};"""

body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf.get("connections", {}),
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", {}),
    "pinData": wf.get("pinData", {}),
}
req(f"/api/v1/workflows/{WID}", "PUT", body)
print(json.dumps({"updated": "Prepare Reel Preview Payload", "reason": "multi-item $items indexing fix"}, ensure_ascii=False))
