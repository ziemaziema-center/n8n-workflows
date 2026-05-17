# Known Failures

## Role

This file records recurring operational failures for TRUE AUTONOMOUS CONTROLLER.

Append only. Do not store secrets, tokens, private keys, or credential values.

## Entry Format

```text
## YYYY-MM-DD HH:mm TZ - Failure Title
- symptom:
- cause:
- affected_files:
- detection_method:
- prevention:
- rollback_or_fix:
```

## 2026-05-16 09:00 KST - Empty Controller Workspace Has No Local Memory
- symptom: Required project memory files were not present in `05_true atonomous_controller`.
- cause: New controller project directory was empty at session start.
- affected_files: `AGENTS.md`, `SESSION_BOOT.md`, `agent_memory/*`, `execution_logs/*`.
- detection_method: `Get-ChildItem -Force` returned no files; `rg --files` returned exit code 1; `git status --short` reported not a Git repository.
- prevention: Bootstrap local memory files before implementation work and record source KB paths in `SESSION_BOOT.md`.
- rollback_or_fix: Remove newly added bootstrap files if rejected; no production, EC2, n8n, Docker, or workflow state was changed.

## 2026-05-16 18:00 KST - Python Executable Name Differs Between Windows And EC2
- symptom: EC2 validation failed while local Windows validation passed; `FileNotFoundError: [Errno 2] No such file or directory: 'python'`.
- cause: The local test used `python`, but the EC2 Ubuntu runner exposed `python3` and not `python`.
- affected_files: `src/tac/controller.py`, `tests/test_phase3_controller.py`.
- detection_method: Bounded EC2 validation script failed in `test_local_command_runs_allowlisted_python`.
- prevention: Use `sys.executable` in tests and allow both `python3` and the current executable basename in the runner allowlist.
- rollback_or_fix: Patched the allowlist and test command; copied the fix to EC2 bounded workspace; reran EC2 validation loop x3 successfully.

## 2026-05-16 18:00 KST - SCP Multi-File Target Can Misplace Files
- symptom: A test file was copied into the remote `src/tac/` directory during EC2 patch deployment.
- cause: Multi-file `scp` command used a single directory target that was correct for one source file but not for the test file.
- affected_files: Remote bounded workspace only: `/home/ubuntu/workspace/true-autonomous-controller/src/tac/test_phase3_controller.py`.
- detection_method: Manual review immediately after the copy command.
- prevention: Copy files with distinct destination paths when source files belong to different target directories.
- rollback_or_fix: Deleted only the exact misplaced generated file from the bounded EC2 workspace and recopied each file to its correct destination.

## 2026-05-16 18:05 KST - Python Cache Files Entered Initial Scaffold Commit
- symptom: `__pycache__` bytecode files were included in the first Phase 0-3 scaffold commit.
- cause: `.gitignore` did not exist before running local Python tests.
- affected_files: `src/tac/__pycache__/*`, `tests/__pycache__/*`, `.gitignore`.
- detection_method: Post-commit review of Git commit output showed `*.pyc` files.
- prevention: Add `.gitignore` before running tests in new Python repositories.
- rollback_or_fix: Added `.gitignore`, removed exact generated cache files from Git, and created cleanup commit `4f30757`.

## 2026-05-17 06:50 KST - n8n Published Workflow Requires Runtime Restart
- symptom: Newly imported and published TAC webhook returned HTTP 404 until n8n restarted.
- cause: `n8n publish:workflow` updated stored workflow state but the running process did not register the new webhook immediately.
- affected_files: `workflows/tac_controller_webhook.json`; n8n workflow `tac_controller_webhook`.
- detection_method: `POST /webhook/tac-controller` returned 404 after publish; n8n CLI warned that changes would not take effect while n8n was running.
- prevention: For CLI-imported webhook workflows, publish sequentially and restart only the n8n container after confirming the path is unique.
- rollback_or_fix: Restarted only the `n8n` container; existing workflows came back active and TAC webhook registered.

## 2026-05-17 06:51 KST - Service Patch Not Deployed Before n8n Status Test
- symptom: n8n `/status` route returned an empty body after the workflow was fixed.
- cause: Local service supported POST `/status`, but EC2 `tac-service` still ran the older service file.
- affected_files: `src/tac/service.py`.
- detection_method: Direct EC2 `POST http://127.0.0.1:8765/status` returned 404.
- prevention: Deploy service file and restart scoped `tac-service` after every service endpoint change before n8n retest.
- rollback_or_fix: Copied updated service file to EC2, restarted only `tac-service`, and `/status` passed through n8n.

