# 📍_codex_: Status Update (2025-09-05)

## 1. Repo Map
- Key directories: `src/`, `configs/`, `training/`, `tools/`, `tests/`, `docs/`, `scripts/`, `deploy/`.
- Key files: `pyproject.toml`, `Dockerfile`, `noxfile.py`, `README.md`, `.pre-commit-config.yaml`, `codex.mk`.
- Stubs & placeholders observed via repository scan:
  - `src/codex_ml/pipeline.py` raises `NotImplementedError` for the real training pipeline.
  - Interfaces under `src/codex_ml/interfaces/` define abstract methods with `NotImplementedError`.
  - `codex_digest/tokenizer.py` is a stub (`NotImplementedError`).
  - `configs/interfaces.example.yaml` contains TODO placeholders for tokenizer wiring.
  - Various tests (`tests/test_offline_repo_auditor.py`, interface tests) include TODO comments and unimplemented assertions.
  - Scaffolding utilities under `tools/` (for example, `apply_interfaces.py`) contain multiple `NotImplementedError` placeholders.
- Recent additions:
  - `tests/test_model_loader.py` adds comprehensive coverage for the `load_model_with_optional_lora` helper, including LoRA and fallback scenarios.
  - Restored training module and Makefile wrapper to support new merges.

## 2. Capability Audit Table
| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
|-----------|--------|-------------------|------|-------|--------------------|---------------|
| Tokenization | Partially Implemented | `src/codex_ml/tokenization/hf_tokenizer.py`, `sentencepiece_adapter.py` | No fast tokenizer wiring; SentencePiece dependency missing; limited padding/truncation tests | Runtime errors on missing packages; slow encoding | Add optional SentencePiece install guard, pad/truncate tests, and fast tokenizer configuration | Revert tokenization modules |
| ChatGPT Codex Modeling | Partially Implemented | `src/codex_ml/modeling/codex_model_loader.py`, `tests/test_model_loader.py` | Dtype/device validation still limited; large-model loading untested | Models may load on CPU or wrong precision; LoRA silently skipped | Extend loader with explicit dtype/device validation and integration tests for larger models | Revert loader to previous version |
| Training Engine | Partially Implemented | `training/engine_hf_trainer.py`, `src/codex_ml/train_loop.py` | Checkpoint resume and gradient accumulation coverage incomplete | Restarting from scratch; incorrect step counts | Implement optimizer/scheduler state restore and grad‑accum tests | Revert trainer module |
| Configuration Management | Implemented | `configs/` (Hydra YAMLs), `src/codex/cli.py` | No sweep/override docs; limited env capture | Misconfigured experiments | Document overrides and add sample sweep config | Remove docs if unstable |
| Evaluation & Metrics | Implemented | `src/codex_ml/metrics/`, `src/codex_ml/train_loop.py` NDJSON writer | Few metrics; no CSV/NDJSON example in docs | Metrics lost or inconsistent | Provide logging examples and unit tests for writers | Revert metric utilities |
| Logging & Monitoring | Partially Implemented | `src/codex_ml/monitoring/codex_logging.py`, `tracking/mlflow_utils.py` | W&B absent; psutil/NVML optional; limited tests | Silent failures or missing logs | Guard MLflow/W&B init, add system metrics sampling tests | Revert monitoring changes |
| Checkpointing & Resume | Partially Implemented | `src/codex_ml/utils/checkpointing.py` | Trainer integration for resume not wired; best‑k retention missing | Unable to restart or verify checkpoints | Wire checkpoint manager into trainer and add resume tests | Revert checkpoint utilities |
| Data Handling | Partially Implemented | `src/codex_ml/data/` loaders, cache, splits | Deterministic shuffling and caching strategies lack tests | Non‑reproducible data splits | Add deterministic split tests and cache directory hashing | Revert data utilities |
| Security & Safety | Partially Implemented | `src/codex_ml/safety/filters.py`, `semgrep_rules/` | No dependency locking in `requirements.lock` tests; secret scanning optional | Leakage of secrets or unsafe prompts | Integrate pre‑commit secret scan, verify requirements.lock in CI | Revert security hooks |
| Internal CI/Test | Partially Implemented | `noxfile.py`, `tests/` | Tests fail without optional deps (sentencepiece, httpx, mlflow); coverage gates unmet | CI instability | Mock optional deps, add requirements markers, enforce coverage | Revert test changes |
| Deployment | Partially Implemented | `Dockerfile`, `docker-compose.yml` | Missing CLI entrypoint and health checks | Containers start without services | Add ENTRYPOINT wiring to CLI and add healthcheck script | Revert container specs |
| Documentation & Examples | Partially Implemented | `README.md`, `docs/`, `examples/`, notebooks | No quickstart; notebooks marked TODO | Onboarding friction | Add quickstart guide and fill example notebook | Revert documentation changes |
| Experiment Tracking | Partially Implemented | `tracking/mlflow_utils.py`, `monitoring/` | No offline MLflow/W&B example; minimal metadata logging | Lost experiment history | Provide local MLflow example and log seed/env metadata | Revert tracking helpers |
| CLI & Interface Tooling | Partially Implemented | `src/codex/cli.py`, `tests/test_cli.py` | `click` dependency missing in coverage env; minimal command tests | CLI commands may break unseen | Add `click` to test deps and broaden CLI tests | Revert CLI if unstable |
| Extensibility | Implemented | `src/codex_ml/registry.py`, modular package layout | Plugin registry for custom components absent | Harder community extensions | Introduce entry-point based plugin registry with tests | Revert registry if unstable |

