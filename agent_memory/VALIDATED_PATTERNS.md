# Validated Patterns

## Role

This file stores reusable execution patterns validated for TRUE AUTONOMOUS CONTROLLER.

Append only unless correcting the latest entry.

## Entry Format

```text
## Pattern Name
- applies_to:
- procedure:
- validation:
- rollback:
- evidence:
```

## Pattern: Additive Bootstrap From Empty Workspace
- applies_to: New project directories with no existing local memory or source files.
- procedure: Read source KB from adjacent project memory first, then add local `AGENTS.md`, `SESSION_BOOT.md`, `agent_memory/*`, and `execution_logs/*` without modifying adjacent projects.
- validation: Confirm required files exist and include required markers for SESSION_BOOT, known failures, validated patterns, patch history, and daily execution log.
- rollback: Delete the newly added bootstrap files if the user rejects the bootstrap.
- evidence: Applied on 2026-05-16 KST after the controller workspace was found empty and non-Git.

## Pattern: Phase 1 Before Production Mutation
- applies_to: Telegram -> n8n -> tmux -> Claude/Codex runner integration.
- procedure: Define local contracts and dry-run runner behavior before changing remote EC2/n8n/Docker state.
- validation: Dry-run command wrapper must prove bounded runtime, log capture, exit status capture, summary generation, and kill-switch routing before live workflow activation.
- rollback: Remove local Phase 1 scaffold files or restore from Git checkpoint after repository initialization.
- evidence: Adopted from prior source KB preference for bounded dry runs, local recorder validation, and zero live mutation until readiness review passes.

## Pattern: Phase 3 Local-To-EC2 Bounded Validation
- applies_to: Planner -> executor -> reviewer scaffold before n8n workflow mutation.
- procedure: Implement contracts and a local dry-run controller, run local unit/smoke loops, copy only scaffold files into `/home/ubuntu/workspace/<project>` on EC2, and execute the same validation script inside tmux.
- validation: Local unit tests and smoke runs pass; EC2 tmux produces `runtime/phase3_result_remote_loop1.json` through `runtime/phase3_result_remote_loop3.json` with `status=PASS`.
- rollback: Use Git to revert local files; remove only generated files under the bounded EC2 workspace if rollback is requested.
- evidence: Validated on 2026-05-16 KST with 8/8 local tests passing and EC2 tmux validation loop x3 producing PASS results.

## Pattern: Semi-Live n8n Webhook To Bounded Runner
- applies_to: Telegram/n8n to EC2 runner MVP without changing existing production workflows.
- procedure: Run TAC HTTP service in scoped EC2 tmux session, import a unique-path n8n webhook workflow, publish it, restart only n8n if required for webhook registration, and validate `/run`, `/status`, and `/killall`.
- validation: n8n webhook `/run` loop x3 returns PASS with runner responses; `/status` returns a prior task result; `/killall` returns scoped tmux kill result.
- rollback: Unpublish or delete the `tac_controller_webhook` workflow and stop only the `tac-service` tmux session.
- evidence: Validated on 2026-05-17 KST against `https://n8n.mykindredai.com/webhook/tac-controller`.

## Pattern: Telegram Trigger With Strict Command Allowlist
- applies_to: Adding Telegram ingress without changing existing workflow logic.
- procedure: Add a separate Telegram Trigger workflow using an existing credential, parse only explicit controller commands, ignore all unsupported messages, and call the bounded TAC runner service.
- validation: n8n logs show `tac_telegram_commands` activated; controller webhook regression for `/run`, `/claude`, `/status`, and `/killall` passes after activation.
- rollback: Unpublish or delete only `tac_telegram_commands`; keep existing clean_01~04 workflows untouched.
- evidence: Activated on 2026-05-17 KST with `tac_telegram_commands` and validated controller routes after activation.

## Pattern: Dedicated Telegram Controller Bot Cutover
- applies_to: Separating TAC commands from an existing debug or approval Telegram bot.
- procedure: Create a dedicated `telegramApi` credential, update every TAC workflow Telegram Trigger and Telegram send node to the new credential, import both workflows, reactivate them, restart only n8n for webhook registration, and confirm credential usage no longer lists TAC workflows under the old bot.
- validation: `Kindred AI Controller` credential is used by `tac_controller_webhook` and `tac_telegram_commands`; `Kindred Debug Guard` usage no longer includes TAC workflows; Telegram Bot API reports bot name/menu set and n8n webhook registered; `/run`, `/claude`, `/status`, and `/killall` webhook regressions pass.
- rollback: Reimport the prior workflow JSON or repoint TAC Telegram nodes to the previous credential, then reactivate and restart only n8n.
- evidence: Validated on 2026-05-17 KST with bot `@kindred_ai_controller_bot` and n8n credential `Kindred AI Controller`.

