from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class YunaGrowthBrainTests(unittest.TestCase):
    def test_schema_and_sample_exist_and_parse(self) -> None:
        schema = json.loads((ROOT / "schemas/yuna_growth_experiment.schema.json").read_text(encoding="utf-8"))
        sample = json.loads((ROOT / "runtime/yuna_growth_experiments/sample_experiment.json").read_text(encoding="utf-8"))
        for key in schema["required"]:
            self.assertIn(key, sample)
        self.assertEqual(sample["status"], "DRAFT")
        self.assertFalse(sample["live_operations_performed"])

    def test_sample_focuses_on_follow_comment_save_dm(self) -> None:
        sample_text = (ROOT / "runtime/yuna_growth_experiments/sample_experiment.json").read_text(encoding="utf-8")
        for marker in ["follow", "comment", "save", "dm_reply", "follows_per_1000_reach"]:
            self.assertIn(marker, sample_text)
        self.assertIn("댓글", sample_text)
        self.assertIn("YUNA", sample_text)

    def test_hq_model_contains_required_agents(self) -> None:
        text = (ROOT / "reports/yuna_brain_hq_agent_operating_model_2026-05-19.md").read_text(encoding="utf-8")
        for marker in [
            "15-year SNS Marketing Strategist",
            "Behavioral Psychology PhD",
            "Content Strategist",
            "Data Analyst",
            "Automation Engineer",
            "Safety Reviewer",
        ]:
            self.assertIn(marker, text)
        self.assertIn("Views alone are not the target", text)

    def test_growth_report_has_meeting_and_next_patch(self) -> None:
        text = (ROOT / "reports/yuna_brain_growth_system_2026-05-19.md").read_text(encoding="utf-8")
        for marker in [
            "Internal HQ Meeting Result",
            "follows per 1,000 reach",
            "comments per 1,000 reach",
            "DM replies per 1,000 reach",
            "Next Executable Patch",
            "No live Instagram publishing",
        ]:
            self.assertIn(marker, text)

    def test_sendoff_contains_future_task_contract(self) -> None:
        text = (ROOT / "docs/YUNA_BRAIN_SENDOFF_2026-05-19.md").read_text(encoding="utf-8")
        for marker in [
            "Do not optimize for views alone",
            "15-year SNS Marketing Strategist",
            "Behavioral Psychology PhD",
            "first-frame claim",
            "comment CTA",
            "Deferred gates",
        ]:
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
