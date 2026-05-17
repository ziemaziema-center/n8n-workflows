# Controller State DB Schema

## Purpose

This SQLite schema is the first controller state store for bounded autonomous operation.

It records:
- task queue state
- execution timeline
- generated artifacts
- telemetry and failure clustering inputs

It does not store:
- secret values
- API keys
- Telegram bot tokens
- exchange keys
- raw credential payloads

## Default Location

Local Codex MCP config uses:

```text
runtime/controller_state.sqlite3
```

The database is created by `scripts/mcp/state_db_mcp_server.py` through the `init_state_db` tool.

## Tables

### tasks

One row per TAC task.

Fields:
- `task_id`: stable TAC task id.
- `source`: Telegram, n8n, local, or another source.
- `workspace`: bounded workspace path when known.
- `status`: `RECEIVED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, or another explicit state.
- `requested_at`, `started_at`, `finished_at`: ISO timestamps.
- `summary`: operator-readable task summary.
- `risk_level`: expected risk class.
- `approvals_json`: approval metadata only, not secret values.
- `metadata_json`: non-secret structured metadata.

### task_events

Append-only timeline for each task.

Typical events:
- `PLANNED`
- `DISPATCHED`
- `AGENT_MESSAGE`
- `VALIDATION_PASS`
- `VALIDATION_FAIL`
- `ESCALATED`
- `REPORTED`

### artifacts

Tracks reports, patches, logs, and generated files.

Each row can include a SHA-256 hash for auditability.

### telemetry

Append-only controller telemetry for success/failure learning.

Typical categories:
- `mcp`
- `runner`
- `telegram`
- `n8n`
- `git`
- `docker`
- `db`
- `safety`

## Safety Rule

The DB MCP must only write inside `TAC_STATE_ROOT`.

If a requested DB path escapes that root, the MCP server blocks the operation.
