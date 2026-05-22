from pathlib import Path


ENGINE = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\templates\clean01_consumer_growth_engine_v4.js"
)

text = ENGINE.read_text(encoding="utf-8")
old = '''      `구성: ${categoryData.configuration_label}`,
      `표시가: ${formatWon(listedPrice)} / 배송가정: ${formatWon(shipping)}`,'''
new = '''      `구성: ${categoryData.configuration_label}`,
      `니코틴 표기: ${spec.nicotine_status_label || "확인 필요"} / ${spec.nicotine_scoring_basis_label || "무니코틴 기준"}`,
      "법 기준: 2026-04-24 이후 온라인 니코틴 액상 판매 기준 확인",
      `표시가: ${formatWon(listedPrice)} / 배송가정: ${formatWon(shipping)}`,'''
if old not in text:
    raise SystemExit("target nicotine caption insertion point not found")
ENGINE.write_text(text.replace(old, new, 1), encoding="utf-8")
print({"status": "PASS", "engine": str(ENGINE)})
