# Coverage Gap Report — Static Cross-Reference

> **Generated:** 2026-05-24T23:00:00Z
> **Branch:** `copilot/analyze-test-coverage-and-documentation`
> **Method:** Static cross-reference of `src/<pkg>/` ↔ `tests/<pkg>/` plus import-name search across `tests/`. The dynamic `pytest --cov` rerun is intentionally **deferred to the existing `Coverage` CI workflow** (running 21,500+ tests in this sandbox is not viable).
> **ADA citation:** [.codex/CODEBASE_AGENCY_POLICY.md](CODEBASE_AGENCY_POLICY.md)
> **Hand-off agent:** `unified-coverage-agent` (consolidated entry point — supersedes `coverage-gapfill-agent`, `coverage-maintenance-agent`, `coverage-roadmap-agent`, `test-coverage-agent`, `test-coverage-monitor`).

---

## 1. Repository inventory

| Metric | Value |
|---|---|
| `src/` Python modules (excl. `__init__.py`) | **943** |
| `src/` top-level packages | 41 |
| `tests/` top-level dirs | 177 |
| Modules with **no import reference** anywhere under `tests/` | **139 / 943 (14.7%)** |
| README-reported coverage badge | **10.7%** |
| Coverage gate (`pyproject.toml [tool.coverage.report].fail_under`) | **80** (full-stack CI only) |

`.coveragerc` no longer carries `fail_under`; `pyproject.toml` is the single source of truth (per S1044 memory and verified at `pyproject.toml [tool.coverage.report]`).

---

## 2. Packages by source size & test footprint

Top src packages ranked by source `.py` file count, with corresponding `tests/<pkg>/` presence:

| Package | src .py files | `tests/<pkg>/` exists | flat `test_<pkg>_*.py` hits |
|---|---:|:-:|---:|
| `codex_ml` | 395 | ✅ | 9 |
| `codex` | 284 | ✅ | 165 |
| `mcp` | 46 | ✅ | 19 |
| `cognitive_brain` | 36 | ✅ | 0 |
| `hhg_logistics` | 17 | ✅ | 0 |
| `services` | 16 | ✅ | 2 |
| `training` | 16 | ✅ | 31 |
| `security` | 14 | ✅ | 14 |
| `context_management` | 13 | ✅ | 1 |
| `codex_crm` | 9 | ✅ | 0 |
| `utils` | 9 | ✅ | 3 |
| `common` | 8 | ✅ | 0 |
| `ingestion` | 8 | ✅ | 10 |
| **`restore_pipeline`** | **7** | ❌ | 0 |
| `tokenization` | 6 | ✅ | 12 |
| `agent` | 5 | ✅ | 15 |
| `codex_audit` | 5 | ✅ | 1 |
| `codex_bridge` | 1 | ❌ | 0 |
| `integrations` | 1 | ❌ | 0 |
| `hydra_extra` | 0 | ❌ | 0 |

### 2.1 Zero-test-directory packages with source code

| Package | src .py | Risk | Priority |
|---|---:|---|---|
| `restore_pipeline` | 7 | Disaster-recovery pipeline; touches checkpoints | **High** |
| `codex_bridge` | 1 | IPC bridge protocol surface | **High** |
| `integrations` | 1 | External-service shim | Medium |

### 2.2 Packages with `tests/<pkg>/` but **0 flat test hits**

`cognitive_brain`, `hhg_logistics`, `codex_crm`, `common`, `workers`, `codex_plans` — verify the existing directory contains substantive tests (not just `__init__.py`).

---

## 3. Untested modules on critical paths

The following src modules have **no import reference in `tests/`** (139 total; critical-path subset below):

### 3.1 `mcp` (Model Context Protocol) — 16 untested
- `mcp.adapters.base_adapter`, `mcp.adapters.pinecone_adapter`, `mcp.adapters.zendesk_adapter`
- `mcp.api.schemas`
- `mcp.embeddings.hf_embedder`, `mcp.embeddings.interface`, `mcp.embeddings.openai_embedder`
- `mcp.packager.cli`, `mcp.packager.config`
- `mcp.server.adapters.mock_adapter`, `mcp.server.json_rpc`, `mcp.server.middleware.auth`, `mcp.server.routes_health`, `mcp.server.run`, `mcp.server.safety_checks`, `mcp.server.schemas`, `mcp.server.tracing`
- `mcp.workers.checkpoint`, `mcp.workers.embedder`

