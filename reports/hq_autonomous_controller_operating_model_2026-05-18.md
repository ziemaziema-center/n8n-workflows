# HQ Autonomous Controller Operating Model - 2026-05-18

## 결론

TRUE AUTONOMOUS CONTROLLER는 "한 번 길게 실행되는 Codex"가 아니라, 상태를 계속 이어받는 HQ 운영 시스템으로 동작해야 한다.

새 기준:
- 하나가 막혀도 전체 중단하지 않는다.
- 막힌 것은 `DEFERRED_GATE`로 분리한다.
- 안전한 로컬/오프라인/문서/테스트/스캐폴드 작업은 계속 진행한다.
- 다음 사이클은 continuation ledger에서 바로 이어간다.

## Internal Departments

| Department | Role | Output |
| --- | --- | --- |
| HQ / Master Controller | 목표, 위험, 우선순위, 최종 판단 | cycle plan, final decision |
| Planner | 작업 분해, 실행 순서 설계 | subtask queue |
| Builder | 파일/스크립트/템플릿 구현 | patch set |
| Reviewer | 결과 검토, 누락 확인 | review notes |
| Debugger | 실패 원인 분석, 재실행 | fix attempts |
| QA | offline validation, regression | validation report |
| Automation Engineer | n8n/tmux/Codex/Docker 연결 설계 | runtime scaffold |
| Safety Reviewer | deferred gate 분류 | gate registry |
| Documentation Writer | 사용법/보고서 작성 | docs/reports |
| Growth Strategist | Instagram 성장 전략 | growth plan |
| Final Reporter | 한국어 operator report | final report |

## Company-Style Loop

1. HQ가 user intent, allowed safe work, deferred gates를 분리한다.
2. Planner가 이번 사이클에서 실행 가능한 작업을 queue로 만든다.
3. Builder가 safe local/offline 작업을 실제로 구현한다.
4. QA가 테스트와 파일 존재 검증을 돌린다.
5. Reviewer가 빠진 요구사항과 위험을 확인한다.
6. Debugger가 실패한 offline validation을 수정한다.
7. Safety Reviewer가 live/credential/network 항목을 deferred gate로 기록한다.
8. Final Reporter가 완료/남은 일/사용법/다음 명령을 한국어로 보고한다.
9. Continuation ledger가 다음 사이클의 시작점이 된다.

## Blocked Item Handling

Blocked item은 전체 실패가 아니다.

처리 순서:
1. gate 이름을 정한다.
2. 왜 막혔는지 기록한다.
3. 필요한 승인/입력을 기록한다.
4. 그 사이 계속 진행한 safe work를 기록한다.
5. 승인 후 다음 행동을 기록한다.
6. 즉시 다음 safe subtask로 넘어간다.

## Runtime Behavior Standard

금지되는 응답 패턴:
- "하나 막혀서 전체 중단"
- "1개만 하고 다음 승인 필요"
- "지금은 못함"만 보고
- "30분 제한이라 여기서 종료"만 보고

허용되는 응답 패턴:
- "A는 deferred gate, B/C/D는 완료"
- "이번 사이클에서 가능한 safe work는 모두 처리"
- "다음 사이클은 ledger의 next_executable_subtasks부터 시작"
- "live action은 실행하지 않았음"

## Next Handoff

다음 사이클은 `reports/hq_continuation_ledger_2026-05-18.json`을 먼저 읽고 `next_executable_subtasks`부터 진행한다.
