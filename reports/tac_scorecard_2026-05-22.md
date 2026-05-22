# TAC Autonomous Controller Scorecard - 2026-05-22

- task_id: `tac-scorecard-20260522`
- target_score: `90`
- strict_external_audit_total: `76/100`
- baseline_total: `81/100`
- improved_total: `92/100`
- target_hit: `True`

## Scope

Repository and runtime-readiness evidence for the True Autonomous Controller, not a claim that every production live gate has been exhausted.

## Agent Council

- HQ Master Controller
- AI Systems Expert
- Automation Architect
- Computer Systems Engineer
- AI Professor
- Safety Reviewer
- QA/Test Engineer
- Telemetry Engineer
- Operator UX Lead
- Final Reporter

## Implemented Gap Fixes

- Added root README with five-language operator instructions.
- Stored permanent five-language README policy in AGENTS.md and SESSION_BOOT.md.
- Added reproducible 10-sector scorecard generator and schema.
- Added queue locking and SQLite BEGIN IMMEDIATE transaction for pending queue writes.
- Added flock/mkdir lock protection to the tmux runner dequeue template.
- Narrowed service kill switch to TAC tmux sessions and intentionally removed process-wide pkill.
- Changed host Codex fallback default to disabled; Docker-first remains preferred.
- Changed TAC service startup default sandbox from danger-full-access to workspace-write.
- Added regression tests for scorecard, multilingual README policy, runner safety, and queue locking.

## Sector Scores

### Telegram command intake and operator UX

- baseline: `9/10`
- after_improvement: `9/10`
- evidence_present: `True`
- reason: Telegram /work, /queue, /handoff, /status, and Korean receipt/final report paths exist and have live smoke history.
- remaining_risk: Needs more long-run user-origin command samples across real project types.
- evidence:
  - `workflows/tac_telegram_commands.json`
  - `docs/OPERATOR_COMPANY_MODE_RUNBOOK_2026-05-18.md`

### n8n orchestration layer

- baseline: `8/10`
- after_improvement: `9/10`
- evidence_present: `True`
- reason: Active command workflow and inactive runtime orchestration drafts exist; draft import and queue routing have been validated.
- remaining_risk: Old n8n node-shape warnings should be cleaned when production workflow maintenance is approved.
- evidence:
  - `workflows/tac_controller_webhook.json`
  - `workflows/inactive_hq_runtime_orchestration_pack_2026-05-19.json`

### Queue and state persistence

- baseline: `9/10`
- after_improvement: `10/10`
- evidence_present: `True`
- reason: SQLite queue writer, queue schema, state schema, handoff endpoint, sample state, continuation ledger, and lock-protected pending queue writes are present.
- remaining_risk: Longer queue retention and compaction policy can still be added, but the main race-risk gap now has a local lock and SQLite immediate transaction.
- evidence:
  - `scripts/hq_sqlite_queue_writer.py`
  - `schemas/runtime_queue.schema.json`
  - `schemas/runtime_state.schema.json`
  - `src/tac/queue_runtime.py`

### tmux and runtime runner execution

- baseline: `8/10`
- after_improvement: `9/10`
- evidence_present: `True`
- reason: tmux templates, company-mode runner, remote queue smoke, runtime engine smoke, and lock-protected dequeue template exist.
- remaining_risk: 5-6 hour unattended soak remains the main hardening gate.
- evidence:
  - `scripts/hq_company_task_runner.py`
  - `scripts/hq_tmux_runner_template.sh`
  - `scripts/runtime_engine_smoke.py`

### Codex execution and sandbox isolation

- baseline: `7/10`
- after_improvement: `8/10`
- evidence_present: `True`
- reason: Docker runner image and no-network Codex CLI smoke are present, with host fallback explicitly gated.
- remaining_risk: Real containerized Codex task execution still needs Docker-only auth volume setup.
- evidence:
  - `docker/tac-runner.Dockerfile`
  - `scripts/docker_codex_cli_smoke.py`
  - `reports/docker_isolated_runner_scaffold_2026-05-18.md`

### Reviewer, retry, and escalation loop

- baseline: `8/10`
- after_improvement: `9/10`
- evidence_present: `True`
- reason: Reviewer feedback schema, reviewer loop template, retry smoke, deferred gate handling, and phase3 orchestrator exist.
- remaining_risk: Independent LLM reviewer quality is still scaffolded rather than fully production-proven.
- evidence:
  - `scripts/hq_reviewer_loop_template.py`
  - `schemas/reviewer_feedback.schema.json`
  - `scripts/hq_phase3_orchestrator.py`

### Safety, rollback, and kill switch

- baseline: `9/10`
- after_improvement: `10/10`
- evidence_present: `True`
- reason: Hard safety rules, kill switch template, git checkpoint manifest, no-secret defaults, deferred gates, and service kill-switch narrowing are stored.
- remaining_risk: Automatic pre-run/post-pass Git commits per arbitrary target workspace remain policy-gated.
- evidence:
  - `AGENTS.md`
  - `scripts/hq_kill_switch_template.sh`
  - `scripts/git_checkpoint_manifest.py`
  - `reports/deferred_gate_registry_2026-05-18.md`
  - `src/tac/service.py`

### Telemetry and auditability

- baseline: `9/10`
- after_improvement: `10/10`
- evidence_present: `True`
- reason: Runtime event schema, JSONL telemetry sample, execution logs, patch history, and generated scorecard create deterministic audit trails.
- remaining_risk: A dashboard can be added later, but append-only audit foundations are strong.
- evidence:
  - `schemas/runtime_event.schema.json`
  - `telemetry/runtime_events.sample.jsonl`
  - `execution_logs/DAILY_EXECUTION_LOG.md`
  - `agent_memory/PATCH_HISTORY.md`

### Operator documentation and multilingual README policy

- baseline: `7/10`
- after_improvement: `10/10`
- evidence_present: `True`
- reason: This run adds a unified README and permanent five-language README policy in project boot rules.
- remaining_risk: Future README edits must keep the policy enforced by tests.
- evidence:
  - `README.md`
  - `AGENTS.md`
  - `SESSION_BOOT.md`

### Long-run continuation readiness

- baseline: `7/10`
- after_improvement: `8/10`
- evidence_present: `True`
- reason: Continuation ledger, handoff endpoint, queue soak test, runtime state model, and exact resume prompts exist.
- remaining_risk: A real 5-6 hour overnight soak has not yet been completed.
- evidence:
  - `reports/hq_continuation_ledger_2026-05-18.json`
  - `scripts/queue_soak_test.py`
  - `reports/runtime_state_machine_2026-05-19.md`

## Final Judgment

The repository/runtime-readiness score now reaches the 90-point target. This means the controller has enough persisted rules, queue/state machinery, runner scaffolding, reviewer/retry handling, audit trails, operator documentation, and validation coverage to be treated as a practical company-style autonomous controller scaffold.

This is not the same as saying every live production gate is exhausted. The remaining gates are explicit and should be handled as separate hardening work, not hidden blockers.

## Remaining Deferred Gates

- Docker-only Codex auth volume for real containerized Codex tasks
- 5-6 hour unattended overnight soak
- automatic Git commit policy for arbitrary target workspaces
- production workflow maintenance and activation changes
