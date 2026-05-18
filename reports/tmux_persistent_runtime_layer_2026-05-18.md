# tmux Persistent Runtime Layer Scaffold - 2026-05-18

## Goal

Create the base layer for:

```text
Telegram -> n8n -> SSH dispatch -> tmux queue/runner -> Codex -> logs -> summary -> Telegram
```

This document is scaffold only. No live production operation was executed.

## Proposed EC2 Layout

```text
/home/ubuntu/workspace/true-autonomous-controller/
  runtime/
    queue/
      pending.jsonl
      running.jsonl
      completed.jsonl
      failed.jsonl
    logs/
      <task_id>.log
    reports/
      <task_id>.md
    handoff/
      latest.json
  scripts/
    hq_tmux_runner_template.sh
    hq_safe_agent_wrapper_template.sh
```

## tmux Sessions

Recommended session names:
- `tac-hq-runner`
- `tac-codex-worker`
- `tac-reviewer`

## Queue Flow

1. n8n writes a task JSON line into `runtime/queue/pending.jsonl`.
2. `tac-hq-runner` picks the next task.
3. wrapper validates workspace, denylist, timeout, and task id.
4. Codex runs inside bounded workspace.
5. stdout/stderr are captured under `runtime/logs`.
6. reviewer validates output.
7. summary is written under `runtime/reports`.
8. handoff is updated under `runtime/handoff/latest.json`.
9. n8n reads summary and sends Telegram report.

## Kill Switch

Expected safe kill behavior:

```bash
tmux kill-session -t tac-codex-worker
tmux kill-session -t tac-reviewer
pkill -f "codex .*TRUE AUTONOMOUS CONTROLLER" || true
```

Do not use broad machine-wide destructive commands.

## n8n SSH Dispatch Draft

Command shape:

```bash
cd /home/ubuntu/workspace/true-autonomous-controller
printf '%s\n' '<TASK_JSON>' >> runtime/queue/pending.jsonl
tmux has-session -t tac-hq-runner || tmux new-session -d -s tac-hq-runner 'bash scripts/hq_tmux_runner_template.sh'
```

## Telegram Command Draft

```text
/run <task>
/codex <task>
/status <task_id>
/killall
/pause
/resume
/retry <task_id>
/review <task_id>
```

## Deferred Gates

Not executed:
- SSH dispatch to EC2
- live n8n workflow activation
- Telegram send
- production Docker restart
- live Codex long run
