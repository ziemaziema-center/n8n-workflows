# YUNA / Instagram Session Handoff - 2026-05-22

이 문서는 현재 세션에서 나온 YUNA / Instagram 관련 내용만 뽑아 다음 Codex 세션에 넘기기 위한 handoff packet입니다.

## Scope

- 대상 프로젝트: SNS Instagram Automation / YUNA DEAL INDEX
- 주 작업공간: `C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning`
- 연결 시스템: n8n, Telegram approval flow, Instagram Graph API publisher, FastAPI reel service
- 운영 철학: YUNA를 단순 콘텐츠 캐릭터가 아니라 "전담 관련 가격 검산/소비자 판단 brain"으로 발전시킨다.

## Current Brand Direction

YUNA DEAL INDEX는 성인 전담 소비자를 위한 가격검산 캐릭터/채널이다.

핵심 포지션:
- 싼 척하는 딜을 걸러준다.
- 표시가가 아니라 실제 지불가, 용량, 배송비, 니코틴 기준, 호환성, 실패비용까지 계산한다.
- 댓글에 가격/구성/배송비/기기/카트리지 정보를 남기면 YUNA가 점수표로 다시 계산한다.

Instagram profile applied manually by user:

```text
YUNA DEAL INDEX | 전담액상 가격검산
```

Bio:

```text
전담액상 가격, 유나가 다시 계산
댓글에 가격/구성/배송비 남기면 점수화
싼 척하는 딜 걸러주는 가격검산표
```

Profile image:
- User already uploaded the YUNA profile image manually.

## Main n8n Workflows

### clean_01_generator

- Workflow name: `clean_01_generator`
- Workflow ID: `KPa5tncCc87z2ZsE`
- Active: true
- Main patched node: `Build Simulation Content`
- Purpose: Generate Telegram approval candidates for Instagram Reels.
- Current role: YUNA candidate generation brain.

Important live versions from this session:
- YUNA Growth Brain active version: `9681289c-8ed9-4369-b474-8d83ba64a8e4`
- YUNA product taxonomy mix active version: `7ddbeac2-ca84-4e50-8aa3-679fe5fdfc43`

Latest taxonomy deploy evidence:
- live code sha: `e11817d1ed039271e4d1dcf1821d7cfc87b876c3c8cbce3faaaf20e6c315172f`
- deploy report: `reports/deployments/clean01_yuna_taxonomy_mix_live_deploy_20260522_150039.md`
- backup: `backups/clean_01_generator_pre_taxonomy_mix_20260522_150039.json`

### clean_03_publisher

- Workflow name: `clean_03_publisher`
- Workflow ID: `TiD7fxWCuAX9mpt6`
- Active: true
- Purpose: Publish approved Reel payloads.

Patch already done:
- Meta `status_code=ERROR`, `Media upload has failed`, and numeric error codes are now treated as immediate terminal failures rather than waiting until timeout.
- Expected behavior: an upload error such as `Media upload has failed with error code 2207085` should surface directly instead of `error=NONE`.

Safety:
- No retry publisher was added in that patch.
- No credential value was printed.

### actual_05_instagram_comment_dm_opener

- Workflow name: `actual_05_instagram_comment_dm_opener`
- Workflow ID: `Afve1lyQgvUIpgsg`
- Active: true
- Active version: `050012f8-27c1-4a32-937f-292b122ddab5`

Purpose:
- Handle incoming Instagram comments.
- Score comments using YUNA Deal Index logic.
- Publicly reply with a DM prompt.
- Send/private-reply a YUNA price score explanation when allowed.

Live marker:

```text
yuna_deal_index_comment_score_actual05_v1
```

Public reply text:

```text
DM 확인하세요. YUNA가 댓글 기준으로 가격 검산표 보냈습니다.
```

Static data/log concepts:
- `yuna_comment_score_log`
- `dm_hot_leads`
- `yuna_comment_reply_final_log`

Known caveat:
- No fresh organic Instagram comment event was forced in the final confirmation pass.
- Latest listed executions were older webhook test runs `7271`, `7270`.

### actual_07_yuna_random_listing_scout

