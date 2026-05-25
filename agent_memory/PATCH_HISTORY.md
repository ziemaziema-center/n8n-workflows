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

## 2026-05-18 12:20 KST - Continuation-First HQ Orchestration Scaffold
- request: Stop ending broad tasks after one blocked item; make TAC behave like a company-style HQ that keeps doing safe local/offline work, records gates, validates, and hands off the next executable cycle.
- files_changed: `AGENTS.md`, `SESSION_BOOT.md`, `src/tac/controller.py`, `workflows/tac_telegram_commands.json`, `tests/test_phase3_controller.py`, `tests/test_workflow_contract.py`, `tests/test_hq_orchestration_scaffold.py`, `scripts/hq_tmux_runner_template.sh`, `scripts/hq_safe_agent_wrapper_template.sh`, `scripts/run_offline_validations.py`, `docs/TRUE_AUTONOMOUS_CONTROLLER_MASTER_SENDOFF_2026-05-18.md`, `reports/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- backup_path: Local Git commit `328283d` before continuation-first HQ scaffold.
- validation: PASS. Full local tests 35/35 PASS; `python scripts/run_offline_validations.py` PASS; continuation ledger JSON parse PASS; `tac_telegram_commands.json` parse PASS.
- side_effects: Local/offline artifacts only; no live Telegram send, n8n activation, production restart, Instagram publish, Upbit action, secret read, AWS mutation, or Docker production operation.
- rollback: Revert this commit and restore prior controller prompt/workflow briefing if continuation-first behavior is rejected.
- next_action: Implement inactive n8n SSH dispatch draft and runtime queue schema from `reports/hq_continuation_ledger_2026-05-18.json`.
## 2026-05-18 13:40 KST - Inactive Runtime Orchestration Dispatch Layer
- request: Continue from the HQ scaffold and build the next real runtime orchestration layer: queue/state schemas, inactive n8n SSH dispatch draft, Telegram command schema, tmux integration templates, reviewer loop, offline tests, ledger updates, and final report.
- files_changed: `schemas/runtime_queue.schema.json`, `schemas/runtime_state.schema.json`, `schemas/telegram_hq_command.schema.json`, `runtime/queue/sample_task.json`, `runtime/state/sample_state.json`, `workflows/inactive_hq_ssh_dispatch_draft_2026-05-18.json`, `reports/runtime_queue_schema_2026-05-18.md`, `reports/runtime_state_model_2026-05-18.md`, `reports/telegram_hq_command_contract_2026-05-18.md`, `reports/inactive_n8n_ssh_dispatch_workflow_2026-05-18.md`, `reports/reviewer_retry_loop_2026-05-18.md`, `reports/hq_runtime_orchestration_final_report_2026-05-18.md`, `reports/hq_continuation_ledger_2026-05-18.json`, `reports/deferred_gate_registry_2026-05-18.md`, `scripts/hq_dispatch_task_template.sh`, `scripts/hq_kill_switch_template.sh`, `scripts/hq_safe_agent_wrapper_template.sh`, `scripts/hq_reviewer_loop_template.py`, `scripts/run_offline_validations.py`, `tests/test_hq_runtime_orchestration_20260518.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- validation: PASS. `python -m unittest discover -s tests` ran 43 tests; `python -m unittest tests.test_hq_runtime_orchestration_20260518` ran 8 tests; `python scripts/run_offline_validations.py` PASS.
- side_effects: Local/offline only. No live n8n activation, live SSH, Telegram send, Instagram publish, Upbit call, Docker production restart, AWS mutation, credential read, or secret output.
- rollback: Revert this commit to remove inactive runtime orchestration artifacts and tests.
- next_action: Add Telegram-ready Korean summary renderer and SQLite-backed queue writer that validates against `schemas/runtime_queue.schema.json`.

