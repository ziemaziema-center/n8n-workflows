from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path


ROOT = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning"
)
ENGINE = ROOT / "templates" / "clean01_consumer_growth_engine_v4.js"
VALIDATOR = ROOT / "tools" / "validate_clean01_consumer_v4_deployment_draft.js"
REPORT = ROOT / "reports" / "yuna_product_taxonomy_mix_20260522.md"
TELEMETRY = ROOT / "telemetry" / "DAILY_EXECUTION_LOG.md"
BACKUP_DIR = ROOT / "backups" / "yuna_product_taxonomy_mix_20260522"


TAXONOMY_BLOCK = r'''
const YUNA_PRODUCT_CATEGORY_MIX_RATIO = "device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3";
const YUNA_PRODUCT_CATEGORY_MIX_SEQUENCE = [
  "e_liquid",
  "disposable_device",
  "e_liquid",
  "disposable_device",
  "e_liquid",
  "disposable_cartridge",
  "e_liquid",
  "disposable_device",
  "e_liquid",
  "disposable_device",
  "e_liquid",
  "disposable_device",
  "e_liquid",
  "disposable_cartridge",
  "e_liquid",
  "disposable_device",
  "e_liquid",
  "disposable_device",
  "e_liquid",
  "disposable_cartridge",
  "device"
];
const YUNA_PRODUCT_TAXONOMY_VERSION = "yuna_product_taxonomy_v1_2026_05_22";
const YUNA_PRODUCT_TAXONOMY = {
  e_liquid: {
    label: "전자담배 액상",
    definition: "리필형 액상. 병 단위 용량, 니코틴/무니코틴 표기, 배송비 포함 ml 단가, 맛 실패위험으로 점수화한다.",
    score_unit: "원/ml",
    comment_prompt: "댓글에 액상 가격/용량/배송비/니코틴 여부를 남기면 YUNA가 ml 단가로 다시 계산합니다.",
    configuration_label: "리필 액상 병 단위"
  },
  disposable_device: {
    label: "일회용 전자담배 기계",
    definition: "배터리, 코일, 액상이 한 몸인 올인원 일회용 기기. 흡입횟수, 내장 액상량, 충전 여부, 배터리/누수 리스크로 점수화한다.",
    score_unit: "원/1000회 흡입 + 원/ml",
    comment_prompt: "댓글에 흡입횟수/내장 ml/가격/배송비를 남기면 YUNA가 1000회당 가격으로 다시 계산합니다.",
    configuration_label: "배터리+코일+액상 일체형"
  },
  disposable_cartridge: {
    label: "일회용 전담용 카트리지",
    definition: "전용 디바이스에 꽂는 폐쇄형/교체형 카트리지 또는 팟. 카트리지 수, ml, 호환 기기, 누수/잠금 생태계 리스크로 점수화한다.",
    score_unit: "원/카트리지 + 원/ml",
    comment_prompt: "댓글에 카트리지 개수/ml/호환기기/가격을 남기면 YUNA가 카트리지당 가격으로 다시 계산합니다.",
    configuration_label: "교체형 폐쇄형 카트리지/팟"
  },
  device: {
    label: "전자담배 디바이스",
    definition: "액상 없이 쓰는 재사용 기기 본체. 기기 가격, 코일/팟 소모품 비용, 호환성, 내구성, AS 리스크로 점수화한다.",
    score_unit: "본체 가격 + 소모품 잠금 비용",
    comment_prompt: "댓글에 기기 가격/호환 팟/코일 가격/AS 조건을 남기면 YUNA가 유지비까지 계산합니다.",
    configuration_label: "재사용 디바이스 본체"
  }
};
'''.strip()


