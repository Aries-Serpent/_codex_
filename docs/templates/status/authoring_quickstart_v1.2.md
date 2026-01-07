# Quickstart: `_codex_` Status v1.2 (One‑Pager)
> Generated: 2024-11-02 15:18:20 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Author Quickstart Curator], [Secondary: Reviewer] ⚡ Energy: 5

Goal
- Produce a daily, schema‑valid status in under 10 minutes.

Steps (TL;DR)
1) Create JSON skeleton
   - python tools/status_report.py --title "📍 `_codex_` : Status Update $(date -u +%Y-%m-%d-%H:%M:UTC)" --out reports/daily/$(date -u +%Y-%m-%d).json
2) Fill these minimum fields
   - snapshot.capabilities (at least 2 items with severity/confidence)
   - snapshot.findings (1–3 items)
   - tests_gates.coverage_percent and quality_gates
   - schema validation results (section 2.6 in the MD report)
3) Validate
   - pytest -q tests/status/test_example_report_schema.py
   - python tools/link_id_crossref.py --report reports/daily/$(date -u +%Y-%m-%d).json
4) Build audit manifest (optional but recommended)
   - python scripts/audit/build_integrity_chain.py
5) Publish
   - Commit under reports/daily/ and open PR

What Good Looks Like (Checklist)
- Title uses exact format and UTC
- Git context and environment populated
- Capabilities and Findings have Severity/Confidence
- Delta present or marked "N/A"
- No secrets; redactions counted
- Schema validation PASS or actionable remediation

Handy Commands
- Validate all training configs:
  - python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml
- Ad‑hoc data+schema validation:
  - python tools/schema_validate.py --data runs/last/evaluation.json --schema configs/schemas/evaluation.schema.json
- Full status cycle:
  - bash scripts/status/run_full_status_cycle.sh
- Cross-reference validation:
  - python tools/link_id_crossref.py --report reports/daily/YYYY-MM-DD.json
- Schema drift detection:
  - python tools/schema_diff.py --old old.schema.json --new new.schema.json

Quick Reference: Minimum Required Sections
1. metadata.title, timestamp_utc, template_version, git_context, environment
2. snapshot.capabilities (2+ with id, severity, confidence)
3. snapshot.findings (1+ with id, severity, confidence)
4. snapshot.tests_gates (coverage_percent, quality_gates)
5. snapshot.repro.core_controls (array with status)
6. delta (or "N/A" with justification)
7. patches (if applicable)
8. automation (empty object OK)
9. security.masking_applied, redactions_count
10. questions (empty array OK)
11. decisions (empty array OK)

Time Budget
- Skeleton generation: 1 min
- Fill capabilities/findings: 3 min
- Fill test/coverage data: 2 min
- Validate and fix: 3 min
- Commit and PR: 1 min
- Total: ~10 min

Common Pitfalls
- Forgetting UTC in timestamp
- Missing Severity/Confidence on capabilities/findings
- Empty delta without "N/A" justification
- Secrets in diffs/logs
- Broken CAP-/FIND-/PATCH-/REPRO- cross-references
- Schema validation skipped

Emergency Shortcuts
- If pressed for time, use example_report_detailed_v1.2.json as a template
- Copy-paste and modify IDs, dates, values
- Still run validation before committing
