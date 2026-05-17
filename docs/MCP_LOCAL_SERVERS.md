# Local TAC MCP Servers

## Registered Servers

Two local stdio MCP servers were added for TRUE AUTONOMOUS CONTROLLER.

They are registered in local Codex config:

```text
~/.codex/config.toml
```

Do not store secret values in this repo or in MCP config docs.

## tac-docker

Script:

```text
scripts/mcp/docker_mcp_server.js
```

Purpose:
- Docker status checks
- container list checks
- bounded `docker run` command planning
- optionally execute a bounded container only after explicit mutation enablement

Default safety:

```text
TAC_DOCKER_MCP_ALLOW_MUTATION=0
```

This means the MCP can plan container execution but will not run containers by default.

Mutation requires:

```text
TAC_DOCKER_MCP_ALLOW_MUTATION=1
```

and Docker daemon must be running.

## tac-state-db

Script:

```text
scripts/mcp/state_db_mcp_server.py
```

Purpose:
- initialize controller state DB
- record task state
- append task events
- record artifacts
- record telemetry
- list and fetch task state

Default DB:

```text
runtime/controller_state.sqlite3
```

Safety:
- DB writes are blocked if the configured DB path escapes `TAC_STATE_ROOT`.
- No secret values should be stored.

## Telegram

No direct Telegram MCP was added.

Telegram remains intentionally routed through:

```text
Telegram -> n8n TAC workflows -> TAC service -> Codex -> n8n -> Telegram
```

Reason:
- n8n already holds the Telegram credential.
- n8n gives workflow auditability.
- direct Telegram MCP would duplicate routing and increase secret exposure unless a clear need appears.

## GitHub

GitHub connector access to `ziemaziema-center/n8n-workflows` was verified through the GitHub plugin.

Local Git remote added:

```text
n8n-workflows-backup -> https://github.com/ziemaziema-center/n8n-workflows.git
```

This remote is intentionally named, not `origin`, so the controller repo does not accidentally push to the workflow backup repo without a deliberate command.
