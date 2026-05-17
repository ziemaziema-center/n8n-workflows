# TRUE AUTONOMOUS CONTROLLER - Agent Operating Rules

## Operating Mode

Use operating mode for this project.

Required baseline:
- memory-first reasoning
- SESSION_BOOT alignment
- validation-first execution
- additive-only modifications
- post-task telemetry

Before work:
- Read `agent_memory/KNOWN_FAILURES.md`.
- Read `agent_memory/VALIDATED_PATTERNS.md`.
- Read `agent_memory/PATCH_HISTORY.md`.
- Read `SESSION_BOOT.md`.

After work:
- Append `execution_logs/DAILY_EXECUTION_LOG.md`.
- Append FAILURE/SUCCESS telemetry where relevant.
- Prefer complete, validated changes over partial patches.

## Non-Negotiable Safety

This project is a persistent autonomous orchestration system, not a generic coding task.

Preserve:
- rollback safety
- sandbox boundaries
- bounded autonomy
- explicit escalation paths
- deterministic logging and auditability
- Git checkpointing before autonomous mutation where a Git repository exists

Forbidden without explicit escalation:
- production mutation
- secret access
- unrestricted AWS mutation
- unrestricted Docker restart
- `sudo`
- `curl | sh`
- force push
- destructive deletion
- writes outside the intended workspace

Hard stops for autonomous runs:
- max iterations: 10
- max runtime: 30 minutes
- max session cost: 5 USD
- auto-pause after 3 failures
- auto-pause after 20 classifier blocks

Kill switch expectation:
- Telegram command: `/killall`
- runner action: terminate Codex agent processes only inside the bounded runner scope

## Current Project Target

Immediate milestone:

Telegram -> n8n -> tmux runner -> Codex runner -> log capture -> Telegram summary

Optimize for safe persistent orchestration, not maximum autonomy.
