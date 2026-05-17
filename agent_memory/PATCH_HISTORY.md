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

## 2026-05-17 07:50 KST - Telegram Command Trigger And Claude Route
- request: Execute the remaining pieces with all approvals.
- files_changed: `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, `docs/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `0c72894` before Telegram command workflow and Claude route changes.
- validation: PASS. n8n logs show `tac_telegram_commands` active; `/run` controller webhook PASS; `/claude` controller webhook PASS with `claude-executor`; `/status` for Claude task PASS; `/killall` PASS; local tests 11/11 PASS.
- side_effects: Added active n8n workflow `tac_telegram_commands`; restarted only n8n to register trigger; existing clean_01~04 workflow logic was not edited.
- rollback: Unpublish/delete `tac_telegram_commands` and/or `tac_controller_webhook`; stop scoped `tac-service` if needed.
- next_action: User can send `/run`, `/claude`, `/status`, or `/killall` to the configured Kindred Debug Guard Telegram bot, or continue using the HTTPS webhook directly.

## 2026-05-17 08:25 KST - Dedicated Kindred AI Controller Bot Cutover
- request: Create a dedicated `Kindred AI Controller` Telegram bot path, move TAC commands off `Kindred Debug Guard`, clean command routing, and keep planner/reviewer loop reachable through n8n.
- files_changed: `workflows/tac_controller_webhook.json`, `workflows/tac_telegram_commands.json`, `docs/TELEGRAM_N8N_TMUX_CONTRACT.md`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `f4e3a47` before dedicated controller bot cutover.
- validation: PASS. New n8n credential `Kindred AI Controller` created; bot identity/menu set for `@kindred_ai_controller_bot`; Telegram webhook registered to n8n with zero pending updates; credential usage shows both TAC workflows on the new credential and no TAC workflows on `Kindred Debug Guard`; local tests 11/11 PASS; `/run`, `/claude`, `/status`, and `/killall` regressions PASS.
- side_effects: Reimported/reactivated `tac_controller_webhook` and `tac_telegram_commands`; restarted only `n8n`; existing clean_01~04 workflow logic not edited; debug bot remains assigned only to existing debug workflows.
- rollback: Reimport previous workflow JSON from Git commit `f4e3a47` or repoint TAC Telegram nodes to the old credential, reactivate both TAC workflows, and restart only n8n.
- next_action: User can open Telegram bot `@kindred_ai_controller_bot`, press Start, then send `/run smoke test` or `/claude Return OK` for human-origin end-to-end confirmation.

## 2026-05-17 09:05 KST - Codex-First Executor Cutover
- request: Replace Claude naming and execution with Codex so the controller bot uses Codex as the live agent.
- files_changed: `AGENTS.md`, `SESSION_BOOT.md`, `src/tac/controller.py`, `scripts/start_tac_service.sh`, `tests/test_phase3_controller.py`, `workflows/tac_controller_webhook.json`, `workflows/tac_telegram_commands.json`, `docs/TELEGRAM_N8N_TMUX_CONTRACT.md`, `docs/PHASE_0_3_RUNBOOK.md`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `0f069f5` before Codex-first cutover.
- validation: PARTIAL PASS. Current-facing source/workflow/docs no longer expose `/claude`; Codex CLI `0.130.0` installed on EC2; local tests 11/11 PASS; EC2 tests 11/11 PASS; n8n TAC workflows active; `/run` PASS; `/codex` returns `BLOCKED` immediately because Codex CLI is not logged in; `/status` PASS; `/killall` PASS.
- side_effects: Reimported/reactivated both TAC workflows; restarted `tac-service`; restarted only `n8n`; updated Telegram bot command menu to `/run`, `/codex`, `/status`, `/killall`; no clean_01~04 logic edited.
- rollback: Revert this commit, redeploy prior `controller.py`, reimport prior TAC workflow JSON, and restart only `tac-service` and n8n.
- next_action: Complete Codex authentication on EC2 runner with `codex login --with-api-key` or `codex login`; then rerun `/codex Print exactly TAC_CODEX_WEBHOOK_OK and do not modify files.`

