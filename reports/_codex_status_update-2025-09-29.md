# _codex_: Status Update (2025-09-29) — Branch: 0D_base_ @ 94c111f1

## 1. Audit Scope & Provenance
- **Most recent branch/commit:** `0D_base_` @ `94c111f1222631c4bf42564eb290438d430cd599` (merge of `7533a009b187b8ca4e8dcc1417bfe3c868e31a86` and `ee408c3929a786992b0ef57a9214ae2bbfd1351e`).【F:.codex/status/provenance.json†L2-L16】
- **Default branch:** `main`; latest activity surfaced via GitHub Events `PullRequestReviewEvent` on 2025-09-29T03:17:45Z.【F:.codex/status/provenance.json†L2-L16】
- **Connectors consulted:** GitHub Events + Contents APIs; local checkout pinned to `S1` for analysis.【F:.codex/status/provenance.json†L12-L15】
- **S0 baseline:** not provided; diff/log addenda note this absence.【F:.codex/status/diff-S0_to_S1.txt†L1-L1】

## 2. Repo Map & Structural Signals
- Top-level inventory highlights large automation metadata under `.codex/`, core libraries in `src/`, ML stack in `codex_ml/`, configs, docs, and extensive test suites.【F:reports/repo_map.md†L1-L40】
- Significant generated/third-party material present in local `.venv/` (installed during audit) — excluded from change set but inflates LoC summary.【F:artifacts/metrics/loc_by_dir.csv†L1-L20】
- Docstring coverage averages **30.1%** across 16,134 documented definitions, signalling gaps in API documentation.【F:artifacts/metrics/docstring_coverage.json†L1-L6】
- Stub detection flagged **391 Python files** with TODO/pass/NotImplemented markers, underscoring widespread incompleteness.【33b595†L1-L6】
- Test-to-code LOC ratio ≈ **0.66** (23,917 test LOC vs 36,070 library LOC), but many suites skip due to missing heavy deps.【a09e95†L1-L16】【085809†L1-L48】

