# SESSION_BOOT - TRUE AUTONOMOUS CONTROLLER

## Project Identity

TRUE AUTONOMOUS CONTROLLER is a persistent autonomous orchestration layer for AWS EC2, Docker, n8n, Telegram, Claude Code, Codex CLI, GitHub, tmux, and the existing Instagram plus flight-deal automation stack.

This is not a single long autonomous agent run. The target is a stateful controller with planner, executor, reviewer, retryer, summarizer, escalation gate, telemetry, rollback, and bounded runtime safety.

## Target Architecture

```text
ChatGPT HQ Project
  -> n8n Orchestrator on EC2
  -> tmux-based Agent Runner
  -> Claude Code auto OR Codex CLI
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

Codex CLI safe default:

```text
codex exec --sandbox workspace-write --ask-for-approval on-request
```

Codex headless pattern:

```text
codex exec --sandbox workspace-write --ask-for-approval never --json "<prompt>"
```

Container-only full autonomy pattern:

```text
codex exec --sandbox danger-full-access --ask-for-approval never --json "<prompt>"
```

Claude Code preferred permission mode:

```text
claude --permission-mode auto
```

Do not assume current CLI semantics without local or official verification.

## Phase Roadmap

Phase 1:
- Telegram -> n8n -> tmux runner -> Claude/Codex -> Telegram summary

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
- Codex/Claude command wrapper with sandbox and timeout
- log capture path
- Telegram summary formatter
- kill switch route
- reviewer command route
- retry/escalation bounds

No EC2, n8n, Docker, or workflow mutation should happen until local contracts and dry-run validation are present.

