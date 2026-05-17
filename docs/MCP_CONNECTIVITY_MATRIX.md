# MCP Connectivity Matrix

## Operator Summary

결론: 현재 세션에서 6개 MCP를 전부 100% 연결했다고 말할 수는 없습니다.

즉시 사용 가능한 것:
- n8n MCP: 연결됨, health check 통과.
- GitHub tool/plugin: 도구는 열려 있음. 다만 이 controller repo에는 remote가 없고, `ziemaziema-center/n8n-workflows` repo 접근은 현재 connector에서 확인되지 않음.
- Filesystem: 별도 MCP는 아니지만 Codex workspace 파일 읽기/쓰기 가능.

아직 MCP로 연결되지 않은 것:
- Docker MCP: 없음. Docker CLI는 보이지만 현재 Windows Docker config 접근 권한 문제가 있음.
- PostgreSQL/SQLite MCP: 없음. `sqlite3` CLI도 현재 PATH에 없음.
- Telegram MCP: 없음. 현재 Telegram은 n8n workflow와 n8n credential을 통해 운영 중.

운영 판단:
- 오늘 바로 쓸 control plane은 `n8n MCP + Codex filesystem + 기존 n8n Telegram bot route`입니다.
- GitHub rollback/audit를 완성하려면 controller repo remote 연결 또는 GitHub connector repo 접근 권한 확인이 먼저 필요합니다.
- Docker MCP는 “컨테이너 격리형 autonomous runner” 전환 전에 별도 설치/설정해야 합니다.
- DB MCP는 task queue/execution history schema를 정한 뒤 붙이는 것이 안전합니다.

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
- status: TOOL_AVAILABLE
- evidence: GitHub plugin tools are available in the current Codex tool namespace.
- current_repo_state: local controller repository has no configured Git remote.
- repository_access_test: repository search for `ziemaziema-center/n8n-workflows` returned no visible repositories in this connector context.
- safe_use: PR/issue/file operations when a repository is accessible to the installed GitHub connector.
- constraint: controller repo needs a remote or accessible GitHub repository before GitHub MCP can provide rollback/archive on this project.

### Filesystem
- status: AVAILABLE_AS_CODEX_FILESYSTEM, not separate MCP
- evidence: Codex can read/write the trusted project workspace and use shell/apply_patch under sandbox rules.
- safe_use: memory files, reports, local artifacts, project docs.
- constraint: writes outside trusted workspace still require approval or are blocked by sandbox.

## A Grade

### Docker MCP
- status: NOT_CONNECTED_AS_MCP
- evidence: no Docker MCP tools are exposed in the current Codex tool list.
- local_capability: Docker CLI exists locally, but `C:\Users\minho\.docker\config.json` is access-denied to the current process.
- safe_use_today: shell-based Docker checks only when explicitly needed and approved.
- next_step: install/configure a dedicated Docker MCP server if container lifecycle control should be exposed as a first-class tool.

### PostgreSQL / SQLite MCP
- status: NOT_CONNECTED_AS_MCP
- evidence: no PostgreSQL/SQLite MCP tools are exposed in the current Codex tool list.
- local_capability: `sqlite3` CLI is not available on PATH in this Windows session.
- safe_use_today: Python standard library `sqlite3` can inspect local SQLite files when inside allowed workspace and not reading secrets.
- next_step: add a database MCP only after deciding the controller state store schema and credential boundary.

### Telegram MCP
- status: NOT_CONNECTED_AS_MCP
- evidence: no Telegram MCP tools are exposed in the current Codex tool list.
- current_capability: Telegram is controlled through n8n workflows and the existing `Kindred AI Controller` bot credential inside n8n.
- safe_use_today: use n8n MCP/workflows as the Telegram control plane.
- next_step: only add direct Telegram MCP if there is a clear reason to bypass n8n, because n8n currently provides audit and routing.

## Practical Conclusion

Current usable control plane:
- n8n MCP: connected and healthy.
- GitHub plugin/MCP tools: available, but target repository access is not confirmed.
- Filesystem: available through Codex workspace controls.
- Docker/PostgreSQL/SQLite/Telegram: not connected as first-class MCP tools in this session.

Recommended next connection order:
1. Add a GitHub remote for this controller repo or grant connector access to the intended repo.
2. Keep Telegram routed through n8n unless direct Telegram MCP is explicitly required.
3. Add Docker MCP before enabling true containerized autonomous execution.
4. Add database MCP after defining controller state tables.