Telemetry says this workflow was deployed/activated earlier:
- Workflow name: `actual_07_yuna_random_listing_scout`
- Workflow ID: `ZiYzD6ote0wuMWBm`
- Schedule: 09:20, 13:20, 18:20 KST

Known role:
- Public listing scout.
- Sends captured listing/image/feed preview to Telegram.
- Later patched with JSON2Video Reel bridge.

Important note:
- clean_01 was later identified as the source of morning Telegram Reel previews, not actual07.
- actual07 is useful for public listing scout/render experiments, but clean_01 is still the main approval candidate generator.

## YUNA Growth Brain Patch

Applied to live `clean_01_generator`.

Core markers:

```text
EXPERIMENT_VERSION = "yuna_deal_index_v6_growth_brain"
GROWTH_BRAIN_VERSION = "yuna_growth_brain_hq_agents_2026_05_19"
```

Added HQ-style agent roles:
- HQ Master Controller
- 15-year SNS Marketing Strategist
- Behavioral Psychology PhD
- Content Strategist
- Data Analyst
- Automation Engineer
- Community DM Strategist
- Safety Reviewer
- QA Reviewer

Primary growth metrics:
- `follows_per_1000_reach`
- `comments_per_1000_reach`
- `dm_replies_per_1000_reach`
- `save_rate`
- `share_rate`
- `profile_visits`
- `average_watch_time`

Candidate-level fields added:
- `growth_experiment_id`
- `behavioral_trigger`
- `follow_conversion_reason`
- `save_reason`
- `comment_cta`
- `decision_rule`
- `experiment_hypothesis`

Telegram candidate should show a `YUNA Brain` block:
- Growth experiment
- Behavioral trigger
- Follow reason
- Save reason
- Comment CTA
- Decision rule

Validation done:

```text
node --check templates\clean01_consumer_growth_engine_v4.js
node tools\validate_clean01_consumer_v4_deployment_draft.js
```

Both passed during the prior application cycle.

Report:

```text
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\reports\yuna_growth_brain_live_application_20260519.md
```

## YUNA Product Taxonomy Patch

User clarified that a screenshot showed a disposable e-cigarette liquid cartridge, not just bottled e-liquid.

Required YUNA knowledge:
- 전자담배 액상
- 일회용 전자담배 기계
- 일회용 전담용 카트리지/팟
- 전자담배 디바이스 본체

Applied live to `clean_01_generator` on 2026-05-22.

Core markers:

```text
YUNA_PRODUCT_TAXONOMY_VERSION = "yuna_product_taxonomy_v1_2026_05_22"
YUNA_PRODUCT_CATEGORY_MIX_RATIO = "device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3"
```

Category definitions:

### e_liquid

Korean label:

```text
전자담배 액상
```

Definition:
- 리필형 액상.
- 병 단위 용량, 니코틴/무니코틴 표기, 배송비 포함 ml 단가, 맛 실패위험으로 점수화.

Score unit:

```text
원/ml
```

Comment prompt:

```text
댓글에 액상 가격/용량/배송비/니코틴 여부를 남기면 YUNA가 ml 단가로 다시 계산합니다.
```

### disposable_device

Korean label:

```text
일회용 전자담배 기계
```

Definition:
- 배터리, 코일, 액상이 한 몸인 올인원 일회용 기기.
- 흡입횟수, 내장 액상량, 충전 여부, 배터리/누수 리스크로 점수화.

Score unit:

```text
원/1000회 흡입 + 원/ml
```

Comment prompt:

```text
댓글에 흡입횟수/내장 ml/가격/배송비를 남기면 YUNA가 1000회당 가격으로 다시 계산합니다.
```

### disposable_cartridge

Korean label:

```text
일회용 전담용 카트리지
```

Definition:
- 전용 디바이스에 꽂는 폐쇄형/교체형 카트리지 또는 팟.
- 카트리지 수, ml, 호환 기기, 누수/잠금 생태계 리스크로 점수화.

Score unit:

```text
원/카트리지 + 원/ml
```

Comment prompt:

