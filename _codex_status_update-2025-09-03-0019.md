# _codex_: Status Update (2025-09-03)

## 1. Repo Map
- **Top-level directories**: `analysis`, `artifacts`, `configs`, `docs`, `notebooks`, `scripts`, `src`, `tests`, `training`, `tools`, `deploy`, `requirements`, etc.
- **Key files**: `README.md`, `pyproject.toml`, `noxfile.py`, `Dockerfile`, `Makefile`, `codex.mk`, `tox.ini`, `requirements.txt`, `requirements-dev.txt`.
- **Stubs & TODOs**:
  - `src/codex_ml/pipeline.py` raises `NotImplementedError` for real training pipeline.
  - Interfaces under `src/codex_ml/interfaces` contain multiple `NotImplementedError` placeholders.
  - Logging utilities (`src/codex/logging/*.py`) include numerous `pass` blocks.
  - Tests (`tests/test_offline_repo_auditor.py`, `tests/test_interfaces_compat.py`) contain TODO markers.

## 2. Capability Audit Table

| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization | Partially Implemented | `HFTokenizerAdapter` with fast padding/truncation (`src/codex_ml/tokenization/hf_tokenizer.py`) | Missing tokenization config wiring, limited tests | Incorrect tokenization causing downstream errors | Add config-driven tokenizer loader, unit tests for encode/decode/padding | Revert new loader and tests |
| ChatGPT Codex Modeling | Partially Implemented | `load_model_with_optional_lora` supporting dtype, device, LoRA (`src/codex_ml/modeling/codex_model_loader.py`) | No CLI hook, limited error handling, no PEFT tests | Runtime failures when PEFT missing; device mismatch | Add CLI wrapper with flags, mock-based tests for LoRA path | Revert loader changes and CLI wrapper |
| Training Engine | Stubbed | Toy loop in `src/codex_ml/train_loop.py` | Missing HF Trainer integration, gradient accumulation beyond toy, optimizer state resume | Training cannot scale; no resume | Integrate HF Trainer with config, implement checkpoint resume, add regression tests | Revert to toy loop |
| Configuration Management | Partially Implemented | Hydra-compatible configs in `configs/` | No sweep/override examples, inconsistent usage across CLI | Misconfigured runs; hard to reproduce | Document Hydra overrides, add `conf` entry points, tests covering config loading | Revert config docs |
| Evaluation & Metrics | Implemented | Metrics in `src/codex_ml/eval/metrics.py` with NDJSON logging | Lacks validation loops, no metrics CLI | Poor visibility into model quality | Add eval runner CLI, tests for metrics file outputs | Revert CLI and tests |
| Logging & Monitoring | Stubbed | Skeleton modules under `src/codex/logging` | No TensorBoard/W&B hooks, system metrics absent | Limited observability; debugging hard | Implement structured logger with psutil/NVML metrics; add logging tests | Revert logging module |
| Checkpointing & Resume | Missing | – | No checkpoint save/load utilities | Loss of training progress on failure | Add checkpoint module, integrate with training loop, tests verifying resume | Revert checkpoint module |
| Data Handling | Partially Implemented | `ingestion` utilities for IO and encoding detection | No dataset split utilities, non-deterministic shuffling | Data leakage, non-reproducible | Implement deterministic dataset splitter, caching options, tests | Revert dataset changes |
| Security & Safety | Stubbed | Basic `safety` package | No dependency locking enforcement, secrets scanning, prompt safety | Vulnerable to supply-chain and prompt attacks | Add safety scanners (pip-audit, secret detectors), stub prompt filters | Revert safety tools |
| Internal CI/Test | Partially Implemented | `noxfile.py`, basic tests | Sparse coverage, no tox/nox gates for lint/type | Bugs slip into production | Expand tests, add lint/type sessions, enforce coverage threshold | Revert CI config |
| Deployment | Partially Implemented | `Dockerfile`, `docker-compose.yml`, `entrypoint.sh` | Missing packaging setup and CLI entry points | Deployment failures | Add `setup.py`/entry points, test docker build | Revert packaging edits |
| Documentation & Examples | Partially Implemented | README, docs, notebooks, examples | Missing architecture diagram, incomplete tutorials | Onboarding friction | Add architecture docs and quickstart notebooks | Revert doc additions |
| Experiment Tracking | Partially Implemented | MLflow utilities (`src/codex_ml/tracking/mlflow_utils.py`) | No local tracking CLI or offline mode examples | Experiments not reproducible | Provide MLflow config examples, offline mode tests | Revert tracking examples |
| Extensibility | Partially Implemented | Simple registry (`src/codex_ml/registry.py`) | No plugin discovery, limited interfaces | Hard to extend components | Introduce entry-point based registry, tests | Revert registry changes |

