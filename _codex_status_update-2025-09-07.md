# _codex_: Status Update (2025-09-07)

## 1. Repo Map
- Top-level directories: `src/`, `training/`, `configs/`, `docs/`, `tests/`, `tools/`, `scripts/`, `examples/`, `notebooks/`, `deploy/`, `monitoring/`, `requirements/`.
- Key files: `Makefile`, `pyproject.toml`, `Dockerfile`, `docker-compose.yml`, `.pre-commit-config.yaml`, `noxfile.py`.
- Notable stubs and placeholders:
  - `src/codex_ml/pipeline.py` raises `NotImplementedError` for real training pipeline.
  - Interface classes in `src/codex_ml/interfaces/` include `NotImplementedError` methods.
  - `codex_digest/tokenizer.py` is a stub.
  - `configs/interfaces.example.yaml` contains TODO placeholders for tokenizer wiring.
  - Several tools and tests (e.g., `tools/apply_interfaces.py`, `tests/test_interfaces_compat.py`) include TODO comments.

## 2. Capability Audit Table
| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
|---|---|---|---|---|---|---|
| Tokenization | Implemented | `src/codex_ml/tokenization/hf_tokenizer.py`, `sentencepiece_adapter.py`, CLI utilities | Lacks explicit vocab versioning and padding/truncation tests | Inconsistent tokenization could break training | Add vocab version in configs; unit tests for padding/truncation | Revert tokenizer config changes |
| ChatGPT Codex Modeling | Partially Implemented | `src/codex_ml/modeling/codex_model_loader.py` with optional LoRA | No dtype/device configuration defaults; limited PEFT error handling | Model may fail on unsupported dtypes/devices | Introduce dtype/device config loader; expand error handling | Revert model loader update |
| Training Engine | Partially Implemented | `training/engine_hf_trainer.py`, checkpoint manager | Resume from checkpoint TODO, gradient accumulation tests absent | Training restarts from scratch; silent grad errors | Implement optimizer/scheduler state restore; tests | Revert trainer changes |
| Configuration Management | Partially Implemented | Hydra configs under `configs/` | Override propagation tests failing; no sweep examples | Misconfigured runs | Fix override handling; add sweep examples | Revert config changes |
| Evaluation & Metrics | Implemented | `src/codex_ml/eval/`, `metrics/` | No NDJSON/CSV logging examples | Metrics lost after runs | Add logging adapters and example scripts | Revert evaluator changes |
| Logging & Monitoring | Partially Implemented | `src/codex_ml/monitoring/` (async writer, mlflow utils) | System metrics via psutil/NVML missing | Blind to resource usage | Add psutil-based metrics collector | Revert monitoring add |
| Checkpointing & Resume | Implemented | `src/codex_ml/utils/checkpointing.py`, `training/checkpoint_manager.py` | Lacks best-k retention tests | Corrupt or missing checkpoints | Add retention tests and CLI hooks | Revert checkpoint commit |
| Data Handling | Partially Implemented | `training/datasets.py`, `data_utils.py` | Deterministic shuffling and caching not enforced | Non-reproducible data splits | Add seed handling and caching layer | Revert data utils change |
| Security & Safety | Stubbed | `.secrets.baseline`, `bandit.yaml`, `safety/` | Dependency locking incomplete; prompt safety docs lacking | Supply-chain or prompt injections | Lock dependencies; expand safety docs | Revert lockfile |
| Internal CI/Test | Partially Implemented | `noxfile.py`, `tests/`, pre-commit hooks | Coverage session failing (`test_override_propagation`), minimal regression tests | Undetected regressions | Fix failing tests; add regression suite | Revert test changes |
| Deployment | Partially Implemented | `Dockerfile`, `docker-compose.yml`, `setup.sh` | No CLI entry points packaged; Docker lacks GPU flags | Difficult deployment | Add entry points in `pyproject.toml`; GPU docker compose | Revert deployment changes |
| Documentation & Examples | Partially Implemented | `README.md`, `docs/`, `examples/`, `notebooks/` | Quickstart and notebooks contain TODOs | User confusion | Update README, fill notebooks | Revert docs commit |
| Experiment Tracking | Stubbed | `monitoring/mlflow_utils.py` | No MLflow offline mode examples | Tracking fails offline | Add offline MLflow init with env guard | Revert tracking code |
| Extensibility | Partially Implemented | `src/codex_ml/registry.py`, interface classes | No plug-in registry pattern; tools contain stubs | Hard to extend | Implement simple registry & remove stubs | Revert registry module |