## 2026-05-18 13:55 KST - Queue Renderer And Live Gate Smoke
- request: Continue from the continuation ledger; build Korean Telegram summary renderer, SQLite-backed queue writer, reviewer feedback queue schema/tests, inactive n8n import checklist, then run approved live gate tests for SSH dispatch, EC2 tmux session, Telegram send, and n8n read-only.
- files_changed: `.gitignore`, `scripts/render_telegram_korean_summary.py`, `scripts/hq_sqlite_queue_writer.py`, `scripts/remote_live_gate_smoke.py`, `schemas/reviewer_feedback.schema.json`, `runtime/reviewer_feedback/sample_feedback.jsonl`, `reports/reviewer_feedback_queue_2026-05-18.md`, `reports/inactive_n8n_import_validation_checklist_2026-05-18.md`, `reports/hq_runtime_orchestration_live_gate_report_2026-05-18.md`, `reports/hq_continuation_ledger_2026-05-18.json`, `tests/test_hq_queue_renderer_20260518.py`, `tests/test_hq_orchestration_scaffold.py`, `tests/test_hq_runtime_orchestration_20260518.py`, `scripts/run_offline_validations.py`, telemetry files.
- validation: PASS. `python -m unittest discover -s tests` ran 47 tests; `python scripts/run_offline_validations.py` PASS; n8n MCP health/minimal workflow reads PASS; EC2 SSH queue append PASS; EC2 tmux scoped session creation/cleanup PASS; Telegram smoke task `tac-20260518044042-7651a7d56d` PASS.
- side_effects: One generated invalid EC2 queue line from an initial quoting attempt was backed up and filtered; one valid smoke queue item was appended; one scoped tmux smoke session was created and cleaned; one Telegram smoke summary was sent. No n8n workflow activation, production workflow mutation, Upbit call, Docker production restart, AWS mutation, credential value print, or secret output occurred.
- rollback: Revert this commit locally; on EC2 remove only the smoke queue item/backup and marker under `/home/ubuntu/workspace/true-autonomous-controller/runtime` if cleanup is requested.
- next_action: Import the inactive n8n SSH dispatch draft as inactive, sync current local scripts/schemas to EC2, then run one full dry-run E2E loop.

## 2026-05-18 14:35 KST - Phase 3 Runtime Orchestration Dry-Run
- request: Proceed through Phase 3 without stopping; all safe approvals granted, including bounded live smoke for n8n draft import, EC2 tmux, Telegram summary, and read-only n8n validation.
- files_changed: `workflows/inactive_hq_ssh_dispatch_draft_2026-05-18.json`, `docker/tac-runner.Dockerfile`, `scripts/remote_phase3_e2e_smoke.py`, `scripts/docker_isolated_runner_plan.py`, `scripts/hq_phase3_orchestrator.py`, `tests/test_phase3_runtime_orchestration_20260518.py`, `tests/test_hq_runtime_orchestration_20260518.py`, `reports/phase3_runtime_orchestration_completion_report_2026-05-18.md`, `reports/docker_isolated_runner_scaffold_2026-05-18.md`, `reports/hq_continuation_ledger_2026-05-18.json`, telemetry files.
- validation: PASS. n8n imported workflow `DoClguwa8aewVM8D` and left it inactive; draft webhook smoke returned `QUEUED_DRAFT`; EC2 Phase 3 E2E smoke `hq-phase3-e2e-smoke-20260518` passed; Telegram smoke task `tac-20260518052543-e86afda736` passed; full local tests 50/50 PASS; `python scripts/run_offline_validations.py` PASS.
- side_effects: Created one inactive n8n draft workflow; temporarily activated/deactivated that draft for webhook smoke; synced local scripts/schemas to EC2 bounded workspace; created and cleaned one scoped tmux dry-run session; sent one Telegram smoke summary. No production workflow left active, Upbit action, Instagram publish, Docker production restart, AWS mutation, credential value read, or secret output.
- rollback: Delete or keep inactive n8n workflow `DoClguwa8aewVM8D`; revert this commit locally; remove scoped EC2 dry-run artifacts under `/home/ubuntu/workspace/true-autonomous-controller/runtime` only if cleanup is requested.
- next_action: Build and run the Docker-isolated runner against a disposable workspace copy, then route selected Telegram commands into the new queue/tmux/reviewer path with the legacy controller route as fallback.

