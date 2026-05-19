from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


SNS_ROOT = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning"
)
TAC_ROOT = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\05_true atonomous_controller"
)

REPORT = SNS_ROOT / "reports" / "yuna_comment_dm_and_clean03_fix_20260519.md"
SNS_LOG = SNS_ROOT / "telemetry" / "DAILY_EXECUTION_LOG.md"
TAC_LOG = TAC_ROOT / "execution_logs" / "DAILY_EXECUTION_LOG.md"
TAC_PATCH = TAC_ROOT / "agent_memory" / "PATCH_HISTORY.md"


def append_once(path: Path, marker: str, text: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in existing:
        path.write_text(existing.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    marker = "ACTUAL05_YUNA_COMMENT_DM_ACTIVATED_20260519"
    report_block = f"""## {marker}

Status: `LIVE_ACTIVE_CONFIRMED`

- Workflow: `actual_05_instagram_comment_dm_opener`
- Workflow ID: `Afve1lyQgvUIpgsg`
- n8n active: `true`
- Active version ID: `050012f8-27c1-4a32-937f-292b122ddab5`
- Updated at: `2026-05-19T10:19:39.832Z`
- Live active graph contains marker: `yuna_deal_index_comment_score_actual05_v1`
- Public reply text: `DM 확인하세요. YUNA가 댓글 기준으로 가격 검산표 보냈습니다.`
- Private reply path: enabled through `Private Reply DM Opener`
- Public reply path: enabled through `Public Reply`
- Duplicate guard: enabled through `Dedupe Comment`
- High-value operator Telegram alert remains disabled.
- Latest saved executions listed by n8n remain old webhook test runs `7271` and `7270`; no fresh live Instagram comment event was forced in this pass.

Safety:
- No artificial Instagram comment was posted.
- No manual DM/private reply was sent.
- No credential value was printed.

Recorded at: `{now}`
"""
    append_once(REPORT, marker, report_block)

    log_entry = f"""## {marker}

- Confirmed `actual_05_instagram_comment_dm_opener` is live active in n8n.
- Confirmed active graph contains YUNA Deal Index scoring marker, public reply, private reply, and dedupe guard.
- Did not force a live Instagram comment/DM event; latest saved executions are prior webhook test runs.
- No credential value was printed.
"""
    append_once(SNS_LOG, marker, log_entry)
    append_once(TAC_LOG, marker, log_entry)
    append_once(TAC_PATCH, marker, log_entry)
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
