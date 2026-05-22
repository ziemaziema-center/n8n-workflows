from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RunnerSafetyTests(unittest.TestCase):
    def test_company_runner_host_fallback_is_not_default(self):
        text = (ROOT / "scripts" / "hq_company_task_runner.py").read_text(encoding="utf-8")
        self.assertIn('TAC_ALLOW_HOST_CODEX_FALLBACK", "0"', text)

    def test_service_start_defaults_to_workspace_write(self):
        text = (ROOT / "scripts" / "start_tac_service.sh").read_text(encoding="utf-8")
        self.assertIn("workspace-write", text)
        self.assertIn("TAC_ALLOW_HOST_CODEX_FALLBACK", text)
        self.assertNotIn(":-danger-full-access", text)

    def test_tmux_runner_uses_queue_locking(self):
        text = (ROOT / "scripts" / "hq_tmux_runner_template.sh").read_text(encoding="utf-8")
        self.assertIn("flock", text)
        self.assertIn("pending.lock", text)
        self.assertIn("multi-runner races", text)


if __name__ == "__main__":
    unittest.main()
