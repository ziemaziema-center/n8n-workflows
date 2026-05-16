# Patch History

## Role

Append-only operational changelog for TRUE AUTONOMOUS CONTROLLER.

## Entry Format

```text
## YYYY-MM-DD HH:mm TZ - Patch Title
- request:
- files_changed:
- backup_path:
- validation:
- side_effects:
- rollback:
- next_action:
```

## 2026-05-16 09:00 KST - Controller Bootstrap Memory Pack
- request: Start new TRUE AUTONOMOUS CONTROLLER session with memory-first, validation-first, additive-only, telemetry-aware operating mode.
- files_changed: `AGENTS.md`, `SESSION_BOOT.md`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Not required because the controller workspace had no existing files.
- validation: PASS. `Get-ChildItem -Recurse -File` confirmed 6 files; `Select-String` confirmed markers for memory-first, SESSION_BOOT, known failures, validated patterns, patch history, daily execution log, and immediate implementation target.
- side_effects: Local documentation and memory files only; no EC2, n8n, Docker, GitHub, Telegram, Git repository, or production workflow mutation.
- rollback: Delete the newly added files if rejected.
- next_action: Validate markers, then implement Phase 1 local contracts and dry-run runner scaffold.

## 2026-05-16 18:00 KST - Phase 0-3 Controller Scaffold And EC2 tmux Validation
- request: Implement through Phase 3, run it, find bugs, debug, loop x3, and report success.
- files_changed: `.gitignore`, `contracts/*`, `docs/*`, `examples/phase3_task.dry_run.json`, `scripts/run_phase3_loop.py`, `scripts/run_validation_loop.sh`, `src/tac/*`, `tests/test_phase3_controller.py`, `runtime/phase3_result_*.json`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Git baseline commit `72c2540` before scaffold implementation.
- validation: PASS. Local tests 8/8 passed repeatedly; local smoke PASS; EC2 read-only readiness confirmed SSH, tmux 3.4, Claude Code 2.1.139, Docker, n8n container, reel-service container; EC2 `codex` not found; EC2 tmux validation loop x3 produced PASS JSON files. Generated Python cache files were removed in cleanup commit `4f30757`.
- side_effects: Created bounded EC2 workspace `/home/ubuntu/workspace/true-autonomous-controller`; copied scaffold files there; no n8n workflow, Docker container, Telegram bot, GitHub remote, or production service mutation.
- rollback: Revert local Git changes after `72c2540`; remove `/home/ubuntu/workspace/true-autonomous-controller` if remote scaffold rollback is requested.
- next_action: Wire n8n/Telegram to call the already validated runner contract, or first add an inactive n8n workflow draft if credential IDs are available.

## 2026-05-17 06:56 KST - Semi-Live n8n Controller MVP
- request: With all approvals, complete the one-day semi-live controller MVP and do not stop mid-run.
- files_changed: `src/tac/controller.py`, `src/tac/service.py`, `scripts/start_tac_service.sh`, `scripts/run_tac_http_service.py`, `tests/*`, `workflows/tac_controller_webhook.json`, `docs/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `5007b9a` before semi-live MVP changes.
- validation: PASS. Local tests 11/11 passed; EC2 tests 11/11 passed; EC2 service `/health`, `/run`, `/status`, `/killall` passed; n8n webhook `/run` loop x3 returned PASS; n8n `/status` and `/killall` returned PASS; Claude Code direct smoke and TAC service `executor=claude` smoke returned command status PASS.
- side_effects: Created/updated active n8n workflow `tac_controller_webhook`; restarted only `n8n` to register the webhook; restarted scoped tmux `tac-service`; no existing clean_01~04 workflow logic was edited.
- rollback: Unpublish/delete `tac_controller_webhook`; stop `tac-service`; revert local Git changes after `5007b9a` if needed.
- next_action: Decide whether to wire an actual Telegram bot webhook to `tac-controller` or keep webhook-based command ingress to avoid conflicting with existing Telegram approval workflows.
