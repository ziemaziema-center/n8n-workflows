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
backup_name = f"clean_01_generator_backup_feed_fallback_duplicate_{ts}.json"
with open(backup_name, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

nodes = [n for n in wf["nodes"] if n.get("name") not in {"Detect Duplicate Content", "Filter Duplicate Blocked Items"}]
connections = wf.get("connections", {})
connections.pop("Detect Duplicate Content", None)
connections.pop("Filter Duplicate Blocked Items", None)

gen_feed = next(n for n in nodes if n.get("name") == "Generate Vape Image")
gen_feed["continueOnFail"] = True
gen_feed.setdefault("parameters", {}).setdefault("options", {})
gen_feed["parameters"]["options"]["continueOnFail"] = True

prep_feed = next(n for n in nodes if n.get("name") == "Prepare Telegram Image Payload")
prep_feed["parameters"]["jsCode"] = r"""
const FALLBACK_URL = 'https://n8n.mykindredai.com/images/fallback.png';
const sourceItems = $items('Filter Feed Preview Items') || [];
const base = (sourceItems[$itemIndex] && sourceItems[$itemIndex].json) ? sourceItems[$itemIndex].json : {};
const j = $json || {};
const b64 = String(j?.data?.[0]?.b64_json || '').trim();
const hasError = Boolean(j.error || j.code || String(j.status || '').toLowerCase() === 'error');
const useFallback = hasError || !b64;

let binaryPhoto;
let imageUrl = '';
if (useFallback) {
  imageUrl = FALLBACK_URL;
} else {
  binaryPhoto = {
    data: b64,
    mimeType: 'image/png',
    fileName: `feed_${base.test_id || Date.now()}.png`
  };
  imageUrl = String(j?.data?.[0]?.url || '').trim();
}

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
      image_url: imageUrl,
      media_url: imageUrl,
    },
    json: true,
    timeout: 15000,
  });
} catch (e) {
  // Feed cache failure must not block Telegram preview.
}

const json = {
  ...base,
  generated_image_model: 'gpt-image-1-mini',
  media_generation_status: useFallback ? 'fallback_due_to_generation_error' : 'ok',
  feed_image_source: useFallback ? 'fallback' : 'generated',
  feed_fallback_used: useFallback,
  feed_image_collection_status: useFallback ? 'fallback_filled' : 'success',
  image_url: imageUrl,
  media_url: imageUrl,
  needs_manual_review: Boolean(base.needs_manual_review || useFallback),
};

if (useFallback) {
  return { json };
}

return {
  json,
  binary: { photo: binaryPhoto }
};
""".strip()

detect_code = r"""
const crypto = require('crypto');
const store = $getWorkflowStaticData('global');
store.generated_content_index = Array.isArray(store.generated_content_index) ? store.generated_content_index : [];

const now = new Date();
const cutoff = now.getTime() - 14 * 24 * 60 * 60 * 1000;
store.generated_content_index = store.generated_content_index
  .filter(r => new Date(r.created_at || 0).getTime() >= cutoff)
  .slice(-500);

function normalize(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[\r\n]+/g, ' ')
    .replace(/[^\u3131-\u318E\uAC00-\uD7A3a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function hash(value) {
  return crypto.createHash('sha256').update(String(value || '')).digest('hex').slice(0, 16);
}

function wordOverlap(a, b) {
  const aw = new Set(normalize(a).split(' ').filter(Boolean));
  const bw = new Set(normalize(b).split(' ').filter(Boolean));
  if (!aw.size || !bw.size) return 0;
  let inter = 0;
  for (const w of aw) if (bw.has(w)) inter++;
  return inter / Math.min(aw.size, bw.size);
}

const existing = store.generated_content_index;
const batchHashes = new Set();
const out = [];

for (const item of $input.all()) {
  const j = item.json || {};
  const mode = String(j.mode || 'live');
  const postType = String(j.post_type || '');
  const hook = String(j.hook || '');
  const caption = String(j.caption || '');
  const imagePrompt = String(j.media_prompt || j.carousel_prompt || '');
  const normalized_caption = normalize(caption);
  const content_hash = hash(`${postType}|${normalize(hook)}|${normalized_caption}`);
  const hook_hash = hash(normalize(hook));
  const caption_hash = hash(normalized_caption);
  const image_prompt_hash = hash(normalize(imagePrompt));

  const exactDuplicate = existing.some(r => r.content_hash === content_hash) || batchHashes.has(content_hash);
  const hookDuplicate = existing.some(r => r.hook_hash === hook_hash);
  const imagePromptDuplicate = imagePrompt && existing.some(r => r.image_prompt_hash === image_prompt_hash);
  const maxOverlap = existing.reduce((max, r) => Math.max(max, wordOverlap(normalized_caption, r.normalized_caption || '')), 0);
  const similarityWarning = maxOverlap >= 0.7;

  batchHashes.add(content_hash);

  const record = {
    content_hash,
    hook_hash,
    caption_hash,
    normalized_caption,
    image_prompt_hash,
    image_url: String(j.image_url || ''),
    image_source: String(j.image_source || ''),
    post_type: postType,
    test_id: String(j.test_id || ''),
    mode,
    created_at: now.toISOString(),
  };

  if (!exactDuplicate && mode === 'live') {
    existing.push(record);
  }

  out.push({
    json: {
      ...j,
      mode,
      content_hash,
      hook_hash,
      caption_hash,
      normalized_caption,
      image_prompt_hash,
      duplicate_blocked: exactDuplicate,
      hook_duplicate_warning: hookDuplicate,
      similarity_warning: similarityWarning,
      similarity_score: Number(maxOverlap.toFixed(3)),
      image_duplicate_warning: Boolean(imagePromptDuplicate),
      needs_manual_review: Boolean(j.needs_manual_review || hookDuplicate || similarityWarning || imagePromptDuplicate),
      queue_disabled_reason: mode === 'test' ? 'test_mode' : String(j.queue_disabled_reason || ''),
    }
  });
}

store.generated_content_index = existing.slice(-500);
return out;
""".strip()

filter_code = r"""
const items = $input.all();
const survivors = items.filter(i => i.json && i.json.duplicate_blocked !== true);
const blocked = items.filter(i => i.json && i.json.duplicate_blocked === true);

const counts = survivors.reduce((acc, i) => {
  const type = String(i.json.post_type || 'unknown');
  acc[type] = (acc[type] || 0) + 1;
  return acc;
}, {});

const store = $getWorkflowStaticData('global');
store.last_duplicate_block_summary = {
  at: new Date().toISOString(),
  blocked_count: blocked.length,
  blocked_items: blocked.map(i => ({
    test_id: String(i.json.test_id || ''),
    post_type: String(i.json.post_type || ''),
    content_hash: String(i.json.content_hash || ''),
  })),
  survivor_counts: counts,
};

return survivors;
""".strip()

detect_node = {
    "id": "detect-duplicate-content",
    "name": "Detect Duplicate Content",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [700, 300],
    "parameters": {"jsCode": detect_code},
}

filter_node = {
    "id": "filter-duplicate-blocked-items",
    "name": "Filter Duplicate Blocked Items",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [940, 300],
    "parameters": {"jsCode": filter_code},
}

nodes.extend([detect_node, filter_node])

connections["Build Simulation Content"] = {
    "main": [[{"node": "Detect Duplicate Content", "type": "main", "index": 0}]]
}
connections["Detect Duplicate Content"] = {
    "main": [[{"node": "Filter Duplicate Blocked Items", "type": "main", "index": 0}]]
}
connections["Filter Duplicate Blocked Items"] = {
    "main": [[
        {"node": "Filter Reel Preview Items", "type": "main", "index": 0},
        {"node": "Filter Carousel Preview Items", "type": "main", "index": 0},
        {"node": "Filter Feed Preview Items", "type": "main", "index": 0},
    ]]
}

body = {
    "name": wf["name"],
    "nodes": nodes,
    "connections": connections,
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", {}),
    "pinData": wf.get("pinData", {}),
}
req(f"/api/v1/workflows/{WID}", "PUT", body)
print(json.dumps({
    "backup": backup_name,
    "workflow": "clean_01_generator",
    "modified": ["Generate Vape Image", "Prepare Telegram Image Payload"],
    "added": ["Detect Duplicate Content", "Filter Duplicate Blocked Items"],
}, ensure_ascii=False, indent=2))
