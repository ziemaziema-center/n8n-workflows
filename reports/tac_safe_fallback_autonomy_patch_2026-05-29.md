# TAC Safe Fallback Autonomy Patch - 2026-05-29

## Status

`PASS`

## Plain Korean Summary

문제의 핵심은 controller 원칙에는 "하나 막혀도 멈추지 말라"가 들어 있었지만, 실제 company runner는 Docker/Codex 실행이 `FAIL` 또는 `DEFERRED_GATE`가 되면 그 상태를 그대로 최종 종료로 반환했다는 점이다.

이번 패치는 그 동작을 바꾼다.

이제 Codex/Docker 실행이 막혀도, 안전한 범위에서 멈추지 않고 다음을 수행한다.

1. 원래 막힌 이유를 기록한다.
2. 막힌 live/credential/network surface만 deferred gate로 남긴다.
3. `runtime/reports/<task_id>.safe_fallback.md`에 continuation-ready fallback report를 쓴다.
4. task 상태를 `PASS_WITH_SAFE_FALLBACK`로 저장한다.
5. tmux 최종 보고서에는 실제 `company_status`와 `generated_report_path`를 표시한다.

즉, controller가 더 이상 "못함/막힘"만 말하고 멈추는 대신, 안전하게 할 수 있는 산출물을 남기고 다음에 이어갈 수 있는 상태로 끝난다.

## Changed

- `scripts/hq_company_task_runner.py`
  - Added `PASS_WITH_SAFE_FALLBACK`.
  - Added safe fallback report generation.
  - Converts blocked runner results into auditable fallback completion unless explicitly disabled.
  - Keeps original runner status/reason in the final JSON.

- `scripts/hq_tmux_runner_template.sh`
  - Adds `company_status` to the tmux markdown task report.
  - Adds `generated_report_path` when available.

- `tests/test_company_runner_safe_fallback_20260529.py`
  - Verifies blocked runner results become fallback completion.
  - Verifies tmux report exposes company status.

- `tests/test_worldvape_safe_rerun_quality_20260528.py`
  - Updated expected status from `DEFERRED_GATE` to `PASS_WITH_SAFE_FALLBACK`.

## Operator Impact

Before:

- Docker/Codex unavailable -> task ended as failed/deferred.
- User saw "blocked" and had to manually ask again.

After:

- Docker/Codex unavailable -> safe fallback report is generated.
- User gets a concrete report and next executable subtasks.
- Blocked live surfaces remain gated.

## What This Does Not Do

- It does not bypass approval gates.
- It does not publish Instagram content.
- It does not read secrets.
- It does not mutate AWS or production services.
- It does not pretend the original Codex task succeeded.

## Validation

- `python -m unittest tests.test_company_runner_safe_fallback_20260529`: PASS
- `python -m unittest tests.test_company_runner_prompt_20260525`: PASS
- `python -m unittest discover -s tests`: PASS, 138 tests
- `python scripts/run_offline_validations.py`: PASS

## Next Hardening

The next improvement should add a bounded one-retry repair loop:

1. classify local fixable failure
2. create repair task
3. run repair once
4. rerun validation
5. only then report fallback if repair still fails

This patch is the first required behavior change: no more silent stop on recoverable blocked execution.
