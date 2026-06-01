# Marketing HQ Posting Scope Manifest - 2026-06-01

## Files Created
- reports/marketing_hq_posting_scope_work_queue_2026-06-01.md
- reports/marketing_hq_posting_scope_confirmation_2026-06-01.md
- reports/marketing_hq_posting_safety_matrix_2026-06-01.md
- reports/marketing_hq_telegram_preview_send_eligibility_2026-06-01.md
- reports/marketing_hq_telegram_preview_send_2026-06-01.md
- runtime/marketing_hq/telegram_preview_send_20260601.json
- reports/marketing_hq_future_render_gate_packet_2026-06-01.md
- reports/marketing_hq_future_publish_gate_packet_2026-06-01.md
- reports/marketing_hq_human_decision_packet_2026-06-01.md
- tests/test_marketing_hq_posting_scope_confirmation_20260601.py
- tests/test_marketing_hq_telegram_preview_send_20260601.py
- reports/marketing_hq_posting_scope_manifest_2026-06-01.md
- reports/marketing_hq_posting_scope_closing_qa_report_2026-06-01.md
- reports/marketing_hq_posting_scope_patch_manifest_2026-06-01.md
- reports/marketing_hq_posting_scope_final_verdict_2026-06-01.md

## Files Modified
- tests/test_company_runner_safe_fallback_20260529.py

## SHA256
- reports/marketing_hq_posting_scope_work_queue_2026-06-01.md: `DFD488E314DEF6FEC1512712EAE0CB83BEF33C12EF73ACEE4C87ACE8212EB8FF`
- reports/marketing_hq_posting_scope_confirmation_2026-06-01.md: `87ED3CC0D0E6D6F47F79F17B536447C59B82DAE338D40821BBDE263DB63F5283`
- reports/marketing_hq_posting_safety_matrix_2026-06-01.md: `1B4DA64320C90EEDC54CEFD488F837BA8B26CF400534AF127A5DAAB8E7978ED8`
- reports/marketing_hq_telegram_preview_send_eligibility_2026-06-01.md: `3E00A2F4FB7744FED6A3079FF2641129B65DA1A48129F06CA5A61854D3BB2CB6`
- reports/marketing_hq_telegram_preview_send_2026-06-01.md: `9BE0C5777494A385DCA47FC288FE6F04F089EAA100470377C81548737AD2A19F`
- runtime/marketing_hq/telegram_preview_send_20260601.json: `2A88D052C84D1EB2E1792CA5BD53797341930CD70FF7E8EF1C2F246034B287B3`
- reports/marketing_hq_future_render_gate_packet_2026-06-01.md: `69B9344B31C11C93200DBA968A5FDBBA21F43EEF9ACF7832F1EA6DF481A0A7C9`
- reports/marketing_hq_future_publish_gate_packet_2026-06-01.md: `12F1FBBFEA516AE1D94A6B8CEDE642BBC4CF683D61EAA532E96E2C3AACEEA2DA`
- reports/marketing_hq_human_decision_packet_2026-06-01.md: `66BE388F7FBAC8233135F283C0AE28FCFF271FD9B266EB493DE7BB7027F82487`
- tests/test_marketing_hq_posting_scope_confirmation_20260601.py: `8EB98BDA3FDF2D663A4DB9500752A6826540DE06F63D6E66AF60DDFB10877983`
- tests/test_marketing_hq_telegram_preview_send_20260601.py: `CCAD2AE28E4B0DC177B4BEBBAC2328E823EB73C933278ED181F6928F0F0E4108`
- reports/marketing_hq_posting_scope_manifest_2026-06-01.md: `37684552EBC95C8E665FCE754E23A640706AC0EC887DD3161E41F7380C55CDE4`
- reports/marketing_hq_posting_scope_closing_qa_report_2026-06-01.md: `7EB0DD93839A6F5B08A15F77B61C57C71BD7354412BC458F0C2D7681EC85E4E0`
- reports/marketing_hq_posting_scope_patch_manifest_2026-06-01.md: `593713D7934D5C70579F34378EA97B3C2F9D5F1A161F8B4897C26E5DEA1C8370`
- reports/marketing_hq_posting_scope_final_verdict_2026-06-01.md: `A92F9716C3D85A4F1D1E8D2CE22744139FC8F9E3CDD858DE6B6E65BBC40A8FE8`
- tests/test_company_runner_safe_fallback_20260529.py: `D25A64297BF7BD2E96154B526C9B2EED9FE95DE27A0A8EA3766248949AC8577F`

## Telegram Send Status
- BLOCKED

## Message IDs
- none

## Tests Run
- `python -m unittest tests.test_marketing_hq_posting_scope_confirmation_20260601` -> PASS
- `python -m unittest tests.test_marketing_hq_telegram_preview_send_20260601` -> PASS
- `python -m unittest tests.test_marketing_hq_telegram_preview_package_20260601` -> PASS
- `python -m unittest discover -s tests` (escalated rerun after sandbox permission failure) -> PASS (224 tests)

## Safety Counters
- publish_authorization_false: true
- render_authorization_false: true
- n8n_live_change_authorization_false: true
- cron_authorization_false: true
- clean01_clean04_execution_false: true
- instagram_publish_false: true
- seller_url_exposure_false: true
- price_invention_false: true

## Future Gates
- render_gate_packet_created: true
- publish_gate_packet_created: true

## Remaining Blockers
- TELEGRAM_DESTINATION_NOT_IDENTIFIABLE
- ACCOUNT_HANDLE_MISSING

This document does not authorize Instagram publishing, image/video rendering, paid media execution, n8n live workflow changes, cron activation, clean01/clean04 execution, DM/comment automation, credential disclosure, or production changes.