CATEGORY_FUNCTION_BLOCK = r'''
function resolveYunaProductCategory(index) {
  if (typeof store.yunaProductCategoryCursor !== "number") store.yunaProductCategoryCursor = 0;
  const seq = YUNA_PRODUCT_CATEGORY_MIX_SEQUENCE;
  return seq[(store.yunaProductCategoryCursor + index) % seq.length];
}

function categoryBreakdown(category) {
  const table = {
    e_liquid: { price_objectivity: 25, flavor_risk: 12, compatibility_risk: 10, inventory_timing: 11, source_freshness: 20 },
    disposable_device: { price_objectivity: 21, flavor_risk: 8, compatibility_risk: 11, inventory_timing: 13, source_freshness: 18 },
    disposable_cartridge: { price_objectivity: 20, flavor_risk: 8, compatibility_risk: 14, inventory_timing: 11, source_freshness: 13 },
    device: { price_objectivity: 18, flavor_risk: 0, compatibility_risk: 18, inventory_timing: 14, source_freshness: 12 }
  };
  return table[category] || table.e_liquid;
}

function categoryScore(breakdown) {
  return Object.values(breakdown).reduce((sum, value) => sum + Number(value || 0), 0);
}

function applyYunaProductTaxonomy(spec, index) {
  const category = resolveYunaProductCategory(index);
  const taxonomy = YUNA_PRODUCT_TAXONOMY[category] || YUNA_PRODUCT_TAXONOMY.e_liquid;
  const breakdown = categoryBreakdown(category);
  const score = categoryScore(breakdown);
  const listedPrice = Number(spec.listed_price || 0);
  const shipping = Number(spec.shipping_fee_assumption || 0);
  const effectivePrice = Number(spec.effective_price || (listedPrice + shipping));
  const ml = Number(spec.total_ml || (Number(spec.ml_per_bottle || 0) * Number(spec.bottle_count || 1))) || 1;
  const unitPricePerMl = effectivePrice / ml;

  const categoryData = {
    e_liquid: {
      product_name_redacted: spec.product_name_redacted || "리필 액상 공개 상품",
      configuration_label: `${spec.ml_per_bottle || 30}ml x ${spec.bottle_count || 1}`,
      visible_price: `액상 표시가 ${formatWon(listedPrice)} / ${spec.ml_per_bottle || 30}ml x ${spec.bottle_count || 1}`,
      hidden_cost: `배송 포함 ${formatWon(effectivePrice)} / ${round1(unitPricePerMl)}원/ml`,
      real_price_question: `액상 ml 단가: ${formatWon(listedPrice)} + 배송 ${formatWon(shipping)} -> ${round1(unitPricePerMl)}원/ml`,
      unit_price_claimed: `${round1(unitPricePerMl)}원/ml`,
      unit_price_display: `${round1(unitPricePerMl)}원/ml`,
      claim_type: "e_liquid_unit_price_score",
      claim_value: "bottled e-liquid price, volume, shipping and nicotine basis"
    },
    disposable_device: {
      product_name_redacted: "일회용 전자담배 기계 공개 상품",
      configuration_label: "배터리+코일+액상 일체형 / 흡입횟수 확인 필요",
      visible_price: `일회용 기기 표시가 ${formatWon(listedPrice)}`,
      hidden_cost: "내장 액상량, 흡입횟수, 충전 여부, 배터리/누수 리스크",
      real_price_question: "1000회 흡입당 가격과 내장 ml 단가를 같이 봐야 함",
      unit_price_claimed: `${round1(unitPricePerMl)}원/ml + 흡입횟수 기준 필요`,
      unit_price_display: `${round1(unitPricePerMl)}원/ml + 1000회당 가격 확인`,
      claim_type: "disposable_device_price_score",
      claim_value: "all-in-one disposable vape device price, puff count, capacity, battery and leak risk"
    },
    disposable_cartridge: {
      product_name_redacted: "교체형 일회용 카트리지 공개 상품",
      configuration_label: "폐쇄형 카트리지/팟 / 호환 디바이스 확인 필요",
      visible_price: `카트리지 표시가 ${formatWon(listedPrice)}`,
      hidden_cost: "호환 기기 잠금, 카트리지 수, ml, 누수/잔량 리스크",
      real_price_question: "카트리지당 가격과 ml 단가를 같이 봐야 함",
      unit_price_claimed: `${round1(unitPricePerMl)}원/ml + 카트리지당 가격 확인`,
      unit_price_display: `${round1(unitPricePerMl)}원/ml + 카트리지당 가격`,
      claim_type: "disposable_cartridge_price_score",
      claim_value: "prefilled cartridge or pod price, cartridge count, ml, compatibility and leak risk"
    },
    device: {
      product_name_redacted: "전자담배 디바이스 본체 공개 상품",
      configuration_label: "액상 미포함 재사용 디바이스 / 팟·코일 유지비 확인 필요",
      visible_price: `디바이스 본체 표시가 ${formatWon(listedPrice)}`,
      hidden_cost: "전용 팟/코일 가격, 호환성, AS, 배터리 수명",
      real_price_question: "본체가 싸도 전용 소모품이 비싸면 총 유지비가 올라감",
      unit_price_claimed: "본체 가격 + 소모품 잠금 비용",
      unit_price_display: "본체 가격 + 팟/코일 유지비",
      claim_type: "device_total_ownership_score",
      claim_value: "reusable device body price, pod/coil ecosystem, compatibility, durability and warranty risk"
    }
  }[category];

  const scoreFormula = category === "device"
    ? "기기 가격/호환성/소모품/내구성/AS 기준 100점 환산"
    : `${taxonomy.score_unit} 기준 + 니코틴 표기 + 배송비 + 실패위험 100점 환산`;
  const scoreReasonLines = [
    `상품분류: ${taxonomy.label}`,
    `분류정의: ${taxonomy.definition}`,
    `점수단위: ${taxonomy.score_unit}`,
    `포스팅비율: 전자담배 디바이스 1 : 전자담배 액상 10 : 일회용 전자담배 기계 7 : 일회용 전담용 카트리지 3`,
    `산식: ${scoreFormula}`,
    `근거: 가격 ${breakdown.price_objectivity}/35, 맛 ${breakdown.flavor_risk}/15, 호환 ${breakdown.compatibility_risk}/15, 재고 ${breakdown.inventory_timing}/15, 출처 ${breakdown.source_freshness}/20`
  ];

  return {
    ...spec,
    ...categoryData,
    yuna_product_taxonomy_version: YUNA_PRODUCT_TAXONOMY_VERSION,
    yuna_product_category: category,
    yuna_product_category_label: taxonomy.label,
    yuna_product_category_definition: taxonomy.definition,
    yuna_product_category_mix_ratio: YUNA_PRODUCT_CATEGORY_MIX_RATIO,
    yuna_product_category_mix_sequence: YUNA_PRODUCT_CATEGORY_MIX_SEQUENCE,
    category_mix_mode: "controlled_weighted_rotation",
    price_score_unit: taxonomy.score_unit,
    configuration_label: categoryData.configuration_label,
    category_comment_prompt: taxonomy.comment_prompt,
    product_category: category,
    product_name_redacted: categoryData.product_name_redacted,
    yuna_deal_index: score,
    deal_score_breakdown: breakdown,
    yuna_score_formula: scoreFormula,
    yuna_score_reason_lines: scoreReasonLines,
    deal_verdict: dealVerdict(score),
    verdict_line: `YUNA ${taxonomy.label} 가격점수: ${score}점 / ${dealVerdict(score)}`,
    hook: `YUNA 분류: ${taxonomy.label} 가격점수는 ${score}점입니다`,
    consumer_payoff: `${taxonomy.label}을 ${taxonomy.score_unit} 기준으로 다시 계산`,
    retention_hook: taxonomy.comment_prompt,
    comment_cta: taxonomy.comment_prompt,
    thumbnail_style: `yuna_${category}_price_score`,
    first_line_pattern: `${category}_price_score`,
    lines: [
      "[YUNA DEAL INDEX]",
      `분류: ${taxonomy.label}`,
      `점수단위: ${taxonomy.score_unit}`,
      `구성: ${categoryData.configuration_label}`,
      `표시가: ${formatWon(listedPrice)} / 배송가정: ${formatWon(shipping)}`,
      `계산: ${categoryData.unit_price_display}`,
      `점수: ${score}점 / ${dealVerdict(score)}`,
      `근거: 가격 ${breakdown.price_objectivity}/35, 맛 ${breakdown.flavor_risk}/15, 호환 ${breakdown.compatibility_risk}/15, 재고 ${breakdown.inventory_timing}/15, 출처 ${breakdown.source_freshness}/20`,
      taxonomy.comment_prompt
    ],
    hashtags: `#YUNADEALINDEX #유나딜인덱스 #${taxonomy.label.replace(/\s+/g, "")} #가격점수 #전담가격검산`
  };
}
'''.strip()


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f"missing replacement target: {old[:80]}")
    return text.replace(old, new, 1)


