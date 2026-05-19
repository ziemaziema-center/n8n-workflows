# YUNA Brain Growth System - 2026-05-19

## Status

`PASS_LOCAL_STRATEGY_SYSTEM`

No live Instagram publishing, live DM test, credential read, or production workflow mutation was performed in this cycle.

## Current Problem

The automation can generate and publish approved reels, but the account is not yet giving strangers a strong reason to follow. A working automation with one follower and sub-100 views usually means the content loop is under-positioned, not that the scheduler itself is broken.

## Research Inputs

Official Instagram guidance confirms the practical operating model:

- Recommendation eligibility matters because recommended content can reach people who do not follow the account.
- Reels insights should track follows, likes, comments, saves, shares, views, watch time, accounts reached, average watch time, and follows from the reel.
- Recommendation systems avoid low-quality or unoriginal repurposed content that lacks material added value.

For YUNA, this means the account should not behave like a simple aggregator. It must add a clear calculation layer, original judgment, and viewer interaction loop.

## Internal HQ Meeting Result

### HQ

The next brain layer must turn every content candidate into an experiment. The default objective is not "post a reel"; it is "make a stranger comment, save, DM, or follow because YUNA solves a repeated buying problem."

### 15-year SNS Marketing Strategist

YUNA should own one sentence:

`싼 척하는 전담액상 딜을 실제 가격으로 다시 계산해주는 계정.`

The fastest growth path is a repeatable series:

- "싼 척 딜 검산"
- "배송비 넣으면 달라지는 딜"
- "ml당 가격표"
- "댓글 딜 점수표"
- "오늘 사도 되는지 10초 판정"

### Behavioral Psychology PhD

The strongest triggers for this niche are:

- loss aversion: "싼 줄 알고 샀는데 손해"
- authority shortcut: "YUNA가 계산한 점수"
- curiosity gap: "배송비 넣으면 순위 바뀜"
- participation: "댓글 남기면 내 딜도 계산됨"
- commitment loop: "저장하고 다음 구매 전에 다시 확인"

### Content Strategist

Every candidate should carry:

- first-frame claim
- one-line conflict
- final payoff
- comment prompt
- follow reason

Bad: "오늘의 전담액상 특가"

Better: "이 전담액상 딜, 배송비 넣으면 안 싼 이유"

### Automation Engineer

Safe next patches for the SNS automation workspace:

- Add growth experiment metadata to clean_01 approval candidates.
- Force each candidate to include a YUNA score angle, first-frame hook, save CTA, comment CTA, and follow CTA.
- Log hook family and CTA family per approved post.
- Feed actual_05 comment/DM outcomes back into experiment reports.

### Data Analyst

Track by post:

- follows per 1,000 reach
- comments per 1,000 reach
- DM replies per 1,000 reach
- save rate
- share rate
- average watch time
- profile visits
- public reply sent
- private reply sent
- YUNA score distribution

### Safety Reviewer

Do not claim a product is safe, medical, legal, or guaranteed. Do not encourage underage or restricted use. Do not scrape private competitors. Do not publish live without the existing approval gate.

## YUNA Brain Rules

1. Every reel must have a follow reason.
2. Every reel must have a comment reason.
3. Every reel must have a save reason.
4. Every reel must add original calculation, interpretation, or buyer guidance.
5. Every experiment must declare the metric that will decide keep/kill.
6. Weak views are not success unless follow/comment/save/DM signal improves.
7. actual_05 comment/DM logic is part of the growth loop, not a side feature.

## 7-Day Sprint

Day 1:
- Patch candidate generation to require hook family, behavioral trigger, CTA family, and expected action.

Day 2:
- Generate 20 YUNA hooks across price shock, hidden shipping, ml-per-price, and comment score table.

Day 3:
- Produce 4 approval candidates with two hook variants each.

Day 4:
- Publish only through the existing approval gate.

Day 5:
- Collect visible metrics manually if API metrics are not available.

Day 6:
- Compare first-frame and CTA families.

Day 7:
- Keep top 2 patterns, kill weak patterns, and create next week variants.

## 14-Day Sprint

Week 1:
- Build and validate the experiment metadata layer.
- Run 4 to 8 approved posts with explicit YUNA CTAs.
- Inspect first results from actual_05 comments/DMs.

Week 2:
- Double down on the best hook family.
- Add a weekly YUNA score recap.
- Start competitor observation only with public pages and no login-gated scraping.
- Create a simple dashboard for follow/comment/save/DM conversion.

## Next Executable Patch

Target workspace:

`C:\Users\minho\Documents\02_work\03_AI\02_sns_automation`

Patch objective:

- Add YUNA growth experiment metadata to candidate generation.
- Make approval messages show hook type, behavioral trigger, follow reason, comment CTA, save CTA, and expected metric.
- Keep live publishing behind user approval.
- Do not perform live Instagram publish or credential reads.

## Deferred Gates

- Live competitor scraping requiring login.
- Credentialed Instagram metric fetch.
- Live publishing rule change.
- Manual comment/DM test outside natural comment events.