## Pattern: Human-Origin Telegram E2E Confirmation
- applies_to: Confirming that the live Telegram bot path works beyond synthetic webhook tests.
- procedure: User opens the dedicated controller bot, presses Start, sends `/run smoke test`, and verifies a returned TAC summary with status, task id, and follow-up commands.
- validation: Bot response must include `[TRUE AUTONOMOUS CONTROLLER]`, `status: PASS`, a `tac-*` task id, bounded execution reason text, `/status <task_id>`, and `/killall`.
- rollback: If no response or wrong bot responds, inspect Telegram webhook registration and n8n credential usage, then reimport/reactivate the TAC workflows and restart only n8n.
- evidence: User screenshot on 2026-05-17 KST showed `/run smoke test` returning `status: PASS` and task `tac-20260516234503-c1d0425439` from `@kindred_ai_controller_bot`.

## Pattern: Codex-First Command Surface
- applies_to: Replacing Claude-facing TAC commands with Codex-facing execution.
- procedure: Use `/codex` as the live agent command, send executor `codex` through n8n, build runner argv with current Codex CLI semantics, install Codex CLI in the EC2 runner user's local prefix, export that prefix in `tac-service`, and preflight `codex login status` before execution.
- validation: Source/workflow/docs contain no current `/claude` command references; local and EC2 tests pass; `/run` passes; `/codex` reaches Codex preflight and returns `BLOCKED` if login is absent; `/status` and `/killall` continue to work.
- rollback: Revert local Git commit and reimport previous n8n workflow JSON, then restart only `tac-service` and n8n.
- evidence: Validated on 2026-05-17 KST with Codex CLI `0.130.0`, active TAC workflows, `/run` PASS, `/codex` auth preflight BLOCKED, `/status` PASS, and `/killall` PASS.

## Pattern: Codex Auth Failure Escalation
- applies_to: Codex CLI executor failures caused by authentication or invalid API key.
- procedure: Detect 401/auth markers in Codex command output, redact API-key-like strings from stdout/stderr tails, classify the task as `BLOCKED`, disable retry, and require human credential refresh.
- validation: Local and EC2 tests pass; `/codex` with an invalid stored key returns `BLOCKED` in one attempt; generated result output contains `sk-REDACTED` instead of key-like material; runtime result files no longer grep for API-key prefixes.
- rollback: Revert the redaction/classification patch and restart `tac-service`, though this is not recommended because it restores retry waste and weaker output hygiene.
- evidence: Validated on 2026-05-17 KST with task `tac-20260517020244-62fc400f8a` returning `BLOCKED` for Codex authentication failure.

## Pattern: Codex ChatGPT Login Live Smoke
- applies_to: Confirming the dedicated controller can execute Codex through ChatGPT login instead of API-key auth.
- procedure: Log in on the EC2 runner user with Codex device auth, confirm `codex login status`, run `/codex` through the n8n webhook, then confirm `/status` and `/killall`.
- validation: Codex login status shows ChatGPT login; `/codex` returns `PASS`; command output contains the expected Codex agent message; `/status <task_id>` returns the same PASS result; `/killall` returns scoped kill PASS.
- rollback: If the login is revoked or expires, rerun `codex login --device-auth` on the EC2 runner user and retry the `/codex` smoke.
- evidence: Validated on 2026-05-17 KST with task `tac-20260517033536-bb8a366f30` returning `TAC_CODEX_OK`.

## Pattern: Codex Output In Telegram Summary
- applies_to: Returning actionable Codex diagnosis, plans, or implementation reports through Telegram.
- procedure: Parse Codex `--json` JSONL output, extract `item.completed` events where `item.type` is `agent_message`, and append that text to the task summary under `Codex output:`.
- validation: Local and EC2 tests pass; `/codex` webhook response includes `Codex output:` with the agent message; Telegram summary will show the same result because the workflow uses `result.summary`.
- rollback: Revert the summary extraction patch and restart `tac-service`.
- evidence: Validated on 2026-05-17 KST with task `tac-20260517034419-6e3a728f89`.