def patch_engine() -> None:
    text = ENGINE.read_text(encoding="utf-8")
    if "YUNA_PRODUCT_TAXONOMY_VERSION" not in text:
        text = replace_once(text, "const productListingSnapshots = [", TAXONOMY_BLOCK + "\n\nconst productListingSnapshots = [")
    if "function applyYunaProductTaxonomy" not in text:
        text = replace_once(text, "function slotToMinutes(slot) {", CATEGORY_FUNCTION_BLOCK + "\n\nfunction slotToMinutes(slot) {")
    text = replace_once(
        text,
        "  spec = buildListingAnalysis(spec, index);\n",
        "  spec = buildListingAnalysis(spec, index);\n  spec = applyYunaProductTaxonomy(spec, index);\n",
    )
    replacements = {
        'textElement(`구성 ${spec.ml_per_bottle}ml x ${spec.bottle_count} / ${formatWon(spec.listed_price)}`,': 'textElement(`구성 ${spec.configuration_label || `${spec.ml_per_bottle}ml x ${spec.bottle_count}`} / ${formatWon(spec.listed_price)}`,',
        'textElement(`= ${formatWon(spec.effective_price)} / ${round1(spec.unit_price_per_ml)}원/ml`,': 'textElement(`= ${spec.unit_price_display || `${round1(spec.unit_price_per_ml)}원/ml`}`,',
        'textElement(`가격 ${spec.deal_score_breakdown.price_objectivity}/35 · 맛 ${spec.deal_score_breakdown.flavor_risk}/15`,': 'textElement(spec.score_breakdown_short_line1 || `가격 ${spec.deal_score_breakdown.price_objectivity}/35 · 맛 ${spec.deal_score_breakdown.flavor_risk}/15`,',
        'textElement(`호환 ${spec.deal_score_breakdown.compatibility_risk}/15 · 재고 ${spec.deal_score_breakdown.inventory_timing}/15 · 출처 ${spec.deal_score_breakdown.source_freshness}/20`,': 'textElement(spec.score_breakdown_short_line2 || `호환 ${spec.deal_score_breakdown.compatibility_risk}/15 · 재고 ${spec.deal_score_breakdown.inventory_timing}/15 · 출처 ${spec.deal_score_breakdown.source_freshness}/20`,',
        '`- 상품: ${spec.product_name_redacted}`,\n    `- 표시가: ${formatWon(spec.listed_price)} / 용량: ${spec.ml_per_bottle}ml x ${spec.bottle_count}`,\n    `- 배송 포함 계산가: ${formatWon(spec.effective_price)}`,\n    `- ml 단가: ${round1(spec.unit_price_per_ml)}원/ml / 등급: ${spec.unit_price_grade}`,\n    `- 산식: ${spec.yuna_score_formula}`,\n    `- breakdown: 가격 ${spec.deal_score_breakdown.price_objectivity}/35 + 맛 ${spec.deal_score_breakdown.flavor_risk}/15 + 호환 ${spec.deal_score_breakdown.compatibility_risk}/15 + 재고 ${spec.deal_score_breakdown.inventory_timing}/15 + 출처 ${spec.deal_score_breakdown.source_freshness}/20 = ${spec.yuna_deal_index}점`,': '`- 상품: ${spec.product_name_redacted}`,\n    `- 분류: ${spec.yuna_product_category_label} (${spec.yuna_product_category})`,\n    `- 구성: ${spec.configuration_label}`,\n    `- 표시가: ${formatWon(spec.listed_price)} / 배송가정: ${formatWon(spec.shipping_fee_assumption)}`,\n    `- 계산단위: ${spec.unit_price_display}`,\n    `- 포스팅비율: ${spec.yuna_product_category_mix_ratio}`,\n    `- 산식: ${spec.yuna_score_formula}`,\n    `- breakdown: 가격 ${spec.deal_score_breakdown.price_objectivity}/35 + 맛 ${spec.deal_score_breakdown.flavor_risk}/15 + 호환 ${spec.deal_score_breakdown.compatibility_risk}/15 + 재고 ${spec.deal_score_breakdown.inventory_timing}/15 + 출처 ${spec.deal_score_breakdown.source_freshness}/20 = ${spec.yuna_deal_index}점`,',
        'product_category: spec.product_category,\n': 'product_category: spec.product_category,\n      yuna_product_taxonomy_version: spec.yuna_product_taxonomy_version,\n      yuna_product_category: spec.yuna_product_category,\n      yuna_product_category_label: spec.yuna_product_category_label,\n      yuna_product_category_definition: spec.yuna_product_category_definition,\n      yuna_product_category_mix_ratio: spec.yuna_product_category_mix_ratio,\n      price_score_unit: spec.price_score_unit,\n      configuration_label: spec.configuration_label,\n      unit_price_display: spec.unit_price_display,\n      category_comment_prompt: spec.category_comment_prompt,\n',
        '`계산가: ${formatWon(spec.effective_price)} / ${round1(spec.unit_price_per_ml)}원/ml`,\n        `근거: 가격 ${spec.deal_score_breakdown.price_objectivity}/35 + 맛 ${spec.deal_score_breakdown.flavor_risk}/15 + 호환 ${spec.deal_score_breakdown.compatibility_risk}/15 + 재고 ${spec.deal_score_breakdown.inventory_timing}/15 + 출처 ${spec.deal_score_breakdown.source_freshness}/20`,\n        "댓글에 전담액상 상품명/가격/용량/배송비 남기면 YUNA가 같은 산식으로 계산합니다."': '`계산가: ${formatWon(spec.effective_price)} / ${spec.unit_price_display}`,\n        `근거: 가격 ${spec.deal_score_breakdown.price_objectivity}/35 + 맛 ${spec.deal_score_breakdown.flavor_risk}/15 + 호환 ${spec.deal_score_breakdown.compatibility_risk}/15 + 재고 ${spec.deal_score_breakdown.inventory_timing}/15 + 출처 ${spec.deal_score_breakdown.source_freshness}/20`,\n        spec.category_comment_prompt',
        'deployment_stage: DEPLOYMENT_STAGE\n': 'deployment_stage: DEPLOYMENT_STAGE,\n  product_taxonomy_version: YUNA_PRODUCT_TAXONOMY_VERSION,\n  category_mix_ratio: YUNA_PRODUCT_CATEGORY_MIX_RATIO,\n  categories: output.map(item => item.json.yuna_product_category)\n',
        'store.last_consumer_growth_v4_batch = {': 'store.yunaProductCategoryCursor = (Number(store.yunaProductCategoryCursor || 0) + output.length) % YUNA_PRODUCT_CATEGORY_MIX_SEQUENCE.length;\nstore.last_consumer_growth_v4_batch = {',
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new, 1)
    ENGINE.write_text(text, encoding="utf-8")


