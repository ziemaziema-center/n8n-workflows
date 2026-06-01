from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEND_REPORT = ROOT / "reports/marketing_hq_telegram_preview_send_2026-06-01.md"
SEND_JSON = ROOT / "runtime/marketing_hq/telegram_preview_send_20260601.json"
RENDER_GATE = ROOT / "reports/marketing_hq_future_render_gate_packet_2026-06-01.md"
PUBLISH_GATE = ROOT / "reports/marketing_hq_future_publish_gate_packet_2026-06-01.md"
CLOSING_QA = ROOT / "reports/marketing_hq_posting_scope_closing_qa_report_2026-06-01.md"


class MarketingHqTelegramPreviewSendTests(unittest.TestCase):
    def test_send_artifacts_exist(self) -> None:
        for path in [SEND_REPORT, SEND_JSON, RENDER_GATE, PUBLISH_GATE]:
            self.assertTrue(path.exists(), str(path))

    def test_send_status_and_message_ids(self) -> None:
        payload = json.loads(SEND_JSON.read_text(encoding="utf-8-sig"))
        self.assertIn(payload["send_status"], {"SENT", "BLOCKED", "NOT_RUN"})
        self.assertIsInstance(payload["message_ids"], list)
        if payload["send_status"] != "SENT":
            self.assertEqual(payload["message_ids"], [])

    def test_preview_send_does_not_authorize_render_or_publish(self) -> None:
        payload = json.loads(SEND_JSON.read_text(encoding="utf-8-sig"))
        self.assertFalse(payload["render_authorization"])
        self.assertFalse(payload["publish_authorization"])
        self.assertFalse(payload["n8n_live_change_authorization"])
        self.assertFalse(payload["cron_authorization"])
        self.assertFalse(payload["clean01_clean04_execution"])
        self.assertFalse(payload["instagram_publish"])

    def test_button_safety_and_seller_price_controls_still_hold(self) -> None:
        text = SEND_REPORT.read_text(encoding="utf-8-sig")
        self.assertIn("send_status:", text)
        self.assertNotIn("seller url", text.lower())
        self.assertNotIn("http://", text)
        self.assertNotIn("https://", text)

    def test_future_gate_packets_do_not_execute_live_actions(self) -> None:
        render_text = RENDER_GATE.read_text(encoding="utf-8-sig")
        publish_text = PUBLISH_GATE.read_text(encoding="utf-8-sig")
        self.assertIn("render_approved_now: false", render_text)
        self.assertIn("no_publish: true", render_text)
        self.assertIn("final_human_publish_approval_required: true", publish_text)

    def test_closing_qa_file_exists_after_full_run(self) -> None:
        self.assertTrue(CLOSING_QA.exists(), str(CLOSING_QA))


if __name__ == "__main__":
    unittest.main()

