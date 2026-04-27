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
backup_name = f"clean_01_generator_backup_variation_engine_{ts}.json"
with open(backup_name, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

build = next(n for n in wf["nodes"] if n.get("name") == "Build Simulation Content")
code = build["parameters"]["jsCode"]

code = code.replace(
    'if (typeof store.dailyPreviewBatchIndex !== "number") store.dailyPreviewBatchIndex = 0;\n',
    'if (typeof store.dailyPreviewBatchIndex !== "number") store.dailyPreviewBatchIndex = 0;\n'
    'store.dailyPreviewBatchIndex += 1;\n'
)

code = code.replace(
    'const batchId = `${dateKey}-${Date.now().toString(36)}`;\n',
    'const executionSeed = `${Date.now().toString(36)}-${store.dailyPreviewBatchIndex}`;\n'
    'const batchId = `${dateKey}-${executionSeed}`;\n'
    'const recentIndex = Array.isArray(store.generated_content_index) ? store.generated_content_index : [];\n'
    'const recentCutoff = Date.now() - 7 * 24 * 60 * 60 * 1000;\n'
    'const recentMemory = recentIndex\n'
    '  .filter(r => new Date(r.created_at || 0).getTime() >= recentCutoff)\n'
    '  .slice(-20)\n'
    '  .map(r => ({ hook: String(r.hook_first_line || "").trim(), post_type: String(r.post_type || ""), angle: String(r.angle || ""), cta_style: String(r.cta_style || "") }));\n'
    'const recent_hooks = recentMemory.map(r => r.hook).filter(Boolean);\n'
    'const recent_angles = recentMemory.map(r => r.angle).filter(Boolean);\n'
    'const recent_cta_styles = recentMemory.map(r => r.cta_style).filter(Boolean);\n'
)

code = code.replace(
    'const slots = [\n'
    '  { post_type: "feed", label: "FEED", slot: "feed_2100", publish_time: "21:00", factIndex: 0 },\n'
    '  { post_type: "reel", label: "REEL 1", slot: "reel_1200", publish_time: "12:00", factIndex: 1 },\n'
    '  { post_type: "carousel", label: "CAROUSEL 1", slot: "carousel_1205", publish_time: "12:05", linked_reel_slot: "reel_1200", factIndex: 1 },\n'
    '  { post_type: "reel", label: "REEL 2", slot: "reel_1800", publish_time: "18:00", factIndex: 2 },\n'
    '  { post_type: "carousel", label: "CAROUSEL 2", slot: "carousel_1805", publish_time: "18:05", linked_reel_slot: "reel_1800", factIndex: 2 },\n'
    '  { post_type: "reel", label: "REEL 3", slot: "reel_2200", publish_time: "22:00", factIndex: 3 },\n'
    '  { post_type: "carousel", label: "CAROUSEL 3", slot: "carousel_2205", publish_time: "22:05", linked_reel_slot: "reel_2200", factIndex: 3 }\n'
    '];\n',
    'const slots = [\n'
    '  { post_type: "feed", label: "FEED", slot: "feed_2100", publish_time: "21:00", factIndex: 0, angle: "deep_analysis", hook_style: "hidden_cost", cta_style: "forced_choice" },\n'
    '  { post_type: "reel", label: "REEL 1", slot: "reel_1200", publish_time: "12:00", factIndex: 1, angle: "loss_emotion", hook_style: "you_are_losing", cta_style: "save_or_get_burned" },\n'
    '  { post_type: "carousel", label: "CAROUSEL 1", slot: "carousel_1205", publish_time: "12:05", linked_reel_slot: "reel_1200", factIndex: 1, angle: "comparison", hook_style: "surface_vs_reality", cta_style: "which_side" },\n'
    '  { post_type: "reel", label: "REEL 2", slot: "reel_1800", publish_time: "18:00", factIndex: 2, angle: "absurd_comedy", hook_style: "this_is_ridiculous", cta_style: "tag_someone" },\n'
    '  { post_type: "carousel", label: "CAROUSEL 2", slot: "carousel_1805", publish_time: "18:05", linked_reel_slot: "reel_1800", factIndex: 2, angle: "checklist", hook_style: "check_before_buying", cta_style: "save_checklist" },\n'
    '  { post_type: "reel", label: "REEL 3", slot: "reel_2200", publish_time: "22:00", factIndex: 3, angle: "debate_trigger", hook_style: "agree_or_disagree", cta_style: "comment_side" },\n'
    '  { post_type: "carousel", label: "CAROUSEL 3", slot: "carousel_2205", publish_time: "22:05", linked_reel_slot: "reel_2200", factIndex: 3, angle: "hidden_structure", hook_style: "who_benefits", cta_style: "dm_if_you_see_it" }\n'
    '];\n'
)

marker = 'const reelCaption = (f) => [\n'
helpers = r'''
const angleOpeners = {
  loss_emotion: (f) => `${f.fact} 이거 모르면 돈보다 먼저 판단력이 털린다.`,
  absurd_comedy: (f) => `${f.fact} 근데 현장은 거의 코미디처럼 굴러간다.`,
  debate_trigger: (f) => `${f.fact} 이건 보호냐, 뒷북 단속이냐부터 갈린다.`,
  comparison: (f) => `${f.fact} 겉보기엔 정리, 실제론 선택지 축소다.`,
  checklist: (f) => `${f.fact} 매장 가기 전에 이것부터 확인해라.`,
  hidden_structure: (f) => `${f.fact} 누가 먼저 알고 움직였는지 봐야 한다.`,
  deep_analysis: (f) => `${f.fact} 이 뉴스는 그냥 넘기면 손해다.`
};
const angleClosers = {
  loss_emotion: "너 이거 그냥 넘길 거야, 아니면 다음 계산대 앞에서 덜 당할 거야?",
  absurd_comedy: "이게 진짜 소비자 보호로 보여, 아니면 규제 코미디로 보여?",
  debate_trigger: "너는 이거 찬성이야, 아니면 말만 보호인 뒷북이라고 봐?",
  comparison: "겉말과 실제 현장 중에 너는 어느 쪽을 믿을 거야?",
  checklist: "이 체크리스트 저장할래, 아니면 또 매장 앞에서 물어볼래?",
  hidden_structure: "이 구조 보이면 댓글 달고, 안 보이면 그냥 지나가도 된다.",
  deep_analysis: "너라면 이걸 소비자 보호라고 보냐, 아니면 늦게 온 단속 장치라고 보냐?"
};
function applyAngleCaption(baseCaption, f, angle) {
  const lines = String(baseCaption || '').split('\n').filter(Boolean);
  const opener = (angleOpeners[angle] || angleOpeners.loss_emotion)(f);
  const closer = angleClosers[angle] || f.question;
  if (lines.length) lines[0] = opener;
  if (lines.length > 1) lines[lines.length - 1] = closer;
  return lines.join('\n');
}
'''
if helpers not in code:
    code = code.replace(marker, helpers + "\n" + marker)

code = code.replace(
    '  const caption = slot.post_type === "feed" ? feedCaption(f) : (slot.post_type === "carousel" ? carouselCaption(f) : reelCaption(f));\n',
    '  const baseCaption = slot.post_type === "feed" ? feedCaption(f) : (slot.post_type === "carousel" ? carouselCaption(f) : reelCaption(f));\n'
    '  const caption = applyAngleCaption(baseCaption, f, slot.angle);\n'
    '  const variation_seed = `${dateKey}_${executionSeed}_${idx + 1}`;\n'
)

code = code.replace(
    '      source_mode: f.source_mode || "latest_rss",\n',
    '      source_mode: f.source_mode || "latest_rss",\n'
    '      variation_seed,\n'
    '      angle: slot.angle,\n'
    '      hook_style: slot.hook_style,\n'
    '      cta_style: slot.cta_style,\n'
    '      recent_hooks,\n'
    '      recent_angles,\n'
    '      recent_cta_styles,\n'
    '      recent_memory_count: recentMemory.length,\n'
    '      avoid_memory_used: true,\n'
)

build["parameters"]["jsCode"] = code

detect = next(n for n in wf["nodes"] if n.get("name") == "Detect Duplicate Content")
detect["parameters"]["jsCode"] = r"""
const store = $getWorkflowStaticData('global');
store.generated_content_index = Array.isArray(store.generated_content_index) ? store.generated_content_index : [];

const now = new Date();
const cutoff = now.getTime() - 14 * 24 * 60 * 60 * 1000;
const previousLive = store.generated_content_index
  .filter(r => new Date(r.created_at || 0).getTime() >= cutoff)
  .filter(r => String(r.mode || 'live') === 'live')
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
  const s = String(value || '');
  let h1 = 0x811c9dc5;
  let h2 = 0x01000193;
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    h1 ^= c;
    h1 = Math.imul(h1, 0x01000193);
    h2 ^= c + i;
    h2 = Math.imul(h2, 0x811c9dc5);
  }
  return `${(h1 >>> 0).toString(16).padStart(8, '0')}${(h2 >>> 0).toString(16).padStart(8, '0')}`;
}

function wordOverlap(a, b) {
  const aw = new Set(normalize(a).split(' ').filter(Boolean));
  const bw = new Set(normalize(b).split(' ').filter(Boolean));
  if (!aw.size || !bw.size) return 0;
  let inter = 0;
  for (const w of aw) if (bw.has(w)) inter++;
  return inter / Math.min(aw.size, bw.size);
}

function compute(j) {
  const postType = String(j.post_type || '');
  const hook = String(j.hook || '').split(/[.!?。\\n]/)[0] || String(j.hook || '');
  const caption = String(j.caption || '');
  const imagePrompt = String(j.media_prompt || j.carousel_prompt || '');
  const normalized_caption = normalize(caption);
  return {
    normalized_caption,
    content_hash: hash(normalized_caption),
    hook_hash: hash(normalize(hook)),
    caption_hash: hash(normalized_caption),
    image_prompt_hash: hash(normalize(imagePrompt)),
    postType,
  };
}

function regenerateOnce(j, reason) {
  const lines = String(j.caption || '').split('\n').filter(Boolean);
  const angle = String(j.angle || '');
  const ctaByAngle = {
    loss_emotion: '이거 저장 안 하면 다음에 똑같이 당할 가능성, 솔직히 없다고 봐?',
    absurd_comedy: '이 상황 웃기다고 넘길래, 아니면 댓글로 한 번 따져볼래?',
    debate_trigger: '너는 이거 질서라고 봐, 아니면 소비자한테 떠넘긴 숙제라고 봐?',
    comparison: '겉으로 보이는 말이 맞아, 아니면 뒤에서 바뀐 기준이 더 진짜야?',
    checklist: '이거 체크하고 갈래, 아니면 또 매장 앞에서 당황할래?',
    hidden_structure: '누가 이 구조에서 먼저 움직였는지 이제 보이지 않아?',
    deep_analysis: '이걸 알고도 그냥 규제 뉴스 하나로 넘길 수 있어?'
  };
  if (lines.length) lines[0] = `${lines[0]} 지금 문제는 여기서 끝이 아니라는 거다.`;
  if (lines.length > 1) lines[lines.length - 1] = ctaByAngle[angle] || ctaByAngle.debate_trigger;
  return {
    ...j,
    caption: lines.join('\n'),
    regenerate_attempted: true,
    regenerate_reason: reason,
  };
}

const out = [];
const newRecords = [];

for (const item of $input.all()) {
  let j = item.json || {};
  const mode = String(j.mode || 'live');
  const postType = String(j.post_type || '');
  const angle = String(j.angle || '');
  let h = compute(j);

  let previousSameTypeDuplicate = previousLive.some(r => r.post_type === postType && r.content_hash === h.content_hash);
  let sameTypeAngleHookDuplicate = previousLive.some(r => r.post_type === postType && r.angle === angle && r.hook_hash === h.hook_hash);
  let hookDuplicate = previousLive.some(r => r.hook_hash === h.hook_hash);
  let imagePromptDuplicate = Boolean(h.image_prompt_hash) && previousLive.some(r => r.image_prompt_hash === h.image_prompt_hash);
  let maxOverlap = previousLive
    .filter(r => r.post_type === postType)
    .reduce((max, r) => Math.max(max, wordOverlap(h.normalized_caption, r.normalized_caption || '')), 0);
  let similarityWarning = maxOverlap >= 0.7;

  if ((similarityWarning || hookDuplicate) && !j.regenerate_attempted) {
    j = regenerateOnce(j, similarityWarning ? 'similarity_warning' : 'hook_duplicate_warning');
    h = compute(j);
    previousSameTypeDuplicate = previousLive.some(r => r.post_type === postType && r.content_hash === h.content_hash);
    sameTypeAngleHookDuplicate = previousLive.some(r => r.post_type === postType && r.angle === angle && r.hook_hash === h.hook_hash);
    hookDuplicate = previousLive.some(r => r.hook_hash === h.hook_hash);
    imagePromptDuplicate = Boolean(h.image_prompt_hash) && previousLive.some(r => r.image_prompt_hash === h.image_prompt_hash);
    maxOverlap = previousLive
      .filter(r => r.post_type === postType)
      .reduce((max, r) => Math.max(max, wordOverlap(h.normalized_caption, r.normalized_caption || '')), 0);
    similarityWarning = maxOverlap >= 0.7;
  }

  const duplicate_blocked = Boolean(previousSameTypeDuplicate || sameTypeAngleHookDuplicate || (j.regenerate_attempted && similarityWarning));
  const blocked_reason = previousSameTypeDuplicate
    ? 'previous_live_duplicate'
    : sameTypeAngleHookDuplicate
      ? 'same_post_type_angle_hook_duplicate'
      : (j.regenerate_attempted && similarityWarning ? 'regenerate_failed_similarity' : '');

  const warningReasons = [];
  if (hookDuplicate && !duplicate_blocked) warningReasons.push('hook_duplicate');
  if (similarityWarning && !duplicate_blocked) warningReasons.push('similarity_warning');
  if (imagePromptDuplicate) warningReasons.push('image_prompt_duplicate');
  if (j.feed_fallback_used || j.reel_fallback_count > 0 || j.carousel_fallback_count > 0) warningReasons.push('fallback_used');

  const record = {
    content_hash: h.content_hash,
    hook_hash: h.hook_hash,
    caption_hash: h.caption_hash,
    normalized_caption: h.normalized_caption,
    image_prompt_hash: h.image_prompt_hash,
    image_url: String(j.image_url || ''),
    image_source: String(j.image_source || j.feed_image_source || ''),
    post_type: postType,
    angle,
    cta_style: String(j.cta_style || ''),
    hook_first_line: String(j.hook || '').split(/[.!?。\\n]/)[0],
    test_id: String(j.test_id || ''),
    mode,
    created_at: now.toISOString(),
  };

  if (!duplicate_blocked && mode === 'live') {
    newRecords.push(record);
  }

  out.push({
    json: {
      ...j,
      mode,
      content_hash: h.content_hash,
      hook_hash: h.hook_hash,
      caption_hash: h.caption_hash,
      normalized_caption: h.normalized_caption,
      image_prompt_hash: h.image_prompt_hash,
      duplicate_blocked,
      blocked_reason,
      hook_duplicate_warning: hookDuplicate && !duplicate_blocked,
      similarity_warning: similarityWarning && !duplicate_blocked,
      similarity_score: Number(maxOverlap.toFixed(3)),
      image_duplicate_warning: Boolean(imagePromptDuplicate),
      warning_reason: warningReasons.join(','),
      needs_manual_review: Boolean(j.needs_manual_review || warningReasons.length),
      queue_disabled_reason: mode === 'test' ? 'test_mode' : String(j.queue_disabled_reason || ''),
    }
  });
}

store.generated_content_index = previousLive.concat(newRecords).slice(-500);
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
print(json.dumps({"backup": backup_name, "workflow": "clean_01_generator", "modified": ["Build Simulation Content", "Detect Duplicate Content"]}, ensure_ascii=False, indent=2))
