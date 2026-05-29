# TAC Self-Repair Company Mode - 2026-05-29

## Status

PASS.

The company runner no longer treats a primary runner block as an immediate fallback path. It now attempts a bounded self-repair cycle before safe fallback.

## Changed

- Stored the permanent self-repair rule in `AGENTS.md`.
- Stored the permanent self-repair rule in `SESSION_BOOT.md`.
- Added `PASS_WITH_AUTO_REPAIR` as a first-class success status.
- Added a root-cause meeting record with Builder, Reviewer, Debugger, and HQ decision notes.
- Added bounded repair budget handling with a default maximum of 5 attempts.
- Added deterministic auto-repair for a missing Docker Codex auth-volume config:
  - detects the missing auth-volume failure signature
  - loads `TAC_CODEX_AUTH_VOLUME` from `runtime/config/tac_codex_auth_volume.local.env`
  - retries the primary runner before fallback
  - writes `runtime/repair/<task_id>.repair.json`
- Added deterministic auto-repair for Docker Codex auth-volume ownership:
  - detects `Permission denied` / `os error 13`
  - runs a bounded root helper container to set the auth volume owner to the container user
  - retries Docker Codex before fallback
- Fixed safe fallback so it does not overwrite `PASS_WITH_AUTO_REPAIR`.
- Added regression coverage proving repair happens before fallback.

## Validation

- `python -m py_compile scripts\hq_company_task_runner.py`: PASS
- `python -m unittest tests.test_company_runner_safe_fallback_20260529`: PASS, 5 tests
- `python -m unittest discover -s tests`: PASS, 141 tests
- `python scripts\run_offline_validations.py`: PASS

## EC2 Deployment Smoke

- Synced `scripts/hq_company_task_runner.py` to `/home/ubuntu/workspace/true-autonomous-controller/scripts/hq_company_task_runner.py`.
- Remote `python3 -m py_compile scripts/hq_company_task_runner.py`: PASS.
- Restarted scoped `tac-hq-runner`: PASS.
- Remote report-only smoke: `self-repair-remote-smoke-20260529`.
- Repair sequence observed:
  - option A loaded `TAC_CODEX_AUTH_VOLUME` from local config and retried Docker Codex.
  - option B repaired Docker Codex auth-volume ownership with the root helper container and retried Docker Codex.
  - option B ownership repair returned PASS.
- Final remote smoke status: `PASS_WITH_SAFE_FALLBACK`.
- Remaining gate: Docker Codex reached OpenAI with the mounted volume but returned `401 Unauthorized / Missing bearer`, so the Docker-only Codex auth volume needs a fresh login/device-auth session before Codex-backed execution can pass.

## Maturity Notes

Current repair coverage is real but intentionally narrow. The first deterministic repair surfaces are Docker Codex auth-volume loading and auth-volume ownership repair. Other failure classes still fall through to safe fallback after the repair meeting records that no safe automatic repair candidate exists.

Next repair candidates to add:

- Docker Codex `401 Unauthorized` preflight that reports a clear device-auth action before execution.
- CRLF shell script normalization before EC2 runner restart.
- Missing workspace directory creation.
- Permission-denied local artifact overwrite retry in user context.
- JSON/schema validation auto-fix for generated queue files.
- tmux runner stale-session recovery.

## Safety

No live n8n action, Telegram send, Instagram publish, Upbit credential action, production Docker restart, AWS mutation, secret read/output, force push, or destructive deletion was performed by this local patch.