## 3. Capability Audit Table
| # | Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
|---|---|---|---|---|---|---|---|
| 1 | Tokenization (SentencePiece, padding/truncation) | Partially Implemented | SentencePiece adapter + CLI cover train/load/encode/decode with padding controls.【F:src/codex_ml/tokenization/sentencepiece_adapter.py†L1-L99】【F:src/codex_ml/tokenization/cli.py†L1-L107】 | Tokenization tests fail when only stub `transformers` available; no automated round-trip/padding assertions; SentencePiece optional dep not pinned in test env.【085809†L1-L48】 | Runtime regressions go unnoticed; CLI unusable without manual deps; downstream metrics unstable. | (a) Guard tests against stub `transformers` by injecting minimal `ModuleSpec` and skip when stub active. (b) Add nox `tests_min` dependency on tokenizer extras to exercise CLI. (c) Write unit test for encode→decode round-trip with padding. | Keep new guards behind env checks; revert by deleting added skip logic and tests if they block CI. |
| 2 | ChatGPT Codex Modeling (init, dtype, LoRA) | Partially Implemented | Decoder-only GPT module with rotary embeddings and LoRA hooks; loader auto-applies LoRA or Hugging Face fallback with dtype/device selection.【F:src/codex_ml/models/decoder_only.py†L1-L160】【F:src/codex_ml/modeling/codex_model_loader.py†L1-L160】 | Heavy reliance on optional deps (torch, transformers, peft); no tiny offline model smoke tests; dtype/device mismatch errors only caught at runtime. | Model load failures silently fallback; LoRA misconfiguration undetected; dtype strings mis-typed cause ValueError. | (a) Add offline tiny-model smoke test using bundled decoder with CPU dtype. (b) Extend loader to validate dtype before import. (c) Document required extras in CLI help. | Back out tests and dtype guard if optional deps unavailable in target env. |
| 3 | Training Engine (precision, grad accumulation) | Partially Implemented | Functional training loop with checkpoint SHA256, retention, telemetry hooks, optional MLflow, and torch dataset fallback stubs.【F:src/codex_ml/train_loop.py†L1-L160】 | Many callbacks degrade to no-ops when deps missing; no deterministic smoke test; no coverage verifying grad accumulation/resume interplay. | Silent degradation (callbacks/logging absent); determinism claims unverified; resume may regress. | (a) Add deterministic overfit test toggling `set_cudnn_deterministic`. (b) Provide structured logging when optional callbacks skipped. (c) Document required extras in configs. | Disable new test and logging if resource constrained; rely on existing manual QA. |
| 4 | Config Management (Hydra/YAML, overrides) | Partially Implemented | Hydra entrypoint registers structured configs; base experiment YAML enumerates seeds/device/logging/checkpoints.【F:src/codex_ml/cli/hydra_main.py†L1-L57】【F:configs/base.yaml†L1-L25】 | No defaults list documentation; limited validation of overrides; config schema huge (16k LOC) with minimal tests. | Misconfigurations slip by; overrides break silently; onboarding friction. | (a) Add `python -m codex_ml.cli.config --info defaults` doc & CLI tests. (b) Introduce pydantic validation smoke test for base config. | Remove new tests/docs if Hydra not desired; revert CLI doc snippet. |
| 5 | Evaluation & Metrics | Partially Implemented | Evaluation runner loads JSONL/CSV, encodes labels, integrates provenance seeding.【F:src/codex_ml/eval/runner.py†L1-L120】 | Metrics modules lack unit tests; no NDJSON logging example; CLI entrypoint fails without extras. | Evaluation regressions unnoticed; inconsistent outputs; offline metrics not reproducible. | (a) Add fixture-driven tests for `_load_records` CSV/JSONL paths. (b) Provide sample eval CLI invocation in docs with offline expectation. | Revert tests/docs if they break minimal env. |
| 6 | Logging & Monitoring (TensorBoard/W&B/MLflow, psutil/NVML) | Partially Implemented | System metrics module auto-detects psutil/NVML, env flags to disable GPU polling.【F:src/codex_ml/monitoring/system_metrics.py†L1-L135】 | psutil optional; no NVML stub tests; CLI entrypoints missing; watchers degrade silently; W&B not validated. | Lack of metrics visibility; GPU sampling fails quietly; production monitoring inconsistent. | (a) Add integration test verifying psutil fallback when missing. (b) Document env toggles for NVML in README. | Remove new tests/doc if environment cannot import psutil/NVML. |
| 7 | Checkpointing & Resume | Partially Implemented | Checkpoint utilities capture RNG across python/numpy/torch, compute SHA256, prune best-K.【F:src/codex_ml/utils/checkpoint.py†L1-L160】 | Tests skipped without torch/numpy; no JSON manifest validation; retention policies not unit tested. | Resume may corrupt RNG state; best-K pruning bugs linger. | (a) Provide pure-Python test using torch stub to validate RNG serialization fallback. (b) Add schema check for checkpoint metadata. | Drop new tests if CI lacks torch; fallback to manual testing. |
| 8 | Data Handling (splits, caching, determinism) | Partially Implemented | Loader streams datasets with shard checksums, deterministic shuffle, safety filters.【F:src/codex_ml/data/loader.py†L1-L160】 | No dataset manifest tests; caching lacks hashing tests; safety filters not integrated in data pipeline tests. | Data drift, cache corruption undetected; policy bypass risk. | (a) Add hashed JSONL smoke test verifying `CacheManifest`. (b) Wire safety filter call in tests. | Remove new tests if large files cause timeouts. |
| 9 | Security & Safety | Partially Implemented | Safety filters include policy loader, redaction, env overrides; detect-secrets/bandit run locally.【F:src/codex_ml/safety/filters.py†L1-L156】【F:artifacts/security/detect-secrets.txt†L1-L15】【F:artifacts/security/bandit.txt†L1-L20】 | Safety CLI missing automation; Safety scan requires login; filters rely on optional YAML; no secrets baseline committed. | Sensitive strings leak; dependency vulns go unnoticed; false sense of coverage. | (a) Document manual steps for `safety` or integrate offline DB; (b) add regression tests for policy load failure. | Revert doc/test additions if `safety` licensing not available. |
|10| Internal CI/Test (pytest, nox, coverage) | Partially Implemented | Nox sessions cover lint/typecheck/tests/coverage; coverage session enforces fail-under; pytest suite broad.【F:noxfile.py†L1-L818】 | `nox -s lint` fails (ruff violations); tests_min/coverage fail without CLI deps & transformers; coverage 5.40% <80%.【835782†L1-L110】【90b94e†L1-L25】【4834d7†L1-L27】【15609e†L1-L124】 | Local gate unreliable; regressions slip; developer friction. | (a) Ensure CLI extras installed in test sessions. (b) Add doc for required extras; optionally adjust fail-under when running subset. | Revert extra installs if causing slow builds; restore prior fail-under once coverage improves. |
|11| Deployment (packaging, Docker, CLI) | Partially Implemented | Dockerfile builds editable install; pyproject exposes CLI entrypoints and extras.【F:Dockerfile†L1-L24】【F:pyproject.toml†L1-L60】 | CLI extras empty; `codex-*` commands fail missing `codex` package; no smoke tests for container. | Docker build works but runtime fails; CLI unusable out-of-box. | (a) Populate `cli` extra with `click`/`typer`; (b) add `nox` session to run `codex-ml-cli --help` smoke test. | Remove extras if packaging conflicts; skip smoke session if environment lacks deps. |
|12| Documentation & Examples | Partially Implemented | README with quickstart, LoRA example, architecture; docs tree extensive.【F:README.md†L1-L60】【F:docs/guides/AGENTS.md†L1-L60】 | Notebook `gpu_training_example.ipynb` invalid JSON; docs link audit lacks verification; docstring coverage low.【1e822a†L1-L9】【056b81†L1-L6】 | Users follow broken notebook; doc drift. | (a) Fix notebook JSON and add nbformat check to CI. (b) Increase docstring coverage for critical APIs. | Revert notebook fix if upstream to be replaced; postpone docstring work if schedule tight. |
|13| Experiment Tracking (MLflow offline) | Partially Implemented | Utility enforces `file:./artifacts/mlruns` default and safe guard for remote URIs; offers no-op logger fallback.【F:src/codex_ml/utils/experiment_tracking_mlflow.py†L1-L155】 | No CLI wiring ensures guard invoked; no tests verifying local URI override; MLflow optional dependency not pinned. | Remote endpoints accidentally hit; tracking disabled silently. | (a) Call `ensure_local_tracking()` from training CLI startup. (b) Add unit test to assert fallback when `MLFLOW_TRACKING_URI` remote without opt-in. | Remove hook if interfering with custom setups; leave doc note to opt back. |
|14| Extensibility (plugins/registries) | Partially Implemented | Registry loads entry points, offers runtime registration and discovery helpers.【F:src/codex_ml/plugins/registry.py†L1-L155】 | No tests covering duplicate handling/errors; plugin CLI help missing; entry points may fail silently. | Plugin load failures undetected; extension ecosystem brittle. | (a) Add regression tests for `Registry.load_from_entry_points` with fake entry points. (b) Emit warning summary in CLI listing. | Remove tests if they require pkg_resources mocking beyond scope. |

