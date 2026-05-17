# MCP Connectivity Matrix

## Operator Summary

결론: 2026-05-17 23:00 KST 기준으로 GitHub 접근, Docker MCP 등록, SQLite state DB MCP 등록까지 진행했습니다.

즉시 사용 가능한 것:
- n8n MCP: 연결됨, health check 통과.
- GitHub tool/plugin: 도구는 열려 있고, `ziemaziema-center/n8n-workflows` commit search 접근 확인됨.
- Filesystem: 별도 MCP는 아니지만 Codex workspace 파일 읽기/쓰기 가능.
- Docker MCP: `tac-docker` 로컬 stdio MCP 서버를 repo에 추가하고 Codex config에 등록함. Docker Desktop/daemon status read 검증 통과.
- SQLite state DB MCP: `tac-state-db` 로컬 stdio MCP 서버를 repo에 추가하고 Codex config에 등록함. `runtime/controller_state.sqlite3` schema init 통과.

아직 MCP로 연결되지 않은 것:
- PostgreSQL direct MCP: 없음. 현재는 SQLite MCP를 controller state store로 사용.
- Telegram direct MCP: 없음. 현재 Telegram은 의도적으로 n8n workflow와 n8n credential을 통해 운영.

운영 판단:
- 오늘 바로 쓸 control plane은 `n8n MCP + Codex filesystem + 기존 n8n Telegram bot route`입니다.
- GitHub remote는 `n8n-workflows-backup` 이름으로 연결했습니다.
- Docker MCP는 기본적으로 mutation disabled입니다. 실제 container run은 명시적으로 `TAC_DOCKER_MCP_ALLOW_MUTATION=1`을 설정해야 가능합니다.
- DB MCP는 SQLite 기반으로 먼저 연결했습니다. PostgreSQL은 별도 DB URL/credential boundary가 정해질 때 추가합니다.

## 2026-05-17 KST Status

This document records which controller integrations are actually available to the current Codex environment.

Do not record secret values here.

## S Grade

### n8n MCP
- status: CONNECTED
- evidence: `mcp__n8n_mcp__.n8n_health_check` returned `success=true`, API status `ok`, MCP version `2.53.0`.
- configured_source: Codex local config has `mcp_servers.n8n-mcp`.
- safe_use: workflow read, validation, credential metadata, data tables, health checks, audit.
- constraint: do not expose API key values.

### GitHub MCP
- status: CONNECTOR_ACCESS_CONFIRMED
- evidence: GitHub plugin tools are available and commit search returned repository commit metadata for `ziemaziema-center/n8n-workflows`.
- current_repo_state: local controller repository has remote `n8n-workflows-backup` pointing to `https://github.com/ziemaziema-center/n8n-workflows.git`.
- repository_access_test: `git ls-remote https://github.com/ziemaziema-center/n8n-workflows.git HEAD` passed.
- safe_use: PR/issue/file operations when a repository is accessible to the installed GitHub connector.
- constraint: controller repo needs a remote or accessible GitHub repository before GitHub MCP can provide rollback/archive on this project.

### Filesystem
- status: AVAILABLE_AS_CODEX_FILESYSTEM, not separate MCP
- evidence: Codex can read/write the trusted project workspace and use shell/apply_patch under sandbox rules.
- safe_use: memory files, reports, local artifacts, project docs.
- constraint: writes outside trusted workspace still require approval or are blocked by sandbox.

## A Grade

### Docker MCP
- status: REGISTERED_FOR_NEXT_CODEX_SESSION
- evidence: `scripts/mcp/docker_mcp_server.js` implements a local stdio MCP server; `~/.codex/config.toml` has `mcp_servers.tac-docker`; MCP protocol tests pass.
- local_capability: Docker CLI and Docker Desktop daemon are available after repairing local `.docker` directory access.
- safe_use_today: read-only Docker status and run-plan generation. Container mutation is blocked unless `TAC_DOCKER_MCP_ALLOW_MUTATION=1`.
- next_step: keep mutation disabled by default; enable `TAC_DOCKER_MCP_ALLOW_MUTATION=1` only for an explicitly approved bounded container run.

### PostgreSQL / SQLite MCP
- status: SQLITE_REGISTERED_FOR_NEXT_CODEX_SESSION
- evidence: `scripts/mcp/state_db_mcp_server.py` implements a local stdio MCP server; `~/.codex/config.toml` has `mcp_servers.tac-state-db`; schema init and MCP protocol tests pass.
- local_capability: Python stdlib SQLite is used; external `sqlite3` CLI is not required.
- safe_use_today: task state, task events, artifacts, and telemetry records inside `runtime/controller_state.sqlite3`.
- next_step: add PostgreSQL only after DB URL, credential boundary, and production retention policy are decided.

### Telegram MCP
- status: INTENTIONALLY_ROUTED_THROUGH_N8N
- evidence: no direct Telegram MCP tools are exposed; current Telegram operation is through n8n TAC workflows and the `Kindred AI Controller` credential.
- current_capability: Telegram is controlled through n8n workflows and the existing `Kindred AI Controller` bot credential inside n8n.
- safe_use_today: use n8n MCP/workflows as the Telegram control plane.
- next_step: only add direct Telegram MCP if there is a clear reason to bypass n8n, because n8n currently provides audit and routing.

## Practical Conclusion

Current usable control plane:
- n8n MCP: connected and healthy.
- GitHub plugin/MCP tools: available; `ziemaziema-center/n8n-workflows` access confirmed.
- Filesystem: available through Codex workspace controls.
- Docker: local TAC Docker MCP registered for next Codex session; daemon status read validated.
- SQLite: local TAC state DB MCP registered for next Codex session.
- Telegram: intentionally routed through n8n, not direct MCP.

Recommended next connection order:
1. Restart/new Codex session to load the newly registered `tac-docker` and `tac-state-db` MCP servers.
2. Enable Docker MCP mutation only for an explicitly approved bounded container run.
3. Decide whether this controller repo should push to `n8n-workflows-backup` or a new dedicated `true-autonomous-controller` repo.
4. Keep Telegram routed through n8n unless direct Telegram MCP is explicitly required.
