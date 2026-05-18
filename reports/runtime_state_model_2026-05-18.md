# Runtime State Model - 2026-05-18

## Purpose

The runtime state file is the lightweight status surface for the HQ runner.

It gives n8n, Telegram, and reviewers a deterministic way to inspect:
- active task
- runner status
- heartbeat
- latest log path
- latest validation result
- blocked gates
- safe next actions
- kill switch status

## Files

- Schema: `schemas/runtime_state.schema.json`
- Sample: `runtime/state/sample_state.json`

## State Flow

```text
IDLE -> RUNNING -> PASS/FAIL/DEFERRED_GATE -> IDLE
```

`DEFERRED_GATE` does not mean the full HQ cycle stopped.

It means a live/credential/network surface is held for later approval while safe work continues.
