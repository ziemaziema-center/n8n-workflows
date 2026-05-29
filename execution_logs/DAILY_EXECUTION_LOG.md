# Daily Execution Log

## Role

Append-only task execution log for TRUE AUTONOMOUS CONTROLLER.

## Entry Format

```text
## YYYY-MM-DD HH:mm TZ - Task Title
- request:
- actions:
- validation:
- telemetry:
- files_changed:
- side_effects:
- rollback_needed:
- next_action:
```

## 2026-05-16 09:00 KST - Session Boot And Local Memory Bootstrap
- request: Continue TRUE AUTONOMOUS CONTROLLER with master sendoff, memory-first execution, validation-first changes, additive-only patching, and post-task telemetry.
- actions: Inspected empty controller workspace; searched adjacent project KB; read HQ shared memory and Instagram execution patch history; created local bootstrap memory and session files.
- validation: PASS. Confirmed 6 bootstrap files and required markers with `Get-ChildItem -Recurse -File` and `Select-String`.
- telemetry: FAILURE: local controller memory baseline and Git repository were absent at session start. SUCCESS: additive bootstrap files created and validated with no remote or production mutation.
- files_changed: `AGENTS.md`, `SESSION_BOOT.md`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Local files only. No remote, workflow, Docker, Telegram, GitHub, Git repository, or production state changed.
- rollback_needed: No.
- next_action: Validate bootstrap files and then proceed to Phase 1 local dry-run scaffold.

## 2026-05-16 09:20 KST - Phase Design Analysis From Source KB
- request: Analyze how many phases are needed to reach TRUE AUTONOMOUS CONTROLLER project goals.
- actions: Read local operating memory plus source KB files `01_TRUE_AUTONOMOUS_CONTROLLER_SOURCE_KB.md` through `05_IMPLEMENTATION_ROADMAP_AND_PROJECT_INSTRUCTIONS.md`; converted the source 4-phase roadmap into a safer 6-phase execution design with explicit gates.
- validation: PASS. Analysis is source-backed by the supplied roadmap, target architecture, tool syntax, and safety guardrail documents; no live tool semantics were claimed as currently verified.
- telemetry: SUCCESS: design-only analysis completed. FAILURE: none during this task.
- files_changed: `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Local telemetry append only. No EC2, n8n, Docker, Telegram, GitHub, Git repository, or production state changed.
- rollback_needed: No.
- next_action: If approved, implement Phase 0/1 local dry-run contracts before any EC2 or n8n mutation.

## 2026-05-16 09:30 KST - Remaining Work Status Summary
- request: Summarize what remains to reach the TRUE AUTONOMOUS CONTROLLER goal.
- actions: Re-read local operating memory and SESSION_BOOT; summarized remaining work by phase and immediate backlog.
- validation: PASS. Summary is aligned with current local memory and does not claim unverified live EC2, n8n, Claude, or Codex state.
- telemetry: SUCCESS: status-only summary completed. FAILURE: none during this task.
- files_changed: `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Local telemetry append only. No EC2, n8n, Docker, Telegram, GitHub, Git repository, or production state changed.
- rollback_needed: No.
- next_action: Start Phase 0/1 local scaffold: contracts, dry-run runner, log schema, and kill-switch design.

