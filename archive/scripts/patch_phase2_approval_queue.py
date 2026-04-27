import json
import re
import urllib.request

BASE = "http://43.201.227.194:5678"
API = re.search(r'API = "([^"]+)"', open("add_reel_pipeline_minimal.py", encoding="utf-8").read()).group(1)
WID = "i6T6ke3ltKNQzaCl"

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
n = next(x for x in wf["nodes"] if x["name"] == "Normalize Callback")
js = n["parameters"]["jsCode"]

insert_after = """const [actionRaw, testIdRaw] = callbackData.split('|');
const action = String(actionRaw || '').trim();
const testId = String(testIdRaw || '').trim();
"""

queue_block = r'''
const isQueueAction = action === 'queue_feed' || action === 'queue_reel' || action === 'queue_carousel';
const isDeleteAction = action === 'delete_test' || action === 'delete';

if (isQueueAction || isDeleteAction) {
  if (!testId) {
    throw new Error('Missing test_id in queue/delete callback');
  }

  const store = $getWorkflowStaticData('global');
  store.daily_publish_queue = (store.daily_publish_queue && typeof store.daily_publish_queue === 'object') ? store.daily_publish_queue : {};
  store.daily_deleted_items = (store.daily_deleted_items && typeof store.daily_deleted_items === 'object') ? store.daily_deleted_items : {};
  store.clean_publish_guard = (store.clean_publish_guard && typeof store.clean_publish_guard === 'object') ? store.clean_publish_guard : {};

  const nowSeoul = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Seoul' }));
  const todayKey = `${nowSeoul.getFullYear()}-${String(nowSeoul.getMonth() + 1).padStart(2, '0')}-${String(nowSeoul.getDate()).padStart(2, '0')}`;
  const dedupeKey = `${action}|${testId}`;
  if (store.clean_publish_guard[dedupeKey]) {
    return [];
  }
  store.clean_publish_guard[dedupeKey] = new Date().toISOString();

  const message = (callback.message && typeof callback.message === 'object') ? callback.message : ((body.message && typeof body.message === 'object') ? body.message : {});
  const callbackCaption = String(message.caption || message.text || '');
  const reelMap = (store.reel_video_urls && typeof store.reel_video_urls === 'object') ? store.reel_video_urls : {};
  const carouselMap = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};
  const carouselPayload = (carouselMap[testId] && typeof carouselMap[testId] === 'object') ? carouselMap[testId] : null;
  const videoUrl = String(reelMap[testId] || '').trim();

  const slotMatch = callbackCaption.match(/\[(FEED|CAROUSEL)\s*\|\s*([0-9:]+)\]/i);
  const plannedTimeFromMessage = slotMatch ? String(slotMatch[2] || '').trim() : '';
  const typeFromAction = action.replace(/^queue_/, '');
  const plannedTime = plannedTimeFromMessage || (
    typeFromAction === 'feed' ? '21:00' :
    typeFromAction === 'carousel' ? '' :
    ''
  );

  if (isDeleteAction) {
    store.daily_deleted_items[testId] = {
      test_id: testId,
      dateKey: todayKey,
      deleted_at: new Date().toISOString(),
      callback_data: callbackData,
      status: 'deleted',
    };
    if (store.daily_publish_queue[testId]) {
      store.daily_publish_queue[testId].status = 'deleted';
      store.daily_publish_queue[testId].deleted_at = new Date().toISOString();
    }
    return [];
  }

  if (store.daily_deleted_items[testId]) {
    return [];
  }

  if (typeFromAction === 'reel' && !/^https?:\/\//i.test(videoUrl)) {
    throw new Error(`Queue reel blocked: missing cached reel video for ${testId}`);
  }

  if (typeFromAction === 'carousel') {
    const media = Array.isArray(carouselPayload?.media) ? carouselPayload.media : [];
    if (media.length < 2) {
      throw new Error(`Queue carousel blocked: missing carousel media for ${testId}`);
    }
  }

  store.daily_publish_queue[testId] = {
    test_id: testId,
    dateKey: todayKey,
    post_type: typeFromAction,
    route_action: action,
    status: 'queued',
    queued_at: new Date().toISOString(),
    planned_publish_time: plannedTime,
    caption: typeFromAction === 'carousel'
      ? String(carouselPayload?.caption || callbackCaption || '').trim()
      : callbackCaption,
    video_url: typeFromAction === 'reel' ? videoUrl : '',
    carousel: typeFromAction === 'carousel' ? {
      caption: String(carouselPayload?.caption || callbackCaption || '').trim(),
      media: Array.isArray(carouselPayload?.media) ? carouselPayload.media : [],
    } : null,
    source: 'telegram_queue_button',
  };

  return [];
}

'''

if "daily_publish_queue" not in js:
    js = js.replace(insert_after, insert_after + queue_block)
n["parameters"]["jsCode"] = js

body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf.get("connections", {}), "settings": wf.get("settings", {}), "staticData": wf.get("staticData", {}), "pinData": wf.get("pinData", {})}
req(f"/api/v1/workflows/{WID}", "PUT", body)
print(json.dumps({"updated": "clean_02_approval / Normalize Callback", "added": ["daily_publish_queue", "daily_deleted_items", "queue_* handlers"]}, ensure_ascii=False))
