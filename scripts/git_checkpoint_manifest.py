from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "runtime" / "git_checkpoint_latest.json"


def git(args: list[str], cwd: Path) -> str:
    completed = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False, timeout=30)
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def build_manifest(workspace: Path) -> dict[str, object]:
    return {
        "status": "CHECKPOINT_READY",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace.resolve()),
        "head": git(["rev-parse", "--short", "HEAD"], workspace),
        "branch": git(["branch", "--show-current"], workspace),
        "dirty_files": [line for line in git(["status", "--short"], workspace).splitlines() if line],
        "pre_run_checkpoint_required": True,
        "post_pass_commit_allowed": "bounded local work only",
        "force_push_allowed": False,
        "rollback_instruction": "Use the recorded HEAD and task report before reverting any user changes.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Write TAC Git checkpoint manifest without mutating Git.")
    parser.add_argument("--workspace", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    manifest = build_manifest(args.workspace)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
