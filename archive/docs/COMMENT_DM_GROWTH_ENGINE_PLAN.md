# Comment / DM Growth Engine Plan

## Objective

Reach 30,000+ Instagram followers by mid-May 2026 by turning every comment into a visible engagement loop, DM entry point, or follower-conversion moment.

This is not a customer-support bot. It is a growth engine.

## Current Status

- Active publishing pipeline is focused on preview, approval, queueing, and Instagram publishing.
- Comment auto-reply and comment-triggered DM are not active in the clean production pipeline yet.
- Existing old comment manager workflow appears inactive and should not be enabled blindly.
- Phase 3 scheduled publishing must be completed first so published media IDs are consistently available for comment monitoring.

## Operating Rule

No comment is ignored by default.

Low-effort, sarcastic, angry, vague, or spam-like comments are still treated as possible engagement fuel. The system should route them differently, not discard them.

## Expert Model

Every generated public reply and private reply should combine three lenses:

- IQ200 Engineer: classify intent, preserve API safety, prevent duplicates, log outcomes.
- 20-Year Psychology PhD: trigger validation, curiosity, identity tension, and return-comment behavior.
- FBI Behavioral Analyst: read emotional posture and respond without sounding generic or defensive.

## Comment Classes

- Agreement: amplify and invite a second thought.
- Disagreement: keep debate open without resolving.
- Question: answer partly, then open a DM continuation.
- Sarcasm / attack: acknowledge emotion, redirect to hidden structure.
- Short reaction: respond quickly so the commenter feels seen.
- Price / where / regulation / store / wholesale / penalty: high-intent private reply candidate.

## Public Reply Formula

1. Recognize the commenter.
2. Add a sharper hidden angle.
3. End with friction or a question.

Examples:

- "이 반응 나올 줄 알았음. 근데 진짜 문제는 그 다음임."
- "맞음. 대부분 여기서 당하고도 본인이 선택했다고 생각함."
- "반박 가능. 근데 가격표 바뀐 이유까지 보면 생각 달라질걸."
- "질문 좋음. 근데 댓글로 다 쓰면 핵심이 너무 길어짐."

## Private Reply Formula

1. "댓글 보고 보냈어" style acknowledgement.
2. One hidden angle.
3. One question that makes reply likely.

Examples:

- "댓글 보고 보냈어. 이거 겉으로는 가격 문제처럼 보이는데, 실제로는 매장 반응이 먼저 바뀌는 구조야."
- "네가 느낀 게 맞아. 사람들이 놓치는 건 제품이 아니라 '언제 바뀌는지' 쪽임."
- "이건 공개 댓글에 다 쓰면 이상하게 보일 수 있어서 짧게만 말하면, 지금 보는 가격이 끝이 아닐 가능성이 큼."

## Required System Design

### Phase 4: Comment Monitoring + Public Reply

Add a separate workflow after Phase 3 is stable.

Flow:

1. Read recently published media IDs from publish logs.
2. Fetch comments for each media item.
3. Deduplicate by comment_id.
4. Classify comment intent and emotional posture.
5. Generate public reply draft.
6. Send draft to Telegram for approval at first.
7. On approval, post public comment reply.
8. Log result.

Safety:

- No workflow should modify reel/carousel/feed publishing.
- No duplicate replies to same comment_id.
- No deletion/hiding/blocking by default.

### Phase 5: Comment-Triggered Private Reply / DM

Only after Phase 4 proves stable.

Flow:

1. Identify comments eligible for private reply.
2. Check no previous private reply was sent for the same comment_id.
3. Generate private reply.
4. Use official Meta private reply API only.
5. Log recipient, comment_id, media_id, response status.

Safety:

- Do not use unofficial Instagram DM automation.
- Do not send duplicate private replies.
- Stop on API errors or rate limits.
- If Meta permissions are missing, report and do not fake success.

## Implementation Dependencies

- Published media IDs must be logged reliably.
- Instagram account must have required Meta permissions for comment management and private replies.
- Comment webhook or polling strategy must be selected.
- A persistent log is required for comment_id, reply status, private_reply status, and generated copy.

## Phase 3 Gate

Do not build or activate Phase 4/5 until Phase 3 scheduled publishing proves:

- Approved items publish at planned times.
- Deleted items are skipped.
- No action means no publish.
- Media IDs are available after publish.
- Publish logs are reliable enough to feed comment monitoring.
