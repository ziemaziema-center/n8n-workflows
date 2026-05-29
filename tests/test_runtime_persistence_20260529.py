from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import hq_company_task_runner as company_runner
from scripts import hq_runtime_handoff as handoff
from scripts import hq_runtime_queue_manager as queue_manager
from scripts import hq_runtime_state_manager as state_manager
from scripts import hq_runtime_telemetry as telemetry


class RuntimePersistenceTests(unittest.TestCase):
    def test_state_initializes_saves_loads_and_recovers_corrupt_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "runtime" / "state" / "current_state.json"
            state_manager.ensure_runtime_dirs(root)
            initial = state_manager.load_state(state_path)
            self.assertEqual(initial["runner_status"], "IDLE")
            saved = state_manager.heartbeat(
                task_id="hq-state-unit",
                runner_status="RUNNING",
                phase="unit",
                log_path="runtime/logs/unit.log",
                state_path=state_path,
            )
            self.assertEqual(saved["active_task_id"], "hq-state-unit")
            loaded = state_manager.load_state(state_path)
            self.assertEqual(loaded["current_phase"], "unit")
            state_path.write_text("{not-json", encoding="utf-8")
            recovered = state_manager.load_state(state_path)
            self.assertTrue(recovered["recovered_from_corrupt_state"])
            self.assertTrue(Path(str(recovered["corrupt_state_backup_path"])).exists())

    def test_queue_enqueue_claim_retry_and_completion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            queue_root = Path(tmp) / "runtime" / "queue"
            task = {
                "task_id": "hq-queue-unit",
                "objective": "Queue persistence unit",
                "workspace_path": "/home/ubuntu/workspace/true-autonomous-controller",
            }
            first = queue_manager.enqueue_task(task, queue_root)
            duplicate = queue_manager.enqueue_task(task, queue_root)
            self.assertEqual(first["status"], "QUEUED")
            self.assertEqual(duplicate["status"], "DUPLICATE")
            self.assertEqual(len(queue_manager.list_pending(queue_root)), 1)
            claimed = queue_manager.claim_next_task(queue_root)
            self.assertIsNotNone(claimed)
            self.assertEqual(claimed["status"], "RUNNING")
            retried = queue_manager.increment_retry("hq-queue-unit", queue_root)
            self.assertEqual(retried["retry_count"], 1)
            claimed_again = queue_manager.claim_next_task(queue_root)
            self.assertIsNotNone(claimed_again)
            done = queue_manager.mark_task("hq-queue-unit", "PASS_WITH_AUTO_REPAIR", queue_root, reason="unit pass")
            self.assertEqual(done["status"], "PASS_WITH_AUTO_REPAIR")
            history = (queue_root / "history.jsonl").read_text(encoding="utf-8")
            self.assertIn("task_retry_incremented", history)

    def test_telemetry_jsonl_appends_without_secret_or_live_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime" / "telemetry" / "events.jsonl"
            event = telemetry.append_event(
                path,
                event_type="task_enqueued",
                task_id="hq-telemetry-unit",
                phase="queue",
                status="QUEUED",
                message="unit event",
                artifacts={"queue": "runtime/queue/pending.json"},
            )
            self.assertFalse(event["live_operations_performed"])
            self.assertFalse(event["secret_values_included"])
            events = telemetry.read_events(path)
            self.assertEqual(len(events), 1)
            rendered = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("sk-", rendered)
            self.assertNotIn("telegram_token", rendered)

    def test_handoff_json_and_markdown_are_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = handoff.build_handoff(
                active_task={"task_id": "hq-handoff-unit"},
                completed_items=["state loaded"],
                pending_items=["resume task"],
                deferred_gates=[{"name": "codex_auth", "reason": "device auth required"}],
                last_validation_result={"status": "PASS", "command": "unit", "checked_at": "now"},
                next_executable_actions=["continue queue"],
                exact_resume_prompt="Resume hq-handoff-unit.",
            )
            paths = handoff.write_handoff(
                payload,
                json_path=root / "runtime" / "handoff" / "current_handoff.json",
                md_path=root / "runtime" / "handoff" / "current_handoff.md",
            )
            self.assertTrue(Path(paths["handoff_json_path"]).exists())
            self.assertIn("Resume hq-handoff-unit", Path(paths["handoff_md_path"]).read_text(encoding="utf-8"))

    def test_company_runner_output_exposes_persistence_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = {
                "task_id": "hq-company-persistence-unit",
                "objective": "Verify persistence integration.",
                "workspace_path": "/home/ubuntu/workspace/true-autonomous-controller",
                "target_runner": "dry_run",
            }
            with mock.patch.object(company_runner, "ROOT", root):
                report = company_runner.run_task(task)
            self.assertEqual(report["status"], "PASS")
            for key in ("runtime_state_path", "queue_path", "telemetry_path", "handoff_path"):
                self.assertIn(key, report)
                self.assertTrue(Path(report[key]).exists())
            self.assertFalse(report["live_production_mutation"])
            self.assertFalse(report["secret_values_printed"])

    def test_recovery_simulation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [sys.executable, "scripts/simulate_runtime_persistence.py", "--root", tmp],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["active_task_before_completion"], "hq-runtime-persistence-sim")
            self.assertFalse(result["live_operations_performed"])
            self.assertTrue(Path(result["state_path"]).exists())
            self.assertTrue(Path(result["handoff_path"]).exists())


if __name__ == "__main__":
    unittest.main()
