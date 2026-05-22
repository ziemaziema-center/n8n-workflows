from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


SNS_ROOT = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning"
)
TAC_ROOT = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\05_true atonomous_controller"
)

REPORT = SNS_ROOT / "reports" / "yuna_product_taxonomy_mix_20260522.md"
SNS_LOG = SNS_ROOT / "telemetry" / "DAILY_EXECUTION_LOG.md"
TAC_LOG = TAC_ROOT / "execution_logs" / "DAILY_EXECUTION_LOG.md"
TAC_PATCH = TAC_ROOT / "agent_memory" / "PATCH_HISTORY.md"


def append_once(path: Path, marker: str, text: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in existing:
        path.write_text(existing.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    marker = "YUNA_PRODUCT_TAXONOMY_MIX_LIVE_20260522"
    report = f"""# YUNA Product Taxonomy Mix - 2026-05-22

## Status

`LIVE_DEPLOYED_WITH_EXECUTION_OBSERVATION_PENDING`

## Applied Product Knowledge

YUNA now separates product scoring into four categories:

- `e_liquid`: 전자담배 액상
- `disposable_device`: 일회용 전자담배 기계
- `disposable_cartridge`: 일회용 전담용 카트리지/팟
- `device`: 전자담배 디바이스 본체

Posting mix:

- 전자담배 디바이스: 1
- 전자담배 액상: 10
- 일회용 전자담배 기계: 7
- 일회용 전담용 카트리지: 3

Implementation detail:

- Mix mode: `controlled_weighted_rotation`
- Ratio marker: `device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3`
- Taxonomy marker: `yuna_product_taxonomy_v1_2026_05_22`

## Category Scoring Logic

- 전자담배 액상: 병 용량, 니코틴/무니코틴 표기, 배송 포함 ml 단가, 맛 실패위험.
- 일회용 전자담배 기계: 배터리+코일+액상 일체형 여부, 흡입횟수, 내장 ml, 충전 여부, 배터리/누수 리스크.
- 일회용 전담용 카트리지: 폐쇄형/교체형 팟, 카트리지 수, ml, 호환 디바이스, 누수/잠금 생태계 리스크.
- 전자담배 디바이스: 본체 가격, 팟/코일 소모품 유지비, 호환성, 내구성, AS 리스크.

## Research Basis

- CDC: e-cigarettes are battery-powered devices that heat liquid into aerosol; market types include disposables and prefilled cartridge/pod systems.
- NIDA: e-cigarettes use cartridges, reservoirs, or pods that hold e-liquid.
- CDC MMWR: disposable e-cigarettes are nonrechargeable/nonreusable and discarded after the e-liquid is depleted.
- FDA authorized product taxonomy distinguishes devices, pods, cartridges, and e-liquid packages.

Sources:
- https://www.cdc.gov/tobacco/e-cigarettes/about.html
- https://nida.nih.gov/publications/drugfacts/vaping-devices-electronic-cigarettes
- https://www.cdc.gov/mmwr/volumes/69/wr/mm6937e2.htm
- https://www.fda.gov/tobacco-products/market-and-distribute-tobacco-product/e-cigarettes-vapes-and-other-electronic-nicotine-delivery-systems-ends-authorized-fda

## Validation

- `node --check templates/clean01_consumer_growth_engine_v4.js`: PASS
- `node tools/validate_clean01_consumer_v4_deployment_draft.js`: PASS
- n8n live deploy: PASS
- active workflow version: `7ddbeac2-ca84-4e50-8aa3-679fe5fdfc43`
- live code sha: `e11817d1ed039271e4d1dcf1821d7cfc87b876c3c8cbce3faaaf20e6c315172f`

## Live Observation

- Webhook trigger returned HTTP 200 / `Workflow was started`.
- After 60 seconds, n8n execution list still showed latest saved run as `12398`, started before this deploy.
- Therefore live code is deployed, but a fresh saved execution using this taxonomy mix has not yet been observed.

## Safety

- No Instagram publish was performed.
- No clean03/clean04 publisher workflow was changed.
- No credential value was printed.
- No Docker/nginx/server/AWS mutation was performed.

Recorded at: `{now}`
"""
    REPORT.write_text(report, encoding="utf-8")

    log = f"""## {marker}

- Applied and live-deployed YUNA product taxonomy mix to `clean_01_generator` Build Simulation Content.
- Categories: e-liquid, disposable device, disposable cartridge/pod, reusable device.
- Ratio: device 1 / e-liquid 10 / disposable device 7 / disposable cartridge 3.
- Local JS syntax and deployment validator passed.
- Live n8n active version confirmed: `7ddbeac2-ca84-4e50-8aa3-679fe5fdfc43`.
- Webhook returned HTTP 200, but saved execution list did not yet show a fresh post-deploy run.
- No Instagram publish, credential output, clean03/clean04 mutation, Docker/nginx/server mutation, or AWS mutation was performed.
"""
    append_once(SNS_LOG, marker, log)
    append_once(TAC_LOG, marker, log)
    append_once(TAC_PATCH, marker, log)
    print({"status": "PASS", "report": str(REPORT), "marker": marker})


if __name__ == "__main__":
    main()
