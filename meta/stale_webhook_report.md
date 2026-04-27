# Stale Webhook Report

Generated: 2026-04-27

## `telegram-factory-callback-v2`

Live n8n logs show repeated requests to an unregistered webhook:

`POST telegram-factory-callback-v2`

Local references found:

- `live_approval.json`
- `workflow_IY3f5KcJDMDgWRJk.json`
- `PROJECT_CONTEXT.md`

Assessment:

- This appears to be a legacy/stale Telegram callback path from the old approval handler exports.
- It is not referenced in the refreshed canonical `workflows/clean_01_generator.json` or `workflows/clean_02_approval.json`.
- No deletion was performed.

Action:

- Keep references for now as historical context.
- Before removing, confirm Telegram bot callback configuration and any active Telegram inline buttons no longer point to `telegram-factory-callback-v2`.
