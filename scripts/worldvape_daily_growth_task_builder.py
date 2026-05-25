from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def build_task(*, date: str, workspace: str) -> dict[str, object]:
    task_id = f"worldvape-daily-growth-{date.replace('-', '')}"
    objective = (
        "Company HQ daily growth routine for Worldvape Gwangwoon Instagram and SNS. "
        "Run the safe local/offline daily cycle: review prior metrics if available, scan stored competitor notes, "
        "generate four YUNA approval candidates, rank them by follow/customer intent, write a Korean operator report, "
        "record learning notes, and prepare the next approval summary. Do not access credential values, do not publish, "
        "do not activate production workflows, do not restart services, and do not copy competitor creative assets."
    )
    return {
        "task_id": task_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requested_by": "tac_daily_growth_routine",
        "source_channel": "scheduled_draft",
        "owner": "Worldvape Growth HQ",
        "department": "growth",
        "priority": "high",
        "objective": objective,
        "allowed_scope": [
            "local_files",
            "offline_tests",
            "docs",
            "templates",
            "scaffold",
            "dry_run",
            "no_live_network",
            "no_secrets",
            "no_production_mutation",
        ],
        "deferred_gates": [
            {
                "name": "live_instagram_publish",
                "reason": "Publishing requires the existing Telegram approval flow.",
                "required_approval": "Operator approves the selected candidate before posting.",
            },
            {
                "name": "credentialed_metric_fetch",
                "reason": "Instagram metrics require approved credentialed read-only access.",
                "required_approval": "Approved read-only metrics route with no credential value output.",
            },
            {
                "name": "n8n_workflow_activation",
                "reason": "The daily n8n routine is draft-only until import review passes.",
                "required_approval": "Explicit n8n activation approval.",
            },
        ],
        "target_runner": "codex",
        "tmux_session": "tac-hq-runner",
        "workspace_path": workspace,
        "validation_commands": [
            "python -m unittest discover -s tests",
            "python scripts/run_offline_validations.py",
        ],
        "expected_artifacts": [
            "reports/worldvape_daily_growth_report.md",
            "runtime/worldvape_growth/daily_growth_memory.jsonl",
            "Telegram approval summary draft",
        ],
        "status": "QUEUED",
        "retry_count": 0,
        "max_retries": 1,
        "continuation_ledger_path": "reports/hq_continuation_ledger_2026-05-18.json",
        "final_report_path": "reports/worldvape_gwangwoon_daily_growth_ops_2026-05-25.md",
        "notification": {"on_completion": True, "channel": "telegram"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a TAC queue task for the Worldvape daily growth routine.")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--workspace", default="/home/ubuntu/workspace/sns_automation_safe")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    task = build_task(date=args.date, workspace=args.workspace)
    text = json.dumps(task, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
