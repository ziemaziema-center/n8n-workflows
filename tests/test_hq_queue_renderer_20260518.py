from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class QueueRendererTests(unittest.TestCase):
    def test_korean_telegram_renderer_writes_preview(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            out = Path(tmp) / "preview.txt"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/render_telegram_korean_summary.py",
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["ok"])
            text = out.read_text(encoding="utf-8")
            self.assertIn("상태: 로컬 준비 완료", text)
            self.assertIn("이번에 끝난 일:", text)
            self.assertIn("아직 남은 일:", text)
            self.assertIn("live Telegram send gate", text)

    def test_sqlite_queue_writer_validates_and_records_task(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db = Path(tmp) / "state.sqlite3"
            queue = Path(tmp) / "queue"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/hq_sqlite_queue_writer.py",
                    "--task-id",
                    "hq-unit-queue-writer-20260518",
                    "--db",
                    str(db),
                    "--queue-dir",
                    str(queue),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["live_dispatch_performed"])
            self.assertTrue(Path(payload["task_path"]).exists())
            self.assertTrue((queue / "pending.jsonl").exists())
            with sqlite3.connect(db) as conn:
                row = conn.execute("SELECT task_id, status FROM tasks WHERE task_id = ?", ("hq-unit-queue-writer-20260518",)).fetchone()
            self.assertEqual(row, ("hq-unit-queue-writer-20260518", "QUEUED"))

    def test_reviewer_feedback_schema_and_sample_jsonl(self) -> None:
        schema = json.loads((ROOT / "schemas/reviewer_feedback.schema.json").read_text(encoding="utf-8"))
        sample_path = ROOT / "runtime/reviewer_feedback/sample_feedback.jsonl"
        lines = [line for line in sample_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        sample = json.loads(lines[0])
        for key in schema["required"]:
            self.assertIn(key, sample)
        self.assertIn(sample["decision"], schema["properties"]["decision"]["enum"])
        self.assertIsInstance(sample["retry_allowed"], bool)
        self.assertNotRegex(lines[0], r"sk-[A-Za-z0-9_-]{20,}|AA[A-Za-z0-9_-]{20,}:[A-Za-z0-9_-]{20,}")

    def test_import_checklist_exists_and_keeps_workflow_inactive(self) -> None:
        checklist = (ROOT / "reports/inactive_n8n_import_validation_checklist_2026-05-18.md").read_text(encoding="utf-8")
        self.assertIn("Keep the workflow inactive", checklist)
        self.assertIn("No credentials are attached", checklist)
        self.assertIn("No SSH command runs", checklist)


if __name__ == "__main__":
    unittest.main()
