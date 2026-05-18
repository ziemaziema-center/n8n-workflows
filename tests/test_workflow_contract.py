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
        self.assertIn("\\uc0c1\\ud0dc: \\uc811\\uc218\\ub428", received_code)
        self.assertIn("\\uc608\\uc0c1 \\uc2dc\\uac04:", received_code)
        self.assertIn("\\uc9c4\\ud589 \\ubc29\\ud5a5:", received_code)
        self.assertIn("\\uc9c4\\ud589 \\uacc4\\ud68d:", received_code)
        self.assertIn("wantsLongRun", received_code)
        self.assertTrue(received_code.isascii())
        self.assertIn("30\\ubd84", received_code)
        self.assertIn("continuation ledger", received_code)
        self.assertIn("deferred gate", received_code)
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

    def test_telegram_workflow_supports_queue_and_handoff_routes(self):
        workflow = self.load_workflow("tac_telegram_commands.json")
        nodes = {node["name"]: node for node in workflow["nodes"]}
        normalize_code = nodes["Normalize Telegram Command"]["parameters"]["jsCode"]
        self.assertIn("^\\/(queue|work)\\b", normalize_code)
        self.assertIn("^\\/handoff\\b", normalize_code)
        self.assertIn("queue_mode: action === 'queue'", normalize_code)
        self.assertIn("handoff_mode: action === 'handoff'", normalize_code)
        self.assertIn("action = 'queue'", normalize_code)
        self.assertIn("!rawText.startsWith('/')", normalize_code)
        body_params = {
            item["name"]: item["value"]
            for item in nodes["Call TAC Runner"]["parameters"]["bodyParameters"]["parameters"]
        }
        self.assertEqual(body_params["objective"], "={{$json.prompt}}")
        self.assertEqual(body_params["workspace_path"], "=/home/ubuntu/workspace/true-autonomous-controller")
        self.assertEqual(body_params["source_channel"], "=telegram")
        self.assertEqual(body_params["chat_id"], "={{$json.chat_id}}")
        self.assertEqual(body_params["dispatch"], "=true")
        self.assertEqual(body_params["notify_webhook_url"], "=https://n8n.mykindredai.com/webhook/tac-controller")

    def test_controller_webhook_supports_notify_without_runner(self):
        workflow = self.load_workflow("tac_controller_webhook.json")
        nodes = {node["name"]: node for node in workflow["nodes"]}
        self.assertIn("IF Notify Action", nodes)
        normalize_code = nodes["Normalize TAC Command"]["parameters"]["jsCode"]
        self.assertIn("action = 'notify'", normalize_code)
        build_code = nodes["Build Telegram Summary"]["parameters"]["jsCode"]
        self.assertIn("isNotify", build_code)
        self.assertIn("notify_summary", build_code)
        self.assertEqual(
            workflow["connections"]["Normalize TAC Command"]["main"][0][0]["node"],
            "IF Notify Action",
        )
        self.assertEqual(
            workflow["connections"]["IF Notify Action"]["main"][0][0]["node"],
            "Build Telegram Summary",
        )
        self.assertEqual(
            workflow["connections"]["IF Notify Action"]["main"][1][0]["node"],
            "Call TAC Runner",
        )

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
            self.assertIn("\\uacb0\\uacfc \\uc694\\uc57d:", code)
            self.assertIn("\\uc0c1\\ud0dc: ", code)
            self.assertIn(".replace(/&/g, '&amp;')", code)
            self.assertIn(".replace(/</g, '&lt;')", code)
            self.assertIn(".replace(/>/g, '&gt;')", code)


if __name__ == "__main__":
    unittest.main()
