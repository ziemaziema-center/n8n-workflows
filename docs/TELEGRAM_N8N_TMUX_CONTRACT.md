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

The production implementation must scope process matching to the runner context before use.

