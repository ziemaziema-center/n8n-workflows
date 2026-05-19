# TRUE AUTONOMOUS CONTROLLER - Agent Operating Rules

## Operating Mode

Use operating mode for this project.

Required baseline:
- memory-first reasoning
- SESSION_BOOT alignment
- validation-first execution
- additive-only modifications
- post-task telemetry
- continuation-first execution when one item is blocked

Permanent continuation rule:
- Do not stop the whole task because one live/credential/network item is blocked.
- Continue all safe local, offline, documentation, test, scaffold, wrapper, config-template, and validation work.
- Convert blocked items into explicit deferred gates, then proceed to the next executable subtask.
- 한국어 기준: live/credential/network 항목 하나가 막혀도 전체 작업을 멈추지 말고, 안전한 로컬/오프라인/문서/테스트/스캐폴드/템플릿/검증 작업은 계속 진행한다. 막힌 항목만 deferred gate로 남긴 뒤 다음 실행 가능한 작업으로 넘어간다.

Before work:
- For a new major task, estimate realistic expected completion/runtime duration first.
- Read `agent_memory/KNOWN_FAILURES.md`.
- Read `agent_memory/VALIDATED_PATTERNS.md`.
- Read `agent_memory/PATCH_HISTORY.md`.
- Read `SESSION_BOOT.md`.

After work:
- Append `execution_logs/DAILY_EXECUTION_LOG.md`.
- Append FAILURE/SUCCESS telemetry where relevant.
- Update continuation ledger, deferred gates, next executable subtasks, final report, and exact resume prompt before ending a major task.
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

Do not behave like a short audit report generator. Behave like the bounded HQ layer: plan, split work, execute safe parts, review, fix, validate, record gates, and hand off the next executable step.
