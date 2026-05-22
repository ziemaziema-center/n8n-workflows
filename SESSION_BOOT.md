# SESSION_BOOT - TRUE AUTONOMOUS CONTROLLER

## Project Identity

TRUE AUTONOMOUS CONTROLLER is a persistent autonomous orchestration layer for AWS EC2, Docker, n8n, Telegram, Codex CLI, GitHub, tmux, and the existing Instagram plus flight-deal automation stack.

This is not a single long autonomous agent run. The target is a stateful controller with planner, executor, reviewer, retryer, summarizer, escalation gate, telemetry, rollback, and bounded runtime safety.

## Target Architecture

```text
ChatGPT HQ Project
  -> n8n Orchestrator on EC2
  -> tmux-based Agent Runner
  -> Codex CLI
  -> Sandboxed Git Workspace
  -> Reviewer Agent
  -> Telegram Summary + Escalation
```

## Current Stack

- EC2 host: `43.201.227.194`
- Reverse proxy: Caddy
- n8n endpoint: `n8n.mykindredai.com`
- Existing workflows: `clean_01` through `clean_04`
- Existing reel service: FastAPI on port `8000`
- Telegram approval flows already exist
- Instagram Graph API flows already exist
- GitHub backup repository: `ziemaziema-center/n8n-workflows`

## Operating Philosophy

Autonomy does not mean no approvals. Correct model: bounded autonomy.

## Permanent Continuation Rule

Clean Korean rule:
- live/credential/network 항목 하나가 막혀도 전체 작업을 멈추지 않는다.
- 안전한 local/offline/documentation/test/scaffold/wrapper/config-template/validation 작업은 계속 진행한다.
- 막힌 항목은 `DEFERRED_GATE`로 기록하고 즉시 다음 실행 가능한 subtask로 넘어간다.
- `BLOCKED`는 전체 중단이 아니라 해당 gate만 중단이라는 뜻이다.
- 최종 보고에는 완료한 safe work, deferred gates, 다음 실행 가능한 작업을 분리해서 말한다.

Do not stop the whole task because one live/credential/network item is blocked. Continue all safe local, offline, documentation, test, scaffold, wrapper, config-template, and validation work. Convert blocked items into explicit deferred gates, then proceed to the next executable subtask.

한국어 기준:
- live/credential/network 항목 하나가 막혔다고 전체 작업을 멈추지 않는다.
- 안전한 local/offline/documentation/test/scaffold/wrapper/config-template/validation 작업은 계속 진행한다.
- 막힌 항목은 `DEFERRED_GATE`로 기록하고 즉시 다음 실행 가능한 subtask로 넘어간다.
- `BLOCKED`는 전체 중단이 아니라 해당 게이트만 중단이라는 뜻이다.
- 최종 보고는 완료한 safe work, deferred gates, 다음 실행 가능한 작업을 분리해서 말한다.

Default permissions:
- local workspace edits: auto allowed
- tests/builds: auto allowed
- reviewer retries: auto allowed within bounds
- Git commit: escalation or user-specific authorization
- production deploy: escalation
- secrets access: forbidden unless explicitly authorized for a bounded task
- AWS mutation: escalation
- destructive deletion: forbidden

## Tool Semantics To Verify Before Use

## Permanent Major-Task Runtime Rule

For every new major task:
- Estimate realistic expected completion/runtime duration first.
- Execute immediately after the estimate.
- Use the full available runtime intelligently and do not stop early while safe executable work remains.
- Do not end the whole task because one live, credential, or network surface is blocked.
- Convert blocked surfaces into `DEFERRED_GATE` records, then continue to the next executable subtask.
- Before session end, update continuation ledger, deferred gates, next executable subtasks, final report, and exact resume prompt.
- Preserve additive-only modifications, rollback safety, and deterministic auditability.

## Permanent README Language Policy

Every README created or edited in this project must include English, French, Spanish, Korean, and Chinese sections in the same file. Apply this automatically even when the user does not repeat the instruction. Third-party vendored README files are the only exception.

Codex CLI safe default:

```text
codex --ask-for-approval on-request exec --sandbox workspace-write "<prompt>"
```

Codex headless pattern:

```text
codex --ask-for-approval never exec --sandbox workspace-write --json "<prompt>"
```

Container-only full autonomy pattern:

```text
codex --dangerously-bypass-approvals-and-sandbox exec --json "<prompt>"
```

Do not assume current CLI semantics without local or official verification.

## Phase Roadmap

Phase 1:
- Telegram -> n8n -> tmux runner -> Codex -> Telegram summary

Phase 2:
- Docker-isolated runner
- workspace-only writable mount
- secret exclusion
- auto mode

Phase 3:
- planner -> executor -> reviewer loop
- retry routing
- escalation routing

Phase 4:
- persistent telemetry
- multi-agent decomposition
- unattended bounded operation
- rollback-aware orchestration

## Source KB Read At Bootstrap

Primary source KB paths:
- `C:\Users\minho\Documents\02_work\03_AI\04_agent_hq\shared_system\agent_memory\KNOWN_FAILURES.md`
- `C:\Users\minho\Documents\02_work\03_AI\04_agent_hq\shared_system\agent_memory\VALIDATED_PATTERNS.md`
- `C:\Users\minho\Documents\02_work\03_AI\04_agent_hq\shared_system\agent_memory\PATCH_HISTORY.md`
- `C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\02_execution\PATCH_HISTORY.md`
- `C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\02_execution\DAILY_EXECUTION_LOG.md`

Bootstrap finding:
- The controller workspace started empty and was not a Git repository.
- Source memory showed append-only memory accumulation, validated structured file generation, and telemetry-first execution as existing patterns.
- Existing Instagram execution logs show strong preference for bounded dry runs, no live mutation without authorization, and explicit FAILURE/SUCCESS telemetry.

## Immediate Next Implementation Target

Build the Phase 1 controller skeleton:
- Telegram intake contract
- n8n task queue and dispatcher contract
- tmux runner script
- Codex command wrapper with sandbox and timeout
- log capture path
- Telegram summary formatter
- kill switch route
- reviewer command route
- retry/escalation bounds

No EC2, n8n, Docker, or workflow mutation should happen until local contracts and dry-run validation are present.
