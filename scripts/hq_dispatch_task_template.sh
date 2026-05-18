#!/usr/bin/env bash
set -euo pipefail

# Template only. This builds the local command shape n8n SSH should run.
# It does not open SSH and does not execute on EC2 by itself.
# Default behavior is DRY_RUN=1. Set TAC_DRY_RUN=0 only inside an explicitly
# approved live SSH dispatch gate.

ROOT="${TAC_ROOT:-/home/ubuntu/workspace/true-autonomous-controller}"
SESSION="${TAC_TMUX_SESSION:-tac-hq-runner}"
QUEUE_FILE="${TAC_QUEUE_FILE:-$ROOT/runtime/queue/pending.jsonl}"
TASK_JSON="${1:-}"
DRY_RUN="${TAC_DRY_RUN:-1}"

if [[ -z "$TASK_JSON" ]]; then
  echo "missing task json" >&2
  exit 2
fi

TASK_ID="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("task_id","unknown"))')"
WORKSPACE="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("workspace_path",""))')"

case "$WORKSPACE" in
  /home/ubuntu/workspace/*) ;;
  "")
    echo "DEFERRED_GATE workspace_path_missing"
    exit 3
    ;;
  *)
    echo "DEFERRED_GATE workspace_path_not_allowed: $WORKSPACE"
    exit 4
    ;;
esac

echo "task_id=$TASK_ID"
echo "dry_run=$DRY_RUN"
echo "queue_file=$QUEUE_FILE"
echo "tmux_session=$SESSION"
echo "commands_to_run_after_live_approval:"
printf '%s\n' "cd '$ROOT'"
printf '%s\n' "mkdir -p '$(dirname "$QUEUE_FILE")'"
printf '%s\n' "printf '%s\\n' '<TASK_JSON_REPLACED_BY_N8N>' >> '$QUEUE_FILE'"
printf '%s\n' "tmux has-session -t '$SESSION' || tmux new-session -d -s '$SESSION' 'bash scripts/hq_tmux_runner_template.sh'"
printf '%s\n' "# Live SSH execution is DEFERRED_GATE until explicitly approved."

if [[ "$DRY_RUN" != "0" ]]; then
  echo "status=DRY_RUN_ONLY"
  exit 0
fi

echo "DEFERRED_GATE live_dispatch_not_implemented_in_template"
exit 5
