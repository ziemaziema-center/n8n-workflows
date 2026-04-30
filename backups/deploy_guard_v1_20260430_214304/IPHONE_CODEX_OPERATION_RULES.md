# iPhone Codex Operation Rules

## iPhone Role

- iPhone is for prompt creation, Codex instruction, diff review, and Telegram approval only.
- iPhone does not directly edit n8n credentials, server settings, nginx/Caddy settings, SSH configuration, or production environment variables.
- iPhone operation should keep changes small, reviewable, and reversible.

## Canonical Live Workflow Path

- Only `workflows/live/*.json` are active editable workflow exports.
- `workflows/archive/**` is read-only reference.
- `backups/**` is read-only recovery history.
- Do not patch workflow JSON from `workflows/archive/**`, `backups/**`, `tmp/**`, or root `.tmp_*` files unless the task is explicitly an archive/report cleanup.

## Safety Rules

- Backup before edit.
- One issue = one node change.
- Never modify credentials.
- Never change active, publish, or schedule settings unless explicitly approved.
- Never edit publisher workflows unless the task explicitly names the publisher workflow.
- No token, API key, cookie, credential, or access token exposure in logs, diffs, reports, or prompts.
- No auto deployment without Telegram approval.
- Do not deploy to n8n during repository preparation, diagnosis, documentation, or planning tasks.
- Preserve existing workflow JSON payload shape unless the task explicitly requires a payload migration.
- If root cause is unclear, diagnose only and stop with a one-node recommendation.

## Codex Workflow

1. Inspect the relevant files only.
2. Plan the smallest safe change.
3. Wait for approval before editing when the task is structural, workflow-affecting, or deployment-related.
4. Edit only the approved file or node.
5. Validate JSON if any JSON file is touched.
6. Report the diff summary and affected paths.
7. Do not deploy.

## Future Deployment Guard Design

Future deployment automation must use this guard sequence:

1. Detect GitHub commit.
2. Validate changed files.
3. Verify changes are limited to canonical live paths, especially `workflows/live/*.json`.
4. Check for secrets and credential exposure.
5. Create a timestamped backup of the live n8n workflow before deployment.
6. Send Telegram approval request with changed files, workflow name, and risk summary.
7. Deploy via n8n API only after Telegram approval.
8. Run a smoke test appropriate to the workflow.
9. Report success or failure to Telegram and repository logs.

Deployment guard must block automatically if:

- Changed files include credentials or server config.
- Workflow active, publish, or schedule settings changed without explicit approval.
- Publisher workflows changed but the task did not explicitly name a publisher.
- More than one workflow node changed for a one-issue task.
- Secret scan finds token/API key exposure.
- JSON validation fails.

## Standard iPhone Prompt Template

Copy and paste this template for future iPhone Codex tasks:

```text
[OBJECTIVE]
<One clear repository or workflow objective>

[SCOPE]
- Repository path: C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\02_execution
- Canonical workflow path: workflows/live/*.json
- Target workflow/file: <exact path>
- Target node if workflow edit: <exact node name>

[RULES]
- Do not deploy to n8n.
- Do not modify credentials.
- Do not expose tokens/API keys.
- Backup before editing.
- One issue = one node change.
- Do not change active/publish/schedule settings unless explicitly approved.
- Do not edit publisher workflows unless this task explicitly names the publisher.
- Preserve existing payload shape unless explicitly instructed.
- Validate JSON after edits.
- Report diff and git status.
- Do not commit unless explicitly requested.

[TASK]
1. Inspect only the relevant files.
2. Diagnose the issue or confirm the requested change.
3. Propose the smallest safe plan.
4. Wait for approval before editing if workflow-affecting.
5. After approval, patch only the target file/node.
6. Validate locally.
7. Report result.

[OUTPUT]
Return:
- files backed up
- files edited
- exact change made
- validation result
- risk
- git status
- next approval needed, if any

[STOP]
```