## 3. High-Signal Findings
 - Test suite coverage fails (`ModuleNotFoundError: No module named 'click'`) and other tests depend on optional packages (`sentencepiece`, `httpx`).
 - New `tests/test_model_loader.py` increases coverage for model loading and LoRA integration but adds to test runtime.
 - Restored training module and Makefile wrapper to support new merges.
 - Real training pipeline is stubbed; checkpoint resume hooks incomplete.
 - Tokenization relies on external packages without fallbacks; fast tokenizer not wired.
 - Coverage environment missing `click` causes CLI tests to abort.
 - MLflow and system metrics logging guarded but lack coverage; no W&B integration.
 - Data loaders lack deterministic shuffling and caching tests.
 - Docker image lacks CLI entrypoint and runtime health checks.
 - Security posture weak: secret scanning optional and requirements locking unverified.
 - Documentation missing quickstart and example notebook remains TODO.
 - Experiment tracking examples absent, risking irreproducible runs.
 - Registry pattern exists but lacks plugin mechanism for external extensions.
 - Code-generation tools in `tools/` remain scaffolds with `NotImplementedError` placeholders.

## 4. Atomic Diffs

### 4.1 Guard SentencePiece Import
```diff
--- a/src/codex_ml/tokenization/sentencepiece_adapter.py
+++ b/src/codex_ml/tokenization/sentencepiece_adapter.py
@@
- import sentencepiece as spm
+try:
+    import sentencepiece as spm
+except Exception:  # sentencepiece optional
+    spm = None
@@
-    model = spm.SentencePieceProcessor(model_file=str(model_file))
+    if spm is None:
+        raise ImportError("sentencepiece not installed")
+    model = spm.SentencePieceProcessor(model_file=str(model_file))
```
- *Why*: Avoid hard crash when sentencepiece is absent.
- *Risk*: Masking genuine install issues.
- *Rollback*: Revert `sentencepiece_adapter.py`.
- *Tests/docs*: Add unit test mocking absence of sentencepiece.

### 4.2 Local MLflow Default
```diff
--- a/src/codex_ml/tracking/mlflow_utils.py
+++ b/src/codex_ml/tracking/mlflow_utils.py
@@
-    tracking_uri: Optional[str] = "./mlruns",
+    tracking_uri: Optional[str] = os.getenv("CODEX_MLFLOW_URI", "file:mlruns"),
```
- *Why*: Use file-based store by default for offline reproducibility.
- *Risk*: Environment variable misconfiguration.
- *Rollback*: Revert change to `mlflow_utils.py`.
- *Tests/docs*: Document `CODEX_MLFLOW_URI`; add test ensuring fallback.

### 4.3 Wire Checkpoint Resume Flag
```diff
--- a/training/engine_hf_trainer.py
+++ b/training/engine_hf_trainer.py
@@
 parser.add_argument("--resume-from", type=str, default=None,
                     help="path to checkpoint")
@@
-    trainer = Trainer(model=model, args=training_args, train_dataset=train_ds, eval_dataset=eval_ds)
+    trainer = Trainer(model=model, args=training_args,
+                      train_dataset=train_ds, eval_dataset=eval_ds,
+                      resume_from_checkpoint=args.resume_from)
```
- *Why*: Enable resuming from checkpoints.
- *Risk*: Incompatible checkpoints causing load errors.
- *Rollback*: Remove `resume_from_checkpoint` argument.
- *Tests/docs*: Integration test starting from saved checkpoint.

### 4.4 Add Secrets Pre-commit Hook
```diff
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@
 -   repo: https://github.com/Yelp/detect-secrets
     rev: v1.4.0
     hooks:
-    - id: detect-secrets
+    - id: detect-secrets
+      args: ["--baseline", ".secrets.baseline"]
```
- *Why*: Enforce secrets scanning using existing baseline.
- *Risk*: False positives blocking commits.
- *Rollback*: Revert pre-commit config.
- *Tests/docs*: Update CONTRIBUTING with secret-scan instructions.

### 4.5 Docker CLI Entry
```diff
--- a/Dockerfile
+++ b/Dockerfile
@@
 CMD ["python", "-m", "codex.cli"]
```
- *Why*: Provide default CLI entrypoint for container deployments.
- *Risk*: Entrypoint may not cover all use cases.
- *Rollback*: Revert Dockerfile.
- *Tests/docs*: Build image and run `docker run <img> --help` test.

## 5. Local Tests & Gates
- `pre-commit run --files _codex_status_update-2025-09-05.md`
- `nox -s tests` *(coverage session: `ModuleNotFoundError: No module named 'click'`; see error blocks)*

