# Docker-Isolated Runner Scaffold - 2026-05-18

## Status

`SCAFFOLD_READY_NOT_PRODUCTION`

## Files

- Dockerfile: `docker/tac-runner.Dockerfile`
- Plan generator: `scripts/docker_isolated_runner_plan.py`
- Generated plan: `runtime/docker_runner_plan_2026-05-18.json`

## Boundary

The runner container must mount only the bounded project workspace:

```text
/home/ubuntu/workspace/<project>:/workspace
```

It must not mount:

- `$HOME`
- `.ssh`
- `.aws`
- `.env`
- credential directories
- Docker socket

## Default Execution

Default network is disabled:

```text
--network=none
```

Enable network only for an explicitly approved task.

## Not Done Yet

- The image was not deployed to production.
- Codex login/credential is not baked into the image.
- No production container was started.

## Next Step

Build the image in a controlled environment, then run one containerized dry-run
task against a disposable workspace copy before replacing the current host-mode
EC2 fallback.
