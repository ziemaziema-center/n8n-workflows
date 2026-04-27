const input = ($input.first() && $input.first().json) ? $input.first().json : {};
const callbackRaw = String(input.callback_data || input.data || input.action || "");
const isRegenMedia = callbackRaw.startsWith("regen_media");

const store = $getWorkflowStaticData("global");
if (typeof store.templateIndex !== "number") store.templateIndex = 0;
if (typeof store.currentTemplateKey !== "string") store.currentTemplateKey = "T1_DEVICE_FOCUS";
if (!store.regenVariantIndex || typeof store.regenVariantIndex !== "object") store.regenVariantIndex = {};

const templates = [
  {
    key: "T1_DEVICE_FOCUS",
    promptBase: "close-up vape device with vapor, dark cinematic lighting, high contrast, no text",
    promptVariants: [
      "close-up vape device with stronger vapor, dark cinematic lighting, high contrast, no text",
      "close-up vape device, darker lighting, high contrast, no text",
      "closer angle on vape device with vapor, dark cinematic lighting, no text"
    ]
  },
  {
    key: "T2_SHOP_SIGNAL",
    promptBase: "vape shop shelf with pods and devices, realistic lighting, no text",
    promptVariants: [
      "vape shop shelf with pods and devices, wider composition, realistic lighting, no text",
      "vape shop shelf close framing on pods and devices, realistic lighting, no text",
      "vape shop shelf with slight composition change, realistic lighting, no text"
    ]
  },
  {
    key: "T3_POLICY_TENSION",
    promptBase: "dark minimal scene with vape device silhouette representing regulation or price tension, cinematic lighting, no text",
    promptVariants: [
      "dark minimal scene with vape device silhouette and stronger regulation tension mood, cinematic lighting, no text",
      "dark minimal scene with vape device silhouette, deeper shadows and price tension mood, cinematic lighting, no text",
      "dark minimal scene, tighter frame on vape device silhouette with regulation tension mood, no text"
    ]
  }
];

const templateMap = Object.fromEntries(templates.map((t) => [t.key, t]));
let selectedTemplate;
let selectedPrompt;

if (isRegenMedia) {
  selectedTemplate = templateMap[store.currentTemplateKey] || templates[0];
  if (typeof store.regenVariantIndex[selectedTemplate.key] !== "number") {
    store.regenVariantIndex[selectedTemplate.key] = 0;
  }
  const vIdx = store.regenVariantIndex[selectedTemplate.key] % selectedTemplate.promptVariants.length;
  selectedPrompt = selectedTemplate.promptVariants[vIdx];
  store.regenVariantIndex[selectedTemplate.key] = (store.regenVariantIndex[selectedTemplate.key] + 1) % selectedTemplate.promptVariants.length;
} else {
  selectedTemplate = templates[store.templateIndex % templates.length];
  selectedPrompt = selectedTemplate.promptBase;
  store.currentTemplateKey = selectedTemplate.key;
  store.templateIndex = (store.templateIndex + 1) % templates.length;
}

const id = String(Date.now()) + "-" + Math.random().toString(36).slice(2, 8);

// 90% B2C consumer-facing + 10% B2B-leaning seeds
const b2cSeeds = [
  {
    topic: "buying_mistake_device",
    hook: "이거 보고 고르면, 결국 다시 사게 된다",
    l1: "처음엔 싸게 산 느낌인데 오래 못 간다.",
    l2: "문제는 성능보다 선택 순서를 거꾸로 잡는 데 있다.",
    l3: "기준 없이 고르면 돈보다 시간부터 새기 시작한다.",
    end: "여기서 대부분 같은 실수를 반복한다.",
    tags: ["#전자담배", "#베이프", "#구매실수", "#선택기준", "#손해패턴"]
  },
  {
    topic: "flavor_confusion",
    hook: "맛이 안 맞는 게 아니라, 고르는 흐름이 틀렸다",
    l1: "향만 보고 고르면 초반 만족감이 빨리 꺼진다.",
    l2: "실제론 니코틴/흡입감/지속감 순서가 먼저다.",
    l3: "이 순서 하나 틀리면 계속 갈아타게 된다.",
    end: "결국 돈은 더 쓰는데 만족은 더 짧아진다.",
    tags: ["#전자담배", "#베이프액상", "#플레이버선택", "#초보실수", "#지출누수"]
  },
  {
    topic: "price_value_confusion",
    hook: "싸게 샀다고 안심하면, 나중에 더 비싸진다",
    l1: "본체 가격만 보면 판단이 자꾸 어긋난다.",
    l2: "소모 속도랑 교체 주기까지 같이 봐야 맞다.",
    l3: "숨은 비용 구조를 빼고 계산하면 계속 손해다.",
    end: "이 구간에서 체감 가성비가 뒤집힌다.",
    tags: ["#전자담배", "#가성비", "#숨은비용", "#선택구조", "#소비자팁"]
  },
  {
    topic: "common_misunderstanding",
    hook: "많이들 착각한다, 문제는 제품이 아니다",
    l1: "입문 장비가 나쁜 게 아니라 조합이 안 맞는다.",
    l2: "코일/출력/흡입 템포가 따로 놀면 금방 지친다.",
    l3: "선택 기준을 하나로 묶지 않으면 반복된다.",
    end: "여기서 대부분 포기하거나 과소비로 간다.",
    tags: ["#전자담배", "#베이프초보", "#오해포인트", "#조합기준", "#반복실수"]
  },
  {
    topic: "regret_pattern",
    hook: "처음 만족했는데 금방 후회하는 이유, 거의 같다",
    l1: "첫인상만 보고 고르면 유지 구간에서 무너진다.",
    l2: "데일리 사용은 편의성 구조가 먼저다.",
    l3: "선택 흐름이 뒤집히면 재구매 루프가 시작된다.",
    end: "이 패턴 못 끊으면 계속 바꾸게 된다.",
    tags: ["#전자담배", "#베이프", "#후회패턴", "#재구매루프", "#선택흐름"]
  },
  {
    topic: "device_selection_risk",
    hook: "이 기준 없이 기기 고르면, 거의 다 여기서 틀린다",
    l1: "스펙 숫자만 보면 실사용 체감이 빗나간다.",
    l2: "손에 맞는 사용 구조를 먼저 잡아야 한다.",
    l3: "기준 없는 비교는 결국 같은 결론으로 돌아온다.",
    end: "다른 제품으로 바꿔도 결과가 비슷한 이유다.",
    tags: ["#전자담배", "#기기선택", "#비교실수", "#사용기준", "#손해방지"]
  },
  {
    topic: "user_side_risk",
    hook: "이 상태로 쓰면 문제 생긴다, 시간문제다",
    l1: "자극만 줄이려다 밸런스를 더 망치는 경우 많다.",
    l2: "체감 불편은 대개 세팅 기준이 안 맞아서 나온다.",
    l3: "기준 하나만 바로잡아도 반복 불만이 줄어든다.",
    end: "대부분 이걸 늦게 알아서 비용이 커진다.",
    tags: ["#전자담배", "#사용리스크", "#세팅기준", "#반복불편", "#소비자경고"]
  },
  {
    topic: "choice_order",
    hook: "뭘 살지보다 먼저 정해야 하는 게 있다",
    l1: "제품보다 사용 순서를 먼저 고정해야 덜 흔들린다.",
    l2: "순서가 없으면 추천 받아도 다시 흔들린다.",
    l3: "선택 구조를 고정하면 낭비가 눈에 띄게 줄어든다.",
    end: "여기서 멈추면 계속 같은 선택으로 돌아온다.",
    tags: ["#전자담배", "#선택순서", "#기준설정", "#낭비방지", "#베이프팁"]
  },
  {
    topic: "hidden_cost_consumer",
    hook: "이거 모르면 절약하는 줄 알고 더 쓴다",
    l1: "겉가격은 낮아도 유지비 흐름이 다르면 끝이 다르다.",
    l2: "교체 타이밍 구조를 모르고 쓰면 지출이 커진다.",
    l3: "소비자 기준에서도 비용 흐름을 봐야 맞다.",
    end: "여기서 대부분 계산이 틀어진다.",
    tags: ["#전자담배", "#유지비", "#숨은지출", "#선택실수", "#절약착각"]
  }
];

