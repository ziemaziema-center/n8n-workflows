from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOPE_REPORT = ROOT / "reports/marketing_hq_posting_scope_confirmation_2026-06-01.md"
SCOPE_SAFETY = ROOT / "reports/marketing_hq_posting_safety_matrix_2026-06-01.md"
SEND_JSON = ROOT / "runtime/marketing_hq/telegram_preview_send_20260601.json"
PREVIEW_JSON = ROOT / "runtime/marketing_hq/telegram_preview_package_20260601.json"


class MarketingHqPostingScopeConfirmationTests(unittest.TestCase):
    def test_core_artifacts_exist(self) -> None:
        for path in [SCOPE_REPORT, SCOPE_SAFETY, SEND_JSON, PREVIEW_JSON]:
            self.assertTrue(path.exists(), str(path))

    def test_candidate_count_is_two(self) -> None:
        payload = json.loads(PREVIEW_JSON.read_text(encoding="utf-8-sig"))
        self.assertEqual(len(payload["candidates"]), 2)

    def test_authorization_locks_are_false(self) -> None:
        payload = json.loads(SEND_JSON.read_text(encoding="utf-8-sig"))
        self.assertFalse(payload["render_authorization"])
        self.assertFalse(payload["publish_authorization"])
        self.assertFalse(payload["n8n_live_change_authorization"])
        self.assertFalse(payload["cron_authorization"])
        self.assertFalse(payload["clean01_clean04_execution"])
        self.assertFalse(payload["instagram_publish"])

    def test_scope_report_records_account_handle_gap(self) -> None:
        text = SCOPE_REPORT.read_text(encoding="utf-8-sig")
        self.assertIn("ACCOUNT_HANDLE_MISSING", text)
        self.assertIn("CONFIRMED_WITH_ACCOUNT_HANDLE_GAP", text)

    def test_scope_report_does_not_authorize_publish(self) -> None:
        text = SCOPE_REPORT.read_text(encoding="utf-8-sig")
        self.assertIn("publish_status: BLOCKED", text)
        self.assertIn("render_status: BLOCKED", text)
        self.assertIn("telegram_preview_status: BLOCKED", text)


if __name__ == "__main__":
    unittest.main()