## 2026-05-18 15:40 KST - Phase 4 Bounded Runtime Route
- request: Approved remaining Phase 4 work after Phase 3; proceed without stopping on one blocked item.
- files_changed: `src/tac/service.py`, `src/tac/queue_runtime.py`, `workflows/tac_telegram_commands.json`, `scripts/docker_container_smoke.py`, `scripts/queue_soak_test.py`, `scripts/git_checkpoint_manifest.py`, `scripts/restart_tac_service_remote.sh`, `scripts/remote_queue_route_smoke.py`, `tests/*`, `reports/phase4_runtime_operating_report_2026-05-18.md`, ledger and telemetry files.
- validation: PASS. Local tests 55/55 PASS; offline validation runner PASS; Docker image `tac-codex-runner:dry-run` build PASS; disposable `--network none` container smoke PASS; EC2 `/queue` and `/handoff` smoke PASS; `tac-hq-runner` processed queue task `hq-live-queue-route-smoke-20260518063612` and wrote handoff/state/report.
- side_effects: Started local Docker Desktop; built local Docker image; ran one disposable local container; restarted scoped EC2 `tac-service`; patched active n8n `tac_telegram_commands` parser; started/reused EC2 `tac-hq-runner`; appended bounded queue smoke items. No Upbit action, Instagram publish, EC2 production Docker restart, AWS mutation, secret output, or force push.
- rollback: Revert this commit, restore prior `tac_telegram_commands` active version through n8n version history if needed, restart `tac-service`, and stop only `tac-hq-runner` if queue dispatch should pause.
- next_action: Install/run Codex inside the Docker runner without host secrets, then run user-origin Telegram `/queue smoke` from the Telegram app.

