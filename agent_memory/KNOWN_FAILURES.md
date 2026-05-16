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
