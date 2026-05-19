from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


SNS_ROOT = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning"
)
TAC_ROOT = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\05_true atonomous_controller"
)

REPORT = SNS_ROOT / "reports" / "yuna_growth_brain_live_application_20260519.md"
SNS_LOG = SNS_ROOT / "telemetry" / "DAILY_EXECUTION_LOG.md"
TAC_LOG = TAC_ROOT / "execution_logs" / "DAILY_EXECUTION_LOG.md"
TAC_PATCH = TAC_ROOT / "agent_memory" / "PATCH_HISTORY.md"


def append_once(path: Path, marker: str, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in existing:
        path.write_text(existing.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()

    report_text = f"""# YUNA Growth Brain Live Application - 2026-05-19

## Status

`DEPLOYED_TO_LIVE_CLEAN_01_WITH_EXECUTION_OBSERVATION_PENDING`

## What Was Applied

- `clean_01_generator` live workflow `Build Simulation Content` node now uses `yuna_deal_index_v6_growth_brain`.
- Added `growth_brain_version` to candidate output.
- Added HQ agent roles including 15-year SNS strategy and behavioral psychology.
- Added primary metrics: follows per reach, comments per reach, DM replies per reach, save rate, share rate, profile visits, average watch time.
- Added per-corner experiment ids, behavioral triggers, follow reasons, save reasons, comment CTAs, hypotheses, and keep/kill decision rules.
- Added a visible `YUNA Brain` section to Telegram approval text.
- Updated validation so future candidate generation fails if these growth fields disappear.

## Live Deployment Evidence

- Workflow: `clean_01_generator`
- Workflow ID: `KPa5tncCc87z2ZsE`
- Target node: `Build Simulation Content`
- Active after deploy: `true`
- Active version after deploy: `9681289c-8ed9-4369-b474-8d83ba64a8e4`
- Code SHA after deploy: `7b39c1369f1ed943b26160f5094e6922505f1353a44a097762b9fd4847f85aad`
- Backup: `backups/clean_01_generator_pre_consumer_live_20260519_193253.json`
- Deploy report: `reports/deployments/clean01_consumer_live_deploy_20260519_193253.md`

## Trigger / Run Observation

- Preview webhook trigger returned HTTP 200 with `Workflow was started`.
- Trigger report: `reports/runs/clean01_today_preview_trigger_20260519_193332.json`
- Execution monitor still showed latest saved run as `11145`, started at `2026-05-19T05:41:30.423Z`.
- Therefore the live workflow code is applied, but a fresh saved execution using the new brain has not yet been proven from the execution list.

## Validation

- `node --check templates/clean01_consumer_growth_engine_v4.js`: PASS
- `node tools/validate_clean01_consumer_v4_deployment_draft.js`: PASS
- n8n active workflow inspection confirmed the new growth brain markers in the live active node.
- n8n static workflow validation still reports existing workflow-level expression/static warnings outside this patch surface.

## Safety

- No Instagram post was published by this patch.
- No manual comment or DM test was sent.
- No credential value was printed.
- Approval gate remains in place.

## Next Confirmation

Check the next generated Telegram approval batch. It should contain a `YUNA Brain` block with growth experiment, behavioral trigger, follow reason, save reason, comment CTA, and decision rule.

Recorded at: `{now}`
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report_text, encoding="utf-8")

    sns_marker = "YUNA_GROWTH_BRAIN_LIVE_DEPLOY_20260519"
    sns_entry = f"""## {sns_marker}

- status: deployed_to_live_clean_01_with_execution_observation_pending
- workflow: clean_01_generator
- active_version_id: 9681289c-8ed9-4369-b474-8d83ba64a8e4
- code_sha256_after: 7b39c1369f1ed943b26160f5094e6922505f1353a44a097762b9fd4847f85aad
- local_validation: PASS
- deploy: PASS
- webhook_trigger: HTTP 200 / Workflow was started
- saved_execution_observation: pending; latest observed execution remained 11145
- live_publish_performed: false
- credentials_printed: false
"""
    append_once(SNS_LOG, sns_marker, sns_entry)

    tac_marker = "YUNA_GROWTH_BRAIN_EXTERNAL_SNS_APPLY_20260519"
    tac_entry = f"""## {tac_marker}

- External SNS planning workspace patched and live `clean_01_generator` Build Simulation Content node deployed.
- Added YUNA growth brain candidate metadata, Telegram approval summary block, and validator assertions.
- Validation passed locally and deployment script reported PASS.
- Preview webhook returned HTTP 200, but n8n saved execution list did not yet show a fresh run after deploy.
- No Instagram publish, comment, DM, credential print, or production Docker restart was performed.
"""
    append_once(TAC_LOG, tac_marker, tac_entry)
    append_once(TAC_PATCH, tac_marker, tac_entry)

    print(
        {
            "status": "PASS",
            "report": str(REPORT),
            "sns_log": str(SNS_LOG),
            "tac_log": str(TAC_LOG),
            "tac_patch_history": str(TAC_PATCH),
        }
    )


if __name__ == "__main__":
    main()
