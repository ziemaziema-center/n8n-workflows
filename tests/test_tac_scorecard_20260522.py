from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TacScorecardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, "scripts/tac_scorecard.py"], cwd=ROOT, check=True, capture_output=True, text=True)

    def test_scorecard_has_ten_sectors_and_hits_target(self):
        data = json.loads((ROOT / "reports" / "tac_scorecard_2026-05-22.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["sectors"]), 10)
        self.assertGreaterEqual(data["improved_total"], 90)
        self.assertTrue(data["target_hit"])
        self.assertLess(data["baseline_total"], data["improved_total"])

    def test_scorecard_keeps_live_gate_caveat(self):
        text = (ROOT / "reports" / "tac_scorecard_2026-05-22.md").read_text(encoding="utf-8")
        self.assertIn("not a claim that every production live gate", text)
        self.assertIn("5-6 hour unattended overnight soak", text)
        self.assertIn("Docker-only Codex auth volume", text)

    def test_scorecard_evidence_files_exist(self):
        data = json.loads((ROOT / "reports" / "tac_scorecard_2026-05-22.json").read_text(encoding="utf-8"))
        for sector in data["sectors"]:
            self.assertTrue(sector["evidence_present"], sector["name"])

    def test_scorecard_records_strict_external_audit(self):
        data = json.loads((ROOT / "reports" / "tac_scorecard_2026-05-22.json").read_text(encoding="utf-8"))
        self.assertLessEqual(data["strict_external_audit_total"], data["baseline_total"])
        self.assertIn("queue locking", "\n".join(data["implemented_gap_fixes"]))
        self.assertIn("process-wide pkill", "\n".join(data["implemented_gap_fixes"]))


if __name__ == "__main__":
    unittest.main()
