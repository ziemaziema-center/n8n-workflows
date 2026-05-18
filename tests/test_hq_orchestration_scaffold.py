import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PERMANENT_RULE = "Do not stop the whole task because one live/credential/network item is blocked."


class HqOrchestrationScaffoldTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_permanent_rule_is_stored_in_instruction_files(self):
        for relative in ("AGENTS.md", "SESSION_BOOT.md", "docs/TRUE_AUTONOMOUS_CONTROLLER_MASTER_SENDOFF_2026-05-18.md"):
            self.assertIn(PERMANENT_RULE, self.read(relative), relative)
            self.assertIn("deferred gate", self.read(relative).lower(), relative)

    def test_hq_operating_model_exists(self):
        text = self.read("reports/hq_autonomous_controller_operating_model_2026-05-18.md")
        for required in (
            "HQ / Master Controller",
            "Planner",
            "Builder",
            "Reviewer",
            "Debugger",
            "QA",
            "Continuation ledger",
            "DEFERRED_GATE",
        ):
            self.assertIn(required, text)

    def test_continuation_ledger_is_machine_readable(self):
        ledger = json.loads(self.read("reports/hq_continuation_ledger_2026-05-18.json"))
        self.assertEqual(ledger["task_id"], "tac-hq-orchestration-20260518")
        self.assertFalse(ledger["live_operations_performed"])
        self.assertGreaterEqual(len(ledger["completed_items"]), 5)
        self.assertGreaterEqual(len(ledger["deferred_gates"]), 3)
        self.assertGreaterEqual(len(ledger["next_executable_subtasks"]), 3)
        self.assertIn("python -m unittest discover -s tests", ledger["validation_commands"])

    def test_deferred_gate_registry_records_blocked_but_not_fatal_items(self):
        text = self.read("reports/deferred_gate_registry_2026-05-18.md")
        for gate in (
            "helper production deploy or restart",
            "Upbit authenticated read-only",
            "n8n authenticated read-only",
            "live Instagram publishing",
            "safe work continued",
        ):
            self.assertIn(gate, text)

    def test_tmux_runtime_scaffold_exists(self):
        report = self.read("reports/tmux_persistent_runtime_layer_2026-05-18.md")
        runner = self.read("scripts/hq_tmux_runner_template.sh")
        wrapper = self.read("scripts/hq_safe_agent_wrapper_template.sh")
        self.assertIn("Telegram -> n8n -> SSH dispatch -> tmux", report)
        self.assertIn("pending.jsonl", runner)
        self.assertIn("tmux", runner)
        self.assertIn("DEFERRED_GATE", wrapper)
        self.assertIn("codex --ask-for-approval never exec", wrapper)

    def test_instagram_growth_plan_exists(self):
        text = self.read("reports/instagram_10k_growth_hq_plan_2026-05-18.md")
        for required in (
            "10K",
            "Growth Strategist",
            "Content Strategist",
            "Automation Engineer",
            "Data Analyst",
            "7-Day Action Plan",
            "14-Day Action Plan",
            "Experiment Backlog",
            "No live Instagram publishing was performed",
        ):
            self.assertIn(required, text)

    def test_safe_work_continues_despite_live_gates(self):
        ledger = json.loads(self.read("reports/hq_continuation_ledger_2026-05-18.json"))
        gate_names = {gate["name"] for gate in ledger["deferred_gates"]}
        self.assertIn("live_instagram_publish", gate_names)
        self.assertIn("n8n_authenticated_read_only", gate_names)
        self.assertIn("Instagram 10K growth HQ plan created", ledger["completed_items"])
        self.assertIn("tmux persistent runtime layer scaffold created", ledger["completed_items"])


if __name__ == "__main__":
    unittest.main()
