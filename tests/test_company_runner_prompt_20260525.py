from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from scripts.hq_company_task_runner import company_prompt, run_codex_docker


class CompanyRunnerPromptTests(unittest.TestCase):
    def test_prompt_forbids_approval_only_plan(self) -> None:
        prompt = company_prompt(
            {
                "objective": "Improve bounded project safely.",
                "workspace_path": "/home/ubuntu/workspace/example",
            }
        )
        self.assertIn("ALL SAFE LOCAL/OFFLINE WORK IS ALREADY APPROVED", prompt)
        self.assertIn("Do not ask for approval", prompt)
        self.assertIn("Do not return only a plan", prompt)
        self.assertIn("execute immediately", prompt)

    @mock.patch("scripts.hq_company_task_runner.subprocess.run")
    @mock.patch("scripts.hq_company_task_runner.shutil.which", return_value="/usr/bin/docker")
    @mock.patch.dict(
        "os.environ",
        {"TAC_CODEX_AUTH_VOLUME": "tac-codex-auth", "TAC_CODEX_IMAGE": "tac-codex-runner:codex"},
        clear=False,
    )
    def test_docker_runner_adds_host_group_for_workspace_writes(self, _which: mock.Mock, run: mock.Mock) -> None:
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""

        result = run_codex_docker("do safe work", Path("/home/ubuntu/workspace/example"), 30)

        command = run.call_args.args[0]
        self.assertEqual(result["status"], "PASS")
        self.assertIn("--group-add", command)
        self.assertRegex(command[command.index("--group-add") + 1], r"^\d+$")


if __name__ == "__main__":
    unittest.main()
