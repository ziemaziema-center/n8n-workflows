import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "http://43.201.227.194:5678"
WID = "KPa5tncCc87z2ZsE"

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
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
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
    return req(f"/api/v1/workflows/{wf['id']}", "PUT", body)


def code_of(wf, name):
    node = next(n for n in wf["nodes"] if n.get("name") == name)
    params = node.setdefault("parameters", {})
    key = "jsCode" if "jsCode" in params else "code"
    return node, params, key, params.get(key, "")


wf = req(f"/api/v1/workflows/{WID}")
backup = f"clean_01_generator_backup_psych_diversity_engine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
Path(backup).write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")


# --- Build Simulation Content: hook/angle/tone/visual diversity layer ---
node, params, key, code = code_of(wf, "Build Simulation Content")
if "PSYCHOLOGICAL DIVERSITY ENGINE v3" not in code:
    insert_before = "const angleOpeners = {"
    psych_block = r'''
// PSYCHOLOGICAL DIVERSITY ENGINE v3
const psychHookTypes = [
  { key: "loss_trigger", label: "Loss Trigger", open: "이거 모르면 계속 돈 날립니다" },
  { key: "identity_threat", label: "Identity Threat", open: "이 방식 쓰는 사람들, 거의 다 잘못 알고 있습니다" },
  { key: "pattern_break", label: "Pattern Break", open: "다들 가격 보는데, 이게 먼저입니다" },
  { key: "regret_projection", label: "Regret Projection", open: "이거 안 보면 다음 달에 후회합니다" },
  { key: "hidden_knowledge", label: "Hidden Knowledge", open: "이건 업자들은 알고 소비자는 모릅니다" },
  { key: "contrarian_truth", label: "Contrarian Truth", open: "싸다고 좋은 게 아니라, 이게 문제입니다" },
  { key: "question_trap", label: "Question Trap", open: "왜 같은 걸 사도 돈이 더 나갈까요?" },
  { key: "time_pressure", label: "Time Pressure", open: "지금 바뀌는 구조, 늦으면 바로 손해입니다" }
];
const psychAngles = ["비용 착각", "선택 순서 오류", "규제 충격", "소비자 심리 착각", "매장 vs 소비자 정보 차이", "타이밍 실패", "반복 구매 패턴"];
const psychToneMix = ["cold_authority", "cold_authority", "cold_authority", "cold_authority", "warning", "warning", "warning", "subtle_accusation", "subtle_accusation", "curiosity"];
const visualScenes = ["매장", "집", "거리", "계산대", "손 클로즈업"];
const visualEmotions = ["당황", "짜증", "혼란", "의심", "후회"];
const visualRenderStyles = ["현실 사진", "과장된 상징", "만화 스타일", "광고 패러디 느낌"];
const visualObjects = ["제품", "가격표", "영수증", "손", "비교 장면"];

function pickRotated(list, idx, salt, previous) {
  let offset = Math.abs(String(salt || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0));
  let picked = list[(idx + offset) % list.length];
  if (previous && (picked.key || picked) === previous) picked = list[(idx + offset + 1) % list.length];
  return picked;
}

function visualCombo(idx, seed) {
  const salt = Math.abs(String(seed || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0));
  return {
    scene: visualScenes[(idx + salt) % visualScenes.length],
    emotion: visualEmotions[(idx * 2 + salt) % visualEmotions.length],
    render_style: visualRenderStyles[(idx * 3 + salt) % visualRenderStyles.length],
    object: visualObjects[(idx * 4 + salt) % visualObjects.length]
  };
}

function compactFact(f) {
  return String(f.fact || '').replace(/\s+/g, ' ').trim();
}

function buildPsychPost(f, slot, idx, seed) {
  const hookType = pickRotated(psychHookTypes, idx, seed, store.last_psych_hook_type || "");
  const dominantAngle = pickRotated(psychAngles, idx, `${seed}_${slot.post_type}`, "");
  const tone = pickRotated(psychToneMix, idx, `${seed}_${dominantAngle}`, "");
  const visual = visualCombo(idx, `${seed}_${dominantAngle}_${hookType.key}`);
  const factLine = compactFact(f);
  const jab = String(f.jab || '').replace(/\s+/g, ' ').trim();
  const question = String(f.question || '').replace(/\s+/g, ' ').trim();
  const opener = `${hookType.open}. ${factLine}`;
  const discomfort = `${dominantAngle}에서 제일 불편한 건 이겁니다. ${jab || '사람들은 제품을 고른다고 생각하지만 실제로는 정보 차이 안에서 움직입니다.'}`;
  const realization = `아... 이거네. 문제는 취향이 아니라, 누가 먼저 구조를 알고 들어가느냐입니다.`;
  const fear = `이걸 놓치면 다음 구매에서 돈, 시간, 선택권 중 하나는 조용히 새나갑니다.`;
  const pressure = question && question.endsWith('?') ? question : `저장해두고 볼래요, 아니면 또 매장 앞에서 감으로 고를래요?`;
  return {
    hookType,
    dominantAngle,
    tone,
    visual,
    hookLine: opener,
    caption: [opener, discomfort, realization, fear, pressure].join('\n'),
    mediaPrompt: `${visual.scene}, ${visual.emotion}, ${visual.render_style}, ${visual.object}, behavioral psychology tension, pattern disruption, adult consumer regret, funny but uncomfortable, scroll-stopping, no readable text, no logos, no minors, no smoking glamor, based on verified Korean news fact: ${factLine}`
  };
}

'''
    if insert_before not in code:
        raise RuntimeError("Could not find angleOpeners insertion point")
    code = code.replace(insert_before, psych_block + "\n" + insert_before, 1)

