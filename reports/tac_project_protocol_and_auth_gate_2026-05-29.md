# TAC Project Protocol And Docker Codex Auth Gate - 2026-05-29

## Status

PASS.

## What Changed

- Stored the permanent project-command protocol in `AGENTS.md`.
- Stored the permanent project-command protocol in `SESSION_BOOT.md`.
- Updated company runner prompts so project-scale tasks must proceed phase by phase.
- Added phase scoring requirements:
  - at least 10 sectors
  - target score 97/100
  - self-improvement/debug/validation loop before advancing when safe
  - reread the original objective at each phase boundary
- Added clear final project report requirements:
  - phase summaries
  - score history
  - bugs found/fixed
  - validation results
  - remaining gates
  - usage instructions
  - revision questions
- Added Docker Codex auth failure classification:
  - `401 Unauthorized`
  - `Missing bearer`
  - `not logged in`
  - `codex cli is not logged in`
- Docker Codex auth failures now become a clear `DEFERRED_GATE` with a device-auth/login action instead of a generic failure.

## Validation

- `python -m py_compile scripts\hq_company_task_runner.py`: PASS
- `python -m unittest tests.test_company_runner_safe_fallback_20260529`: PASS, 8 tests
- `python -m unittest discover -s tests`: PASS, 144 tests
- `python scripts\run_offline_validations.py`: PASS

## EC2 Deployment Smoke

- Synced `scripts/hq_company_task_runner.py` to `/home/ubuntu/workspace/true-autonomous-controller/scripts/hq_company_task_runner.py`.
- Remote `python3 -m py_compile scripts/hq_company_task_runner.py`: PASS.
- Restarted scoped `tac-hq-runner`: PASS.
- Remote report-only smoke: `self-repair-remote-smoke-20260529`.
- Final smoke status: `PASS_WITH_SAFE_FALLBACK`.
- Important improvement: `original_runner_status` is now `DEFERRED_GATE`, and the repair meeting cause is `Docker Codex auth volume exists but is not logged in`.
- Remaining user action: refresh Docker-only Codex login/device-auth for the configured auth volume, then retry Codex-backed tasks.

## Remaining Gate

Docker-only Codex auth still needs an actual valid login inside the configured auth volume. This cannot be completed non-interactively when OpenAI device auth requires the user to enter a one-time code.

## Safety

No live n8n workflow activation, Telegram send, Instagram publish, Upbit action, production Docker restart, AWS mutation, secret read/output, force push, or destructive deletion was performed by this local patch.
