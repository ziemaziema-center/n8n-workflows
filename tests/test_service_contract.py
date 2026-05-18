import json
import tempfile
import unittest
from pathlib import Path

from src.tac.controller import task_from_prompt
from src.tac.service import ControllerState


class ServiceContractTests(unittest.TestCase):
    def test_state_runs_and_loads_task_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = ControllerState(root)
            task = task_from_prompt("service smoke", task_id="service-smoke", source="test")
            result = state.run_task(task)
            self.assertEqual(result["status"], "PASS")
            loaded = state.load_result("service-smoke")
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["task_id"], "service-smoke")
            raw = json.loads(state.result_path("service-smoke").read_text(encoding="utf-8"))
            self.assertEqual(raw["status"], "PASS")

    def test_telegram_followup_uses_latest_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target-workspace"
            target.mkdir()
            state = ControllerState(root)
            prior_dir = state.runtime_root / "tac-prior"
            prior_dir.mkdir(parents=True)
            (prior_dir / "result.json").write_text(
                json.dumps({"task_id": "tac-prior", "workspace": str(target), "status": "PASS"}),
                encoding="utf-8",
            )
            task = task_from_prompt(
                "FOLLOWUP_TASK: true\nUser message:\nread only 승인",
                task_id="tac-followup",
                source="telegram",
            )
            result = state.run_task(task)
            self.assertEqual(result["workspace"], str(target.resolve()))
            saved_task = json.loads(state.task_path("tac-followup").read_text(encoding="utf-8"))
            self.assertEqual(saved_task["workspace"], str(target))

    def test_state_enqueue_writes_queue_and_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = ControllerState(root)
            result = state.enqueue(
                {
                    "task_id": "hq-service-queue-smoke",
                    "objective": "service queue smoke",
                    "workspace_path": "/home/ubuntu/workspace/true-autonomous-controller",
                }
            )
            self.assertTrue(result["ok"])
            self.assertFalse(result["live_dispatch_performed"])
            self.assertTrue((root / "runtime/queue/hq-service-queue-smoke.json").exists())
            pending = (root / "runtime/queue/pending.jsonl").read_text(encoding="utf-8")
            self.assertIn("hq-service-queue-smoke", pending)
            self.assertTrue((root / "runtime/controller_state.sqlite3").exists())
            task = json.loads((root / "runtime/queue/hq-service-queue-smoke.json").read_text(encoding="utf-8"))
            self.assertIn("notification", task)
            self.assertFalse(task["notification"]["on_completion"])

    def test_state_enqueue_records_telegram_completion_notification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = ControllerState(root)
            result = state.enqueue(
                {
                    "task_id": "hq-service-notify-smoke",
                    "objective": "service notify smoke",
                    "workspace_path": "/home/ubuntu/workspace/true-autonomous-controller",
                    "chat_id": "12345",
                    "notify_webhook_url": "https://n8n.mykindredai.com/webhook/tac-controller",
                }
            )
            self.assertTrue(result["ok"])
            task = json.loads((root / "runtime/queue/hq-service-notify-smoke.json").read_text(encoding="utf-8"))
            self.assertTrue(task["notification"]["on_completion"])
            self.assertEqual(task["notification"]["chat_id"], "12345")

    def test_state_handoff_reads_continuation_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir()
            (reports / "hq_continuation_ledger_2026-05-18.json").write_text(
                json.dumps(
                    {
                        "current_phase": "phase4",
                        "next_executable_subtasks": ["docker dry-run"],
                        "final_report_path": "reports/phase4.md",
                        "resume_instruction": "resume here",
                    }
                ),
                encoding="utf-8",
            )
            state = ControllerState(root)
            result = state.handoff()
            self.assertTrue(result["ok"])
            self.assertEqual(result["status"], "HANDOFF_READY")
            self.assertEqual(result["next_executable_subtasks"], ["docker dry-run"])


if __name__ == "__main__":
    unittest.main()