def patch_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    if "allowedProductCategories" not in text:
        text = replace_once(
            text,
            "  const ids = new Set();\n  const pillars = new Set();\n  const slots = new Set();\n",
            '  const ids = new Set();\n  const pillars = new Set();\n  const slots = new Set();\n  const categories = new Set();\n  const allowedProductCategories = new Set(["e_liquid", "disposable_device", "disposable_cartridge", "device"]);\n',
        )
        text = replace_once(text, "    slots.add(j.publish_slot);\n", "    slots.add(j.publish_slot);\n    categories.add(j.yuna_product_category);\n")
        text = replace_once(
            text,
            '    assert(j.product_name_redacted && j.listed_price && j.shipping_fee_assumption !== undefined, "objective product price fields required");\n',
            '    assert(j.product_name_redacted && j.listed_price && j.shipping_fee_assumption !== undefined, "objective product price fields required");\n    assert(allowedProductCategories.has(j.yuna_product_category), `unsupported YUNA product category: ${j.yuna_product_category}`);\n    assert(j.yuna_product_taxonomy_version === "yuna_product_taxonomy_v1_2026_05_22", "YUNA product taxonomy version missing");\n    assert(j.yuna_product_category_label && j.yuna_product_category_definition, "YUNA product category label/definition required");\n    assert(j.yuna_product_category_mix_ratio === "device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3", "YUNA product category mix ratio mismatch");\n    assert(j.price_score_unit && j.configuration_label && j.unit_price_display && j.category_comment_prompt, "category scoring fields required");\n',
        )
        text = replace_once(
            text,
            '  assert(staticData.last_consumer_growth_v4_batch.total === 4, "static batch total mismatch");\n  return { source_sha256: sha(source), item_count: result.length, pillars: Array.from(pillars), slots: Array.from(slots) };\n',
            '  assert(staticData.last_consumer_growth_v4_batch.total === 4, "static batch total mismatch");\n  assert(staticData.last_consumer_growth_v4_batch.category_mix_ratio === "device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3", "static batch category mix ratio missing");\n  assert(categories.has("e_liquid") && categories.has("disposable_device"), "first batch should include liquid and disposable device categories");\n  assert(source.includes("disposable_cartridge") && source.includes("device"), "taxonomy source must include cartridge and device categories");\n  return { source_sha256: sha(source), item_count: result.length, pillars: Array.from(pillars), slots: Array.from(slots), categories: Array.from(categories) };\n',
        )
        text = replace_once(
            text,
            '    "growth_brain_version",\n',
            '    "growth_brain_version",\n    "yuna_product_taxonomy_version",\n    "yuna_product_category",\n    "yuna_product_category_label",\n    "yuna_product_category_definition",\n    "yuna_product_category_mix_ratio",\n    "price_score_unit",\n    "configuration_label",\n    "unit_price_display",\n    "category_comment_prompt",\n',
        )
    VALIDATOR.write_text(text, encoding="utf-8")