## Pattern: Bounded Workspace Codex Host-Mode Fallback
- applies_to: EC2 hosts where Codex `workspace-write` sandbox fails with `bwrap` before any file read.
- procedure: Extract an explicit workspace from `WORKSPACE:` lines, absolute `/home/ubuntu/workspace/...` paths, or known project aliases; resolve only relative paths inside the controller project root and absolute paths inside configured `TAC_ALLOWED_WORKSPACE_ROOTS`; run Codex with service-level `TAC_CODEX_SANDBOX=danger-full-access` only as a temporary host-mode fallback; close stdin so Codex cannot hang waiting for inherited input; keep the prompt denylist for secrets, sudo, destructive deletion, Docker restart, production mutation, AWS mutation, and live trading.
- validation: Local tests 18/18 pass; EC2 tests 18/18 pass; n8n `/codex` read-only smoke for `/home/ubuntu/workspace/02_업비트_자동화` returns a Korean Codex report with workspace, file count, secret count, and no file modification; `/status` and `/killall` pass.
- rollback: Set `TAC_CODEX_SANDBOX=workspace-write` or revert the patch and restart `tac-service`; final long-term replacement is Docker-isolated runner mode.
- evidence: Validated on 2026-05-17 KST with task `tac-20260517035838-8102c8f455`.

## Pattern: Long Codex Telegram Reply Timeout Guard
- applies_to: `/codex` tasks that may run longer than the previous 60-120 second n8n HTTP request timeouts.
- procedure: Set TAC n8n HTTP Request node timeouts to the controller hard runtime window, store parsed Codex `agent_text` from full stdout before truncating command tails, and keep Telegram message bodies under Telegram's 4096 character limit.
- validation: Local tests 20/20 pass; EC2 tests 20/20 pass; both TAC workflows are active; n8n webhook `/codex` returns `Codex output: TELEGRAM_TIMEOUT_FIX_OK`.
- rollback: Restore shorter n8n timeouts and revert controller `agent_text` extraction if needed, though that reintroduces silent long-run failures.
- evidence: Validated on 2026-05-17 KST with task `tac-20260517051453-69c2e2e7fe`.

## Pattern: Telegram Natural Follow-Up To Latest Workspace
- applies_to: Dedicated controller bot messages that are natural follow-ups rather than slash commands.
- procedure: Route non-slash Telegram text as a Codex follow-up task, tag the prompt with `FOLLOWUP_TASK: true`, and, when no explicit workspace is present, hydrate the task workspace from the latest TAC result.
- validation: Local tests 21/21 pass; EC2 tests 21/21 pass; n8n `tac_telegram_commands` is active after reimport; follow-up smoke without `WORKSPACE:` runs in the latest Upbit bounded workspace and returns `FOLLOWUP_WORKSPACE_OK`.
- rollback: Restore slash-command-only Telegram parser and remove follow-up workspace hydration.
- evidence: Validated on 2026-05-17 KST with task `tac-20260517054736-54de626dc9`.

## Pattern: Telegram Received Ack Before Long Runner
- applies_to: Dedicated controller bot `/run`, `/codex`, and natural follow-up messages.
- procedure: Generate a task id in the Telegram normalization node, send a `status: RECEIVED` Telegram message with `/status <task_id>` before calling the TAC runner, then send the final report after runner completion. Route unsupported slash commands to an explicit ignored/help reply.
- validation: Local tests 23/23 pass; EC2 tests 23/23 pass; `tac_telegram_commands` is active after reimport; `/status tac-20260517055951-c2007161f8` returns PASS; `/codex` smoke returns `FINAL_PIPELINE_OK`.
- rollback: Restore the direct IF Supported Command -> Call TAC Runner edge and remove received/unsupported reply nodes.
- evidence: Validated on 2026-05-17 KST with task `tac-20260517060655-8488d97be4`.

## Pattern: Telegram Immediate Execution Briefing
- applies_to: Dedicated controller bot run/codex/follow-up commands that need immediate user-facing orientation.
- procedure: In the pre-run `status: RECEIVED` message, include task id, estimated time, expected direction, HQ-to-agent flow, execution plan, `/status <task_id>`, and `/killall`.
- validation: Local tests 23/23 pass; EC2 tests 23/23 pass; workflow contract asserts `expected_time`, `expected_direction`, `hq_agent_flow`, and `execution_plan`; n8n TAC workflows are active; `/codex` smoke returns `ACK_BRIEFING_PATCH_OK`.
- rollback: Revert only `tac_telegram_commands.json` and `tests/test_workflow_contract.py`, reimport the prior Telegram workflow, and restart n8n.
- evidence: Validated on 2026-05-17 KST with task `tac-20260517063840-a53dda620e`.

