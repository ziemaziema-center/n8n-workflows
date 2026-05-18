# Reviewer Retry Loop Draft - 2026-05-18

## Purpose

The reviewer loop inspects logs, diffs, and validation output before HQ reports success.

This draft is local/offline only.

## Template

`scripts/hq_reviewer_loop_template.py`

Inputs:
- task log path
- review output path
- max retry count
- current retry count
- optional ledger update output path

## Decisions

- `PASS`: no failure marker found and expected artifacts exist.
- `FAIL`: failure marker found; retry can continue if `retry_count < max_retries`.
- `DEFERRED_GATE`: live/credential/network gate detected; do not retry blindly.
- `HUMAN_APPROVAL_REQUIRED`: secret/credential or production mutation surface detected.

## Retry Rule

Retries are bounded:

```text
retry_count < max_retries
```

Default `max_retries` is `3`.

## Continuation Ledger Update

After every review, HQ should update:

```text
reports/hq_continuation_ledger_2026-05-18.json
```

Fields to update:
- `completed_items`
- `pending_items`
- `deferred_gates`
- `next_executable_subtasks`
- `validation_commands`

## Deferred Gates

If a task needs live SSH, live n8n credential access, live Telegram send, production workflow activation, helper restart, or Upbit credential use, the reviewer returns `DEFERRED_GATE` or `HUMAN_APPROVAL_REQUIRED` and HQ continues other safe work.

## Offline Boundary

This reviewer template does not call live LLM APIs, n8n, SSH, Telegram, Docker,
Instagram, or Upbit. It only reads local logs and writes local JSON review
artifacts. Live retry dispatch remains a deferred gate until explicitly
approved.