## 4. High-Signal Findings
1. **Lint gate red:** `nox -s lint` emits 78 Ruff violations (invalid `# noqa`, unused imports, multi-statement lines) blocking automated checks.【835782†L1-L110】
2. **Pytest smoke broken:** Minimal suite fails due to missing `click`, revealing packaging/test harness gaps.【90b94e†L1-L25】
3. **Coverage floor unmet:** Focused run achieved only 5.40% line coverage vs 80% requirement; coverage command exits non-zero.【15609e†L1-L124】【961dff†L1-L1】
4. **CLI entrypoints unusable:** `codex-*` scripts exit `ModuleNotFoundError` because installed package lacks runtime deps or exports (`codex` namespace not packaged).【80d304†L1-L10】
5. **Tokenization tests crash with stubs:** When `transformers` stub present, `find_spec` returns object with null spec causing ValueError.【085809†L1-L48】
6. **Notebook drift:** `notebooks/gpu_training_example.ipynb` fails nbformat parsing, signalling corrupted asset.【1e822a†L1-L9】
7. **Docstring coverage low:** Only 30% of callable surfaces documented, increasing support burden.【F:artifacts/metrics/docstring_coverage.json†L1-L6】
8. **Stub debt pervasive:** 391 Python files still rely on TODO/pass placeholders, many inside core ML subsystems.【33b595†L1-L6】
9. **Security scan incomplete:** `safety` requires account login; no offline baseline captured, leaving dependency CVEs unchecked.【98de62†L1-L3】【24a736†L1-L1】
10. **MLflow guard in place but untested:** Offline guard ensures local `file:` URI yet no CLI integration or tests confirm usage.【F:src/codex_ml/utils/experiment_tracking_mlflow.py†L20-L88】
11. **System metrics degrade silently:** psutil/NVML imports optional without status telemetry, risking observability blind spots.【F:src/codex_ml/monitoring/system_metrics.py†L32-L135】
12. **Hydra configs rich but unvalidated:** Base config enumerates deterministic settings yet lacks automated validation/override tests.【F:configs/base.yaml†L1-L25】
13. **Repro utilities exist but seldom invoked:** `set_seed` wraps deterministic modes, yet no gating ensures CLI uses it by default.【F:src/codex_ml/utils/repro.py†L1-L61】
14. **Import graph cycle:** Internal analysis shows `training` module imports itself indirectly, hinting at architectural sprawl.【F:artifacts/metrics/import_graph.json†L1-L12】

