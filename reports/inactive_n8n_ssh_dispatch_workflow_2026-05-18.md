# Inactive n8n SSH Dispatch Workflow Draft - 2026-05-18

## File

`workflows/inactive_hq_ssh_dispatch_draft_2026-05-18.json`

## Status

Inactive draft only.

This workflow must not be activated without a separate live approval gate.

## Concept

```text
Webhook or Telegram command input
  -> normalize command into queue item
  -> validate safe local/offline scope
  -> build SSH dispatch command template
  -> classify PASS/FAIL/DEFERRED_GATE
  -> return Telegram summary template placeholder
```

## Safety

The draft:
- has `"active": false`
- uses no real credentials
- has no SSH node with credentials
- does not call live n8n API
- does not send Telegram messages
- only builds an SSH command template string

## Deferred Gate

Actual SSH dispatch to EC2 remains:

```text
DEFERRED_GATE: live_ssh_dispatch_to_ec2
```
