# Deferred Gate Registry - 2026-05-18

## Purpose

이 문서는 "막혔지만 전체 작업을 중단시키지 않는 항목"만 모아둔다.

Rule:
하나의 live/credential/network gate가 막혀도 전체 작업은 계속 진행한다.

## Gates

### 1. helper production deploy or restart
- status: `DEFERRED_GATE`
- why blocked: production runtime mutation이다.
- required approval/input: 배포 대상, rollback point, 재시작 허용 범위.
- safe work continued: local scaffold, docs, tests, wrapper template.
- next action after approval: pre-run git checkpoint -> deploy dry-run -> scoped restart -> health check.

### 2. Upbit authenticated read-only after IP allowlist
- status: `DEFERRED_GATE`
- why blocked: exchange credential/IP boundary가 필요하다.
- required approval/input: Upbit allowlist 완료, read-only call 범위, secret-safe execution path.
- safe work continued: Upbit live mutation 없이 growth/HQ/runtime scaffold 진행.
- next action after approval: read-only state check only -> no order/cancel/reorder.

### 3. n8n authenticated read-only
- status: `DEFERRED_GATE`
- why blocked: authenticated n8n API access가 필요하다.
- required approval/input: read-only n8n API access boundary.
- safe work continued: inactive templates and local validation.
- next action after approval: workflow/execution metadata read only -> no activation/deactivation.

### 4. live Telegram sending
- status: `DEFERRED_GATE`
- why blocked: real user-facing message can create operational confusion.
- required approval/input: target chat, exact message, send approval.
- safe work continued: non-live Telegram renderer/template work.
- next action after approval: send one test message -> verify -> stop.

### 5. live Instagram publishing
- status: `DEFERRED_GATE`
- why blocked: production account publishing affects audience/brand.
- required approval/input: content approval, publishing window, rollback/removal plan.
- safe work continued: strategy, experiment backlog, metrics plan.
- next action after approval: one controlled publish test -> metrics capture.

### 6. n8n workflow activation/deactivation or cron activation
- status: `DEFERRED_GATE`
- why blocked: production automation behavior changes.
- required approval/input: workflow id, expected trigger, rollback plan.
- safe work continued: inactive workflow templates and tests.
- next action after approval: import inactive -> validate -> activate only selected workflow.

### 7. Docker production restart
- status: `DEFERRED_GATE`
- why blocked: can interrupt production services.
- required approval/input: target container, maintenance window, rollback.
- safe work continued: Docker MCP status/read-only and run-plan scaffold.
- next action after approval: inspect -> checkpoint -> restart selected service -> health check.

### 8. secret reading or credential exposure
- status: `DEFERRED_GATE`
- why blocked: irreversible leak risk.
- required approval/input: do not read secret value; use presence/metadata only unless a secure path is explicitly defined.
- safe work continued: config templates with placeholders.
- next action after approval: use secret via environment only, never print/store.

### 9. n8n credentialed read-only check
- status: `DEFERRED_GATE`
- why blocked: authenticated n8n API access is a credential boundary.
- required approval/input: read-only credential path and exact metadata fields to inspect.
- safe work continued: inactive workflow draft and local JSON validation.
- next action after approval: inspect workflow/execution metadata only; no activation or mutation.

### 10. live SSH dispatch test
- status: `DEFERRED_GATE`
- why blocked: it executes commands against the EC2 runtime boundary.
- required approval/input: exact EC2 target, queue item, log path, rollback/kill-switch plan.
- safe work continued: inactive n8n workflow draft, SSH command template, queue schema, dry-run dispatch template.
- next action after approval: run one dry-run SSH dispatch that appends a sample queue item only.

### 11. Telegram live send test
- status: `DEFERRED_GATE`
- why blocked: it sends a real user-facing message.
- required approval/input: target chat, exact message, and one-message verification scope.
- safe work continued: Telegram command schema and summary template placeholders.
- next action after approval: send one test message, verify receipt, then stop.

### 12. EC2 tmux live session creation
- status: `DEFERRED_GATE`
- why blocked: it creates or mutates a live persistent runtime process.
- required approval/input: tmux session name, bounded workspace path, log path, kill-switch confirmation.
- safe work continued: tmux runner template, kill-switch template, runtime state schema.
- next action after approval: create one scoped `tac-hq-runner` session and verify local log/state files only.

### 13. production workflow activation
- status: `DEFERRED_GATE`
- why blocked: activation changes production automation behavior.
- required approval/input: workflow id, trigger, rollback plan, and expected output.
- safe work continued: inactive/importable workflow draft.
- next action after approval: import inactive, inspect, then activate only the selected workflow.

### 14. helper deploy/restart
- status: `DEFERRED_GATE`
- why blocked: helper deployment/restart changes production service behavior.
- required approval/input: target helper, rollback point, maintenance window, health-check command.
- safe work continued: local runtime orchestration scaffold and validation.
- next action after approval: checkpoint -> dry-run deploy plan -> scoped restart -> health check.

### 15. Upbit IP/auth read-only check
- status: `DEFERRED_GATE`
- why blocked: Upbit auth and IP allowlist are external credential boundaries.
- required approval/input: allowlist confirmation and a read-only-only command path that does not print secrets.
- safe work continued: schema, local docs, offline validation, no exchange call.
- next action after approval: perform one current-state read-only check; no order, cancel, retry, or reorder.
