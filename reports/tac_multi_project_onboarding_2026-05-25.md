# TAC Multi-Project Onboarding - 2026-05-25

## Status

`PASS_WITH_DEFERRED_GATES`

## Goal

Use the proven TRUE AUTONOMOUS CONTROLLER runtime to start company-mode work on the user's real projects:

- Upbit automation
- SNS / Instagram automation
- Flight-deal automation discovery
- TAC runtime self-hardening

## Safety Boundary

Automatically allowed:

- bounded workspace inspection
- documentation
- local/offline tests
- static workflow validation
- report generation
- scaffold/config-template improvements
- reviewer/deferred-gate classification

Still gated:

- Upbit live order/cancel/reorder
- Instagram live publishing outside the existing approval flow
- production n8n workflow activation
- production deploy/restart
- secret value reading/output
- AWS mutation
- force push

## Workspace Plan

| Project | EC2 Workspace | Status |
|---|---|---|
| TAC runtime | `/home/ubuntu/workspace/true-autonomous-controller` | ready |
| Upbit automation | `/home/ubuntu/workspace/02_upbit_automation_clean` | ready |
| SNS / Instagram automation | `/home/ubuntu/workspace/sns_automation_safe` | sync required |
| Flight-deal automation | discovery in TAC/SNS/n8n artifacts | workspace unknown |

## Execution Result

Completed:

1. Created a secret-excluding bounded archive for the local SNS automation project.
2. Synced it to EC2 and extracted it under `/home/ubuntu/workspace/sns_automation_safe`.
3. Queued TAC company-mode tasks for Upbit, SNS/Instagram, flight-deal discovery, and TAC portfolio registry.
4. Verified `tac-service` health and `tac-hq-runner` availability.
5. Verified Docker Codex workspace write behavior with host group propagation.
6. Fixed the company runner prompt so safe local/offline queue tasks must not stop at approval-only plans.
7. Generated the portfolio registry report:
   - local: `reports/hq_portfolio_registry_2026-05-25.md`
   - EC2: `/home/ubuntu/workspace/true-autonomous-controller/runtime/reports/hq_portfolio_registry_2026-05-25.md`

## Task Evidence

| Project | Task ID | Result |
|---|---|---|
| Upbit automation | `hq-upbit-company-onboarding-20260525060614` | PASS, static onboarding completed; helper contract and report-path issues found |
| SNS / Instagram automation | `hq-sns-instagram-write-enabled-20260525062532` | PASS, operator report, YUNA issue list, validation notes, next tasks, and README generated in bounded Docker workspace |
| Flight-deal discovery | `hq-flightdeal-discovery-20260525060614` | PASS, no dedicated flight-deal implementation found in readable artifacts |
| TAC portfolio registry | deterministic report generation | PASS, `hq_portfolio_registry_2026-05-25.md` generated |

## Runner Fix Applied

Issue:

- The first SNS queue run returned an approval-only plan instead of doing work.

Fix:

- Updated `scripts/hq_company_task_runner.py` so each queued company-mode task explicitly states that all safe local/offline work is already approved.
- Added a regression test in `tests/test_company_runner_prompt_20260525.py`.
- Added host group propagation to Docker Codex runs so the container user can write inside ubuntu-owned bounded workspaces without running as root.

Validation:

- Local targeted tests passed.
- EC2 targeted tests passed.
- EC2 Docker write probes passed for TAC, SNS, and Upbit bounded workspaces.

## Still Deferred

- Upbit exchange actions and authenticated runtime checks.
- Instagram live publishing outside the existing approval flow.
- Production n8n workflow activation.
- Production service/Docker restart.
- Credential value reading/output.
- AWS mutation.
- Force push.
