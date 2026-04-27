import json
import re
import urllib.request

BASE = "http://43.201.227.194:5678"
API = re.search(r'API = "([^"]+)"', open("add_reel_pipeline_minimal.py", encoding="utf-8").read()).group(1)
GEN = "KPa5tncCc87z2ZsE"
APP = "i6T6ke3ltKNQzaCl"

def req(path, method="GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))

# clean_01: feed preview payload mirrors feed text into clean_02 before Telegram.
wf1 = req(f"/api/v1/workflows/{GEN}")
n = next(x for x in wf1["nodes"] if x["name"] == "Prepare Telegram Image Payload")
js = n["parameters"]["jsCode"]
if "cache_feed" not in js:
    js = js.replace(
        "if (!b64) throw new Error(\"Generate Vape Image did not return b64_json\");",
        """if (!b64) throw new Error(\"Generate Vape Image did not return b64_json\");
try {
  await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://n8n.mykindredai.com/webhook/clean_02_approval',
    body: {
      action: 'cache_feed',
      test_id: String(base.test_id || ''),
      caption: String(base.caption || ''),
      planned_publish_time: String(base.planned_publish_time || '21:00'),
      content_slot: String(base.content_slot || 'feed_2100'),
      source_url: String(base.source_url || ''),
      hook: String(base.hook || ''),
    },
    json: true,
    timeout: 15000,
  });
} catch (e) {
  // Feed cache failure must not block Telegram preview.
}"""
    )
    n["parameters"]["jsCode"] = js
    body = {"name": wf1["name"], "nodes": wf1["nodes"], "connections": wf1.get("connections", {}), "settings": wf1.get("settings", {}), "staticData": wf1.get("staticData", {}), "pinData": wf1.get("pinData", {})}
    req(f"/api/v1/workflows/{GEN}", "PUT", body)

# clean_02: accept cache_feed and queue feed from feed_payloads.
wf2 = req(f"/api/v1/workflows/{APP}")
n = next(x for x in wf2["nodes"] if x["name"] == "Normalize Callback")
js = n["parameters"]["jsCode"]
if "directAction === 'cache_feed'" not in js:
    insert = r'''if (directAction === 'cache_feed') {
  const testId = String(body.test_id || '').trim();
  const caption = String(body.caption || '').trim();
  if (!testId || !caption) {
    return [];
  }
  const store = $getWorkflowStaticData('global');
  store.feed_payloads = (store.feed_payloads && typeof store.feed_payloads === 'object') ? store.feed_payloads : {};
  store.feed_payloads[testId] = {
    test_id: testId,
    caption,
    planned_publish_time: String(body.planned_publish_time || '21:00').trim(),
    content_slot: String(body.content_slot || 'feed_2100').trim(),
    source_url: String(body.source_url || '').trim(),
    hook: String(body.hook || '').trim(),
    updated_at: new Date().toISOString(),
  };
  return [];
}

'''
    js = js.replace("if (directAction === 'cache_reel') {", insert + "if (directAction === 'cache_reel') {")

if "const feedPayloads =" not in js:
    js = js.replace(
        "const reelMap = (store.reel_video_urls && typeof store.reel_video_urls === 'object') ? store.reel_video_urls : {};",
        "const reelMap = (store.reel_video_urls && typeof store.reel_video_urls === 'object') ? store.reel_video_urls : {};\n  const feedPayloads = (store.feed_payloads && typeof store.feed_payloads === 'object') ? store.feed_payloads : {};\n  const feedPayload = (feedPayloads[testId] && typeof feedPayloads[testId] === 'object') ? feedPayloads[testId] : null;"
    )
js = js.replace(
    "const plannedTime = plannedTimeFromMessage || String(reelPayload?.planned_publish_time || '').trim() || (",
    "const plannedTime = plannedTimeFromMessage || String(feedPayload?.planned_publish_time || '').trim() || String(reelPayload?.planned_publish_time || '').trim() || ("
)
js = js.replace(
    "caption: typeFromAction === 'carousel'\n      ? String(carouselPayload?.caption || callbackCaption || '').trim()\n      : (typeFromAction === 'reel' ? String(reelPayload?.caption || callbackCaption || '').trim() : callbackCaption),",
    "caption: typeFromAction === 'carousel'\n      ? String(carouselPayload?.caption || callbackCaption || '').trim()\n      : (typeFromAction === 'reel' ? String(reelPayload?.caption || callbackCaption || '').trim() : String(feedPayload?.caption || callbackCaption || '').trim()),"
)
n["parameters"]["jsCode"] = js
body = {"name": wf2["name"], "nodes": wf2["nodes"], "connections": wf2.get("connections", {}), "settings": wf2.get("settings", {}), "staticData": wf2.get("staticData", {}), "pinData": wf2.get("pinData", {})}
req(f"/api/v1/workflows/{APP}", "PUT", body)

print(json.dumps({"updated": ["clean_01 Prepare Telegram Image Payload cache_feed", "clean_02 Normalize Callback cache_feed/feed_payloads"]}, ensure_ascii=False))
