# Inactive n8n Import Validation Checklist - 2026-05-18

## Scope

This checklist is for importing `workflows/inactive_hq_ssh_dispatch_draft_2026-05-18.json`
as a draft only.

## Pre-Import Checks

- Confirm workflow JSON parses locally.
- Confirm top-level `active` is `false`.
- Confirm `meta.draftOnly` is `true`.
- Confirm no node contains `credentials`.
- Confirm no SSH node executes live commands.
- Confirm the workflow only builds an `ssh_command_template`.
- Confirm Telegram output is a template only, not a live send node.

## Manual Import Steps

1. Open n8n UI.
2. Import the JSON file as a new workflow.
3. Keep the workflow inactive.
4. Inspect every node for missing credentials and draft-only behavior.
5. Do not activate, publish, or attach production credentials during this check.

## Pass Criteria

- Workflow appears in n8n UI as inactive.
- No credentials are attached.
- Webhook path is unique.
- No execution is triggered.
- No Telegram message is sent.
- No SSH command runs.

## Fail Criteria

- Workflow imports as active.
- Credentials attach automatically.
- Any node performs live SSH or Telegram send.
- Any production workflow changes state.

## Next Step After Pass

Run one separately approved live SSH dispatch test using a sample queue item.
