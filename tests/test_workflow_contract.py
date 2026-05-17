import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WorkflowContractTests(unittest.TestCase):
    def load_workflow(self, name):
        return json.loads((ROOT / "workflows" / name).read_text(encoding="utf-8"))

    def test_telegram_workflow_sends_received_before_runner(self):
        workflow = self.load_workflow("tac_telegram_commands.json")
        nodes = {node["name"]: node for node in workflow["nodes"]}
        self.assertIn("Build Received Reply", nodes)
        self.assertIn("Send Received Reply", nodes)
        self.assertIn("Restore Command After Received", nodes)
        self.assertIn("makeTaskId", nodes["Normalize Telegram Command"]["parameters"]["jsCode"])
        self.assertIn("/status ${taskId}", nodes["Build Received Reply"]["parameters"]["jsCode"])
        connections = workflow["connections"]
        self.assertEqual(
            connections["IF Run Action"]["main"][0][0]["node"],
            "Build Received Reply",
        )
        self.assertEqual(
            connections["Restore Command After Received"]["main"][0][0]["node"],
            "Call TAC Runner",
        )

    def test_telegram_workflow_replies_to_unsupported_slash_commands(self):
        workflow = self.load_workflow("tac_telegram_commands.json")
        nodes = {node["name"]: node for node in workflow["nodes"]}
        self.assertIn("Build Unsupported Reply", nodes)
        self.assertIn("Send Unsupported Reply", nodes)
        unsupported_branch = workflow["connections"]["IF Supported Command"]["main"][1]
        self.assertEqual(unsupported_branch[0]["node"], "Build Unsupported Reply")


if __name__ == "__main__":
    unittest.main()
