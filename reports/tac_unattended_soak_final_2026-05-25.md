# TAC Unattended Soak Final - 2026-05-25

## Status

`PASS`

## What Was Verified

- Docker-only Codex auth volume exists: `tac-codex-auth`.
- Container Codex login status: `Logged in using ChatGPT`.
- Direct Docker Codex exec smoke returned `DOCKER_CODEX_AUTH_VOLUME_OK`.
- Long soak session: `tac-unattended-soak-20260524`.
- Requested duration: 360 minutes.
- Actual recorded window: `2026-05-24T03:58:28Z` to `2026-05-24T09:58:28Z`.
- Heartbeat reached `21600.83` seconds.
- Tasks enqueued during soak: 18.
- Soak task reports with `PASS`: 18.
- Soak task reports with `FAIL`: 0.
- Host Codex fallback: disabled.
- Docker Codex tasks requested: true.
- Production mutation: false.

## Evidence On EC2

- `/home/ubuntu/workspace/true-autonomous-controller/runtime/soak/tac-unattended-soak-20260524.final.json`
- `/home/ubuntu/workspace/true-autonomous-controller/runtime/soak/tac-unattended-soak-20260524.heartbeat.jsonl`
- `/home/ubuntu/workspace/true-autonomous-controller/runtime/reports/tac-unattended-soak-20260524-000.md` through `017.md`
- `/home/ubuntu/workspace/true-autonomous-controller/runtime/company_runner/tac-unattended-soak-20260524-000.json` through `017.json`

## Interpretation

The remaining hardening gates from the prior TAC scorecard are now closed at the runtime-evidence level:

- Docker-only Codex auth volume: passed.
- Containerized Codex execution: passed.
- 5-6 hour unattended queue soak: passed.

This does not mean unsafe production actions should become automatic. Production deploy, workflow activation, secret access, AWS mutation, live Instagram publishing, and Upbit live operations remain explicit approval gates.
