# Runtime Queue Schema - 2026-05-18

## Purpose

The runtime queue schema defines one task item that n8n can write and a tmux HQ runner can consume.

The queue is intentionally file-based for the first orchestration draft:

```text
runtime/queue/pending.jsonl
runtime/queue/running.jsonl
runtime/queue/completed.jsonl
runtime/queue/failed.jsonl
```

## Files

- Schema: `schemas/runtime_queue.schema.json`
- Sample: `runtime/queue/sample_task.json`

## Required Fields

- `task_id`
- `created_at`
- `requested_by`
- `source_channel`
- `priority`
- `objective`
- `allowed_scope`
- `deferred_gates`
- `target_runner`
- `tmux_session`
- `workspace_path`
- `validation_commands`
- `expected_artifacts`
- `status`
- `retry_count`
- `max_retries`
- `continuation_ledger_path`
- `final_report_path`

## Safety

The queue item must explicitly list allowed scope and deferred gates.

If live SSH, n8n credential use, Telegram sending, Instagram publishing, Upbit credential use, production Docker restart, or secret access is required, that item is recorded in `deferred_gates` and the runner continues safe local/offline work.
