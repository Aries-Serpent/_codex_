# Guide: Evidence & Citation in Status (v1.2)
> Generated: 2025-11-02 15:55:27 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Evidence Curator], [Secondary: Reviewer] ⚡ Energy: 5

Purpose
- Standardize how authors reference evidence (tests, logs, artifacts) to support claims in daily status.

Rules
- Prefer repo-relative paths (stable, reviewable).
- Cite exact files and line anchors when applicable (e.g., tests).
- Include artifact hashes when referencing external files (use audit_run_manifest.json).
- Avoid linking to ephemeral CI logs; download essential snippets into repo artifacts.

Examples
| Claim | Evidence |
|---|---|
| "Coverage rose by 2.3%" | reports/.coverage.json (totals.percent_covered), delta.tests_coverage_delta |
| "Parity tests added" | tests/tokenization/test_tokenizer_parity.py |
| "Secrets baseline present" | .secrets.baseline (audited) |
| "Schema validation PASS" | scripts/status/collect_schema_results.py → schema_validation_results.json |

Checklist
- [ ] Evidence path exists and is readable
- [ ] If artifact, hash recorded in audit_run_manifest.json
- [ ] Links resolve in PR diff (or in repo tree)
