# _codex_: Status Update (2025-09-27) — Iteration 3 Completion

## 1. Iteration 3 Summary
- Remote connectors now resolve to an explicit offline adapter that refuses remote read/write operations while allowing callers to enumerate fallbacks without hitting real services.
- Deployment helpers ship as a structured offline shim returning deterministic status blocks for automation instead of touching cloud APIs.
- Analysis providers adopt a formal interface with richer evidence normalisation (score/source capture) to support expanded logging pipelines.
- Added tests covering the remote connector guardrails and deployment shim behaviour to keep the offline contract enforced.

## 2. Repository Map (unchanged footprint)
- Top-level directories mirror the Iteration 2 scan (50+ entries) including: `.codex`, `agents`, `analysis`, `codex_ml`, `docs`, `monitoring`, `src`, `tests`, `tools`, `training`, `typer`, among others.
- Control files remain anchored at the root: `pyproject.toml`, `noxfile.py`, `pytest.ini`, `Dockerfile`, `codex_task_sequence.py`, `codex_setup.py`, and related automation assets.

## 3. Stub & Placeholder Histogram (unchanged counts)
- TODO markers: **4,534**
- `NotImplementedError` raises: **4,192**
- Bare `pass` placeholders: **365**
- Concentrated hotspots persist in automation entry points (`codex_setup.py`, `noxfile.py`, `codex_task_sequence.py`, `codex_ast_upgrade.py`). Iteration 3 removed the blocking runtime stubs for remote connectors/deployment but overall counts are unchanged pending broader cleanup.

## 4. Capability Audit Table
| Capability | Status | Artifacts / Notes | Remaining Gaps | Next Actions |
| --- | --- | --- | --- | --- |
| Connectors (local, remote adapters) | **Implemented (offline)** | `src/codex_ml/connectors/{base.py,remote.py,registry.py}`; async tests under `tests/connectors/test_remote_connector.py` | Remote storage is intentionally disabled; future work may add opt-in fixtures | Harden registry validation, consider per-endpoint allow-list when remote support returns |
| Deployment (cloud packaging) | **Implemented (offline shim)** | `src/codex_ml/deployment/cloud.py`, orchestration wiring in `codex_task_sequence.py`, tests in `tests/deployment/test_cloud.py` | No actual cloud provisioning; needs integration with packaging once remote allowed | Model local packaging artefacts, surface CLI entry point |
| Analysis Providers & Logging | **Partially Implemented → Strengthened** | Abstract provider interface with richer evidence metadata in `src/codex_ml/analysis/providers.py`; coverage via existing external search tests | Additional providers (docs/knowledge bases) still pending; evidence deduping not yet implemented | Add offline doc index provider, wire logging summaries into telemetry |
| Training / Checkpointing Integration | **Implemented** | Deterministic seeding + checkpoint utilities in `src/codex_ml/training` and `src/codex_ml/utils/checkpointing.py`; offline MLflow guardrails intact | Need regression tests for offline MLflow/connector interplay | Schedule deterministic regression suite for Iteration 4 |

## 5. Determinism & Logging Snapshot
- Deterministic seeding continues to be enforced via `codex_task_sequence.py` and training utilities (`codex_ml/utils/repro.py`).
- Offline MLflow guards remain active (`codex_ml/tracking/mlflow_guard.py`); deployment shim now mirrors the same offline stance for provisioning.
- Evidence normalisation now retains optional `score`/`source` metadata for future telemetry enrichment.

## 6. Proposed Iteration 4 Scope — Regression Hardening
1. **Deterministic Test Gates**: extend `noxfile.py` / `pytest` sessions to assert MLflow guard decisions and remote connector behaviour (mock remote-enabled envs).
2. **Offline Logging Regression Suite**: add fixtures ensuring telemetry writers gracefully handle disabled MLflow/W&B while respecting local summaries.
3. **Connector/Deployment Integration Tests**: compose higher-level smoke tests that exercise connector registry selection + deployment shim from orchestration entry points.
4. **Stub Backlog Burn-down**: prioritise remaining automation hotspots (esp. `codex_ast_upgrade.py`) with focus on replacing `NotImplementedError` paths that still gate orchestrators.
5. **Documentation Sync**: document offline guardrails across CLI + developer docs to prevent regression when remote functionality is reintroduced.

---
Prepared for Iteration 4 planning; automation scaffolding is now stable enough to support regression hardening work.
