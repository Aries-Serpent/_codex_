# _codex_: Status Update (2025-09-29) — Branch: main @ 142662e1dd0bcce7a16d34d0bfeaee5a467a3025

## 1. Audit Scope & Provenance
- Default branch `main` at commit `142662e1dd0bcce7a16d34d0bfeaee5a467a3025`; parents `7533a009b187b8ca4e8dcc1417bfe3c868e31a86` and `c5032f742800b934f6c4d30a2a44bfb7d873ed27`. Push event telemetry was unavailable, so the audit fell back to the default branch head.【F:.codex/status/provenance.json†L1-L19】【F:.codex/status/errors.ndjson†L8-L11】
- Audit executed from local branch `work` in a clean workspace; no base SHA (`S0`) supplied for compare artifacts.【F:.codex/status/provenance.json†L13-L18】

## 2. Repo Map
- Repository spans 52 tracked root files and 44 top-level directories; largest domains are `tests/` (444 files) and `src/` (223 files).【F:reports/repo_map.md†L1-L59】
- Domain LOC split: `src/` 35,524 LOC, `tests/` 23,972 LOC, `docs/` 7,780 LOC, `training/` 2,528 LOC, `notebooks/` 214 LOC. Test-to-code ratio ≈0.66 (23,776 test LOC vs. 36,297 code LOC).【F:artifacts/metrics/loc_by_dir.csv†L1-L6】【F:artifacts/metrics/test_code_ratio.json†L1-L5】
- Docstring coverage is 40.8 % (703/1,721 definitions); the stub scan surfaces 2,600+ TODO/placeholder hits, concentrated in legacy automation scripts and prior audit reports.【F:artifacts/metrics/docstring_coverage.json†L1-L5】【F:artifacts/metrics/stub_detection.json†L1-L40】
- Import graph contains a cycle between `codex_ml.data.loader` and `codex_ml.data_utils`, increasing coupling risk for the data stack.【F:artifacts/metrics/import_graph.json†L1-L8】【d28958†L1-L5】
- Notebook integrity checks confirm both notebooks load (10 and 26 cells respectively) with no validation errors.【F:artifacts/notebook_checks/quick_start.json†L1-L6】【F:artifacts/notebook_checks/gpu_training_example.json†L1-L6】

