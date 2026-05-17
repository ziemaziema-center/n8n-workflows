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

## 2026-05-17 14:15 KST - Long Telegram Codex Reply Fix
- request: Explain whether no Telegram response after a long `/codex` command is normal and fix it if not.
- files_changed: `src/tac/controller.py`, `tests/test_phase3_controller.py`, `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `7a3f537` before timeout/output extraction patch.
- validation: PASS. Existing user task `tac-20260517044407-96cf346ad5` completed after 185 seconds but n8n disconnected; local tests 20/20 PASS; EC2 tests 20/20 PASS; n8n TAC workflows active; `/codex` webhook smoke task `tac-20260517051453-69c2e2e7fe` returned `Codex output: TELEGRAM_TIMEOUT_FIX_OK`.
- side_effects: Restarted only `tac-service` and n8n; updated only TAC workflows; no clean_01~04, Docker workload, Upbit live order, or credential value changed.
- rollback: Revert this patch, reimport previous workflow JSON, and restart `tac-service`/n8n.
- next_action: User can resend the long Telegram command; tasks under the 30-minute hard limit should now return a final Telegram report.

## 2026-05-17 14:50 KST - Telegram Natural Follow-Up Routing
- request: Fix another no-response case after the user sent a normal follow-up approval message without `/codex`.
- files_changed: `src/tac/controller.py`, `src/tac/service.py`, `tests/test_service_contract.py`, `workflows/tac_telegram_commands.json`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `60125ed` before natural follow-up routing patch.
- validation: PASS. Local tests 21/21 PASS; EC2 tests 21/21 PASS; `tac_telegram_commands` reimported/published and active; follow-up smoke task `tac-20260517054736-54de626dc9` returned `Codex output: FOLLOWUP_WORKSPACE_OK` and used `/home/ubuntu/workspace/02_upbit_automation_clean`.
- side_effects: Restarted only `tac-service` and n8n; updated only TAC Telegram workflow; no clean_01~04, Docker workload, Upbit live order, or credential value changed.
- rollback: Revert this patch, reimport prior `tac_telegram_commands.json`, and restart `tac-service`/n8n.
- next_action: User can resend the natural follow-up text; it should now be treated as a Codex follow-up to the latest bounded workspace.

## 2026-05-17 15:10 KST - Telegram Received Ack And Status UX
- request: Fix the controller bot end-to-end so users are not left wondering if a long task started.
- files_changed: `workflows/tac_telegram_commands.json`, `tests/test_workflow_contract.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `12c05a5` before Telegram received-ack patch.
- validation: PASS. Local tests 23/23 PASS; EC2 tests 23/23 PASS; n8n `tac_telegram_commands` reimported/published and active; `/status tac-20260517055951-c2007161f8` PASS; `/codex` smoke task `tac-20260517060655-8488d97be4` returned `FINAL_PIPELINE_OK`.
- side_effects: Restarted only n8n; updated only TAC Telegram workflow; no clean_01~04, Docker workload, Upbit live order, or credential value changed.
- rollback: Revert workflow JSON/test patch, reimport prior `tac_telegram_commands.json`, and restart n8n.
- next_action: Telegram run messages should now produce an immediate `status: RECEIVED` reply followed by the final report.

## 2026-05-17 15:40 KST - Telegram Immediate Execution Briefing
- request: Make Telegram immediately report expected direction, HQ/agent communication flow, execution approach, and estimated work time after a command.
- files_changed: `workflows/tac_telegram_commands.json`, `tests/test_workflow_contract.py`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `29bcf5b` before briefing patch.
- validation: PASS. Local tests 23/23 PASS; EC2 tests 23/23 PASS; workflow JSON parses; contract test requires `expected_time`, `expected_direction`, `hq_agent_flow`, and `execution_plan`; n8n `tac_telegram_commands` reimported/published and active; `/codex` smoke task `tac-20260517063840-a53dda620e` returned `ACK_BRIEFING_PATCH_OK`.
- side_effects: Restarted only n8n; updated only TAC Telegram workflow; no clean_01~04, Docker workload, Upbit live order, or credential value changed.
- rollback: Revert this patch, reimport previous Telegram workflow JSON, and restart n8n.
- next_action: User can send a Telegram command and should immediately receive a briefing message, then a final report.

## 2026-05-17 16:50 KST - Telegram Parse Mode Hardening
- request: Fix the real Telegram command path after the immediate briefing still failed for a natural-language follow-up.
- files_changed: `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, `tests/test_workflow_contract.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `baebb95` before parse-mode hardening.
- validation: PASS. Decoded n8n execution `10487` and found `Send Received Reply` failed with Telegram HTTP 400 `can't parse entities`; local tests 25/25 PASS; EC2 tests 25/25 PASS; live n8n export confirms all TAC Telegram send nodes use `parse_mode: HTML`; `tac_controller_webhook` with chat id returned 200 and sent task `tac-20260517074612-960807be93`.
- side_effects: Restarted only n8n; sent one validation Telegram summary to the user's controller chat; no clean_01~04 logic, Docker workload, Upbit live order, or credential value changed.
- rollback: Reimport workflow JSONs from commit `baebb95` and restart n8n, though that restores the Markdown entity bug.
- next_action: User can resend the 16:23 natural-language command; it should now receive the immediate briefing and then continue to runner execution.

