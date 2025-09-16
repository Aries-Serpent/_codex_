# *codex*: Status Update (2025‑09‑16)

## 1 Repo Map

| Area | Files/folders | Notes |
| --- | --- | --- |
| **Project root** | `README.md`, `Makefile`, `Dockerfile`, `docker-compose.yml`, `mkdocs.yml`, `pyproject.toml`, `noxfile.py`, `pytest.ini`, `bandit.yaml`, `codex.mk`, `conftest.py`, `scripts/`, `tools/`, `configs/` | The project is packaged as a Python library with optional CLI entry points. The `Makefile` and `noxfile.py` provide local gates for linting, type-checking and test coverage. The `README` emphasises **offline-only** validation and instructs users to run local gates via `scripts/codex_local_gates.sh`[github.com](https://github.com/Aries-Serpent/_codex_/blob/main/README.md#:~:text=NCCL%20backend%20are%20installed,run_hf_trainer%28...%2C%20distributed%3DFalse). |
| **`src/codex_ml/`** | Contains modules for tokenization, models, training, data loading, evaluation metrics, logging/monitoring, telemetry, tracking (MLflow & local NDJSON), registry, safety filters, CLI entry points and utilities. The package exposes console scripts such as `codex-ml-cli`, `codex-train`, `codex-tokenizer` via `pyproject.toml`[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject.scripts%5D%20codex,config%20%3D%20%22codex_ml.cli.validate%3Amain). |  |
| **Tokenization (`tokenization/`)** | `__init__.py` defines a `TokenizerAdapter` protocol and `load_tokenizer` function[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tokenization/__init__.py#:~:text=). `hf_tokenizer.py` wraps HuggingFace fast tokenizers[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tokenization/hf_tokenizer.py#:~:text=%40dataclass%20class%20HFTokenizerAdapter%28TokenizerAdapter%29%3A%20,tokenizer). `sentencepiece_adapter.py` implements a SentencePiece adapter[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tokenization/sentencepiece_adapter.py#:~:text=BEGIN%3A%20CODEX_SENTENCEPIECE_ADAPTER%20,with%20minimal%20conveniences). `train_tokenizer.py` uses Hydra to train tokenizers[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tokenization/train_tokenizer.py#:~:text=,tokenizers). |  |
| **Models (`models/`)** | Implements a minimal GPT-style **decoder-only** transformer with LoRA support (`decoder_only.py`)[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/models/decoder_only.py#:~:text=class%20DecoderOnlyLM%28nn.Module%29%3A%20%22%22%22A%20minimal%20GPT,language%20model). Additional minimal models (e.g., `MiniLM`) live in `models/minilm.py` (not examined in detail). The `peft/peft_adapter.py` integrates optional LoRA adaptation via PEFT[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/peft/peft_adapter.py#:~:text=,LoRA%20integration%20for%20Codex%20models). |  |
| **Training (`training/`)** | `training/__init__.py` defines `TrainingRunConfig`, `SafetySettings` and helpers to normalise configs, load datasets, apply safety filters, set seeds and run the **functional training** loop[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/training/__init__.py#:~:text=seed%3A%20int%20%3D%2042%20model%3A,%5B%5D%2C%20%7D). `training/functional_training.py` implements a simple fallback training loop using PyTorch[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/training/functional_training.py#:~:text=,Codex%20models). `train_loop.py` (in `codex_ml`) provides a **toy training loop** for demonstration and writes metrics to JSON/NDJSON files[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/train_loop.py#:~:text=BEGIN%3A%20CODEX_TRAIN_LOOP%20,evaluation%20hooks%20and%20metrics%20persistence). |  |
| **Data (`data/`)** | `data/loaders.py` provides streaming loaders for JSONL/TXT datasets with optional safety filtering, deterministic shuffling and multithreaded prefetching[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/data/loaders.py#:~:text=def%20_parse_jsonl_line%28line%3A%20str%2C%20,c). |  |
| **Evaluation (`eval/metrics.py`)** | Implements metrics like perplexity, accuracy and token-level accuracy[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/eval/metrics.py#:~:text=logits_or_nll%3A%20Iterable%2C%20targets%3A%20Iterable%5Bint%5D%2C%20,for%20a%20batch%20of%20predictions). |  |
| **Logging & Monitoring** | `monitoring/codex_logging.py` provides unified logging to TensorBoard, W&B and MLflow with optional GPU/CPU telemetry and includes a `write_ndjson` helper[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/monitoring/codex_logging.py#:~:text=def%20write_ndjson%28path%3A%20str%20,as%20NDJSON%20with%20basic%20redaction). `logging/run_logger.py` and `logging/ndjson_logger.py` implement structured NDJSON logging for parameters and metrics[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/logging/run_logger.py#:~:text=class%20RunLogger%3A%20,run%20using%20a%20shared%20schema)[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/logging/ndjson_logger.py#:~:text=def%20__init__,Lock). `tracking/mlflow_utils.py` wraps MLflow calls with graceful fallbacks[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tracking/mlflow_utils.py#:~:text=if%20not%20cfg.enable%3A%20%23%20No,nullcontext%28None), and `tracking/init_experiment.py` fans out metrics to multiple backends[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tracking/init_experiment.py#:~:text=def%20log_metric,metric%20to%20all%20configured%20writers). |  |
| **Telemetry** | Exposes Prometheus counters and histograms (`telemetry/metrics.py`)[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/telemetry/metrics.py#:~:text=REQUEST_LATENCY%20%3D%20Histogram%28,if%20_HAS_PROM%20else%20None) and can start a metrics server[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/telemetry/server.py#:~:text=def%20start_metrics_server,is%20available). |  |
| **Safety** | `safety/filters.py` is a large rules-based content filter supporting pattern matching, overrides, external classifier hooks and redaction[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/safety/filters.py#:~:text=). |  |
| **Registry & Extensibility** | `registry` exposes registries for models, tokenizers, metrics, data loaders and trainers[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/registry/__init__.py#:~:text=tokenizer_registry%2C%20%29%20from%20,get_trainer%2C%20list_trainers%2C%20register_trainer%2C%20trainer_registry). `models/registry.py` shows how LoRA is applied automatically when requested[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/models/registry.py#:~:text=,apply%20LoRA%2Fdevice%20settings%20when%20requested). |  |
| **Utilities** | `utils/checkpointing.py` handles saving/loading checkpoints with environment summaries and RNG state[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/checkpointing.py#:~:text=def%20save_checkpoint,%29%20except%20Exception%3A%20pass). `utils/provenance.py` captures environment metadata and writes reproducibility artefacts[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/provenance.py#:~:text=def%20environment_summary%28%29%20,package%2C%20and%20Python%20runtime%20metadata). `utils/seeding.py` seeds Python/NumPy/Torch and enables deterministic CUDA behaviour[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/seeding.py#:~:text=def%20set_reproducible%28seed%3A%20int%29%20,effort%20deterministic%20behaviour). |  |
| **CLI (`cli/`)** | Hydra-based dispatcher (`cli/main.py`) runs pipeline steps using Hydra configs and functional training[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/cli/main.py#:~:text=%40hydra.main%28version_base%3D,eval); `cli/validate.py` validates config files[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/cli/validate.py#:~:text=config_path%3A%20Path%20%3D%20typer,). |  |
| **Tests** | `pytest.ini` defines markers for interfaces, ML, data, infra, perf, regression, security, slow, gpu and net tests[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pytest.ini#:~:text=addopts%20%3D%20,in%20via%20RUN_NET_TESTS%3D1). Example tests include `test_tokenization.py` for round-trip correctness, `test_peft_adapter.py` for LoRA integration[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/tests/test_peft_adapter.py#:~:text=def%20test_apply_lora_merges_config_without_peft%28monkeypatch%29%3A%20monkeypatch.setattr%28,), `test_registry.py` for registry semantics[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/tests/test_registry.py#:~:text=def%20test_registry_register_get_roundtrip%28%29%3A%20reg%20%3D%20Registry%28), `test_mlflow_utils.py` for MLflow logging[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/tests/test_mlflow_utils.py#:~:text=def%20test_start_run_no_mlflow_accepts_noop_or_raise%28monkeypatch%29%3A%20,import_module) and `test_train_loop.py` with a **Codex-tailored prompt** instructing ChatGPT to expand and harden the training loop tests[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/tests/test_train_loop.py#:~:text=,loop%20utilities). |  |
| **Unimplemented/Stubs** | `src/codex_ml/peft/__init__.py` is empty, acting as a placeholder. The `test_train_loop.py` includes a human-written prompt describing missing tests and features to implement, signalling incomplete training loop capabilities[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/tests/test_train_loop.py#:~:text=,loop%20utilities). Any `TODO` comments or `pass` statements were not prominent in the inspected code. |  |

## 2 Capability Audit Table

| Capability | Status | Existing artefacts | Gaps (what’s missing) | Risks | Minimal patch plan | Rollback plan |
| --- | --- | --- | --- | --- | --- | --- |
| **Tokenization** | **Implemented**: Both HuggingFace and SentencePiece adapters provide fast encode/decode, vocabulary control, padding/truncation and saving[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tokenization/__init__.py#:~:text=)[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tokenization/hf_tokenizer.py#:~:text=%40dataclass%20class%20HFTokenizerAdapter%28TokenizerAdapter%29%3A%20,tokenizer). Training script integrates Hydra for offline training[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tokenization/train_tokenizer.py#:~:text=,tokenizers). Tests cover round-trip and determinism. | Modules: `tokenization/hf_tokenizer.py`, `sentencepiece_adapter.py`, `train_tokenizer.py`; `TokenizerAdapter` protocol; CLI entry point. | Lacks built-in vocabulary inspection CLI, automatic merging of special tokens across datasets and dataset-driven vocab expansion. SentencePiece training is optional and may not enforce reproducibility across OS. | Without consistent vocabulary and token IDs, training results may not be comparable; mismatched BOS/EOS tokens could cause generation errors. | Implement a `codex-tokenizer stats` CLI to inspect vocab size and special token IDs; add a `--seed` option in `train_tokenizer.py` to seed SentencePiece for reproducibility; provide integration tests for multi-file vocab merging. | Revert new CLI by removing it from `pyproject.toml` and training script; ensure tests run without the extension. |
| **ChatGPT Codex Modeling** | **Partially implemented**: Minimal decoder-only model with rotary embeddings and LoRA integration[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/models/decoder_only.py#:~:text=class%20DecoderOnlyLM%28nn.Module%29%3A%20%22%22%22A%20minimal%20GPT,language%20model); registry auto-applies LoRA and dtype/device settings[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/models/registry.py#:~:text=,apply%20LoRA%2Fdevice%20settings%20when%20requested). | Modules: `models/decoder_only.py`, `models/minilm.py`, `peft/peft_adapter.py`; `registry/models.py`. | Only a toy GPT variant is provided; lacks support for encoder-decoder models, attention masking for variable sequence lengths and efficient GPU kernels. LoRA config does not expose task type. | Real-world tasks require larger pretrained weights; the toy model may underfit or overfit and may not handle long sequences; LoRA incorrectly configured can degrade performance. | Add support for loading pretrained HuggingFace causal LMs offline via the registry with local-cache enforcement; update `peft_adapter.py` to expose `task_type` in the LoRA config and document recommended values; extend registry to register `llama`/`gpt2` by default. | Keep the original minimal model in registry and guard new models behind a config flag. Provide rollback by toggling `model.name` in config to `MiniLM`. |
| **Training Engine** | **Partially implemented**: `functional_training.py` provides a simple PyTorch training loop with gradient accumulation and checkpoint saving[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/training/functional_training.py#:~:text=,Codex%20models). `train_loop.py` is a separate toy loop for metrics logging[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/train_loop.py#:~:text=def%20run_training%28%20,record_metrics). Hydra-based CLI can dispatch training via functional trainer[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/cli/main.py#:~:text=%40hydra.main%28version_base%3D,eval). | Modules: `training/__init__.py`, `training/functional_training.py`, `codex_ml/train_loop.py`. | Lacks integration with HuggingFace `Trainer` or `accelerate` for mixed precision; no support for resume from checkpoint in functional trainer; gradient accumulation logic only in toy loop; dataset splits (train/eval) not fully exploited. | Without resume or scheduler warm-start, long-running jobs may waste resources; missing HF Trainer features limit scalability; separate toy loop duplicates functionality, leading to drift. | Consolidate training loops: unify `run_functional_training` and `train_loop` into one trainer API. Add resume-from-checkpoint logic using `utils/checkpointing.py`. Expose `--precision` flag (bfloat16/float16) and integrate `accelerate` when available. Add tests verifying resume and gradient accumulation. | Keep a copy of the existing loops under `legacy/` and provide config toggle to switch to the new unified trainer. To rollback, set the CLI to invoke the legacy loop. |
| **Configuration Management** | **Partially implemented**: Hydra integration in CLI; Pydantic schema for minimal training config[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/config_schema.py#:~:text=class%20TrainConfig,); ability to normalise and merge dataset settings[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/training/__init__.py#:~:text=def%20_merge_dataset_config%28dataset%3A%20Dict,eval_texts). | Files: `config_schema.py`, Hydra config templates under `configs/` (not fully explored). | Hydra sweeps and multirun support not documented; environment/seed not fully captured in config; missing `uv`/`uv.lock` gating in offline mode. | Misconfigured overrides can silently ignore fields; lack of config versioning may break backwards compatibility. | Extend `TrainConfig` to include seed, device, dtype and LoRA parameters; document recommended overrides in README; create Hydra default config with structured composition; add a `validate` CI gate using `typer` CLI. | Maintain backward-compatibility by falling back to old config if new fields missing; provide `train_config_version` field to manage migrations. |
| **Evaluation & Metrics** | **Partially implemented**: Implements perplexity, accuracy and token accuracy[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/eval/metrics.py#:~:text=logits_or_nll%3A%20Iterable%2C%20targets%3A%20Iterable%5Bint%5D%2C%20,for%20a%20batch%20of%20predictions) and analysis utilities like McCabe complexity and perplexity conversion[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/analysis/metrics.py#:~:text=def%20mccabe_minimal%28ast_tree%3A%20ast.AST%29%20,walk%28ast_tree%29%20if%20isinstance%28n%2C%20branches). The toy training loop records metrics and writes NDJSON. | Files: `eval/metrics.py`, `analysis/metrics.py`, `train_loop.py` (metrics logging). | Limited metrics (e.g., F1, BLEU, ROUGE) for generative tasks; evaluation loop integration not present; no metrics registry hooking for dynamic loading. | Without robust metrics, performance may be misinterpreted; addition of new metrics may require code changes rather than plugin registration. | Add metric functions (F1, ROUGE) and register them via `entry_points` in `pyproject.toml`. Provide an evaluation runner that loads a dataset and computes metrics. Write tests for new metrics. | Make metric registry additions reversible by registering them under names; to rollback, delete their entry point declarations. |
| **Logging & Monitoring** | **Implemented** with optional backends for TensorBoard, Weights & Biases and MLflow; NDJSON logging of parameters and metrics; Prometheus metrics with telemetry server[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/monitoring/codex_logging.py#:~:text=def%20write_ndjson%28path%3A%20str%20,as%20NDJSON%20with%20basic%20redaction)[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/telemetry/server.py#:~:text=def%20start_metrics_server,is%20available). | Files: `monitoring/codex_logging.py`, `logging/run_logger.py`, `logging/ndjson_logger.py`, `tracking/mlflow_utils.py`, `tracking/init_experiment.py`, `telemetry/`. | Some features (e.g., GPU sampling via NVML, psutil) depend on optional deps; no integration with external alerting. `write_ndjson` redacts only `text` fields, not `prompt`. | Optional dependencies may not be installed, causing silent disablement; NDJSON logs may grow unbounded; missing redaction of completions may leak sensitive data. | Add `max_bytes` rotation parameter to `write_ndjson` calls; implement redaction of `prompt` and `completion` fields via safety filters; provide a fallback `psutil` stub message in telemetry. | To revert, restore original redaction behaviour and remove rotation parameter. Ensure tests cover both behaviours. |
| **Checkpointing & Resume** | **Implemented**: `utils/checkpointing.py` writes checkpoints with SHA256 checksums, environment summaries, RNG state and meta information[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/checkpointing.py#:~:text=def%20save_checkpoint,%29%20except%20Exception%3A%20pass). Functions to load and verify checkpoints exist. | Files: `utils/checkpointing.py`, used by training. | Functional training loop does not expose `--resume-from` CLI; no automatic pruning of old checkpoints (e.g., best-k retention); integration with `tracking` metadata is absent. | Without resume, a crashed training session cannot recover; uncontrolled checkpoint accumulation may exhaust disk space. | Modify `run_functional_training` and CLI to accept `--resume-from` and call `load_training_checkpoint`; implement a retention policy parameter `keep_last_k`. Write tests verifying resume and retention logic. | Add a CLI flag `--no-resume` to disable resume. To rollback retention logic, set `keep_last_k=None`. |
| **Data Handling** | **Partially implemented**: `data/loaders.py` streams JSONL/TXT files with deterministic shuffling and optional multithreading[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/data/loaders.py#:~:text=def%20_parse_jsonl_line%28line%3A%20str%2C%20,c). Safety filters can redact prompts and completions. | Modules: `data/loaders.py`, dataset config within `TrainingRunConfig`. | No dataset caching or memory-mapped reading; evaluation dataset splitting not automated; dataset schema not validated; no support for streaming remote datasets. | Large datasets may lead to slow training or memory errors; inconsistent splits hinder reproducibility; streaming remote data could break offline assumption. | Implement a dataset manifest file that stores offsets and caching; add `train/val/test` split utilities; integrate dataset schema validation using Pydantic; add tests for splitting and caching. | Provide a configuration flag `use_cache` to toggle caching; to rollback, set `use_cache=False` and delete manifest files. |
| **Security & Safety** | **Partially implemented**: A comprehensive pattern-based safety filter with YAML/JSON policy parsing, redaction and bypass options[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/safety/filters.py#:~:text=). `bandit.yaml` defines static analysis config; `pip_audit_wrapper.py` and `LFS_POLICY.md` handle supply-chain risk. | Files: `safety/filters.py`, `bandit.yaml`, `tools/pip_audit_wrapper.py`, `tools/select_precommit.py`. | Policies rely on external YAML; integration with runtime prompts/generations may not be enforced consistently; secrets scanning not automatically run in local gates. | Missing or misconfigured safety policies can allow harmful content or secrets in prompts. | Add automatic invocation of `SafetyFilters` in training and generation flows; integrate `pip_audit` into `scripts/codex_local_gates.sh`; provide tests verifying that banned phrases are redacted. | Rollback by gating safety enforcement behind an environment variable `CODEX_SAFETY_BYPASS` and leaving it disabled by default. |
| **Internal CI/Test** | **Implemented**: `pytest.ini` defines markers and coverage threshold; `noxfile.py` has sessions for linting, type-checking, coverage and security scanning[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/noxfile.py#:~:text=%40nox,only%22%2C). `scripts/codex_local_gates.sh` runs pre-commit and tests offline[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/scripts/codex_local_gates.sh#:~:text=set%20,under%3D70%20fi). | Files: `noxfile.py`, `Makefile`, `scripts/codex_local_gates.sh`, tests. | Some tests (e.g., `test_train_loop.py`) are placeholders instructing ChatGPT to expand testing. Coverage threshold is 80 % across `src` but may be artificially low. No performance regression tests. | Incomplete tests may fail to catch regressions; low coverage thresholds can hide untested branches; absence of property-based tests for safety. | Expand test coverage for training loop (edge cases, error handling, CLI parsing) and data loaders; add performance and regression markers; raise coverage threshold gradually to 90 %. Add nox session for `pytest --durations=10` to detect slow tests. | To revert, keep original tests untouched and adjust coverage threshold back to 80 %. Provide `--skip-expanded-tests` marker to exclude new tests temporarily. |
| **Deployment** | **Partially implemented**: `Dockerfile` and `docker-compose.yml` define a container with pinned dependencies; `pyproject.toml` exposes console scripts and optional extras for CPU/GPU installations[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject.optional,peft%3E%3D0.10.0). `Makefile` has a `package` and `wheelhouse` target. | Files: `Dockerfile`, `docker-compose.yml`, `Makefile`, `codex.mk`. | Dockerfile does not include GPU support; no multi-stage build for smaller images; missing instructions to build offline images; no Windows support. | Large images slow to build; inability to use GPU in production container; missing environment capture may hinder reproducibility. | Provide separate Dockerfiles for CPU and CUDA versions; configure `pip install` to use offline wheelhouse; use multi-stage build to reduce final size; update README with container usage examples. | Keep the original Dockerfile; allow selecting CPU or GPU container via build arg; revert to original by using `Dockerfile.original`. |
| **Documentation & Examples** | **Partially implemented**: The `README` covers offline validation, quickstart commands and explains the toy model and tokenizer workflow[github.com](https://github.com/Aries-Serpent/_codex_/blob/main/README.md#:~:text=NCCL%20backend%20are%20installed,run_hf_trainer%28...%2C%20distributed%3DFalse). `mkdocs.yml` suggests a documentation site. | Files: `README.md`, `docs/` (if exists), `mkdocs.yml`. | Many modules lack docstrings; no architecture diagrams; training and evaluation examples are limited; no quickstart for LoRA or MLflow. | Users may misuse APIs or misinterpret default behaviours; missing docs hinder adoption. | Document each capability (tokenization, models, training engine, safety, telemetry) with code examples; add diagrams illustrating data flow and registry interactions; provide a notebook demonstrating training with LoRA and logging. | Rollback by leaving docs unchanged; new docs can be added in separate markdown files without affecting code. |
| **Experiment Tracking** | **Implemented**: MLflow integration with safe fallbacks; NDJSON logging; composite writer for multiple backends【439923708608160†L182-L347】. `init_experiment` records run/config/provenance and provides tags[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/tracking/init_experiment.py#:~:text=def%20log_metric,metric%20to%20all%20configured%20writers). | Files: `tracking/mlflow_utils.py`, `tracking/init_experiment.py`, `logging/run_logger.py`, `logging/ndjson_logger.py`. | `codex_ml.train_loop` does not use `init_experiment`; no W&B offline integration in the training pipeline; no explicit correlation between checkpoints and MLflow run IDs. | Inconsistent tracking across components; metrics may not be logged in a central location; mis-matching run IDs can hinder reproducibility. | Modify functional trainer to call `init_experiment` and log metrics via `ExperimentContext`; unify `train_loop` with experiment tracking; add optional W&B offline writer. | Provide a flag `--use-experiment-tracking` to enable; revert to original logging by disabling this flag and not calling `init_experiment`. |
| **Extensibility** | **Implemented**: Registries for tokenizers, models, metrics, data loaders and trainers allow dynamic registration[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/registry/__init__.py#:~:text=tokenizer_registry%2C%20%29%20from%20,get_trainer%2C%20list_trainers%2C%20register_trainer%2C%20trainer_registry). Entry points defined in `pyproject.toml` register built-in components[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/pyproject.toml#:~:text=%5Bproject.entry). | Files: `registry/base.py` (not inspected), `registry/models.py`, `registry/tokenizers.py` etc. | The plugin discovery relies on Python entry points; missing examples for adding third-party plugins; no versioning or conflict resolution documentation. | Users may register conflicting names; silent override may lead to unpredictable results; outdated plugins could break training. | Provide documentation and examples on how to implement and register custom components; add collision checking in registries and suggest namespacing; provide tests for plugin loading. | To rollback, revert the registry modifications and remove docs; provide deprecation warnings for conflicting registrations. |

## 3 High-Signal Findings

1. **Training loop duplication** – there are two separate training paths: `run_functional_training` in `training/` and the toy `train_loop.py`. The test file `test_train_loop.py` contains a **Codex prompt** instructing ChatGPT to expand testing and suggests the toy loop is only a placeholder[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/tests/test_train_loop.py#:~:text=,loop%20utilities). Consolidating these loops and expanding tests is critical.
2. **Model support is minimal** – only a small GPT-style model (`decoder_only`) and `MiniLM` exist. No support for mainstream HuggingFace models or encoder-decoder architectures, limiting usefulness for real tasks[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/models/decoder_only.py#:~:text=class%20DecoderOnlyLM%28nn.Module%29%3A%20%22%22%22A%20minimal%20GPT,language%20model).
3. **LoRA integration is optional but hidden** – `peft_adapter.py` provides LoRA adaptation but the default model config does not expose LoRA parameters and there are no examples. LoRA task type (`CAUSAL_LM`) is not configurable[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/peft/peft_adapter.py#:~:text=%23%20task_type%20is%20a%20top,CAUSAL_LM).
4. **Configuration schema is narrow** – the Pydantic `TrainConfig` only accepts a handful of fields (model_name, learning_rate, epochs, max_samples, data_path)[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/config_schema.py#:~:text=class%20TrainConfig,). Most training settings (seed, batch size, scheduler, device, dtype, LoRA, evaluation splits) are not validated.
5. **Dataset handling lacks split management** – `TrainingRunConfig` includes dataset paths but there is no utility for train/val/test splitting, caching or schema validation[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/training/__init__.py#:~:text=seed%3A%20int%20%3D%2042%20model%3A,%5B%5D%2C%20%7D). This may lead to inconsistent splits and data leakage.
6. **Evaluation metrics are limited** – only perplexity and (token) accuracy are implemented[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/eval/metrics.py#:~:text=logits_or_nll%3A%20Iterable%2C%20targets%3A%20Iterable%5Bint%5D%2C%20,for%20a%20batch%20of%20predictions). There is no F1, ROUGE or BLEU; no integration with evaluation loops or dataset evaluation.
7. **Experiment tracking is inconsistently used** – `train_loop.py` writes metrics but does not use `init_experiment`, while `functional_training` may rely on NDJSON logs; thus metrics and parameters may scatter across files[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/train_loop.py#:~:text=def%20run_training%28%20,record_metrics).
8. **Safety enforcement is optional** – safety filters exist but are not invoked in all code paths (e.g., generation or `train_loop`). Without enforcement, prompts or completions may leak sensitive information[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/safety/filters.py#:~:text=).
9. **Logging/Telemetry dependencies optional** – `psutil`, `pynvml`, `wandb` and `mlflow` are optional; absent packages silently disable features. This may mislead users into believing telemetry is active[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/monitoring/codex_logging.py#:~:text=def%20write_ndjson%28path%3A%20str%20,as%20NDJSON%20with%20basic%20redaction).
10. **Docs and examples are insufficient** – there is no quickstart for training a model with LoRA or using MLflow, no architectural overview and minimal code documentation. The `README` is heavy on offline gating but light on usage[github.com](https://github.com/Aries-Serpent/_codex_/blob/main/README.md#:~:text=NCCL%20backend%20are%20installed,run_hf_trainer%28...%2C%20distributed%3DFalse).

## 4 Atomic Diffs (examples)

Below are small, high-impact diff proposals. Each diff includes rationale, risks, rollback and test/doc considerations. **These diffs must be applied locally (no GitHub Actions)**.

### Diff 1 – Expose LoRA configuration and task type

*Rationale:* LoRA integration exists but the user cannot configure parameters or task type. Exposing these improves flexibility.

```
*** Begin Patch
*** Update File: src/codex_ml/peft/peft_adapter.py
@@
-DEFAULT_CFG: Dict[str, Any] = {
-    "r": 8,
-    "lora_alpha": 16,
-    "lora_dropout": 0.05,
-    "bias": "none",
-    # task_type is handled specially; kept out of defaults to avoid surprising LoraConfig kwargs
-    # "task_type": "CAUSAL_LM",
-}
+DEFAULT_CFG: Dict[str, Any] = {
+    "r": 8,
+    "lora_alpha": 16,
+    "lora_dropout": 0.05,
+    "bias": "none",
+    # default task type for causal language modelling; users may override via cfg or kwargs
+    "task_type": "CAUSAL_LM",
+}
@@
 def apply_lora(model: Any, cfg: Optional[Dict[str, Any]] = None, /, **overrides: Any) -> Any:
-    # task_type is a top-level parameter for LoraConfig
-    task_type = merged.get("task_type", "CAUSAL_LM")
+    # allow explicit override of task_type via cfg or kwargs
+    task_type = str(merged.pop("task_type", "CAUSAL_LM"))
*** End Patch
```

*Risk:* Changing defaults may break existing callers expecting `task_type` to be ignored. However, the patch still allows overrides and uses `pop` to prevent duplication.

*Rollback:* Revert the added `task_type` entry and the `pop` call. Existing tests should continue to pass.

*Tests/Docs:* Update tests in `test_peft_adapter.py` to assert that `peft_config["task_type"]` equals the default. Document LoRA configuration and examples in README.

### Diff 2 – Add resume-from-checkpoint support in functional trainer

*Rationale:* Running jobs cannot resume from checkpoints; adding a `--resume-from` flag makes experiments recoverable.

```
*** Begin Patch
*** Update File: src/codex_ml/training/__init__.py
@@
 def run_functional_training(cfg: Mapping[str, Any]) -> None:
     """Run a simplified training loop using functional_training.py."""
@@
-    ckpt_dir = cfg.get("checkpoint_dir") or None
-    resume = None
-    # prepare output and checkpoints
-    out_dir = Path(cfg.get("output_dir", "runs/default"))
-    out_dir.mkdir(parents=True, exist_ok=True)
+    ckpt_dir = cfg.get("checkpoint_dir") or None
+    resume_from = cfg.get("resume_from")
+    out_dir = Path(cfg.get("output_dir", "runs/default"))
+    out_dir.mkdir(parents=True, exist_ok=True)
+    if resume_from:
+        # best-effort load epoch and extra
+        try:
+            epoch, _ = load_training_checkpoint(resume_from)
+            print(f"[Training] Resuming from {resume_from} @ epoch {epoch}")
+        except Exception as exc:
+            print(f"[Training] Failed to resume from {resume_from}: {exc}")
*** End Patch
```

*Risk:* Users may mistakenly provide an invalid path, causing training to start from epoch `None`. The diff prints a message and continues.

*Rollback:* Remove the new resume logic and the `resume_from` config key.

*Tests/Docs:* Add a test that saves a checkpoint via `save_checkpoint` and then resumes training; verify that the starting epoch increases. Document the `resume_from` option in the config schema.

### Diff 3 – Consolidate training loops and call experiment tracking

*Rationale:* The toy training loop duplicates functionality and does not use experiment tracking. Consolidating loops reduces drift and enables MLflow/W&B logging.

```
*** Begin Patch
*** Update File: src/codex_ml/train_loop.py
@@
-def run_training(
-    *
-    epochs: int,
-    grad_accum: int,
-    mlflow_enable: bool = False,
-    mlflow_uri: str = "file:./mlruns",
-    mlflow_experiment: str = "codex",
-    telemetry_enable: bool = False,
-    telemetry_port: int = 8001,
-) -> None:
-    """Run demo training loop with optional MLflow and telemetry."""
-    set_reproducible()
-    cfg_hash = "c898a1161dce426c3f46d5b5f09fd0544abc292a4be5076ecf0d75af2bce2a9c"
-    best = {"epoch": -1, "acc": -1.0}
-    if telemetry_enable:
-        start_metrics_server(port=telemetry_port)
-    if mlflow_enable and _HAS_MLFLOW:
-        mlflow.set_tracking_uri(mlflow_uri)
-        mlflow.set_experiment(mlflow_experiment)
-        mlflow.start_run()
-        mlflow.log_params({"epochs": epochs, "grad_accum": grad_accum})
-    for ep in range(epochs):
-        m = demo_epoch(ep, grad_accum=grad_accum)
-        record_metrics("epoch_end", ep, m, cfg_hash)
-        if mlflow_enable and _HAS_MLFLOW:
-            mlflow.log_metrics(m, step=ep)
-        if m["acc"] > best["acc"]:
-            best = {"epoch": ep, "acc": m["acc"]}
-    record_metrics(
-        "best_checkpoint",
-        best["epoch"],
-        {"acc": best["acc"], "ppl": None},
-        cfg_hash,
-        notes="best-of-toy",
-    )
-    if mlflow_enable and _HAS_MLFLOW:
-        mlflow.end_run()
+def run_training(*, epochs: int, grad_accum: int, **options: Any) -> None:
+    """Run the demo training loop and dispatch metrics via experiment tracking."""
+    from codex_ml.tracking.init_experiment import init_experiment
+
+    set_reproducible()
+    ctx = init_experiment(
+        type(
+            "Cfg",
+            (),
+            {
+                "experiment": options.get("mlflow_experiment", "codex"),
+                "tracking": {
+                    "output_dir": options.get("output_dir", "runs/demo"),
+                    "mlflow": {"enable": options.get("mlflow_enable", False)},
+                    "tensorboard": {"enable": options.get("tb_enable", False)},
+                    "wandb": {"enable": options.get("wandb_enable", False), "project": "codex-offline"},
+                },
+                "model": "decoder_only",
+                "dataset": None,
+                "seed": 42,
+            },
+        )()
+    )
+    best = {"epoch": -1, "acc": -1.0}
+    for ep in range(epochs):
+        metrics = demo_epoch(ep, grad_accum=grad_accum)
+        # log via ExperimentContext
+        ctx.log_metric(step=ep, split="train", metric="acc", value=metrics["acc"])
+        ctx.log_metric(step=ep, split="train", metric="ppl", value=metrics["ppl"])
+        ctx.log_metric(step=ep, split="train", metric="grad_accum", value=metrics["grad_accum"])
+        if metrics["acc"] > best["acc"]:
+            best = {"epoch": ep, "acc": metrics["acc"]}
+    ctx.log_metric(step=best["epoch"], split="best", metric="acc", value=best["acc"])
+    ctx.finalize()
*** End Patch
```

*Risk:* This diff introduces a dependency on the experiment tracking subsystem; if optional MLflow or W&B are not installed, init may fail. However, `init_experiment` gracefully disables missing backends. Existing scripts depending on `mlflow.log_metrics` will need updates.

*Rollback:* Keep the original `run_training` function under a new name (e.g., `run_training_legacy`) and update CLI to call either version based on a flag (e.g., `--use-experiment-tracking`).

*Tests/Docs:* Update tests in `test_train_loop.py` to validate that metrics are written via `ExperimentContext` and not just JSON/NDJSON. Document how to enable experiment tracking.

### Diff 4 – Add dataset split utilities and config

*Rationale:* Data handling currently loads datasets but does not provide train/val/test splitting or schema validation.

```
*** Begin Patch
*** Add File: src/codex_ml/data/split_utils.py
+"""Dataset split and validation helpers."""
+from __future__ import annotations
+
+from dataclasses import dataclass
+from pathlib import Path
+from typing import Iterable, Tuple, List, Any
+
+
+@dataclass
+class SplitPaths:
+    train: Path
+    val: Path
+    test: Path | None = None
+
+
+def split_jsonl(input_path: str | Path, ratios: Tuple[float, float, float] = (0.8, 0.1, 0.1), seed: int = 42) -> SplitPaths:
+    """Split a JSONL file into train/val/test according to ratios.
+
+    Returns a SplitPaths dataclass with paths to the created files.
+    """
+    import json, random
+
+    inp = Path(input_path)
+    data = [json.loads(l) for l in inp.read_text(encoding="utf-8").splitlines() if l.strip()]
+    random.Random(seed).shuffle(data)
+    n = len(data)
+    t_end = int(n * ratios[0])
+    v_end = t_end + int(n * ratios[1])
+    splits: List[List[Any]] = [data[:t_end], data[t_end:v_end], data[v_end:]]
+    out_paths = []
+    for name, items in zip(["train", "val", "test"], splits):
+        p = inp.with_name(f"{inp.stem}.{name}.jsonl")
+        with p.open("w", encoding="utf-8") as fh:
+            for obj in items:
+                fh.write(json.dumps(obj) + "\n")
+        out_paths.append(p)
+    return SplitPaths(*out_paths)
*** End Patch
```

*Risk:* Splitting large datasets may exhaust memory; ratios may not sum to 1.0. Use streaming splitting for large files in future. The utility writes new files in the same directory, potentially overwriting existing splits.

*Rollback:* Remove the new file and update dataset loading to treat a single path as containing all data.

*Tests/Docs:* Add tests verifying that `split_jsonl` produces non-overlapping splits and preserves all records; document dataset splitting in README.

## 5 Local Tests & Gates

- **Pytest markers and commands**: Continue using `pytest -q -m "not slow"` as default. Increase coverage threshold in `pytest.ini` from 80 % to 85 %. Recommend running `pytest -m "perf" --durations=10` to detect performance regressions.
- **Nox sessions**: Add a new session `nox -s perf` which installs optional deps and runs performance tests. Extend the existing `coverage` session to install MLflow and W&B offline and run tests under both CPU and GPU markers.
- **ML Test Score mapping**:

    | Test file | Category |
    | --- | --- |
    | `tests/test_tokenization.py` | Data correctness: ensures deterministic encode/decode |
    | `tests/test_peft_adapter.py` | Model integration: tests LoRA adaptation |
    | `tests/test_mlflow_utils.py` | Infrastructure: logs/tracking integration |
    | `tests/test_checkpointing.py` | Infrastructure/reproducibility |
    | `tests/test_registry.py` | Extensibility |
    | Proposed `test_data_split_utils.py` | Data handling correctness |
    | Expanded `test_train_loop.py` (to be implemented) | Model & training, regression |

## 6 Reproducibility Checklist

- **Seeds**: The project uses `TrainingRunConfig.seed` (default 42) and calls `set_reproducible()` to seed Python/NumPy/Torch and configure deterministic CUDA[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/seeding.py#:~:text=def%20set_reproducible%28seed%3A%20int%29%20,effort%20deterministic%20behaviour). ✔️
- **Environment capture**: `utils/provenance.export_environment` writes environment summary, pip freeze and concise NDJSON[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/provenance.py#:~:text=def%20environment_summary%28%29%20,package%2C%20and%20Python%20runtime%20metadata). Checkpointing includes environment summary in the `extra` field[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/checkpointing.py#:~:text=def%20save_checkpoint,%29%20except%20Exception%3A%20pass). ✔️
- **Code versioning**: Git commit hash is captured where possible via `_git_commit` and included in checkpoints and logs[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/checkpointing.py#:~:text=def%20save_checkpoint,best). ✔️
- **Determinism**: Deterministic shuffling uses random seeds in data loaders[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/data/loaders.py#:~:text=%29%20,None%3A%20import%20random%20as%20_rnd). Torch is seeded with deterministic flags[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/utils/seeding.py#:~:text=def%20set_reproducible%28seed%3A%20int%29%20,effort%20deterministic%20behaviour). ✔️
- **Result logging**: Metrics and parameters are written to NDJSON with timestamps[raw.githubusercontent.com](https://raw.githubusercontent.com/Aries-Serpent/_codex_/main/src/codex_ml/train_loop.py#:~:text=ART_DIR.mkdir%28parents%3DTrue%2C%20exist_ok%3DTrue%29%20payload%20%3D%20,write_ndjson%28out_ndjson%2C%20payload); experiment tracking optionally logs to MLflow and W&B. ✔️
- **Missing items**: There is no explicit mechanism to capture the exact version of external datasets; dataset splitting/caching is manual. Hydra run directory snapshots are written only when Hydra is used. There is no reproducibility report summarising random seeds, environment, config, dataset hash and code version in one place. ✘

## 7 Deferred Items

- **Distributed training and mixed precision**: Implementing a full HuggingFace `Trainer` or `accelerate` loop would require significant work and GPU resources; deferred until core features are stabilised.
- **Full dataset caching and remote streaming**: Complex due to offline policy and would add build/test overhead. Use local splits for now and revisit when remote datasets are required.
- **Advanced safety classification**: Integration with large safety classifiers (e.g., OpenAI’s moderation endpoint) would require network calls; deferred due to offline requirement.
- **Comprehensive documentation site**: An MkDocs site exists but content is minimal; writing full docs would take time. Prioritised after feature completeness.

## 8 Error Capture Blocks

Whenever an analysis step or training run encounters an unexpected error, record it using the following format:

```
Question for ChatGPT @codex {timestamp}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

This captures sufficient context (step number, description, error and surrounding context) to allow ChatGPT to reason about the failure without replicating the entire environment.

## 9 Codex-ready Task Sequence and Script

Below is a template describing how to transform the high-signal findings and diffs into a **Codex-ready** sequential execution plan. The tasks instruct ChatGPT-5 to implement missing features, explore modules and write code patches while adhering to offline constraints. The corresponding executable script automates the workflow.

```
**Codex-ready Task Sequence**
Transform the supplied task below into a **Codex-ready sequential execution block** that:
1. Enforces **best-effort construction** before pruning.
2. Explicitly explores related modules, scripts, or tooling in depth.
3. Compares purposes and identifies whether a viable mapping or adaptation can be made.
4. Only after exhausting all possibilities should an item be pruned, and **pruning must include documented rationale**.
5. Includes explicit **error capture** formatted as a research question tailored for ChatGPT-5 to investigate and provide solutions.
6. Scripts will typically be in python, bash, sql, javascript, html, etc.

**Structure Requirements:**
- **Sequential, numbered execution phases** (Preparation, Search & Mapping, Best-Effort Construction, Controlled Pruning, Error Capture, Finalization).
- Must be **ready for Codex to execute until completion**.
- Detailed sub-steps under each phase.
- Error capture block must format questions like:
  > Question for ChatGPT-5 {{timestamp}}:
  > While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error: [ERROR_MESSAGE]
  > Context: [BRIEF_CONTEXT].
  > What are the possible causes, and how can this be resolved while preserving intended functionality?

**Additional Deliverable:**
After producing the sequential execution block, also generate an **executable script** (Python and CLI, Bash as needed) sequential Codex-ready execution blocks that implements the workflow end-to-end, including:
- README parsing and reference replacement/removal
- File search and adaptation attempt
- Gap documentation in a change log
- Error capture and formatting for ChatGPT-5 research questions
- Finalization with updated deliverables
- **Note that the only prohibited action is enabling or producing any `yaml` files that will initiate a Cost Incurring GitHub Action. ALL pre-commit checks must run solely within Codex environment only— (no GitHub Actions, etc.).**

**Supplied Task (expand on task as needed for Codex to action each until completion):**
:::Example Suggested Task Prompt for Codex to action until completion based on gaps, missing, and incomplete aspects mentioned from High-Signal Findings, Atomic Diffs, Local Tests & Gates, all items on Reproducibility Checklist.
Second Example Suggested Task Prompt for Codex to action until completion based on gaps, missing, and incomplete aspects mentioned from High-Signal Findings, Atomic Diffs, Local Tests & Gates, all items on Reproducibility Checklist.
Third Example Suggested Task Prompt for Codex to action until completion based on gaps, missing, and incomplete aspects mentioned from High-Signal Findings, Atomic Diffs, Local Tests & Gates, all items on Reproducibility Checklist.:::
```

An **executable script** implementing the sequence might:

1. **Preparation**: Read the README and existing config files; detect which features (LoRA, checkpoint resume, dataset splitting) are currently missing. Write a `change_log.md` documenting current gaps.
2. **Search & Mapping**: Traverse the `src/codex_ml` directory to locate relevant modules (e.g., `peft_adapter.py`, `training/__init__.py`, `train_loop.py`). For each gap, map where code should be added or modified.
3. **Best-Effort Construction**: Apply patches (similar to the diffs above) using `sed` or Python file editing; add new modules (e.g., `split_utils.py`); update tests accordingly. Run `pytest` locally to verify that new code passes existing tests.
4. **Controlled Pruning**: If a feature cannot be fully implemented (e.g., distributed training), document in the change log with rationale and mark as deferred.
5. **Error Capture**: Wrap each modification step in try/except; on exception, write an error block to `error_log.md` using the prescribed format.
6. **Finalization**: Update README and docs; run `pre-commit` and `pytest` to ensure local gates pass; create a summary of changes in `change_log.md`.

A simplified Python script skeleton is provided below:

```
# scripts/update_codex_features.py
import subprocess
from pathlib import Path
import datetime, json

change_log = Path("change_log.md")
error_log = Path("error_log.md")

# Step 1: Analyse README and config
readme = Path("README.md").read_text(encoding="utf-8")
# ... parse for features

# Step 2: Apply patches
try:
    # Example: insert LoRA task_type default
    content = Path("src/codex_ml/peft/peft_adapter.py").read_text()
    # ... string replace operations matching Diff 1 ...
    Path("src/codex_ml/peft/peft_adapter.py").write_text(content)
    change_log.write_text("Applied LoRA task_type default.\n", append=True)
except Exception as exc:
    ts = datetime.datetime.utcnow().isoformat()
    with error_log.open("a") as fh:
        fh.write(f"Question for ChatGPT-5 {ts}:\n")
        fh.write(f"While performing PATCH LoRA default, encountered error: {exc}\n")
        fh.write("Context: updating peft_adapter.py\n\n")

# Step 3: Run tests
subprocess.run(["pytest", "-q"], check=False)
# Log results and continue
```

This script can be extended to implement all diff patches, update tests and docs, and collect error capture blocks.