## 2026-05-17 07:47 KST - JSON-Embedded JavaScript Regex Word Boundary Became Backspace
- symptom: n8n workflow JSON validated, but parser regexes contained actual backspace characters instead of JavaScript `\\b` word-boundary tokens.
- cause: Python string generation used `\\b` inside a non-raw string, which became ASCII backspace before JSON serialization.
- affected_files: `workflows/tac_controller_webhook.json`, `workflows/tac_telegram_commands.json`.
- detection_method: Python inspection found `ord(c) == 8` in `jsCode`.
- prevention: Use raw strings for JavaScript code embedded inside JSON workflows and scan generated workflow JSON for control characters before import.
- rollback_or_fix: Rewrote parser `jsCode` with raw strings, verified no backspace characters, reimported, republished, and restarted n8n.

## 2026-05-17 08:20 KST - TAC Telegram Credential Was Split Across Workflows
- symptom: `tac_telegram_commands` used the new controller credential, but `tac_controller_webhook` still referenced the old debug bot for Telegram summary sends.
- cause: Credential cutover initially updated only the Telegram Trigger workflow and missed the webhook workflow's Telegram send node.
- affected_files: `workflows/tac_controller_webhook.json`, `workflows/tac_telegram_commands.json`.
- detection_method: n8n credential usage scan showed `Kindred Debug Guard` still used by `tac_controller_webhook`.
- prevention: During bot cutover, scan all TAC workflow JSON files for old credential ID/name and use n8n credential usage with workflow references.
- rollback_or_fix: Updated both TAC workflow files to the `Kindred AI Controller` credential, reimported/reactivated both workflows, restarted only n8n, and revalidated `/run`, `/claude`, `/status`, and `/killall`.

## 2026-05-17 09:00 KST - Codex CLI Cutover Requires Current CLI Semantics And Login
- symptom: `/codex` initially failed with an unsupported approval flag location, then reached Codex CLI but failed with 401 authentication errors.
- cause: Codex CLI `0.130.0` expects `--ask-for-approval` as a global option before `exec`; the EC2 runner user also had no Codex CLI login credential.
- affected_files: `src/tac/controller.py`, `tests/test_phase3_controller.py`, `workflows/tac_controller_webhook.json`, `workflows/tac_telegram_commands.json`, `scripts/start_tac_service.sh`.
- detection_method: Webhook `/codex` smoke returned `codex-executor exited 2`; direct `codex exec --help` showed current option layout; `codex login status` returned `Not logged in`.
- prevention: Verify installed CLI help before wiring executor arguments; add Codex login preflight so authentication failures return `BLOCKED` without retry loops.
- rollback_or_fix: Updated argv to `codex --ask-for-approval never exec --sandbox workspace-write --json --skip-git-repo-check <prompt>`, installed Codex CLI on EC2, added PATH bootstrap, and added a login preflight gate.

## 2026-05-17 11:05 KST - Codex Login Status Can Pass With Invalid API Key
- symptom: `/codex` returned `FAIL` with `codex-executor exited 1` even after Codex CLI login was completed.
- cause: `codex login status` reported an API-key login, but the stored key was rejected by OpenAI API with `invalid_api_key`.
- affected_files: `src/tac/controller.py`, `tests/test_phase3_controller.py`, EC2 generated `runtime/tasks/*/result.json`.
- detection_method: Failed task result `tac-20260517015618-99fc7dea5d` showed 401 `invalid_api_key` from the Responses API.
- prevention: Treat Codex auth API errors as `BLOCKED` with escalation instead of retryable executor failures; redact API-key-like strings from command output tails before storing result JSON.
- rollback_or_fix: Added auth-error classification and output redaction; deployed to EC2; restarted `tac-service`; redacted existing EC2 runtime result JSON files.

## 2026-05-17 12:45 KST - Telegram PASS Summary Hid Codex Output
- symptom: Telegram returned `status: PASS` and task id, but did not show the actual Codex diagnosis or plan content.
- cause: Controller summary used only the reviewer status string and did not extract Codex JSONL `agent_message` text from command output.
- affected_files: `src/tac/controller.py`, `tests/test_phase3_controller.py`.
- detection_method: User received generic `PASS ... reason=all commands completed` after asking for project diagnosis and could not see the planned content.
- prevention: Extract Codex `agent_message` events from JSONL stdout and include them under `Codex output:` in the result summary returned to Telegram.
- rollback_or_fix: Added Codex output extraction and tests; deployed to EC2; restarted `tac-service`; verified Telegram/webhook summary includes the actual Codex output.

