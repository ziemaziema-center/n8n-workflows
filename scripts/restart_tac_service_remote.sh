#!/usr/bin/env sh
set -eu

ROOT="${TAC_ROOT:-/home/ubuntu/workspace/true-autonomous-controller}"

tmux kill-session -t tac-service 2>/dev/null || true
cd "$ROOT"
tmux new-session -d -s tac-service ./scripts/start_tac_service.sh
sleep 2
tmux has-session -t tac-service
