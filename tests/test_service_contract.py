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


if __name__ == "__main__":
    unittest.main()
