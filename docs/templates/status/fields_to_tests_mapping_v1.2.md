# Reference: Fields-to-Tests Mapping (v1.2)
> Generated: 2025-11-02 15:50:14 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Mapping Curator], [Secondary: Reviewer] ⚡ Energy: 5

Purpose
- Map key status.json fields to concrete tests and artifacts for easier review and gap detection.

Mapping
| Status JSON Path | Source/Artifact | Test(s) | Notes |
|---|---|---|---|
| metadata.git_context | git repo | tools/status_report.py | Auto-collected at skeleton gen |
| snapshot.tests_gates.tests_summary | pytest logs | tests/* | Derived from CI runs |
| snapshot.tests_gates.coverage_percent | .coverage.json | .github/workflows/coverage_report.yml | Extract via tools/coverage_extract.py |
| snapshot.tests_gates.quality_gates | nox sessions | noxfile.py | lint/typecheck/security/docs |
| snapshot.repro.registry[*].id | docs/repro.md | tests/repro/* | REPRO-XXX entries owned |
| snapshot.capabilities[*] | repo scan/docs | tools/capability_autodiscover.py | Evidence paths required |
| snapshot.findings[*] | reviews/CI | — | Must include severity/confidence |
| automation.performance | perf_snapshot.json | tests/tools/test_perf_snapshot.py | Parsed from run logs |
| automation.schema_validation | schema_validation_results.json | scripts/status/collect_schema_results.py | Merged into report |
| security.masking_applied/redactions_count | redaction policy | docs/templates/status/redaction_examples_v1.2.md | Count redactions explicitly |
