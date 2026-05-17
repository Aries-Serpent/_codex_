# Review Codebase / Next Changes — What's Next

## Session Status (Current)

| Item | Status |
|---|---|
| Core report (`next_expected_codebase_change_48h.md`) | ✅ Complete |
| Mermaid + expected results + equations + token descriptions | ✅ Complete |
| Iterative promptset + groundwork package | ✅ Complete |
| Living docs sync (`whats_next`, `session_diagram`) | ✅ Complete |
| CHANGELOG + accountability updates | ✅ Complete |
| **S1042 — Quantum conftest remediation** | ✅ Complete |

## Evidence Summary (S1042-2026-05-17)

| Metric | Before | After |
|---|---|---|
| Collection errors | 1 (hard interrupt) | 0 |
| Tests collected | 0 (interrupted) | 16,373 |
| Quantum tests passing | N/A (blocked) | 95/95 |
| Targeted test set | N/A | 105/106 (1 pre-existing flaky) |

**Root cause:** `pytest_plugins = ("tests.utils.quantum_helpers",)` in `tests/quantum/conftest.py` was rejected by pytest 8+ as unsupported in non-root conftest files.  
**Fix:** Removed `pytest_plugins`, directly imported `quantum_plugin_fixture` instead. One-line change, backward-compatible.

## Next Objectives (Session B)

1. Run `nox -s tests` full suite in CI to confirm zero collection errors end-to-end.
2. Characterize remaining runtime test failures separate from collection gate.
3. Update accountability + reporting with measured CI run outcomes.
4. Validate WEC/workflow governance state remains stable.

## Follow-Up Continuation Prompt

> Run `nox -s tests` full suite, confirm zero collection errors from the quantum conftest fix, characterize remaining runtime failures, and update reporting/accountability with measured CI run outcomes.
