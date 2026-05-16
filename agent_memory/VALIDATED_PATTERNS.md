# Validated Patterns

## Role

This file stores reusable execution patterns validated for TRUE AUTONOMOUS CONTROLLER.

Append only unless correcting the latest entry.

## Entry Format

```text
## Pattern Name
- applies_to:
- procedure:
- validation:
- rollback:
- evidence:
```

## Pattern: Additive Bootstrap From Empty Workspace
- applies_to: New project directories with no existing local memory or source files.
- procedure: Read source KB from adjacent project memory first, then add local `AGENTS.md`, `SESSION_BOOT.md`, `agent_memory/*`, and `execution_logs/*` without modifying adjacent projects.
- validation: Confirm required files exist and include required markers for SESSION_BOOT, known failures, validated patterns, patch history, and daily execution log.
- rollback: Delete the newly added bootstrap files if the user rejects the bootstrap.
- evidence: Applied on 2026-05-16 KST after the controller workspace was found empty and non-Git.

## Pattern: Phase 1 Before Production Mutation
- applies_to: Telegram -> n8n -> tmux -> Claude/Codex runner integration.
- procedure: Define local contracts and dry-run runner behavior before changing remote EC2/n8n/Docker state.
- validation: Dry-run command wrapper must prove bounded runtime, log capture, exit status capture, summary generation, and kill-switch routing before live workflow activation.
- rollback: Remove local Phase 1 scaffold files or restore from Git checkpoint after repository initialization.
- evidence: Adopted from prior source KB preference for bounded dry runs, local recorder validation, and zero live mutation until readiness review passes.

## Pattern: Phase 3 Local-To-EC2 Bounded Validation
- applies_to: Planner -> executor -> reviewer scaffold before n8n workflow mutation.
- procedure: Implement contracts and a local dry-run controller, run local unit/smoke loops, copy only scaffold files into `/home/ubuntu/workspace/<project>` on EC2, and execute the same validation script inside tmux.
- validation: Local unit tests and smoke runs pass; EC2 tmux produces `runtime/phase3_result_remote_loop1.json` through `runtime/phase3_result_remote_loop3.json` with `status=PASS`.
- rollback: Use Git to revert local files; remove only generated files under the bounded EC2 workspace if rollback is requested.
- evidence: Validated on 2026-05-16 KST with 8/8 local tests passing and EC2 tmux validation loop x3 producing PASS results.
