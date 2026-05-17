import json
import sys
import tempfile
import unittest
from pathlib import Path

from src.tac.controller import (
    ControllerError,
    Review,
    extract_codex_agent_text,
    load_task,
    make_result_summary,
    redact_sensitive_text,
    review_attempt,
    run_controller,
    task_from_prompt,
    validate_task_shape,
)


ROOT = Path(__file__).resolve().parents[1]


class Phase3ControllerTests(unittest.TestCase):
    def base_task(self):
        return {
            "task_id": "unit-phase3",
            "requested_phase": 3,
            "source": "test",
            "prompt": "unit test",
            "workspace": ".",
            "execution_mode": "dry_run",
            "risk_level": "read_only",
            "limits": {
                "max_iterations": 10,
                "max_runtime_sec": 1800,
                "retry_limit": 3,
                "cost_ceiling_usd": 5,
            },
            "commands": [{"id": "ok", "argv": ["echo", "ok"]}],
        }

    def test_loads_example_task(self):
        task = load_task(ROOT / "examples" / "phase3_task.dry_run.json")
        self.assertEqual(task["requested_phase"], 3)

    def test_dry_run_passes(self):
        result = run_controller(self.base_task(), ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["attempts"], 1)
        self.assertIn("[PASS]", result["summary"])

    def test_blocks_risky_task(self):
        task = self.base_task()
        task["risk_level"] = "risky"
        result = run_controller(task, ROOT)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(result["review"]["escalation_required"])

    def test_blocks_workspace_escape(self):
        task = self.base_task()
        task["workspace"] = ".."
        result = run_controller(task, ROOT)
        self.assertEqual(result["status"], "BLOCKED")

    def test_blocks_denied_executable(self):
        task = self.base_task()
        task["commands"] = [{"id": "bad", "argv": ["ssh", "example.com"]}]
        result = run_controller(task, ROOT)
        self.assertEqual(result["status"], "BLOCKED")

    def test_rejects_excessive_limits(self):
        task = self.base_task()
        task["limits"]["max_runtime_sec"] = 1801
        with self.assertRaises(ControllerError):
            validate_task_shape(task)

    def test_local_command_runs_allowlisted_python(self):
        task = self.base_task()
        task["execution_mode"] = "local_command"
        task["commands"] = [{"id": "python-version", "argv": [sys.executable, "--version"]}]
        result = run_controller(task, ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["commands"][0]["exit_code"], 0)

    def test_cli_result_file_shape(self):
        task = self.base_task()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "task.json"
            path.write_text(json.dumps(task), encoding="utf-8")
            loaded = load_task(path)
        self.assertEqual(loaded["task_id"], "unit-phase3")

    def test_task_from_prompt_is_bounded_dry_run(self):
        task = task_from_prompt("/run hello", task_id="unit-generated", source="telegram")
        self.assertEqual(task["task_id"], "unit-generated")
        self.assertEqual(task["execution_mode"], "dry_run")
        self.assertEqual(task["risk_level"], "read_only")
        validate_task_shape(task)
        result = run_controller(task, ROOT)
        self.assertEqual(result["status"], "PASS")

    def test_task_from_prompt_can_build_codex_executor(self):
        task = task_from_prompt("say ok", task_id="unit-codex", source="test", executor="codex")
        self.assertEqual(task["execution_mode"], "local_command")
        self.assertEqual(task["commands"][0]["id"], "codex-executor")
        self.assertEqual(task["commands"][0]["argv"][:4], ["codex", "--ask-for-approval", "never", "exec"])
        self.assertIn("--sandbox", task["commands"][0]["argv"])
        self.assertIn("workspace-write", task["commands"][0]["argv"])
        self.assertIn("--skip-git-repo-check", task["commands"][0]["argv"])
        validate_task_shape(task)

    def test_codex_auth_error_blocks_without_retry(self):
        task = task_from_prompt("say ok", task_id="unit-codex-auth", source="test", executor="codex")
        review = review_attempt(
            task,
            [
                {
                    "id": "codex-executor",
                    "exit_code": 1,
                    "stdout_tail": "unexpected status 401 Unauthorized: Incorrect API key provided",
                    "stderr_tail": "",
                }
            ],
        )
        self.assertEqual(review.status, "BLOCKED")
        self.assertFalse(review.retry_allowed)
        self.assertTrue(review.escalation_required)

    def test_redacts_api_keys_from_command_output(self):
        text = "Incorrect API key provided: " + "sk-" + "proj-abcdefghijklmnopqrstuvwxyz1234567890"
        redacted = redact_sensitive_text(text)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", redacted)
        self.assertIn("sk-REDACTED", redacted)

    def test_extracts_codex_agent_message_for_summary(self):
        stdout_tail = "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "unit"}),
                json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "진단 결과: Phase 1부터 진행"}}),
            ]
        )
        command_result = {
            "id": "codex-executor",
            "exit_code": 0,
            "stdout_tail": stdout_tail,
            "stderr_tail": "",
        }
        self.assertEqual(extract_codex_agent_text(command_result), "진단 결과: Phase 1부터 진행")
        task = self.base_task()
        summary = make_result_summary(task, "PASS", Review("PASS", ["ok"], False, False), [command_result])
        self.assertIn("Codex output:", summary)
        self.assertIn("진단 결과", summary)


if __name__ == "__main__":
    unittest.main()
