# PR: Legacy Import Refactor — Batch 01 (example)

Branch: chore/legacy-refactor/batch-01-training-apply
Base: main

Summary
-------
This PR applies the first safe batch of AST-based import refactors (mapping top patterns)
and validates determinism and tests after the batch. It includes small commits (<=10 files)
to keep reviewable and reversible.

Mapping Applied
---------------
- training -> src.training
- tokenization -> src.tokenization
- models -> src.modeling
- hydra (local) -> config_legacy (deprecation shim)

Commands Executed (exact)
-------------------------
# Baseline report
python scripts/remediation/analyze_legacy_usage.py
wc -l reports/legacy_import_usage.csv

# Dry-run
python scripts/remediation/refactor_imports.py --mapping mappings/batch1_mappings.json --dry-run --limit 200

# Apply (batch-size = 10)
python scripts/remediation/refactor_imports.py --mapping mappings/batch1_mappings.json --apply --batch-size 10 --limit 200

# Post-apply validation
pytest -q tests/validation/
python scripts/space_traversal/verify_determinism.py --runs 2
python scripts/remediation/verify_conflicts.py --expect-site-packages
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py diff --old audit_artifacts/baselines/capabilities_scored.json --new audit_artifacts/capabilities_scored.json || true

Determinism Equality Proof
-------------------------
- repo_root_sha[run1]: <shaA>
- repo_root_sha[run2]: <shaB>
- capabilities_scored.json normalized hash[run1]: <hA>
- capabilities_scored.json normalized hash[run2]: <hB>
- Result: <PASS / FAIL>

Tests Summary
-------------
(paste pytest output here)
- validation: <PASS/FAIL>

Legacy Import Counts (before → after)
-------------------------------------
- Before (rows): <count_before>
- After  (rows): <count_after>
- Reduction: <delta_pct %>

Artifacts & SHAs
----------------
- audit_run_manifest.json: <sha>
- audit_artifacts/capabilities_scored.json: <sha>
- audit_artifacts/baselines/capabilities_scored.json: <sha>

Reviewer Checklist
------------------
- [ ] AST refactors reviewed (diff samples look correct)
- [ ] Tests PASS; Determinism PASS
- [ ] Shadowing checks PASS
- [ ] Legacy imports reduced (≥ target per batch)
- [ ] CI trend & baseline metadata present
- [ ] Evidence attached; Rollback plan documented

Rollback Plan
-------------
- Revert batch commit: git revert <commit-sha>
- Or restore backups (.bak) produced by tool and run tests
- Re-run `verify_conflicts.py --expect-site-packages` and `verify_determinism.py`