## Pattern: Telegram HTML-Safe Controller Replies
- applies_to: Any TAC workflow node that sends Telegram text generated by controller, Codex, reviewer, or n8n code nodes.
- procedure: Set `additionalFields.parse_mode` to `HTML` on every TAC Telegram `sendMessage` node; avoid Markdown-sensitive labels in pre-run text; HTML-escape dynamic summaries before sending them through Telegram.
- validation: Local tests 25/25 pass; EC2 tests 25/25 pass; live n8n export shows `parse_mode: HTML` on all `tac_telegram_commands` send nodes; controller webhook with chat id returns 200 and sends Telegram summary task `tac-20260517074612-960807be93`.
- rollback: Reimport the prior workflow JSONs and restart n8n, but this is not recommended because unset parse mode restores Markdown entity failures.
- evidence: Validated after n8n execution `10487` showed `Send Received Reply` failed on Telegram Markdown entity parsing before the runner started.

## Pattern: Korean Operator-First Telegram Reports
- applies_to: Any Telegram-facing TAC received, final, status, or escalation report.
- procedure: Present Korean plain-language sections before technical detail: status, task id, estimated time, direction, role split, plan, result summary, completed work, blocked work, remaining work, and next commands. Keep raw logs and English labels out of the first screen.
- validation: Local tests 25/25 pass; EC2 tests 25/25 pass; `tac_controller_webhook` smoke returns Korean `결과 요약`; real Telegram Trigger execution `10554` sends Korean `상태: 접수됨` and `상태: 완료` messages successfully.
- rollback: Revert `src/tac/controller.py` and both TAC workflow JSON files, then restart `tac-service` and n8n.
- evidence: Added after the user reported that the prior successful Upbit report was too English/technical to operate from Telegram.

## Pattern: MCP Connectivity Matrix
- applies_to: Adding or claiming Codex MCP/plugin capabilities for the autonomous controller.
- procedure: Verify available tools through `tool_search`, verify configured local MCP servers without exposing secrets, run a health check where available, then record each integration as connected, tool-available, filesystem-native, or not connected as MCP.
- validation: n8n MCP health returned `success=true`; GitHub plugin tools were exposed; node REPL MCP returned cwd; Docker/PostgreSQL/SQLite/Telegram were not exposed as MCP tools in the current session.
- rollback: Remove `docs/MCP_CONNECTIVITY_MATRIX.md` if the project chooses not to track MCP state in-repo.
- evidence: Recorded on 2026-05-17 KST after user requested n8n, GitHub, Filesystem, Docker, PostgreSQL/SQLite, and Telegram MCP coverage.

## Pattern: Local Dependency-Free MCP Server Registration
- applies_to: Adding controller-specific MCP tools when a curated MCP server is not installed or exposed.
- procedure: Implement a minimal stdio MCP server with JSON-RPC content-length framing, keep the tool surface bounded and secret-free, register it in `~/.codex/config.toml`, and validate with direct framed protocol tests before relying on tool discovery.
- validation: `tests/test_mcp_servers.py` verifies `tac-docker` tool listing and `tac-state-db` SQLite init/task recording; full local suite passes 28/28.
- rollback: Remove the relevant `[mcp_servers.*]` block from `~/.codex/config.toml`, delete the local server scripts, and remove docs/tests if the server is no longer wanted.
- evidence: Applied on 2026-05-17 KST for `tac-docker` and `tac-state-db`.

## Pattern: Multi-Project Company-Mode Onboarding
- applies_to: Handing real projects such as Upbit, SNS/Instagram, and flight-deal automation to TAC without immediate production mutation.
- procedure: Create or confirm a bounded workspace for each project; exclude secret-like files and heavy generated directories for copied workspaces; queue one company-mode task per project; keep live operations as deferred gates; collect runtime reports; generate a portfolio registry that maps status, evidence, and next operator commands.
- validation: TAC service health passes; `tac-hq-runner` is running; queued tasks move from pending to completed or explicit failed/deferred state; Docker Codex write probes pass for bounded workspaces; local and EC2 targeted tests pass.
- rollback: Remove generated bounded workspace copies and runtime reports if requested; revert local runner/test changes through Git; do not touch production n8n/Instagram/Upbit state.
- evidence: Applied on 2026-05-25 KST with Upbit onboarding, SNS/Instagram onboarding, flight-deal discovery, and deterministic TAC portfolio registry generation.