## 2026-05-17 11:05 KST - Codex Invalid API Key Handling
- request: Diagnose `/codex` failure after user completed Codex login.
- files_changed: `src/tac/controller.py`, `tests/test_phase3_controller.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `7b528f3` before auth failure handling patch.
- validation: PASS. Failed task result showed `invalid_api_key`; local tests 13/13 PASS; EC2 tests 13/13 PASS; `/codex` now returns `BLOCKED` with escalation in one attempt; EC2 generated result files were redacted and no longer match API-key prefixes.
- side_effects: Restarted only `tac-service`; no n8n workflow, Docker, clean_01~04, or credential value was changed.
- rollback: Revert this patch and restart `tac-service`, not recommended because it would restore retrying invalid credentials.
- next_action: User must replace the EC2 Codex credential with a valid OpenAI API key or use device auth, then rerun `/codex Print exactly TAC_CODEX_OK and do not modify files.`

## 2026-05-17 12:36 KST - Codex ChatGPT Login Live PASS
- request: Validate controller after user completed Codex device auth login.
- files_changed: `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `0b70845` before recording live Codex PASS.
- validation: PASS. EC2 `codex login status` shows ChatGPT login; n8n TAC workflows are active; `tac-service` is running; `/codex Print exactly TAC_CODEX_OK and do not modify files.` returned task `tac-20260517033536-bb8a366f30` with status PASS and agent message `TAC_CODEX_OK`; `/status` PASS; `/killall` PASS.
- side_effects: Local telemetry append only; no EC2 code, n8n workflow, Docker, or credential value changed.
- rollback: Not required.
- next_action: Use `/codex` for real bounded development tasks, starting with small repo diagnosis before longer implementation.

## 2026-05-17 12:45 KST - Telegram Summary Includes Codex Output
- request: Make Telegram report show the actual Codex plan/diagnosis, not only generic PASS.
- files_changed: `src/tac/controller.py`, `tests/test_phase3_controller.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `05a6c0f` before summary extraction patch.
- validation: PASS. Local tests 14/14 PASS; EC2 tests 14/14 PASS; `/codex` webhook response for task `tac-20260517034419-6e3a728f89` includes `Codex output:` and the actual agent message in `telegram_text`.
- side_effects: Restarted only `tac-service`; no n8n workflow, Docker, clean_01~04, or credential value changed.
- rollback: Revert this patch and restart `tac-service`.
- next_action: Re-run the Upbit diagnosis prompt; Telegram should now include the visible diagnosis/report body.

## 2026-05-17 13:00 KST - Codex Bounded Workspace Host-Mode Fallback
- request: Fix `/codex` Upbit diagnosis after Telegram showed Codex could not read files because `bwrap` failed on EC2.
- files_changed: `src/tac/controller.py`, `src/tac/service.py`, `scripts/start_tac_service.sh`, `tests/test_phase3_controller.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `d020864` before host-mode fallback patch.
- validation: PASS. Local tests 18/18 PASS; EC2 tests 18/18 PASS; `tac-service` health PASS; n8n `/codex` read-only Upbit workspace smoke returned PASS with concrete Codex output; `/status tac-20260517035838-8102c8f455` PASS; `/killall` PASS and no Codex process remained.
- side_effects: Restarted only `tac-service`; switched EC2 service default Codex sandbox to `danger-full-access` as a temporary host-mode fallback bounded by `/home/ubuntu/workspace`; no n8n workflow, Docker, clean_01~04, or credential value changed.
- rollback: Set `TAC_CODEX_SANDBOX=workspace-write` and restart `tac-service`, or revert this patch; recommended long-term fix remains Docker-isolated Codex runner.
- next_action: Send real project requests with an explicit first line such as `WORKSPACE: /home/ubuntu/workspace/02_업비트_자동화`; build Docker isolation before unattended overnight mutation.
