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


if __name__ == "__main__":
    unittest.main()
