#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
cd "$PROJECT_ROOT"
mkdir -p runtime/service
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

HOST="${TAC_SERVICE_HOST:-0.0.0.0}"
PORT="${TAC_SERVICE_PORT:-8765}"

exec python3 -m tac.service --host "$HOST" --port "$PORT" --project-root "$PROJECT_ROOT"
