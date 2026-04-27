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
    ],
    mediaUrl: "https://www.pexels.com/download/video/2340434/"
  },
  {
    key: "T2_SHOP_SIGNAL",
    promptBase: "vape shop shelf with pods and devices, realistic lighting, no text",
    promptVariants: [
      "vape shop shelf with pods and devices, wider composition, realistic lighting, no text",
      "vape shop shelf close framing on pods and devices, realistic lighting, no text",
      "vape shop shelf with slight composition change, realistic lighting, no text"
    ],
    mediaUrl: "https://www.pexels.com/download/video/2340461/"
  },
  {
    key: "T3_POLICY_TENSION",
    promptBase: "dark minimal scene with vape device silhouette representing regulation or price tension, cinematic lighting, no text",
    promptVariants: [
      "dark minimal scene with vape device silhouette and stronger regulation tension mood, cinematic lighting, no text",
      "dark minimal scene with vape device silhouette, deeper shadows and price tension mood, cinematic lighting, no text",
      "dark minimal scene, tighter frame on vape device silhouette with regulation tension mood, no text"
    ],
    mediaUrl: "https://www.pexels.com/download/video/2340433/"
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

const seeds = [
  {
    topic: "price_policy",
    hook: "\ub2f4\ubc30\uac12 1\ub9cc\uc6d0 \uac00\uba74, \uc804\uc790\ub2f4\ubc30 \ub9e4\uc7a5\ubd80\ud130 \uac08\ub9b0\ub2e4",
    l1: "\uac00\uaca9 \uc778\uc0c1 \uc774\uc288\uac00 \ub728\uba74 \uad6c\ub9e4 \ub3d9\uc120\uc774 \uba3c\uc800 \ubc14\ub010\ub2e4.",
    l2: "\ubb38\uc81c\ub294 \uc81c\ud488\ubcf4\ub2e4 \ud68c\uc804 \uc18d\ub3c4\uc640 \uac1d\ub2e8\uac00\uac00 \ubd84\ub9ac\ub41c\ub2e4.",
    l3: "\uc774 \uad6c\uac04 \ub193\uce58\uba74 \uc7ac\uace0\ub791 \ub9c8\uc9c4\uc774 \uac19\uc774 \ud754\ub4e4\ub9b0\ub2e4.",
    end: "\uc5ec\uae30\uc11c \ub300\ubd80\ubd84 \ub300\uc751 \uc21c\uc11c\ubd80\ud130 \ud2c0\ub9b0\ub2e4.",
    tags: ["#\uc804\uc790\ub2f4\ubc30", "#\ubca0\uc774\ud504", "#\uc815\ucc45\uc774\uc288", "#\ub9e4\uc7a5\uc6b4\uc601", "#\uc2dc\uc7a5\ubcc0\ud654"]
  },
  {
    topic: "regulation",
    hook: "\ub2e8\uc18d \uae30\uc900 \ubc14\ub00c\uba74, \ub9e4\ucd9c\ubcf4\ub2e4 \uba3c\uc800 \ud130\uc9c0\ub294 \uac8c \uc788\ub2e4",
    l1: "\ud45c\uc2dc\ub294 \uac19\uc544 \ubcf4\uc5ec\ub3c4 \uc801\uc6a9 \uae30\uc900\uc740 \uc774\ubbf8 \ub2ec\ub77c\uc84c\ub2e4.",
    l2: "\uc751\ub300 \ubb38\uad6c \ud558\ub098\uac00 \ubbfc\uc6d0\uacfc \ub9ac\ubdf0\ub97c \uac08\ub77c\ubc84\ub9b0\ub2e4.",
    l3: "\ubc84\ud2f0\uba74 \ub204\uc801 \ub9ac\uc2a4\ud06c\uac00 \ube44\uc6a9\uc73c\ub85c \ubc14\ub010\ub2e4.",
    end: "\uc774 \uae30\uc900\uc740 \uacf5\uac1c \uae00\uc5d0\uc11c \ub05d\uae4c\uc9c0 \ubabb \ud47c\ub2e4.",
    tags: ["#\uc804\uc790\ub2f4\ubc30", "#\ubca0\uc774\ud504\ub9e4\uc7a5", "#\uaddc\uc815\uccb4\ud06c", "#\uc6b4\uc601\ub9ac\uc2a4\ud06c", "#\ub9e4\ucd9c\ubc29\uc5b4"]
  },
  {
    topic: "market_shift",
    hook: "\uc694\uc998 \ubca0\uc774\ud504 \uc798 \ub098\uac00\ub294 \ub9e4\uc7a5, \uacf5\ud1b5\uc810 \ud558\ub098 \uc788\uc74c",
    l1: "\uc2e0\uc81c\ud488\ubcf4\ub2e4 \ud68c\uc804 \uad6c\uc870\ub97c \uba3c\uc800 \ubc14\uafbc\ub2e4.",
    l2: "\uace0\uac1d\uc740 \ub9db\ubcf4\ub2e4 \uc120\ud0dd \ud53c\ub85c\uc5d0\uc11c \uba3c\uc800 \uc774\ud0c8\ud55c\ub2e4.",
    l3: "\uc9c4\uc5f4\uacfc \uad8c\uc7a5 \uc21c\uc11c\uc5d0\uc11c \ub9e4\ucd9c\uc774 \uac08\ub9b0\ub2e4.",
    end: "\uc774 \ud3ec\uc778\ud2b8 \ub193\uce58\uba74 \uacc4\uc18d \ud560\uc778\uc73c\ub85c \ubc84\ud2f0\uac8c \ub41c\ub2e4.",
    tags: ["#\uc804\uc790\ub2f4\ubc30", "#\ubca0\uc774\ud504\uc0f5", "#\uace0\uac1d\uc2ec\ub9ac", "#\uc7ac\uace0\ud68c\uc804", "#\ub9c8\uc9c4\uad6c\uc870"]
  }
];

const pick = seeds[Number(String(Date.now()).slice(-2)) % seeds.length];
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
  media_url: selectedTemplate.mediaUrl,
  video_url: selectedTemplate.mediaUrl,
  media_type: "vape_visual",
  media_prompt: selectedPrompt,
  media_template_key: selectedTemplate.key,
  chat_id: "7592247598",
  dm_response_library: {
    general_user: ["\uc9c0\uae08 \ubcf4\uc2e0 \uac74 \uacf5\uac1c \uac00\ub2a5\ud55c \ubc94\uc704\ub9cc \uc815\ub9ac\ud55c \uac81\ub2c8\ub2e4.", "\uc815\ubcf4\ub9cc \ubcf4\uba74 \uacc4\uc18d \uac19\uc740 \uad6c\uac04\uc5d0\uc11c \ub9c9\ud799\ub2c8\ub2e4."],
    curious_user: ["\ud575\uc2ec\uc740 \uc81c\ud488\ubcf4\ub2e4 \uc6b4\uc601 \uae30\uc900 \uc21c\uc11c\uc785\ub2c8\ub2e4.", "\uc774 \ub2e4\uc74c \ub2e8\uacc4\ub294 \uacf5\uac1c\ud615\uc73c\ub85c \ub2e4 \ubabb \ud47c\ub2e4."],
    business_owner: ["\uc774\uac74 \uadf8\ub0e5 \uc815\ubcf4\uac00 \uc544\ub2c8\ub77c \uc6b4\uc601 \uad6c\uc870 \uc774\uc288\uc785\ub2c8\ub2e4.", "\ub9c8\uc9c4, \ud68c\uc804, \ub9ac\uc2a4\ud06c\ub97c \uac19\uc774 \ubd10\uc57c \uacb0\ub860\uc774 \ub9de\uc2b5\ub2c8\ub2e4."],
    skeptical_user: ["\uc758\uc2ec\uc740 \ub9de\ub294 \ubc18\uc751\uc785\ub2c8\ub2e4.", "\uacb0\uacfc\ubcf4\ub2e4 \uae30\uc900\ubd80\ud130 \ub9de\ucdb0\uc57c \ud310\ub2e8\uc774 \ub429\ub2c8\ub2e4."],
    extractor_user: ["\uacf5\uac1c DM\uc5d0\uc11c\ub294 \uc5ec\uae30\uae4c\uc9c0\ub9cc \uacf5\uc720\ud569\ub2c8\ub2e4.", "\ud575\uc2ec \uad6c\uc870\ub294 \ub2e8\uacc4 \ud655\uc778 \uc804\uc5d0\ub294 \uc5f4\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4."],
    follow_up_question: ["\uc9c0\uae08 \uac1c\uc778\uc6a9 \uae30\uc900\uc778\uac00\uc694, \ub9e4\uc7a5 \uc6b4\uc601 \uae30\uc900\uc778\uac00\uc694?"]
  },
  dm_routing_hints: {
    business_owner_keywords: ["\ub9e4\uc7a5", "\uc6b4\uc601", "\uc7ac\uace0", "\ub9c8\uc9c4", "\ud68c\uc804", "\ubc1c\uc8fc", "\uc9c4\uc5f4", "\ub9ac\uc2a4\ud06c"],
    low_value_patterns: ["\uadf8\ub0e5 \uc815\ubcf4", "\uc694\uc57d\ub9cc", "\uc815\ub2f5\ub9cc"],
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
