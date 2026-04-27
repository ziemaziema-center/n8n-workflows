import json
import re
import urllib.request

BASE = "http://43.201.227.194:5678"
API = re.search(r'API = "([^"]+)"', open("add_reel_pipeline_minimal.py", encoding="utf-8").read()).group(1)

IDS = {
    "clean_01_generator": "KPa5tncCc87z2ZsE",
    "clean_02_approval": "i6T6ke3ltKNQzaCl",
    "clean_04_carousel_publisher": "w9e3wiyca6qZUS4r",
}


def req(path, method="GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


def get_workflow(wid):
    return req(f"/api/v1/workflows/{wid}")


def put_workflow(wf):
    body = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData", {}),
        "pinData": wf.get("pinData", {}),
    }
    return req(f"/api/v1/workflows/{wf['id']}", "PUT", body)


def node(wf, name):
    for n in wf["nodes"]:
        if n.get("name") == name:
            return n
    raise KeyError(name)


wf1 = get_workflow(IDS["clean_01_generator"])
wf2 = get_workflow(IDS["clean_02_approval"])
wf4 = get_workflow(IDS["clean_04_carousel_publisher"])

# 1) clean_01: after reel URL is created, mirror it to clean_02 approval staticData via existing webhook.
cache_reel = node(wf1, "Cache Reel Video URL")
cache_reel["parameters"]["jsCode"] = """const j = $json || {};
const testId = String(j.test_id || '');
const videoUrl = String(j.video_url || '');
const videoBase64 = String(j.video_base64 || '');
if (!testId || !videoUrl) throw new Error('Missing test_id/video_url for reel cache');
if (!videoBase64) throw new Error('Missing video_base64 for Telegram binary upload');

const store = $getWorkflowStaticData('global');
if (!store.reel_video_urls || typeof store.reel_video_urls !== 'object') store.reel_video_urls = {};
store.reel_video_urls[testId] = videoUrl;
store.reel_video_cached_at = new Date().toISOString();

try {
  await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://n8n.mykindredai.com/webhook/clean_02_approval',
    body: {
      action: 'cache_reel',
      test_id: testId,
      video_url: videoUrl,
    },
    json: true,
    timeout: 15000,
  });
} catch (e) {
  // Preview delivery must not be blocked by cache mirroring.
}

const cleanJson = { ...j, reel_video_cached: true };
delete cleanJson.video_base64;

return {
  json: cleanJson,
  binary: {
    video: {
      data: videoBase64,
      mimeType: 'video/mp4',
      fileName: `${testId}.mp4`
    }
  }
};"""

# 2) clean_02: accept the cache_reel action and store the URL in approval workflow staticData.
norm = node(wf2, "Normalize Callback")
js = norm["parameters"]["jsCode"]
insert = """if (directAction === 'cache_reel') {
  const testId = String(body.test_id || '').trim();
  const videoUrl = String(body.video_url || body.reel_video_url || body.media_url || body.reel_url || '').trim();
  if (!testId || !/^https?:\\/\\//i.test(videoUrl)) {
    return [];
  }
  const store = $getWorkflowStaticData('global');
  store.reel_video_urls = (store.reel_video_urls && typeof store.reel_video_urls === 'object') ? store.reel_video_urls : {};
  store.reel_video_urls[testId] = videoUrl;
  store.reel_video_cached_at = new Date().toISOString();
  return [];
}

"""
needle = "if (directAction === 'cache_carousel') {"
if "directAction === 'cache_reel'" not in js:
    js = js.replace(needle, insert + needle)
norm["parameters"]["jsCode"] = js

# 3) clean_04: fix malformed jsonBody expression only.
pub = node(wf4, "IG Publish Carousel")
current = pub["parameters"].get("jsonBody", "")
token_match = re.search(r'"access_token"\s*:\s*"([^"]+)"', current)
if not token_match:
    token_match = re.search(r"'access_token'\s*:\s*'([^']+)'", current)
token = token_match.group(1) if token_match else ""
if not token:
    raise RuntimeError("Could not preserve access token expression/value from IG Publish Carousel")
pub["parameters"]["jsonBody"] = '={{ { "creation_id": $json.id, "access_token": "' + token + '" } }}'

put_workflow(wf1)
put_workflow(wf2)
put_workflow(wf4)

print(json.dumps({
    "updated": [
        {"workflow": "clean_01_generator", "node": "Cache Reel Video URL"},
        {"workflow": "clean_02_approval", "node": "Normalize Callback"},
        {"workflow": "clean_04_carousel_publisher", "node": "IG Publish Carousel"},
    ],
    "ig_publish_carousel_jsonBody": pub["parameters"]["jsonBody"].replace(token, "REDACTED"),
}, ensure_ascii=False, indent=2))
