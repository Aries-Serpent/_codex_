# 📍_codex_: Status Update (2025-09-02)

## 1. Repo Map
- Key directories: `src/`, `configs/`, `training/`, `tools/`, `tests/`, `docs/`, `scripts/`.
- Key files: `pyproject.toml`, `Dockerfile`, `noxfile.py`, `README.md`, `.pre-commit-config.yaml`.
- Stubs & placeholders observed via repository scan:
  - `training/engine_hf_trainer.py` contains TODO for loading optimizer state.
  - `src/codex/cli.py` defines command groups with `pass` implementations.
  - `codex_ml/utils/checkpointing.py` missing full checkpoint resume logic.
  - `codex_ml/tracking/mlflow_utils.py` provides no-op wrappers when MLflow missing.

## 2. Capability Audit Table
| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
|-----------|--------|-------------------|------|-------|--------------------|---------------|
| Tokenization | Partially Implemented | `src/codex_ml/tokenization/hf_tokenizer.py` | No fast tokenizer wiring or padding/truncation flags | Inefficient encoding and runtime failures on long sequences | Add padding/truncation arguments and tests | Revert module import to previous revision |
| ChatGPT Codex Modeling | Partially Implemented | `src/codex_ml/modeling/codex_model_loader.py` | Limited dtype/device handling; minimal PEFT hooks | Model may load on CPU or with wrong precision | Extend loader with dtype checks and LoRA flags | Revert file if loaders break |
| Training Engine | Partially Implemented | `training/engine_hf_trainer.py` | Resume checkpoints TODO, gradient accumulation tests missing | Training restarts from scratch | Implement optimizer/scheduler state restore and tests | Revert commit |
| Configuration Management | Implemented | `configs/` Hydra YAMLs | No sweep/override docs | Misconfigured runs | Add README examples, Hydra sweep example | Remove doc if unstable |
| Evaluation & Metrics | Implemented | `src/codex_ml/metrics/text.py`, NDJSON writer | No NDJSON/CSV logging example | Metrics lost | Wire metrics writer and tests | Revert metrics hooks |
| Logging & Monitoring | Partially Implemented | `src/codex_ml/monitoring/codex_logging.py` | No W&B offline test, psutil/NVML optional | Silent failures | Add guarded init and unit tests | Revert monitoring init |
| Checkpointing & Resume | Stubbed | `codex_ml/utils/checkpointing.py` | Missing optimizer/scheduler serialization | Inability to resume | Implement save/load helpers and tests | Revert utils module |
| Data Handling | Partially Implemented | `src/codex_ml/data/splits.py` | No deterministic shuffling tests or caching | Non-reproducible datasets | Add deterministic split test and cache module | Revert data changes |
| Security & Safety | Partially Implemented | `src/codex_ml/safety/filters.py` | No dependency scanning or secrets check | Exposure of secrets in logs | Integrate pre-commit secret hook, tests | Revert hook |
| Internal CI/Test | Partially Implemented | `noxfile.py`, `tests/` | Tests require optional deps (`httpx`, `mlflow`) | Test suite fails | Add optional deps to requirements-dev.txt, mark slow tests | Revert requirements update |
| Deployment | Partially Implemented | `Dockerfile`, `docker-compose.yml` | No CLI entry wiring in container | Deploy image lacks entrypoint | Add ENTRYPOINT and CLI, test build | Revert Dockerfile |
| Documentation & Examples | Partially Implemented | `README.md`, `docs/`, `examples/` | No quickstart or architecture diagram | Onboarding friction | Add quickstart doc, diagram | Revert doc |
| Experiment Tracking | Partially Implemented | `codex_ml/monitoring/mlflow_utils.py` | No offline MLflow example | Lack of traceability | Add example, guard init | Revert utilities |
| Extensibility | Implemented | `src/codex_ml/registry.py` | Registry limited to functions | Hard to register classes | Extend to class registry | Revert registry changes |

