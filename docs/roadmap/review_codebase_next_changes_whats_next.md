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

## Evidence Summary (S1044-2026-05-17)

| Metric | Before S1044 | After S1044 |
|---|---|---|
| Collection errors | 56 (dep bucket) | **0** (collect-only succeeded, nox session successful) |
| Dominant collection failure | `pydantic`/`click`/`fastapi`/`httpx`/`crypto` missing | None — all 5 resolved via `requirements-dev.txt` |
| `pydantic` missing | 26 errors | **0** |
| `click` missing | 23 errors | **0** |
| `fastapi.testclient` missing | 2 errors | **0** |
| `httpx` missing | 1 error | **0** |
| `cryptography` missing | 1 error | **0** |
| Workflow promotion | `0D_base_` hard-coded | **configurable** via `target_branch`/`pr_base_branch` inputs |
| Full runtime phase | not reached | partial (full run still in progress at session end) |

**S1044 changes:**
- Added `pydantic>=2.4,<3`, `click>=8.1,<9`, `fastapi>=0.135.3,<1`, `httpx>=0.26,<1`, `cryptography>=42.0.0,<47.0.0` to `requirements-dev.txt`.
- Extended `.github/workflows/promote-integration-branch.yml` with `target_branch`, `pr_base_branch`, `create_or_update_pr` inputs — enables UI-driven SHA→branch promotion for files in `copilot/review-codebase-and-next-changes` (or any source branch) to `main`.

## Session Status (Current — S1044)

| Item | Status |
|---|---|
| Core report (`next_expected_codebase_change_48h.md`) | ✅ Complete |
| Mermaid + expected results + equations + token descriptions | ✅ Complete |
| Iterative promptset + groundwork package | ✅ Complete |
| Living docs sync (`whats_next`, `session_diagram`) | ✅ Complete |
| CHANGELOG + accountability updates | ✅ Complete |
| **S1042 — Quantum conftest remediation** | ✅ Complete |
| **S1043 — Loader import-contract stabilization** | ✅ Complete |
| **S1044 — Baseline dep normalization** | ✅ Complete (`requirements-dev.txt` +5 deps, 0 collection errors) |
| **S1044 — SHA→branch promotion workflow** | ✅ Complete (`promote-integration-branch.yml` generalized) |
| Full `nox -s tests` runtime failure triage | 🔄 Pending (Session D) |

## Next Objectives (Session D)

1. Run full `nox -s tests` (not collect-only) with the new env and capture the complete runtime failure inventory.
2. Characterize residual failures — expected categories: optional-heavy-dep tests (torch, mlflow, ray) vs. genuine logic failures.
3. Triage and address top runtime failure buckets that do not require heavy optional deps.
4. Validate the `promote-integration-branch.yml` workflow dispatch UX from the Actions tab with a test run.
5. Update reporting / accountability with the measured runtime delta.

## Follow-Up Continuation Prompt

> Continue from `docs/roadmap/review_codebase_next_changes_whats_next.md` and `docs/reporting/next_expected_codebase_change_48h.md` (Session D).
> The baseline nox dependency surface is now normalized — `pydantic`, `click`, `fastapi`, `httpx`, `cryptography` are installed in `requirements-dev.txt` and collection returns 0 ModuleNotFoundError instances.
> Run the full `nox -s tests` suite, capture the complete runtime failure breakdown, triage top non-heavy-dep failures, and update accountability/reporting artifacts.
> Also validate the `promote-integration-branch.yml` workflow_dispatch UI with `target_branch=main` and a source SHA from `copilot/review-codebase-and-next-changes`.
