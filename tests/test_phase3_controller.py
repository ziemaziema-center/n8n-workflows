import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.tac.controller import (
    ControllerError,
    Review,
    extract_requested_workspace,
    extract_codex_agent_text,
    extract_codex_agent_text_from_output,
    load_task,
    make_result_summary,
    redact_sensitive_text,
    resolve_workspace,
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
        self.assertIn("\uacb0\ub860: \uc644\ub8cc", result["summary"])

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
        self.assertIn("Return the final report in Korean", task["commands"][0]["argv"][-1])
        self.assertIn("Return the final report in Korean", task["commands"][0]["argv"][-1])
        self.assertIn("\uacb0\ub860, \uc608\uc0c1 \uc2dc\uac04/\uc2e4\uc81c \uc18c\uc694", task["commands"][0]["argv"][-1])
        validate_task_shape(task)

    def test_task_from_prompt_extracts_upbit_workspace_alias(self):
        task = task_from_prompt("upbit project diagnosis", task_id="unit-upbit", source="test", executor="codex")
        self.assertEqual(task["workspace"], "/home/ubuntu/workspace/02_\uc5c5\ube44\ud2b8_\uc790\ub3d9\ud654")
        self.assertIn("Bounded workspace: /home/ubuntu/workspace/02_\uc5c5\ube44\ud2b8_\uc790\ub3d9\ud654", task["commands"][0]["argv"][-1])

    def test_extract_requested_workspace_from_explicit_line(self):
        self.assertEqual(
            extract_requested_workspace("WORKSPACE: /home/ubuntu/workspace/demo\ndiagnose"),
            "/home/ubuntu/workspace/demo",
        )

    def test_resolve_workspace_allows_configured_workspace_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            allowed = Path(tmp).resolve()
            child = allowed / "project"
            child.mkdir()
            with patch.dict(os.environ, {"TAC_ALLOWED_WORKSPACE_ROOTS": str(allowed)}):
                self.assertEqual(resolve_workspace(ROOT, str(child)), child.resolve())

    def test_codex_sandbox_can_be_host_mode_from_environment(self):
        with patch.dict(os.environ, {"TAC_CODEX_SANDBOX": "danger-full-access"}):
            task = task_from_prompt("say ok", task_id="unit-codex-host", source="test", executor="codex")
        self.assertIn("danger-full-access", task["commands"][0]["argv"])

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
                json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "吏꾨떒 寃곌낵: Phase 1遺??吏꾪뻾"}}),
            ]
        )
        command_result = {
            "id": "codex-executor",
            "exit_code": 0,
            "stdout_tail": stdout_tail,
            "stderr_tail": "",
        }
        self.assertEqual(extract_codex_agent_text(command_result), "吏꾨떒 寃곌낵: Phase 1遺??吏꾪뻾")
        task = self.base_task()
        summary = make_result_summary(task, "PASS", Review("PASS", ["ok"], False, False), [command_result])
        self.assertIn("결론: 완료", summary)
        self.assertIn("상세 보고:", summary)
        self.assertIn("吏꾨떒 寃곌낵", summary)


    def test_extracts_codex_agent_message_from_agent_text_field(self):
        command_result = {
            "id": "codex-executor",
            "exit_code": 0,
            "agent_text": "?꾨즺 蹂닿퀬",
            "stdout_tail": '"text":"truncated',
            "stderr_tail": "",
        }
        self.assertEqual(extract_codex_agent_text(command_result), "?꾨즺 蹂닿퀬")

    def test_extracts_codex_agent_message_from_full_output(self):
        output = json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "full report"}})
        self.assertEqual(extract_codex_agent_text_from_output(output), "full report")


if __name__ == "__main__":
    unittest.main()
