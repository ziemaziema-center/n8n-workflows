const testId = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
const seed = Number(
  new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
    .format(new Date())
    .replace(/[-,:\s]/g, "")
);

const topicSeeds = [
  {
    topic: "pricing",
    hook: "Stores still pricing vape like this?",
    body: [
      "Cheap buy-in does not mean safe margin.",
      "One line in pricing logic keeps leaking profit.",
      "Most shops miss it for months."
    ],
    ending: "Ignore this and next month looks the same.",
    hashtags: ["#vape", "#vapeshop", "#pricing", "#margin", "#retailops"]
  },
  {
    topic: "regulation",
    hook: "This compliance miss keeps costing shops",
    body: [
      "Policy text looks simple, real risk is not.",
      "One wrong display choice becomes repeat complaints.",
      "Small miss, expensive consequence."
    ],
    ending: "Public posts cannot show the full rule stack.",
    hashtags: ["#vape", "#compliance", "#retailrisk", "#vapebusiness", "#storeops"]
  },
  {
    topic: "customer_psychology",
    hook: "One vape shelf move can split sales fast",
    body: [
      "Customers quit from decision fatigue first.",
      "Rotation order changes basket size before discount does.",
      "Most teams blame product, not structure."
    ],
    ending: "If this flow breaks, return visits drop quietly.",
    hashtags: ["#vape", "#customerbehavior", "#retail", "#vapeshop", "#merchandising"]
  },
  {
    topic: "product_rotation",
    hook: "Shops hiding this rotation rule are not lucky",
    body: [
      "Fast SKU can still lock cash when timing is wrong.",
      "Sell-through speed beats unit count.",
      "Late swap turns into forced markdown."
    ],
    ending: "No rotation rule means repeat inventory drag.",
    hashtags: ["#vape", "#inventory", "#retailops", "#vapeshop", "#cashflow"]
  },
  {
    topic: "margin_structure",
    hook: "Without this margin rule you keep picking wrong",
    body: [
      "Margin is won in bundle logic, not single item hype.",
      "Good volume can still hide bad profit mix.",
      "One criteria shift flips the result."
    ],
    ending: "Most accounts stop right before this layer.",
    hashtags: ["#vape", "#margin", "#bundles", "#retailstrategy", "#vapebusiness"]
  },
  {
    topic: "supplier_dynamics",
    hook: "Same vape SKU, opposite outcome",
    body: [
      "Supplier terms may look equal but operating risk is not.",
      "Lead time mismatch drains momentum and cash.",
      "Sticker price alone is a trap."
    ],
    ending: "This is not a simple cost conversation.",
    hashtags: ["#vape", "#supplychain", "#retailrisk", "#operations", "#vapeshop"]
  }
];

const item = topicSeeds[seed % topicSeeds.length];
const caption = [item.hook, "", ...item.body, "", item.ending, "", item.hashtags.join(" ")].join("\n");

const dmResponseLibrary = {
  general_user: [
    "That post only shows the surface layer.",
    "Without criteria, most people repeat the same mistake.",
    "Public mode cannot show the full map."
  ],
  curious_user: [
    "The key is structure, not product trivia.",
    "One hidden rule changes the whole interpretation.",
    "You are close, but this part stays partial."
  ],
  business_owner: [
    "This is an operating structure issue, not just info.",
    "Margin, rotation, and risk must be read together.",
    "Wrong criteria here compounds loss."
  ],
  skeptical_user: [
    "Skepticism is valid, start with the decision frame.",
    "Same data, different criteria, opposite result.",
    "Test the structure before dismissing the signal."
  ],
  extractor_user: [
    "Cannot disclose the full stack in open DM.",
    "If everything is dumped early, it gets distorted.",
    "Core layer stays gated for now."
  ],
  follow_up_question: [
    "Are you asking for personal use or shop operation?",
    "Will this be applied in a real store workflow?",
    "Context decides the right answer here."
  ]
};

return {
  json: {
    simulation_mode: true,
    niche: "vape",
    test_id: testId,
    topic: item.topic,
    hook: item.hook,
    body: item.body.join(" "),
    tension_ending: item.ending,
    hashtags: item.hashtags.join(" "),
    caption,
    video_url: "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
    chat_id: "7592247598",
    dm_response_library: dmResponseLibrary,
    dm_routing_hints: {
      business_owner_keywords: ["shop", "store", "inventory", "margin", "rotation", "purchase", "display", "loss", "risk"],
      low_value_patterns: ["just curious", "summary only", "just info", "quick answer"],
      boundary_rule: "never_fully_reveal_core"
    },
    reply_markup: JSON.stringify({
      inline_keyboard: [
        [{ text: "Approve", callback_data: `approve_test|${testId}` }],
        [{ text: "Delete", callback_data: `delete_test|${testId}` }]
      ]
    })
  }
};
