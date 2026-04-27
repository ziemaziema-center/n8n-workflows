const input = ($input.first() && $input.first().json) ? $input.first().json : {};
const callbackRaw = String(input.callback_data || input.data || input.action || "");
const isRegenMedia = callbackRaw.startsWith("regen_media");

const store = $getWorkflowStaticData("global");
if (typeof store.templateIndex !== "number") store.templateIndex = 0;
if (typeof store.currentTemplateKey !== "string") store.currentTemplateKey = "T1_POLICY_ENTRY";
if (!store.regenVariantIndex || typeof store.regenVariantIndex !== "object") store.regenVariantIndex = {};
if (typeof store.contentMixIndex !== "number") store.contentMixIndex = 0;
if (typeof store.b2cPolicyIndex !== "number") store.b2cPolicyIndex = 0;
if (typeof store.b2bPolicyIndex !== "number") store.b2bPolicyIndex = 0;

const templates = [
  {
    key: "T1_POLICY_ENTRY",
    promptBase: "8-scene reel storyboard, real vape retail context, documentary realism, no text: 1) entering store under new tobacco rule notice 2) close shelf scan of disposable devices 3) two products with changed price tags 4) hand hesitating between options 5) staff points to compliant line only 6) customer checks old vs new package 7) checkout pause before payment 8) exit with doubtful expression, gritty lighting, imperfect handheld feel",
    promptVariants: [
      "8-scene reel storyboard, real convenience vape point, no text: 1) door sticker about new tobacco implementation 2) shelf crowding from supply shift 3) old label covered by new price label 4) buyer compares two similar SKUs 5) uncertain hand movement and pause 6) clerk redirects to allowed stock 7) payment moment with tension 8) customer leaves questioning decision, realistic mixed lighting",
      "8-scene reel storyboard, grounded shop sequence, no text: 1) customer enters after policy update day 2) fast scan of limited stock shelf 3) visible price jump tags on same category 4) hand pulls back from first choice 5) side glance at regulation guidance card 6) compare pod count and final cost 7) checkout hesitation under harsh light 8) face-level doubt before leaving, imperfect real-life composition",
      "8-scene reel storyboard, uncomfortable shopping narrative, no text: 1) new rule flyer at entrance 2) tense shelf browsing 3) similar product different final price 4) customer confusion over compliance sticker 5) employee suggests substitute line 6) close-up on unexpected total cost cue 7) card payment hesitation 8) slow exit with suspicion, realistic retail shadows"
    ]
  },
  {
    key: "T2_POLICY_PRICE_SHOCK",
    promptBase: "8-scene reel storyboard, policy-price tension, no text: 1) customer re-enters familiar vape store 2) notices changed price structure board 3) compares same flavor different compliance version 4) hand hovers, uncertain 5) supply-limited section highlighted 6) staff explains implementation impact 7) checkout amount surprises customer 8) customer freezes before leaving, natural retail realism",
    promptVariants: [
      "8-scene reel storyboard, price shock in vape retail, no text: 1) routine visit feeling 2) regulation-driven price board in frame 3) close shelf comparison with mismatched tags 4) customer turns product to inspect details 5) substitute stock shown due supply shift 6) doubtful eye-line toward counter 7) final total confrontation at checkout 8) silent regret exit, handheld documentary style",
      "8-scene reel storyboard, factual policy impact sequence, no text: 1) arrival at busy vape counter 2) new implementation notice beside shelf 3) old favorite now marked differently 4) buyer compares unit price and refill cycle 5) stock gap from distributor adjustment 6) staff points to limited compliant items 7) hesitation while tapping card 8) walkout with uneasy expression, gritty realism",
      "8-scene reel storyboard, consumer discomfort narrative, no text: 1) entering after regulation enforcement 2) searching previous go-to product 3) sudden price spread across similar SKUs 4) hand shifts between two choices 5) compliance sticker check moment 6) hidden total-cost realization 7) slow checkout decision 8) unresolved suspicion on exit, realistic store clutter"
    ]
  },
  {
    key: "T3_POLICY_SUPPLY_REACTION",
    promptBase: "8-scene reel storyboard, supply reaction under new tobacco implementation, no text: 1) shelf gaps from distribution change 2) customer asks for old option 3) staff says route changed after regulation 4) replacement product comparison 5) visible confusion over value 6) customer recalculates monthly spend 7) tense checkout compromise 8) post-purchase doubt, cinematic realism",
    promptVariants: [
      "8-scene reel storyboard, store reaction sequence, no text: 1) opened boxes behind counter 2) half-empty shelf and new compliant line 3) buyer requests previous best-seller 4) staff indicates delayed restock 5) two alternatives with different final costs 6) hesitation and second look at tags 7) reluctant payment 8) dissatisfied exit, imperfect real-life framing",
      "8-scene reel storyboard, regulation-supply tension, no text: 1) customer enters expecting usual purchase 2) notices missing SKU blocks 3) employee references implementation timeline 4) buyer compares substitute products 5) hand pauses above higher-cost option 6) quick mental monthly budget check 7) pressured checkout moment 8) unresolved frustration while leaving, grounded lighting",
      "8-scene reel storyboard, market shift in-store, no text: 1) retail floor with restock cart 2) old product lane reduced 3) new rule cue near counter 4) buyer toggles between alternatives 5) uncertainty over value-for-money 6) subtle manipulation feeling at display order 7) checkout delay before approval 8) quiet suspicion after purchase, realistic documentary tone"
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

const b2cPolicySeeds = [
  {
    topic: "policy_implementation_price_behavior",
    hook: "너 아직도 그 구조 이해 못한거지?",
    l1: "신규 담배 규정 시행 첫 주에는 같은 라인처럼 보여도 체감 가격이 다르게 꽂힌다. 카운터 앞에서 두 개를 들고 고민하는 순간, 매장은 이미 규정 대응 재고를 앞줄에 배치해 선택 순서를 고정하고 비교 시간을 짧게 만든다.",
    l2: "사실 포인트는 단순 가격 인상이 아니다. 시행 이후엔 공급 라우트가 재정렬되면서 인기 SKU가 끊기고, 대체 SKU의 월 유지비가 더 빨리 누적된다. 그래서 '지금은 싸다'는 판단이 다음 교체 시점에서 바로 뒤집히고, 체감 손실이 늦게 터진다.",
    l3: "이 흐름을 모르면 본인은 합리적으로 샀다고 믿는데, 실제론 매번 불리한 구조를 반복 구매한다. 그때부터는 취향 문제가 아니라 규정 이후 시장 반응을 못 읽어서 생긴 손실 패턴이고, 소비자는 이유도 모른 채 계속 손해를 감수하게 된다.",
    tags: ["#베이프", "#전자담배", "#신규규정", "#가격변동", "#시장반응"]
  },
  {
    topic: "policy_implementation_store_reaction",
    hook: "이거 모르고 있으면 그냥 계속 당하는거다",
    l1: "매장 들어가서 가격표만 보고 집으면 이미 늦는다. 신규 규정 시행 구간에서는 매장들이 리스크 낮은 라인을 먼저 노출하고, 기존 회전 라인은 뒤로 밀거나 품절처럼 보이게 만든다. 소비자는 선택권이 줄었다는 사실을 계산이 끝난 뒤에야 체감한다.",
    l2: "팩트는 명확하다. 시행 직후엔 동일 카테고리라도 공급 안정성 차이 때문에 최종 체감비용이 갈라진다. 표면 단가가 낮아도 교체 주기, 재입고 지연, 대체품 전환까지 합치면 월지출이 더 커지고, 구매 빈도도 더 불리하게 바뀐다.",
    l3: "문제는 대부분 여기서 '내가 선택을 잘못했나'로 끝낸다는 점이다. 실제론 시행 이후 유통 반응과 매장 동선이 먼저 작동했고, 너는 그 구조 안에서 비싼 쪽으로 유도된 거다. 그걸 모르면 다음 방문에서도 같은 방식으로 다시 당한다.",
    tags: ["#베이프", "#전자담배", "#정책시행", "#공급변화", "#소비자손해"]
  },
  {
    topic: "policy_implementation_supply_shift",
    hook: "매장에서 이거 안 보면 그냥 호구된다",
    l1: "신규 담배 규정 시행 후 가장 먼저 바뀌는 건 추천 멘트가 아니라 진열 구조다. 카운터 근처엔 규정 대응 재고가 먼저 배치되고, 기존 익숙한 옵션은 재고 공백이나 지연으로 체감 선택지에서 빠진다. 그래서 소비자는 처음부터 동일 비교를 못 하게 된다.",
    l2: "현장 팩트는 반복된다. 시행 직후 공급 이동이 생기면 동일 사용량 기준에서도 월 비용이 다르게 누적되고, 소비자는 처음 결제 순간엔 그 차이를 거의 못 본다. 그래서 결제는 빠르게 끝나도 후회는 다음 주에 시작되고, 재구매 때 손실이 더 커진다.",
    l3: "이걸 단순 '매장마다 다르다'로 넘기면 계속 당한다. 지금 필요한 건 취향 탐색이 아니라 시행 이후 가격-공급-노출 순서가 어떻게 묶여 작동하는지 읽는 기준이다. 그 기준이 없으면 매번 불리한 선택을 스스로 반복하게 된다.",
    tags: ["#베이프", "#전자담배", "#규정시행효과", "#공급이동", "#가격구조"]
  },
  {
    topic: "policy_implementation_market_effect",
    hook: "이 구조 모르면 평생 비싸게 산다",
    l1: "신규 담배 규정이 시행되면 시장은 단가보다 속도로 반응한다. 익숙한 제품이 먼저 줄고 대체 라인이 밀려오는데, 소비자는 '같은 계열이면 비슷하겠지'라고 착각한 채 결제한다. 이 순간 이미 비교 기준이 흐려져서 손실 루트가 열리기 시작한다.",
    l2: "여기서 팩트 하나. 시행 초기에는 매장별로 재고 복구 속도가 다르고, 그 차이가 실제 구매자 체감가를 갈라놓는다. 즉, 가격표 한 줄은 같아 보여도 월 기준 총비용은 전혀 같지 않고, 구매 주기마다 격차가 더 커진다.",
    l3: "그래서 문제는 정보 부족이 아니다. 시행 후 시장 반응을 모른 채 진열된 순서대로 고르면, 본인은 선택했다고 생각하지만 구조적으로 더 비싼 루트에 고정된다. 결국 똑같은 예산으로도 더 적게 가져가고 더 자주 다시 사게 된다.",
    tags: ["#베이프", "#전자담배", "#신규담배규정", "#시장효과", "#체감비용"]
  }
];

const b2bPolicySeeds = [
  {
    topic: "policy_hidden_b2b_signal",
    hook: "너 아직도 왜 어떤 매장만 안 무너지는지 모르지?",
    l1: "신규 담배 규정 시행 후 소비자 불만은 취향 이슈처럼 보이지만, 실제로는 진열 순서와 대체 SKU 전환 속도에서 갈린다. 버티는 매장은 시행 첫 주부터 규정 대응 재고를 앞세우고, 월 유지비 기준으로 선택을 유도해 이탈을 늦춘다.",
    l2: "팩트는 간단하다. 공급 라인이 흔들리는 구간에서 회전 유지에 실패하면 동일 방문자 수에서도 남는 구조가 얇아진다. 반대로 시행 반응을 읽은 매장은 가격표보다 동선 설계로 체감 손실을 줄이고, 재방문 체감을 방어한다.",
    l3: "이 차이를 모르면 소비자는 계속 당했다고 느끼고, 매장은 '운이 나빴다'고 착각한다. 시행 구간에선 제품 설명보다 구조 설계가 먼저 수익과 신뢰를 갈라버리고, 그 격차는 시간이 갈수록 더 벌어진다.",
    tags: ["#베이프", "#전자담배", "#정책시행", "#매장반응", "#구조신호"]
  }
];

const nowSeoul = new Date(
  new Date().toLocaleString("en-US", { timeZone: "Asia/Seoul" })
);
const hardPolicyStart = new Date("2026-04-22T00:00:00+09:00");
const hardPolicyEnd = new Date("2026-04-30T23:59:59+09:00");
const policyHardLock = nowSeoul >= hardPolicyStart && nowSeoul <= hardPolicyEnd;

const mixSlot = store.contentMixIndex % 10;
const isB2BLeaning = mixSlot === 9; // deterministic 90% B2C / 10% hidden B2B
store.contentMixIndex = (store.contentMixIndex + 1) % 10;

let pick;
if (policyHardLock) {
  if (isB2BLeaning) {
    pick = b2bPolicySeeds[store.b2bPolicyIndex % b2bPolicySeeds.length];
    store.b2bPolicyIndex = (store.b2bPolicyIndex + 1) % b2bPolicySeeds.length;
  } else {
    pick = b2cPolicySeeds[store.b2cPolicyIndex % b2cPolicySeeds.length];
    store.b2cPolicyIndex = (store.b2cPolicyIndex + 1) % b2cPolicySeeds.length;
  }
} else {
  if (isB2BLeaning) {
    pick = b2bPolicySeeds[store.b2bPolicyIndex % b2bPolicySeeds.length];
    store.b2bPolicyIndex = (store.b2bPolicyIndex + 1) % b2bPolicySeeds.length;
  } else {
    pick = b2cPolicySeeds[store.b2cPolicyIndex % b2cPolicySeeds.length];
    store.b2cPolicyIndex = (store.b2cPolicyIndex + 1) % b2cPolicySeeds.length;
  }
}

const fixedEnding = "그런데 그거 알어?";
const caption = [pick.hook, pick.l1, pick.l2, pick.l3, fixedEnding, pick.tags.join(" ")].join("\n");
const id = String(Date.now()) + "-" + Math.random().toString(36).slice(2, 8);

const item = {
  simulation_mode: false,
  mode: "production_content",
  niche: "vape",
  content_type: "vape_news_info",
  test_id: id,
  topic: pick.topic,
  hook: pick.hook,
  body_lines: [pick.l1, pick.l2, pick.l3],
  tension_ending: fixedEnding,
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
