from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tac.queue_runtime import make_queue_task, validate_queue_task
from src.tac.runtime_engine import (
    build_continuation_handoff,
    record_heartbeat,
    retry_decision,
    runtime_event,
    transition_task,
)


class RuntimeEngineTests(unittest.TestCase):
    def test_queue_task_contains_lifecycle_continuation_and_telemetry(self) -> None:
        task = make_queue_task(task_id="hq-runtime-engine-unit", objective="validate queue metadata")
        validate_queue_task(task)
        self.assertEqual(task["owner"], "HQ")
        self.assertEqual(task["department"], "runtime_orchestration")
        self.assertTrue(task["continuation"]["handoff_required"])
        self.assertIn("event_log_path", task["telemetry"])
        self.assertEqual(task["lifecycle"][0]["to"], "QUEUED")

    def test_task_state_transition_and_retry_decision(self) -> None:
        task = make_queue_task(task_id="hq-runtime-transition-unit", objective="validate transition")
        running = transition_task(task, "RUNNING", actor="unit", reason="start")
        self.assertEqual(running["status"], "RUNNING")
        passed = transition_task(running, "PASS", actor="unit", reason="done")
        self.assertEqual(passed["status"], "PASS")
        self.assertEqual(len(passed["lifecycle"]), 3)
        decision = retry_decision(
            {"decision": "FAIL", "retry_allowed": True, "reason": "forced"},
            retry_count=1,
            max_retries=3,
        )
        self.assertEqual(decision["next_status"], "QUEUED")

    def test_invalid_state_transition_is_rejected(self) -> None:
        task = make_queue_task(task_id="hq-runtime-invalid-unit", objective="validate invalid transition")
        with self.assertRaises(ValueError):
            transition_task(task, "PASS", actor="unit", reason="skip running")

    def test_heartbeat_event_and_handoff_contract(self) -> None:
        state = {
            "active_task_id": None,
            "runner_status": "IDLE",
            "current_phase": "unit",
            "last_heartbeat_at": None,
            "last_log_path": None,
            "last_validation_result": {"status": "NOT_RUN", "command": None, "checked_at": None},
            "blocked_gates": [],
            "safe_next_actions": [],
            "kill_switch_status": {"enabled": True, "last_triggered_at": None, "command": "/killall"},
        }
        updated = record_heartbeat(state, runner_status="RUNNING", phase="unit", log_path="runtime/logs/unit.log")
        self.assertEqual(updated["runner_status"], "RUNNING")
        self.assertIsNotNone(updated["last_heartbeat_at"])
        event = runtime_event(
            task_id="hq-runtime-event-unit",
            event_type="HEARTBEAT",
            actor="unit",
            status="INFO",
            message="heartbeat",
        )
        self.assertFalse(event["live_operation"])
        self.assertFalse(event["secret_values_included"])
        handoff = build_continuation_handoff(
            task_id="hq-runtime-event-unit",
            completed_items=["heartbeat"],
            deferred_gates=[],
            next_actions=["continue"],
            validation_commands=["python scripts/runtime_engine_smoke.py"],
            final_report_path="reports/autonomous_runtime_buildout_report_2026-05-19.md",
        )
        self.assertIn("resume_prompt", handoff)

    def test_runtime_event_schema_sample_and_smoke(self) -> None:
        schema = json.loads((ROOT / "schemas/runtime_event.schema.json").read_text(encoding="utf-8"))
        sample_line = (ROOT / "telemetry/runtime_events.sample.jsonl").read_text(encoding="utf-8").strip()
        sample = json.loads(sample_line)
        for key in schema["required"]:
            self.assertIn(key, sample)
        self.assertFalse(sample["live_operation"])
        self.assertFalse(sample["secret_values_included"])
        completed = subprocess.run(
            [sys.executable, "scripts/runtime_engine_smoke.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads((ROOT / "runtime/runtime_engine_smoke_2026-05-19.json").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["live_operations_performed"])

    def test_reports_exist_for_runtime_and_growth_systems(self) -> None:
        for rel in [
            "reports/autonomous_runtime_buildout_report_2026-05-19.md",
            "reports/runtime_state_machine_2026-05-19.md",
            "reports/instagram_growth_experiment_system_2026-05-19.md",
            "reports/n8n_runtime_orchestration_draft_pack_2026-05-19.md",
        ]:
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_inactive_n8n_runtime_pack_is_draft_only(self) -> None:
        workflow = json.loads((ROOT / "workflows/inactive_hq_runtime_orchestration_pack_2026-05-19.json").read_text(encoding="utf-8"))
        self.assertFalse(workflow["active"])
        self.assertTrue(workflow["meta"]["draftOnly"])
        self.assertFalse(workflow["meta"]["liveSshExecuted"])
        self.assertFalse(workflow["meta"]["credentialsRequired"])
        names = {node["name"] for node in workflow["nodes"]}
        for expected in {
            "Normalize Queue Ingestion",
            "Validation Routing Draft",
            "Reviewer Routing Draft",
            "Retry Routing Draft",
            "Final Report Draft",
            "Escalation Routing Draft",
        }:
            self.assertIn(expected, names)
        for node in workflow["nodes"]:
            self.assertNotIn("credentials", node)
        rendered = json.dumps(workflow)
        self.assertIn("DEFERRED_GATE_DRAFT_ONLY", rendered)
        self.assertNotIn("n8n-nodes-base.ssh", rendered)


if __name__ == "__main__":
    unittest.main()
