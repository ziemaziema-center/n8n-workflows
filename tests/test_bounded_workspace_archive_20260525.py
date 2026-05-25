from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.create_bounded_workspace_archive import build_archive


class BoundedWorkspaceArchiveTests(unittest.TestCase):
    def test_archive_excludes_secret_like_files_and_heavy_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            root.mkdir()
            (root / "safe.md").write_text("safe", encoding="utf-8")
            (root / ".env").write_text("blocked", encoding="utf-8")
            (root / "credentials.json").write_text("blocked", encoding="utf-8")
            node_modules = root / "node_modules"
            node_modules.mkdir()
            (node_modules / "package.json").write_text("blocked", encoding="utf-8")

            output = Path(tmp) / "out.zip"
            manifest = build_archive(root, output)

            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
            self.assertEqual(names, {"safe.md"})
            self.assertEqual(manifest["included_count"], 1)
            self.assertGreaterEqual(manifest["skipped_count"], 2)
            self.assertTrue(output.with_suffix(".zip.manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