code = code.replace("return slots.map((slot, idx) => {", "const output = slots.map((slot, idx) => {", 1)
code = code.replace(
    '  const style = slot.post_type === "feed" ? "DUALITY_POSTER" : visualStyles[idx % visualStyles.length];\n  const baseCaption = slot.post_type === "feed" ? feedCaption(f) : (slot.post_type === "carousel" ? carouselCaption(f) : reelCaption(f));\n  const caption = applyAngleCaption(baseCaption, f, slot.angle);',
    '  const style = slot.post_type === "feed" ? "DUALITY_POSTER" : visualStyles[idx % visualStyles.length];\n  const psych = buildPsychPost(f, slot, idx, executionSeed);\n  const caption = psych.caption;',
    1,
)
code = code.replace("      angle: slot.angle,", "      angle: psych.dominantAngle,\n      legacy_angle: slot.angle,\n      psych_angle: psych.dominantAngle,\n      psych_hook_type: psych.hookType.key,\n      psych_hook_label: psych.hookType.label,\n      psych_tone: psych.tone,", 1)
code = code.replace("      hook_style: slot.hook_style,", "      hook_style: psych.hookType.key,", 1)
code = code.replace('      hook: f.fact,\n      body_lines: [f.jab, f.question],\n      tension_ending: f.question,', '      hook: psych.hookLine,\n      body_lines: caption.split("\\n").slice(1, 4),\n      tension_ending: caption.split("\\n").slice(-1)[0],', 1)
code = code.replace('      media_prompt: `${mediaPrompts[style]}, based on verified Korean news fact: ${f.fact}`,', '      media_prompt: `${psych.mediaPrompt}, ${mediaPrompts[style] || ""}`,\n      visual_scene: psych.visual.scene,\n      visual_emotion: psych.visual.emotion,\n      visual_style: psych.visual.render_style,\n      visual_object: psych.visual.object,', 1)
code = code.replace('      content_rules_version: "v2_2026_04_news_daily7_phase1",', '      content_rules_version: "v3_psychological_diversity_2026_04",', 1)
if code.rstrip().endswith("});"):
    code = code.rstrip()[:-3] + "});\nstore.last_psych_hook_type = output.length ? output[output.length - 1].json.psych_hook_type : store.last_psych_hook_type;\nreturn output;\n"
params[key] = code