## 3. Capability Audit
| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Tokenization (SentencePiece, padding/truncation, CLI) | Partially Implemented | SentencePiece adapter with padding/truncation support; tokenizer trainer supporting streaming and Hydra configs; Typer CLI for inspection/export.【F:src/tokenization/sentencepiece_adapter.py†L15-L52】【F:src/tokenization/train_tokenizer.py†L51-L200】【F:src/tokenization/cli.py†L48-L118】 | Missing round-trip tests for padding/truncation; CLI depends on optional `tokenizers`/`sentencepiece` without graceful fallbacks; ingestion dependency undocumented. | Runtime failures in air-gapped envs when deps absent; regressions unnoticed due to absent tests. | Add pytest round-trip covering padding/truncation and CLI fallback stub; document ingestion dependency in README. | Revert new test module and doc updates if regressions appear. |
| 2. ChatGPT Codex Modeling & PEFT hooks | Partially Implemented | Registry-based loader with offline-first weight resolution, PEFT adapter integration, and MiniLM reference model.【F:src/codex_ml/models/registry.py†L1-L200】【F:src/codex_ml/models/minilm.py†L1-L84】 | No coverage for dtype/device routing; LoRA guard lacks telemetry when adapters skipped; minimal synthetic model only. | Offline deployments may silently downgrade precision/device; missing adapters harder to debug. | Add logging/asserts when PEFT disabled; introduce smoke test covering dtype/device args via CPU-only MiniLM. | Revert added logging/test files to restore prior behaviour. |
| 3. Training Engine (precision, grad accumulation) | Partially Implemented | `run_training` handles deterministic mode, gradient accumulation, telemetry hooks, MLflow logging, and checkpoint retention.【F:src/codex_ml/train_loop.py†L491-L620】【F:src/codex_ml/train_loop.py†L900-L980】 | Relies on optional torch; lacks tests for retention/MLflow branches; LoRA application not validated. | Silent no-ops when torch missing; retention bugs unnoticed; MLflow misconfiguration persists. | Add dependency-guarded unit tests (pytest marks) covering retention path using torch stub; gate MLflow via offline guard. | Remove new tests and guard call if they break CI. |
| 4. Config Management (Hydra/YAML) | Partially Implemented | Hydra root config with defaults stack; dataclass validations for training/tokenization configs.【F:configs/config.yaml†L1-L62】【F:src/codex_ml/config.py†L31-L120】 | Defaults list lacks documentation of overrides; no automated validation of composed configs; `hydra` optional. | Misconfigurations slip through; env-specific overrides harder to audit. | Add `codex-validate-config` smoke test in CI to compose defaults; document defaults tree referencing Hydra guidance.[Hydra defaults list](https://hydra.cc/docs/advanced/defaults_list/) | Revert validation hook if it blocks existing flows. |
| 5. Evaluation & Metrics | Partially Implemented | Metric registry with plugin loading, accuracy/perplexity/F1 helpers, offline resource resolver.【F:src/codex_ml/metrics/registry.py†L1-L120】 | No persisted metric manifest; evaluation pipelines under-documented; limited metric unit tests. | Metric drift unnoticed; offline assets missing detection. | Add NDJSON metric logging in evaluation CLI; create lightweight unit tests for registry & offline resolver. | Remove NDJSON logging/test if regressions observed. |
| 6. Logging & Monitoring | Partially Implemented | System metrics module toggles psutil/NVML via env flags; ML telemetry server integration; MLflow guard ensures file backend.【F:src/codex_ml/monitoring/system_metrics.py†L13-L120】【F:src/codex_ml/tracking/mlflow_guard.py†L1-L39】 | No psutil/NVML availability telemetry; MLflow guard not invoked from training CLI; TensorBoard path defaults undocumented. | Monitoring silently degraded; MLflow may hit remote URI unintentionally. | Call `ensure_file_backend()` when enabling MLflow; emit warning counters when psutil/nvml disabled. | Revert guard/warning changes if incompatible with existing configs. |
| 7. Checkpointing & Resume | Implemented | Checkpoint utility captures weights and RNG states (python/numpy/torch, CUDA) with serialization helpers.【F:src/codex_ml/utils/checkpoint.py†L1-L110】 | Resume path relies on torch presence; lacks corruption detection tests; RNG restore not covered. | Restores may mismatch RNG leading to nondeterminism; silent corruption. | Add offline unit test verifying RNG serialization round-trip using numpy stubs. | Drop test if deterministic regression arises. |
| 8. Data Handling (splits, caching) | Partially Implemented | Loaders handle JSONL/CSV normalization, checksum logging, deterministic splits with seed; integrates safety filters.【F:src/codex_ml/data/loaders.py†L1-L140】 | Cache/corpus ingestion relies on external `ingestion` module; no dataset manifest produced; missing large-file streaming tests. | Data drift undetected; ingestion errors invisible offline. | Produce dataset manifest JSON when training; add CLI option to verify checksum map. | Disable manifest emission if storage constraints appear. |
| 9. Security & Safety | Partially Implemented | Safety filters with policy parsing, environment overrides, and logging; Bandit + detect-secrets executed (offline).【F:src/codex_ml/safety/filters.py†L1-L70】【F:artifacts/security/bandit.txt†L1-L20】【F:artifacts/security/detect-secrets.txt†L1-L15】 | Safety CLI depends on online Safety DB; `safety` scan blocked offline; policy coverage lacks regression tests. | Vulnerabilities undetected offline; policy regressions slip through. | Vendor cached Safety database and add offline baseline tests; document fallback behaviour. | Revert offline baseline if it blocks pipeline. |
| 10. Internal CI/Test (pytest, nox) | Partially Implemented | Nox sessions for lint/typecheck/tests/coverage; pytest-cov run attempted with HTML/XML outputs.【F:noxfile.py†L495-L618】【F:artifacts/coverage/summary.txt†L1-L1】 | `nox -s lint` fails due to invalid `# noqa`; tests require optional deps (transformers, torch) and abort; coverage 6.7 %.【7c240a†L20-L120】【028416†L1-L120】【F:artifacts/coverage/summary.txt†L1-L1】 | Offline gating unreliable; coverage signal weak; lint debt accumulates. | Fix invalid `# noqa` directives and add dependency stubs for offline pytest run. | Revert lint/stub adjustments if they cause regressions. |
| 11. Deployment (packaging, Docker) | Partially Implemented | `pyproject` exposes CLI entry points; Dockerfiles present; packaging via `nox -s package`.【F:pyproject.toml†L61-L111】【F:noxfile.py†L612-L676】 | No automated smoke test for Docker images; packaging tests optional; missing lock sync guidance. | Broken images shipped; CLI drift. | Add `docker build --target test` smoke step offline; document packaging prerequisites. | Remove smoke test if local builders lack resources. |
| 12. Documentation & Examples | Partially Implemented | Extensive `docs/` tree, notebooks validated, README & prior audits exist.【F:reports/repo_map.md†L1-L59】【F:artifacts/notebook_checks/quick_start.json†L1-L6】 | Docs lack task-focused quickstart for Codex ML; no diagram for training data flow; stubbed TODOs remain. | User onboarding friction; stale docs degrade reliability. | Produce concise “offline training” tutorial referencing current CLI; triage TODOs from stub scan. | Revert doc additions if conflicting with doc tooling. |
| 13. Experiment Tracking (MLflow offline) | Partially Implemented | MLflow guard sets `file:` URIs; training loop logs params when `mlflow_enable` and MLflow installed.【F:src/codex_ml/tracking/mlflow_guard.py†L1-L39】【F:src/codex_ml/train_loop.py†L516-L579】 | Guard not called automatically; no NDJSON/CSV export fallback; minimal tests. | Users may write to remote tracking servers inadvertently; missing runs. | Call guard in CLI before enabling MLflow; add local experiment export to JSON for offline review. | Disable guard call if existing deployments rely on custom URIs. |
| 14. Extensibility (registries, plugins) | Partially Implemented | Registry pattern for models/metrics/tokenizers/trainers with entry points; plugin loader for metrics.【F:pyproject.toml†L61-L90】【F:src/codex_ml/metrics/registry.py†L1-L80】 | No health check for entry points; lack documentation of extension contracts; plugin errors swallowed. | Third-party plugins fail silently; integration friction. | Add CLI command to list plugin load errors and document registry contract. | Remove CLI if plugin ecosystem not ready. |

## 4. High-Signal Findings
1. Lint gate fails with 78 Ruff violations, primarily invalid `# noqa` annotations across the training loop and tooling scripts.【7c240a†L20-L120】
2. Offline pytest run aborts because the `transformers` stub lacks `__spec__`, stopping the suite before exercising coverage; dozens of tests are also skipped when torch/numpy/peft are absent.【028416†L1-L120】
3. Coverage artifacts report only 6.7 % line coverage and 1.2 % branch coverage, providing limited regression signal.【F:artifacts/coverage/summary.txt†L1-L1】
4. Security tooling executed locally: Bandit surfaces subprocess usage warnings; detect-secrets completes; Safety CLI cannot run offline and requires alternative workflow.【F:artifacts/security/bandit.txt†L1-L20】【F:artifacts/security/detect-secrets.txt†L1-L15】【F:artifacts/security/safety.txt†L1-L1】
5. Import graph analysis reveals a `codex_ml.data.loader` ↔ `codex_ml.data_utils` cycle, signaling tight coupling in the data module.【d28958†L1-L5】
6. Docstring coverage (40.8 %) and high volume of TODO/placeholder markers indicate documentation debt and potential incomplete implementations.【F:artifacts/metrics/docstring_coverage.json†L1-L5】【F:artifacts/metrics/stub_detection.json†L1-L40】
7. Tokenization trainer depends on an undocumented `ingestion` module and optional Hydra integration; missing documentation hampers reproducibility.【F:src/tokenization/train_tokenizer.py†L13-L139】
8. Training loop logs to MLflow only when `_HAS_MLFLOW` and manual enable flags are set; without calling `ensure_file_backend`, runs may default to remote tracking URIs contrary to offline guardrails.【F:src/codex_ml/train_loop.py†L516-L579】【F:src/codex_ml/tracking/mlflow_guard.py†L1-L39】
9. System metrics module gracefully downgrades when psutil/NVML absent but provides no explicit warning counters, making silent degradations easy to miss.【F:src/codex_ml/monitoring/system_metrics.py†L13-L92】
10. CLI entry points for training/tokenization/validation exist in `pyproject.toml`, yet no automated smoke tests cover them; manual regressions possible.【F:pyproject.toml†L61-L90】
11. Notebook validation confirms assets load, but no conversion or execution tests run, so runtime drift (e.g., API changes) may go unnoticed.【F:artifacts/notebook_checks/quick_start.json†L1-L6】
12. Guardrail scan shows no active `.github/workflows` files modified, aligning with offline mandate.【F:artifacts/guardrails/no-gh-actions-scan.txt†L1-L10】

## 5. Atomic Diffs
### Diff A — Harden transformers stub for offline pytest
```diff
--- a/tests/tokenization/conftest.py
+++ b/tests/tokenization/conftest.py
@@
-    sys.modules.setdefault(
-        "transformers",
-        types.SimpleNamespace(__version__="0.0", IS_CODEX_STUB=True),
-    )
+    if "transformers" not in sys.modules:
+        stub = types.SimpleNamespace(__version__="0.0", IS_CODEX_STUB=True)
+        try:
+            from importlib.machinery import ModuleSpec
+
+            stub.__spec__ = ModuleSpec("transformers", loader=None)  # type: ignore[attr-defined]
+        except Exception:  # pragma: no cover - best-effort stub enrichment
+            pass
+        sys.modules["transformers"] = stub
```
- **Why:** Ensure pytest can import the stub without `ValueError` when `transformers.__spec__` is inspected, restoring offline test execution.【028416†L1-L120】【F:tests/tokenization/conftest.py†L13-L31】
- **Risk:** Low; change touches stub path only. Unexpected attribute writes ignored.
- **Rollback:** Revert the block if upstream provides a proper stub.
- **Tests/Docs:** Run `nox -s tests_sys` offline; document stub behaviour in developer guide.

### Diff B — Enforce MLflow file backend when enabling tracking
```diff
--- a/src/codex_ml/train_loop.py
+++ b/src/codex_ml/train_loop.py
@@
-from codex_ml.utils.retention import prune_checkpoints
+from codex_ml.utils.retention import prune_checkpoints
+from codex_ml.tracking.mlflow_guard import ensure_file_backend
@@
-    if mlflow_enable and _HAS_MLFLOW:
+    if mlflow_enable and _HAS_MLFLOW:
+        mlflow_uri = mlflow_uri or ensure_file_backend()
         mlflow.set_tracking_uri(mlflow_uri)
```
- **Why:** Guarantee offline MLflow writes to a local `file:` backend without manual configuration, aligning with guardrails.【F:src/codex_ml/train_loop.py†L516-L579】【F:src/codex_ml/tracking/mlflow_guard.py†L1-L39】[MLflow tracking docs](https://mlflow.org/docs/latest/tracking.html)
- **Risk:** Medium; environments relying on pre-set URIs must ensure compatibility. The guard respects pre-populated `MLFLOW_TRACKING_URI` unless `force=True` is used.
- **Rollback:** Remove the import and guard call to restore prior behaviour.
- **Tests/Docs:** Add unit test asserting `ensure_file_backend` invoked when `mlflow_enable=True`; update documentation explaining offline default.

### Diff C — Replace invalid Ruff suppressions with explicit error codes
```diff
--- a/src/codex_ml/train_loop.py
+++ b/src/codex_ml/train_loop.py
@@
-except Exception:  # noqa: broad-except
+except Exception:  # noqa: BLE001
@@
-    except Exception as e:  # noqa: broad-except
+    except Exception as e:  # noqa: BLE001
```
- **Why:** Fix invalid `# noqa` usage causing Ruff failures, recovering lint gating.【7c240a†L20-L120】【F:src/codex_ml/train_loop.py†L60-L137】
- **Risk:** Low; only comments change.
- **Rollback:** Revert comment edits if lint configuration changes.
- **Tests/Docs:** Re-run `nox -s lint` to confirm clean outcome; note lint requirement in CONTRIBUTING.[nox automation](https://nox.thea.codes/)

## 6. Codex-ready Task Sequence
1. **Stabilize offline tokenizer tests** — Apply Diff A and add pytest coverage for padding/padding round-trips (Phase 3 & 5 alignment).
2. **Lock MLflow to file backend** — Apply Diff B, extend training CLI docs, add smoke test covering offline tracking setup (Phases 3, 4, 6, 7).
3. **Restore lint gate** — Apply Diff C broadly across files flagged in Ruff output, ensure `nox -s lint` passes locally (Phases 5 & 6).
4. **Document Hydra defaults & ingestion dependency** — Update README/config docs referencing Hydra defaults guidance.[Hydra defaults list](https://hydra.cc/docs/advanced/defaults_list/)
5. **Add offline dependency stubs for torch/numpy** — Extend pytest conftest to avoid cascading skips; map tests to ML test score facets (data integrity & infra).

## 7. Local Tests & Gates
| Command | Result | Notes |
| --- | --- | --- |
| `nox -s lint` | ❌ (fails) | Ruff reports 78 violations due to invalid `# noqa` comments and unused imports.【7c240a†L20-L120】 |
| `nox -s typecheck` | ✅ | Mypy succeeds on 214 source files.【d2bb61†L1-L3】 |
| `nox -s tests_sys` | ❌ (fails) | Abort: `transformers.__spec__ is None`; numerous skips when torch/numpy/peft absent; coverage artifacts still generated (6.7 % lines).【028416†L1-L120】【F:artifacts/coverage/summary.txt†L1-L1】 |
- **ML Test Score Mapping:**
  - *Data integrity*: checksum logging and ingestion splits exercised via coverage run (partial due to skips).【F:src/codex_ml/data/loaders.py†L1-L140】
  - *Model/inference*: MiniLM synthetic training path executed until failure; LoRA path untested.【F:src/codex_ml/train_loop.py†L491-L620】
  - *Infra/monitoring*: MLflow guard not automatically invoked; system metrics not validated.
  - *Regression*: Low due to 6.7 % coverage.

## 8. Reproducibility Checklist
- **Seeds & Determinism:** `run_training` accepts `seed`, toggles CUDNN determinism, and checkpoints RNG (python/numpy/torch) for resume.【F:src/codex_ml/train_loop.py†L491-L620】【F:src/codex_ml/utils/checkpoint.py†L1-L110】[PyTorch determinism guidance](https://pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html)
- **Environment Capture:** Captured `python --version`, `pip freeze`, `uname`, `lscpu` snapshots.【F:artifacts/env/python.txt†L1-L1】【F:artifacts/env/pip-freeze.txt†L1-L20】【F:artifacts/env/os.txt†L1-L1】【F:artifacts/env/hw.txt†L1-L20】
- **Code Versioning:** Branch/SHA recorded in `provenance.json`; working tree clean after audit commands.【F:.codex/status/provenance.json†L1-L19】
- **Data Manifest:** Loaders compute file checksums and track skipped records; no manifest persisted by default.【F:src/codex_ml/data/loaders.py†L35-L90】
- **Checkpoints:** SHA-256 recorded per epoch, latest metadata persisted, retention pruning supported.【F:src/codex_ml/train_loop.py†L900-L933】
- **Experiment Tracking:** MLflow guard provides file backend but needs integration into training entry point; consider documenting usage of `MLFLOW_TRACKING_URI=file:` per MLflow guidance.【F:src/codex_ml/tracking/mlflow_guard.py†L1-L39】[MLflow tracking docs](https://mlflow.org/docs/latest/tracking.html)

## 9. Deferred Items
- Safety CLI offline replacement deferred; offline Safety DB/licensing unresolved.【F:artifacts/security/safety.txt†L1-L1】【F:.codex/status/errors.ndjson†L7-L9】
- Docker/packaging smoke tests not executed to honour “no network” guardrail; recommend future local dry-run when resources permit.【F:noxfile.py†L612-L676】
- No attempt to resolve legacy errors recorded in `.codex/status/errors.ndjson` predating this audit to avoid conflating historical automation issues.【F:.codex/status/errors.ndjson†L1-L7】

## 10. Error Capture Blocks
All encountered issues have been logged in `.codex/status/errors.ndjson` (GitHub Events API PushEvent absence, Safety CLI hang, lint/test failures).【F:.codex/status/errors.ndjson†L1-L11】 Refer to that log for root-cause triage discussion prompts.

## 11. Diff-Addendum S0→S1
Base SHA `S0` not provided; compare artifacts intentionally omitted.

## 12. References
- Hydra defaults list — <https://hydra.cc/docs/advanced/defaults_list/>
- PyTorch determinism guidance — <https://pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html>
- MLflow offline tracking — <https://mlflow.org/docs/latest/tracking.html>
- SentencePiece project — <https://github.com/google/sentencepiece>
- psutil documentation — <https://psutil.readthedocs.io/>
- NVIDIA NVML API — <https://docs.nvidia.com/deploy/nvml-api/>
- nox automation — <https://nox.thea.codes/>
- pytest-cov usage — <https://pytest-cov.readthedocs.io/>
- pydocstyle — <http://www.pydocstyle.org/>