const b2bSeeds = [
  {
    topic: "hidden_b2b_signal_rotation",
    hook: "같은 제품도 왜 어떤 곳은 계속 팔리고, 어떤 곳은 멈출까",
    l1: "표면은 취향 문제처럼 보여도 실제로는 선택 구조 차이다.",
    l2: "진열/권장 순서가 바뀌면 소비자 반응 흐름도 달라진다.",
    l3: "이 기준을 모르면 같은 품목도 회전이 멈춘다.",
    end: "겉으로는 비슷한데 결과는 여기서 갈린다.",
    tags: ["#전자담배", "#베이프", "#선택구조", "#회전포인트", "#가격구조"]
  }
];

const entropy = Number(String(Date.now()).slice(-4));
const isB2BLeaning = (entropy % 10) === 0; // ~10%
const pool = isB2BLeaning ? b2bSeeds : b2cSeeds;
const pick = pool[entropy % pool.length];

const caption = [pick.hook, pick.l1, pick.l2, pick.l3, pick.end, pick.tags.join(" ")].join("\n");

const item = {
  simulation_mode: false,
  mode: "production_content",
  niche: "vape",
  content_type: "vape_news_info",
  test_id: id,
  topic: pick.topic,
  hook: pick.hook,
  body_lines: [pick.l1, pick.l2, pick.l3],
  tension_ending: pick.end,
  hashtags: pick.tags.join(" "),
  caption,
  media_type: "vape_visual",
  media_prompt: selectedPrompt,
  media_template_key: selectedTemplate.key,
  chat_id: "7592247598",
  dm_response_library: {
    general_user: ["지금 보신 건 공개 가능한 범위만 정리한 겁니다.", "정보만 보면 계속 같은 구간에서 막힙니다."],
    curious_user: ["핵심은 제품보다 운영 기준 순서입니다.", "이 다음 단계는 공개형으로 다 못 풉니다."],
    business_owner: ["이건 그냥 정보가 아니라 운영 구조 이슈입니다.", "마진, 회전, 리스크를 같이 봐야 결론이 맞습니다."],
    skeptical_user: ["의심은 맞는 반응입니다.", "결과보다 기준부터 맞춰야 판단이 됩니다."],
    extractor_user: ["공개 DM에서는 여기까지만 공유합니다.", "핵심 구조는 단계 확인 전에는 열지 않습니다."],
    follow_up_question: ["지금 개인용 기준인가요, 매장 운영 기준인가요?"]
  },
  dm_routing_hints: {
    business_owner_keywords: ["매장", "운영", "재고", "마진", "회전", "발주", "진열", "리스크"],
    low_value_patterns: ["그냥 정보", "요약만", "정답만"],
    boundary_rule: "never_fully_reveal_core"
  },
  reply_markup: JSON.stringify({
    inline_keyboard: [
      [{ text: "Approve", callback_data: "approve_test|" + id }],
      [{ text: "Regen Text", callback_data: "regen_text|" + id }],
      [{ text: "Regen Media", callback_data: "regen_media|" + id }],
      [{ text: "Delete", callback_data: "delete_test|" + id }]
    ]
  })
};

return [{ json: item }];
