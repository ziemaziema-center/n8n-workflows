from __future__ import annotations

import unittest

from scripts.hq_notify_completion import redact_response_body


class HqNotifyCompletionTests(unittest.TestCase):
    def test_redacts_chat_id_from_response_tail(self) -> None:
        body = '{"status":"PASS","chat_id":"7592247598","summary":"ok"}'
        redacted = redact_response_body(body)
        self.assertIn('"chat_id":"REDACTED_CHAT_ID"', redacted)
        self.assertNotIn("7592247598", redacted)

    def test_redacts_escaped_chat_id_from_saved_json_string(self) -> None:
        body = r'{\"status\":\"PASS\",\"chat_id\":\"7592247598\",\"summary\":\"ok\"}'
        redacted = redact_response_body(body)
        self.assertIn(r'\"chat_id\":\"REDACTED_CHAT_ID\"', redacted)
        self.assertNotIn("7592247598", redacted)


if __name__ == "__main__":
    unittest.main()
