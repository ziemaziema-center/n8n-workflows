from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase3RuntimeOrchestrationTests(unittest.TestCase):
    def test_docker_runner_scaffold_exists(self) -> None:
        dockerfile = (ROOT / "docker/tac-runner.Dockerfile").read_text(encoding="utf-8")
        report = (ROOT / "reports/docker_isolated_runner_scaffold_2026-05-18.md").read_text(encoding="utf-8")
        self.assertIn("USER tacrunner", dockerfile)
        self.assertIn("--network=none", report)
        self.assertIn("must not mount", report)

    def test_docker_runner_plan_generator(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/docker_isolated_runner_plan.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        plan = json.loads((ROOT / "runtime/docker_runner_plan_2026-05-18.json").read_text(encoding="utf-8"))
        self.assertFalse(plan["live_container_started"])
        self.assertEqual(plan["network_policy"], "disabled by default; enable only per approved task")

    def test_phase3_orchestrator_passes_local_loop(self) -> None:
        out = ROOT / "runtime/phase3_orchestrator_result_2026-05-18.json"
        completed = subprocess.run(
            [sys.executable, "scripts/hq_phase3_orchestrator.py", "--out", str(out)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["live_operations_performed"])
        self.assertIn("planner", result)
        self.assertIn("final_review", result)

    def test_queue_soak_observes_retry_and_deferred_gate(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/queue_soak_test.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads((ROOT / "runtime/queue_soak_result_2026-05-18.json").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["forced_retry_observed"])
        self.assertTrue(result["deferred_gate_recorded"])
        self.assertTrue(result["safe_work_continued"])

    def test_git_checkpoint_manifest_is_non_mutating(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/git_checkpoint_manifest.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads((ROOT / "runtime/git_checkpoint_latest.json").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "CHECKPOINT_READY")
        self.assertTrue(result["pre_run_checkpoint_required"])
        self.assertFalse(result["force_push_allowed"])


if __name__ == "__main__":
    unittest.main()
