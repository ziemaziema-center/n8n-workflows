#!/usr/bin/env bash
set -euo pipefail

# Template only. Do not run against production until reviewed.
# Intended tmux session: tac-hq-runner.

ROOT="${TAC_ROOT:-/home/ubuntu/workspace/true-autonomous-controller}"
QUEUE_DIR="$ROOT/runtime/queue"
LOG_DIR="$ROOT/runtime/logs"
REPORT_DIR="$ROOT/runtime/reports"
HANDOFF_DIR="$ROOT/runtime/handoff"
WRAPPER="$ROOT/scripts/hq_safe_agent_wrapper_template.sh"

mkdir -p "$QUEUE_DIR" "$LOG_DIR" "$REPORT_DIR" "$HANDOFF_DIR"
touch "$QUEUE_DIR/pending.jsonl" "$QUEUE_DIR/running.jsonl" "$QUEUE_DIR/completed.jsonl" "$QUEUE_DIR/failed.jsonl"

echo "[tac-hq-runner] started at $(date -Iseconds)"

while true; do
  if [[ ! -s "$QUEUE_DIR/pending.jsonl" ]]; then
    sleep "${TAC_QUEUE_POLL_SEC:-5}"
    continue
  fi

  task_line="$(head -n 1 "$QUEUE_DIR/pending.jsonl")"
  tail -n +2 "$QUEUE_DIR/pending.jsonl" > "$QUEUE_DIR/pending.jsonl.tmp"
  mv "$QUEUE_DIR/pending.jsonl.tmp" "$QUEUE_DIR/pending.jsonl"

  task_id="$(printf '%s' "$task_line" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("task_id","unknown"))')"
  printf '%s\n' "$task_line" >> "$QUEUE_DIR/running.jsonl"

  log_path="$LOG_DIR/${task_id}.log"
  report_path="$REPORT_DIR/${task_id}.md"

  if bash "$WRAPPER" "$task_line" > "$log_path" 2>&1; then
    printf '%s\n' "$task_line" >> "$QUEUE_DIR/completed.jsonl"
    {
      echo "# TAC Task Report"
      echo
      echo "- task_id: $task_id"
      echo "- status: PASS"
      echo "- log_path: $log_path"
    } > "$report_path"
  else
    printf '%s\n' "$task_line" >> "$QUEUE_DIR/failed.jsonl"
    {
      echo "# TAC Task Report"
      echo
      echo "- task_id: $task_id"
      echo "- status: FAIL_OR_DEFERRED"
      echo "- log_path: $log_path"
      echo "- next_action: inspect log and deferred gate registry"
    } > "$report_path"
  fi

  cat > "$HANDOFF_DIR/latest.json" <<JSON
{"task_id":"$task_id","report_path":"$report_path","log_path":"$log_path","updated_at":"$(date -Iseconds)"}
JSON
done
