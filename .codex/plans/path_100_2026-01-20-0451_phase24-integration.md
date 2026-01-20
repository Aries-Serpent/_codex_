# Path to 100% Coverage: Phase 24 Integration + Workflow Expansion

**Date**: 2026-01-20 04:51 UTC  
**Feature**: Phase 24 integration/workflow expansion for CLI → data → model flows  
**Owner**: Codex agent  
**Status**: ✅ IN PROGRESS (Phase 24 tests added)

## Scope
- Add deterministic integration tests for CLI workflow orchestration.
- Add deterministic workflow/E2E tests for data pipeline flows.
- Provide fixtures for multi-step workflows and prepare coverage tracking.

## Work Completed
- Added 23 integration tests for CLI workflow wiring, overrides, error paths.
- Added 20 workflow/E2E tests for data pipeline splits, validation, deterministic seeds.
- Added 20 training/evaluation workflow tests for SimpleTrainer and CheckpointConfig.
- Added 27 service workflow tests for GitHub exceptions/types and workflow metadata.
- Added 30 service workflow/crawler tests for parser, inventory, crawler edge cases.
- Added deterministic fixtures (mock_classification.tsv, workflow_classification.tsv).
- Re-enabled coverage gating: `--cov-fail-under=70` to align with pyproject.toml.

## Continuation to 70% Coverage
- Phase 24: Expand integration + workflow coverage to 50% threshold.
- Phase 25: Add critical-path coverage and verify `fail_under=70` is green.
- Track coverage gating failures until service coverage lifts above 70%.

## CI/Validation Commands
- `python .codex/smoke/import_check.py`
- `pytest -q tests/unit`
- `pytest -q tests/integration`
