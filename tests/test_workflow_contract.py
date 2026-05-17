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
        received_code = nodes["Build Received Reply"]["parameters"]["jsCode"]
        self.assertIn("expected time:", received_code)
        self.assertIn("expected direction:", received_code)
        self.assertIn("HQ-agent flow:", received_code)
        self.assertIn("execution plan:", received_code)
        self.assertNotIn("expected_time:", received_code)
        self.assertNotIn("hq_agent_flow:", received_code)
        self.assertIn("/status ${taskId}", received_code)
        self.assertEqual(
            nodes["Send Received Reply"]["parameters"]["additionalFields"]["parse_mode"],
            "HTML",
        )
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

    def test_telegram_send_nodes_use_html_parse_mode(self):
        for name in ("tac_telegram_commands.json", "tac_controller_webhook.json"):
            workflow = self.load_workflow(name)
            send_nodes = [
                node for node in workflow["nodes"]
                if node["type"] == "n8n-nodes-base.telegram"
                and node["parameters"].get("operation") == "sendMessage"
            ]
            self.assertTrue(send_nodes)
            for node in send_nodes:
                self.assertEqual(
                    node["parameters"]["additionalFields"]["parse_mode"],
                    "HTML",
                    node["name"],
                )

    def test_telegram_dynamic_summaries_are_html_escaped(self):
        for name, build_node_name in (
            ("tac_telegram_commands.json", "Build Telegram Reply"),
            ("tac_controller_webhook.json", "Build Telegram Summary"),
        ):
            workflow = self.load_workflow(name)
            nodes = {node["name"]: node for node in workflow["nodes"]}
            code = nodes[build_node_name]["parameters"]["jsCode"]
            self.assertIn("escapeHtml", code)
            self.assertIn(".replace(/&/g, '&amp;')", code)
            self.assertIn(".replace(/</g, '&lt;')", code)
            self.assertIn(".replace(/>/g, '&gt;')", code)


if __name__ == "__main__":
    unittest.main()