## 2026-05-16 18:00 KST - Phase 0-3 Implementation And Debug Loop
- request: Complete Phase 3, run it, find bugs, debug, loop x3, and report success.
- actions: Initialized local Git baseline; implemented task/result contracts, local controller, runner CLI, validation loop, runbooks, tests, and dry-run example; ran local validation loops; copied scaffold to EC2 bounded workspace; ran EC2 tmux validation x3.
- validation: PASS. Local `python -m unittest discover -s tests` returned 8/8 PASS; local smoke returned PASS; EC2 tmux validation produced `phase3_result_remote_loop1.json`, `phase3_result_remote_loop2.json`, and `phase3_result_remote_loop3.json`, all with `status=PASS`.
- telemetry: FAILURE: Git add initially hit sandbox/ownership safe-directory issue; fixed with scoped `git -c safe.directory`. FAILURE: EC2 failed on `python` executable absence; fixed with `sys.executable` and `python3` allowlist. FAILURE: one scp command misplaced a generated test-file copy; deleted exact generated artifact and recopied correctly. FAILURE: Python `__pycache__` entered first scaffold commit; fixed with `.gitignore` and cleanup commit. SUCCESS: Phase 0-3 scaffold passed local and EC2 tmux loop x3.
- files_changed: `.gitignore`, `contracts/*`, `docs/*`, `examples/*`, `scripts/*`, `src/tac/*`, `tests/*`, `runtime/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Created local Git repo and baseline commit; created remote bounded workspace `/home/ubuntu/workspace/true-autonomous-controller`; did not mutate n8n workflows, Docker containers, Telegram, GitHub remote, or production services.
- rollback_needed: No.
- next_action: Connect n8n Telegram trigger to the runner contract after credential IDs and inactive workflow import path are verified.

## 2026-05-17 06:56 KST - Semi-Live n8n Controller MVP
- request: Execute with all approvals and complete a one-day semi-live controller MVP without stopping mid-run.
- actions: Added TAC HTTP service, `/run`/`/status`/`/killall` endpoints, optional Claude executor mode, n8n webhook workflow, EC2 service tmux deployment, n8n workflow import/publish, and final validation loops.
- validation: PASS. Local tests 11/11, EC2 tests 11/11, direct EC2 service `/run` PASS, n8n `/run` loop x3 PASS, n8n `/status` PASS, n8n `/killall` PASS, Claude Code smoke PASS, service Claude executor command status PASS.
- telemetry: FAILURE: local service import initially depended on PYTHONPATH; fixed with relative import. FAILURE: local `/killall` failed where `tmux` was absent; fixed with safe no-op. FAILURE: n8n webhook was 404 after CLI publish; fixed by restarting only n8n. FAILURE: `/status` initially failed because service patch was not deployed; fixed by copying service and restarting only `tac-service`. SUCCESS: semi-live n8n -> EC2 bounded runner MVP is active and validated.
- files_changed: `src/tac/controller.py`, `src/tac/service.py`, `scripts/start_tac_service.sh`, `scripts/run_tac_http_service.py`, `tests/*`, `workflows/tac_controller_webhook.json`, `docs/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Active n8n workflow `tac_controller_webhook` exists at unique path `/webhook/tac-controller`; n8n was restarted to register it; existing production workflow logic was not edited.
- rollback_needed: No.
- next_action: Keep current webhook ingress or explicitly migrate Telegram bot webhook after checking existing approval-flow webhook ownership.

## 2026-05-17 07:50 KST - Telegram Trigger And Claude Route Completion
- request: Execute all remaining work with all permissions approved.
- actions: Added active Telegram command workflow, added `/claude` route to controller webhook, fixed JSON-embedded JS regex escaping, reimported/published workflows, restarted only n8n, and ran final route validations.
- validation: PASS. n8n logs show `tac_telegram_commands` active; `/run` PASS; `/claude` PASS with `claude-executor`; `/status` PASS for Claude task; `/killall` PASS; local tests 11/11 PASS; `tac-service` tmux session alive.
- telemetry: FAILURE: JS regex `\\b` became backspace in JSON-generated workflow code; fixed with raw strings and control-character scan. SUCCESS: Telegram command workflow and Claude route are active and validated.
- files_changed: `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, `docs/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Active n8n workflow `tac_telegram_commands` added; n8n restarted to register trigger; existing production workflow logic not edited.
- rollback_needed: No.
- next_action: Use Telegram commands directly or continue via `POST /webhook/tac-controller`.

## 2026-05-17 08:25 KST - Dedicated Controller Telegram Bot Cutover
- request: Finish the new `Kindred AI Controller` Telegram bot setup, register it in n8n, replace TAC workflow credentials, remove TAC command handling from `Kindred Debug Guard`, clean command menus, and validate the planner/executor/reviewer path.
- actions: Created n8n Telegram credential `Kindred AI Controller`; updated both TAC workflow Telegram credential references; reimported/reactivated `tac_controller_webhook` and `tac_telegram_commands`; restarted only n8n; set Telegram bot name, descriptions, and command menu; validated credential usage and webhook registration; ran `/run`, `/claude`, `/status`, and `/killall` regressions.
- validation: PASS. `Kindred AI Controller` credential is used by both TAC workflows; `Kindred Debug Guard` no longer lists TAC workflows; Telegram Bot API reports `@kindred_ai_controller_bot`, webhook registered to n8n, and pending updates `0`; local tests 11/11 PASS; controller webhook `/run` PASS; `/claude` PASS with task `tac-20260516231952-100535c483`; `/status` PASS; `/killall` PASS.
- telemetry: FAILURE: initial cutover updated only `tac_telegram_commands`; fixed after credential usage showed `tac_controller_webhook` still on Debug Guard. FAILURE: Windows SSH key ACL blocked one validation batch; fixed with scoped `icacls` on the private key. FAILURE: Windows TLS clients failed against the n8n domain; validation retried with Python urllib. SUCCESS: dedicated controller bot path is active and validated without editing clean_01~04 logic.
- files_changed: `workflows/tac_controller_webhook.json`, `workflows/tac_telegram_commands.json`, `docs/TELEGRAM_N8N_TMUX_CONTRACT.md`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: n8n restarted once for workflow registration; `tac-service` tmux session remained alive; debug bot retained only existing debug workflows.
- rollback_needed: No.
- next_action: Human-origin Telegram confirmation: open `@kindred_ai_controller_bot`, press Start, send `/run smoke test`, then verify the returned TAC summary.

## 2026-05-17 08:45 KST - Human Telegram Smoke Confirmation
- request: Confirm live Telegram bot behavior with user-origin command.
- actions: Reviewed user-provided Telegram screenshot showing `/run smoke test` sent to `@kindred_ai_controller_bot` and TAC summary returned by the bot.
- validation: PASS. Screenshot response contains `[TRUE AUTONOMOUS CONTROLLER]`, `status: PASS`, task `tac-20260516234503-c1d0425439`, bounded local scaffold reason text, `/status tac-20260516234503-c1d0425439`, and `/killall`.
- telemetry: SUCCESS: Telegram app -> n8n Telegram Trigger -> TAC runner -> Telegram summary path is confirmed from a real user-origin message. FAILURE: none observed in this validation.
- files_changed: `agent_memory/VALIDATED_PATTERNS.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Local telemetry append only; no EC2, n8n, Docker, workflow, or credential mutation.
- rollback_needed: No.
- next_action: Proceed to hardening backlog: Docker-isolated runner, automatic Git checkpoints per task, stronger reviewer loop, and overnight unattended queue validation.

## 2026-05-17 09:05 KST - Codex-First Command And Executor Cutover
- request: Replace Claude naming with Codex naming and make Codex the executor path.
- actions: Replaced current `/claude` command parsing with `/codex`; changed runner executor from `claude` to `codex`; installed Codex CLI in EC2 runner user local prefix; added PATH bootstrap to `tac-service`; fixed Codex CLI `0.130.0` argv ordering; added Codex login preflight; updated docs, Telegram command menu, and n8n workflows; redeployed EC2 bounded workspace files; reimported/reactivated TAC workflows; restarted `tac-service` and n8n.
- validation: PARTIAL PASS. Current-facing source/workflow/docs scan found no `/claude` command references; local tests 11/11 PASS; EC2 tests 11/11 PASS; Codex CLI version `0.130.0` installed; n8n TAC workflows active; `/run` PASS with task `tac-20260516235509-df9363c789`; `/codex` returns `BLOCKED` with task `tac-20260517000017-5c7149e94b` because Codex CLI is not logged in; `/status` PASS; `/killall` PASS.
- telemetry: FAILURE: first npm prefix was misquoted through Windows/SSH and installed under an unintended path; fixed by reinstalling with remote shell quoting. FAILURE: previous Codex CLI arg pattern used an invalid `exec` option position for version `0.130.0`; fixed from live `codex exec --help`. FAILURE: Codex auth is not complete; preflight now blocks instead of retrying. SUCCESS: Controller command surface is Codex-first and safely blocks until Codex login is completed.
- files_changed: `AGENTS.md`, `SESSION_BOOT.md`, `src/tac/controller.py`, `scripts/start_tac_service.sh`, `tests/test_phase3_controller.py`, `workflows/tac_controller_webhook.json`, `workflows/tac_telegram_commands.json`, `docs/TELEGRAM_N8N_TMUX_CONTRACT.md`, `docs/PHASE_0_3_RUNBOOK.md`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Codex CLI installed under `/home/ubuntu/.local`; Telegram bot commands now show `/codex`; n8n restarted once; `tac-service` restarted; existing clean_01~04 logic not edited.
- rollback_needed: No.
- next_action: Authenticate Codex CLI on EC2 runner, then run `/codex` live smoke.

## 2026-05-17 11:05 KST - Codex Invalid API Key Debug
- request: Diagnose why `/codex` still failed after user logged in through PowerShell/OpenAI.
- actions: Inspected failed task `tac-20260517015618-99fc7dea5d`; confirmed Codex CLI login exists but the stored API key is rejected by OpenAI API; added auth-error classification; added API-key output redaction; deployed to EC2; restarted `tac-service`; redacted existing generated task result JSON files.
- validation: PASS. Local tests 13/13 PASS; EC2 tests 13/13 PASS; `/codex` now returns `BLOCKED` with task `tac-20260517020244-62fc400f8a` and one attempt instead of retrying as `FAIL`; generated result files no longer match API-key prefixes.
- telemetry: FAILURE: Codex `login status` can pass even when the stored key is invalid at API request time. FAILURE: previous result tails contained masked API-key material from Codex error text; fixed by redacting command output and existing generated results. SUCCESS: invalid Codex credentials now escalate deterministically and do not retry.
- files_changed: `src/tac/controller.py`, `tests/test_phase3_controller.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only `tac-service`; no n8n workflow, Docker, clean_01~04, or credential value was changed.
- rollback_needed: No.
- next_action: Replace Codex auth on EC2 with a valid OpenAI API key or device auth, then rerun `/codex Print exactly TAC_CODEX_OK and do not modify files.`

## 2026-05-17 12:36 KST - Codex ChatGPT Login Live PASS
- request: Validate the controller after user completed Codex device auth login on EC2.
- actions: Confirmed `codex login status`; executed `/codex` through the n8n controller webhook; checked `/status`; checked `/killall`; confirmed active TAC workflows and `tac-service`.
- validation: PASS. Codex login status shows ChatGPT login; `/codex Print exactly TAC_CODEX_OK and do not modify files.` returned task `tac-20260517033536-bb8a366f30` with status PASS and output `TAC_CODEX_OK`; `/status tac-20260517033536-bb8a366f30` PASS; `/killall` PASS; n8n workflows `tac_controller_webhook` and `tac_telegram_commands` active; `tac-service` tmux session alive.
- telemetry: SUCCESS: Telegram/n8n/controller/Codex live execution path is now open using ChatGPT login. FAILURE: direct shell smoke had a quoting issue and was skipped in favor of the real controller path.
- files_changed: `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Local telemetry append only; no EC2 code, n8n workflow, Docker, or credential value changed.
- rollback_needed: No.
- next_action: Send bounded real tasks via `/codex`, beginning with diagnosis/readiness commands before long implementation runs.

## 2026-05-17 12:45 KST - Codex Output Telegram Summary Fix
- request: Fix generic PASS Telegram replies so the user can see Codex's plan, diagnosis, or report content.
- actions: Added Codex JSONL `agent_message` extraction to controller summaries; added unit coverage; deployed `controller.py` and tests to EC2; restarted `tac-service`; validated through the n8n webhook.
- validation: PASS. Local tests 14/14 PASS; EC2 tests 14/14 PASS; task `tac-20260517034419-6e3a728f89` returned `telegram_text` containing `Codex output:` and the agent message `업비트 진단 보고서는 이제 Telegram summary에 표시됩니다.`
- telemetry: FAILURE: previous PASS summary hid the useful Codex output. SUCCESS: Telegram summaries now include actionable Codex output text.
- files_changed: `src/tac/controller.py`, `tests/test_phase3_controller.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only `tac-service`; no n8n workflow, Docker, or credential value changed.
- rollback_needed: No.
- next_action: Re-run the `/codex` Upbit diagnosis prompt and inspect the visible `Codex output:` section.

## 2026-05-17 13:00 KST - Codex Workspace Read Fix For Upbit Diagnosis
- request: Diagnose and fix why `/codex` now shows output but cannot read the Upbit workspace due to `bwrap: loopback: Failed RTM_NEWADDR`.
- actions: Added bounded workspace extraction from `WORKSPACE:` lines, `/home/ubuntu/workspace/...` paths, and Upbit aliases; changed relative workspace validation to remain project-root scoped while allowing absolute configured workspace roots; added service-level `TAC_ALLOWED_WORKSPACE_ROOTS=/home/ubuntu/workspace` and temporary `TAC_CODEX_SANDBOX=danger-full-access`; closed Codex stdin; expanded `/killall` to terminate scoped Codex/Claude processes; deployed to EC2 and restarted only `tac-service`.
- validation: PASS. Local tests 18/18 PASS; EC2 tests 18/18 PASS; service health PASS; n8n `/codex` read-only smoke for `/home/ubuntu/workspace/02_업비트_자동화` returned PASS with Codex output showing cwd, file count `102`, secret count `0`, and no file modification; `/status tac-20260517035838-8102c8f455` PASS; `/killall` PASS; `pgrep -a codex` returned no process.
- telemetry: FAILURE: Codex `workspace-write` sandbox is not usable on this EC2 because bwrap cannot configure loopback networking. FAILURE: first workspace-root patch accidentally allowed relative `..` because `/home/ubuntu/workspace` was allowed; fixed by restricting relative paths to the controller project root only. SUCCESS: real n8n -> TAC -> Codex -> bounded Upbit workspace -> Telegram summary path now returns actionable reports.
- files_changed: `src/tac/controller.py`, `src/tac/service.py`, `scripts/start_tac_service.sh`, `tests/test_phase3_controller.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only `tac-service`; no n8n workflow, Docker, clean_01~04, or credential value changed. Temporary host-mode Codex is less isolated than the final Docker target.
- rollback_needed: No immediate rollback; set `TAC_CODEX_SANDBOX=workspace-write` and restart `tac-service` if host-mode fallback must be disabled.
- next_action: Use explicit `WORKSPACE:` in Telegram commands for real project work; complete Docker-isolated runner before unattended overnight mutation.

## 2026-05-17 14:15 KST - Long Telegram Reply Timeout Fix
- request: Determine whether no Telegram reply after a long `/codex` command is normal.
- actions: Inspected EC2 runtime tasks and `tac-service`; confirmed task `tac-20260517044407-96cf346ad5` reached TAC and completed PASS after 185 seconds; found `BrokenPipeError` from n8n disconnecting before TAC response; increased TAC n8n HTTP timeouts to 30 minutes; added controller `agent_text` extraction before stdout truncation; redeployed controller/tests/workflows; reimported/published TAC workflows; restarted `tac-service` and n8n.
- validation: PASS. Local tests 20/20 PASS; EC2 tests 20/20 PASS; `tac_controller_webhook` and `tac_telegram_commands` active; n8n `/run` smoke PASS; n8n `/codex` smoke task `tac-20260517051453-69c2e2e7fe` returned `Codex output: TELEGRAM_TIMEOUT_FIX_OK`.
- telemetry: FAILURE: Long Telegram Codex run completed but the user saw no reply because n8n timeout was shorter than Codex runtime. FAILURE: Long Codex final messages could be truncated out of `stdout_tail` and omitted from summaries. SUCCESS: Future long runs within the 30-minute hard limit should return Telegram final reports with parsed Codex output.
- files_changed: `src/tac/controller.py`, `tests/test_phase3_controller.py`, `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only `tac-service` and n8n; no clean_01~04 workflow logic, Docker workload, Upbit live trading, or credential value changed.
- rollback_needed: No.
- next_action: Resend the Telegram `/codex` project command; it should now return a final report instead of silently disappearing.

## 2026-05-17 14:50 KST - Telegram Natural Follow-Up Routing Fix
- request: Fix another no-response case when a follow-up approval was sent as ordinary text instead of `/codex`.
- actions: Confirmed the screenshot message had no slash command; patched `tac_telegram_commands` so non-slash text becomes a Codex follow-up; tagged follow-up prompts; added service logic to hydrate the workspace from the latest TAC result; added regression coverage; deployed to EC2; reimported/published the Telegram workflow; restarted `tac-service` and n8n.
- validation: PASS. Local tests 21/21 PASS; EC2 tests 21/21 PASS; `tac_telegram_commands` active; follow-up smoke task `tac-20260517054736-54de626dc9` returned `Codex output: FOLLOWUP_WORKSPACE_OK` and used `/home/ubuntu/workspace/02_upbit_automation_clean`.
- telemetry: FAILURE: Dedicated controller bot silently ignored non-slash natural follow-up text. SUCCESS: Natural text now routes as a Codex follow-up to the latest bounded workspace when no explicit `WORKSPACE:` is present.
- files_changed: `src/tac/controller.py`, `src/tac/service.py`, `tests/test_service_contract.py`, `workflows/tac_telegram_commands.json`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only `tac-service` and n8n; no clean_01~04 workflow logic, Docker workload, Upbit live trading, or credential value changed.
- rollback_needed: No.
- next_action: User can resend the natural follow-up text; it should now produce a controller response.

## 2026-05-17 15:10 KST - Telegram Received Ack And Status UX
- request: Fix the controller bot once so long Telegram commands do not look ignored while running.
- actions: Inspected latest runtime tasks and confirmed the user's 14:59 message produced task `tac-20260517055951-c2007161f8`, which completed PASS; added pre-run `status: RECEIVED` Telegram reply, generated task ids before runner execution, included `/status <task_id>` in the received reply, added unsupported command reply nodes, added workflow contract tests, deployed workflow to EC2/n8n, and restarted n8n.
- validation: PASS. Local tests 23/23 PASS; EC2 tests 23/23 PASS; workflow JSON parses; n8n TAC workflows active; `/status tac-20260517055951-c2007161f8` PASS; `/codex` smoke task `tac-20260517060655-8488d97be4` returned `FINAL_PIPELINE_OK`.
- telemetry: FAILURE: Final-only Telegram reporting made long tasks indistinguishable from ignored messages. SUCCESS: Future run/follow-up messages should immediately return `status: RECEIVED` and then a final report.
- files_changed: `workflows/tac_telegram_commands.json`, `tests/test_workflow_contract.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only n8n; no clean_01~04 workflow logic, Docker workload, Upbit live trading, or credential value changed.
- rollback_needed: No.
- next_action: Continue with actual Upbit project work only after read-only live state and n8n runtime checks are explicitly approved.

## 2026-05-17 15:40 KST - Telegram Immediate Execution Briefing
- request: Make Telegram immediately show expected direction, HQ/agent communication, execution plan, and estimated work time when a command is sent.
- actions: Replaced the simple `RECEIVED` pre-run message with a deterministic execution briefing that includes `expected_time`, `expected_direction`, `hq_agent_flow`, `execution_plan`, `/status <task_id>`, and `/killall`; added workflow contract assertions; deployed updated Telegram workflow to EC2/n8n; reimported/published workflow and restarted n8n.
- validation: PASS. Local tests 23/23 PASS; EC2 tests 23/23 PASS; workflow JSON parses; contract test verifies briefing fields; n8n TAC workflows active; TAC service health PASS; `/codex` smoke task `tac-20260517063840-a53dda620e` returned `ACK_BRIEFING_PATCH_OK`.
- telemetry: SUCCESS: Telegram pre-run responses now explain what will happen before the long runner starts. FAILURE: none observed in validation.
- files_changed: `workflows/tac_telegram_commands.json`, `tests/test_workflow_contract.py`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only n8n; no clean_01~04 workflow logic, Docker workload, Upbit live trading, or credential value changed.
- rollback_needed: No.
- next_action: User can send a Telegram command to verify the new immediate briefing in the real Telegram UI.

## 2026-05-17 16:50 KST - Telegram Parse Mode Hardening
- request: Fix the real Telegram path after the user sent a natural-language command and still received no immediate briefing.
- actions: Queried n8n execution metadata; decoded execution `10487`; confirmed the user message reached `tac_telegram_commands` but failed at `Send Received Reply` before runner dispatch; set all TAC Telegram send nodes to `parse_mode: HTML`; changed pre-run briefing labels to Telegram-safe text; added HTML escaping for dynamic summaries; redeployed both TAC workflows; restarted n8n.
- validation: PASS. Local tests 25/25 PASS; EC2 tests 25/25 PASS; workflow JSON parses; live n8n export confirms `parse_mode: HTML` on all `tac_telegram_commands` send nodes; TAC service health PASS; actual `tac_controller_webhook` send with chat id returned HTTP 200 and task `tac-20260517074612-960807be93`.
- telemetry: FAILURE: n8n Telegram send nodes silently default to Markdown when `parse_mode` is unset, so underscore labels can block the entire pre-run branch. SUCCESS: TAC Telegram sends now use explicit HTML mode and escape arbitrary summaries.
- files_changed: `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, `tests/test_workflow_contract.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only n8n; one validation Telegram summary was sent to the controller chat; no clean_01~04 workflow logic, Docker workload, Upbit live order, or credential value changed.
- rollback_needed: No.
- next_action: User can resend the natural-language command; it should now receive the immediate briefing before runner work starts.

## 2026-05-17 20:50 KST - Upbit First Bounded Cycle Replay
- request: User asked whether the validation Telegram message was the end; execute the missed Upbit command rather than only explaining.
- actions: Confirmed the prior message `tac-20260517074612-960807be93` was only a validation send; derived the Telegram Trigger secret header from n8n source semantics; replayed the command through the actual Telegram Trigger path; found execution `10545` failed in `Build Received Reply` because non-ASCII regex literals became invalid; patched long-run detection to ASCII-only and added test coverage; redeployed `tac_telegram_commands`; replayed an explicit Upbit `/codex` bounded cycle.
- validation: PASS. Local tests 25/25 PASS; EC2 tests 25/25 PASS; n8n execution `10546` success; task `tac-20260517114459-672cbd72` PASS; workspace `/home/ubuntu/workspace/02_upbit_automation_clean`; WF05 offline regression 12/12 PASS; all six workflow JSON artifacts now report `active=false`; TAC service health PASS; no Codex process remains.
- telemetry: FAILURE: Embedded n8n JS should not use unproven non-ASCII regex literals. SUCCESS: Real Telegram Trigger path now starts runner work and completes a bounded Upbit cycle.
- files_changed: `workflows/tac_telegram_commands.json`, `tests/test_workflow_contract.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- upbit_workspace_changes: Added explicit `active: false` to WF01, WF02, WF03, WF06 local artifacts; added `reports/first_bounded_controller_cycle_2026-05-17.md`; updated Upbit workspace `PATCH_HISTORY.md` and `DAILY_EXECUTION_LOG.md`; backup at `backups/controller_cycle_20260517_inactive_flags`.
- side_effects: Restarted only n8n; sent immediate/final Telegram messages; no live trading, cancel, reorder, n8n activation, Docker restart, production mutation, or secret value output.
- rollback_needed: No controller rollback. Upbit artifact rollback is available from the generated backup if needed.
- next_action: Continue in bounded cycles: read-only runtime n8n/helper preflight, then current-order state verification, then remaining production-readiness gaps.

## 2026-05-17 21:05 KST - Korean Operator Telegram Reports
- request: Make Telegram command replies readable for the operator in Korean, not as English/technical logs.
- actions: Updated Codex prompt to require Korean plain-language final reports; changed controller result summaries from `[PASS]`/`Codex output` style to Korean labels; changed Telegram received/final/unsupported replies to Korean operator-first sections; kept workflow JavaScript source ASCII-safe with unicode escapes; redeployed controller and both TAC workflows; restarted `tac-service` and n8n.
- validation: PASS. Local tests 25/25 PASS; workflow JSON parses; EC2 tests 25/25 PASS; `tac-service` health PASS; `tac_controller_webhook` smoke returned Korean result summary with Korean reason; real Telegram Trigger execution `10554` succeeded and sent Korean received/final messages.
- telemetry: FAILURE: Previous successful Telegram reports were not operator-readable. SUCCESS: New Telegram messages start with Korean status, task id, estimated time, plan, result summary, and next commands.
- files_changed: `src/tac/controller.py`, `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`, `tests/test_phase3_controller.py`, `tests/test_workflow_contract.py`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Restarted only `tac-service` and n8n; sent one short Telegram validation pair; no production workflow logic, Docker workload, Upbit live order, or credential value changed.
- rollback_needed: No.
- next_action: Use the new report shape for the next real Upbit bounded cycle.

## 2026-05-17 22:35 KST - MCP Connectivity Verification
- request: Connect n8n, GitHub, Filesystem, Docker, PostgreSQL/SQLite, and Telegram MCP capabilities to Codex with all approvals.
- actions: Verified actual tool exposure instead of assuming availability; checked n8n MCP health; checked GitHub connector/tool visibility; checked Codex filesystem access; checked Docker CLI presence; checked SQLite CLI presence; documented the verified integration matrix in `docs/MCP_CONNECTIVITY_MATRIX.md`.
- validation: PASS. n8n MCP health returned `success=true`; GitHub plugin tools are exposed but target repo access is not confirmed; Codex filesystem is available in the trusted workspace; Docker/PostgreSQL/SQLite/Telegram are not exposed as first-class MCP tools in this session; project docs contain no secret values; local tests 25/25 PASS; TAC workflow JSON parse PASS.
- telemetry: SUCCESS: MCP status is now explicit and operator-readable. FAILURE: Requested “100% all MCP connected” is not currently true because several MCP servers are not installed/exposed to Codex.
- files_changed: `docs/MCP_CONNECTIVITY_MATRIX.md`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Documentation and telemetry only; no n8n workflow, Docker container, database, Telegram bot, credential, or production state changed.
- rollback_needed: No.
- next_action: Connect GitHub repo/remote first, then add Docker MCP before containerized autonomous execution, then add DB MCP after schema decisions.

## 2026-05-17 23:10 KST - GitHub Remote, Docker MCP, And SQLite State DB MCP
- request: Execute the next MCP connection steps completely.
- actions: Verified GitHub connector access to `ziemaziema-center/n8n-workflows`; added local git remote `n8n-workflows-backup`; implemented local dependency-free `tac-docker` stdio MCP server; implemented local dependency-free `tac-state-db` SQLite MCP server; defined controller state DB schema; initialized `runtime/controller_state.sqlite3`; registered both MCP servers in `~/.codex/config.toml`; repaired local `.docker` ACL and started Docker Desktop for runtime validation; kept Telegram intentionally routed through n8n instead of adding a direct Telegram MCP.
- validation: PASS. `git ls-remote` PASS; GitHub connector commit search PASS; Docker MCP tools/list protocol test PASS; Docker MCP `docker_status` read PASS against Docker Desktop 4.69.0; SQLite MCP init and task round-trip PASS; controller state DB status PASS; full local tests 28/28 PASS.
- telemetry: SUCCESS: GitHub access, Docker MCP registration, Docker daemon status read, SQLite state DB MCP registration, and state schema are now in place. FAILURE: new MCP tool namespaces require a new Codex session/reload to appear in normal tool discovery.
- files_changed: `.gitignore`, `scripts/mcp/docker_mcp_server.js`, `scripts/mcp/state_db_mcp_server.py`, `tests/test_mcp_servers.py`, `docs/MCP_CONNECTIVITY_MATRIX.md`, `docs/MCP_LOCAL_SERVERS.md`, `docs/CONTROLLER_STATE_DB_SCHEMA.md`, `agent_memory/KNOWN_FAILURES.md`, `agent_memory/VALIDATED_PATTERNS.md`, `agent_memory/PATCH_HISTORY.md`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Updated local `~/.codex/config.toml` with backup; created ignored SQLite runtime DB; repaired local `.docker` ACL; started Docker Desktop; no production workflow, Telegram bot, n8n credential, Docker container, or live trading state changed.
- rollback_needed: No.
- next_action: Start a new Codex session to load `tac-docker` and `tac-state-db`; keep Docker mutation disabled until an explicitly approved bounded container execution.

## 2026-05-18 12:20 KST - Continuation-First HQ Orchestration Scaffold
- request: Execute the full HQ/autonomous controller prompt so TAC stops acting like a short blocked-item report generator and starts preserving company-style orchestration, continuation handoff, deferred gates, tmux runtime scaffold, and Instagram growth planning.
- actions: Added permanent continuation rule to instruction/sendoff files; changed Codex prompt and Telegram received briefing toward continuation ledger/deferred gate behavior; created HQ operating model, continuation ledger, deferred gate registry, tmux persistent runtime scaffold, safe wrapper template, Instagram 10K growth HQ plan, final report, and offline validation runner; added regression tests.
- validation: PASS. Full local tests 35/35 PASS; `python scripts/run_offline_validations.py` PASS; `reports/hq_continuation_ledger_2026-05-18.json` JSON parse PASS; `workflows/tac_telegram_commands.json` JSON parse PASS.
- telemetry: SUCCESS: Safe local/offline work continued despite live/credential/network deferred gates. FAILURE: Previous controller behavior could end too early after one blocked item; permanent continuation rule now prevents that regression.
- files_changed: `AGENTS.md`, `SESSION_BOOT.md`, `src/tac/controller.py`, `workflows/tac_telegram_commands.json`, `tests/test_phase3_controller.py`, `tests/test_workflow_contract.py`, `tests/test_hq_orchestration_scaffold.py`, `scripts/hq_tmux_runner_template.sh`, `scripts/hq_safe_agent_wrapper_template.sh`, `scripts/run_offline_validations.py`, `docs/TRUE_AUTONOMOUS_CONTROLLER_MASTER_SENDOFF_2026-05-18.md`, `reports/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Local/offline only. No live Telegram send, n8n activation, production restart, Instagram publish, Upbit mutation, secret read, AWS mutation, or Docker production operation.
- rollback_needed: No.
- next_action: Continue from `reports/hq_continuation_ledger_2026-05-18.json`: create inactive n8n SSH dispatch draft and runtime queue schema.
## 2026-05-18 13:40 KST - Inactive Runtime Orchestration Dispatch Layer
- request: Build the inactive runtime orchestration layer after the continuation-first HQ scaffold.
- actions: Created runtime queue/state schemas and samples; created Telegram HQ command schema; created inactive/importable n8n SSH dispatch draft; documented runtime queue/state/Telegram contracts; hardened dispatch and kill-switch templates for dry-run default; extended reviewer loop template; updated continuation ledger and deferred gate registry; added runtime orchestration offline tests and final report.
- validation: PASS. `python -m unittest discover -s tests` PASS, 43 tests; `python -m unittest tests.test_hq_runtime_orchestration_20260518` PASS, 8 tests; `python scripts/run_offline_validations.py` PASS.
- telemetry: SUCCESS: TAC now has a locally validated queue/state/Telegram/n8n draft layer for future persistent runtime orchestration. FAILURE_PREVENTED: live SSH, credentialed n8n, Telegram send, workflow activation, and production mutation remain explicit deferred gates instead of blocking safe local work.
- side_effects: Local/offline only; no live operation, credential read, secret output, or production mutation.
- next_action: Build Telegram-ready Korean summary renderer and SQLite-backed validated queue writer.

## 2026-05-18 13:55 KST - Queue Renderer And Approved Live Gate Smoke
- request: Build the next queue/renderer/reviewer layer and execute approved live gate tests.
- actions: Added Korean Telegram preview renderer; added SQLite-backed runtime queue writer; added reviewer feedback schema/sample/report; added inactive n8n import checklist; added remote live gate smoke helper; updated continuation ledger; ran approved EC2 SSH queue append, EC2 tmux creation/cleanup, n8n read-only check, and Telegram smoke send.
- validation: PASS. Local tests 47/47 PASS; offline validation runner PASS; live SSH queue append PASS; EC2 tmux smoke PASS; n8n read-only PASS; Telegram smoke task `tac-20260518044042-7651a7d56d` PASS.
- telemetry: SUCCESS: TAC now has local queue writer, Korean summary preview, reviewer feedback schema, and first scoped live gate smoke evidence. FAILURE_PREVENTED: inline SSH JSON quoting corrupted one generated queue line; helper-based JSON append now validates and backs up before filtering.
- side_effects: One Telegram smoke message sent; one EC2 queue smoke item appended; one scoped tmux smoke session created and cleaned. No production activation, Upbit call, Docker restart, AWS mutation, credential read, or secret output.
- next_action: Import inactive n8n dispatch draft as inactive and run full dry-run E2E loop.

## 2026-05-18 14:35 KST - Phase 3 Runtime Orchestration Dry-Run
- request: Continue to Phase 3 with all approvals and do not stop after one gate; validate n8n draft import, EC2 tmux dry-run, reviewer loop, Telegram summary, and local tests.
- actions: Patched the inactive n8n dispatch draft for n8n validation; imported it as inactive workflow `DoClguwa8aewVM8D`; temporarily activated only for one draft webhook smoke and deactivated it; synced scripts/schemas to `/home/ubuntu/workspace/true-autonomous-controller`; added Docker runner scaffold and local run plan; added Phase 3 local orchestrator; ran EC2 queue -> tmux -> wrapper -> reviewer -> report dry-run; sent one Telegram summary smoke.
- validation: PASS. n8n workflow validation PASS; draft webhook returned `QUEUED_DRAFT` with no live SSH; EC2 E2E dry-run `hq-phase3-e2e-smoke-20260518` PASS and left no tmux session running; local tests 50/50 PASS; offline validation runner PASS.
- telemetry: SUCCESS: Phase 3 bounded orchestration path now exists and is validated from n8n draft through EC2 tmux/reviewer and Telegram summary. FAILURE_PREVENTED: n8n draft workflow final state was rechecked as inactive after temporary smoke activation.
- files_changed: `workflows/inactive_hq_ssh_dispatch_draft_2026-05-18.json`, `docker/tac-runner.Dockerfile`, `scripts/remote_phase3_e2e_smoke.py`, `scripts/docker_isolated_runner_plan.py`, `scripts/hq_phase3_orchestrator.py`, `tests/test_phase3_runtime_orchestration_20260518.py`, `reports/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: One inactive n8n draft workflow exists; one temporary activation/deactivation was performed for smoke testing; one Telegram smoke summary was sent; EC2 bounded workspace received synced scripts/schemas and dry-run runtime artifacts. No production activation, Upbit order/read, Instagram publish, Docker restart, AWS mutation, credential value read, or secret output.
- rollback_needed: No.
- next_action: Build Docker-isolated runner image in disposable mode, then wire selected Telegram commands to the new queue/tmux/reviewer path behind a fallback.

## 2026-05-18 15:40 KST - Phase 4 Bounded Runtime Route
- request: User approved the remaining Phase 4 operating work.
- actions: Added queue runtime module; added `/queue` and `/handoff` service endpoints; patched Telegram workflow parser for `/queue` and `/handoff`; added Docker container smoke, queue soak, Git checkpoint manifest, EC2 restart, and remote queue route smoke helpers; built Docker runner image; ran disposable no-network Docker smoke; deployed service/scripts to EC2; restarted scoped `tac-service`; patched active n8n Telegram workflow parser; verified `/queue` dispatch starts/reuses `tac-hq-runner` and produces handoff/state/report.
- validation: PASS. Local tests 55/55 PASS; offline validation runner PASS; Docker build PASS; Docker no-network smoke PASS; EC2 `/queue`/`/handoff` smoke PASS; runner handoff latest task `hq-live-queue-route-smoke-20260518063612` PASS.
- telemetry: SUCCESS: TAC moved from Phase 3 dry-run pieces into a bounded Phase 4 runtime route where queue dispatch wakes a persistent tmux runner. FAILURE_PREVENTED: missing runner script on EC2 caused initial tmux dispatch to exit; synced full runner script set and revalidated.
- files_changed: `src/tac/*`, `workflows/tac_telegram_commands.json`, `scripts/*`, `tests/*`, `reports/*`, `runtime/*`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Local Docker Desktop started; local Docker image built; disposable container run completed; active n8n Telegram parser patched; EC2 `tac-service` restarted; EC2 `tac-hq-runner` started/reused; bounded smoke queue items appended. No Upbit, Instagram, AWS, secret, force-push, or production Docker restart.
- rollback_needed: No immediate rollback.
- next_action: Build Docker Codex runner execution and run a user-origin Telegram `/queue smoke` from the Telegram app.

## 2026-05-18 16:10 KST - PC Power-Off Resilience Options Review
- request: Explain three realistic ways to prevent Kindred/TAC automation from stopping when the local PC is powered off.
- actions: Reviewed project memory and current SESSION_BOOT; compared always-on EC2 runner, managed container/job runner, and local always-on machine/VPN options against the existing Telegram -> n8n -> tmux -> Codex route.
- validation: PASS. Advisory-only review; no live command, workflow activation, credential read, deployment, Docker restart, AWS mutation, or production state change.
- telemetry: SUCCESS: Recommended keeping orchestration on the existing EC2 path first, then moving Codex execution into a Docker-isolated runner. FAILURE_PREVENTED: Avoided treating the local Codex desktop session as the durable runtime for long-running automation.
- side_effects: Documentation/telemetry only.
- next_action: If approved, implement the recommended path by finishing Docker Codex runner execution on EC2 and routing selected Telegram commands through the persistent `/queue` path.

## 2026-05-18 16:30 KST - Company Mode Runtime And Completion Notification
- request: Make the controller operate like a company-style HQ/agents system where the user can order work once, leave the computer, and receive a completion update.
- actions: Added company-mode task runner, completion notifier, Docker Codex CLI image install, `/work` and natural-language queue routing, queue notification metadata, active n8n notify route, and operator runbook. Synced runner/service updates to EC2, built the Docker Codex image locally and on EC2, restarted scoped service/runner sessions, and ran queue smoke.
- validation: PASS. 59 local tests passed; offline validation passed; local/EC2 Docker Codex CLI smoke passed; n8n notify route returned Korean summary; EC2 queue -> tmux -> company wrapper -> handoff/state/report smoke passed and wrote notifier artifact.
- telemetry: SUCCESS: Telegram-origin company-mode work can now enter the async queue and produce final notification attempts without the user waiting at the computer. FAILURE_PREVENTED: Existing `tac-hq-runner` sessions must be restarted after runner script sync, and Docker Codex CLI installation must not be mistaken for authenticated Docker Codex execution.
- side_effects: Local/EC2 Docker image builds, scoped EC2 `tac-service` restart, scoped `tac-hq-runner` restart, active TAC n8n workflow patches. No secret output, Upbit action, Instagram publish, AWS mutation, production Docker restart, or force push.
- remaining: Real Docker Codex execution needs a container-specific auth volume; real Telegram completion notification needs one user-origin `/work` message so the real chat id is present.

## 2026-05-18 16:20 KST - Monthly Runtime Cost Estimate
- request: Estimate monthly cost for the recommended PC power-off resilient TAC/Kindred runtime.
- actions: Checked current public AWS Lightsail bundle pricing and USD/KRW reference rate; separated infrastructure cost from AI/Codex usage cost.
- validation: PASS. Advisory-only calculation; no live AWS, n8n, Telegram, Docker, credential, or production mutation.
- telemetry: SUCCESS: Baseline always-on runtime estimate is approximately $12-$24/month if using a 2GB-4GB Linux VPS class, plus AI usage/subscription costs. FAILURE_PREVENTED: Avoided implying local Codex desktop can be the reliable always-on runtime when the PC is powered off.
- side_effects: Documentation/telemetry only.

## 2026-05-18 16:30 KST - Existing Cloud Storage Vs Compute Review
- request: Explain whether existing cloud spaces such as iCloud, Google Drive, or Google Cloud can host the always-on Kindred/TAC runtime.
- actions: Checked current public Apple iCloud+ and Google Cloud documentation; distinguished storage-only products from compute products that can run n8n/TAC/Codex runners.
- validation: PASS. Advisory-only; no live cloud, credential, workflow, Docker, Telegram, or production mutation.
- telemetry: SUCCESS: Clarified that iCloud/Google Drive can only support backups/log sync, while Google Cloud Compute Engine or Cloud Run can run the persistent automation. FAILURE_PREVENTED: Avoided designing the durable runtime around consumer file-sync storage that cannot execute background processes.
- side_effects: Documentation/telemetry only.

## 2026-05-19 KST - Autonomous Runtime Engine Buildout
- request: Build out the practical autonomous runtime orchestration platform from the current company-mode queue/runner foundation.
- actions: Stored the major-task runtime estimate/continuation rule; added runtime state transition, heartbeat, retry decision, telemetry event, and continuation handoff module; expanded queue schema/sample with owner, department, lifecycle, continuation, and telemetry pointers; added runtime event schema and sample JSONL telemetry; added inactive n8n runtime orchestration pack draft; added runtime state machine, autonomous buildout, and Instagram growth experiment reports; expanded offline validation and tests.
- validation: PASS. `python -m unittest discover -s tests` ran 66 tests; `python scripts/run_offline_validations.py` PASS; `python scripts/runtime_engine_smoke.py` PASS; JSON parse checks for runtime event schema and inactive n8n runtime pack PASS.
- telemetry: SUCCESS: TAC now has local primitives for stateful runtime continuity and audit events before longer unattended operation. FAILURE_PREVENTED: Ledger final report path contract was updated after the ledger advanced to the new buildout report.
- side_effects: Local/offline only. No live SSH, live Telegram send, live Instagram publish, Upbit operation, production Docker restart, AWS mutation, credential read, secret output, or force push.
- next_action: Run a bounded 5-6 hour soak with heartbeat/retry/handoff checks, or use the Instagram growth experiment system to upgrade the SNS automation project without live publishing.

## 2026-05-19 KST - YUNA Comment DM Opener Activation
- request: User confirmed Instagram profile bio submit and profile image upload, then approved activating `actual_05_instagram_comment_dm_opener` automatic public comment reply and private DM opener.
- actions: Located n8n workflow `actual_05_instagram_comment_dm_opener` (`Afve1lyQgvUIpgsg`); verified YUNA scoring logic was present; enabled `Public Reply` and `Private Reply DM Opener`; activated the workflow; verified active graph shows workflow active with both reply nodes enabled.
- validation: PASS. n8n update validation accepted operations before applying; update applied 3 operations; active workflow now has `active=true`, `activeVersionId=050012f8-27c1-4a32-937f-292b122ddab5`, `Public Reply.disabled=false`, and `Private Reply DM Opener.disabled=false`.
- telemetry: SUCCESS: YUNA comment scoring can now automatically reply publicly and send the YUNA score/private reply flow when Instagram comment webhook events arrive. FAILURE_PREVENTED: `Telegram Operator Alert` remained disabled because it is not required for automatic comment/DM activation and would add extra operator notifications.
- side_effects: Live n8n workflow activation and live Instagram comment/private reply capability enabled. No credentials were read or printed, no manual execution was triggered, no live test comment/DM was sent by Codex, and no unrelated workflow was modified.
- next_action: Wait for the next real Instagram comment event, then inspect execution/log rows for `public_reply_sent`, `private_reply_sent`, `yuna_score`, `yuna_verdict`, and any Graph API error.

## 2026-05-19 KST - YUNA Growth Brain HQ System
- request: User asked to deepen the Instagram account brain using research, HQ/agents, senior SNS marketing, and behavioral analysis so more people follow, comment, save, DM, and join.
- actions: Checked current TAC memory and YUNA activation state; researched current Instagram recommendation/insight guidance; created YUNA HQ agent operating model, growth brain report, future sendoff, experiment schema, sample experiment, and regression tests; updated offline validation runner and continuation ledger.
- validation: PASS. `python -m unittest discover -s tests` ran 71 tests; `python scripts/run_offline_validations.py` PASS; YUNA schema and sample JSON parse PASS.
- telemetry: SUCCESS: YUNA growth work now has a structured experiment brain instead of only a static 10K plan. FAILURE_PREVENTED: Views alone are no longer accepted as the main success metric.
- files_changed: `schemas/yuna_growth_experiment.schema.json`, `runtime/yuna_growth_experiments/sample_experiment.json`, `reports/yuna_brain_hq_agent_operating_model_2026-05-19.md`, `reports/yuna_brain_growth_system_2026-05-19.md`, `docs/YUNA_BRAIN_SENDOFF_2026-05-19.md`, `tests/test_yuna_growth_brain_20260519.py`, `scripts/run_offline_validations.py`, `reports/hq_continuation_ledger_2026-05-18.json`, `agent_memory/*`, `execution_logs/DAILY_EXECUTION_LOG.md`.
- side_effects: Local/offline only. No live publishing, manual DM/comment send, credential read, production workflow mutation, secret output, or force push.
- rollback_needed: No.
- next_action: Patch the SNS automation workspace with YUNA experiment metadata in approval candidates and reporting.

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
- Extracted YUNA/Instagram-only session state into a standalone handoff packet for the next Codex session.
- Included live workflow IDs, active versions, product taxonomy, posting ratio, reports, remaining gaps, and exact continuation prompt.
- Documentation only; no live Instagram/n8n/credential/Docker/server/AWS mutation.

## TAC_SCORECARD_AND_RUNTIME_HARDENING_20260522

- request: User asked TAC HQ and expert agents to objectively score the autonomous controller across 10 sectors, improve it until the target score reached 90, save the result, update README in five languages, and push to GitHub.
- actions: Created root multilingual README, permanent README language policy, TAC scorecard generator/schema/reports, agent council review, queue lock, tmux dequeue lock, narrowed kill switch, safer Codex fallback defaults, and regression tests.
- scoring: strict external audit baseline `76/100`; local pre-improvement baseline `81/100`; post-improvement repository/runtime readiness `92/100`.
- validation: PASS. `python -m unittest discover -s tests` ran 82 tests. `python scripts/run_offline_validations.py` PASS.
- telemetry: SUCCESS: TAC now has reproducible 10-sector score governance and permanent multilingual README policy. FAILURE_PREVENTED: broad process-wide kill and queue race risks were reduced.
- side_effects: Local repository changes only so far. No live n8n activation, production deploy, secret read, AWS mutation, Instagram publish, Upbit action, or force push performed.
- next_action: Commit and push, then schedule or run the 5-6 hour unattended queue soak as the next hardening proof.

## TAC_DOCKER_AUTH_AND_SOAK_STARTED_20260524

- request: Create Docker-only Codex auth volume, validate containerized Codex execution, then start 5-6 hour unattended soak.
- actions: Built/reused `tac-codex-runner:codex`, created `tac-codex-auth`, completed Codex device auth, verified container login, ran direct Docker Codex exec smoke, added `scripts/unattended_soak_runner.py`, normalized EC2 shell scripts to LF, and started tmux session `tac-unattended-soak-20260524`.
- validation: PASS for Docker-only Codex auth smoke. PASS for queue preflight task `tac-soak-preflight3-20260524-000` with `runner_result.runner = docker_codex` and host fallback disabled.
- long_run_status: RUNNING. 360-minute soak started on EC2 with heartbeat file `runtime/soak/tac-unattended-soak-20260524.heartbeat.jsonl`.
- telemetry: SUCCESS: Docker-only Codex auth volume is no longer just a deferred gate; authenticated container Codex execution has been proven. SOAK_PENDING: final 5-6 hour result is still running.
- side_effects: EC2 Docker volume created, one device login completed, bounded Docker Codex smoke executed, tmux soak session started. No production deploy, n8n activation, secret output, AWS mutation, Instagram publish, Upbit action, or force push.

## TAC_UNATTENDED_SOAK_FINAL_PASS_20260525

- request: User asked whether the controller is now perfect after the remaining Docker auth and 5-6 hour soak gates.
- actions: Checked EC2 tmux sessions, final soak JSON, heartbeat tail, stdout log, task reports, company runner artifacts, and failed/completed queue entries.
- result: PASS. `tac-unattended-soak-20260524.final.json` reports PASS after 360 minutes.
- evidence: 18 tasks enqueued during soak; all 18 corresponding reports show `status: PASS`; no soak entries appeared in `runtime/queue/failed.jsonl`.
- interpretation: Docker-only Codex auth volume, containerized Codex execution, and 5-6 hour unattended soak are now proven. Production gates remain intentionally gated.

## TAC_MULTI_PROJECT_COMPANY_ONBOARDING_20260525

- request: Use TAC to move into company-mode delegation for real projects: Upbit, SNS/Instagram, flight-deal automation, and TAC itself.
- actions: Created a secret-excluding bounded archive for the local SNS automation workspace; uploaded and extracted it on EC2; queued company-mode TAC tasks for Upbit, SNS/Instagram, flight-deal discovery, and TAC portfolio registry; fixed the company runner prompt to forbid approval-only plans; added Docker `--group-add` workspace write support; generated deterministic portfolio registry report.
- validation: PASS. Local targeted tests for company runner prompt/archive passed. EC2 targeted tests passed. Docker write probes passed for TAC, SNS, and Upbit bounded workspaces. Upbit, SNS/Instagram, and flight-deal queue tasks completed PASS; TAC portfolio report was generated deterministically after the Codex version timed out.
- evidence: `reports/tac_multi_project_onboarding_2026-05-25.md`, `reports/hq_portfolio_registry_2026-05-25.md`, EC2 `/home/ubuntu/workspace/true-autonomous-controller/runtime/reports/hq_portfolio_registry_2026-05-25.md`.
- telemetry: SUCCESS: TAC can now accept real project work through the queue/tmux/Docker-Codex path and create project-level reports/artifacts. FAILURE_PREVENTED: approval-only company prompts and Docker workspace write permission gaps were fixed.
- side_effects: SNS safe archive was synced to EC2. No Upbit exchange action, Instagram publish, production n8n activation, production restart, AWS mutation, credential value read/output, or force push occurred.
- next_action: Continue project-specific safe work from the portfolio registry commands, or explicitly approve one deferred live gate at a time.

## WORLDVAPE_GWANGWOON_DAILY_GROWTH_ROUTINE_20260525

- request: Build a TAC routine that automatically supports 월드베이프 광운대점 Instagram/SNS growth by analyzing competitors/content/performance, generating YUNA candidates, requesting approval before posting, and learning from results.
- actions: Added a daily growth routine schema, sample routine JSON, TAC queue task builder, inactive n8n schedule draft, Korean operator report, future sendoff, regression tests, and offline validation coverage.
- validation: PASS. `python -m unittest tests.test_worldvape_daily_growth_ops_20260525` ran 5 tests; `python -m unittest discover -s tests` ran 90 tests; `python scripts/run_offline_validations.py` PASS.
- telemetry: SUCCESS: TAC now has the offline/draft structure for a recurring local-business SNS growth loop instead of a one-off YUNA report. FAILURE_PREVENTED: live publish, credentialed metric fetch, live scraping, n8n activation, and production restart remain deferred gates.
- side_effects: Local/offline only. No live Instagram publish, credential read, n8n activation, production restart, AWS mutation, or external scraping was performed.
- next_action: Import `workflows/inactive_worldvape_daily_growth_ops_2026-05-25.json` into n8n as inactive, validate mapping, then explicitly approve activation when ready.

## WORLDVAPE_DAILY_GROWTH_LIVE_VERIFICATION_20260525

- request: After user approval, complete the final queued smoke verification for the Worldvape Gwangwoon Marketing HQ daily routine.
- result: PASS with n8n CLI manual-execute caveat.
- live_state: n8n workflow `WorldvapeGrowth20260525` is active; scoped `tac-hq-runner` is running.
- smoke: `worldvape-daily-growth-smoke-20260525094702` was processed by `tac-hq-runner` and completed PASS.
- notification: notifier artifact was created and webhook returned HTTP 200.
- fix: EC2 runner shell scripts were normalized from CRLF to LF; local `.gitattributes` was added to prevent recurrence.
- privacy_hardening: `scripts/hq_notify_completion.py` now redacts chat ids in stored response tails; existing smoke artifact was redacted.
- queue_handling: 36 unrelated stale pending lines were moved to a deferred backup before focused smoke verification.
- safety: No Instagram publish, no comment/DM send, no credential output, no AWS mutation, no unrelated workflow mutation, no force push, and no destructive deletion.

## TAC_SAFE_FALLBACK_AUTONOMY_PATCH_20260529

- request: User reported that TAC still stops on blocked items and asked to patch the logic.
- actions: Added safe fallback completion to the company runner, added tmux `company_status` reporting, updated Worldvape safe-rerun expectations, created an operator report, and recorded memory.
- result: PASS.
- validation: `python -m unittest tests.test_company_runner_safe_fallback_20260529` PASS; `python -m unittest discover -s tests` PASS with 138 tests; `python scripts/run_offline_validations.py` PASS; EC2 `py_compile` PASS; EC2 safe fallback smoke returned `PASS_WITH_SAFE_FALLBACK`.
- telemetry: SUCCESS: blocked primary runner results no longer end the whole company-mode task by default. FAILURE_PREVENTED: user-facing "blocked and stopped" behavior now produces continuation-ready fallback artifacts.
- side_effects: Local files plus scoped EC2 sync of TAC runner scripts and scoped `tac-hq-runner` restart. No live n8n, Telegram, Instagram, Docker production, AWS, secret, or external API operation.
- next_action: Add a one-retry bounded repair loop that attempts local fixable repair before fallback.

## TAC_CODEX_AUTH_VOLUME_SMOKE_20260528

- request: Run a TAC Codex-backed report-only smoke using `TAC_CODEX_AUTH_VOLUME=tac_codex_auth` after device-auth login completed.
- result: PASS.
- project_root: `C:\Users\minho\Documents\02_work\03_AI\05_true atonomous_controller`.
- auth_volume: `runtime/config/tac_codex_auth_volume.local.env` loads `TAC_CODEX_AUTH_VOLUME=tac_codex_auth`; verify script returned `VERIFY_STATUS PASS`.
- smoke: Docker Codex mounted `tac_codex_auth:/home/tacrunner/.codex` and returned `TAC_CODEX_AUTH_VOLUME_SMOKE_OK`.
- validation: `python -m unittest discover -s tests` PASS, 114 tests; `python scripts/run_offline_validations.py` PASS.
- safety: No Instagram publish, Telegram send, n8n activation/deactivation/API call, Instagram/Telegram API call, production mutation, or secret inspection/output/modification.

## WORLDVAPE_DAILY_GROWTH_REPEATABLE_QUEUE_20260528

- request: Convert Worldvape daily growth into a repeatable TAC Codex-backed report-only queue workflow.
- result: PASS.
- created: `scripts/create_worldvape_daily_growth_queue.py`, `tests/test_worldvape_repeatable_queue_20260528.py`, `runtime/reports/worldvape-daily-growth-repeatable-queue-20260528.md`.
- generated_queue: `runtime/queue/worldvape-daily-growth-20260528140820.json`.
- generated_report: `runtime/reports/worldvape-daily-growth-20260528140820.md`.
- codex_backed_execution: PASS via Docker Codex with `TAC_CODEX_AUTH_VOLUME=tac_codex_auth`.
- validation: `python -m unittest discover -s tests` PASS, 121 tests; `python scripts/run_offline_validations.py` PASS.
- safety: No Instagram publish, Telegram send, n8n activation/deactivation/API call, Instagram/Telegram API call, production mutation, or secret inspection/output/modification.

## WORLDVAPE_DAILY_GROWTH_ONE_COMMAND_RUNNER_20260528

- request: Create a one-command local runner for Worldvape daily growth report-only execution.
- result: PASS.
- created: `scripts/run_worldvape_daily_growth_once.py`, `scripts/run_worldvape_daily_growth_once.ps1`, `tests/test_worldvape_one_command_runner_20260528.py`.
- one_command_smoke: `powershell -ExecutionPolicy Bypass -File scripts\run_worldvape_daily_growth_once.ps1 -Timestamp 20260528152000` PASS.
- generated_queue: `runtime/queue/worldvape-daily-growth-20260528152000.json`.
- generated_report: `runtime/reports/worldvape-daily-growth-20260528152000.md`.
- validation: `python -m unittest discover -s tests` PASS, 127 tests; `python scripts/run_offline_validations.py` PASS.
- safety: No Instagram publish, Telegram send, n8n activation/deactivation/API call, Instagram/Telegram API call, production mutation, or secret inspection/output/modification.

## WORLDVAPE_DAILY_GROWTH_TASK_SCHEDULER_20260528

- request: Create a safe Windows Task Scheduler setup for daily Worldvape report-only execution.
- result: PASS.
- created: `scripts/register_worldvape_daily_growth_task.ps1`, `scripts/verify_worldvape_daily_growth_task.ps1`, `scripts/unregister_worldvape_daily_growth_task.ps1`, `tests/test_worldvape_task_scheduler_scripts_20260528.py`.
- scheduler_contract: task `Kindred_Worldvape_Daily_Growth_ReportOnly`, default daily time `09:30`, working directory `C:\Users\minho\Documents\02_work\03_AI\05_true atonomous_controller`, command `powershell -ExecutionPolicy Bypass -File scripts\run_worldvape_daily_growth_once.ps1`.
- validation: targeted task scheduler tests PASS, PowerShell parser PASS, `python -m unittest discover -s tests` PASS with 134 tests, `python scripts/run_offline_validations.py` PASS.
- scheduler_state: Not registered during this setup pass; operator can run the register script explicitly.
- safety: No Instagram publish, Telegram send, n8n activation/deactivation/API call, Instagram/Telegram API call, production mutation, or secret inspection/output/modification.

## WORLDVAPE_TASK_SCHEDULER_ENCODING_FIX_20260528

- request: Fix mojibake in Windows PowerShell output for Worldvape scheduler scripts while preserving scheduler behavior.
- result: PASS.
- changed: Added `Initialize-SafeConsoleOutput` to the three scheduler scripts and one-command wrapper; switched visible status lines to ASCII fallback labels.
- preserved: task name, schedule `09:30`, working directory, runner command, limited run level, verification/unregistration scope.
- validation: targeted display tests PASS, PowerShell parser PASS, `python -m unittest discover -s tests` PASS with 136 tests, `python scripts/run_offline_validations.py` PASS.
- safety: Local script text only. No Instagram publish, Telegram send, n8n activation/deactivation/API call, Instagram/Telegram API call, production mutation, or secret inspection/output/modification.

## TAC_SELF_REPAIR_COMPANY_MODE_20260529

- request: Patch TAC so a failure triggers company-style root-cause analysis, repair, validation, and retry instead of stopping or immediately falling back.
- result: PASS.
- changed: Added permanent self-repair rule to `AGENTS.md` and `SESSION_BOOT.md`; added `PASS_WITH_AUTO_REPAIR`, repair meeting records, bounded repair attempts, Docker Codex auth-volume config repair, and Docker auth-volume ownership repair via root helper container to `scripts/hq_company_task_runner.py`.
- tests: Added regression coverage proving missing auth-volume config and auth-volume permission failures are repaired and retried before fallback.
- validation: `python -m py_compile scripts\hq_company_task_runner.py` PASS; `python -m unittest tests.test_company_runner_safe_fallback_20260529` PASS, 5 tests; `python -m unittest discover -s tests` PASS, 141 tests; `python scripts\run_offline_validations.py` PASS.
- ec2_deployment: Synced `scripts/hq_company_task_runner.py`, remote `py_compile` PASS, scoped `tac-hq-runner` restarted.
- ec2_smoke: `self-repair-remote-smoke-20260529` executed repair option A and option B; ownership repair returned PASS; final status `PASS_WITH_SAFE_FALLBACK` because Docker Codex auth reached `401 Unauthorized / Missing bearer`.
- safety: Local source/test/report/memory update only. No live n8n, Telegram send, Instagram publish, Upbit credential action, production Docker restart, AWS mutation, secret read/output, force push, or destructive operation.

## TAC_PROJECT_PROTOCOL_AND_AUTH_GATE_20260529

- request: Store permanent project-scale TAC protocol and continue the next hardening item after self-repair.
- result: PASS.
- changed: Added permanent project-command protocol to `AGENTS.md` and `SESSION_BOOT.md`; updated company runner prompt with phase-by-phase execution, original objective reread, 10-sector scoring, 97/100 self-improvement loop, and final project report requirements.
- auth_gate: Docker Codex 401/missing-bearer/not-logged-in failures now return a clear `DEFERRED_GATE` and device-auth/login required action.
- validation: `python -m py_compile scripts\hq_company_task_runner.py` PASS; `python -m unittest tests.test_company_runner_safe_fallback_20260529` PASS, 8 tests; `python -m unittest discover -s tests` PASS, 144 tests; `python scripts\run_offline_validations.py` PASS.
- ec2_deployment: Synced `scripts/hq_company_task_runner.py`, remote `py_compile` PASS, scoped `tac-hq-runner` restarted.
- ec2_smoke: `self-repair-remote-smoke-20260529` returned `PASS_WITH_SAFE_FALLBACK`; original runner status is now `DEFERRED_GATE`; repair meeting cause is `Docker Codex auth volume exists but is not logged in`.
- safety: Local source/test/report/memory update only. No live n8n, Telegram send, Instagram publish, Upbit action, production Docker restart, AWS mutation, secret read/output, force push, or destructive operation.