## 5. Atomic Diffs (Proposed)
### Diff A — Install CLI extras in nox test sessions
**Why:** Ensure smoke suites install required CLI deps (`click`, `typer`) to avoid `ModuleNotFoundError` and make coverage reproducible.【90b94e†L1-L25】  
**Risk:** Slightly longer environment setup; risk of network fetch (mitigated by caching).  
**Rollback:** Remove the added `_install(..., "-e", ".[cli]")` lines from `noxfile.py`.  
**Tests/Docs:** `nox -s tests_min`, `nox -s coverage`.
```diff
@@ def tests_min(session):
-    _ensure_pip_cache(session)
-    _install(session, "pytest", "pytest-randomly")
+    _ensure_pip_cache(session)
+    _install(session, "pytest", "pytest-randomly", "-e", ".[cli]")
@@ def coverage(session):
-    _install(session, "pytest", "pytest-cov", "pytest-randomly")
+    _install(session, "pytest", "pytest-cov", "pytest-randomly", "-e", ".[cli]")
```

### Diff B — Populate `cli` extra with runtime deps
**Why:** Editable installs omit `click`/`typer`; filling the extras ensures `pip install .[cli]` delivers required binaries.【80d304†L1-L10】【5b9a55†L1-L21】  
**Risk:** Version pin drift; ensure semver constraints align with supported APIs.  
**Rollback:** Revert additions under `[project.optional-dependencies].cli`.  
**Tests/Docs:** `pip install .[cli]`, `codex-ml-cli --help` smoke test.
```diff
 [project.optional-dependencies]
-cli = []
+cli = [
+  "click>=8.1",
+  "typer>=0.19"
+]
```

### Diff C — Harden tokenization test stub detection
**Why:** Prevent `transformers.__spec__ is None` errors when stub module lacks metadata; skip gracefully when stub active.【085809†L1-L48】  
**Risk:** Could hide legitimate import regressions; keep informative warning.  
**Rollback:** Remove new guard/skip logic.  
**Tests/Docs:** `pytest tests/tokenization -k sentencepiece` with stub + real deps.
```diff
@@
-if _TRANSFORMERS_STUB or importlib.util.find_spec("transformers") is None:
-    sys.modules.setdefault(
-        "transformers",
-        types.SimpleNamespace(__version__="0.0", IS_CODEX_STUB=True),
-    )
+spec = importlib.util.find_spec("transformers")
+if _TRANSFORMERS_STUB or spec is None:
+    stub = types.SimpleNamespace(__version__="0.0", IS_CODEX_STUB=True)
+    if spec is None:
+        spec = importlib.machinery.ModuleSpec("transformers", loader=None)  # type: ignore[attr-defined]
+    stub.__spec__ = spec  # type: ignore[attr-defined]
+    sys.modules.setdefault("transformers", stub)
```

### Diff D — Invoke MLflow guard from training CLI
**Why:** Guarantee offline default kicks in even when MLflow installed; documents local artifact path.【F:src/codex_ml/utils/experiment_tracking_mlflow.py†L39-L88】  
**Risk:** Users needing remote tracking must opt-in via env; highlight in docs.  
**Rollback:** Remove `ensure_local_tracking()` call.  
**Tests/Docs:** unit test mocking `MLFLOW_TRACKING_URI`. 
```diff
@@ def main(cfg: AppConfig) -> Mapping[str, Any]:
-    resolved = _to_mapping(cfg)
-    return run_functional_training(resolved)
+    from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking
+
+    ensure_local_tracking()
+    resolved = _to_mapping(cfg)
+    return run_functional_training(resolved)
```

### Diff E — Restore GPU notebook JSON integrity
**Why:** `gpu_training_example.ipynb` is invalid JSON; rewriting via `nbformat` ensures usability.【1e822a†L1-L9】  
**Risk:** Minimal; ensure outputs cleared to keep diff small.  
**Rollback:** Revert notebook to prior placeholder.  
**Tests/Docs:** `nbformat.validate('notebooks/gpu_training_example.ipynb')`.

