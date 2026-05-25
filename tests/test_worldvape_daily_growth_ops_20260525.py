from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WorldvapeDailyGrowthOpsTests(unittest.TestCase):
    def test_schema_and_sample_parse(self) -> None:
        schema = json.loads((ROOT / "schemas/worldvape_daily_growth_routine.schema.json").read_text(encoding="utf-8"))
        sample = json.loads((ROOT / "runtime/worldvape_growth/sample_daily_routine.json").read_text(encoding="utf-8"))
        for key in schema["required"]:
            self.assertIn(key, sample)
        self.assertEqual(sample["brand"], "월드베이프 광운대점")
        self.assertFalse(sample["live_operations_performed"])

    def test_routine_contains_growth_loop_and_approval_gate(self) -> None:
        sample_text = (ROOT / "runtime/worldvape_growth/sample_daily_routine.json").read_text(encoding="utf-8")
        for marker in [
            "competitor_monitoring",
            "generate_yuna_candidates",
            "send_for_operator_approval",
            "record_result_and_learn",
            "follows_per_1000_reach",
            "publish_without_approval",
        ]:
            self.assertIn(marker, sample_text)

    def test_inactive_n8n_workflow_is_draft_only(self) -> None:
        workflow = json.loads((ROOT / "workflows/inactive_worldvape_daily_growth_ops_2026-05-25.json").read_text(encoding="utf-8"))
        self.assertFalse(workflow["active"])
        self.assertTrue(workflow["meta"]["draftOnly"])
        self.assertFalse(workflow["meta"]["liveOperationsPerformed"])
        for node in workflow["nodes"]:
            self.assertNotIn("credentials", node)
        self.assertNotRegex(json.dumps(workflow), r"sk-[A-Za-z0-9_-]{20,}|AA[A-Za-z0-9_-]{20,}:")
        for node in workflow["nodes"]:
            code = node.get("parameters", {}).get("jsCode")
            if code:
                self.assertTrue(code.isascii(), node["name"])

    def test_task_builder_outputs_safe_queue_task(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/worldvape_daily_growth_task_builder.py",
                "--date",
                "2026-05-25",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        task = json.loads(completed.stdout)
        self.assertEqual(task["task_id"], "worldvape-daily-growth-20260525")
        self.assertEqual(task["target_runner"], "codex")
        self.assertIn("no_production_mutation", task["allowed_scope"])
        self.assertIn("YUNA", task["objective"])
        self.assertIn("credential values", task["objective"])
        self.assertNotIn("force push", task["objective"].lower())
        self.assertFalse(task["notification"]["on_completion"] is False)

    def test_report_and_sendoff_exist(self) -> None:
        report = (ROOT / "reports/worldvape_gwangwoon_daily_growth_ops_2026-05-25.md").read_text(encoding="utf-8")
        sendoff = (ROOT / "docs/WORLDVAPE_GWANGWOON_GROWTH_SENDOFF_2026-05-25.md").read_text(encoding="utf-8")
        for marker in [
            "월드베이프 광운대점",
            "YUNA",
            "approval",
            "No live Instagram publish",
        ]:
            self.assertIn(marker, report + "\n" + sendoff)


if __name__ == "__main__":
    unittest.main()