## Pattern: Daily Local-Business SNS Growth Routine
- applies_to: Turning a local business Instagram/SNS account into a recurring TAC-operated growth loop without immediate live publishing.
- procedure: Store a machine-readable daily routine schema and sample; create a queue task builder for TAC; create an inactive n8n schedule draft; require four approval candidates with hook, YUNA score angle, local customer reason, CTA, follow reason, and risk notes; keep publish, credentialed metrics, live scraping, and workflow activation as deferred gates.
- validation: JSON schema/sample parse, inactive n8n draft parses and has no credentials, task builder emits a bounded TAC queue task, offline tests assert approval gate and learning loop markers.
- rollback: Revert the routine files and tests; no live n8n, Instagram, or credential state needs rollback because the routine is draft/offline by default.
- evidence: Applied on 2026-05-25 KST for 월드베이프 광운대점 daily Instagram/SNS growth operations.

## Pattern: Local TAC Codex Auth Volume Report-Only Smoke

- applies_to: Verifying a local Docker-only Codex auth volume without Instagram, Telegram, n8n, or production mutation.
- procedure: Load `TAC_CODEX_AUTH_VOLUME` from `runtime/config/tac_codex_auth_volume.local.env`, run `scripts/verify_tac_codex_auth_volume.ps1`, mount `<volume>:/home/tacrunner/.codex` into `tac-codex-runner:codex`, use a minimal read-only local workspace, and require a deterministic Codex `agent_message`.
- validation: `VERIFY_STATUS PASS`; Docker Codex returned `TAC_CODEX_AUTH_VOLUME_SMOKE_OK`; `python -m unittest discover -s tests` passed 114 tests; `python scripts/run_offline_validations.py` passed.
- rollback: Remove the generated smoke task, report, workspace, and telemetry files if the smoke record is no longer wanted; no production state was changed.
- evidence: Applied on 2026-05-28 KST in `runtime/reports/tac-codex-auth-volume-smoke-20260528.md`.

## Pattern: Repeatable Worldvape Report-Only Codex Queue

- applies_to: Generating recurring Worldvape daily growth queue tasks without live publish, Telegram send, n8n API/activation, secrets, or production mutation.
- procedure: Run `python scripts/create_worldvape_daily_growth_queue.py` to create a timestamped `runtime/queue/worldvape-daily-growth-<timestamp>.json`, append it to `runtime/queue/pending.jsonl`, create a local workspace under `runtime/workspaces/<task_id>`, then execute with `scripts/hq_company_task_runner.py` using `TAC_CODEX_AUTH_VOLUME=tac_codex_auth` for report-only Docker Codex output.
- validation: Generated task `worldvape-daily-growth-20260528140820` completed PASS through `docker_codex`; full unittest suite passed 121 tests; offline validations passed.
- rollback: Remove generated queue/report/workspace artifacts if the record is no longer wanted; no live system rollback is required because no live surface was touched.
- evidence: Applied on 2026-05-28 KST in `runtime/reports/worldvape-daily-growth-repeatable-queue-20260528.md`.

## Pattern: One-Command Worldvape Report-Only Local Runner

- applies_to: Running one local Worldvape daily growth report-only cycle from an operator shell without touching live Instagram, Telegram, n8n, secrets, or production.
- procedure: Run `powershell -ExecutionPolicy Bypass -File scripts\run_worldvape_daily_growth_once.ps1`; the wrapper confirms project root, ensures `TAC_CODEX_AUTH_VOLUME=tac_codex_auth`, calls the Python runner, creates a timestamped queue, validates report-only scope/deferred gates, and runs `scripts/hq_company_task_runner.py`.
- validation: One-command smoke with timestamp `20260528152000` passed; full unittest suite passed 127 tests; offline validations passed.
- rollback: Remove the generated queue/report/workspace artifacts and one-command scripts/tests if no longer wanted; no live system rollback is required.
- evidence: Applied on 2026-05-28 KST in `runtime/reports/worldvape-daily-growth-one-command-runner-20260528.md`.

## Pattern: Windows Task Scheduler Wrapper For Report-Only Runner

