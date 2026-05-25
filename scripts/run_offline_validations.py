from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> dict[str, object]:
    completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def main() -> int:
    checks = [
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests"]),
        run([sys.executable, "-m", "json.tool", "reports/hq_continuation_ledger_2026-05-18.json"]),
        run([sys.executable, "-m", "json.tool", "schemas/runtime_queue.schema.json"]),
        run([sys.executable, "-m", "json.tool", "schemas/runtime_state.schema.json"]),
        run([sys.executable, "-m", "json.tool", "schemas/telegram_hq_command.schema.json"]),
        run([sys.executable, "-m", "json.tool", "schemas/reviewer_feedback.schema.json"]),
        run([sys.executable, "-m", "json.tool", "schemas/runtime_event.schema.json"]),
        run([sys.executable, "-m", "json.tool", "schemas/yuna_growth_experiment.schema.json"]),
        run([sys.executable, "-m", "json.tool", "schemas/tac_scorecard.schema.json"]),
        run([sys.executable, "-m", "json.tool", "schemas/worldvape_daily_growth_routine.schema.json"]),
        run([sys.executable, "-m", "json.tool", "runtime/queue/sample_task.json"]),
        run([sys.executable, "-m", "json.tool", "runtime/state/sample_state.json"]),
        run([sys.executable, "-m", "json.tool", "runtime/yuna_growth_experiments/sample_experiment.json"]),
        run([sys.executable, "-m", "json.tool", "runtime/worldvape_growth/sample_daily_routine.json"]),
        run([sys.executable, "-m", "json.tool", "workflows/inactive_hq_ssh_dispatch_draft_2026-05-18.json"]),
        run([sys.executable, "-m", "json.tool", "workflows/inactive_hq_runtime_orchestration_pack_2026-05-19.json"]),
        run([sys.executable, "-m", "json.tool", "workflows/inactive_worldvape_daily_growth_ops_2026-05-25.json"]),
        run(
            [
                sys.executable,
                "-m",
                "py_compile",
                "scripts/render_telegram_korean_summary.py",
                "scripts/hq_sqlite_queue_writer.py",
                "scripts/remote_live_gate_smoke.py",
                "scripts/remote_phase3_e2e_smoke.py",
                "scripts/docker_isolated_runner_plan.py",
                "scripts/hq_phase3_orchestrator.py",
                "scripts/docker_container_smoke.py",
                "scripts/queue_soak_test.py",
                "scripts/git_checkpoint_manifest.py",
                "scripts/remote_queue_route_smoke.py",
                "scripts/hq_company_task_runner.py",
                "scripts/hq_notify_completion.py",
                "scripts/docker_codex_cli_smoke.py",
                "scripts/runtime_engine_smoke.py",
                "scripts/tac_scorecard.py",
                "scripts/create_bounded_workspace_archive.py",
                "scripts/worldvape_daily_growth_task_builder.py",
                "src/tac/runtime_engine.py",
            ]
        ),
        run([sys.executable, "scripts/tac_scorecard.py"]),
        run([sys.executable, "scripts/docker_isolated_runner_plan.py"]),
        run([sys.executable, "scripts/hq_phase3_orchestrator.py"]),
        run([sys.executable, "scripts/queue_soak_test.py"]),
        run([sys.executable, "scripts/git_checkpoint_manifest.py"]),
        run([sys.executable, "scripts/render_telegram_korean_summary.py"]),
        run([sys.executable, "scripts/hq_sqlite_queue_writer.py", "--task-id", "hq-offline-validation-queue-writer-20260518"]),
        run([sys.executable, "scripts/runtime_engine_smoke.py"]),
        run([sys.executable, "scripts/worldvape_daily_growth_task_builder.py", "--date", "2026-05-25"]),
        run([sys.executable, "-m", "json.tool", "workflows/tac_telegram_commands.json"]),
        run([sys.executable, "-m", "json.tool", "workflows/tac_controller_webhook.json"]),
    ]
    report = {
        "status": "PASS" if all(check["returncode"] == 0 for check in checks) else "FAIL",
        "checks": checks,
        "live_operations_performed": False,
    }
    out = ROOT / "runtime" / "offline_validation_latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(out)}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
