# Operator Company Mode Runbook - 2026-05-18

## What To Type

Use the dedicated Telegram bot: `Kindred AI Controller`.

Preferred command:

```text
/work <what you want done>
```

Natural language also works in the dedicated controller bot. If the message is not a slash command, the controller treats it as company-mode work and places it into the HQ queue.

Examples:

```text
/work 업비트 자동화 프로젝트를 오늘 끝낼 수 있게 전체 구조를 점검하고, 가능한 수정/테스트/보고까지 해.
```

```text
Insta automation을 성장 관점에서 다시 설계하고, 가능한 자동화 개선안과 테스트 계획까지 만들어.
```

## What Happens

1. Telegram receives the command.
2. n8n sends an immediate Korean receipt and plan.
3. n8n writes a validated task into the TAC runtime queue.
4. EC2 `tac-hq-runner` processes the queue in tmux.
5. The company-mode runner builds an HQ-style prompt for Codex.
6. The runner writes logs, state, handoff, and a task report.
7. If the Telegram chat id is present, the runner calls the TAC notify webhook.
8. n8n sends the final Telegram completion report.

## Current Runner Behavior

Docker image `tac-codex-runner:codex` now contains Codex CLI `0.130.0`.

Execution order for `target_runner=codex`:

1. Try Docker Codex runner when `TAC_CODEX_AUTH_VOLUME` is configured.
2. If Docker auth is not ready, use the existing bounded host Codex fallback when `TAC_ALLOW_HOST_CODEX_FALLBACK=1`.
3. Record Docker auth as a deferred gate instead of stopping the whole task.

## Still Separate Gates

- Container-specific Codex login volume.
- Production deployment/restart.
- Upbit authenticated read/order/cancel/retry.
- Instagram live publish.
- AWS infrastructure mutation.
- Force push.
- Secret reading or printing.

## Operator Rule

You should not need to stay in front of the computer for normal queued work. Send `/work ...` or natural language, then wait for the final Telegram report.