- applies_to: Scheduling a local TAC report-only runner on Windows without live Instagram, Telegram, n8n, production, or secret surfaces.
- procedure: Use a scoped task name, fixed project root, limited run level, explicit working directory, and a PowerShell action that calls the already validated report-only runner. Keep registration, verification, and unregistration as separate scripts.
- validation: `tests/test_worldvape_task_scheduler_scripts_20260528.py` checks task name, project root, runner path, secret-like strings, limited privilege, verification non-execution, and scoped unregistration; full unittest suite passed 134 tests; offline validations passed.
- rollback: Run `powershell -ExecutionPolicy Bypass -File scripts\unregister_worldvape_daily_growth_task.ps1` to remove only `Kindred_Worldvape_Daily_Growth_ReportOnly`.
- evidence: Applied on 2026-05-28 KST in `runtime/reports/worldvape-daily-growth-task-scheduler-20260528.md`.

## Pattern: ASCII-Fallback PowerShell Operator Output

- applies_to: Windows PowerShell scripts where non-ASCII status text can render as mojibake under mixed code pages or capture hosts.
- procedure: Initialize `[Console]::InputEncoding`, `[Console]::OutputEncoding`, `$script:OutputEncoding`, and best-effort `chcp.com 65001`, then keep operator-facing status labels ASCII-only.
- validation: Scheduler and one-command PowerShell scripts parse successfully; tests assert the display scripts include UTF-8 setup, `chcp.com 65001`, and ASCII-only output text; full unittest suite passed 136 tests; offline validations passed.
- rollback: Restore prior Korean display strings if a Unicode-safe host is proven and tests are updated accordingly.
- evidence: Applied on 2026-05-28 KST in `runtime/reports/worldvape-task-scheduler-encoding-fix-20260528.md`.

## Pattern: Safe Fallback Instead Of Terminal Runner Block

- applies_to: Company-mode TAC tasks where the primary Codex/Docker runner returns `FAIL` or `DEFERRED_GATE` before exhausting safe local/offline work.
- procedure: Keep live/credential/network surfaces blocked, write a `runtime/reports/<task_id>.safe_fallback.md` continuation report, preserve original runner status/reason, return `PASS_WITH_SAFE_FALLBACK`, and expose `company_status` in the tmux task report.
- validation: `tests/test_company_runner_safe_fallback_20260529.py`; full unittest suite passed 138 tests; offline validation passed.
- rollback: Set `disable_safe_fallback: true` on a specific queue task or revert the safe fallback patch if strict terminal failure behavior is required.
- evidence: Applied on 2026-05-29 KST after the user reported TAC still stopping instead of finishing safe work.

## Pattern: Continuation-First HQ Cycle
- applies_to: Multi-hour or broad TAC tasks that include live/credential/network blockers.
- procedure: Store a permanent continuation rule, split blocked live surfaces into deferred gates, keep executing safe local/offline/docs/tests/scaffold work, write a machine-readable continuation ledger, and validate that safe work continued despite gates.
- validation: `tests/test_hq_orchestration_scaffold.py` verifies instruction files, HQ model, continuation ledger, deferred gate registry, tmux scaffold, Instagram growth plan, and safe continuation; full local suite passes 35/35.
- rollback: Revert the HQ scaffold commit and restore prior Telegram briefing text if the project chooses to return to bounded single-cycle reporting.
- evidence: Applied on 2026-05-18 KST after user requested company-style HQ/autonomous agent behavior without stopping on one blocked item.
## 2026-05-18 - Inactive runtime orchestration dispatch layer

- pattern: Build queue/state/Telegram schemas first, generate an inactive n8n dispatch draft, keep dispatch/kill scripts dry-run by default, then validate with offline tests.
- validated_by:
  - `python -m unittest discover -s tests`
  - `python -m unittest tests.test_hq_runtime_orchestration_20260518`
  - `python scripts/run_offline_validations.py`
- result: PASS. Runtime orchestration can now be reviewed/imported as a draft without live SSH, n8n activation, Telegram send, secret access, or production mutation.

## 2026-05-18 - Scoped live gate smoke after local validation

- pattern: Run live gates only after local/offline tests pass; keep each live action one-shot, bounded, and credential-value-free in reports.
- validated_by:
  - EC2 SSH connectivity check
  - `scripts/remote_live_gate_smoke.py all`
  - n8n MCP health/minimal workflow metadata reads
  - one `tac_controller_webhook` Telegram smoke send