## 2026-05-18 16:30 KST - Company Mode Runtime And Completion Notification
- request: Finish remaining controller behavior so the user can tell Codex to act like a company with HQ and agents, queue work, leave the computer, and receive completion updates.
- files_changed: `docker/tac-runner.Dockerfile`, `scripts/hq_company_task_runner.py`, `scripts/hq_notify_completion.py`, `scripts/hq_safe_agent_wrapper_template.sh`, `scripts/hq_tmux_runner_template.sh`, `src/tac/queue_runtime.py`, `src/tac/service.py`, `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, schemas, tests, docs, reports, telemetry.
- validation: PASS. Local tests 59/59; offline validation PASS; local Docker Codex CLI smoke PASS; EC2 Docker Codex CLI smoke PASS; n8n notify webhook smoke PASS; EC2 queue -> tmux -> company wrapper -> handoff/state/report smoke PASS with notifier artifact.
- side_effects: Built Docker images locally and on EC2; restarted scoped EC2 `tac-service`; restarted scoped `tac-hq-runner`; patched active TAC n8n workflows. No Upbit action, Instagram publish, AWS mutation, secret output, production Docker restart, or force push.
- rollback: Revert this commit, restore prior active n8n versions, restart `tac-service`, and stop/restart only `tac-hq-runner`.
- next_action: User sends a real Telegram `/work smoke test...` message to validate the real chat-id completion notification path.

## 2026-05-19 KST - Autonomous Runtime Engine Buildout
- request: Continue building the autonomous runtime orchestration platform; store the major-task runtime rule; expand queue, state, n8n draft, Telegram ops contracts, reviewer/retry, telemetry, continuation, Instagram growth scaffolding, offline validation, reports, and Git hygiene.
- files_changed: `AGENTS.md`, `SESSION_BOOT.md`, `src/tac/runtime_engine.py`, `src/tac/queue_runtime.py`, `schemas/runtime_queue.schema.json`, `schemas/runtime_event.schema.json`, `runtime/queue/sample_task.json`, `telemetry/runtime_events.sample.jsonl`, `scripts/runtime_engine_smoke.py`, `scripts/hq_sqlite_queue_writer.py`, `scripts/run_offline_validations.py`, `workflows/inactive_hq_runtime_orchestration_pack_2026-05-19.json`, `reports/*2026-05-19.md`, `tests/test_runtime_engine_20260519.py`, and related ledger/telemetry files.
- validation: PASS. `python -m unittest discover -s tests` ran 66 tests; `python scripts/run_offline_validations.py` PASS; runtime engine smoke PASS; runtime event schema and inactive n8n runtime pack JSON parse PASS.
- side_effects: Local/offline only. No live SSH, Telegram send, Instagram publish, Upbit operation, production Docker restart, AWS mutation, credential read, secret output, or force push.
- rollback: Revert this commit to return to the previous company-mode runtime notification scaffold.
- next_action: Run a bounded 5-6 hour queue soak or apply the SNS growth experiment system to the Instagram automation workspace without live publishing.

## 2026-05-19 KST - YUNA Growth Brain HQ System
- request: User asked to use deep research, HQ and agents, 15-year SNS marketing strategy, and behavioral analysis to make the Instagram account brain stronger for followers and signups, with at least a serious extended work cycle.
- files_changed: `schemas/yuna_growth_experiment.schema.json`, `runtime/yuna_growth_experiments/sample_experiment.json`, `reports/yuna_brain_hq_agent_operating_model_2026-05-19.md`, `reports/yuna_brain_growth_system_2026-05-19.md`, `docs/YUNA_BRAIN_SENDOFF_2026-05-19.md`, `tests/test_yuna_growth_brain_20260519.py`, `scripts/run_offline_validations.py`, `reports/hq_continuation_ledger_2026-05-18.json`, telemetry files.
- validation: PASS. `python -m unittest discover -s tests` ran 71 tests; `python scripts/run_offline_validations.py` PASS; YUNA schema and sample JSON parse PASS.
- side_effects: Local/offline only. No live Instagram publishing, manual DM/comment send, credential read, production workflow mutation, AWS mutation, or secret output.
- rollback: Revert this patch to remove the YUNA growth brain system artifacts.
- next_action: Apply the YUNA brain sendoff to the SNS automation workspace so approval candidates show hook family, behavioral trigger, follow reason, comment CTA, save CTA, and success metric.

## YUNA_GROWTH_BRAIN_EXTERNAL_SNS_APPLY_20260519

- External SNS planning workspace patched and live `clean_01_generator` Build Simulation Content node deployed.
- Added YUNA growth brain candidate metadata, Telegram approval summary block, and validator assertions.
- Validation passed locally and deployment script reported PASS.
- Preview webhook returned HTTP 200, but n8n saved execution list did not yet show a fresh run after deploy.
- No Instagram publish, comment, DM, credential print, or production Docker restart was performed.

## ACTUAL05_YUNA_COMMENT_DM_ACTIVATED_20260519

- Confirmed `actual_05_instagram_comment_dm_opener` is live active in n8n.
- Confirmed active graph contains YUNA Deal Index scoring marker, public reply, private reply, and dedupe guard.
- Did not force a live Instagram comment/DM event; latest saved executions are prior webhook test runs.
- No credential value was printed.

## YUNA_PRODUCT_TAXONOMY_MIX_LIVE_20260522

- Applied and live-deployed YUNA product taxonomy mix to `clean_01_generator` Build Simulation Content.
- Categories: e-liquid, disposable device, disposable cartridge/pod, reusable device.
- Ratio: device 1 / e-liquid 10 / disposable device 7 / disposable cartridge 3.
- Local JS syntax and deployment validator passed.
- Live n8n active version confirmed: `7ddbeac2-ca84-4e50-8aa3-679fe5fdfc43`.
- Webhook returned HTTP 200, but saved execution list did not yet show a fresh post-deploy run.
- No Instagram publish, credential output, clean03/clean04 mutation, Docker/nginx/server mutation, or AWS mutation was performed.

## YUNA_INSTAGRAM_SESSION_HANDOFF_20260522

- Created `docs/YUNA_INSTAGRAM_SESSION_HANDOFF_2026-05-22.md`.
- Extracted YUNA/Instagram-only state from the current session: brand direction, workflow IDs, live versions, growth brain, taxonomy mix, reports, validation, known gaps, and exact next prompt.
- Documentation only; no n8n workflow, Instagram publish, credential, Docker, server, or AWS state changed.

## TAC_SCORECARD_AND_RUNTIME_HARDENING_20260522

- Created a 10-sector TAC readiness scorecard with strict external audit baseline `76/100`, local baseline `81/100`, and post-improvement repository/runtime readiness score `92/100`.
- Added root `README.md` with English, French, Spanish, Korean, and Chinese operator instructions.
- Stored the permanent five-language README policy in `AGENTS.md`, `SESSION_BOOT.md`, and `docs/TAC_OPERATOR_README_POLICY_2026-05-22.md`.
- Added `scripts/tac_scorecard.py`, `schemas/tac_scorecard.schema.json`, `reports/tac_scorecard_2026-05-22.*`, and `reports/tac_agent_council_review_2026-05-22.md`.
- Hardened queue writes with a local `.pending.lock` and SQLite `BEGIN IMMEDIATE`.
- Hardened tmux dequeue with `flock` or mkdir-lock fallback.
- Narrowed `/killall` service behavior to TAC tmux sessions and removed broad process-wide `pkill`.
- Disabled host Codex fallback by default and changed TAC service startup default sandbox to `workspace-write`.
- Added regression tests for scorecard, multilingual README policy, runner safety, queue locking, and updated the offline validation runner.
- Validation: PASS. `python -m unittest discover -s tests` ran 82 tests. `python scripts/run_offline_validations.py` PASS.
- Remaining gates: Docker-only Codex auth volume, 5-6 hour unattended soak, production n8n workflow maintenance, and Git auto-commit policy for arbitrary target workspaces.

## TAC_DOCKER_AUTH_AND_SOAK_STARTED_20260524

- Created and verified Docker-only Codex auth volume `tac-codex-auth` on EC2.
- Device auth completed inside the Docker volume; container `codex login status` reports ChatGPT login.
- Direct Docker Codex exec smoke returned `DOCKER_CODEX_AUTH_VOLUME_OK`.
- Queue preflight task `tac-soak-preflight3-20260524-000` completed PASS through `runner_result.runner = docker_codex`.
- Started 360-minute tmux soak session `tac-unattended-soak-20260524` with host Codex fallback disabled and Docker auth volume enabled.
- Evidence is written under `/home/ubuntu/workspace/true-autonomous-controller/runtime/soak`.
- Validation caveat: nested Docker Codex container cannot run Docker/tmux itself and has limited write access to ubuntu-owned workspace paths; host runner records authoritative soak artifacts.

## TAC_UNATTENDED_SOAK_FINAL_PASS_20260525

- Checked EC2 final soak artifacts for `tac-unattended-soak-20260524`.
- Final status: PASS.
- Duration: 360 minutes, heartbeat reached 21600.83 seconds.
- Enqueued soak tasks: 18.
- Soak task reports PASS: 18/18.
- Soak task reports FAIL: 0/18.
- Docker-only Codex auth volume remained active, and host Codex fallback stayed disabled.
- The prior `failed=3` queue count was cumulative from older preflight failures; no `tac-unattended-soak-20260524` entries appeared in `runtime/queue/failed.jsonl`.
- Conclusion: Docker-only Codex execution and 5-6 hour unattended soak hardening gates are now closed by runtime evidence.

## TAC_MULTI_PROJECT_COMPANY_ONBOARDING_20260525

- Created `scripts/create_bounded_workspace_archive.py` and tests to package project workspaces without secret-like files or heavy generated directories.
- Synced SNS automation as a bounded EC2 workspace and queued TAC company-mode tasks for Upbit, SNS/Instagram, flight-deal discovery, and TAC portfolio registry.
- Fixed `scripts/hq_company_task_runner.py` so queued safe local/offline work is treated as already approved and must not stop at approval-only planning.
- Added Docker `--group-add` workspace group propagation so the non-root container user can write inside ubuntu-owned bounded workspaces.
- Added tests: `tests/test_company_runner_prompt_20260525.py` and `tests/test_bounded_workspace_archive_20260525.py`.
- Generated `reports/tac_multi_project_onboarding_2026-05-25.md` and `reports/hq_portfolio_registry_2026-05-25.md`.
- Validation: targeted local tests PASS; EC2 targeted tests PASS; EC2 Docker write probes PASS for TAC, SNS, and Upbit bounded workspaces; Upbit/SNS/flight TAC queue tasks completed PASS; deterministic TAC portfolio registry generated PASS after the Codex portfolio run timed out.
- Side effects: EC2 bounded SNS workspace was created from a secret-excluding archive. No Upbit exchange action, Instagram publish, production n8n activation, production restart, AWS mutation, credential value read/output, or force push occurred.

## WORLDVAPE_GWANGWOON_DAILY_GROWTH_ROUTINE_20260525

- Created a TAC daily growth operating routine for 월드베이프 광운대점 Instagram/SNS.
- Added `schemas/worldvape_daily_growth_routine.schema.json`, `runtime/worldvape_growth/sample_daily_routine.json`, `scripts/worldvape_daily_growth_task_builder.py`, and `workflows/inactive_worldvape_daily_growth_ops_2026-05-25.json`.
- Added operator artifacts: `reports/worldvape_gwangwoon_daily_growth_ops_2026-05-25.md` and `docs/WORLDVAPE_GWANGWOON_GROWTH_SENDOFF_2026-05-25.md`.
- Added regression tests in `tests/test_worldvape_daily_growth_ops_20260525.py` and expanded `scripts/run_offline_validations.py`.
- The routine covers daily metrics review, competitor pattern notes, four YUNA candidates, behavioral ranking, Telegram approval packaging, and learning memory.
- Live gates remain deferred: Instagram publish, credentialed metric fetch, live competitor scraping, n8n activation, and production restart.
- No live Instagram publish, credential read, n8n activation, production restart, AWS mutation, or external scraping was performed.
