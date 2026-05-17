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