## 2026-05-17 20:50 KST - Upbit First Bounded Cycle Replay
- request: Clarify whether the validation Telegram message was the end, then actually restart the missed Upbit command through the real Telegram Trigger path.
- files_changed: `workflows/tac_telegram_commands.json`, `tests/test_workflow_contract.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `e0dcc21` before long-run briefing regex hardening.
- validation: PASS. n8n execution `10545` exposed a non-ASCII regex failure; patched the briefing code to ASCII-only long-run detection; local tests 25/25 PASS; EC2 tests 25/25 PASS; replayed an explicit Upbit `/codex` bounded task through the Telegram Trigger webhook; n8n execution `10546` succeeded; TAC task `tac-20260517114459-672cbd72` PASS.
- side_effects: Restarted only n8n; sent immediate and final Telegram messages for the replayed Upbit task; Codex modified only the bounded Upbit workspace by adding explicit local `active: false` fields and additive report/memory entries; no live trading, n8n activation, Docker restart, production mutation, or secret printing.
- rollback: Revert local controller workflow/test patch; in the Upbit workspace, use the generated backup `backups/controller_cycle_20260517_inactive_flags` if the explicit inactive flags need to be restored.
- next_action: Continue Upbit work in additional bounded cycles, starting with read-only runtime n8n/helper preflight and current-order state verification.

## 2026-05-17 21:05 KST - Korean Operator Telegram Reports
- request: Make Telegram replies easy to understand in Korean, with clear planning, expected time, completed work, blocked work, remaining work, and updates.
- files_changed: `src/tac/controller.py`, `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, `tests/test_phase3_controller.py`, `tests/test_workflow_contract.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `6788a4f` before Korean operator-report patch.
- validation: PASS. Local tests 25/25 PASS; JSON validation PASS; EC2 tests 25/25 PASS; `tac-service` health PASS after restart; n8n TAC workflows active after reimport/publish/restart; webhook smoke `tac-20260517120607-84e5e72d6d` returned Korean result summary; real Telegram Trigger execution `10554` succeeded with Korean received/final messages.
- side_effects: Restarted only `tac-service` and n8n; sent one short Telegram smoke pair; no clean_01~04 logic, Docker workload, Upbit live order, or credential value changed.
- rollback: Revert this patch, redeploy previous controller/workflow files, restart `tac-service` and n8n.
- next_action: Future real `/codex` tasks should produce Korean plain-language reports from both the controller wrapper and Codex prompt.

## 2026-05-17 22:20 KST - MCP Connectivity Matrix
- request: Connect n8n, GitHub, Filesystem, Docker, PostgreSQL/SQLite, and Telegram MCP capabilities to Codex with all approvals.
- files_changed: `docs/MCP_CONNECTIVITY_MATRIX.md`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `bbeee6d` before MCP connectivity documentation.
- validation: PASS. n8n MCP health returned `success=true`; GitHub plugin tools are exposed; node REPL MCP returned current workspace; Codex local config confirms n8n MCP and GitHub plugin are configured without recording secrets; Docker CLI exists but Docker MCP is not exposed; PostgreSQL/SQLite/Telegram MCP tools are not exposed in this session.
- side_effects: Documentation and telemetry only; no credential value stored; no n8n workflow, Docker container, database, Telegram bot, or production state changed.
- rollback: Delete `docs/MCP_CONNECTIVITY_MATRIX.md` and revert telemetry append if this project should not track MCP state.
- next_action: Add GitHub remote/repo access first, then install/configure Docker MCP before true containerized autonomy.

## 2026-05-17 23:10 KST - Local Docker And State DB MCP Registration
- request: Execute the remaining MCP connection steps: GitHub remote/connector access, Docker MCP install/register, controller state DB schema plus PostgreSQL/SQLite MCP, and keep Telegram through n8n.
- files_changed: `.gitignore`, `scripts/mcp/docker_mcp_server.js`, `scripts/mcp/state_db_mcp_server.py`, `tests/test_mcp_servers.py`, `docs/MCP_CONNECTIVITY_MATRIX.md`, `docs/MCP_LOCAL_SERVERS.md`, `docs/CONTROLLER_STATE_DB_SCHEMA.md`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- external_config_changed: Added `mcp_servers.tac-docker` and `mcp_servers.tac-state-db` to `~/.codex/config.toml`; backup created beside the config before modification.
- git_remote_changed: Added local remote `n8n-workflows-backup` pointing to `https://github.com/ziemaziema-center/n8n-workflows.git`.
- validation: PASS. GitHub connector commit search for `ziemaziema-center/n8n-workflows` succeeded; `git ls-remote` succeeded; MCP protocol tests pass; SQLite state DB initialized; Docker Desktop daemon status read passed through `tac-docker` MCP; full local tests 28/28 PASS.
- side_effects: Created ignored local DB file `runtime/controller_state.sqlite3`; repaired local `.docker` directory ACL; started Docker Desktop; no container was started; direct Telegram MCP was intentionally not added.
- rollback: Remove the two TAC MCP blocks from `~/.codex/config.toml`, delete `runtime/controller_state.sqlite3`, remove remote `n8n-workflows-backup`, and revert this commit.
- next_action: Start a new Codex session to load the newly registered MCP tool namespaces; keep Docker mutation disabled until an explicitly approved bounded container run.
