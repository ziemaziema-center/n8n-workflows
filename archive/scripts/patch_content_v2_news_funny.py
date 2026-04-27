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


build_sim_js = r'''const input = ($input.first() && $input.first().json) ? $input.first().json : {};
const callbackRaw = String(input.callback_data || input.data || input.action || "");
const isRegenMedia = callbackRaw.startsWith("regen_media");

const store = $getWorkflowStaticData("global");
if (typeof store.newsFactIndex !== "number") store.newsFactIndex = 0;
if (typeof store.visualStyleIndex !== "number") store.visualStyleIndex = 0;
if (!store.regenVariantIndex || typeof store.regenVariantIndex !== "object") store.regenVariantIndex = {};
if (typeof store.currentVisualKey !== "string") store.currentVisualKey = "ABSURD_NEWSROOM";

const newsFacts = [
  {
    topic: "synthetic_nicotine_same_regulation",
    keyword: "합성니코틴 전자담배 규제",
    source: "Korea.kr / Pressian, 2026-02-03~2026-04-23",
    source_url: "https://www.korea.kr/news/policyNewsView.do?newsId=148959006",
    fact: "4월 24일부터 합성니코틴 액상형 전자담배도 ‘담배’로 묶였다.",
    jab: "어제까진 애매하다더니 오늘부턴 금연구역 규제까지 같이 온다.",
    question: "이게 질서 정리야, 아니면 늦게 온 뒷북이야?",
    emotion: "DEBATE",
    tags: ["#전자담배", "#합성니코틴", "#담배규제", "#4월24일"]
  },
  {
    topic: "non_smoking_area_fine",
    keyword: "전자담배 금연구역 과태료",
    source: "서울신문 / 동아일보, 2026-02-03~2026-02-04",
    source_url: "https://m.eye.seoul.co.kr/news/society/health-medical/2026/02/04/20260204008010",
    fact: "4월 24일부터 금연구역 액상 전담 사용도 과태료 10만원 얘기가 나온다.",
    jab: "기기는 작아졌는데 벌금 감각은 갑자기 일반담배랑 똑같아졌다.",
    question: "이거 알고도 ‘그냥 전담인데?’라고 할 수 있어?",
    emotion: "SHOCK",
    tags: ["#전자담배", "#금연구역", "#과태료10만원", "#담배정책"]
  },
  {
    topic: "tobacco_definition_37_years",
    keyword: "담배 정의 확대",
    source: "Korea JoongAng Daily / 동아일보, 2026-02-03",
    source_url: "https://koreajoongangdaily.joins.com/news/2026-02-03/national/socialAffairs/Revised-Tobacco-Business-Act-takes-effect-April-24-strengthens-regulations-on-ecigarettes/2515133",
    fact: "담배 정의가 37년 만에 ‘연초의 잎’에서 ‘니코틴 제품’까지 넓어졌다.",
    jab: "근데 소비자는 매장 앞에서야 갑자기 룰이 바뀐 걸 배운다.",
    question: "이건 보호야, 아니면 소비자만 늦게 맞는 패치야?",
    emotion: "ANGER",
    tags: ["#담배사업법", "#전자담배", "#니코틴", "#정책변화"]
  },
  {
    topic: "health_warning_ad_restriction",
    keyword: "전자담배 광고 제한",
    source: "Korea.kr, 2026-02-03",
    source_url: "https://www.korea.kr/news/policyNewsView.do?newsId=148959006",
    fact: "합성니코틴 액상형 전담도 건강경고 표시와 광고 제한이 적용된다.",
    jab: "맛 표현까지 막히면 사람들은 더 잘 고를까, 더 헷갈릴까.",
    question: "정보를 줄이는 게 보호라는 말, 납득돼?",
    emotion: "DEBATE",
    tags: ["#전자담배", "#광고제한", "#건강경고", "#소비자정보"]
  },
  {
    topic: "retailer_designation_penalty",
    keyword: "합성니코틴 도소매인 지정",
    source: "비전21뉴스, 2026-04-01",
    source_url: "https://www.vision21.kr/news/article.html?no=569593",
    fact: "안산시는 4월 23일까지 합성니코틴 도·소매인 지정 신청을 받았다.",
    jab: "지정 없이 팔면 6개월 이하 징역이나 500만원 이하 벌금까지 간다.",
    question: "이 정도면 안내야, 아니면 작은 매장 압박이야?",
    emotion: "ANGER",
    tags: ["#합성니코틴", "#도소매인지정", "#전자담배매장", "#규제시행"]
  }
];

const visualStyles = [
  {
    key: "ABSURD_NEWSROOM",
    media_prompt: "8-scene vertical reel, absurd Korean breaking-news comedy about vape regulation, no readable text, no brands, adult-only: confused vape device wearing a tiny suit at a news desk, giant 100000 won fine stamp, shopper holding empty wallet, cartoon regulation cloud, clerk pointing at a ridiculous rule maze, split screen angry commenters, receipt rolling like toilet paper, final unresolved debate face, mix photoreal mockumentary and cartoon inserts"
  },
  {
    key: "WALLET_MONSTER",
    media_prompt: "8-scene vertical reel, hilarious consumer panic visual, no readable text, no logos, adult-only: convenience store door, price tag monster eating a wallet, vape package wearing handcuffs, adult customer frozen at counter, tiny judge gavel beside a nicotine bottle, vending machine with judgmental eyes, receipt tornado, final yes-or-no debate stare, colorful Korean internet meme energy"
  },
  {
    key: "CCTV_CHAOS",
    media_prompt: "8-scene vertical reel, fake CCTV documentary comedy, no readable text, no brands, adult-only: overhead store camera view, adult shopper walking in confidently, sudden regulation sign blur, shelf transforms into maze, clerk shrugging, wallet tries to escape, cartoon exclamation bubble without text, customer exits looking betrayed, gritty real-life plus comic overlays"
  },
  {
    key: "COURTROOM_CARTOON",
    media_prompt: "8-scene vertical reel, surreal courtroom cartoon about vape regulation, no readable text, adult-only: vape bottle on witness stand, giant calendar page April 24, angry wallet as defendant, policy book slamming shut, adult shopper in jury seat, vending machine with age-check visor, receipt evidence pile, final split vote scene, funny but uncomfortable"
  },
  {
    key: "STREET_INTERVIEW",
    media_prompt: "8-scene vertical reel, chaotic Korean street interview comedy, no readable text, adult-only: interviewer asks adult vape users, exaggerated shocked faces, 100000 won fine visual metaphor, store counter confusion, cartoon thought bubble fight, two adults arguing yes/no, wallet close-up, final unresolved debate freeze-frame, raw handheld look"
  }
];

let selectedFact = newsFacts[store.newsFactIndex % newsFacts.length];
store.newsFactIndex = (store.newsFactIndex + 1) % newsFacts.length;

let selectedVisual;
if (isRegenMedia) {
  const current = visualStyles.find((v) => v.key === store.currentVisualKey) || visualStyles[0];
  if (typeof store.regenVariantIndex[current.key] !== "number") store.regenVariantIndex[current.key] = 1;
  selectedVisual = visualStyles[(visualStyles.findIndex((v) => v.key === current.key) + store.regenVariantIndex[current.key]) % visualStyles.length];
  store.regenVariantIndex[current.key] += 1;
} else {
  selectedVisual = visualStyles[store.visualStyleIndex % visualStyles.length];
  store.visualStyleIndex = (store.visualStyleIndex + 1) % visualStyles.length;
}
store.currentVisualKey = selectedVisual.key;

const lines = [selectedFact.fact, selectedFact.jab, selectedFact.question];
const caption = lines.join("\n");
const id = String(Date.now()) + "-" + Math.random().toString(36).slice(2, 8);

const item = {
  simulation_mode: false,
  mode: "production_content",
  niche: "vape",
  content_type: "news_based_debate",
  test_id: id,
  topic: selectedFact.topic,
  topic_keyword: selectedFact.keyword,
  source: selectedFact.source,
  source_url: selectedFact.source_url,
  emotion_trigger: selectedFact.emotion,
  hook: selectedFact.fact,
  body_lines: [selectedFact.jab, selectedFact.question],
  tension_ending: selectedFact.question,
  hashtags: selectedFact.tags.join(" "),
  caption,
  media_type: "funny_news_reel",
  media_prompt: selectedVisual.media_prompt,
  media_template_key: selectedVisual.key,
  content_rules_version: "v2_2026_04_news_debate",
  validation: {
    line1_fact_or_number: true,
    line2_friction: true,
    line3_comment_trigger: true,
    under_5_lines: true,
    no_corporate_phrases: true
  },
  chat_id: "7592247598",
  dm_response_library: {
    general_user: ["공개된 뉴스 기준으로만 말하면, 핵심은 4월 24일 이후 룰이 달라졌다는 점입니다.", "이건 취향 문제가 아니라 규제 체감 문제로 번질 수 있습니다."],
    curious_user: ["어느 부분이 제일 이상하게 느껴졌는지 먼저 봐야 합니다.", "숫자와 시행일 기준으로 보면 댓글이 갈릴 지점이 분명합니다."],
    business_owner: ["운영 관점에서는 판매/진열/안내 문구 리스크를 같이 봐야 합니다.", "다만 공개 DM에서는 출처가 확인된 범위까지만 말하겠습니다."],
    skeptical_user: ["의심하는 게 맞습니다. 그래서 날짜, 과태료, 법 적용 범위처럼 확인 가능한 것만 봐야 합니다."],
    extractor_user: ["출처 없는 내부 썰은 공유하지 않습니다.", "공개 기사와 정책자료 기준으로만 정리합니다."],
    follow_up_question: ["이걸 소비자 관점으로 볼까요, 매장 운영 관점으로 볼까요?"]
  },
  dm_routing_hints: {
    business_owner_keywords: ["매장", "도매", "소매", "지정", "재고", "진열", "광고", "벌금"],
    low_value_patterns: ["요약만", "정답만", "출처없이"],
    boundary_rule: "verified_news_only"
  },
  reply_markup: JSON.stringify({
    inline_keyboard: [
      [{ text: "Approve Reel", callback_data: "approve_reel|" + id }],
      [{ text: "Approve Carousel", callback_data: "approve_carousel|" + id }],
      [{ text: "Approve (Legacy)", callback_data: "approve_test|" + id }],
      [{ text: "Regen Text", callback_data: "regen_text|" + id }],
      [{ text: "Regen Media", callback_data: "regen_media|" + id }],
      [{ text: "Delete", callback_data: "delete_test|" + id }]
    ]
  })
};

return [{ json: item }];'''

