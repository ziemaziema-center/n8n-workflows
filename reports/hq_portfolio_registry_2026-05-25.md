# TAC Multi-Project Company Registry - 2026-05-25

Generated at: 2026-05-25T06:33:30.903762+00:00

## Overall Status

TAC is now ready to receive company-mode work for real projects through the queue/tmux/Docker-Codex path. The path was tested with Upbit, SNS/Instagram, flight-deal discovery, and TAC portfolio registry generation.

## Registered Projects

| Project | Workspace | Current State | Safe Next Work |
|---|---|---|---|
| Upbit automation | /home/ubuntu/workspace/02_upbit_automation_clean | Onboarded. Static workflow checks pass; one helper contract issue found. | Fix helper no-journal contract, make WF05 report path writable/overrideable, add dependency-free pytest alternative. |
| SNS / Instagram automation | /home/ubuntu/workspace/sns_automation_safe plus generated /workspace/sns_automation_safe artifact path inside Docker | Onboarded. YUNA growth operator report, issue list, validation notes, next task queue, and README generated. | Continue with daily topic queue, hook scoring sheet, offline publish queue schema, weekly pattern review template. |
| Flight-deal automation | Not yet found as a dedicated workspace | Discovery completed. Only TAC queue/discovery evidence found; no actual flight workflow implementation discovered in readable artifacts. | Locate or create bounded flight-deal workspace, then build mock-fixture discovery scaffold. |
| TAC runtime | /home/ubuntu/workspace/true-autonomous-controller | Service healthy, runner active, Docker-only Codex path works, 6-hour soak passed. | Keep portfolio report generation deterministic for short jobs; use Codex for project-specific analysis. |

## Task Evidence

`json
{
  "upbit": {
    "task_id": "hq-upbit-company-onboarding-20260525060614",
    "log_exists": true,
    "runner_json_exists": true,
    "tac_report_exists": true,
    "status": "PASS",
    "runner": "docker_codex",
    "returncode": 0
  },
  "sns": {
    "task_id": "hq-sns-instagram-write-enabled-20260525062532",
    "log_exists": true,
    "runner_json_exists": true,
    "tac_report_exists": true,
    "status": "PASS",
    "runner": "docker_codex",
    "returncode": 0
  },
  "flight": {
    "task_id": "hq-flightdeal-discovery-20260525060614",
    "log_exists": true,
    "runner_json_exists": true,
    "tac_report_exists": true,
    "status": "PASS",
    "runner": "docker_codex",
    "returncode": 0
  },
  "portfolio_timeout": {
    "task_id": "hq-portfolio-registry-write-enabled-20260525062532",
    "log_exists": true,
    "runner_json_exists": false,
    "tac_report_exists": true,
    "status": "FAIL_OR_DEFERRED"
  }
}
`

## Deferred Gates

- Upbit exchange actions and authenticated runtime checks remain gated.
- Instagram live publishing and production workflow activation remain gated.
- Flight-deal external booking/API calls remain gated.
- Production n8n activation/restart remains gated.
- Credential value reading/output remains gated.

## Operator Commands

Use Telegram for normal project work:

`	ext
/work WORKSPACE:/home/ubuntu/workspace/02_upbit_automation_clean 회사형 HQ로 업비트 자동화 안전 개선 계속 진행. 실거래/credential 값/n8n 활성화 없이 로컬 테스트와 보고서까지.
`

`	ext
/work WORKSPACE:/home/ubuntu/workspace/sns_automation_safe 회사형 HQ로 YUNA 인스타 성장 루프 개선. 게시/credential 값/n8n 활성화 없이 안전 산출물, 검증, 다음 작업 큐 생성.
`

`	ext
/work WORKSPACE:/home/ubuntu/workspace/true-autonomous-controller 비행기딜 자동화 workspace를 찾고 없으면 mock-fixture 기반 bounded scaffold를 제안/생성. 외부 예약 API와 credential 값은 금지.
`

## Live Operations

No Upbit exchange action, Instagram publish, production n8n activation, production restart, AWS mutation, or credential value output was performed.
