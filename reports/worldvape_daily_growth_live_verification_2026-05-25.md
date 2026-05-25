# Worldvape Daily Growth Live Verification - 2026-05-25

## Status

`PASS_WITH_NOTED_CLI_LIMIT`

## Korean Operator Summary

월드베이프 광운대점 Marketing HQ 일일 성장 루틴은 n8n에 실제 활성화되었습니다.

현재 매일 루틴의 역할:

1. 매일 08:20 KST에 실행됩니다.
2. TAC HQ 큐에 월드베이프 Instagram/SNS 성장 작업을 넣습니다.
3. 작업 목표는 성과 확인, 경쟁/콘텐츠 패턴 정리, YUNA 후보 4개 생성, 승인용 보고서 작성, 학습 기록 반영입니다.
4. Instagram 게시, 댓글, DM 발송은 직접 하지 않습니다.
5. 완료되면 TAC notifier를 통해 Telegram 완료 보고를 시도합니다.

## Verified Live State

- Active n8n workflow:
  - `WorldvapeGrowth20260525`
  - `worldvape_daily_growth_ops_ACTIVE_2026-05-25`
- Inactive audit draft imported:
  - `inactive_worldvape_daily_growth_ops_2026-05-25`
- Scoped runner:
  - `tac-hq-runner` running
- Smoke task:
  - `worldvape-daily-growth-smoke-20260525094702`
  - status: `PASS`
- Artifacts created:
  - company runner JSON report
  - markdown task report
  - log file
  - handoff file
  - notifier artifact
- Telegram notification:
  - notifier HTTP status: `200`

## Issue Found And Fixed

The runner did not start because EC2 shell scripts had Windows CRLF line endings.

Fix:

- Normalized EC2 runner shell scripts to LF.
- Added repository `.gitattributes` so shell scripts stay LF.

## Notification Privacy Fix

The notifier artifact previously stored a Telegram response body tail that could contain a chat id.

Fix:

- `scripts/hq_notify_completion.py` now redacts chat ids in stored response tails.
- Existing smoke notifier artifact was redacted.
- Regression test added.

## n8n Manual Execute Caveat

`n8n execute --id=WorldvapeGrowth20260525` failed because the running n8n instance already owns the task broker port.

Interpretation:

- This does not mean the schedule workflow is inactive.
- The workflow is active in the n8n active workflow list.
- Queue -> runner -> report -> notifier was verified through a direct TAC queue smoke after activation.

## Deferred Queue Items

Before verification, the shared pending queue contained 37 pending lines. To avoid executing unrelated stale tasks while testing this single route, the 36 non-target pending lines were moved to a deferred backup file on EC2:

`/home/ubuntu/workspace/true-autonomous-controller/runtime/queue/pending.deferred_except_worldvape_1779703628.jsonl`

The original pending queue was backed up before modification.

## Live Operations Performed

Performed:

- Imported inactive audit draft.
- Imported and activated Worldvape daily n8n workflow.
- Restarted only the `n8n` container to register the workflow state.
- Started scoped `tac-hq-runner`.
- Ran one bounded dry-run smoke through TAC queue/runner/notifier.

Not performed:

- No Instagram publish.
- No Instagram comment/DM send.
- No credential value read or output.
- No AWS mutation.
- No unrelated workflow mutation.
- No force push.
- No destructive deletion.

## How To Use

The daily routine should now run automatically at 08:20 KST.

For manual Marketing HQ work from Telegram, send a natural instruction such as:

```text
월드베이프 광운대점 오늘 SNS 성장 회의하고, YUNA 후보 4개 만들어서 승인용 보고서 줘.
```

Publishing still requires user approval.