reel_scenes_js = r'''const base = ($input.all()[0]?.json) || {};
const fact = String(base.hook || '').trim();
const jab = String((base.body_lines && base.body_lines[0]) || '').trim();
const question = String((base.body_lines && base.body_lines[1]) || base.tension_ending || '').trim();
const style = String(base.media_template_key || 'ABSURD_NEWSROOM');
const keyword = String(base.topic_keyword || '전자담배 규제').trim();

const styleNotes = {
  ABSURD_NEWSROOM: 'absurd Korean breaking-news comedy, photoreal mockumentary mixed with cartoon insert',
  WALLET_MONSTER: 'hilarious wallet monster visual, colorful meme-like realism and cartoon hybrid',
  CCTV_CHAOS: 'fake CCTV documentary chaos, gritty overhead camera plus comic overlays',
  COURTROOM_CARTOON: 'surreal courtroom cartoon, funny but uncomfortable adult regulation debate',
  STREET_INTERVIEW: 'chaotic street interview comedy, raw handheld adult reaction shots'
};
const mood = styleNotes[style] || styleNotes.ABSURD_NEWSROOM;

const scenes = [
  `scene 1/8, ${mood}, adult-only, ${keyword} breaking news moment, giant April 24 calendar visual, no readable text, no brand logos, subtitle idea '${fact}'`,
  `scene 2/8, completely different shot, confused adult shopper at store entrance, rule change hits like a cartoon thundercloud, no readable text`,
  `scene 3/8, funny symbolic shot, price tag or fine stamp chasing an empty wallet, exaggerated but not childish, no readable text`,
  `scene 4/8, surreal product comparison, vape package wearing tiny handcuffs beside normal receipt, adult consumer hesitation, no readable text`,
  `scene 5/8, absurd authority metaphor, vending machine with judgmental eyes or tiny courtroom gavel, regulation tension, no readable text`,
  `scene 6/8, mockumentary close-up, clerk shrugging while consumer calculates cost, ${jab}, no readable text`,
  `scene 7/8, debate visual, two adults split-screen yes/no reaction, comment-war energy, no smoking, no readable text`,
  `scene 8/8, final unresolved freeze-frame, shocked adult face plus empty wallet and question-mark shaped shadow, ${question}, no readable text`
];

return scenes.map((scene, idx) => ({
  json: {
    ...base,
    scene_index: idx + 1,
    scene_prompt: scene
  }
}));'''