### 3.2 `codex_ml.tokenization` — 5 untested
- `_protocols`, `_types`, `api`, `pipeline`, `train_tokenizer`

### 3.3 `cognitive_brain` — 6 untested
- `experiments.exp1_validation` … `exp6_validation` (no `exp4`), `rhizome_connector`

### 3.4 `codex.rag` — 7 untested
- `analytics.dashboard`, `analytics.metrics_db`
- `benchmarks.{e2e_bench, embedding_bench, indexing_bench, retrieval_bench, runner}`

### 3.5 `quantum` — 2 untested
- `quantum.orchestrator`, `quantum.testing`

### 3.6 `monitoring` / serving — 4 untested
- `monitoring.performance_monitor`
- `codex_ml.monitoring.cli`, `codex_ml.serving.monitoring`
- `codex.zendesk.monitoring.registry`

### 3.7 `services.audio` — 2 untested
- `services.audio.core.audio_processor`, `services.audio.effects.noise_reduction`
- (Use existing convention: `python -m ruff check src/services/audio apps/dev tests/services/audio` + `python -m pytest tests/services/audio -q` per repo memory.)

### 3.8 Other notable
- `codex_ml.ast.storage.sqlite_storage`, `codex_ml.training.saas_integration`
- `codex.zendesk.quantum.orchestrator`, `codex.zendesk.rag.bridge`

---

## 4. Authoring strategy (per plan §A2)

| Test style | Targets | Notes |
|---|---|---|
| Unit | parsers/validators/utils in `mcp.api.schemas`, `mcp.server.schemas`, `_protocols`, `_types`, `codex_ml.tokenization.api` | Pure-logic first |
| Property-based (`hypothesis`) | `codex_ml.tokenization.pipeline`, `train_tokenizer` (round-trip), checkpoint payload bytes, RNG state dump (`build_payload_bytes`, `dump_rng_state` per checkpoint-imports memory) | |
| Integration | `codex_bridge` (bridge protocol v2 — see `src/bridge_protocol_v2.py`), `scripts/cognitive/sensors/`, `scripts/cognitive/actions/`, `.codex/config/monitoring.yaml` hot-reload | Honor monitoring-thresholds memory |
| Security regression | `codex_audit/*`, `scripts/ci/fetch_security_snapshot.py` secret-scanning redaction | Verify `stage == "secrets"` path; `by_type`/`by_validity` print `[REDACTED]` |
| CLI | `mcp.packager.cli`, `codex_ml.monitoring.cli`, `codex_cli` entrypoints | `typer.testing.CliRunner` |
| Negative/edge | Empty inputs, malformed configs, missing optional deps, timezone-aware datetimes via `strftime("%Y-%m-%dT%H:%M:%SZ")` | Per timestamp-format memory; SQLite pool tests assert ranges, not exact thread counts |

### Conventions to honor
- Ruff selects only `E,F,I`; tests ignore `E402,F811` (per linting memory).
- Targeted validation per change set: `python -m ruff check <paths>` + `python -m pytest <dirs> -q`.

---

## 5. Coverage roadmap (stepped gate)

Current badge: 10.7%. Proposed stepped thresholds for `pyproject.toml [tool.coverage.report].fail_under` (CPU-only CI; full-stack remains at 80):

| Step | Gate | Trigger criteria |
|---|---:|---|
| S0 (today) | **10** | Floor — prevents regression from current state |
| S1 | 12 | After untested `mcp.server.*` and `codex_ml.tokenization.api` are covered |
| S2 | 15 | After `cognitive_brain.experiments.*` + `services.audio.*` units are covered |
| S3 | 20 | After `mcp.adapters.*`, `mcp.workers.*`, `codex.rag.benchmarks.*` units are covered |

`unified-coverage-agent` should both **fill gaps** (authoring) and **enforce the gate** (PR check) — its current ownership of the deprecated five sub-agents is verified.

---

## 6. Hand-off

This report is delivered to `unified-coverage-agent` for authoring under PDA Loop → AfterMath, with `autonomous-test-healer-agent`, `test-enhancement-agent`, `fragile-test-guardian`, and `mutation-testing-agent` as supporting agents per the plan's sub-agent table.

Every authored test PR must include the ADA citation footer (`.codex/CODEBASE_AGENCY_POLICY.md`) and the PDA/AfterMath turn ID per repo convention.
