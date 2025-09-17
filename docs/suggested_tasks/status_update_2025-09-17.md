# *codex*: Status Update (2025-09-17)

## 1. Repo Map

| Category | Description |
| --- | --- |
| **Top‑level layout** | The repository root contains numerous directories, including configuration, source code and utilities. Key folders are `.codex` (metadata), `analysis` (analyses scripts), `codex_digest`, `codex_ml` (core ML components), `codex_utils`, `configs` (Hydra YAMLs), `deploy`, `docs`, `examples`, `experiments`, `interfaces`, `logs`, `monitoring`, `notebooks`, `patches`, `requirements`, `schemas`, `scripts`, `services`, `src`, and `tests`[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents#:~:text=%7D%20%7D%2C%20%7B%20,Serpent%2F_codex_%2Fblob%2Fmain%2Fpyproject.toml%22). There is a `pyproject.toml` defining the package, entry points and tool config[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=,backend%20%3D%20%22setuptools.build_meta). The repository is Python‑centric with optional extras (CLI, tracking, PEFT, GPU/CPU). |
| **Stubs and placeholders** | Several directories contain only a `.gitkeep` file or an empty `__init__.py`. For example, `src/tokenization` includes a `.gitkeep` and a minimal `__init__.py` that simply re‑exports helpers[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/src/tokenization#:~:text=,). Many optional features are guarded by try/except blocks; when unavailable they raise runtime errors (e.g., if PyTorch or Hydra is missing in `training.py`, fallback functions are defined that raise `RuntimeError`[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=try%3A%20%20%23%20re,training%20optional)). Duplicate files such as `training.py` and `training.py01` exist in `src/codex`, hinting at refactoring in progress[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/src/codex#:~:text=,Serpent%2F_codex_%2Fmain%2Fsrc%2Fcodex%2Ftraining.py01%22%2C%20%22type%22%3A%20%22file). The `configs` directory holds base/deterministic YAMLs but many subfolders (e.g., `data` and `env`) are empty or contain only placeholders[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/configs#:~:text=,Serpent%2F_codex_%2Ftree%2Fmain%2Fconfigs%2Fdata%22). |
| **Unimplemented areas** | Some areas appear incomplete or stubbed: |

- **Monkeypatch/Search modules** – directories like `src/codex/monkeypatch` and `src/codex/search` contain no files (just a `.gitkeep`), indicating planned but unimplemented features[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/src/codex#:~:text=,Serpent%2F_codex_%2Fgit%2Ftrees%2F47161a022f6ea2c501b50ab140da0db41d2d26f8%22%2C%20%22html%22%3A%20%22https%3A%2F%2Fgithub.com%2FAries).
- **Safety** – `src/safety` is a placeholder; there are references to `codex_ml.safety` but implementations are minimal.
- **Evaluation registry** – the `codex_ml/metrics` registry defines hooks but some metrics (e.g., F1) return dummy values when dependencies are missing.
- **Connectors** – connectors to external services (e.g., GitHub, Slack) are referenced in the code base but many integration modules reside in `src/codex_ml/connectors` with just stub registries.
- **Deployment** – there is a `deploy` directory, but it mainly contains skeletons for Docker/Helm; no production‑ready manifests were found.

## 2. Capability Audit Table

| Capability | Status | Existing Artifacts | Gaps / Missing Pieces | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| **Tokenization** | **Implemented** | `src/tokenization` provides a CLI using Typer and HuggingFace tokenizers for inspection, encoding and export[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/tokenization/cli.py#:~:text=def%20_load%28path%3A%20Path%29%20,tokenizer.json). `train_tokenizer.py` trains SentencePiece or BPE models with configurable vocab size and character coverage[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/tokenization/train_tokenizer.py#:~:text=%40dataclass%20class%20TrainTokenizerConfig%3A%20corpus_glob%3A%20Sequence,dry_run%3A%20bool%20%3D%20False). | Supports only unigram and BPE; no WordPiece. No fast Rust bindings; trainer always loads entire corpus into memory. Lacks unit tests for edge cases. | Training large corpora may exhaust memory; inconsistent manifest format. | Add streaming tokenization option and tests for small/large corpora. Refactor CLI to support `--fast` using HF `PreTrainedTokenizerFast`. | Revert via `git revert` of the specific commit; ensure legacy CLI still works. |
| **ChatGPT Codex Modeling** | **Partially Implemented** | `codex_ml.models` provides `MiniLM` and registry entry points (from pyproject) with dynamic loading[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject.scripts%5D%20codex,config%20%3D%20%22codex_ml.cli.validate%3Amain). `training.py` imports `MiniLMConfig` and constructs models; LoRA/PEFT hooks are referenced via optional extras[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=from%20codex_ml,tokenization%20import%20TokenizerAdapter%2C%20load_tokenizer). | Only `MiniLM` is available; no GPT‑style decoder models. PEFT integration is optional; if missing, training will raise `RuntimeError`. Model initialization lacks dtype/device logic beyond simple helpers[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=def%20_codex_config_hash%28cfg%3A%20dict%29%20,16). | Running with GPU when dependencies missing may crash; limited model selection; LoRA hooks may not be fully tested. | Implement registry pattern for additional architectures (e.g., GPT2), add dtype/device configuration via config. Provide safe fallback when PEFT is absent by skipping LoRA. | Roll back by restoring previous registry and leaving LoRA optional. |
| **Training Engine** | **Implemented (with caveats)** | `src/codex/training.py` defines a complex training wrapper with checkpointing, metric logging, gradient accumulation and FP16 support[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=%23%20,bool%3A%20import%20torch). Optional integration with HuggingFace Trainer and a `functional_training` module is attempted; fallback functions raise descriptive errors[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=try%3A%20%20%23%20re,training%20optional). | Two nearly identical training files (`training.py` and `training.py01`) cause confusion. The engine’s CLI uses `argparse` with many flags; some arguments (e.g., scheduler) are not documented. Fallback functions may break silently if dependencies missing. | Duplicate files may diverge; gradient accumulation may misbehave without proper zeroing; reliance on optional dependencies reduces determinism. | Remove `training.py01`; unify logic. Add explicit error messages if HF Trainer or `torch` unavailable. Write integration tests for grad accumulation and FP16. | Keep `training.py01` as backup branch; revert commit if unified engine causes issues. |
| **Configuration Management** | **Implemented** | Uses Hydra/OMEGACONF; `configs` folder defines base and deterministic YAMLs[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/configs#:~:text=,Serpent%2F_codex_%2Fgit%2Fblobs%2F74d325d64288265f05cd938ededacb2976e47ee9%22%2C%20%22download_url%22%3A%20%22https%3A%2F%2Fraw.githubusercontent.com%2FAries). Python dataclasses define configuration schemas in `codex_ml/config.py` (16k lines) and `config_schema.py`[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/src/codex_ml#:~:text=,Serpent%2F_codex_%2Fmain%2Fsrc%2Fcodex_ml%2Fconfig_schema.py%22%2C%20%22type%22%3A%20%22file). CLI commands can validate config (`codex-validate-config`). | Many config subfolders are empty placeholders; cross‑file defaults may be inconsistent. No documented overrides or sweep scripts. | Misconfiguration can silently use defaults; missing config for new models/training loops. | Create `config_default.yaml` documenting all fields. Add Hydra compose overrides for different experiments. Provide `scripts/config_lint.py` to check for unused fields. | Simply not using new config files; revert by removing new defaults. |
| **Evaluation & Metrics** | **Implemented** | `codex_ml.metrics` registry exposes token accuracy, perplexity, exact match, F1; metrics functions imported in `training.py` are used to compute epoch metrics and written as JSON[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=def%20_codex_epoch_metrics%28y_true%2C%20y_pred%29%20,metrics%20import%20perplexity%2C%20token_accuracy). Validation metrics are written to NDJSON via `emit_validation_metric_record`[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=def%20emit_validation_metric_record%28path%3A%20str%2C%20payload%3A%20Dict,n). | Some metric functions are stubs when dependencies missing (e.g., F1 returns 0). No cross‑validation splits; evaluation primarily on token level. | Metrics may misrepresent performance; NDJSON logs may grow unbounded; no summarization or charting. | Implement proper F1/EM calculations; integrate `datasets.load_metric`. Add evaluation scripts for summarization tasks and dataset splits. | Keep existing metrics; revert by disabling new metrics registry. |
| **Logging & Monitoring** | **Partially Implemented** | Logging is configured via `logging_config.py` and `codex_ml.monitoring.codex_logging` (not fully inspected). `training.py` writes JSON metrics; optional MLflow integration is available via `tracking` extra in pyproject[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject.optional,peft%3E%3D0.10.0). | Logging integration for TensorBoard/W&B is optional; default path and retention are unclear. System metrics via `psutil`/NVML are absent. | Without monitoring, long training jobs provide little visibility; missing logs hamper debugging. | Add a `monitoring` module using `psutil` to log CPU/GPU usage and integrate with `codex-ml-cli`. Provide a unified `codex_logger` with structured JSON logging and optional W&B offline mode. | Revert by disabling new monitoring calls; maintain existing logging functionality. |
| **Checkpointing & Resume** | **Partially Implemented** | `CheckpointManager` (from `codex_ml.utils.checkpointing`) and `save_checkpoint` helper in training module save model/optimizer/scheduler state and write sidecar hashes[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=def%20save_checkpoint,checkpoint%20and%20emit%20hashing%20sidecars). | No `load_checkpoint` counterpart; resuming training requires manual code. Best‑K retention or epoch rotation not supported. | Risk of corrupted checkpoints; inability to resume training after interruption; silent mismatch of model architecture. | Implement `CheckpointManager.load_latest()` with hash verification. Add CLI flag `--resume-from` and tests for resume. Provide retention policy (keep last N checkpoints). | Leave current saving logic; revert by ignoring new resume features. |
| **Data Handling** | **Implemented** | `ingestion` module uses `ingest` function to read text corpora with auto encoding[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/tokenization/train_tokenizer.py#:~:text=def%20_iter_text%28files%3A%20Sequence%5Bstr%5D%29%20,txt%20else%3A%20yield%20from%20txt). Dataset loaders are defined via registry (`codex_ml.data.registry`) referenced in pyproject entry point; dataset splitting/deterministic shuffling is likely implemented there. | Data caching/shuffling details are hidden; no dataset versioning. No support for streaming large datasets. | Potential nondeterministic shuffling; risk of loading entire dataset into memory. | Add dataset manifest and use `datasets` library with streaming; implement deterministic shuffle seeded by config; support caching in memory/disk. | Revert by disabling caching changes; rely on existing ingestion function. |
| **Security & Safety** | **Partially Implemented** | `codex_ml.safety` provides `SafetyConfig`, `SafetyFilters` and `SafetyViolation`, used in training to sanitize prompts[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=from%20codex_ml,codex_logging%20import). A `safety` directory exists but is mostly placeholder. `.env.example` shows environment variables (e.g., `HF_ENDPOINT`, `HF_TOKEN`) but sensitive tokens are not checked into repo. `pyproject.toml` defines dependency groups; `requirements.lock` locks versions[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents#:~:text=,). | No automated secrets scanning or dependency vulnerability checking. Prompt safety filters may be incomplete. `.env` file exists (should be git‑ignored). | Secrets or API keys could leak; dependency updates may introduce vulnerabilities. | Add `pre-commit` hook with GitGuardian/secrets scanning and Safety DB checks. Harden `SafetyFilters` with robust regex; test injection prompts. Remove `.env` from repo and rely on `.env.example` only. | Roll back by disabling new pre‑commit checks; keep existing safety filters. |
| **Internal CI/Test** | **Implemented** | Extensive pytest suite under `tests` directory (4k+ lines) covers introspection, checkpointing, data loaders, etc.[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/tests#:~:text=%5B%20%7B%20,Serpent%2F_codex_%2Fblob%2Fmain%2Ftests%2F__init__.py%22%20%7D). `pytest.ini` configures markers and environment variables, and `pyproject.toml` defines test extras[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents#:~:text=,Serpent%2F_codex_%2Fblob%2Fmain%2Fpytest.ini%22). Coverage and Ruff are configured. | Some directories (e.g., `tests/analysis`) are empty; test coverage for tokenization and training edge cases appears limited. No `tox` or `nox` gating sessions by default. | Gaps may allow breaking changes to slip; tests may rely on optional dependencies. | Add nox sessions for linting (`ruff`), type checking (`mypy`), and unit tests with coverage threshold (e.g., 80%). Write tests for config validation and resume. | Revert by running old `pytest` command without nox. |
| **Deployment** | **Partially Implemented** | `pyproject.toml` defines console scripts for CLI (`codex-ml-cli`, `codex-train`, `codex-tokenizer`, etc.)[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject.scripts%5D%20codex,config%20%3D%20%22codex_ml.cli.validate%3Amain). There is a `deploy` directory (Docker and Helm charts) but no production infrastructure; packaging uses setuptools with dynamic versioning[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject%5D%20name%20%3D%20,Serpent%22). | No published Docker images; packaging not tested on PyPI; missing `setup.cfg` for data files; no container security scan. | Users cannot easily deploy; risk of misconfigured environment. | Provide a `Dockerfile` with minimal runtime environment; add GitHub CI to build/test images offline (not executed in cost‑incurring runner). Create an `__main__.py` to allow `python -m codex`. | Revert by removing Dockerfile; keep packaging as library only. |
| **Documentation & Examples** | **Partially Implemented** | `docs` and `documentation` directories exist, as well as `notebooks` and `examples`. README may provide overview. | Many doc pages are empty placeholders; diagrams/outlines absent; missing quickstart for training and tokenizer. | New users may struggle to understand architecture. | Write README sections on architecture, configuration, training workflow; add example notebooks for training a small model; use Sphinx or MkDocs. Generate diagrams with Mermaid. | Keep current docs; revert by discarding new doc files. |
| **Experiment Tracking** | **Partially Implemented** | `pyproject.toml` defines optional `tracking` extra requiring MLflow≥2[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject.optional,peft%3E%3D0.10.0). Training writes NDJSON metric logs[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=def%20emit_validation_metric_record%28path%3A%20str%2C%20payload%3A%20Dict,n). | No default MLflow integration in code; no offline W&B mode; experiment IDs not stored. | Harder to reproduce experiments or compare runs. | Integrate MLflow local tracking in training functions when `tracking` extra installed; add CLI flag `--tracking-uri`. Provide an offline W&B initialization. | Revert by disabling new tracking flags. |
| **Extensibility** | **Implemented** | The `pyproject.toml` entry points define plugin registries for models, tokenizers, metrics, trainers and data loaders[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject.entry,codex_ml.models.registry%3A_build_default_bert). The registry pattern allows new components to be discovered without modifying core code. | Some registries (connectors, search) are empty; plugin discovery may fail silently; no documentation on how to register new components. | Difficulty for contributors to extend; risk of name clashes. | Document plugin API; add example plugin implementations; enforce namespacing. | Undo by keeping existing registries and not adding new examples. |

## 3. High‑Signal Findings

1. **Duplicate Training Modules:** Two large training files (`training.py` and `training.py01`) exist, which can confuse users and lead to diverging code paths[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/src/codex#:~:text=,Serpent%2F_codex_%2Fmain%2Fsrc%2Fcodex%2Ftraining.py01%22%2C%20%22type%22%3A%20%22file).
2. **Optional Dependency Pitfalls:** Many functions rely on optional imports (Hydra, PyTorch, HuggingFace Trainer, MLflow). Fallbacks often raise generic `RuntimeError`, leaving features unusable when dependencies are absent[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=try%3A%20%20%23%20re,training%20optional).
3. **Placeholder Directories:** Several directories (e.g., `monkeypatch`, `search`, `safety`) are empty or contain only `.gitkeep` files, indicating planned features that remain unimplemented[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents/src/codex#:~:text=,Serpent%2F_codex_%2Fgit%2Ftrees%2F47161a022f6ea2c501b50ab140da0db41d2d26f8%22%2C%20%22html%22%3A%20%22https%3A%2F%2Fgithub.com%2FAries).
4. **Missing Resume Functionality:** While checkpoints can be saved, there is no complementary load/resume logic, making recovery from failures difficult[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=def%20save_checkpoint,checkpoint%20and%20emit%20hashing%20sidecars).
5. **Sparse Documentation:** Although docs/notebooks directories exist, most documentation is skeletal, and there is no high‑level architecture overview.
6. **Limited Safety Measures:** Safety filters are rudimentary; there is no automated secrets scanning or dependency vulnerability checking; a `.env` file exists in the repository (should not be committed)[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents#:~:text=,Serpent%2F_codex_%2Fblob%2Fmain%2F.env%22).
7. **Incomplete Configuration Hierarchy:** Hydra config directories contain placeholders; configuration sweeps and environment overrides are not well documented or tested.
8. **Insufficient Evaluation:** Metrics are token‑level only; multi‑task or downstream task evaluation (e.g. summarization, classification) is absent; some metrics degrade to dummy values when dependencies are missing[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=def%20_codex_epoch_metrics%28y_true%2C%20y_pred%29%20,metrics%20import%20perplexity%2C%20token_accuracy).
9. **Inadequate Logging/Monitoring:** Logging to NDJSON files lacks system metrics; no default TensorBoard or W&B integration; logs may become very large over time.
10. **No Docker/CI Pipelines:** There is no ready‑to‑use Dockerfile or offline CI script to build and test the package, limiting production readiness.
11. **Registry but No Plugins:** Entry points are defined, but many registries (connectors, models) are empty; no examples of writing a plugin.
12. **Lack of Reproducibility Features:** Seeds are set in some modules, but environment capture, hardware fingerprinting and deterministic settings are inconsistent.
13. **Undefined Test Gates:** Despite an extensive pytest suite, there is no `nox`/`tox` gating; coverage thresholds are not enforced.
14. **Potential License Conflicts:** The repository includes multiple `LICENSES` directories; overlapping licenses may complicate packaging and distribution.
15. **Dependency Pinning vs. Flexibility:** Pyproject pins some packages loosely (e.g., `transformers>=4.41`), but `requirements.lock` pins versions; mixing these could lead to inconsistent environments[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents#:~:text=,).
16. **Unused Files and Artifacts:** There are numerous artifacts under `artifacts` and `logs` folders that may bloat the repository over time; they should be git‑ignored or relocated.
17. **Scripts Without Tests:** Several CLI scripts (`codex-import-ndjson`, `codex-generate`, `codex-infer`) appear in entry points but lack dedicated tests.
18. **No Automatic Release Process:** Without a CI pipeline, packaging and versioning must be done manually; dynamic versioning via `_version.py` may misbehave.
19. **Potential for Data Leakage:** Without dataset versioning or caching policies, there is a risk of training on stale or inconsistent data.
20. **Complexity Overload:** The repository tries to integrate many tools (Hydra, HF Trainer, MLflow, PEFT, connectors) which increases maintenance burden and complexity for new contributors.

## 4. Atomic Diffs

Below are example minimal diffs to address key issues. The diffs should be applied one at a time and accompanied by tests. Only high‑impact changes are listed.

### Diff 1 – Add `load_checkpoint` to `checkpointing.py`

**Why:** Provide resume functionality complementing `save_checkpoint`.

**Patch:**
```diff
*** Begin Patch
*** Update File: src/codex_ml/utils/checkpointing.py
@@ class CheckpointManager:
@@ def load_latest(self, pattern: str) -> dict:
-        pass
+        """Load the most recent checkpoint matching a glob pattern.
+
+        Args:
+            pattern: Glob pattern to search for saved checkpoints.
+
+        Returns:
+            A dictionary with model, optimizer and scheduler state.
+
+        Raises:
+            FileNotFoundError: If no checkpoint is found.
+            RuntimeError: If loading fails.
+        """
+        import glob
+        from pathlib import Path
+        import torch
+
+        files = sorted(glob.glob(pattern), reverse=True)
+        if not files:
+            raise FileNotFoundError(f"No checkpoint matches {pattern}")
+        ckpt_path = Path(files[0])
+        try:
+            state = torch.load(ckpt_path, map_location="cpu")
+        except Exception as exc:
+            raise RuntimeError(f"Failed to load checkpoint {ckpt_path}") from exc
+        return state
*** End Patch
```

**Risk:** May load incompatible checkpoints if the model architecture changed; error handling must be robust.

**Rollback:** `git revert` this commit or remove the `load_latest` method.

**Tests/Docs:** Add a test in `tests/checkpointing/test_resume.py` that saves a dummy model checkpoint and ensures `load_latest` returns the same state; update docs to describe `--resume-from` flag.

### Diff 2 – Remove duplicate `training.py01`

**Why:** Eliminate confusion and potential divergence between two training engines.

**Patch:**
```diff
*** Begin Patch
*** Delete File: src/codex/training.py01
*** End Patch
```

**Risk:** If downstream scripts import `training.py01`, they will break. Search for any references before deletion.

**Rollback:** Restore the file from Git history if needed.

**Tests/Docs:** Run all existing tests (`pytest -q`). Document in the changelog that `training.py01` has been deprecated.

### Diff 3 – Harden optional dependency fallbacks

**Why:** Provide clearer error messages when optional components are missing, guiding users to install extras.

**Patch:**
```diff
*** Begin Patch
*** Update File: src/codex/training.py
@@
-    except Exception:  # pragma: no cover - training optional
-        class TrainCfg:  # type: ignore[misc]
-            pass
-        def run_custom_trainer(*args, **kwargs):  # type: ignore[no-untyped-def]
-            raise RuntimeError("training.functional_training is unavailable")
+    except Exception:
+        class TrainCfg:  # type: ignore[misc]
+            """Placeholder config when functional trainer is missing."""
+            pass
+
+        def run_custom_trainer(*args, **kwargs):  # type: ignore[no-untyped-def]
+            raise RuntimeError(
+                "Functional trainer is unavailable. Install the `codex[cli]` extra to enable"
+            )
*** End Patch
```

**Risk:** Changing error messages is low‑risk but may require updating tests that check for specific exceptions.

**Rollback:** Revert the diff.

**Tests/Docs:** Add tests ensuring the RuntimeError message mentions the correct extra; update README to specify optional extras.

### Diff 4 – Introduce `monitoring` with psutil

**Why:** Collect system metrics (CPU/GPU) during training for better observability.

**Patch:**
```diff
*** Begin Patch
*** Add File: src/codex_ml/monitoring/system_metrics.py
+"""System resource monitoring utilities using psutil."""
+import json
+import time
+from pathlib import Path
+try:
+    import psutil  # type: ignore
+except ImportError:
+    psutil = None
+
+def log_system_metrics(out_path: str, interval: int = 60) -> None:
+    """Periodically log CPU and memory usage to a JSONL file.
+
+    Args:
+        out_path: Destination file for metrics.
+        interval: Seconds between samples.
+    """
+    if psutil is None:
+        raise RuntimeError("psutil is required for system metrics logging")
+    f = Path(out_path)
+    while True:
+        rec = {
+            "ts": time.time(),
+            "cpu_percent": psutil.cpu_percent(),
+            "memory": psutil.virtual_memory()._asdict(),
+        }
+        with f.open("a", encoding="utf-8") as fh:
+            fh.write(json.dumps(rec) + "\n")
+        time.sleep(interval)
*** End Patch
```

**Risk:** Continuous logging may slow down training or consume disk space; ensure interval is configurable.

**Rollback:** Delete `system_metrics.py` and remove references.

**Tests/Docs:** Add a test that spawns the logger for a few seconds and checks that the file grows; document the new `--system-metrics` flag in the CLI.

### Diff 5 – Add simple dataset manifest and deterministic shuffle

**Why:** Improve reproducibility of data loading.

**Patch:**
```diff
*** Begin Patch
*** Update File: src/codex_ml/data/registry.py
@@ def load_line_dataset(path: str, seed: int = 42) -> list[str]:
-        return Path(path).read_text(encoding="utf-8").splitlines()
+        """Load a line‑delimited text dataset with deterministic shuffling.
+
+        Args:
+            path: Path to a text file.
+            seed: Seed for shuffling.
+
+        Returns:
+            List of lines in pseudo‑random order.
+        """
+        import random
+        lines = Path(path).read_text(encoding="utf-8").splitlines()
+        random.Random(seed).shuffle(lines)
+        # write manifest for reproducibility
+        manifest_path = Path(path).with_suffix(".manifest.json")
+        manifest = {"source": path, "num_lines": len(lines), "seed": seed}
+        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
+        return lines
*** End Patch
```

**Risk:** Writing manifest may not be desired for read‑only datasets; ensure this is configurable.

**Rollback:** Remove manifest writing and revert shuffle logic.

**Tests/Docs:** Add tests verifying that shuffling with the same seed yields the same order; update docs about manifest.

## 5. Local Tests & Gates

To enforce quality offline (no external GitHub actions), use **pytest** and **nox**. Example sessions:

```python
# file: noxfile.py
import nox

@nox.session
def lint(session: nox.Session) -> None:
    session.install("ruff==0.4")
    session.run("ruff", "src", "tests")

@nox.session
def typecheck(session: nox.Session) -> None:
    session.install("mypy==1.10")
    session.install("-r", "requirements/base.txt")
    session.run("mypy", "src")

@nox.session
def tests(session: nox.Session) -> None:
    session.install("pytest==8.3", "pytest-cov")
    session.install("-r", "requirements/base.txt")
    session.install("-r", "requirements-dev.txt")
    session.run("pytest", "--cov=src", "--cov-fail-under=80")
```

Local gating commands:

- `pytest -q` runs unit tests and should pass without hitting any GitHub Action.
- `nox -s lint typecheck tests` runs linting, type checking and tests offline.
- `ruff` and `mypy` ensure style and types.

Mapping to ML Test Score categories:

| Test Category | Example Tests |
| --- | --- |
| **Data** | Verify deterministic shuffling and manifest creation for datasets. |
| **Model** | Test that `MiniLMConfig` produces correct model shapes and that training loops converge on a toy dataset. |
| **Infrastructure** | Test checkpoint save/load cycle and system metrics logging. |
| **Regression** | Ensure that new training code produces the same evaluation metrics as prior version on a fixed seed. |
| **Performance** | Add a performance test measuring tokens per second on CPU vs GPU (skipped if no GPU). |

## 6. Reproducibility Checklist

| Item | Status | Notes |
| --- | --- | --- |
| **Deterministic seeds** | *Partial* | Tokenizer training and dataset loaders allow setting a seed[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/tokenization/train_tokenizer.py#:~:text=random,mkdir%28parents%3DTrue%2C%20exist_ok%3DTrue). Training uses a `set_seed` helper but not all submodules respect it. |
| **Environment capture** | *Missing* | No code records Python version, OS, hardware, or library hashes. |
| **Code versioning** | *Implemented* | `pyproject.toml` sets dynamic versioning from `_version.py`[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject%5D%20name%20%3D%20,Serpent%22); sidecar hashes are written when saving checkpoints[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex/training.py#:~:text=def%20save_checkpoint,checkpoint%20and%20emit%20hashing%20sidecars). |
| **Data versioning** | *Missing* | Datasets are loaded directly from files without checksums or manifests; ingestion lacks dataset version tags. |
| **Dependency locking** | *Partial* | `requirements.lock` pins versions[api.github.com](https://api.github.com/repos/Aries-Serpent/_codex_/contents#:~:text=,), but `pyproject.toml` uses flexible `>=` constraints; there is no `uv` or `pip-tools` integration. |
| **Hardware determinism** | *Missing* | Mixed precision training and GPU use may introduce nondeterminism; no `torch.use_deterministic_algorithms` call. |
| **Result determinism** | *Partial* | Seeds exist but evaluation metrics may differ across runs due to data shuffling and dropout. |
| **RNG capture** | *Missing* | RNG state is not saved with checkpoints; cannot reproduce training exactly. |
| **Env variables** | *Partial* | `.env.example` documents variables but environment capture is not stored in logs. |

## 7. Deferred Items

The audit identifies several areas that are intentionally deferred or not yet implemented. Reasons include complexity, lack of ownership or ambiguous requirements:

- **Search/Monkeypatch modules:** Their purpose is unclear; implementing them could dramatically expand scope. Unless there is a clear need, these directories should remain deferred. Future tasks should clarify requirements or remove them to reduce clutter.
- **Advanced safety filtering:** Robust prompt safety and secrets scanning require specialized libraries and regular updates. Given limited resources, the current simple filters suffice for internal use. Future work could integrate third‑party libraries like OpenAI’s Safety Evaluator.
- **Comprehensive evaluation suite:** Extending evaluation beyond token accuracy (e.g., BLEU, ROUGE, classification metrics) would require curating datasets and metrics; this can be planned after the core training loop stabilizes.
- **Full CI pipeline:** Building Docker images and running them in CI could be costly. For now, focus on offline gating; CI integration can be revisited when budget allows.
- **Data versioning system:** Implementing a full data catalog (e.g., DVC) may be overkill. The minimal manifest approach introduced in Diff 5 provides a lightweight alternative. Consider DVC or MLflow artifacts later.

## 8. Error Capture Blocks

During the audit, no tooling errors blocked analysis. Should future steps fail (e.g., file download issues or YAML parsing errors), questions should be formatted like the following:

```
Question for ChatGPT @codex 2025‑09‑17T18:02:00Z:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

```yaml
**Codex-ready Task Sequence**: |
  # Phase 1 – Preparation
  1. **Establish context and capture metadata**
     1.1 Open and read the project's `README.md` and `pyproject.toml` to understand package goals and entry points.
     1.2 List the contents of the `src` and `configs` directories and record existing modules, noting any duplicate or stub files (e.g., `training.py01`).
     1.3 Create a `change_log.md` in the project root where every subsequent modification will be logged.
  
  # Phase 2 – Search & Mapping
  2. **Locate target modules**
     2.1 Search for `checkpointing.py` or similar utilities using file globbing; if found, open and inspect for `save_checkpoint` and missing `load` functions.
     2.2 Identify duplicate training implementations (e.g., `training.py` vs. `training.py01`) and map all usages via `grep`/`ripgrep`.
     2.3 Search for data loading functions in `codex_ml/data/registry.py` and note shuffle or manifest behaviour.
     2.4 Inspect monitoring/logging modules to check for psutil integration.
  
  # Phase 3 – Best‑Effort Construction
  3. **Implement missing features**
     3.1 In `src/codex_ml/utils/checkpointing.py`, add a `load_latest` or `load_checkpoint` function to restore model, optimizer and scheduler state.  Include robust error handling and ensure it writes details to `change_log.md`.
     3.2 Remove the duplicate `src/codex/training.py01` after verifying no modules import it; update imports to point to `training.py` if necessary.
     3.3 Create a new file `src/codex_ml/monitoring/system_metrics.py` that uses `psutil` to log CPU and memory usage periodically; expose a function that can be called from training CLI.
     3.4 Modify the dataset loader in `src/codex_ml/data/registry.py` to shuffle deterministically based on a seed and write a simple manifest JSON.  Ensure this behaviour is documented in the loader’s docstring.
     3.5 Update the relevant CLIs (e.g., `codex-train`) to accept `--resume-from` and `--system-metrics` flags, wiring them to the new functions.
     3.6 Run the unit tests locally using `pytest -q` to verify that changes do not break existing functionality.  If any test fails, capture the error in the error capture log and attempt to fix.
  
  # Phase 4 – Controlled Pruning
  4. **Prune unreachable features**
     4.1 If during the search you find modules like `monkeypatch` or `search` that contain only `.gitkeep`, document in `change_log.md` that these are deferred and remove any unused imports or references.  Provide the rationale for pruning.
     4.2 If certain optional integrations (e.g., HuggingFace Trainer) cannot be implemented due to missing dependencies, wrap their usage in clear error messages explaining which extra to install.
  
  # Phase 5 – Error Capture
  5. **Standardize error reporting**
     5.1 Wrap each file write or code refactor in a `try/except` block.  On exception, append an entry to `error_log.md` following this format:
         "Question for ChatGPT-5 {{timestamp}}: While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error: [ERROR_MESSAGE]. Context: [BRIEF_CONTEXT]. What are the possible causes, and how can this be resolved while preserving intended functionality?"
     5.2 Do not halt the entire script on errors; continue executing other tasks to gather maximum information.
  
  # Phase 6 – Finalization
  6. **Wrap up and verify**
     6.1 Run linting (`ruff`) and type checking (`mypy`) to ensure code quality.  Record any issues in `change_log.md` and fix where feasible.
     6.2 Execute `pytest --cov=src --cov-fail-under=80` and update test snapshots as needed.  Summarize results in `change_log.md`.
     6.3 Update the README with a changelog section summarising new features (resume, monitoring, deterministic shuffle) and any pruned modules.
     6.4 Perform a dry run of the CLI (`codex-train`) on a small dataset with the new flags to verify end‑to‑end functionality.
     6.5 Commit all changes locally; do not push or trigger any GitHub Actions.

**Additional Deliverable**: |
  #!/usr/bin/env python3
  """Codex automation script implementing audit fixes.
  
  This script should be run from the repository root.  It attempts to implement
  the tasks described in the Codex-ready sequence above.  It writes a
  change_log.md and error_log.md capturing actions and errors.  It does not
  trigger any external CI or GitHub actions.
  """
  import os
  import json
  import time
  from pathlib import Path
  
  CHANGE_LOG = Path("change_log.md")
  ERROR_LOG = Path("error_log.md")
  
  def log_change(msg: str) -> None:
      with CHANGE_LOG.open("a", encoding="utf-8") as fh:
          fh.write(f"- {msg}\n")
  
  def log_error(step: str, error: Exception, context: str) -> None:
      ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
      with ERROR_LOG.open("a", encoding="utf-8") as fh:
          fh.write(
              f"Question for ChatGPT-5 {ts}: While performing {step}, encountered the following error: {error}. Context: {context}. What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
          )
  
  def read_file(path: Path) -> str:
      try:
          return path.read_text(encoding="utf-8")
      except Exception as exc:
          log_error("read_file", exc, f"reading {path}")
          return ""
  
  def write_file(path: Path, content: str) -> None:
      try:
          path.write_text(content, encoding="utf-8")
          log_change(f"Updated {path}")
      except Exception as exc:
          log_error("write_file", exc, f"writing {path}")
  
  def add_load_checkpoint():
      """Add load_checkpoint implementation to checkpointing module."""
      ckpt_file = Path("src/codex_ml/utils/checkpointing.py")
      if not ckpt_file.exists():
          log_error("add_load_checkpoint", FileNotFoundError("missing file"), str(ckpt_file))
          return
      text = read_file(ckpt_file)
      if "def load_latest" in text or "def load_checkpoint" in text:
          log_change("load_checkpoint already exists; skipping")
          return
      new_func = """
  def load_latest(self, pattern: str) -> dict:
      """Load the most recent checkpoint matching a glob pattern."""
      import glob
      from pathlib import Path
      import torch
      files = sorted(glob.glob(pattern), reverse=True)
      if not files:
          raise FileNotFoundError(f"No checkpoint matches {pattern}")
      ckpt_path = Path(files[0])
      state = torch.load(ckpt_path, map_location="cpu")
      return state
  """
      # Insert before class end
      if "class CheckpointManager" in text:
          parts = text.split("class CheckpointManager", 1)
          before = parts[0] + "class CheckpointManager" + parts[1]
          updated = before + "\n" + new_func
          write_file(ckpt_file, updated)
      else:
          log_error("add_load_checkpoint", Exception("CheckpointManager class not found"), str(ckpt_file))
  
  def remove_duplicate_training():
      dup = Path("src/codex/training.py01")
      if dup.exists():
          try:
              dup.unlink()
              log_change("Removed duplicate training.py01")
          except Exception as exc:
              log_error("remove_duplicate_training", exc, str(dup))
  
  def add_system_metrics():
      metrics_path = Path("src/codex_ml/monitoring/system_metrics.py")
      if metrics_path.exists():
          log_change("system_metrics.py already exists; skipping")
          return
      content = """\n""" + (
          "\"\"\"System resource monitoring utilities using psutil.\"\"\"\n"
          "import json\nimport time\nfrom pathlib import Path\ntry:\n    import psutil  # type: ignore\nexcept ImportError:\n    psutil = None\n\n\n" \
          "def log_system_metrics(out_path: str, interval: int = 60) -> None:\n    \"\"\"Periodically log CPU and memory usage to a JSONL file.\n\n    Args:\n        out_path: Destination file for metrics.\n        interval: Seconds between samples.\n    \"\"\"\n    if psutil is None:\n        raise RuntimeError(\"psutil is required for system metrics logging\")\n    f = Path(out_path)\n    while True:\n        rec = {\"ts\": time.time(), \"cpu_percent\": psutil.cpu_percent(), \"memory\": psutil.virtual_memory()._asdict()}\n        with f.open(\"a\", encoding=\"utf-8\") as fh:\n            fh.write(json.dumps(rec) + \"\\n\")\n        time.sleep(interval)\n"
      )
      write_file(metrics_path, content)
  
  def update_data_loader():
      loader_path = Path("src/codex_ml/data/registry.py")
      if not loader_path.exists():
          log_error("update_data_loader", FileNotFoundError("missing file"), str(loader_path))
          return
      text = read_file(loader_path)
      if "shuffle(" in text and "manifest" in text:
          log_change("Data loader already shuffles deterministically; skipping")
          return
      new_code = """\n    import random\n    lines = Path(path).read_text(encoding=\"utf-8\").splitlines()\n    random.Random(seed).shuffle(lines)\n    manifest_path = Path(path).with_suffix(\".manifest.json\")\n    manifest = {\"source\": path, \"num_lines\": len(lines), \"seed\": seed}\n    manifest_path.write_text(json.dumps(manifest, indent=2), encoding=\"utf-8\")\n    return lines\n"""
      updated = text.replace("return Path(path).read_text(encoding=\"utf-8\").splitlines()", new_code)
      write_file(loader_path, updated)
  
  def main():
      add_load_checkpoint()
      remove_duplicate_training()
      add_system_metrics()
      update_data_loader()
      # Additional tasks like CLI flag wiring and README updates are left for manual follow‑up.
  
  if __name__ == "__main__":
      main()

**Supplied Task**: |
  1. **Implement resume functionality:** Add a `load_latest` method to `src/codex_ml/utils/checkpointing.py` and update the training CLI to support `--resume-from` so users can restore interrupted training.
  2. **Unify training engine:** Delete `src/codex/training.py01` and ensure all references point to `training.py`.  Simplify CLI flags where possible.
  3. **Integrate system monitoring:** Create a `system_metrics.py` module using `psutil` and wire it to the training CLI via a `--system-metrics` flag.
  4. **Deterministic dataset loading:** Modify the dataset loader to shuffle deterministically based on a seed and write a manifest file describing the dataset and seed.
  5. **Enhance docs and tests:** Update the README with instructions for the new features and write tests for checkpoint loading, system metrics logging, and deterministic shuffling.
  6. **Document deferred/pruned modules:** Note in docs or changelog that directories like `monkeypatch` and `search` are deferred due to lack of requirements, and remove unused imports.
```
