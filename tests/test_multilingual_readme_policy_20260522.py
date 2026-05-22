from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MultilingualReadmePolicyTests(unittest.TestCase):
    def test_root_readme_has_required_language_sections(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for heading in ["## English", "## Français", "## Español", "## 한국어", "## 中文"]:
            self.assertIn(heading, text)

    def test_permanent_policy_is_stored_in_boot_files(self):
        combined = "\n".join(
            [
                (ROOT / "AGENTS.md").read_text(encoding="utf-8"),
                (ROOT / "SESSION_BOOT.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "TAC_OPERATOR_README_POLICY_2026-05-22.md").read_text(encoding="utf-8"),
            ]
        )
        self.assertIn("English, French, Spanish, Korean, and Chinese", combined)
        self.assertIn("Every README", combined)
        self.assertIn("vendored README", combined)


if __name__ == "__main__":
    unittest.main()