```text
댓글에 카트리지 개수/ml/호환기기/가격을 남기면 YUNA가 카트리지당 가격으로 다시 계산합니다.
```

### device

Korean label:

```text
전자담배 디바이스
```

Definition:
- 액상 없이 쓰는 재사용 기기 본체.
- 기기 가격, 코일/팟 소모품 비용, 호환성, 내구성, AS 리스크로 점수화.

Score unit:

```text
본체 가격 + 소모품 잠금 비용
```

Comment prompt:

```text
댓글에 기기 가격/호환 팟/코일 가격/AS 조건을 남기면 YUNA가 유지비까지 계산합니다.
```

## Product Posting Mix

User requested this exact ratio:

```text
전자담배 디바이스 1
전자담배 액상 10
일회용 전자담배 기계 7
일회용 전담용 카트리지 3
```

Implemented ratio marker:

```text
device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3
```

Implementation mode:

```text
controlled_weighted_rotation
```

YUNA category sequence includes:
- 10x e_liquid
- 7x disposable_device
- 3x disposable_cartridge
- 1x device

Known first local validation batch showed only:
- `e_liquid`
- `disposable_device`

Reason:
- clean_01 generates 4 candidates per run.
- Full 21-slot ratio appears across multiple runs, not necessarily in the first 4-item batch.

## Product Taxonomy Research Basis

Used current web research during the session.

Sources:
- CDC e-cigarette overview: `https://www.cdc.gov/tobacco/e-cigarettes/about.html`
- NIDA vaping device facts: `https://nida.nih.gov/publications/drugfacts/vaping-devices-electronic-cigarettes`
- CDC MMWR disposable device definition: `https://www.cdc.gov/mmwr/volumes/69/wr/mm6937e2.htm`
- FDA authorized ENDS product taxonomy: `https://www.fda.gov/tobacco-products/market-and-distribute-tobacco-product/e-cigarettes-vapes-and-other-electronic-nicotine-delivery-systems-ends-authorized-fda`

Practical interpretation stored for YUNA:
- E-cigarette/vape is a battery device that heats liquid into aerosol.
- E-liquid may sit in bottle, reservoir, pod, or cartridge depending on product format.
- Disposable e-cigarette means the whole device is discarded after liquid/battery use; it is not simply a cartridge.
- Prefilled cartridge/pod means a replaceable sealed liquid unit used with a compatible device.
- Reusable device body should be scored by total ownership cost, not ml unit price only.

## Validation / Deployment Results

### YUNA Product Taxonomy Mix

Commands:

```text
node --check templates\clean01_consumer_growth_engine_v4.js
node tools\validate_clean01_consumer_v4_deployment_draft.js
```

Result:
- PASS

Deployment:
- `clean_01_generator` live deploy PASS
- Active version: `7ddbeac2-ca84-4e50-8aa3-679fe5fdfc43`
- Code SHA: `e11817d1ed039271e4d1dcf1821d7cfc87b876c3c8cbce3faaaf20e6c315172f`

Report:

```text
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\reports\yuna_product_taxonomy_mix_20260522.md
```

TAC commit:

```text
4bbd369 apply yuna product taxonomy mix
```

### Webhook Observation

Webhook trigger returned:

```text
HTTP 200 / Workflow was started
```

But after 60 seconds, n8n execution list still showed latest saved clean_01 execution as old `12398`.

Interpretation:
- Live code is deployed.
- Fresh saved execution using taxonomy mix has not yet been observed.
- This is a known recurring n8n observation issue from earlier clean_01 runs.

## Important Reports and Artifacts

SNS workspace reports:

```text
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\reports\yuna_growth_brain_live_application_20260519.md
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\reports\yuna_comment_dm_and_clean03_fix_20260519.md
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\reports\yuna_product_taxonomy_mix_20260522.md
```

Deploy reports:

```text
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\reports\deployments\clean01_consumer_live_deploy_20260519_193253.md
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\reports\deployments\clean01_yuna_taxonomy_mix_live_deploy_20260522_150039.md
```

Backups:

```text
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\backups\yuna_growth_brain_20260519
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\backups\yuna_product_taxonomy_mix_20260522
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\backups\clean_01_generator_pre_taxonomy_mix_20260522_150039.json
```

Live engine snapshot:

```text
C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning\workflow_drafts\live_consumer_growth\Build_Simulation_Content_taxonomy_mix_live_20260522_150039.js
```

## Safety Status

Actions not performed during YUNA taxonomy patch:
- No Instagram publish.
- No clean03/clean04 publisher mutation.
- No credential value output.
- No Docker/nginx/server mutation.
- No AWS mutation.
- No forced live comment or DM test.

Actions performed:
- clean_01_generator `Build Simulation Content` live node update.
- n8n active workflow inspection.
- one webhook trigger smoke returning HTTP 200.
- local validation.
- reports/telemetry updates.
- TAC git commit.

## Known Gaps / Remaining Work

### 1. Confirm next actual clean_01 batch

Need check the next real Telegram approval candidates.

Expected signs:
- Candidate shows product category:
  - 전자담배 액상
  - 일회용 전자담배 기계
  - 일회용 전담용 카트리지
  - 전자담배 디바이스
- Candidate shows category-specific score unit.
- Candidate no longer treats cartridge/device as ordinary liquid bottle only.
- Candidate uses category-specific comment prompt.

### 2. Confirm full 21-slot ratio over multiple runs

One 4-item batch cannot prove the full ratio.

Need collect multiple clean_01 batches until enough items exist to check:

```text
device: 1
e_liquid: 10
disposable_device: 7
disposable_cartridge: 3
```

### 3. Real actual_05 comment test

Need one real Instagram comment event.

Expected:
- `actual_05_instagram_comment_dm_opener` runs.
- Comment is scored by YUNA.
- Public reply is posted if allowed.
- Private reply/DM opener path runs if allowed.
- Logs update.

### 4. Performance feedback loop still incomplete

YUNA now has better generation logic, but growth loop still needs real metric ingestion:
- views
- reach
- saves
- shares
- comments
- profile visits
- follows
- average watch time
- DM replies

Need store metrics by:
- experiment_id
- product_category
- hook family
- posting time
- Reel/caption variant

### 5. Competitor monitoring not fully automated

Need build or activate a competitor/account monitoring path for:
- hook patterns
- thumbnail patterns
- CTA patterns
- comment themes
- posting times
- repeated winning formats

### 6. n8n execution observation issue

Webhook can return HTTP 200 while execution list does not show a fresh saved run.

Need diagnose:
- save execution settings
- queue mode
- execution list filters
- active version behavior
- webhook response before saved execution creation

## Next Recommended Task Prompt

Use this in the next Codex session if continuing YUNA/Instagram:

```text
Continue YUNA / Instagram automation from docs/YUNA_INSTAGRAM_SESSION_HANDOFF_2026-05-22.md.

First confirm the current live clean_01_generator active version and Build Simulation Content markers:
- yuna_product_taxonomy_v1_2026_05_22
- device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3

Then inspect the latest clean_01 executions and Telegram approval payloads.
Verify whether the new product categories are visible in actual generated candidates.

If not visible, diagnose the clean_01 webhook/execution observation mismatch without touching clean03/clean04.

If visible, build the next safe layer:
- store generated candidate category history
- count category mix over multiple runs
- create daily YUNA growth metrics schema
- create a Korean daily growth report template
- add validator that category mix and taxonomy fields remain present

Do not publish to Instagram, do not send fake comments/DMs, do not print credentials, and do not mutate clean03/clean04 unless explicitly approved.

Run local validations, update telemetry, and commit safe TAC-side changes.
```

## Operator Summary

현재 YUNA는 더 이상 “전담액상만 보는 캐릭터”가 아니다.

현재 YUNA brain은 아래 4개를 구분해서 가격점수를 매기도록 live clean_01에 반영됐다:

- 전자담배 액상
- 일회용 전자담배 기계
- 일회용 전담용 카트리지/팟
- 전자담배 디바이스 본체

다만 아직 다음 실제 Telegram 후보에서 이 분류가 눈에 보이는지 최종 확인해야 한다.