## 3. High-Signal Findings
- Test suite fails due to missing optional dependencies (`httpx`, MLflow).
- Checkpoint resume logic largely unimplemented.
- CLI entry points are stubs, reducing usability.
- Tokenization lacks padding/truncation controls.
- No secrets scanning or security audits.
- Monitoring utilities depend on optional packages without clear fallbacks.
- Documentation lacks quickstart and architecture overview.
- Deployment container lacks firm entrypoints.
- Data handling functions lack deterministic shuffling tests.
- Missing offline experiment tracking examples.

## 4. Atomic Diffs (examples)
1. **Add padding/truncation flags to HF tokenizer**
```diff
@@
-        return self.tokenizer.encode(text, add_special_tokens=False)
+        return self.tokenizer.encode(
+            text,
+            add_special_tokens=False,
+            padding="max_length" if pad_to_max else False,
+            truncation=True,
+        )
```
- *Why*: Enable consistent sequence lengths.
- *Risk*: Incorrect max length may truncate useful context.
- *Rollback*: Revert `hf_tokenizer.py`.
- *Tests/docs*: Add unit test for padding and README note.

2. **Load optimizer/scheduler state in trainer**
```diff
@@
-            # TODO: load model/optimizer state when supported
+            model.load_state_dict(torch.load(os.path.join(ckpt, "model.pt")))
+            optim.load_state_dict(torch.load(os.path.join(ckpt, "optim.pt")))
```
- *Why*: Enable resume from checkpoints.
- *Risk*: Shape mismatch if model changed.
- *Rollback*: Revert training file.
- *Tests/docs*: Integration test restoring from checkpoint.

3. **Guard MLflow init with offline default**
```diff
@@
-    if getattr(args, "mlflow_enable", False) and mlflow is not None:
-        try:
-            uri = getattr(args, "mlflow_tracking_uri", "") or "./mlruns"
-            mlflow.set_tracking_uri(uri)
-            exp = getattr(args, "mlflow_experiment", "codex")
-            mlflow.set_experiment(exp)
-            mlflow.start_run()
-            mlflow_active = True
-        except Exception:
-            mlflow_active = False
+    if getattr(args, "mlflow_enable", False) and mlflow is not None:
+        try:
+            uri = getattr(args, "mlflow_tracking_uri", "") or "file:mlruns"
+            mlflow.set_tracking_uri(uri)
+            mlflow.set_experiment(getattr(args, "mlflow_experiment", "codex"))
+            mlflow.start_run()
+            mlflow_active = True
+        except Exception:
+            mlflow_active = False
```
- *Why*: Default to local file-based tracking.
- *Risk*: MLflow version incompatibility.
- *Rollback*: Revert `codex_logging.py`.
- *Tests/docs*: Unit test mocking mlflow.

## 5. Local Tests & Gates
- `pre-commit run --files _codex_status_update-2025-09-02.md`
- `nox -s tests` *(fails: missing httpx and other optional deps)*
  - Errors: `RuntimeError: The starlette.testclient module requires the httpx package to be installed.`

## 6. Reproducibility Checklist
- [x] Seeds defined in configs (`experiment.seed`).
- [ ] Environment capture scripts.
- [x] Code versioning via git.
- [ ] Deterministic data shuffling tests.
- [ ] Documented hardware/software stack.

## 7. Deferred Items
- Full checkpoint resume: complex, requires cross-team coordination.
- Security scanning: pending decision on tooling (Semgrep vs. Bandit).
- Docker deployment entrypoint: awaiting infra requirements.

## 8. Error Capture Blocks
```
Question for ChatGPT @codex 2025-09-02:
While performing step "nox -s tests", encountered the following error:
RuntimeError: The starlette.testclient module requires the httpx package to be installed.
Context: Running test suite without optional dependency httpx.
What are the possible causes, and how can this be resolved while preserving intended functionality?
```
