# Telegram / n8n / tmux Contract

## Telegram Commands

```text
/run <task text>
/status <task_id>
/killall
```

## n8n Responsibilities

- Receive Telegram command.
- Convert the command into `task_spec.schema.json`.
- Dispatch task spec to the runner.
- Read runner JSON result.
- Send summary back to Telegram.
- Route `RISK` or `BLOCKED` to human escalation.

## Current Semi-Live MVP

Current active n8n workflow:

```text
tac_controller_webhook
```

Current production webhook:

```text
POST https://n8n.mykindredai.com/webhook/tac-controller
```

Accepted request bodies:

```json
{ "text": "/run final smoke" }
{ "text": "/status tac-..." }
{ "text": "/killall" }
```

Optional Telegram-style body:

```json
{
  "message": {
    "text": "/run final smoke",
    "chat": { "id": "..." }
  }
}
```

The workflow calls:

```text
http://172.17.0.1:8765/run
http://172.17.0.1:8765/status
http://172.17.0.1:8765/killall
```

## Runner Boundary

Runner accepts only a task spec file path and returns a runner result JSON.

```text
python scripts/run_phase3_loop.py <task_spec.json> --out <result.json>
```

## tmux Live Shape

Live tmux wiring is not enabled by this scaffold. Expected future shape:

```text
tmux new-session -d -s tac-runner-<task_id> '<bounded runner command>'
```

## Kill Switch

Telegram:

```text
/killall
```

Bounded action:

```text
pkill -f claude
pkill -f codex
```

Current implementation scopes kill behavior to `tmux` sessions named `tac-task-*`.
