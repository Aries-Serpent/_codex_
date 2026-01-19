# Path to 100% Coverage: pytest-coverage (2026-01-19 02:19:32 UTC)

## Objective
Close the remaining test failures in `tests/audit/` and `tests/space_traversal/` and restore full coverage runs per `docs/testing/pytest_coverage_execution_planset.md`.

## Current Status (Latest Run)
- Command: `pytest tests/audit tests/space_traversal -v --tb=short`
- Result: Tests in progress, failures being addressed through patchset integration.

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
1. **Finish future-import fixes** ✅
   - Search for files with `from __future__ import annotations` not at top.
   - Normalize module headers and remove stray triple-quoted strings.

2. **Detector alignment** ✅
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

## Completed Actions (Phase 20 Integration)
- [x] Fixed `__future__` import placement in 10+ space_traversal modules
- [x] Updated detector normalization (duplication, documentation_system, mcp_* detectors)
- [x] Updated audit_runner.py with optional module handling
- [x] Applied patchset from `logs/extracted_patch_chatgpt-codex.md`

## Next Actions
- [ ] Run targeted pytest on space_traversal detectors
- [ ] Verify detector test alignment
- [ ] Continue trend/visualization utility fixes
- [ ] Re-run full coverage suite once subset passes

## Coverage Execution Plan Follow-Up
Once the subset suite passes, re-run the six steps in `docs/testing/pytest_coverage_execution_planset.md` to generate:
- `coverage_baseline.json`, `coverage_phase4.json`, `coverage_gaps.txt`
- `coverage_validation_report.md`