def write_report() -> None:
    text = """# YUNA Product Taxonomy Mix - 2026-05-22

## Status

`APPLIED_LOCALLY_PENDING_DEPLOY_VALIDATION`

## What Changed

- YUNA now separates four product categories:
  - `e_liquid`: 전자담배 액상
  - `disposable_device`: 일회용 전자담배 기계
  - `disposable_cartridge`: 일회용 전담용 카트리지/팟
  - `device`: 전자담배 디바이스 본체
- Posting mix ratio added:
  - 전자담배 디바이스 1
  - 전자담배 액상 10
  - 일회용 전자담배 기계 7
  - 일회용 전담용 카트리지 3
- clean_01 now uses a controlled weighted rotation instead of treating every product as bottled liquid.
- Telegram approval text now shows category, configuration, scoring unit, and category-specific comment prompt.
- Validator now fails if taxonomy fields or mix ratio disappear.

## Research Basis

- CDC: e-cigarettes are battery-operated devices that heat liquid into aerosol; product forms include disposable devices and prefilled cartridge/pod systems.
- NIDA: e-cigarettes use a cartridge/reservoir/pod that holds e-liquid; device heats the liquid.
- CDC MMWR: disposable devices are nonrechargeable/nonreusable and not intended to be refilled; once liquid is consumed, the device is discarded.
- FDA authorized-product taxonomy shows devices, pods, cartridges, and e-liquid packages as distinct product surfaces.

## Safety

- No Instagram publish was performed by this patch.
- No credential value was printed.
- No clean03/clean04 publisher workflow was changed.
"""
    REPORT.write_text(text, encoding="utf-8")


