# Marketing HQ Telegram Preview Send Eligibility - 2026-06-01

## Verdict
- TELEGRAM_PREVIEW_SEND_BLOCKED

## Checks
- package candidate_count == 2: PASS
- publish/render/n8n/cron path closed: PASS
- seller URL exposure exists: NO
- invented price exists: NO
- button direct publish exists: NO
- credential/secret exposure risk: PASS
- Telegram send destination configured and identifiable: FAIL

## Blocking Reason
- Telegram review destination (chat/channel) is not identifiable from local safe artifacts without credential-surface access.

## Note
- ACCOUNT_HANDLE_MISSING alone does not block preview-only flow; destination-identifiability does block actual send.

This document does not authorize Instagram publishing, image/video rendering, paid media execution, n8n live workflow changes, cron activation, clean01/clean04 execution, DM/comment automation, credential disclosure, or production changes.