## 6. Local Tests & Gates
| Command | Result | ML Test Score Facet |
|---|---|---|
| `nox -s lint` | ❌ Ruff violations (unused imports, multi-statements).【835782†L1-L110】 | Regression / Infra |
| `nox -s typecheck` | ✅ Mypy passes on 213 files.【ffbbf8†L1-L3】 | Infra |
| `nox -s tests_min` | ❌ Fails: missing `click` then transformers stub crash.【90b94e†L1-L25】【085809†L1-L48】 | Regression |
| `nox -s tests -- --cov --cov-report=xml --cov-report=html` | ❌ Coverage session aborts (missing `click`).【4834d7†L1-L27】 | Regression |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/analysis -q` | ✅ Analysis unit tests green.【64f13f†L1-L1】 | Regression |
| `pytest tests/analysis -q --cov=src ...` | ❌ Coverage 5.40% < 80%.【15609e†L1-L124】【961dff†L1-L1】 | Regression |

Artifacts captured under `artifacts/gates/` for reproducibility (see log files named above).【F:artifacts/gates/pytest-analysis.log†L1-L20】

## 7. Reproducibility Checklist
- **Seeds & Determinism:** `codex_ml/utils/repro.py` seeds Python/NumPy/Torch and toggles deterministic algorithms; CUBLAS workspace config set when CUDA present.【F:src/codex_ml/utils/repro.py†L1-L61】【F:src/codex_ml/utils/determinism.py†L1-L127】
- **Checkpoint RNG State:** Checkpoint utilities serialize RNG for python/numpy/torch/cuda, plus SHA256 for payload integrity.【F:src/codex_ml/utils/checkpoint.py†L1-L119】
- **Configuring determinism:** Base config enforces deterministic execution; training loop records dataset checksums when available.【F:configs/base.yaml†L1-L17】【F:src/codex_ml/train_loop.py†L30-L47】
- **Environment capture:** Python, pip freeze, OS, hardware recorded under `artifacts/env/` for this audit.【F:artifacts/env/python.txt†L1-L1】【F:artifacts/env/pip-freeze.txt†L1-L40】【F:artifacts/env/os.txt†L1-L1】【F:artifacts/env/hw.txt†L1-L8】
- **Experiment tracking:** MLflow guard defaults to local `file:./artifacts/mlruns` to avoid network writes unless opt-in env set.【F:src/codex_ml/utils/experiment_tracking_mlflow.py†L20-L88】
- **Data manifests:** Loader writes `CacheManifest` with checksums/splits for deterministic sharding.【F:src/codex_ml/data/loader.py†L45-L104】

## 8. Deferred Items
- Full torch/transformers installation skipped to respect offline constraints; numerous tests remain skipped (documented in logs).【085809†L1-L48】
- Safety CLI login not attempted; placeholder recorded for future credentialed run.【24a736†L1-L1】
- Comprehensive lint fixes out-of-scope; flagged issues queued for follow-up (see Diff A).【835782†L1-L110】

## 9. Error Capture Blocks
See `.codex/status/errors.ndjson` for structured records of encountered issues spanning GitHub Events filtering, dependency gaps, lint/test failures, coverage shortfall, and Safety auth prompts.【F:.codex/status/errors.ndjson†L1-L7】

## 10. Diff-Addendum S0→S1
No `S0` baseline provided; diff/log artifacts record this for completeness.【F:.codex/status/diff-S0_to_S1.txt†L1-L1】【F:.codex/status/log-S0_to_S1.txt†L1-L1】

## 11. References (Best Practices)
1. Hydra defaults list — https://hydra.cc/docs/advanced/defaults_list/  
2. PyTorch deterministic algorithms — https://pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html  
3. PyTorch randomness notes — https://pytorch.org/docs/stable/notes/randomness.html  
4. MLflow tracking URIs — https://mlflow.org/docs/latest/tracking.html  
5. MLflow Python API (`set_tracking_uri`) — https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.set_tracking_uri  
6. SentencePiece project — https://github.com/google/sentencepiece  
7. psutil documentation — https://psutil.readthedocs.io/  
8. NVIDIA NVML API — https://docs.nvidia.com/deploy/nvml-api/  
9. nox automation — https://nox.thea.codes/  
10. pytest-cov — https://pytest-cov.readthedocs.io/  
11. pydocstyle — http://www.pydocstyle.org/
