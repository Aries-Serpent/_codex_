# Validation Errors: _codex_status_update-2025-11-04.md

This file contains validation errors and incomplete aspects detected in the status report.

**Report Path:** `reports/daily/_codex_status_update-2025-11-04.md`
**Schema:** `docs/templates/status/codex_status_template.schema_v1.2.yaml`
**Validator:** `tools/validate_status_report.py`

---

## Validation Errors

1. Title format incorrect - Expected format: 📍 `_codex_` : Status Update <date>
2. Missing 13 required sections:
  - ## Template Version
  - ### 2.3 High‑Signal Findings
  - ## 3. Delta From Last Report
  - ## 4. Atomic Patch Diffs
  - ## 5. Automation Data Ingest
  - ## 6. Concise Tokenization Insights
  - ## 7. Secret‑Masking Guidance
  - ## 8. Error Capture Blocks
  - ## 9. Open Questions & Answers
  - ## 10. Decision Log
  - ## 11. Scoring Rubric
  - ## 12. Appendix
  - ### 2.9 Deferred Items
3. Scoring rubric elements incomplete - Missing severity or confidence markers

---

## Resolution Steps

To resolve these validation errors:

1. Review each error listed above
2. Update the report file to include all required sections and fix formatting issues
3. Ensure the report follows the schema at `docs/templates/status/codex_status_template.schema_v1.2.yaml`
4. Re-run validation: `python tools/validate_status_report.py <report_file>`
5. Delete this error file once all issues are resolved

---

## Required Sections Checklist

For template version v1.2, the following sections are required:

- [ ] ## Template Version
- [ ] ## 0. Report Metadata
- [ ] ## 1. Executive Summary
- [ ] ## 2. Full Snapshot
- [ ] ### 2.1 Repo Map
- [ ] ### 2.2 Capability Audit
- [ ] ### 2.3 High‑Signal Findings
- [ ] ### 2.4 Tests & Gates Snapshot
- [ ] ### 2.5 Reproducibility Checklist
- [ ] ### 2.6 Schema Validation Report
- [ ] ### 2.7 Security Input Validation Summary
- [ ] ### 2.8 Audit Integrity Chain
- [ ] ### 2.9 Deferred Items
- [ ] ## 3. Delta From Last Report
- [ ] ## 4. Atomic Patch Diffs
- [ ] ## 5. Automation Data Ingest
- [ ] ## 6. Concise Tokenization Insights
- [ ] ## 7. Secret‑Masking Guidance
- [ ] ## 8. Error Capture Blocks
- [ ] ## 9. Open Questions & Answers
- [ ] ## 10. Decision Log
- [ ] ## 11. Scoring Rubric
- [ ] ## 12. Appendix
