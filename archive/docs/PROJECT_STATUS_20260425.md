# SNS 자동화 프로젝트 상태 업데이트 - 2026-04-25

## 현재 목적

이 프로젝트는 n8n 기반 Instagram SNS 성장 자동화 시스템이다. 핵심 목적은 콘텐츠 생성, Reel/Carousel 미디어 생성, Telegram 승인, Instagram 발행을 하나의 반복 가능한 운영 파이프라인으로 묶는 것이다.

현재 운영 원칙은 완전 자동 발행이 아니라 `Telegram Preview -> 사용자가 승인 -> Instagram Publish` 구조다. 즉, 자동화는 만들고 준비하고 검증하는 역할을 하고, 최종 게시 버튼은 사람이 누른다.

## 활성 워크플로우

| Workflow | 역할 | 현재 상태 |
| --- | --- | --- |
| `clean_01_generator` | 콘텐츠, Reel, Carousel 이미지, Telegram preview 생성 | 정상. 최신 preview-only 실행 `4095` 성공 |
| `clean_02_approval` | Telegram callback 수신, Approve Reel/Carousel 분기 | 정상. 최신 test_id의 reel URL/cache 저장 확인 |
| `clean_03_publisher` | Instagram Reel 발행 | 정상. 최근 Reel 실제 발행 성공 이력 있음 |
| `clean_04_carousel_publisher` | Instagram Carousel 발행 | 부분 준비. publish expression 문법은 수정됨. Meta limit 이후 live 재검증 필요 |

## 오늘 적용한 업데이트

### 1. Reel URL 승인 캐시 보강

- 수정 workflow: `clean_01_generator`
- 수정 node: `Cache Reel Video URL`
- 변경 내용: Reel mp4 URL이 생성되면 `clean_02_approval`로 `cache_reel` 요청을 보내 approval workflow의 staticData에도 저장되도록 보강했다.
- 이유: 기존에는 `clean_01_generator` 내부 staticData에만 reel URL이 저장되어, Telegram 승인 시 `clean_02_approval`에서 URL을 못 찾아 Reel publish가 막힐 수 있었다.

### 2. Approval workflow cache_reel 수신 추가

- 수정 workflow: `clean_02_approval`
- 수정 node: `Normalize Callback`
- 변경 내용: `action=cache_reel` 요청을 받으면 `reel_video_urls[test_id] = video_url`로 저장하도록 최소 로직을 추가했다.
- 이유: 새 Telegram preview 이후 Approve Reel이 callback payload fallback에 의존하지 않고 안정적으로 reel asset을 찾게 하기 위함이다.

### 3. Carousel final publish expression 문법 수정

- 수정 workflow: `clean_04_carousel_publisher`
- 수정 node: `IG Publish Carousel`
- 변경 내용: 깨져 있던 n8n `jsonBody` expression을 정상 형태로 복구했다.
- 이유: 이전 rollback 후 `invalid syntax`가 재발 가능한 상태였기 때문에, final publish 단계가 최소한 문법 오류로 막히지 않게 정리했다.

## 최신 검증 결과

### Preview-only generator 실행

- 실행 ID: `4095`
- 상태: success
- Telegram message_id: `803`
- Telegram Send Video 실행: 정상
- 중복 메시지: 없음
- 버튼 확인:
  - `Approve Reel`: 있음
  - `Approve Carousel`: 있음
  - `Approve (Legacy)`: 있음
  - `Regen Text`: 있음
  - `Regen Media`: 있음
  - `Delete`: 있음
- `[CAROUSEL]` block: 있음

### Approval cache 확인

- 최신 test_id: `1777088029231-u6lhvm`
- `clean_02_approval.staticData.global.reel_video_urls` 저장: 확인
- `clean_02_approval.staticData.global.carousel_payloads` 저장: 확인
- Carousel media count: 5

## 현재 안정적으로 되는 것

- Telegram preview 생성
- Reel video preview 전송
- 버튼 분리 표시
- Carousel preview block 표시
- Korean caption 표시
- Reel URL approval cache 저장
- Carousel image URL 저장
- Reel publish 경로
- Daily cap / dedupe guard 유지
- OpenAI image model 비용 절감 설정:
  - `model: gpt-image-1-mini`
  - `quality: medium`

## 아직 조심해야 하는 것

### Carousel 실제 발행

Carousel child/parent 생성은 이전에 성공했지만 final publish에서 Meta API limit 이슈가 있었다.

확인된 Meta 오류:

```text
Application request limit reached
OAuthException
code: 4
subcode: 2207051
```

따라서 Carousel live publish는 바로 반복 테스트하지 말고 cooldown 후 1회만 검증해야 한다.

### Content Strategy v2

콘텐츠 전략 v2 프롬프트 교체는 아직 적용하지 않았다. 이유는 publish 안정화와 content migration을 한 번에 섞으면 문제 발생 시 원인 분리가 어려워지기 때문이다.

## 다음 실행 계획

| 순서 | 작업 | 목적 | 승인 필요 |
| --- | --- | --- | --- |
| 1 | 사용자가 Telegram message `803`에서 `Approve Reel` 1회 클릭 | Reel 승인->발행 최종 확인 | 사용자 수동 실행 |
| 2 | Reel 게시 확인 후 execution 로그 점검 | publish success / caption / URL 검증 | 필요 |
| 3 | Meta cooldown 후 `Approve Carousel` 1회 클릭 | Carousel final publish 검증 | 사용자 수동 실행 |
| 4 | 실패 시 `clean_04`의 정확한 Meta 응답만 진단 | workflow 문제 vs Meta limit 분리 | 필요 |
| 5 | Reel/Carousel 발행 안정 확인 후 Content Strategy v2 적용 | 성장형 콘텐츠 전략으로 전환 | 별도 승인 필요 |
| 6 | v2 적용 후 preview-only 1회 실행 | JSON/content 품질 검증 | 필요 |

## 운영 판단

현재 시스템은 Reel 기준으로 운영 가능 상태다. Carousel은 준비 상태에 가까우나 Meta rate limit 이후 live publish 최종 검증이 남아 있다.

권장 운영은 다음과 같다.

1. 먼저 Reel 1개를 message `803`에서 승인한다.
2. Instagram에 즉시 올라가는지 확인한다.
3. Reel이 성공하면 Carousel은 cooldown 후 딱 1회만 테스트한다.
4. 둘 다 안정화되면 그때 콘텐츠 전략 v2를 적용한다.

## 백업

수정 전 백업 파일:

- `backup_KPa5tncCc87z2ZsE_before_operational_update_20260425_122828.json`
- `backup_i6T6ke3ltKNQzaCl_before_operational_update_20260425_122828.json`
- `backup_w9e3wiyca6qZUS4r_before_operational_update_20260425_122828.json`