## 3. High-Signal Findings
- Training pipeline is not implemented; critical path for model training.
- Logging modules are placeholders, lacking real monitoring or structured logging.
- Interfaces for tokenizers and RL components are abstract with no concrete implementations.
- Checkpointing functionality is absent, risking inability to resume training.
- Tests contain TODOs and insufficient coverage; no gating for linting or typing.
- Configuration management is inconsistent, making runs hard to reproduce.
- Security measures such as dependency locking and secret scanning are minimal.
- Lack of CI/test gating beyond basic `nox -s tests`; no performance or regression benchmarks.
- Experiment tracking exists but may fail silently if MLflow absent; no fallback logging.
- Data ingestion utilities rely on many `pass` statements, leaving edge cases unhandled.

## 4. Atomic Diffs
1. **Guarded MLflow initialization**
   ```diff
   --- a/src/codex_ml/tracking/mlflow_utils.py
   +++ b/src/codex_ml/tracking/mlflow_utils.py
   @@
   -    _ensure_mlflow_available()
   -    # Set system metrics env var only if explicitly provided
   -    if cfg.enable_system_metrics is not None:
   -        os.environ.setdefault(
   -            "MLFLOW_ENABLE_SYSTEM_METRICS", "1" if cfg.enable_system_metrics else "0"
   -        )
   +    try:
   +        _ensure_mlflow_available()
   +    except RuntimeError:
   +        return contextlib.nullcontext(None)
   +    if cfg.enable_system_metrics is not None:
   +        os.environ.setdefault(
   +            "MLFLOW_ENABLE_SYSTEM_METRICS", "1" if cfg.enable_system_metrics else "0"
   +        )
   ```
   - *Why*: Provides safe fallback when MLflow isn't installed.
   - *Risk*: MLflow-dependent features silently disabled.
   - *Rollback*: Revert changes in `mlflow_utils.py`.
   - *Tests/docs*: Add unit test verifying no-op when MLflow missing.

2. **Hydra defaults for tokenizer**
   ```diff
   --- a/configs/base.yaml
   +++ b/configs/base.yaml
   @@
   tokenizer:
   -  name: gpt2
   +  name: gpt2
   +  cache_dir: ./cache/tokenizers
   ```
   - *Why*: Establish deterministic tokenizer caching.
   - *Risk*: Cache path misconfigured on Windows.
   - *Rollback*: Remove added `cache_dir` key.
   - *Tests/docs*: Update README with cache usage.

3. **Add deterministic dataset split helper**
   ```diff
   --- a/src/codex_ml/data/__init__.py
   +++ b/src/codex_ml/data/__init__.py
   @@
   +def deterministic_split(dataset, seed: int = 42):
   +    rng = random.Random(seed)
   +    data = list(dataset)
   +    rng.shuffle(data)
   +    n = len(data)
   +    split = int(0.9 * n)
   +    return data[:split], data[split:]
   ```
   - *Why*: Ensures reproducible train/val splits.
   - *Risk*: Assumes dataset fits in memory.
   - *Rollback*: Revert added helper.
   - *Tests/docs*: Add unit test for deterministic behavior.

## 5. Local Tests & Gates
- **Commands**:
  - `pre-commit run --files _codex_status_update-2025-09-03.md`
  - `nox -s tests`
- **Example Outputs**:
  - Pre-commit: formatting checks (no output implies pass).
  - Nox tests: executes existing pytest suite; failures indicate missing dependencies.
- **ML Test Score Mapping**:
  - *Data*: deterministic split test (planned)
  - *Model*: tokenizer encode/decode tests
  - *Infrastructure*: MLflow no-op behavior test
  - *Regression*: training loop metric regression test
  - *Performance*: placeholder for future GPU profiling

## 6. Reproducibility Checklist
- [ ] Global seeds set (`set_reproducible` exists but not used consistently)
- [ ] Environment capture via `requirements.lock`
- [ ] Code versioning through Git commits
- [ ] Deterministic data splits (planned helper)
- [ ] Config hashes recorded in metrics (`train_loop.py`)

## 7. Deferred Items
- Full HF Trainer integration deferred due to complexity and lack of maintainer bandwidth.
- Advanced safety tooling (prompt filtering, red-teaming datasets) postponed pending policy decisions.

## 8. Error Capture Blocks
None encountered during audit.
