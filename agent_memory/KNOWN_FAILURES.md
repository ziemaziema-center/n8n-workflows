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