## 3. High-Signal Findings
- Real training pipeline not implemented; interfaces mostly stubs.
- Tokenizer and LoRA wiring present but lacks config integration and tests.
- Checkpoint utilities robust but retention policies untested.
- Hydra configuration overrides currently fail in tests.
- Logging subsystem missing system metrics collectors.
- Documentation and notebooks contain numerous TODOs; no quickstart guide.
- Security posture relies on baseline scans without dependency pinning.
- CI gate fails at coverage stage due to Hydra override parsing.
- Deployment artifacts lack GPU support and CLI entry points.
- Experiment tracking via MLflow not wired for offline mode.

## 4. Atomic Diffs
### Diff 1: Guarded MLflow Init
```diff
@@
-from codex_ml.monitoring import mlflow_utils
-mlflow_utils.init()
+from codex_ml.monitoring import mlflow_utils
+if mlflow_utils.HAS_MLFLOW:
+    mlflow_utils.init()
```
- **Why**: Avoid runtime failure when MLflow is absent.
- **Risk**: None; guarded by feature flag.
- **Rollback**: Revert file to previous state.
- **Tests/docs**: Add unit test ensuring init is skipped when missing.

### Diff 2: Hydra Override Fix
```diff
@@
-    parser.add_argument("--override-file", type=Path)
+    parser.add_argument("--override-file", type=Path, default=None)
```
- **Why**: Fix failing tests expecting optional override file.
- **Risk**: Mis-parsed CLI args.
- **Rollback**: Restore previous parser line.
- **Tests/docs**: Update `tests/config/test_override_propagation.py`.

### Diff 3: psutil Metrics Collector
```diff
@@
-from codex_ml.monitoring.codex_logging import _codex_log_all
+from codex_ml.monitoring.codex_logging import _codex_log_all
+import psutil
+
+def log_system_metrics():
+    cpu = psutil.cpu_percent(interval=0.1)
+    mem = psutil.virtual_memory().percent
+    _codex_log_all({"cpu": cpu, "mem": mem})
```
- **Why**: Basic system monitoring.
- **Risk**: psutil unavailable.
- **Rollback**: Remove function and import.
- **Tests/docs**: Mock psutil in tests; document optional dependency.

## 5. Local Tests & Gates
- `pre-commit run --files _codex_status_update-2025-09-07.md`
  - passed after dependency installation.
- `nox -s tests`
  - **failed** at coverage stage (`test_override_propagation`).
  - see captured log for traceback and failure cause.

**ML Test Score mapping:**
- Data: deterministic splits missing (gap).
- Model: LoRA integration tests absent (gap).
- Infrastructure: failing Hydra override test (regression).
- Regression: pre-commit and pytest cover basic gates (implemented).
- Performance: no benchmarking tests (missing).

## 6. Reproducibility Checklist
- [ ] Seeds set globally (`set_seed`, `set_reproducible`).
- [ ] Environment capture via `codex_utils.repro.log_env_info`.
- [ ] Version control: git hashes recorded.
- [ ] Deterministic data loading (missing).
- [ ] Config snapshots via Hydra (implemented).

## 7. Deferred Items
- Real training pipeline deferred due to complexity of orchestration and lack of ownership.
- Notebook examples postponed until core features stabilize.
- Experiment tracking backends beyond MLflow omitted pending decision on storage.

## 8. Error Capture Blocks
```
Question for ChatGPT @codex 2025-09-07:
While performing STEP_1: run chatgpt-codex audit command, encountered the following error:
'bash: command not found: chatgpt-codex'
Context: generating status update via `chatgpt-codex` tool.
What are the possible causes, and how can this be resolved while preserving intended functionality?
```
```
Question for ChatGPT @codex 2025-09-07:
While performing STEP_2: initial pre-commit run, encountered the following error:
'KeyboardInterrupt during environment installation'
Context: pre-commit hooks downloading environments.
What are the possible causes, and how can this be resolved while preserving intended functionality?
```
```
Question for ChatGPT @codex 2025-09-07:
While performing STEP_3: run nox -s tests, encountered the following error:
"subprocess.CalledProcessError: ... unrecognized arguments: --override-file ..."
Context: Hydra override propagation test failing.
What are the possible causes, and how can this be resolved while preserving intended functionality?
```
