#!/usr/bin/env bash
set -euo pipefail

# Template only. Do not run against production until reviewed.
# Intended tmux session: tac-hq-runner.

ROOT="${TAC_ROOT:-/home/ubuntu/workspace/true-autonomous-controller}"
QUEUE_DIR="$ROOT/runtime/queue"
LOG_DIR="$ROOT/runtime/logs"
REPORT_DIR="$ROOT/runtime/reports"
HANDOFF_DIR="$ROOT/runtime/handoff"
STATE_DIR="$ROOT/runtime/state"
WRAPPER="$ROOT/scripts/hq_safe_agent_wrapper_template.sh"
NOTIFIER="$ROOT/scripts/hq_notify_completion.py"
STATE_FILE="$STATE_DIR/current_state.json"

mkdir -p "$QUEUE_DIR" "$LOG_DIR" "$REPORT_DIR" "$HANDOFF_DIR" "$STATE_DIR"
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
  cat > "$STATE_FILE" <<JSON
{"active_task_id":"$task_id","runner_status":"RUNNING","current_phase":"executing_wrapper","last_heartbeat_at":"$(date -Iseconds)","last_log_path":"$log_path","last_validation_result":{"status":"NOT_RUN","command":null,"checked_at":null},"blocked_gates":[],"safe_next_actions":["wait for wrapper result"],"kill_switch_status":{"enabled":true,"last_triggered_at":null,"command":"/killall"}}
JSON

  if bash "$WRAPPER" "$task_line" > "$log_path" 2>&1; then
    printf '%s\n' "$task_line" >> "$QUEUE_DIR/completed.jsonl"
    {
      echo "# TAC Task Report"
      echo
      echo "- task_id: $task_id"
      echo "- status: PASS"
      echo "- log_path: $log_path"
    } > "$report_path"
    result_status="PASS"
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
    result_status="DEFERRED_GATE"
  fi

  notify_path="$REPORT_DIR/${task_id}.notify.json"
  if [[ -f "$NOTIFIER" ]]; then
    python3 "$NOTIFIER" "$task_line" "$report_path" "$log_path" "$result_status" > "$notify_path" 2>&1 || true
  else
    printf '{"status":"SKIPPED","reason":"notifier_missing"}\n' > "$notify_path"
  fi

  cat > "$HANDOFF_DIR/latest.json" <<JSON
{"task_id":"$task_id","report_path":"$report_path","log_path":"$log_path","notify_path":"$notify_path","updated_at":"$(date -Iseconds)"}
JSON
  cat > "$STATE_FILE" <<JSON
{"active_task_id":null,"runner_status":"IDLE","current_phase":"handoff_written","last_heartbeat_at":"$(date -Iseconds)","last_log_path":"$log_path","last_validation_result":{"status":"$result_status","command":"bash $WRAPPER","checked_at":"$(date -Iseconds)"},"blocked_gates":[],"safe_next_actions":["read $HANDOFF_DIR/latest.json","Telegram notification is attempted automatically when notification webhook is present"],"kill_switch_status":{"enabled":true,"last_triggered_at":null,"command":"/killall"}}
JSON
done
