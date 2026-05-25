# Worldvape Gwangwoon Daily Growth Ops - 2026-05-25

## Status

`READY_FOR_IMPORT_REVIEW`

## Plain Korean Summary

월드베이프 광운대점용 Instagram/SNS 성장 루틴을 TAC 안에 추가했다.

목표는 단순히 릴을 매일 만드는 것이 아니다. 매일 아래 순서로 돌아가는 운영 루프를 만든다.

1. 어제 성과를 본다.
2. 경쟁 계정과 전담/베이프 콘텐츠 패턴을 정리한다.
3. YUNA가 오늘 올릴 후보 4개를 만든다.
4. HQ가 팔로우, 댓글, 저장, DM, 방문 가능성 기준으로 후보를 고른다.
5. Telegram으로 사용자가 승인할 수 있게 보낸다.
6. 승인된 것만 게시 루트로 넘긴다.
7. 성과를 기록해서 다음날 생성 기준을 바꾼다.

## What Was Built

- Machine-readable routine schema:
  - `schemas/worldvape_daily_growth_routine.schema.json`
- Sample daily routine contract:
  - `runtime/worldvape_growth/sample_daily_routine.json`
- TAC queue task builder:
  - `scripts/worldvape_daily_growth_task_builder.py`
- Inactive n8n daily workflow draft:
  - `workflows/inactive_worldvape_daily_growth_ops_2026-05-25.json`
- Sendoff for future TAC/Codex sessions:
  - `docs/WORLDVAPE_GWANGWOON_GROWTH_SENDOFF_2026-05-25.md`
- Regression tests:
  - `tests/test_worldvape_daily_growth_ops_20260525.py`

## Daily HQ Routine

| Step | Owner | Output |
|---|---|---|
| Yesterday metrics | Data Analyst | reach, follows, comments, saves, shares, profile visits, DM replies |
| Competitor pattern scan | Competitor Monitor | hooks, offer framing, CTA, visible engagement, idea to adapt |
| YUNA candidate generation | Content Strategist | 4 approval candidates |
| Behavioral ranking | Behavioral Psychology Analyst | best candidate and why |
| Approval packaging | Telegram Ops | Korean approval-ready message |
| Learning update | HQ | daily memory note and next-day constraints |

## Candidate Requirements

Every daily candidate must include:

- first-frame hook
- YUNA score angle
- product category
- local customer reason
- comment CTA
- save CTA
- follow reason
- risk notes

## Topic Mix

Use the previously approved YUNA product ratio:

| Topic | Ratio |
|---|---:|
| 전자담배 액상 가격점수 | 10 |
| 일회용 전자담배 기계 가격점수 | 7 |
| 일회용 전담용 카트리지 가격점수 | 3 |
| 전자담배 디바이스 총유지비 | 1 |

## Metrics

Primary:

- follows per 1,000 reach
- profile visits per 1,000 reach
- comments per 1,000 reach
- DM replies per 1,000 reach

Secondary:

- save rate
- share rate
- average watch time
- approval accept rate

Decision rule:

- Keep a hook family only if it improves a primary metric by at least 20 percent or creates a clear store visit / DM signal.

## Deferred Gates

These were not executed:

- live Instagram publishing
- credentialed Instagram metric fetch
- live competitor scraping
- n8n workflow activation
- production service restart

## How To Use

Generate a queue task:

```powershell
python scripts\worldvape_daily_growth_task_builder.py --date 2026-05-25 --workspace /home/ubuntu/workspace/sns_automation_safe --output runtime\worldvape_growth\queue_task_20260525.json
```

Then the generated JSON can be queued through TAC `/queue` after the live scheduling route is approved.

Telegram operator wording after import/activation should be:

```text
/work WORKSPACE:/home/ubuntu/workspace/sns_automation_safe
월드베이프 광운대점 오늘의 Instagram/SNS 성장 루틴 실행.
어제 성과 확인, 경쟁 패턴 정리, YUNA 후보 4개 생성, 승인용 요약 작성, 학습 기록까지.
게시/credential 값/n8n 활성화는 승인 전 금지.
```

## Validation

Required local validation:

```powershell
python -m unittest tests.test_worldvape_daily_growth_ops_20260525
python scripts\run_offline_validations.py
```

## Live Operations

No live Instagram publish, no credential read, no n8n activation, no production restart, no AWS mutation, and no external scraping was performed.
