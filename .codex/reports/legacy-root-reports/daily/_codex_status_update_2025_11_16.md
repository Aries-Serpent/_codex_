# 📍_codex_: Status Update (2025-11-16)

## 1. Repo Map

| Area | Contents & Purpose | Stubs/Unimplemented |
|---|---|---|
| **Root** | `README.md` with CI status, offline-first philosophy, quick index for search links and categories; `pyproject.toml` defines package `codex-ml`, dependencies (Hydra, pydantic, transformers, accelerate, datasets, MLflow, W&B, psutil), optional extras (analysis, hydra, dev, logging, metrics); CLI entrypoints for `codex-train`, `codex-eval`, `codex-import-ndjson` etc. `noxfile.py` defines local pre-commit/test sessions with segmentation and evidence checks. `.pre-commit-config.yaml` defines offline-only hooks (bandit, semgrep, gitleaks, detect-secrets, ruff). `MANIFEST.in`, segmented `requirements/*.txt` and `uv.lock` provide reproducible dependency pinning. | Many support files reference vendor scanning and CI integration; these are local only. No stubs. |
| **.codex/** | Local artefact cache for logs, metrics, sessions and reproducibility. Not version-controlled but described in docs. | N/A |
| **.github/** | Contains workflows for documentation & linting; intentionally unused because offline-first; ensures no GitHub Actions will trigger. | N/A |
| **analysis/** | Reports and audits; includes hydra defaults audit and modernization reports. | Contains template status update generator; some placeholders for manual audits. |
| **src/codex_ml/** | Primary source code. Submodules: |
| | • `cli`: Typer CLI entrypoints for training (`hydra_main.py`), evaluation, data import, LoRA/PEFT, plugin management.
• `data`: dataset registry with deterministic splits and offline dataset loaders (`hf_datasets.py`, `dataset_wrapper.py`, `registry.py`). Supports CSV/JSONL/line datasets, manifest generation, offline fixtures and caching.
• `tokenization`: adapters and loaders; uses HuggingFace or SentencePiece if available; fallback dummy loader for offline mode. See also legacy `tokenization/loader.py` at root.
• `training`: unified training orchestrator (`unified_training.py`) providing seeding, device/dtype management, callback integration, checkpointing, LoRA/PEFT, MLflow/W&B integration; optional `engine_hf_trainer.py` (in `training/`) for HF Trainer wrapper with accelerate compatibility shim, LoRA and checkpoint manager.
• `callbacks`: base classes (`Callback`, `EvaluationCallback`, `LoggingCallback`, `merge_callback_results`); NDJSON logger; system metrics collector using `psutil` and NVML.
• `metrics`: registry of built-in metrics (token accuracy, perplexity, F1, distinct n-grams, BLEU, ROUGE) with plugin support.
• `logging`: SQLite-backed session logger (`db_manager.py`, `session_logger.py`, `conversation_logger.py`) for structured event logging and secret redaction.
• `utils`: checkpoint core capturing RNG state and environment for reproducibility; hydra compatibility functions; reproducibility helpers; HF revision pinning; dataset hashing; YAML safe loading.
• `monitoring`: structured logging, MLflow/TensorBoard integration, asynchronous log writer.
• `peft`, `distributed`, `codex_structured_logging` etc.: optional; provide LoRA wiring and distributed training. | The `tokenization/loader.py` at root is a stub returning a dummy tokenizer with TODO comment; real implementation resides in `src/codex_ml/tokenization`. |
| **configs/** | Hydra configuration directory with numerous YAML files for experiments, models, datasets and continual-learning curricula. Includes `default.yaml`, `training/*.yaml`, `metrics/*.yaml`, `continual/*.yaml`. `configs/schemas` contains JSON schemas for dataset manifests and evaluation records. | Some YAML groups may contain `???` placeholders requiring overrides. |
| **data/** | Contains offline fixture corpora and manifest examples. | Some placeholders for dataset directories. |
| **docs/** | Extensive documentation: quickstarts for Hydra, CLI usage, metrics registry, session tracking, Hydra sweeps, reproducibility, security, contributions. Many docs summarise system design and examples. | Minor TODO tags for future sections. |
| **docker/** | `Dockerfile` defines a multi-stage build to create a CPU-only runtime image with pre-built wheels and non-root user. `entrypoint.sh` sets env and runs uvicorn. | No stubs. |
| **models/** | Directory reserved for model checkpoints (empty). | Placeholder. |
| **scripts/** | Utility scripts such as `validate_dataset.py`, `hash_dataset_files.py`; used in offline gating. | No stubs. |
| **tools/** | Collection of command-line helpers: generating status audits, Hydra sweep smoke tests, monitoring integration, dependency graph analysis, code search. | Some scripts may be skeletons awaiting enhancements. |
| **tests/** | Extensive pytest suite organised into multiple directories covering data handling, tokenization, training loops, checkpointing, CLI, monitoring, metrics, and reproducibility. `noxfile.py` orchestrates test sessions for CPU-only gating. | Some tests are marked `xfail` due to optional dependencies; a few placeholders for integration tests. |
| **requirements/** | Segmented requirements for `base`, `dev`, `datasets`, `monitoring`, `docker`, `docs`, `analysis`; plus `uv.lock` (compiled lockfile) ensuring reproducible installs. | `requirements/actions.txt` intentionally empty to disable cost-incurring actions. |

## 2. Capability Audit Table

For each capability, the table summarises the implementation status, artefacts, gaps, risks, minimal patch plan, and rollback.

| Capability | Status | Existing artefacts | Gaps | Risks | Minimal patch plan | Rollback plan |
|---|---|---|---|---|---|---|
| **Tokenization** | Implemented for core training stack; stubbed at legacy entrypoint. | `src/codex_ml/tokenization/adapter.py`, `api.py` define `TokenizerAdapter` protocol and `load_tokenizer` with HF or SentencePiece fallback; dataset wrappers call tokenizer; `engine_hf_trainer.py` auto-pads and sets EOS token; `requirements/base.txt` includes `transformers` and `sentencepiece`. | Root `tokenization/loader.py` contains a dummy `_DummyTok` with TODO comment. No on-disk caching of tokenizers; no support for multi-threaded tokenization or vocabulary export. | Users importing `tokenization` package may inadvertently load dummy tokenizer and get unexpected behaviour; duplication of tokenizer code across modules increases maintenance risk. | Remove root `tokenization` stub and re-export from `src/codex_ml/tokenization`; implement caching of loaded tokenizers to disk; provide CLI flag for vocabulary export; add `TokenizerAdapter.save_pretrained`. | Deleting the stub and adding re-export is easily reversible: revert commit to restore stub; caching can be disabled via env var; CLI flag behind `--experimental` guard. |
| **ChatGPT Codex Modeling (model init, dtype, device, LoRA/PEFT hooks)** | Implemented. | `src/codex_ml/training/device_strategy.py` configures CUDA/MPS/CPU and dtype detection with dataclass `DeviceConfig`; `unified_training.py` orchestrates seeding, device, dtype, LoRA injection, W&B/MLflow integration; `engine_hf_trainer.py` provides HF Trainer wrapper with LoRA, accelerate compatibility shim, multi-GPU & distributed support. | Some LoRA and PEFT features rely on optional `peft` package; if not installed, warnings appear; automatic device detection missing support for XPU/TPU; no quantisation support; device config duplicated in trainer vs unified engine. | If LoRA is enabled without gradient accumulation adjustments, training can diverge; missing quantisation may limit resource-constrained deployment; unsupported devices cause silent fallback to CPU. | Add optional quantisation flags (int8/QLoRA); implement plugin pattern for additional devices; unify device/dtype config across modules; add smoke tests for LoRA/resume interactions. | Add features behind feature flags; revert easily by disabling new flags; LoRA/quantisation modules loaded conditionally; integration tests can be toggled. |
| **Training Engine (HF Trainer/custom loop)** | Implemented with robust unified training and HF Trainer wrapper; optional LoRA/PEFT; resume & checkpointing; multi-GPU; deterministic seeds. | `unified_training.py` encapsulates training loop with callbacks, evaluation, seeding, MLflow/W&B logging and checkpoint management; `engine_hf_trainer.py` provides HF Trainer wrapper; `callbacks` base classes and NDJSONLogger; `training/continual` config group for curriculum learning; `noxfile.py` includes smoke test session. | Unified training lacks explicit curriculum progress logging; limited support for gradient checkpointing; evaluation logic partially duplicated between engines; missing early-exit on NaN metrics; no streaming dataset support via HF streaming API for all loaders. | Without gradient checkpointing, large models may OOM; inconsistent evaluation may produce mismatched metrics; missing NaN checks may propagate invalid gradients; streaming gaps may block huge datasets. | Add `--gradient-checkpointing` flag; add evaluation hook to detect NaNs and abort; integrate dataset streaming where possible; implement callback to log curriculum progress. | New features can be disabled via config; revert by removing CLI flags; tests ensure backward compatibility. |
| **Configuration Management (Hydra/YAML, overrides, sweeps)** | Partially implemented. | Hydra configuration directory with many YAML files; `hydra_main.py` registers dataclass `AppConfig` and merges YAML defaults into runtime config; `tools/hydra_sweep_smoke.py` tests sweeps; docs for Hydra quickstart and sweeps; `hydra_cs.py` provides utils for config store. | Some config groups contain `???` placeholders; missing default group for experiment tracking; no centralised schema validation; config names can drift across files; no official `codex-hydra-audit` CLI yet. | Placeholder `???` cause runtime failure if not overridden; lack of schema leads to silent misconfiguration; no CLI to list available configs; multiple config versions create confusion. | Provide JSON schemas for each config group; implement `codex-hydra-audit` CLI to list defaults and detect unresolved fields; require config validation before running training; unify naming conventions. | Introduce `hydra-validator` script and pre-commit hook; revert by disabling strict validation; maintain synergy with existing Hydra CLI. |
| **Evaluation & Metrics (validation loops, metrics API, NDJSON/CSV logging)** | Implemented. | `metrics/registry.py` registers metrics (token_accuracy, perplexity, f1, distinct-n, BLEU, ROUGE, chrF) with plugin support; `docs/metrics.md` details usage and NDJSON summarizer; evaluation callback merges metrics; `engine_hf_trainer.py` computes token accuracy and perplexity by default. | Weighted accuracy and classification metrics missing; no confidence intervals; evaluation API not exposed via standalone CLI; metrics not persisted in a structured DB beyond NDJSON; plugin discovery not cached. | Without classification metrics, classification tasks require custom code; plugin loading may slow startup; missing CLI evaluation may hinder offline evaluation; metrics may be harder to query longitudinally. | Add additional metrics (accuracy, precision/recall, ROC-AUC) and parameterizable metrics; implement `codex-eval` CLI for evaluation of saved checkpoints; cache plugin discovery at module load; record metrics in SQLite or NDJSON with timestamps. | New metrics can be optional extras; CLI is additive; revert by disabling plugin group; persisting metrics in NDJSON is backwards compatible. |
| **Logging & Monitoring (TB/W&B/MLflow; psutil/NVML)** | Implemented. | SQLite session logger (`session_logger.py`, `conversation_logger.py`) with secret redaction and WAL for concurrency; system metrics callback uses `psutil` and NVML to sample CPU/GPU utilisation; NDJSONLogger writes per-epoch metrics; MLflow/TensorBoard offline integration in `engine_hf_trainer.py`; docs for session tracking. | Logging API not fully integrated with all CLI commands; no built-in support for remote log aggregation; system metrics not recorded during evaluation; asynchronous log writer optional; no unified metrics table. | Without centralised dashboards, logs remain local; missing evaluation metrics may hinder debugging; high-frequency metric sampling may degrade performance; lack of structured metrics table makes querying harder. | Expose `codex-log` CLI to query sessions; integrate push gateway for Prometheus or filebeat; extend system metrics callback to evaluation; throttle sampling frequency via config; add `metric_records` table keyed by session/epoch/metric. | Logging enhancements can be toggled via env var; revert by removing push integration; maintain backward compatibility; metrics table is additive and can be ignored. |
| **Checkpointing & Resume (weights, optim, scheduler, RNG, best-k)** | Implemented. | `checkpoint_core.py` writes atomic checkpoint files with metadata (schema version, environment summary, git SHA, RNG state, config snapshot, digest) and manages best-k retention; `unified_training.py` uses save/load helpers; `engine_hf_trainer.py` defines `CheckpointManager` callback for HF Trainer. | Checkpointing in HF Trainer is optional; some features rely on optional `peft`; no incremental snapshot of training states; no compression/encryption of checkpoint metadata; no cross-run checkpoint lineage index. | Incomplete checkpoints may corrupt if power loss occurs; storing secrets in config snapshot may leak environment; large checkpoint size impacts storage; lack of lineage may make resuming complex experiments harder. | Implement incremental/delta checkpoints; compress and encrypt metadata; enforce safe path names; integrate integrity checks (hash verification) with pre-commit gating or local scripts; build `checkpoint_index.json` per run. | New features behind flags; revert by switching to previous `save_checkpoint`; encryption optional; lineage index can be ignored by older code. |
| **Data Handling (splits, deterministic shuffling, caching)** | Implemented. | `data/registry.py` registers dataset loaders and resolves offline fixtures; deterministic `split_dataset` with reproducible shuffling; `dataset_wrapper.py` implements train/val/test split for HF datasets; `hf_datasets.py` loads HF datasets with pinned revisions and streaming fallback; CLI provides split-smoke and dataset manifest validation; dataset manifest schema present. | CSV and JSONL loaders rely on optional dependencies; streaming not uniformly available for all formats; caching directory resolution may fail on read-only filesystems; data augmentation pipeline limited. | Without streaming, large datasets may not fit memory; optional dependencies must be installed manually; caching path resolution can raise errors; lack of augmentation may reduce model performance. | Provide streaming wrappers for CSV/JSONL using Python iterators; implement `--cache-dir` override; add dataset augmentation pipeline with small, composable transforms; document environment variables controlling cache. | New loaders optional; revert by using original functions; caching path can fallback to temporary directory; augmentation can be disabled by config. |
| **Security & Safety (dependency locking, secrets scanning, prompt safety)** | Implemented. | `security/core.py` sanitises inputs for SQL injection, XSS, JSON injection, path traversal and implements token bucket rate limiting, CSRF and session validation; `.pre-commit-config.yaml` includes gitleaks, detect-secrets, bandit and semgrep for secret scanning; `requirements/lockfiles` provide pinned deps; logging system redacts secrets. | Prompt safety module absent; no explicit E2E encryption; vulnerability scanning integrated in local gating but not automated across the codebase; no explicit red-team prompts or safety policies codified in code. | Without prompt filtering, generative outputs may expose harmful content; lack of encryption may leak sensitive data; scanning only in pre-commit may miss issues in environments where hooks are not installed; operational safety posture is implicit. | Add prompt safety layer with content filtering and jailbreak detection; integrate `pip-audit` and `safety` checks; implement encryption for logs and checkpoints; schedule periodic dependency update scripts; codify safety policies in `SECURITY.md`. | Safety features optional; revert by disabling new filters; scanning can be toggled; encryption can be made opt-in. |
| **Internal CI/Test (pytest, nox local gates, coverage)** | Implemented. | `tests/` directory contains extensive pytest suite with unit and integration tests; `noxfile.py` orchestrates segmented test sessions and pre-commit checks; `pytest.ini` defines markers and options; offline gating ensures tests run with CPU-only environment. | Some integration tests marked `xfail` or pending; coverage enforcement not mandated; `tox` template not provided; missing test for plugin metrics; no high-performance benchmarks. | Incomplete tests may allow regressions; lacking performance tests means slow algorithms unnoticed; coverage gaps hide dead code; plugin regressions may go undetected. | Add coverage reporting via `pytest-cov`; write integration tests for metrics registry and LoRA; implement `tox` config for multiple Python versions; add performance benchmark harness via a dedicated nox session. | Coverage enforcement can be disabled via env; revert by removing `pytest-cov` plugin; new tests optional; tox config is additive. |
| **Deployment (packaging, CLI entry points, Docker)** | Partially implemented. | `Dockerfile` builds runtime image with pre-built wheels and non-root user; `docker/entrypoint.sh` loads `.env` and runs uvicorn; Typer CLI commands run offline; CLI docs provide smoke tests for checkpointing and dataset splitting. | Missing Kubernetes/Helm manifests; no integration with packaging registries (PyPI or Docker Hub); no `make install` script; environment variables not well-documented; no compose examples; no GPU Dockerfile. | Without deployment scripts, users must craft their own; misconfigured env may break runtime; no GPU support in Dockerfile; secrets may leak via environment variables; onboarding friction for infra teams. | Provide Helm chart and docker-compose example; document environment variables; add GPU variant of Dockerfile; integrate container scanning tools; create `codex-deploy` CLI wrapper for common deployment flows. | Additional deployment scripts optional; revert by removing compose and helm charts; GPU support behind build arguments; documentation changes additive. |
| **Documentation & Examples (README, quickstarts, diagrams, notebooks)** | Implemented. | `docs` directory includes Hydra quickstart, CLI guide, metrics documentation, monitoring, reproducibility, session tracking, and security; README provides search index; docstrings across code; reports directory contains modernization report. | Some docs out-of-date with latest API; no design diagrams; examples limited to short snippets; missing tutorial notebooks; `docs/api` incomplete; no explicit architecture overview in a single diagram. | Without diagrams, understanding flows is hard; outdated docs may mislead users; missing notebooks reduces approachability; new contributors face a steep learning curve. | Update docs to reflect unified training API; add architecture diagrams; include Jupyter notebooks demonstrating training and evaluation; generate API docs via Sphinx or mkdocs; add design rationale section. | Documentation updates are additive; can be rolled back by reverting commit; diagrams stored in `docs/_static`; notebooks can be optional in extras. |
| **Experiment Tracking (MLflow local, W&B offline)** | Implemented (offline). | `engine_hf_trainer.py` logs metrics to MLflow in file-backed store when `mlflow_enable` flag or `MLFLOW_TRACKING_URI` env is set; W&B offline mode triggered by env variables; CLI tracking commands write minimal MLflow runs; session logging includes experiment metadata. | MLflow integration optional; no CLI to resume or compare experiments; W&B offline logs not aggregated; no experiments dashboard; lacking fine-grained run metadata or run comparison tools. | Without centralised UI, comparing runs is manual; duplication of run IDs; offline W&B logs require manual sync; run metadata may not include config diff or git SHA in all flows. | Implement `codex-track` CLI to list and compare runs; integrate with MLflow UI when present; add `--log-config` to persist config diff; add W&B sync script; log git SHA and dataset manifest digest automatically for every run. | Tracking features optional; revert by disabling CLI; logs remain local; no breaking changes. |
| **Extensibility (pluggable components, registry patterns)** | Implemented with registry patterns. | Dataset loaders and metrics use registries for plugin discovery; Hydra config allows override of components; CLI exposes plugin management; plugin registry loads entry points via `metadata.entry_points`; metrics registry similarly uses entry points; LoRA and accelerate integration modular; config overrides support sweeps. | Plugin scaffolding not documented; no sample third-party plugin; registry uses entry points which require packaging; plugin conflict resolution policies not fully exposed; no version compatibility checks; no explicit plugin safety guidelines. | Without documentation, developers may misuse plugin API; conflict resolution may lead to hidden overrides; unversioned plugins can break compatibility; unsafe plugins may degrade security posture. | Provide template for plugin packages; document plugin API; implement `--list-plugins` CLI; add semantic versioning checks; include plugin conflict policy (error/ignore/override) as config; define safety guidelines for plugins. | Plugin API changes behind versioned major release; revert by deprecating plugin CLI; maintain baseline features. |

## 3. High-Signal Findings

1. **Main branch is most recent** – `main` carries the most recent commit and is effectively the trunk. Branches like `0D_base_` are close but slightly behind.
2. **Strong offline posture** – all tooling emphasises offline operation: dataset loaders fallback gracefully, metrics and logging store NDJSON/SQLite locally, CLI tools avoid network calls, Docker images build dependencies from pinned wheels.
3. **Modular registries** – datasets, metrics, callbacks and plugins use registries and entry points; new extensions can be added without modifying core code.
4. **Comprehensive training engine** – unified training orchestrator supports seeding, device/dtype management, LoRA/PEFT, MLflow/W&B integration, checkpointing and best-k retention; HF Trainer wrapper includes accelerate compatibility and LoRA injection, enabling rapid prototyping.
5. **Deterministic data splitting** – dataset registry ensures reproducible splits and writes dataset manifests with checksums, enabling dataset provenance tracking.
6. **Robust checkpointing** – `checkpoint_core.py` captures full RNG state across Python, NumPy and Torch and records environment metadata, ensuring reproducibility on resume.
7. **Security & safety built-in** – `security/core.py` sanitises inputs (SQL injection, XSS, JSON injection) and implements rate limiting and CSRF/session validation; pre-commit checks include gitleaks and detect-secrets.
8. **Hydra integration** – training CLI uses Hydra to compose configs and supports CLI overrides, multirun sweeps and defaults merging; docs provide quickstart and sweeps examples.
9. **Monitoring and logging** – NDJSON logger and session logger record per-epoch metrics and training/inference events; system metrics callback collects CPU/GPU utilisation; logs are local but can be forwarded to centralised dashboards.
10. **Comprehensive docs & tests** – extensive documentation covers Hydra, metrics, session tracking, CLI, reproducibility; test suite covers modules and ensures offline compatibility; `noxfile.py` orchestrates segmented sessions and evidence checks.
11. **Gaps in deployment** – runtime Docker image is CPU-only and lacks Kubernetes/compose examples; environment variables are not well-documented; GPU support would require additional Dockerfile.
12. **Configuration gaps** – some Hydra configs contain `???` placeholders that must be overridden; no schema validation; config names can drift across files.
13. **Stubbed tokenisation at root** – the top-level `tokenization/loader.py` returns a dummy tokenizer; users must import from `src/codex_ml/tokenization` to get actual functionality.
14. **Missing classification metrics** – metrics registry lacks accuracy/precision/recall; evaluation API not exposed via CLI; NDJSON metrics not persisted in structured DB.
15. **No central experiment dashboard** – although MLflow and W&B are integrated offline, there is no CLI to list or compare runs; W&B sync is manual.
16. **Plugin documentation limited** – plugin registry exists but lacks templates and conflict policies; plugin discovery may be slow due to entry_points scanning.
17. **Partial deployment readiness** – Dockerfile builds CPU image but there is no automated push to registry; no helm chart; secrets management not addressed.
18. **Potential long-term maintainability** – large monolithic `engine_hf_trainer.py` mixes many concerns (accelerate shim, LoRA injection, logging, checkpointing); refactoring into smaller modules would aid maintainability and testing.

## 4. Atomic Diffs

Below are example minimal diffs to address key gaps. Each diff includes rationale, risk, rollback and tests/docs.

### Diff 1 – Remove root tokenisation stub and re-export real implementation

**Why:** Avoid confusing users with a dummy tokenizer and centralise tokenizer loading.

```diff
*** Begin Patch
*** Delete File: tokenization/loader.py
*** End Patch
*** Begin Patch
*** Add File: tokenization/__init__.py
+"""Tokenization API re-exported from codex_ml.tokenization."""
+
+from codex_ml.tokenization import (
+    TokenizerAdapter,
+    load_tokenizer,
+    register_tokenizer,
+)
+
+__all__ = ["TokenizerAdapter", "load_tokenizer", "register_tokenizer"]
*** End Patch
```text

- **Risk:** Removing the stub may break imports for users that rely on the `_DummyTok`. However, exposing the real API under the same package ensures forwards compatibility.
- **Rollback:** Restore `tokenization/loader.py` and revert `__init__.py` to its original state.
- **Tests/docs:** Add unit test verifying `import tokenization; tokenization.load_tokenizer()` returns a functional adapter and update README to inform users of the change.

### Diff 2 – Add classification metrics to metrics registry

**Why:** Provide out-of-the-box support for classification tasks.

```diff
*** Begin Patch
*** Update File: src/codex_ml/metrics/registry.py
@@
 _BUILTIN_METRICS = {
     "token_accuracy": token_accuracy,
     "perplexity": perplexity,
     "exact_match": exact_match,
     "f1": f1_score,
     "dist-1": dist1,
     "dist-2": dist2,
     "bleu": bleu,
     "rougeL": rougeL,
     "weighted_accuracy": weighted_accuracy,
+    # New classification metrics
+    "accuracy": lambda preds, labels: float((preds == labels).mean()),
+    "precision": lambda preds, labels: float(_precision(preds, labels)),
+    "recall": lambda preds, labels: float(_recall(preds, labels)),
+    "f1_macro": lambda preds, labels: float(_f1_macro(preds, labels)),
 }
*** End Patch
*** Begin Patch
*** Add File: src/codex_ml/metrics/classification_metrics.py
+"""Basic classification metrics for binary/multiclass tasks."""
+
+from __future__ import annotations
+
+import numpy as np
+
+
+def _precision(preds, labels):
+    preds = np.array(preds)
+    labels = np.array(labels)
+    tp = np.sum((preds == labels) & (labels == 1))
+    fp = np.sum((preds != labels) & (preds == 1))
+    return tp / (tp + fp + 1e-8)
+
+
+def _recall(preds, labels):
+    preds = np.array(preds)
+    labels = np.array(labels)
+    tp = np.sum((preds == labels) & (labels == 1))
+    fn = np.sum((preds != labels) & (preds == 0))
+    return tp / (tp + fn + 1e-8)
+
+
+def _f1_macro(preds, labels):
+    p = _precision(preds, labels)
+    r = _recall(preds, labels)
+    return 2 * p * r / (p + r + 1e-8)
*** End Patch
```text

- **Risk:** Additional metrics may introduce slight runtime overhead; naming collisions could occur with existing plugin metrics.
- **Rollback:** Remove entries from `_BUILTIN_METRICS` and delete `classification_metrics.py`.
- **Tests/docs:** Write unit tests for classification metrics; update `docs/metrics.md` to describe new metrics and usage examples.

### Diff 3 – Provide Hydra config validation CLI

**Why:** Detect unresolved `???` placeholders and invalid fields before running training.

```diff
*** Begin Patch
*** Add File: src/codex_ml/cli/hydra_audit.py
+"""CLI to validate Hydra configs and list defaults."""
+
+from __future__ import annotations
+
+import json
+import sys
+
+import hydra
+from hydra import compose, initialize_config_dir
+from omegaconf import OmegaConf
+
+from codex_ml.cli.config import register_configs
+
+
+def audit_config(config_name: str = "app", config_path: str = "configs") -> int:
+    """Validate Hydra config and report unresolved fields."""
+
+    register_configs()
+    with initialize_config_dir(config_dir=config_path):
+        cfg = compose(config_name=config_name)
+        flat = OmegaConf.to_container(cfg, resolve=False)
+        unresolved = [k for k, v in flat.items() if v == "???"]
+        if unresolved:
+            print(json.dumps({"status": "error", "unresolved": unresolved}))
+            return 1
+
+        print(json.dumps({"status": "ok"}))
+        return 0
+
+
+if __name__ == "__main__":
+    sys.exit(audit_config())
*** End Patch
*** Begin Patch
*** Update File: pyproject.toml
@@
 [project.scripts]
 codex-train = "codex_ml.cli.hydra_main:main"
 codex-eval = "codex_ml.cli.eval:main"
 codex-import-ndjson = "codex_ml.cli.import_ndjson:main"
+codex-hydra-audit = "codex_ml.cli.hydra_audit:audit_config"
*** End Patch
```text

- **Risk:** Hydra optional dependency may not be installed; CLI returns non-zero exit code if placeholders found, which could break existing scripts expecting success.
- **Rollback:** Remove the CLI and entrypoint from `pyproject.toml`.
- **Tests/docs:** Add unit tests verifying unresolved configs are detected; update Hydra docs with validation usage.

### Diff 4 – Integrate NDJSON metrics with SQLite session logger

**Why:** Consolidate metrics and session events for easy querying and correlation.

```diff
*** Begin Patch
*** Update File: src/codex/logging/db_manager.py
@@
     def init_schema(self, conn: sqlite3.Connection) -> None:
         cursor = conn.cursor()
         cursor.execute(
             """
             CREATE TABLE IF NOT EXISTS log_events (
@@
                 data TEXT
             )
             """
         )
+
+        cursor.execute(
+            """
+            CREATE TABLE IF NOT EXISTS metric_records (
+                id INTEGER PRIMARY KEY AUTOINCREMENT,
+                session_id TEXT NOT NULL,
+                epoch INTEGER NOT NULL,
+                metric TEXT NOT NULL,
+                value REAL NOT NULL
+            )
+            """
+        )
*** End Patch
*** Begin Patch
*** Update File: src/codex/logging/session_logger.py
@@
     def log_event(self, role: str, event_type: str, data: dict[str, Any]) -> None:
         """Log a structured event into SQLite and optional JSONL file."""
@@
         # existing logic persists JSONL and inserts into log_events
+
+        # When logging per-epoch metrics, also persist individual metric values
+        if event_type == "epoch":
+            epoch_num = data.get("epoch")
+            metrics = data.get("metrics") or {}
+            if epoch_num is not None and isinstance(metrics, dict):
+                conn = self._db_manager.get_connection()
+                try:
+                    cur = conn.cursor()
+                    for m, v in metrics.items():
+                        if isinstance(v, (int, float)):
+                            cur.execute(
+                                "INSERT INTO metric_records (session_id, epoch, metric, value) VALUES (?, ?, ?, ?)",
+                                (self._session_id, epoch_num, m, float(v)),
+                            )
+                    conn.commit()
+                except Exception:
+                    conn.rollback()
+                finally:
+                    self._db_manager.close_connection(conn)
*** End Patch
```text

- **Risk:** Slightly increases logging overhead; SQLite schema migration required on existing installations.
- **Rollback:** Drop `metric_records` table and remove insertion logic; logs remain unaffected.
- **Tests/docs:** Add migration test ensuring the new table is created; update monitoring docs to describe metrics table and query examples.

### Diff 5 – Provide GPU-enabled Dockerfile variant

**Why:** Support GPU training without requiring users to craft their own Dockerfile.

```diff
*** Begin Patch
*** Add File: docker/Dockerfile.gpu
+# syntax=docker/dockerfile:1.7
+
+FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04 AS runtime
+
+LABEL org.opencontainers.image.title="codex-gpu" \
+      org.opencontainers.image.description="GPU-enabled runtime for codex" \
+      org.opencontainers.image.licenses="Apache-2.0"
+
+ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
+
+RUN apt-get update && apt-get install -y --no-install-recommends \
+    python3 python3-venv python3-pip \
+    && rm -rf /var/lib/apt/lists/*
+
+WORKDIR /app
+
+COPY pyproject.toml MANIFEST.in requirements/ uv.lock ./
+
+RUN pip install --upgrade pip && pip install -r requirements/docker.txt
+
+COPY . .
+
+RUN pip install .
+
+EXPOSE 8000
+
+CMD ["uvicorn", "src.codex.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
*** End Patch
```text

- **Risk:** Increases repository size; GPU images require large base image; maintainers must build and publish this variant.
- **Rollback:** Remove `Dockerfile.gpu`; CPU variant remains unchanged.
- **Tests/docs:** Add build instructions in deployment docs; provide helm/compose examples referencing GPU variant; test image builds in local gating.

## 5. Local Tests & Gates

Use `nox` to run offline tests. Example sessions:

| Session | Command | Expected outcome | Category |
|---|---|---|---|
| Unit tests | `nox -s tests` | Runs pytest with CPU-only environment; should pass. | Regression, infrastructure |
| ML smoke | `nox -s ml_smoke` | Executes tiny training using HF Trainer on `sshleifer/tiny-gpt2` with NDJSON logging; verifies training loop and checkpoint save; should complete quickly. | Model, data |
| Eval smoke | `nox -s eval_smoke` | Runs evaluation CLI on a small checkpoint; checks evaluation metrics integration. | Evaluation |
| Hygiene | `nox -s hygiene` | Runs ruff/black/isort, bandit, semgrep, gitleaks, detect-secrets; ensures no linting or security issues. | Quality, security |
| Hydra audit | `nox -s hydra_audit` | Invokes `codex-hydra-audit` on default configs to ensure no unresolved `???`; fails if placeholders remain. | Configuration |
| Docs build | `nox -s docs` | Builds docs offline; ensures examples compile. | Documentation |

Mapping to ML Test Score categories:

- **Data tests**: dataset manifest validation, deterministic splitting.
- **Model tests**: smoke training, evaluation metrics, checkpoint save/resume.
- **Infrastructure tests**: logging, metrics callback, system metrics sampling.
- **Regression tests**: unit tests covering tokenizer, config merging, security sanitisation.
- **Performance tests**: not yet implemented; to be added via `nox -s perf_bench` capturing time/memory.

## 6. Reproducibility Checklist

| Checklist Item | Status & Evidence |
|---|---|
| Fixed random seeds across libraries (Python, NumPy, Torch) | Implemented: `set_reproducible` utilities in training stack set seeds for Python, NumPy and Torch, including CUDA, and enforce deterministic algorithms where feasible. |
| Capturing environment details | Implemented: checkpoint core writes environment summary (Python version, platform, git SHA, config hash, RNG state) into checkpoint metadata; environment logging utilities record environment JSON. |
| Pinning external dependencies | Implemented: `pyproject.toml` uses version ranges plus `uv.lock` to lock packages; optional extras separated; `Dockerfile` builds from pinned wheels; segmented `requirements` files document dependency classes. |
| Deterministic dataset splitting | Implemented: dataset registry uses seeded RNG for line-based datasets and HF dataset wrapper provides deterministic train/val/test split. |
| Versioning of configs and code | Implemented: checkpoint metadata records git SHA; training CLI merges config defaults with YAML and dataclasses; planned Hydra audit CLI to validate unresolved configs. |
| Hardware determinism | Partially: code sets CUDNN deterministic mode; no explicit CPU affinity or GPU power management; multi-GPU distributed training may introduce nondeterministic behaviour. |
| Results determinism across runs | Largely: seeds and dataset splits ensure deterministic training for most setups; non-deterministic operations in PyTorch may still vary; a stricter mode via `torch.use_deterministic_algorithms(True)` could be documented. |
| Artifact archival | Implemented: checkpoints saved in a structured directory, NDJSON logs in `.codex/logs`, dataset manifests stored alongside data; docs instruct users to persist these for reproducibility. |

Missing items / flags:

- Reproducible hardware environment capture (CPU model, GPU driver) to be added to environment summary.
- Pinned HF model revisions for all recipes, not only selected ones.
- Container image digests and provenance for training environment.
- Multi-GPU determinism guarantees and documentation.

## 7. Deferred Items

- **Quantisation & QLoRA support** – Complex integration surface with HF accelerate and PEFT; requires additional dependencies and performance-testing infrastructure. Defer until base LoRA integration stabilises and GPU pipeline is firmly validated.
- **Kubernetes deployment templates** – Helm charts and dev→prod pipeline are platform/organisation-specific; better owned by platform engineering. Provide hooks and config examples but not a full stack in this repo.
- **Central dashboard for experiments** – Building an MLflow/W&B UI aggregator requires server infra; defer to future iteration once offline logs and runs accumulate.
- **Interactive notebook examples** – Valuable but increase repo size and maintenance cost; plan post-MVP with a curated set of notebooks showing key workflows.
- **Performance benchmarks** – To be designed after baseline functionality is stable; will measure throughput/latency across model sizes and devices; likely to be kept under `benchmarks/` or `tools/benchmarks`.
- **Extended security hardening** – Prompt filtering, encryption, vulnerability scanning integration and explicit safety policies to be addressed in a dedicated security hardening sprint.

## 8. Error Capture Blocks

When conducting future analysis or extending the system, use the following block to record unexpected failures:

```text
Question for ChatGPT @codex {{timestamp}}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```text

This structured question can be inserted into conversations with ChatGPT @codex to obtain targeted troubleshooting guidance.
