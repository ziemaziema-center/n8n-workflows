# JSON Integrity Report

Generated: 2026-04-27

Scope: local backup/export integrity only. No live workflow import, activation, or publish action was performed.

## Parse Failure Classification

| File | Classification | Action |
| --- | --- | --- |
| `workflows/clean_01_generator.json` | B: corrupted local export | Previous invalid copy archived; refreshed from live n8n export and validated. |
| `workflows/clean_02_approval.json` | B: corrupted local export | Previous invalid copy archived; refreshed from live n8n export and validated. |
| `backups/2026-04-26/clean_01_generator_backup.json` | B: corrupted backup export | Invalid original archived; valid fixed copy created as `clean_01_generator_backup.json.fixed.json`. |
| `backups/2026-04-26/clean_02_approval_backup.json` | B: corrupted backup export | Invalid original archived; valid fixed copy created as `clean_02_approval_backup.json.fixed.json`. |
| `workflow_01_live_final_stabilized.json` | B: corrupted legacy/root export | Archived under `backups/invalid_json/`; not regenerated because it is not a canonical workflow export. |
| `workflow_body.json` | B: corrupted legacy/root export | Archived under `backups/invalid_json/`; not regenerated because it is not a canonical workflow export. |
| `execution_462.json` | C: temporary execution dump | Archived under `backups/invalid_json/`. |
| `execution_470.json` | C: temporary execution dump | Archived under `backups/invalid_json/`. |
| `tmp_choose_items.json` | C: temporary scratch file | Archived under `backups/invalid_json/`. |
| `tmp_norm_test_438.json` | C: temporary scratch file | Archived under `backups/invalid_json/`. |

## Live Export Refresh

Refreshed only:

- `clean_01_generator` (`KPa5tncCc87z2ZsE`)
- `clean_02_approval` (`i6T6ke3ltKNQzaCl`)

Protected workflows not modified:

- `clean_03_publisher`
- `clean_04_carousel_publisher`

## Validation

- All JSON files under `workflows/` parse successfully.
- `workflows/clean_01_generator.json` parses successfully.
- `workflows/clean_02_approval.json` parses successfully.
- `backups/2026-04-26/clean_01_generator_backup.json.fixed.json` parses successfully.
- `backups/2026-04-26/clean_02_approval_backup.json.fixed.json` parses successfully.
