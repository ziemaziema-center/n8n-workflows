# YUNA Comment DM Activation - 2026-05-19

## Status

`PASS_ACTIVE`

## Activated Workflow

- n8n workflow: `actual_05_instagram_comment_dm_opener`
- workflow id: `Afve1lyQgvUIpgsg`
- active version: `050012f8-27c1-4a32-937f-292b122ddab5`

## Enabled Nodes

- `Public Reply`
- `Private Reply DM Opener`

## Left Disabled

- `Telegram Operator Alert`

Reason: this node is only an internal high-value lead alert. It is not required for automatic public reply/private DM behavior, and leaving it disabled avoids extra operator Telegram noise.

## Expected Behavior

When a valid Instagram comment webhook arrives:

1. Comment is normalized.
2. Duplicate comments are skipped.
3. YUNA scores comment content using price, 구성, 배송비, 기기, 취향, 재입고, and 구매처 signals.
4. If allowed, public reply is attempted:
   `DM 확인하세요. YUNA가 댓글 기준으로 가격 검산표 보냈습니다.`
5. Private reply is attempted with the YUNA score table.
6. Result is logged to Google Sheets and static workflow logs.

## Safety Notes

- No credential value was read or printed.
- No manual webhook execution was triggered.
- No test comment or DM was sent by Codex.
- This is a live activation: the next real qualifying Instagram comment can trigger public reply and private reply attempts.

## Next Check

After the next real Instagram comment, inspect:

- `public_reply_sent`
- `private_reply_sent`
- `yuna_score`
- `yuna_verdict`
- `error_message`
