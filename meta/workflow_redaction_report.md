# Workflow Redaction Report

Generated: 2026-04-27

Scope: redacted documentation/export copies only. Original workflow exports were not overwritten.

## workflows/archive/redacted/clean_01_generator.redacted.json

- Source: workflows/live/clean_01_generator.json
- Secret-key fields redacted: 0
- Runtime/cache fields cleared: 4
- Embedded token-like strings redacted: 6
- Node structure and connections preserved except runtime/static data removal.

## workflows/archive/redacted/clean_02_approval.redacted.json

- Source: workflows/live/clean_02_approval.json
- Secret-key fields redacted: 0
- Runtime/cache fields cleared: 4
- Embedded token-like strings redacted: 1
- Node structure and connections preserved except runtime/static data removal.

## Rules Applied

- Secret-like keys replaced with `REDACTED`, `{}`, or `[]` depending on value type.
- Embedded bearer/API/GitHub/OpenAI/Telegram token-like strings replaced with redacted placeholders.
- Runtime `staticData` and cache/queue/history fields cleared.
- Originals were not modified.

## Second Pass

- Remaining likely-secret patterns in redacted `url` and `jsCode` fields were replaced with `REDACTED_URL` or `REDACTED_TOKEN`.
- Original workflow exports were not modified.
