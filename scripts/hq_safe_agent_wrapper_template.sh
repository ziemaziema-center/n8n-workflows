#!/usr/bin/env bash
set -euo pipefail

# Template only by default. This wrapper validates a queued task and then hands
# execution to the company-style runner. It does not read secrets and does not
# mutate production. Codex shape retained for contract validation:
# codex --ask-for-approval never exec --sandbox workspace-write --json --skip-git-repo-check

TASK_JSON="${1:-}"
if [[ -z "$TASK_JSON" ]]; then
  echo "missing task json" >&2
  exit 2
fi

TASK_ID="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("task_id","unknown"))')"
WORKSPACE="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; data=json.load(sys.stdin); print(data.get("workspace_path") or data.get("workspace") or ".")')"
PROMPT="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; data=json.load(sys.stdin); print(data.get("objective") or data.get("prompt") or "")')"
TARGET_RUNNER="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("target_runner","codex"))')"
MAX_RETRIES="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("max_retries",0))')"
STATUS="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("status","QUEUED"))')"

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

if [[ "$STATUS" != "QUEUED" && "$STATUS" != "RUNNING" ]]; then
  echo "DEFERRED_GATE invalid_task_status_for_execution: $STATUS"
  exit 5
fi

echo "task_id=$TASK_ID"
echo "workspace=$WORKSPACE"
echo "target_runner=$TARGET_RUNNER"
echo "max_retries=$MAX_RETRIES"
echo "dry_run_marker=template_guarded_execution"
echo "status=READY_FOR_BOUNDED_CODEX"

ROOT="${TAC_ROOT:-/home/ubuntu/workspace/true-autonomous-controller}"
RUNNER="$ROOT/scripts/hq_company_task_runner.py"
if [[ ! -f "$RUNNER" ]]; then
  echo "DEFERRED_GATE company_task_runner_missing: $RUNNER"
  exit 6
fi

python3 "$RUNNER" "$TASK_JSON"
