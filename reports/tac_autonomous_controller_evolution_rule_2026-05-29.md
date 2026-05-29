# TAC Autonomous Controller Evolution Rule - 2026-05-29

## Status

PASS.

## What Changed

- Stored the autonomous-controller evolution rule in `AGENTS.md`.
- Stored the autonomous-controller evolution rule in `SESSION_BOOT.md`.
- Updated the company runner prompt so project-scale tasks must ask:

```text
What part of the operating system does this improve?
```

- Added operating-system categories:
  - Runtime
  - Queue
  - Orchestration
  - Validation
  - Telemetry
  - Review
  - Retry
  - Continuation
  - Growth
  - Infrastructure
- Added priority preference to the runner prompt:
  - working runtime over new documentation
  - automation over manual process
  - persistent execution over single execution
  - operating-system capability over project-specific customization
  - maturity over superficial completion

## Validation

- `python -m py_compile scripts\hq_company_task_runner.py`: PASS
- `python -m unittest tests.test_company_runner_safe_fallback_20260529`: PASS, 9 tests
- `python -m unittest discover -s tests`: PASS, 145 tests
- `python scripts\run_offline_validations.py`: PASS

## Safety

No live n8n workflow activation, Telegram send, Instagram publish, Upbit action, production Docker restart, AWS mutation, secret read/output, force push, or destructive deletion was performed by this local patch.
