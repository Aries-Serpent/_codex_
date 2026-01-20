# Path to 100% Coverage: Phase 23 Week 2 Integration Tests

**Date**: 2026-01-20 04:26 UTC  
**Feature**: Phase 23 Week 2 CLI → pipeline + data → model integration tests  
**Owner**: Codex agent  
**Status**: ✅ COMPLETE (Week 2 integration tests added)

## Scope
- Add deterministic integration tests for CLI → pipeline orchestration.
- Add deterministic integration tests for data → model interactions.
- Use fixed seeds, tmp_path fixtures, mock IO.

## Work Completed
- Added 8 CLI pipeline integration tests (trainer wiring, device handling, checkpoints).
- Added 7 data pipeline integration tests (splits, validation paths, tokenizer validation).
- Added deterministic fixture: `tests/fixtures/data/mock_classification.tsv`.

## Continuation to 70% Coverage
- Week 3 (Phase 23): Add 30–50 tests in low-coverage modules; raise `fail_under` to 30.
- Phase 24 (50%): Add 100–120 integration tests and 80–100 workflow/E2E tests.
- Phase 25 (70%): Add 80–100 critical-path + edge-case tests.

## CI/Validation Commands
- `python .codex/smoke/import_check.py`
- `pytest -q tests/unit`
- `pytest -q tests/integration`
