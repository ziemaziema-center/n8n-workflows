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
