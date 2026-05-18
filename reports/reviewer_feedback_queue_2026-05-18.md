# Reviewer Feedback Queue - 2026-05-18

## Purpose

The reviewer feedback queue records one JSON object per line after a runner cycle.
HQ reads these events before deciding whether to retry, continue safe work, or ask
for a live gate approval.

## Files

- Schema: `schemas/reviewer_feedback.schema.json`
- Sample JSONL: `runtime/reviewer_feedback/sample_feedback.jsonl`

## Decisions

- `PASS`: report success and update ledger.
- `FAIL`: retry only when `retry_allowed` is true and retry count is inside bounds.
- `DEFERRED_GATE`: do not treat the whole task as failed; continue safe work.
- `HUMAN_APPROVAL_REQUIRED`: stop only the unsafe action and report exact approval needed.

## Safety

Reviewer feedback must not include secret values, raw credentials, Telegram tokens,
exchange keys, or private keys. It should reference logs by path, not paste large
raw logs into Telegram.
