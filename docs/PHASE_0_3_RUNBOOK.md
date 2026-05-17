# Phase 0-3 Local Runbook

## Scope

This runbook covers the local scaffold for:
- Phase 0: baseline, contracts, logging, rollback
- Phase 1: Telegram/n8n/tmux interface contract
- Phase 2: bounded runner semantics
- Phase 3: planner -> executor -> reviewer -> retry loop

It does not mutate EC2, n8n, Docker, Telegram, GitHub, or production workflows.

## Local Validation Command

```text
python -m unittest discover -s tests
```

## Local Smoke Run

```text
python scripts\run_phase3_loop.py examples\phase3_task.dry_run.json --out runtime\phase3_result.json
```

## EC2 Service

The semi-live MVP runs this service in a scoped tmux session:

```text
tmux new-session -d -s tac-service /home/ubuntu/workspace/true-autonomous-controller/scripts/start_tac_service.sh
```

Health check:

```text
GET http://127.0.0.1:8765/health
```

n8n container reaches the service at:

```text
http://172.17.0.1:8765/health
```

## n8n Webhook Smoke

```text
POST https://n8n.mykindredai.com/webhook/tac-controller
Body: { "text": "/run final n8n loop" }
```

Validated commands:
- `/run`
- `/codex`
- `/status <task_id>`
- `/killall`

Codex executor direct service smoke:

```json
{
  "prompt": "Return exactly TAC_SERVICE_CODEX_OK and do not modify files.",
  "source": "test",
  "executor": "codex"
}
```

Codex executor requires the EC2 runner user to be logged in:

```text
codex login status
codex login --with-api-key
```

If Codex is not logged in, `/codex` returns `BLOCKED` instead of retrying.

Webhook Codex smoke:

```text
POST https://n8n.mykindredai.com/webhook/tac-controller
Body: { "text": "/codex Return exactly TAC_WEBHOOK_CODEX_OK and do not modify files." }
```

## Live Wiring Gate

Do not wire live n8n/EC2 until all are true:
- local test suite passes
- local smoke run returns `PASS`
- Git baseline exists
- runner output JSON is written
- kill-switch command contract exists
- remote EC2 tool availability is verified with read-only commands

## Phase 3 PASS Definition

Phase 3 local scaffold passes only if:
- task spec is validated
- risk gate allows the task
- executor produces structured command results
- reviewer returns PASS
- retry loop respects configured bounds
- final result JSON is written
