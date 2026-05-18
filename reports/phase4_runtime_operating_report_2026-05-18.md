# Phase 4 Runtime Operating Report - 2026-05-18

## Status

`PASS_PHASE_4_PARTIAL_RUNTIME_OPERATIONAL`

Phase 4 is not fully finished, but the next operating layer is now live-tested:

- Docker runner image builds.
- Docker runner can execute a disposable workspace smoke test with `--network none`.
- `/queue` and `/handoff` service endpoints exist.
- n8n `tac_telegram_commands` active workflow recognizes `/queue` and `/handoff`.
- EC2 `/queue` writes a validated queue task and starts or reuses `tac-hq-runner`.
- `tac-hq-runner` processes the queued task and writes handoff/state/report artifacts.

## Built

- `src/tac/queue_runtime.py`
- `POST /queue` in `src/tac/service.py`
- `GET/POST /handoff` in `src/tac/service.py`
- `/queue` and `/handoff` parser support in `workflows/tac_telegram_commands.json`
- `scripts/docker_container_smoke.py`
- `scripts/queue_soak_test.py`
- `scripts/git_checkpoint_manifest.py`
- `scripts/restart_tac_service_remote.sh`
- `scripts/remote_queue_route_smoke.py`

## Live Validation

Docker:

- Started Docker Desktop daemon.
- Built image: `tac-codex-runner:dry-run`
- Ran disposable workspace container:
  - network: disabled
  - memory: `2g`
  - cpus: `2`
  - secret mount: none
  - result: PASS

EC2:

- Synced service and runner scripts to `/home/ubuntu/workspace/true-autonomous-controller`.
- Restarted scoped `tac-service`.
- Ran `/queue` route smoke.
- `tac-hq-runner` tmux session started or reused.
- Latest queue smoke task: `hq-live-queue-route-smoke-20260518063721`
- Latest runner state: `IDLE` after handoff.
- Latest validation result: `PASS`.

n8n:

- Active `tac_telegram_commands` workflow was patched to parse `/queue` and `/handoff`.
- Active graph confirms queue/handoff route code is present.
- Existing validator still reports pre-existing IF node typeVersion warnings/errors for the old v1 IF node shape, but the workflow remains active and the route code is present.

## Offline Validation

- `python -m unittest discover -s tests`: PASS, 55 tests.
- `python scripts/run_offline_validations.py`: PASS.
- `python scripts/queue_soak_test.py`: PASS.
- `python scripts/git_checkpoint_manifest.py`: PASS.

## Side Effects

Performed:

- Docker Desktop started locally.
- Docker image `tac-codex-runner:dry-run` built locally.
- One disposable workspace container smoke was run.
- EC2 `tac-service` was restarted.
- EC2 `tac-hq-runner` tmux session was started/reused.
- n8n active `tac_telegram_commands` workflow parser was patched.
- Several bounded queue smoke items were appended under EC2 runtime queue.

Not performed:

- No Upbit order/read/cancel/retry.
- No Instagram publish.
- No production Docker restart on EC2.
- No AWS infrastructure mutation.
- No secret value read or output.
- No force push.

## Remaining Gates

- Docker image does not yet run real Codex CLI inside the container.
- Host-mode Codex fallback is still used for legacy `/codex` execution.
- User-origin Telegram `/queue` smoke from the Telegram app is not yet confirmed.
- Git checkpoint is a manifest generator; actual pre-run commit/post-pass commit execution is not yet wired into every task.
- Overnight unattended operation is not yet proven.

## Next Exact Task

Build the Docker Codex runner so `target_runner=codex` executes inside the container, then run a user-origin Telegram `/queue smoke` from the Telegram app and confirm:

1. Telegram receives the operator report.
2. n8n routes to `/queue`.
3. EC2 queue receives the task.
4. `tac-hq-runner` processes it.
5. handoff/report/state files are written.
6. no host secrets are mounted into the container.