## 2026-05-17 13:00 KST - EC2 Codex Workspace Sandbox Fails With bwrap
- symptom: `/codex` reached Codex but read-only file diagnosis failed before `pwd` or memory-file reads with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`.
- cause: The EC2 kernel/container environment blocks the Codex `workspace-write` sandbox setup path.
- affected_files: `src/tac/controller.py`, `src/tac/service.py`, `scripts/start_tac_service.sh`, `tests/test_phase3_controller.py`.
- detection_method: User-provided Telegram result for task `tac-20260517034624-91d65b73bf`; direct EC2 `codex --sandbox danger-full-access` smoke confirmed host mode can read files where `workspace-write` blocks.
- prevention: Keep Docker-isolated runner as the final safety target; until then, run Codex host mode only from explicit bounded workspaces under `/home/ubuntu/workspace`, with prompt-level deny rules and Telegram escalation.
- rollback_or_fix: Added workspace extraction/allowlist, set EC2 service fallback `TAC_CODEX_SANDBOX=danger-full-access`, closed Codex stdin, expanded `/killall` to terminate Codex/Claude processes, deployed to EC2, and validated Upbit read-only smoke through n8n.

## 2026-05-17 14:15 KST - Long Telegram Codex Runs Can Finish Without Reply
- symptom: User sent a long `/codex` project task in Telegram and received no bot reply.
- cause: `tac_telegram_commands` HTTP Request timeout was 120 seconds while Codex completed after about 185 seconds; n8n disconnected before TAC service wrote the response. The controller also stored only the final stdout tail, so a long Codex `agent_message` JSON line could be truncated and omitted from `result.summary`.
- affected_files: `src/tac/controller.py`, `tests/test_phase3_controller.py`, `workflows/tac_telegram_commands.json`, `workflows/tac_controller_webhook.json`.
- detection_method: Latest task `tac-20260517044407-96cf346ad5` had a PASS `result.json`, no running Codex process, and `tac-service` showed `BrokenPipeError`.
- prevention: Keep n8n runner HTTP timeout aligned with TAC hard runtime limit; store parsed Codex `agent_text` separately from stdout tails.
- rollback_or_fix: Increased TAC workflow HTTP timeouts to 30 minutes, expanded Telegram summary allowance, added `agent_text` extraction from full stdout before truncation, deployed to EC2/n8n, restarted `tac-service` and n8n, and validated `TELEGRAM_TIMEOUT_FIX_OK`.

## 2026-05-17 14:50 KST - Telegram Follow-Up Text Was Silently Ignored
- symptom: User sent a natural follow-up approval message in the dedicated controller bot and received no response.
- cause: `tac_telegram_commands` only treated slash-prefixed `/run`, `/codex`, `/status`, and `/killall` messages as supported; ordinary text was routed to the unsupported branch with no reply.
- affected_files: `workflows/tac_telegram_commands.json`, `src/tac/controller.py`, `src/tac/service.py`, `tests/test_service_contract.py`.
- detection_method: User screenshot showed a non-slash follow-up message after a prior TAC report; workflow parser review confirmed non-slash text leaves `action` empty.
- prevention: Dedicated controller bot should treat non-slash text as a Codex follow-up, and the service should carry forward the latest bounded workspace when no explicit `WORKSPACE:` is provided.
- rollback_or_fix: Added Telegram non-slash follow-up parsing, tagged follow-up tasks, hydrated follow-up workspace from latest result, deployed to EC2/n8n, restarted `tac-service` and n8n, and validated `FOLLOWUP_WORKSPACE_OK`.

## 2026-05-17 15:10 KST - Telegram Long-Run UX Had No Received State
- symptom: User could not tell whether a Telegram `/codex` message had been accepted, ignored, or was still running.
- cause: `tac_telegram_commands` sent only the final report after the runner completed; long Codex runs therefore looked silent until completion.
- affected_files: `workflows/tac_telegram_commands.json`, `tests/test_workflow_contract.py`.
- detection_method: User screenshot showed a long run with no immediate controller feedback; latest runtime task had completed PASS, but the UI had no running/received marker.
- prevention: Telegram run commands must send a `status: RECEIVED` acknowledgement before the long runner call and include a task id plus `/status` command.
- rollback_or_fix: Added pre-run received reply, pre-generated n8n task ids, unsupported-command replies, workflow contract tests, redeployed to n8n, and validated service/status/Codex smoke.
