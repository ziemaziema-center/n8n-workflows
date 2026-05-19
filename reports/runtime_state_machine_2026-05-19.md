# Runtime State Machine - 2026-05-19

## Task Lifecycle

```text
QUEUED -> RUNNING -> PASS
QUEUED -> RUNNING -> FAIL -> QUEUED
QUEUED -> RUNNING -> DEFERRED_GATE
QUEUED -> CANCELLED
```

Rules:
- `FAIL -> QUEUED` is allowed only while retry budget remains.
- `DEFERRED_GATE` records the blocked live/credential/network surface and does not stop unrelated safe work.
- `PASS` and `CANCELLED` are terminal.

## Runner Lifecycle

```text
IDLE -> RUNNING -> IDLE
RUNNING -> PAUSED -> RUNNING
RUNNING -> STOPPING -> STOPPED
RUNNING -> ERROR -> IDLE
```

## Required Runtime Files

- Queue tasks: `runtime/queue/*.json`
- Pending queue: `runtime/queue/pending.jsonl`
- Completed queue: `runtime/queue/completed.jsonl`
- Runner state: `runtime/state/current_state.json`
- Runtime telemetry: `telemetry/runtime_events.jsonl`
- Audit telemetry: `telemetry/audit_events.jsonl`
- Handoff: `runtime/handoff/latest.json`

## Recovery Notes

- If tmux is running stale code, restart only `tac-hq-runner`.
- If Docker CLI smoke passes but real Codex fails, check the container-specific auth volume gate.
- If Telegram final notify is skipped, confirm the queue task contains `notification.chat_id`.
