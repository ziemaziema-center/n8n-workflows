from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "backups",
    "logs",
    "tmp",
    ".pytest_cache",
}

SECRET_NAME_PARTS = {
    ".env",
    "credential",
    "credentials",
    "secret",
    "token",
    "apikey",
    "api_key",
    "private",
    "pem",
    "key",
}


def is_excluded(path: Path, root: Path) -> tuple[bool, str]:
    rel = path.relative_to(root)
    parts = {part.lower() for part in rel.parts}
    if parts & DEFAULT_EXCLUDE_DIRS:
        return True, "excluded_directory"
    name = path.name.lower()
    if any(part in name for part in SECRET_NAME_PARTS):
        return True, "secret_like_name"
    return False, ""


def build_archive(source: Path, output: Path) -> dict[str, object]:
    source = source.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    included: list[str] = []
    skipped: list[dict[str, str]] = []
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            excluded, reason = is_excluded(path, source)
            if excluded:
                if path.is_file():
                    skipped.append({"path": str(path.relative_to(source)), "reason": reason})
                continue
            if not path.is_file():
                continue
            rel = path.relative_to(source).as_posix()
            archive.write(path, rel)
            included.append(rel)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "output": str(output),
        "included_count": len(included),
        "skipped_count": len(skipped),
        "excluded_dirs": sorted(DEFAULT_EXCLUDE_DIRS),
        "secret_name_parts": sorted(SECRET_NAME_PARTS),
        "sample_included": included[:50],
        "sample_skipped": skipped[:50],
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a secret-excluding bounded workspace archive.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = build_archive(args.source, args.output)
    print(json.dumps({"status": "PASS", **manifest}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
