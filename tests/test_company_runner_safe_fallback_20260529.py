from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import hq_company_task_runner as runner


class CompanyRunnerSafeFallbackTests(unittest.TestCase):
    def test_safe_fallback_converts_runner_block_into_auditable_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task = {
                "task_id": "safe-fallback-smoke",
                "objective": "Finish safe local work even if Docker is unavailable.",
                "workspace_path": "/home/ubuntu/workspace/example",
                "deferred_gates": [{"name": "docker_codex_unavailable"}],
            }
            blocked = {"status": "DEFERRED_GATE", "runner": "docker_codex", "reason": "docker unavailable"}
            with mock.patch.object(runner, "ROOT", root):
                fallback, fallback_path = runner.apply_safe_fallback(task, blocked)

            self.assertEqual(fallback["status"], "PASS_WITH_SAFE_FALLBACK")
            self.assertEqual(fallback["original_runner_status"], "DEFERRED_GATE")
            self.assertIsNotNone(fallback_path)
            report = Path(str(fallback_path))
            self.assertTrue(report.exists())
            text = report.read_text(encoding="utf-8")
            self.assertIn("Safe Work Completed Instead Of Stopping", text)
            self.assertIn("docker_codex_unavailable", text)
            self.assertIn("Next Executable Safe Subtasks", text)

    def test_tmux_report_includes_company_status(self) -> None:
        script = Path("scripts/hq_tmux_runner_template.sh").read_text(encoding="utf-8")
        self.assertIn("company_status", script)
        self.assertIn("generated_report_path", script)


if __name__ == "__main__":
    unittest.main()
