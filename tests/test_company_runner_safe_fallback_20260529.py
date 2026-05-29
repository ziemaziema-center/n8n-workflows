from __future__ import annotations

import os
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

    def test_auto_repair_retries_codex_after_loading_auth_volume_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = root / "runtime" / "config" / "tac_codex_auth_volume.local.env"
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text("TAC_CODEX_AUTH_VOLUME=tac_codex_auth\n", encoding="utf-8")
            task = {
                "task_id": "auto-repair-auth-volume-smoke",
                "objective": "Repair missing Docker Codex auth volume before falling back.",
                "workspace_path": str(root / "workspace"),
                "target_runner": "codex",
                "max_repair_attempts": 5,
            }
            first = {
                "status": "DEFERRED_GATE",
                "runner": "docker_codex",
                "reason": "container-specific Codex auth volume is not configured",
            }
            second = {
                "status": "PASS",
                "runner": "docker_codex",
                "agent_message": "AUTO_REPAIR_OK",
            }

            with mock.patch.object(runner, "ROOT", root), mock.patch.object(
                runner, "run_codex_docker", side_effect=[first, second]
            ), mock.patch.dict(os.environ, {"TAC_USE_DOCKER_CODEX": "1"}, clear=False):
                os.environ.pop("TAC_CODEX_AUTH_VOLUME", None)
                report = runner.run_task(task)

            self.assertEqual(report["status"], "PASS_WITH_AUTO_REPAIR")
            self.assertEqual(report["runner_result"]["repair_cycles_used"], 1)
            self.assertEqual(report["runner_result"]["repaired_runner_result"]["agent_message"], "AUTO_REPAIR_OK")
            repair_path = Path(str(report["repair_record_path"]))
            self.assertTrue(repair_path.exists())
            repair_text = repair_path.read_text(encoding="utf-8")
            self.assertIn("builder_opinion", repair_text)
            self.assertIn("repair_options", repair_text)

    def test_auto_repair_chowns_auth_volume_after_permission_denied(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = root / "runtime" / "config" / "tac_codex_auth_volume.local.env"
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text("TAC_CODEX_AUTH_VOLUME=tac_codex_auth\n", encoding="utf-8")
            task = {
                "task_id": "auto-repair-auth-volume-permission-smoke",
                "objective": "Repair Docker Codex auth volume ownership before falling back.",
                "workspace_path": str(root / "workspace"),
                "target_runner": "codex",
                "max_repair_attempts": 5,
            }
            first = {
                "status": "DEFERRED_GATE",
                "runner": "docker_codex",
                "reason": "container-specific Codex auth volume is not configured",
            }
            second = {
                "status": "FAIL",
                "runner": "docker_codex",
                "stderr_tail": "Error: Permission denied (os error 13)",
            }
            third = {
                "status": "PASS",
                "runner": "docker_codex",
                "agent_message": "CHOWN_REPAIR_OK",
            }

            with mock.patch.object(runner, "ROOT", root), mock.patch.object(
                runner, "run_codex_docker", side_effect=[first, second, third]
            ), mock.patch.object(
                runner, "repair_docker_auth_volume_ownership", return_value={"status": "PASS", "runner": "ownership_repair"}
            ) as ownership_repair, mock.patch.dict(os.environ, {"TAC_USE_DOCKER_CODEX": "1"}, clear=False):
                os.environ.pop("TAC_CODEX_AUTH_VOLUME", None)
                report = runner.run_task(task)

            self.assertEqual(report["status"], "PASS_WITH_AUTO_REPAIR")
            self.assertEqual(report["runner_result"]["repair_cycles_used"], 2)
            self.assertEqual(report["runner_result"]["repaired_runner_result"]["agent_message"], "CHOWN_REPAIR_OK")
            ownership_repair.assert_called_once()
            repair_text = Path(str(report["repair_record_path"])).read_text(encoding="utf-8")
            self.assertIn("repair Docker Codex auth-volume ownership", repair_text)

    def test_auth_volume_ownership_repair_runs_helper_as_root(self) -> None:
        completed = mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch.object(runner.shutil, "which", return_value="docker"), mock.patch.object(
            runner.subprocess, "run", return_value=completed
        ) as subprocess_run:
            result = runner.repair_docker_auth_volume_ownership("tac_codex_auth", "tac-codex-runner:codex")

        self.assertEqual(result["status"], "PASS")
        command = subprocess_run.call_args.args[0]
        self.assertIn("--user", command)
        self.assertIn("0:0", command)


if __name__ == "__main__":
    unittest.main()
