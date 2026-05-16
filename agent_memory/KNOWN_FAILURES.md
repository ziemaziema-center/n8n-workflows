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
