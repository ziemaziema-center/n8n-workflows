# Company Mode Runtime Completion Report - 2026-05-18

## Status

`PASS_COMPANY_MODE_RUNTIME_READY_WITH_DOCKER_AUTH_GATE`

The controller can now receive operator work through Telegram, queue it, dispatch it to the EC2 tmux runner, run the company-style HQ wrapper, write handoff/state/report artifacts, and attempt a completion notification through n8n.

## Built

- Company-style task runner: `scripts/hq_company_task_runner.py`
- Completion notifier: `scripts/hq_notify_completion.py`
- Telegram operator runbook: `docs/OPERATOR_COMPANY_MODE_RUNBOOK_2026-05-18.md`
- Docker Codex CLI smoke: `scripts/docker_codex_cli_smoke.py`
- Runtime queue notification fields in `schemas/runtime_queue.schema.json`
- `/work` and natural-language queue routing in `workflows/tac_telegram_commands.json`
- `notify` action path in `workflows/tac_controller_webhook.json`

## Verified

- Local unit tests: PASS, 59 tests.
- Offline validation runner: PASS.
- Local Docker image `tac-codex-runner:codex`: built.
- Local Docker Codex CLI no-network smoke: PASS.
- EC2 Docker image `tac-codex-runner:codex`: built.
- EC2 Docker Codex CLI no-network smoke: PASS.
- n8n `tac_telegram_commands` active graph: `/work`, `/queue`, natural text queue routing, `chat_id`, `dispatch`, and `notify_webhook_url` present.
- n8n `tac_controller_webhook` active graph: `notify` route returns a Telegram-ready Korean summary without calling the runner.
- EC2 `/queue -> tmux -> company wrapper -> handoff/state/report` smoke: PASS.
- EC2 notifier artifact: PASS/SKIPPED correctly; skipped only when chat id is absent.

## What The User Can Do Now

Send this to the Kindred AI Controller Telegram bot:

```text
/work <your task>
```

Or just send a normal message in the same bot. The controller will treat it as queued company-mode work.

## Remaining Gates

- Docker Codex can run `codex --version`, but real Codex execution inside Docker still needs a container-specific Codex auth volume. Host Codex fallback remains enabled for useful work until that auth volume is created.
- A real user-origin Telegram `/work ...` smoke still requires the user to send one message from the Telegram app so the real chat id is present.
- Multi-hour unattended soak is not yet proven.
- Fully automatic Git pre-run commit/post-pass commit for arbitrary target workspaces is not enabled because it can accidentally commit unrelated user changes.

## Exact Next Operator Command

```text
/work smoke test: 회사형 HQ 모드로 작업을 접수하고, 큐 처리 후 완료 알림까지 보내는지 확인해. 실제 운영 변경은 하지 마.
```
