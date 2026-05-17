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
| **S1043 — Loader import-contract stabilization** | ✅ Complete |

## Evidence Summary (S1042/S1043-2026-05-17)

| Metric | Before | After |
|---|---|---|
| Collection errors | 143 (`_core_loaders.stream_paths` cascade after S1042) | 56 |
| Dominant collection failure | `_core_loaders.stream_paths` import cascade | Optional-dependency gaps in baseline nox env |
| Loader-focused targeted regressions | blocked | 16/16 pass |
| Quantum regression sample | blocked | 14/14 pass |
| Full `nox -s tests` runtime phase | not reached | not reached (collection still interrupts) |

**S1042 root cause:** `pytest_plugins = ("tests.utils.quantum_helpers",)` in `tests/quantum/conftest.py` was rejected by pytest 8+ as unsupported in non-root conftest files.  
**S1042 fix:** Removed `pytest_plugins`, directly imported `quantum_plugin_fixture`.

**S1043 root cause class:** recursive loader import contract plus optional monitoring coupling:
- `src/codex_ml/data/__init__.py` eagerly imported `.loaders`, exposing a partially initialized `codex_ml.data._core_loaders`
- `src/codex_ml/connectors/remote.py` tied loader importability to optional monitoring extras

**S1043 fix:** removed eager `.loaders` package import and added optional `record_health_event` fallback.

**Remaining baseline nox collection blockers (56 total):**
- `pydantic`: 26
- `click`: 23
- `fastapi.testclient`: 2
- `httpx`: 1
- `cryptography`: 1
- pydantic symbol imports (`ConfigDict`, `ValidationError`): 3

## Next Objectives (Session C)

1. Normalize the baseline nox dependency contract for `pydantic`, `click`, `fastapi.testclient`, `httpx`, and `cryptography`.
2. Re-run `nox -s tests` until collection reaches zero and runtime failures become visible.
3. Update accountability + reporting with the next measured CI run outcomes.
4. Validate WEC/workflow governance state remains stable.

## Follow-Up Continuation Prompt

> Continue from `/home/runner/work/_codex_/_codex_/docs/reporting/next_expected_codebase_change_48h.md` and this living doc. Normalize the baseline nox dependency contract (`pydantic`, `click`, `fastapi.testclient`, `httpx`, `cryptography`), then re-run `nox -s tests`, capture the next collection/runtime delta, and update reporting/accountability artifacts.
