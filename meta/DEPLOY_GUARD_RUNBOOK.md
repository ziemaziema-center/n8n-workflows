# Deploy Guard Runbook

## Purpose

`actual_09_mobile_codex_deploy_guard` is the planned mobile Codex deployment guard for this repository.

V1 is approval-only:

- Poll GitHub `master`.
- Detect new commits.
- Validate changed files.
- Validate one changed workflow export under `workflows/live/*.json`.
- Run a basic secret scan.
- Send a Telegram approval request.
- Record approval or rejection callbacks.
- Do not deploy to n8n.

## Current Local Files

- Workflow export: `workflows/live/actual_09_mobile_codex_deploy_guard.json`
- Runbook: `meta/DEPLOY_GUARD_RUNBOOK.md`
- iPhone operation rules: `meta/IPHONE_CODEX_OPERATION_RULES.md`

## Required Manual n8n Setup Later

Do not import this workflow until explicitly approved.

Before import, configure environment variables on the n8n host:

- `DEPLOY_GUARD_REPO=ziemaziema-center/n8n-workflows`
- `DEPLOY_GUARD_BRANCH=master`
- `DEPLOY_GUARD_GITHUB_TOKEN=<GitHub token with repo read access>`
- `DEPLOY_GUARD_TELEGRAM_BOT_TOKEN=<Telegram bot token>`
- `DEPLOY_GUARD_TELEGRAM_CHAT_ID=<approval chat id>`

No token should be placed directly in the workflow JSON.

## V1 Safety Boundaries

- No n8n API PUT node exists.
- No import/deploy is triggered by Cron.
- Approval callback records approval state only.
- Publisher workflows are blocked in V1:
  - `workflows/live/clean_03_publisher.json`
  - `workflows/live/clean_04_carousel_publisher.json`
- V1 requires exactly one changed `workflows/live/*.json` file.
- Changes outside `workflows/live/*.json` are blocked.
- Workflow JSON must parse and include `name`, `nodes`, and `connections`.
- Secret-like token patterns block the approval request path and send a blocked report.
- `active: true` in a changed workflow file is blocked in V1.

## Intended V2 Deployment Path

V2 must not be implemented without a separate approval.

The future deployment path should add, behind Telegram approval only:

1. Fetch current live workflow from n8n API.
2. Backup current live workflow export.
3. Normalize approved GitHub workflow payload.
4. Preserve current active state.
5. PUT workflow via n8n API.
6. Read back the deployed workflow.
7. Run smoke test.
8. Report result to Telegram.

## Smoke Test Policy

V1 has no smoke test because it does not deploy.

Future smoke tests must be workflow-specific:

- Non-publisher workflows: dry-run webhook or read-back validation.
- Publisher workflows: blocked unless a dedicated publisher approval protocol is created.
- Instagram publish behavior must not be touched by this guard without explicit approval.

## Manual Validation Checklist

Before importing V1 into n8n later:

- Confirm `workflows/live/actual_09_mobile_codex_deploy_guard.json` parses as JSON.
- Confirm no hardcoded token/API key exists in the workflow export.
- Confirm Cron branch is `master`.
- Confirm no n8n deploy node exists.
- Confirm approval callback does not deploy.
- Confirm Telegram variables are configured in n8n environment.

## Rollback

Because V1 is local-only until imported, rollback is file-level:

- Remove the workflow from n8n if it was imported during a future approved task.
- Restore local workflow export from the timestamped backup made before that task.
- Do not alter existing `clean_*` or `actual_07/08` workflows during rollback.