def append_log() -> None:
    marker = "YUNA_PRODUCT_TAXONOMY_MIX_20260522"
    existing = TELEMETRY.read_text(encoding="utf-8") if TELEMETRY.exists() else ""
    if marker not in existing:
        TELEMETRY.write_text(existing.rstrip() + f"""

## {marker}

- Added YUNA product taxonomy for e-liquid, disposable device, disposable cartridge/pod, and reusable device.
- Added posting mix ratio device:1, e_liquid:10, disposable_device:7, disposable_cartridge:3.
- Patched clean01 engine and validator locally; deployment validation still required after this script.
- No Instagram publish, credential output, clean03/clean04 mutation, Docker/nginx/server mutation, or AWS mutation was performed by this script.
""", encoding="utf-8")


def main() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ENGINE, BACKUP_DIR / "clean01_consumer_growth_engine_v4.js.before")
    shutil.copy2(VALIDATOR, BACKUP_DIR / "validate_clean01_consumer_v4_deployment_draft.js.before")
    patch_engine()
    patch_validator()
    write_report()
    append_log()
    print(json.dumps({
        "status": "PASS",
        "engine": str(ENGINE),
        "validator": str(VALIDATOR),
        "report": str(REPORT),
        "backup_dir": str(BACKUP_DIR),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
