# Secret Scan Summary

Scope: tracked and unignored repository text files only; `.git/` excluded. Secret values are intentionally omitted.

Generated: 2026-04-27 07:42:27 +09:00

Likely real secret files: 48
Placeholder/redacted secret-reference files: 37
False-positive/config-field-only files: 57

## Likely Real Secret
- add_reel_pipeline_minimal.py
- apply_memory_workflow_patch.ps1
- backup_DGMQEgFXqzeS3sJ5_memory_patch.json
- backup_ER3V1JqA9BjbnJkI_memory_patch.json
- backup_i6CxwaOkND3LGqv0_memory_patch.json
- backups/2026-04-26/clean_01_generator_backup.json.fixed.json
- backups/2026-04-26/clean_02_approval_backup.json.fixed.json
- backups/invalid_json/20260427_073620_execution_462.json
- backups/invalid_json/20260427_073620_execution_470.json
- backups/invalid_json/20260427_073620_workflow_01_live_final_stabilized.json
- backups/invalid_json/20260427_073620_workflow_body.json
- execution_438.json
- execution_439.json
- execution_440.json
- execution_445.json
- execution_446.json
- execution_449.json
- execution_455.json
- execution_457.json
- fix_telegram_getfile_url.py
- live_approval.json
- live_gen.json
- live_pub.json
- node_send_video_before.json
- node_send_video_current.json
- patch_add_separate_carousel_path.py
- patch_clean01_duplicate_calibration_summary.py
- patch_clean01_summary_code_node.py
- patch_dmqv.ps1
- patch_dmqvd.ps1
- patch_dmqvd_refresh_edit.ps1
- patch_phase1_content_requirements_v2.py
- patch_phase1_daily7_news_queue_preview.py
- patch_phase1_feed_photo_plus_text.py
- patch_phase3c_scheduler_execute.py
- PROJECT_CONTEXT.md
- repair_clean_system.ps1
- rewire_reel_pipeline_service.py
- verify_send_node_after.json
- workflow_01_live.json
- workflow_01_live_current.json
- workflow_01_live_final_payload.json
- workflow_01_live_latest.json
- workflow_DGMQEgFXqzeS3sJ5.json
- workflow_giWKQwX7x2fasi1h.json
- workflow_IY3f5KcJDMDgWRJk.json
- workflows/clean_01_generator.json
- workflows/clean_02_approval.json

## Placeholder / Redacted References
- backups/2026-04-26/actual_07_auto_debugger_collector_backup.json
- backups/2026-04-26/actual_08_github_logger_backup_response_fix.json
- backups/2026-04-26/clean_03_publisher_backup.json
- backups/2026-04-26/clean_04_carousel_publisher_backup.json
- backups/invalid_json/20260427_073620_actual_08_github_logger_before_local_patch.json
- backups/invalid_json/20260427_073620_backups_2026-04-26_clean_01_generator_backup.json
- backups/invalid_json/20260427_073620_backups_2026-04-26_clean_02_approval_backup.json
- backups/invalid_json/20260427_073620_clean_01_generator.json
- backups/invalid_json/20260427_073620_clean_02_approval.json
- create_auto_debugger_v3.py
- deploy_clean_ig_system.ps1
- deploy_clean_ig_system_v2.ps1
- fix_generator_sheet_init.ps1
- import_and_test_minimal.ps1
- instagram_reel_publisher_minimal.json
- meta/secret_scan_summary.md
- operational_update_20260425.py
- patch_approve_split_and_clean04.py
- patch_auto_debugger_event_driven.py
- patch_carousel_media_v2_saveimage.py
- patch_carousel_media_v3_dataurl.py
- patch_clean01_summary_message_fix.py
- patch_clean03_diagnostics_only_step2.py
- patch_clean04_ig_child_jsonbody_syntax.py
- patch_fix_carousel_children_ids.py
- patch_issue2_telegram_carousel_caption.py
- patch_phase3b_minimal_feed_clean04.py
- patch_phase3c_feed_error_raw_logging.py
- patch_publisher_caption_encoding_minimal.py
- patch_telegram_append_carousel.py
- repair_sheet_setup_subworkflow.ps1
- setup_github_backup_logging_system.py
- update_n8n_workflows.ps1
- workflows/actual_07_auto_debugger_collector.json
- workflows/actual_08_github_logger.json
- workflows/clean_03_publisher.json
- workflows/clean_04_carousel_publisher.json

## False Positive / Field Names Only
- add_execute_trigger_to_generator.py
- apply_minimal_prod_fix_20260422.py
- build_queue_system.ps1
- create_minimal_sheet_setup_runtime.ps1
- create_runtime_sheet_setup_and_patch_generator.ps1
- create_setup_runner_fixed.ps1
- create_sheet_setup_webhook.ps1
- fix_reel_ffmpeg_node_type.py
- fix_sheet_setup_and_rerun.ps1
- fix_sheet_setup_only.ps1
- fix_sheet_setup_with_python.py
- fix_sheet_setup_workflow.ps1
- inspect_generator_nodes.ps1
- inspect_latest_generator_execution.ps1
- openapi.yml
- patch_add_build_carousel_content.py
- patch_approval_reel_url.py
- patch_build_sim_korean_literals.py
- patch_carousel_b64_to_public_url.py
- patch_clean01_carousel_image_fallback.py
- patch_clean01_collapse_telegram_single_item.py
- patch_clean01_collect_reel_images_fallback.py
- patch_clean01_content_variation_engine.py
- patch_clean01_duplicate_hash_no_crypto.py
- patch_clean01_feed_fallback_duplicate_guard.py
- patch_clean01_nonblocking_reel_image.py
- patch_clean01_production_mode.ps1
- patch_clean01_psychological_diversity_engine.py
- patch_clean01_strict_angle_rotation.py
- patch_clean03_daily_cap_guard.py
- patch_content_v2_news_funny.py
- patch_detect_duplicate_simple_hash.py
- patch_generator_bypass_setup.py
- patch_generator_quality_only.py
- patch_media_template_only.ps1
- patch_phase1_branch_grouping_fix.py
- patch_phase1_caption_function_replace.py
- patch_phase1_feed_length_fact_guard.py
- patch_phase1_prepare_reel_multiitem_fix.py
- patch_phase2_approval_queue.py
- patch_phase2_feed_payload_cache.py
- patch_phase3a_dry_run_scheduler.py
- patch_phase3c_feed_full_response_logging.py
- patch_phase3c_skip_existing_status_fix.py
- patch_phase3c_status_fix_feed_logging.py
- patch_run_sheet_setup_mode.ps1
- patch_setup_noop.py
- patch_sheet_setup_connections_raw.ps1
- patch_vape_generator.ps1
- rebuild_sheet_setup_connections.ps1
- rename_workspace_safe.ps1
- run_generator_via_webhook.py
- run_queue_path_via_webhook.py
- setup_sheets_manual.py
- update_build_node_only.py
- validate_minimal_prod_fix_20260422.py
- webhook_test_minimal.ps1

Action: do not stage likely-real-secret files until manually reviewed and redacted.