# --- Build Reel Scene Prompts: per-scene visual diversity ---
node, params, key, code = code_of(wf, "Build Reel Scene Prompts")
code = re.sub(
    r"  const scenes = \[[\s\S]*?\n  \];",
    r'''  const sceneBank = ['매장', '집', '거리', '계산대', '손 클로즈업'];
  const emotionBank = ['당황', '짜증', '혼란', '의심', '후회'];
  const styleBank = ['현실 사진', '과장된 상징', '만화 스타일', '광고 패러디 느낌'];
  const objectBank = ['제품', '가격표', '영수증', '손', '비교 장면'];
  const angle = String(base.psych_angle || base.angle || '').trim();
  const hookType = String(base.psych_hook_label || base.psych_hook_type || '').trim();
  const scenes = Array.from({ length: 6 }, (_, i) => {
    const scene = sceneBank[(i + Number(base.daily_preview_index || 0)) % sceneBank.length];
    const emotion = emotionBank[(i * 2 + Number(base.daily_preview_index || 0)) % emotionBank.length];
    const render = styleBank[(i * 3 + Number(base.daily_preview_index || 0)) % styleBank.length];
    const object = objectBank[(i * 4 + Number(base.daily_preview_index || 0)) % objectBank.length];
    return `scene ${i + 1}/6, ${mood}, ${scene}, ${emotion}, ${render}, ${object}, dominant psychology angle: ${angle}, hook type: ${hookType}, adult-only, pattern disruption, regret/fear trigger, each frame must look completely different from the previous frame, no readable text, no brand logos, no minors, no smoking glamor, inspired by '${i === 0 ? fact : i === 4 ? jab : question}'`;
  });''',
    code,
    count=1,
)
params[key] = code


# --- Build Carousel Prompts: visual combination engine ---
node, params, key, code = code_of(wf, "Build Carousel Prompts")
code = r'''const inputItems = $input.all();
const out = [];
const scenes = ['매장', '집', '거리', '계산대', '손 클로즈업'];
const emotions = ['당황', '짜증', '혼란', '의심', '후회'];
const renderStyles = ['현실 사진', '과장된 상징', '만화 스타일', '광고 패러디 느낌'];
const objects = ['제품', '가격표', '영수증', '손', '비교 장면'];

for (const item of inputItems) {
  const data = item.json || {};
  const carousel = data.carousel || {};
  const slides = Array.isArray(carousel.slides) ? carousel.slides : [];
  if (!slides.length) continue;
  const offset = Number(data.daily_preview_index || 0);
  const image_prompts = slides.map((slide, idx) => {
    const scene = scenes[(idx + offset) % scenes.length];
    const emotion = emotions[(idx * 2 + offset) % emotions.length];
    const render = renderStyles[(idx * 3 + offset) % renderStyles.length];
    const object = objects[(idx * 4 + offset) % objects.length];
    return `${scene}, ${emotion}, ${render}, ${object}, psychological tension, FBI behavioral pattern disruption, decision bias, fear of regret, funny but uncomfortable adult consumer moment, each slide must feel visually different, inspired by: ${String(slide || '').trim()}, dark background, cinematic lighting, high contrast, no readable text, no logos, no minors, no smoking glamor`;
  });
  const base = { ...data, carousel: { ...carousel, image_prompts } };
  image_prompts.forEach((prompt, idx) => out.push({ json: { ...base, carousel_prompt: prompt, carousel_slide_index: idx + 1 } }));
}
return out;'''
params[key] = code


# --- Feed image prompt: preserve duality but add visual diversity fields ---
node, params, key, code = code_of(wf, "Filter Feed Preview Items")
code = r'''return $input.all()
  .filter(i => String(i.json?.post_type || '') === 'feed')
  .map(i => ({
    json: {
      ...i.json,
      media_prompt: `${i.json.media_prompt || ''}, ${i.json.visual_scene || '계산대'}, ${i.json.visual_emotion || '의심'}, ${i.json.visual_style || '과장된 상징'}, ${i.json.visual_object || '영수증'}, 세상의 이중성, looks like A on the surface but reveals B underneath, split image, polished public face versus hidden cost, symbolic editorial image, no readable text, no logos`
    }
  }));'''
params[key] = code

put_workflow(wf)
print(json.dumps({"backup": backup, "workflow": wf["name"], "patched_nodes": ["Build Simulation Content", "Build Reel Scene Prompts", "Build Carousel Prompts", "Filter Feed Preview Items"]}, ensure_ascii=False, indent=2))