- result: PASS. Live SSH queue append, EC2 tmux session creation/cleanup, n8n read-only check, and one Telegram smoke send succeeded without production activation or secret output.

## 2026-05-18 - Phase 3 dry-run queue to reviewer loop

- pattern: Import the n8n dispatch workflow as inactive, validate it, run a single draft webhook smoke, sync scripts/schemas to the EC2 bounded workspace, then run queue -> tmux -> safe wrapper -> reviewer -> report as a scoped dry-run.
- validated_by:
  - n8n workflow validator for `DoClguwa8aewVM8D`
  - n8n draft webhook smoke returning `QUEUED_DRAFT`
  - `scripts/remote_phase3_e2e_smoke.py` on EC2
  - `python -m unittest discover -s tests`
  - `python scripts/run_offline_validations.py`
- result: PASS. Phase 3 runtime orchestration dry-run completed with final workflow state inactive, no live SSH from the n8n draft, scoped tmux cleanup, reviewer feedback written, and one Telegram summary smoke.

## 2026-05-18 - Phase 4 bounded runtime route

- pattern: Build Docker image first, run disposable container smoke with `--network none`, then add `/queue` and `/handoff` service endpoints, patch n8n Telegram command parsing, and verify EC2 queue dispatch by checking tmux session, queue completion, state, and handoff files.
- validated_by:
  - `docker build -f docker/tac-runner.Dockerfile -t tac-codex-runner:dry-run .`
  - `docker run --rm --network none --memory=2g --cpus=2 ... scripts/docker_container_smoke.py`
  - `python -m unittest discover -s tests`
  - `python scripts/run_offline_validations.py`
  - EC2 `scripts/remote_queue_route_smoke.py`
- result: PASS. `/queue` now writes a validated queue task and starts/reuses `tac-hq-runner`; the runner processed the smoke task and wrote handoff/state/report artifacts.

## Pattern: Daily Marketing HQ Schedule Activation

- applies_to: Promoting a draft local-business SNS growth routine into a scheduled TAC queue route.
- procedure: Import the inactive audit draft, import a separate active n8n schedule workflow, restart only n8n when needed for workflow registration, run one bounded queue smoke through `tac-hq-runner`, verify company report, markdown report, handoff, and notifier artifact, then redact chat ids in stored notifier response tails.
- validation: Active workflow `WorldvapeGrowth20260525` listed in n8n; smoke task `worldvape-daily-growth-smoke-20260525094702` completed PASS; notifier returned HTTP 200; `tac-hq-runner` remained running.
- rollback: Deactivate `WorldvapeGrowth20260525`, stop scoped `tac-hq-runner` if desired, and restore pending queue from the timestamped backup if the deferred old queue lines are needed.
- evidence: Applied on 2026-05-25 KST for Worldvape Gwangwoon daily Marketing HQ operations.

## 2026-05-18 - Company-mode queued work with completion notification

- pattern: Route `/work`, `/queue`, and natural Telegram text into the asynchronous queue, include chat notification metadata, let the tmux runner execute the company-style HQ wrapper, then call the n8n notify webhook for final Telegram reporting.
- validated_by:
  - `python -m unittest discover -s tests`
  - `python scripts/run_offline_validations.py`
  - local `docker build -f docker/tac-runner.Dockerfile -t tac-codex-runner:codex .`
  - local `python scripts/docker_codex_cli_smoke.py`
  - EC2 Docker Codex CLI smoke
  - EC2 `/queue -> tac-hq-runner -> company wrapper -> handoff/state/report` smoke
  - n8n notify webhook smoke without chat id
- result: PASS. Operator commands can now be queued and completed without the user staying in front of the computer; final Telegram notification is attempted automatically when the real chat id is present.

## 2026-05-19 - Local runtime engine state and telemetry expansion

- pattern: Add state-transition and telemetry primitives before attempting longer unattended runtime, then validate queue lifecycle, heartbeat, retry decision, handoff, and inactive n8n draft contracts offline.
- validated_by:
  - `python -m unittest discover -s tests`
  - `python scripts/run_offline_validations.py`
  - `python scripts/runtime_engine_smoke.py`
  - `python -m json.tool schemas/runtime_event.schema.json`
  - `python -m json.tool workflows/inactive_hq_runtime_orchestration_pack_2026-05-19.json`
