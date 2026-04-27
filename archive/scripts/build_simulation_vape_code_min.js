const id = String(Date.now()) + "-" + Math.random().toString(36).slice(2, 8);
const variants = [
  {
    hook: "This vape pricing rule leaks margin",
    body: [
      "Cheap buy-in does not guarantee profit.",
      "One criteria gap keeps draining cash.",
      "Most shops detect it too late."
    ],
    ending: "This layer stays unresolved in public.",
    hashtags: "#vape #vapeshop #margin #retailops #inventory"
  },
  {
    hook: "One vape shelf move can split sales",
    body: [
      "Customer fatigue kills conversion before price.",
      "Rotation order changes basket size.",
      "Most teams blame product, not structure."
    ],
    ending: "Miss this and repeat loss starts again.",
    hashtags: "#vape #customerbehavior #retail #vapebusiness #ops"
  },
  {
    hook: "Same vape SKU, opposite outcome",
    body: [
      "Supplier terms can look equal but risk is not.",
      "Lead-time mismatch quietly hurts cashflow.",
      "Sticker price alone is a trap."
    ],
    ending: "Not a simple cost story.",
    hashtags: "#vape #supplychain #cashflow #storeops #risk"
  }
];

const t = variants[Math.floor(Math.random() * variants.length)];
const caption = [t.hook, "", ...t.body, "", t.ending, "", t.hashtags].join("\n");

return {
  json: {
    simulation_mode: true,
    niche: "vape",
    test_id: id,
    topic: "controlled_seed",
    hook: t.hook,
    body: t.body.join(" "),
    hashtags: t.hashtags,
    caption,
    video_url: "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
    chat_id: "7592247598",
    dm_response_library: {
      general_user: ["Surface info only.", "No criteria means repeat mistakes."],
      curious_user: ["The hidden rule is in structure.", "Full answer stays gated."],
      business_owner: ["This is an operating structure issue.", "Margin rotation risk must be read together."],
      skeptical_user: ["Skepticism is fair, test the criteria first."],
      extractor_user: ["Cannot expose the full stack in open DM."],
      follow_up_question: ["Personal use or store operation?"]
    },
    dm_routing_hints: {
      business_owner_keywords: ["shop", "store", "margin", "inventory", "rotation", "risk"],
      low_value_patterns: ["just info", "summary only"],
      boundary_rule: "never_fully_reveal_core"
    },
    reply_markup: JSON.stringify({
      inline_keyboard: [
        [{ text: "Approve", callback_data: "approve_test|" + id }],
        [{ text: "Delete", callback_data: "delete_test|" + id }]
      ]
    })
  }
};
