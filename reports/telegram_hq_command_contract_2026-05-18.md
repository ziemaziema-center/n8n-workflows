# Telegram HQ Command Contract - 2026-05-18

## Purpose

This contract defines the Telegram command surface for the HQ runtime layer.

Schema:

```text
schemas/telegram_hq_command.schema.json
```

## Commands

| Command | Safety Class | Live Approval Required | Expected Output |
| --- | --- | --- | --- |
| `/run <objective>` | safe_queue | false | task id, queue status, expected runner |
| `/status <task_id>` | safe_read | false | current state, latest report/log path |
| `/queue` | safe_read | false | pending/running/completed counts |
| `/pause` | control | false for local state, true for live runner | pause marker |
| `/resume` | control | false for local state, true for live runner | resume marker |
| `/killall` | control | true for live execution | kill switch result |
| `/review <task_id>` | review | false | reviewer decision |
| `/retry <task_id>` | review | false for local queue, true for live dispatch | retry queue item |
| `/handoff` | safe_read | false | continuation ledger summary |

## Validation Rules

- Command must be allowlisted.
- Task id must be explicit for status/review/retry.
- Live dispatch, live Telegram send, live SSH, workflow activation, and production restarts remain deferred gates.
- Unknown command must return a help message, not fail silently.

## Output Shape

Every command response should include:
- status
- task_id when available
- what HQ will do
- deferred gates when present
- next safe action
