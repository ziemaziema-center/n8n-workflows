# TAC Docker Auth And Unattended Soak Start - 2026-05-24

## Status

`RUNNING`

## Completed Before Long Soak

- Built or reused Docker runner image on EC2: `tac-codex-runner:codex`.
- Created Docker-only Codex auth volume: `tac-codex-auth`.
- Completed Codex device auth inside the Docker-only volume.
- Verified `codex login status` inside the container: `Logged in using ChatGPT`.
- Ran direct Docker Codex exec smoke with the auth volume and received `DOCKER_CODEX_AUTH_VOLUME_OK`.
- Started `tac-hq-runner` with:
  - `TAC_CODEX_AUTH_VOLUME=tac-codex-auth`
  - `TAC_USE_DOCKER_CODEX=1`
  - `TAC_ALLOW_HOST_CODEX_FALLBACK=0`
- Ran preflight queue task `tac-soak-preflight3-20260524-000`.
- Preflight task completed with `runner_result.runner = docker_codex` and `status = PASS`.

## Long Soak

- Session: `tac-unattended-soak-20260524`
- EC2 path: `/home/ubuntu/workspace/true-autonomous-controller`
- Runtime: 360 minutes
- Interval: 20 minutes
- Docker Codex tasks requested: 2
- Host fallback: disabled
- Production mutation: false
- Secret value read/output: false

## Evidence Paths On EC2

- `runtime/soak/tac-unattended-soak-20260524.heartbeat.jsonl`
- `runtime/soak/tac-unattended-soak-20260524.stdout.log`
- `runtime/soak/tac-unattended-soak-20260524.final.json`
- `runtime/company_runner/tac-unattended-soak-20260524-000.json`
- `runtime/reports/tac-unattended-soak-20260524-000.md`
- `runtime/logs/tac-unattended-soak-20260524-000.log`

## Known Observation

Inside the Docker Codex container, `docker` and `tmux` are intentionally unavailable. The Docker/host orchestration evidence is therefore collected by the EC2 host runner and the company runner JSON, not by asking the nested Codex process to run Docker.

The mounted workspace is owned by `ubuntu`, so the nested `tacrunner` user can read many files but cannot write all telemetry paths. The EC2 host runner still writes task logs, company runner JSON, reports, and soak heartbeat files.

## Follow-Up

Automation `check-tac-soak-result` was created to inspect the soak after the long run window.