carousel_content_js = r'''const items = $input.all();

return items.map(item => {
  const data = item.json || {};
  const fact = String(data.hook || "").trim();
  const jab = String((data.body_lines && data.body_lines[0]) || "").trim();
  const question = String((data.body_lines && data.body_lines[1]) || data.tension_ending || "").trim();
  const keyword = String(data.topic_keyword || data.topic || "전자담배 규제").trim();

  const slides = [
    fact || `${keyword}에서 숫자 하나가 바뀌었습니다.`,
    jab || "문제는 규제보다 사람들이 너무 늦게 안다는 겁니다.",
    "이건 취향 문제가 아니라, 모르면 갑자기 당하는 쪽에 가깝습니다.",
    "누군가는 보호라고 하고, 누군가는 뒷북이라고 할 겁니다.",
    question || "당신은 이 규제, 찬성입니까 반대입니까?"
  ];

  const carouselCaption = `${slides[0]}\n${slides[1]}\n${slides[4]}`;

  return {
    ...item,
    json: {
      ...data,
      carousel: {
        slides,
        caption: carouselCaption
      }
    }
  };
});'''

carousel_prompts_js = r'''const inputItems = $input.all();
const out = [];

const styles = [
  "absurd breaking-news thumbnail, giant calendar and shocked adult face, cinematic comedy",
  "cartoon wallet monster eating a receipt, funny Korean internet meme style, high contrast",
  "fake CCTV still of confused adult shopper in store maze, gritty documentary comedy",
  "surreal courtroom cartoon with vape bottle on witness stand, no brands, adult-only",
  "street interview reaction shot, two adults debating yes or no, raw handheld look"
];

for (const item of inputItems) {
  const data = item.json || {};
  const carousel = data.carousel || {};
  const slides = Array.isArray(carousel.slides) ? carousel.slides : [];
  const image_prompts = slides.map((slide, idx) => {
    const s = String(slide || "").trim();
    const style = styles[idx % styles.length];
    return `${style}, inspired by: ${s}, dark background, cinematic lighting, high contrast, minimal composition, symbolic emotional visual, no readable text, no logos, no minors, no smoking glamor`;
  });

  const base = {
    ...data,
    carousel: {
      ...carousel,
      image_prompts
    }
  };

  if (image_prompts.length === 0) {
    out.push({ json: base });
    continue;
  }

  image_prompts.forEach((prompt, idx) => {
    out.push({
      json: {
        ...base,
        carousel_prompt: prompt,
        carousel_slide_index: idx + 1
      }
    });
  });
}

return out;'''

wf = get_workflow(WID)
node(wf, "Build Simulation Content")["parameters"]["jsCode"] = build_sim_js
node(wf, "Build Reel Scene Prompts")["parameters"]["jsCode"] = reel_scenes_js
node(wf, "Build Carousel Content")["parameters"]["jsCode"] = carousel_content_js
node(wf, "Build Carousel Prompts")["parameters"]["jsCode"] = carousel_prompts_js
put_workflow(wf)

print(json.dumps({
    "updated": [
        "Build Simulation Content",
        "Build Reel Scene Prompts",
        "Build Carousel Content",
        "Build Carousel Prompts"
    ],
    "rule_version": "v2_2026_04_news_debate",
}, ensure_ascii=False, indent=2))
