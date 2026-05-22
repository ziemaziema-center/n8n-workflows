#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
cd "$PROJECT_ROOT"
mkdir -p runtime/service
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export TAC_ALLOWED_WORKSPACE_ROOTS="${TAC_ALLOWED_WORKSPACE_ROOTS:-/home/ubuntu/workspace}"
# Default to workspace-write. Host danger-full-access must be explicitly set
# only inside a reviewed isolated runner boundary.
export TAC_CODEX_SANDBOX="${TAC_CODEX_SANDBOX:-workspace-write}"
export TAC_ALLOW_HOST_CODEX_FALLBACK="${TAC_ALLOW_HOST_CODEX_FALLBACK:-0}"

HOST="${TAC_SERVICE_HOST:-0.0.0.0}"
PORT="${TAC_SERVICE_PORT:-8765}"

exec python3 -m tac.service --host "$HOST" --port "$PORT" --project-root "$PROJECT_ROOT"