- result: PASS. TAC now has local runtime primitives for queue lifecycle, runner heartbeat, retry budget decisions, telemetry JSONL events, and machine-readable handoff generation.

## 2026-05-19 - YUNA Growth Brain As Experiment System

- pattern: Treat broad Instagram growth requests as an HQ brain upgrade, not a one-off content suggestion. Store agent roles, behavioral triggers, experiment schema, sample experiment, sendoff, and validation tests before patching the live SNS workspace.
- validated_by:
  - `python -m unittest discover -s tests`
  - `python scripts/run_offline_validations.py`
  - `python -m json.tool schemas/yuna_growth_experiment.schema.json`
  - `python -m json.tool runtime/yuna_growth_experiments/sample_experiment.json`
- result: PASS. The account brain now optimizes for follows, comments, saves, shares, DM replies, profile visits, and average watch time rather than views alone.

## 2026-05-29 - Self-Repair Before Safe Fallback

- pattern: When the primary company runner returns `FAIL` or `DEFERRED_GATE`, run a bounded repair meeting and retry before writing a safe fallback report.
- validated_by:
  - `python -m py_compile scripts\hq_company_task_runner.py`
  - `python -m unittest tests.test_company_runner_safe_fallback_20260529`
  - `python -m unittest discover -s tests`
  - `python scripts\run_offline_validations.py`
- result: PASS. A missing Docker Codex auth-volume failure now loads `TAC_CODEX_AUTH_VOLUME` from local config, retries Docker Codex, can repair auth-volume ownership on permission denial, records `runtime/repair/<task_id>.repair.json`, and returns `PASS_WITH_AUTO_REPAIR` when the repaired runner passes instead of immediately falling back.

## 2026-05-29 - Project-Scale Commands Use TAC Phase Protocol

- pattern: Project-scale commands must start with a complete PROJECT plan, then proceed phase by phase after approval with self-repair, 10-sector scoring, target 97/100, original-objective reread, and final project report.
- validated_by:
  - `python -m unittest tests.test_company_runner_safe_fallback_20260529`
  - `python -m unittest discover -s tests`
  - `python scripts/run_offline_validations.py`
- result: PASS. The permanent protocol is stored in `AGENTS.md` and `SESSION_BOOT.md`, and company runner prompts now include phase scoring, 97/100 self-improvement target, original objective reread, and final report requirements.

## 2026-05-29 - Docker Codex 401 Is A Login Gate, Not A Generic Failure

- pattern: Classify `401 Unauthorized`, `Missing bearer`, and not-logged-in Codex output as an explicit Docker Codex auth `DEFERRED_GATE`.
- validated_by:
  - `python -m unittest tests.test_company_runner_safe_fallback_20260529`
  - `python -m unittest discover -s tests`
  - `python scripts/run_offline_validations.py`
- result: PASS. Docker Codex auth failures now return a clear required device-auth/login action instead of a vague `FAIL`.

## 2026-05-29 - Runtime-First Operating System Maturity Rule

- pattern: For project-scale work, classify the task by operating-system improvement category before producing new plans or documentation, and prefer runtime/automation/persistence improvements where possible.
- validated_by:
  - `python -m py_compile scripts\hq_company_task_runner.py`
  - `python -m unittest tests.test_company_runner_safe_fallback_20260529`
  - `python -m unittest discover -s tests`
  - `python scripts/run_offline_validations.py`
- result: PASS. The permanent evolution rule is stored in `AGENTS.md` and `SESSION_BOOT.md`, and company runner prompts now ask what OS capability the task improves before adding more documentation.

## 2026-05-29 - Runtime Persistence Layer

- pattern: Persist runner state, queue state, telemetry, and handoff files so a task can be recovered after interruption instead of being remembered only by a single process.
- validated_by:
  - `python -m py_compile scripts\hq_runtime_state_manager.py scripts\hq_runtime_queue_manager.py scripts\hq_runtime_telemetry.py scripts\hq_runtime_handoff.py scripts\simulate_runtime_persistence.py scripts\hq_company_task_runner.py`
  - `python -m unittest tests.test_runtime_persistence_20260529`
  - `python -m unittest discover -s tests`
  - `python scripts\run_offline_validations.py`
- result: PASS. Company runner reports now expose persistent `runtime_state_path`, `queue_path`, `telemetry_path`, and `handoff_path`, and the recovery simulation proves enqueue -> claim -> reload -> handoff -> completion.
