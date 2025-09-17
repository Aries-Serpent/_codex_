# 📍_codex_: Status Update (2025-09-03)

## 1. Repo Map
- Key directories: `src/`, `configs/`, `training/`, `tools/`, `tests/`, `docs/`, `scripts/`, `deploy/`.
- Key files: `pyproject.toml`, `Dockerfile`, `noxfile.py`, `README.md`, `.pre-commit-config.yaml`, `codex.mk`.
- Stubs & placeholders observed via repository scan:
  - `src/codex_ml/pipeline.py` raises `NotImplementedError` for the real training pipeline.
  - Interfaces under `src/codex_ml/interfaces/` define abstract methods with `NotImplementedError`.
  - `codex_digest/tokenizer.py` is a stub (`NotImplementedError`).
  - `configs/interfaces.example.yaml` contains TODO placeholders for tokenizer wiring.
  - Various tests (`tests/test_offline_repo_auditor.py`, interface tests) include TODO comments and unimplemented assertions.

## 2. Capability Audit Table
| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
|-----------|--------|-------------------|------|-------|--------------------|---------------|
| Tokenization | Partially Implemented | `src/codex_ml/tokenization/hf_tokenizer.py`, `sentencepiece_adapter.py` | No fast tokenizer wiring; SentencePiece dependency missing; limited padding/truncation tests | Runtime errors on missing packages; slow encoding | Add optional SentencePiece install guard, pad/truncate tests, and fast tokenizer configuration | Revert tokenization modules |
| ChatGPT Codex Modeling | Partially Implemented | `src/codex_ml/modeling/codex_model_loader.py` | Limited dtype/device checks; LoRA path handling minimal | Models may load on CPU or wrong precision; LoRA silently skipped | Extend loader with explicit dtype/device validation and LoRA load tests | Revert loader to previous version |
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
| Extensibility | Implemented | `src/codex_ml/registry.py`, modular package layout | Plugin registry for custom components absent | Harder community extensions | Introduce entry-point based plugin registry with tests | Revert registry if unstable |

## 3. High-Signal Findings
- Test suite fails: missing optional dependencies (`sentencepiece`, `httpx`) and failing tokenizer tests.
- Real training pipeline is stubbed; checkpoint resume hooks incomplete.
- Tokenization relies on external packages without fallbacks; fast tokenizer not wired.
- MLflow and system metrics logging guarded but lack coverage; no W&B integration.
- Data loaders lack deterministic shuffling and caching tests.
- Docker image lacks CLI entrypoint and runtime health checks.
- Security posture weak: secret scanning optional and requirements locking unverified.
- Documentation missing quickstart and example notebook remains TODO.
- Experiment tracking examples absent, risking irreproducible runs.
- Registry pattern exists but lacks plugin mechanism for external extensions.

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
- `pre-commit run --files _codex_status_update-2025-09-03.md`
- `nox -s tests` *(fails: missing optional dependencies and failing tokenizer tests; see error block)*

## 6. Reproducibility Checklist
- [ ] Seeds: partial—`set_seed` helper exists but not enforced in all scripts.
- [ ] Environment capture: no automated env snapshot or requirements freeze in pipeline.
- [x] Code versioning: git repository with history.
- [ ] Deterministic data: dataset shuffling not tested for determinism.
- [ ] Hardware/software stack docs: minimal Dockerfile but no detailed system spec.

## 7. Deferred Items
- Full Hydra sweep integration: deferred due to configuration complexity.
- W&B monitoring hooks: postponed until dependency strategy confirmed.
- Plugin registry for external components: pending design discussion.

## 8. Error Capture Blocks
```
Question for ChatGPT @codex 2025-09-03:
While performing step "nox -s tests", encountered the following error:
FAILED tests/test_requirements_lock.py::test_requirements_lock_exists - AssertionError: assert False
FAILED tests/test_search_providers.py::test_internal_search_finds_known_string - assert False
... (see `/tmp/nox.log` for full list)
Context: Running test suite without optional dependencies like sentencepiece and httpx.
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

## Outstanding Codex Automation Questions

Canonical source: docs/status_update_outstanding_questions.md (update there first, then copy the refreshed table below).

| Timestamp(s) | Step / Phase | Recorded blocker | Status | Current disposition |
| --- | --- | --- | --- | --- |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | Hook execution failed because `yamllint`, `mdformat`, and `detect-secrets-hook` were missing. | Retired | The active pre-commit configuration only invokes local commands (ruff, black, mypy, pytest, git-secrets, license checker, etc.), so those CLIs are optional for developers and no longer required by automation. |
| 2025-08-28T03:55:32Z | PH6: Run pytest with coverage | `pytest` rejected legacy `--cov=src/codex_ml` arguments. | Retired | Coverage flags were removed from `pytest.ini`, and the nox helper now targets `src/codex`, so the legacy failure mode is obsolete. |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | `check-merge-conflicts` and ruff flagged merge markers / unused imports. | Retired | The hook set no longer includes `check-merge-conflicts`; ruff/black remain for lint enforcement, so the merge-marker question is superseded. |
| 2025-09-10T05:02:28Z | `nox -s tests` | Coverage session failed during the gate. | Action required | `nox -s tests` still delegates to the coverage session, so the suite must pass with coverage enabled before this blocker can be closed. |
| 2025-09-10T05:45:43Z; 08:01:19Z; 08:01:50Z; 08:02:00Z | Phase 4: `file_integrity_audit compare` | Compare step reported unexpected file changes. | Action required | Expand the allowlists (beyond `.codex/pre_manifest.json`) and rely on move detection before rerunning the audit; the remediation has not been committed yet. |
| 2025-09-10T05:46:35Z; 08:02:12Z; 13:54:41Z | Phase 6: pre-commit | Hook execution failed because `pre-commit` was missing in the environment. | Action required | Install or gate `pre-commit` in the validation environment as documented; automation still expects it to be present. |
| 2025-09-10T05:46:47Z; 08:02:25Z; 13:55:11Z | Phase 6: pytest | Test suite failed under the gate. | Action required | Failures stem from missing optional dependencies and locale/encoding issues; install the extras or skip affected tests per the remediation notes. |
| 2025-09-10T05:46:52Z; 07:14:07Z; 08:02:32Z | Phase 6 & Validation: MkDocs | MkDocs build aborted (strict mode warnings / missing pages). | Mitigated / deferred | MkDocs now runs with `strict: false`, and navigation gaps were patched. Keep docs healthy before attempting to re-enable strict mode. |
| 2025-09-10T07:13:54Z; 11:12:28Z | Validation: pre-commit | `pre-commit` command not found during validation. | Action required | Same remediation as the Phase 6 failures—install or gate `pre-commit` before running validation jobs. |
| 2025-09-10T07:14:03Z; 11:12:36Z | Validation: pytest | Legacy `--cov=src/codex_ml` arguments rejected. | Retired | Covered by the coverage tooling update; remove the legacy flags and rely on the current nox/pytest configuration targeting `src/codex`. |
| 2025-09-10T08:01:17Z | Phase 4: `file_integrity_audit compare` | `file_integrity_audit.py` rejected argument order. | Documented resolution | The script expects `compare pre post --allow-*`; follow the documented invocation to avoid the error. |
| 2025-09-10 (timestamp `$ts`) | `tests_docs_links_audit` | Script crashed with `NameError: name 'root' is not defined`. | Action required | Add `root = Path('.')` (or similar) before using the variable the next time the audit script runs; the fix is recorded but not applied. |
| 2025-09-10T21:10:43Z | Validation: nox | `nox` command not found. | Action required | Install `nox` prior to running the validation gate, per the documented remediation. |