## 6. Reproducibility Checklist
- [ ] **Seeds** – `codex_utils.set_seed` helper exists but is not consistently invoked across CLI entrypoints or tests.
- [ ] **Environment capture** – repository ships `requirements.txt` and a `requirements.lock`, yet no run pipeline automatically snapshots Python packages, OS, or hardware metadata.
- [x] **Code versioning** – project lives in git with changelog history, but run artifacts do not embed commit hashes or tags.
- [ ] **Deterministic data** – loaders in `src/codex_ml/data/` shuffle datasets without tests verifying reproducibility.
- [ ] **Hardware / software stack docs** – Dockerfile offers a base image, however GPU/CPU specs and kernel information are not captured for runs.

| Checklist Item | Existing Artifacts / Practices | Needed for Parity | Research Prompt |
|----------------|--------------------------------|-------------------|-----------------|
| Seeds | `codex_utils.set_seed`; ad‑hoc manual seeding in some notebooks | Enforce `set_seed` in all training/CLI scripts and add tests verifying deterministic outputs | How do mature ML frameworks guarantee global seeding across distributed jobs? |
| Environment capture | `requirements.txt`; `requirements.lock` | Automated `pip freeze` or `uv pip compile` snapshot, log `python --version`, `nvidia-smi`, and OS info | What tooling patterns capture full env state for reproducible ML runs? |
| Code versioning | Git repo with changelog entries | Embed commit hash/tag in model artifacts and logs; consider CI badge showing commit SHA | What are best practices for recording git metadata alongside experiment outputs? |
| Deterministic data | Data loaders and caches in `src/codex_ml/data/` | Deterministic shuffling tests; dataset hashing; dataloader seeding hooks | What strategies ensure dataloader determinism and dataset integrity checks? |
| Hardware / software stack docs | `Dockerfile` specifying base image | Document CPU/GPU specs; capture kernel, driver, and library versions in run reports | Which templates or schemas exist for documenting HW/SW stacks in reproducible research? |

### Research Questions for @codex
- Seeds: *Which approaches ensure reproducible seeding across multi‑process PyTorch/HF training pipelines?*
- Environment capture: *What tools or templates enable automatic snapshotting of Python packages, OS, and hardware for experiment runs?*
- Code versioning: *How can commit hashes or tags be embedded automatically into model checkpoints and logs?*
- Deterministic data: *What patterns verify deterministic shuffling and dataset hashing in data loaders?*
- Hardware/software stack docs: *Are there existing blueprints for capturing full system specifications (CPU, GPU, drivers, kernel) within ML experiment reports?*

### 6.1 Environment Specification Capture Methods
- **Python snapshot script**

  ```python
  """capture_env.py: write environment metadata to JSON"""
  import json, os, platform, subprocess, sys
  from importlib import metadata

  snapshot = {
      "python": sys.version,
      "platform": platform.platform(),
      "packages": {
          dist.metadata["Name"]: dist.version for dist in metadata.distributions()
      },
      "env_vars": dict(os.environ),
      "gpu": subprocess.run(
          [
              "nvidia-smi",
              "--query-gpu=name,driver_version,cuda_version,memory.total",
              "--format=csv,noheader",
          ],
          capture_output=True,
          text=True,
      ).stdout.strip(),
  }

  with open("artifacts/env_snapshot.json", "w") as fh:
      json.dump(snapshot, fh, indent=2)
  ```

- **Bash recipe**

  ```bash
  mkdir -p artifacts/env
  python --version > artifacts/env/python_version.txt
  pip freeze > artifacts/env/pip_freeze.txt
  uname -a > artifacts/env/uname.txt
  lscpu > artifacts/env/cpu.txt
  env | sort > artifacts/env/env_vars.txt
  nvidia-smi --query-gpu=name,driver_version,cuda_version,memory.total --format=csv > artifacts/env/gpu.csv
  ```

- **Other tools**: `conda env export --no-builds`, `pip list --format=json`, `pipdeptree --json-tree`, `uv pip list --frozen`.

- **Question for @codex**: *Which open-source templates or utilities best standardize full environment snapshots (packages, OS, hardware) for ML experiments?*

## 7. Deferred Items
- Full Hydra sweep integration: deferred due to configuration complexity.
- W&B monitoring hooks: postponed until dependency strategy confirmed.
- Plugin registry for external components: pending design discussion.

## 8. Error Capture Blocks
```
Question for ChatGPT @codex 2025-09-05:
While performing step "nox -s tests", encountered the following error:
ERROR tests/test_cli.py
E   ModuleNotFoundError: No module named 'click'
Context: Coverage environment lacks `click`; CLI tests abort.
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

```
Historical log excerpt (errors_codex.log):
ModuleNotFoundError: No module named 'codex_ml.cli'
Context: audit_repo metrics generation executed without repo installed.
Status: Unresolved — ensure `codex_ml` is on `PYTHONPATH` or installed.
```

```
Historical log excerpt (errors_codex.log):
command not found: pre-commit
Context: pre-commit hook invoked before installing `pre-commit`.
Status: Resolved — `pre-commit` installed and runs successfully.
```
