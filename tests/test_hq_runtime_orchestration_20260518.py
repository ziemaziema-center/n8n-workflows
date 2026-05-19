from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TELEGRAM_COMMANDS = {
    "/run",
    "/work",
    "/status",
    "/queue",
    "/pause",
    "/resume",
    "/killall",
    "/review",
    "/retry",
    "/handoff",
}


class RuntimeOrchestrationDraftTests(unittest.TestCase):
    def read_json(self, path: str) -> dict:
        with (ROOT / path).open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_runtime_queue_schema_and_sample(self) -> None:
        schema = self.read_json("schemas/runtime_queue.schema.json")
        sample = self.read_json("runtime/queue/sample_task.json")
        for key in schema["required"]:
            self.assertIn(key, sample)
        self.assertTrue(sample["workspace_path"].startswith("/home/ubuntu/workspace/"))
        self.assertIn("no_secrets", sample["allowed_scope"])
        self.assertIn("no_production_mutation", sample["allowed_scope"])
        self.assertEqual(sample["status"], "QUEUED")
        self.assertLessEqual(sample["max_retries"], 3)

        try:
            import jsonschema  # type: ignore
        except Exception:
            return
        jsonschema.validate(sample, schema)

    def test_runtime_state_schema_and_sample(self) -> None:
        schema = self.read_json("schemas/runtime_state.schema.json")
        sample = self.read_json("runtime/state/sample_state.json")
        for key in schema["required"]:
            self.assertIn(key, sample)
        self.assertIn(sample["runner_status"], {"IDLE", "RUNNING", "PAUSED", "KILLED", "ERROR"})
        self.assertTrue(sample["kill_switch_status"]["enabled"])

    def test_inactive_n8n_workflow_is_draft_only(self) -> None:
        workflow = self.read_json("workflows/inactive_hq_ssh_dispatch_draft_2026-05-18.json")
        self.assertFalse(workflow["active"])
        self.assertTrue(workflow["meta"]["draftOnly"])
        self.assertFalse(workflow["meta"]["liveSshExecuted"])
        self.assertFalse(workflow["meta"]["credentialsRequired"])
        for node in workflow["nodes"]:
            self.assertNotIn("credentials", node)
        rendered = json.dumps(workflow)
        self.assertIn("ssh_command_template", rendered)
        self.assertIn("DEFERRED_GATE_DRAFT_ONLY", rendered)

    def test_telegram_command_schema_contract(self) -> None:
        schema = self.read_json("schemas/telegram_hq_command.schema.json")
        commands = set(schema["properties"]["command"]["enum"])
        self.assertEqual(REQUIRED_TELEGRAM_COMMANDS, commands)
        rendered = json.dumps(schema)
        self.assertIn("live_approval_required", rendered)
        self.assertIn("expected_output", rendered)

    def test_tmux_templates_are_dry_run_and_bounded(self) -> None:
        required = [
            "scripts/hq_tmux_runner_template.sh",
            "scripts/hq_safe_agent_wrapper_template.sh",
            "scripts/hq_dispatch_task_template.sh",
            "scripts/hq_kill_switch_template.sh",
        ]
        for rel in required:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertRegex(text.lower(), r"dry[-_ ]?run|template only")
            self.assertIn("/home/ubuntu/workspace", text)
        wrapper = (ROOT / "scripts/hq_safe_agent_wrapper_template.sh").read_text(encoding="utf-8")
        self.assertIn("DEFERRED_GATE", wrapper)
        self.assertIn("--sandbox workspace-write", wrapper)
        self.assertIn("hq_company_task_runner.py", wrapper)

    def test_reviewer_loop_template_exists_and_classifies(self) -> None:
        text = (ROOT / "scripts/hq_reviewer_loop_template.py").read_text(encoding="utf-8")
        self.assertIn("DEFERRED_GATE", text)
        self.assertIn("HUMAN_APPROVAL_REQUIRED", text)
        self.assertIn("retry_count < max_retries", text)

    def test_ledger_and_deferred_gate_registry_are_updated(self) -> None:
        ledger = self.read_json("reports/hq_continuation_ledger_2026-05-18.json")
        completed = "\n".join(ledger["completed_items"])
        self.assertIn("runtime queue schema", completed)
        self.assertIn("inactive n8n SSH dispatch workflow draft", completed)
        self.assertEqual(
            ledger["final_report_path"],
            "reports/yuna_brain_growth_system_2026-05-19.md",
        )
        registry = (ROOT / "reports/deferred_gate_registry_2026-05-18.md").read_text(encoding="utf-8")
        for gate in [
            "n8n credentialed read-only check",
            "live SSH dispatch test",
            "Telegram live send test",
            "EC2 tmux live session creation",
            "production workflow activation",
            "helper deploy/restart",
            "Upbit IP/auth read-only check",
        ]:
            self.assertIn(gate, registry)

    def test_no_real_credentials_in_new_runtime_artifacts(self) -> None:
        targets = [
            "schemas/runtime_queue.schema.json",
            "schemas/runtime_state.schema.json",
            "schemas/telegram_hq_command.schema.json",
            "runtime/queue/sample_task.json",
            "runtime/state/sample_state.json",
            "workflows/inactive_hq_ssh_dispatch_draft_2026-05-18.json",
            "scripts/hq_tmux_runner_template.sh",
            "scripts/hq_safe_agent_wrapper_template.sh",
            "scripts/hq_dispatch_task_template.sh",
            "scripts/hq_kill_switch_template.sh",
            "scripts/hq_reviewer_loop_template.py",
        ]
        forbidden = re.compile(
            r"(sk-proj-[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|AA[A-Za-z0-9_-]{20,}:[A-Za-z0-9_-]{20,})"
        )
        for rel in targets:
            self.assertIsNone(forbidden.search((ROOT / rel).read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
