#!/usr/bin/env bash
set -euo pipefail

# Template only. This wrapper validates a queued task and shows the bounded
# Codex command shape. It does not read secrets and does not mutate production.

TASK_JSON="${1:-}"
if [[ -z "$TASK_JSON" ]]; then
  echo "missing task json" >&2
  exit 2
fi

TASK_ID="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("task_id","unknown"))')"
WORKSPACE="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("workspace","."))')"
PROMPT="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))')"

case "$WORKSPACE" in
  /home/ubuntu/workspace/*) ;;
  *)
    echo "DEFERRED_GATE workspace_not_allowed: $WORKSPACE"
    exit 3
    ;;
esac

if printf '%s' "$PROMPT" | grep -Eiq '(force push|rm -rf|sudo|curl .*\|.*sh|secret|private key|aws mutation|live order|cancel order|reorder)'; then
  echo "DEFERRED_GATE forbidden_prompt_surface"
  exit 4
fi

echo "task_id=$TASK_ID"
echo "workspace=$WORKSPACE"
echo "status=READY_FOR_BOUNDED_CODEX"
echo "planned_command:"
printf '%q ' codex --ask-for-approval never exec --sandbox workspace-write --json --skip-git-repo-check "$PROMPT"
echo
