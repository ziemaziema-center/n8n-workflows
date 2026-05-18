#!/usr/bin/env bash
set -euo pipefail

# Template only. Scoped kill switch for TAC runner sessions.
# Do not broaden this to machine-wide destructive process killing.
# Default behavior is dry-run. Set TAC_KILL_DRY_RUN=0 only after explicit
# live kill-switch approval.

SESSIONS=(
  "${TAC_HQ_SESSION:-tac-hq-runner}"
  "${TAC_CODEX_SESSION:-tac-codex-worker}"
  "${TAC_REVIEWER_SESSION:-tac-reviewer}"
)
ROOT="${TAC_ROOT:-/home/ubuntu/workspace/true-autonomous-controller}"
DRY_RUN="${TAC_KILL_DRY_RUN:-1}"

case "$ROOT" in
  /home/ubuntu/workspace/*) ;;
  *)
    echo "DEFERRED_GATE kill_switch_root_not_allowed: $ROOT"
    exit 3
    ;;
esac

for session in "${SESSIONS[@]}"; do
  if [[ "$DRY_RUN" != "0" ]]; then
    echo "dry-run would inspect/kill tmux session: $session"
    continue
  fi
  if tmux has-session -t "$session" 2>/dev/null; then
    tmux kill-session -t "$session"
    echo "killed tmux session: $session"
  else
    echo "session not running: $session"
  fi
done

if [[ "$DRY_RUN" == "0" ]]; then
  pkill -f "codex .*TRUE AUTONOMOUS CONTROLLER" 2>/dev/null || true
else
  echo "dry-run would run scoped pkill for Codex TAC process marker"
fi
echo "kill switch template completed"
