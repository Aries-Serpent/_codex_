# Path to 100% Coverage: pytest-coverage (2026-01-19 02:19:32 UTC)

## Objective
Close the remaining test failures in `tests/audit/` and `tests/space_traversal/` and restore full coverage runs per `docs/testing/pytest_coverage_execution_planset.md`.

## Current Status (Latest Run)
- Command: `pytest tests/audit tests/space_traversal -v --tb=short`
- Result: 178 failed, 414 passed, 13 skipped (see `pytest_space_traversal.log`).

## Primary Failure Themes
1. **`__future__` import placement**
   - Several `scripts/space_traversal/*.py` modules place `from __future__ import annotations` after non-docstring statements.
   - Fix by moving the import to immediately follow the module docstring and removing stray triple-quoted blocks.

2. **Capability detectors returning incorrect patterns/metrics**
   - Example failures: `mcp_tooling_registry`, `mcp_security_safeguards`, `documentation_system`.
   - Align expected outputs (patterns, evidence files, detector versions) with tests.

3. **Trend/visualization utilities**
   - Numerous failures in `trend_compare`, `trend_db`, `viz_ascii`, `viz_cli_api`, `viz_html`, and `webhooks`.
   - Review deterministic output formats and file generation paths; ensure tests run without external services.

4. **PEFT/training integration tests**
   - Failing tests in `tests/space_traversal/test_peft_comprehensive/` indicate missing or mismatched behaviors in training utilities.
   - Audit `src/` training components referenced by tests; implement or update deterministic outputs and metadata logging.

## Fix Strategy (Iterative)
1. **Finish future-import fixes**
   - Search for files with `from __future__ import annotations` not at top.
   - Normalize module headers and remove stray triple-quoted strings.

2. **Detector alignment**
   - For each detector failure, update the detector implementation to match expected `found_patterns`, `required_patterns`, `meta.detector_version`, and evidence file filtering.
   - Add/adjust deterministic sorting for evidence lists.

3. **Trend + visualization outputs**
   - Ensure output directories are created consistently.
   - Verify default templates/HTML are embedded and deterministic.
   - Update output schemas to match tests.

4. **PEFT/training fixes**
   - Validate that deterministic seeding, checkpoint metadata, and training status outputs align with tests.
   - Add missing fields or logging keys expected by tests.

5. **Re-run test subsets**
   - `pytest tests/audit tests/space_traversal -v --tb=short`
   - Expand to full coverage plan once the above is green.

## Next Actions (Immediate)
- [ ] Continue `__future__` import cleanup across `scripts/space_traversal/`.
- [ ] Fix `ci_integration` and detector mismatches first (highest volume of unit tests).
- [ ] Re-run `pytest tests/space_traversal/test_ci_integration.py -v` to verify.

## Coverage Execution Plan Follow-Up
Once the subset suite passes, re-run the six steps in `docs/testing/pytest_coverage_execution_planset.md` to generate:
- `coverage_baseline.json`, `coverage_phase4.json`, `coverage_gaps.txt`
- `coverage_validation_report.md`
