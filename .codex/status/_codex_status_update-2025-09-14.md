# _codex_: Status Update (2025-09-14)
===================================

1 Repo map
----------
The repository contains several top‑level folders and files. Below is a high‑level overview of the structure and obvious stubs or placeholders.

| Path | Purpose / notes | Stubs & placeholders |
| --- | --- | --- |
| **README.md** | Project overview, quickstart instructions, deterministic installation, offline CI policies and dataset registry[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L17-L84)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L191-L260). | – |
| **AUDIT_PROMPT.md** | Template for running this audit. | – |
| **.codex/** | Stores internal status updates, validation manifests, `change_log.md`, error logs and codex-script outputs. The directory also contains scripts (`setup.sh`) and notes used for local validation. | Files under `.codex/status/` are generated reports; `.codex/scripts/setup.sh` configures pre‑commit & nox locally; `.codex/release/PINNED_SHAS.md` pins upstream dependencies; `.codex/validation/…` holds manifests from previous runs. |
| **configs/** | Hydra configuration tree. Root `config.yaml` defines defaults for `env`, `model`, `data`, `tokenization`, `training`, `logging`, `tracking`, etc. Subfolders include `env/ubuntu.yaml` for environment overrides[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/env/ubuntu.yaml#L1-L6), `model/base.yaml` for model and LoRA settings[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/model/base.yaml#L1-L10), `training/base.yaml` specifying hyper‑parameters and LoRA/PEFT defaults[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/training/base.yaml#L1-L20), `tokenization/base.yaml` for tokenizer training[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/tokenization/base.yaml#L1-L14), `data/base.yaml` for dataset splitting[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/data/base.yaml#L1-L2) and `tracking/base.yaml` for mlflow/wandb toggles[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/tracking/base.yaml#L1-L6). | No apparent stubs; Hydra defaults may not cover all CLI flags. |
| **analysis/** | Houses small utilities for metrics logging (`metrics.py`), file scanning (`providers.py`), offline CI injection (`parsers.py`) and registry helpers (`registry.py`). | All implemented. |
| **docs/** | Markdown documentation covering data handling[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/data_handling.md#L1-L34), model registry[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/model_registry.md#L1-L38), evaluation runner[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/evaluation_runner.md#L1-L11) and reproducibility guidelines[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/repro.md#L1-L14). Also includes architecture notes and a runbook. | – |
| **training/** | Contains the Hugging‑Face training wrapper `engine_hf_trainer.py`, dataset utilities (`datasets.py`, `data_utils.py`), streaming and caching utilities (`streaming.py`, `cache.py`), and optional functional training loops. A Hydra loader converts YAML configs into `TrainingArguments`. | Extensive but some features (e.g. gradient accumulation tests) are skipped or xfailed in `tests/test_engine_hf_trainer.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tests/test_engine_hf_trainer.py#L97-L141). |
| **src/codex/** | Houses CLI entry points (`cli.py`), chat logging (`chat.py`), session logging (`logging/session_logger.py`), ingestion helpers and various utilities. | `_fix_pool()` stub in `cli.py` is marked `# TODO` and never called. Several modules include fallback code guarded by `try/except` blocks, but these are not stubs. |
| **src/codex_ml/** | Primary ML package. Subpackages include:
| | * `cli/main.py`: Hydra entry point for training/evaluation[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/cli/main.py#L98-L130). * `models/registry.py`: model factory with LoRA support[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/models/registry.py#L1-L118). Only `MiniLM` and a generic Hugging‑Face model are registered. * `peft/peft_adapter.py`: LoRA integration with graceful fallbacks[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/peft/peft_adapter.py#L1-L138). * `eval/`: evaluation runner (`eval_runner.py`) producing NDJSON/CSV logs[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/eval/eval_runner.py#L49-L108) and dataset loader[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/eval/datasets.py#L22-L62). * `metrics/registry.py`: built‑in metrics (accuracy@token, perplexity, EM, F1, BLEU, ROUGE, chrF)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/metrics/registry.py#L65-L100)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/metrics/registry.py#L171-L195). * `interfaces/`: tokenization and RL interfaces. `tokenizer.py` defines `TokenizerAdapter` and `HFTokenizer`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/interfaces/tokenizer.py#L35-L91); `reward_model.py` and `rl.py` provide abstract base classes[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/interfaces/reward_model.py#L8-L36)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/interfaces/rl.py#L8-L29); `registry.py` loads components via configuration and writes error logs[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/interfaces/registry.py#L61-L88). * `reward_models/simple.py`: a toy length‑based reward model[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/reward_models/simple.py#L8-L27); `reward_models/rlhf.py` is a stub for RLHF with unimplemented methods[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/reward_models/rlhf.py#L1-L27). * `utils/determinism.py`: sets seeds and deterministic settings across Python, NumPy and PyTorch[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/determinism.py#L33-L89); `utils/config_loader.py` loads Hydra configs with fallback[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L26-L83). |
| **src/ingestion/** | Provides file reading with encoding detection, deterministic shuffling and dataset splitting with caching[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/ingestion/utils.py#L118-L188). | Fully implemented. |
| **services/api/** | Implements a FastAPI app for inference, training and evaluation with API key and rate limiting[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/services/api/main.py#L26-L117). Training jobs create dummy artifact folders. | Simplistic; security and concurrency controls are minimal. |
| **tools/** | Several helper scripts. `apply_stack_polish.py` and `codex_script.py` orchestrate environment hardening: adding dev/run requirements, GPU check scripts, SentencePiece adapter, LoRA hooks and tests, and capturing errors; these scripts write to `.codex/` but do not run remote CI. | Many features are unimplemented or only stubbed within these scripts. |
| **tests/** | Test suite run via `pytest`. Coverage includes training config loading[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tests/training/test_config_loading.py#L1-L87), HF trainer integration, dataset splitting and interfaces contracts[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tests/test_interfaces_compat.py#L1-L115). Some tests are marked `xfail` or `skip` (e.g., gradient accumulation and heavy sentencepiece training). | Some behaviours (e.g. RL interfaces) are untested. |
| **noxfile.py** | Defines local nox sessions for linting, tests and coverage. | – |
| **Makefile** | Basic convenience commands; no remote CI. | – |

### Observed stubs and unimplemented areas
* **`_fix_pool()` stub** in `src/codex/cli.py` is marked `# TODO` and never called. It likely intended to configure a thread/process pool, but currently raises a `NotImplementedError`.
* **RLHF integration** (`src/codex_ml/reward_models/rlhf.py`) contains placeholder classes `RewardModel` and `RLTrainer` with unimplemented `score()` and `train()` methods[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/reward_models/rlhf.py#L1-L27).
* **LoRA training hooks** exist via `peft_adapter.py`, but integration into the HF training engine lacks tests; LoRA options appear in configs but some CLI flags remain unused.
* **Chat interfaces and RL agents** in `src/codex_ml/interfaces/rl.py` provide abstract methods but no concrete implementation.
* **Tools** such as `codex_script.py` and `apply_stack_polish.py` describe various tasks (adding GPU checks, SentencePiece adapters, etc.) but many features are only inserted into the repo as code snippets guarded by sentinel markers; they are not invoked by the main training pipeline.
* Some tests (e.g., gradient accumulation) are marked `xfail` or `skip` indicating incomplete support.

2 Capability audit table
------------------------
For each capability the table below summarises current implementation status, available artifacts, gaps, risks, suggested minimal patch and rollback plan.

| Capability | Status | Existing artifacts / modules | Gaps & missing pieces | Risks if used in production | Minimal patch plan | Rollback plan |
| --- | --- | --- | --- | --- | --- | --- |
| **Tokenization** (fast tokenizer, vocab, encode/decode, padding/truncation) | **Partially implemented** | `src/codex_ml/interfaces/tokenizer.py` provides `TokenizerAdapter`, `HFTokenizer` with encode/decode, batch_encode/plus and property accessors[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/interfaces/tokenizer.py#L35-L91). Configs under `configs/tokenization/base.yaml` specify vocab size and model type[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/tokenization/base.yaml#L1-L14). `training/datasets.py` uses HF tokenizers. `codex_script.py`/`apply_stack_polish.py` include a SentencePiece adapter stub. | No built‑in training of new tokenizers; SentencePiece adapter exists only in script form and is not wired into the training pipeline. No tests verify fast tokenization or vocabulary consistency. Padding/truncation options are partly exposed via HFTokenizer but not surfaced via CLI. | Wrong tokenization settings cause sequence length mismatches and degrade model performance. Without tests, encoded outputs may differ across versions (fast vs slow). | (i) Promote the `SentencePieceAdapter` from `tools` into `src/codex_ml/tokenizers/sentencepiece_adapter.py` with proper training/loading functions and Hydra config; (ii) expose `tokenization` settings via CLI flags; (iii) add tests ensuring encode/decode round‑trip, vocab size assertion and padding/truncation behaviours. | Isolate tokenization changes behind new module; revert by restoring `HFTokenizer` as default and disabling SentencePiece in configs. Provide fallback to HF tokenizer if the new adapter fails. |
| **ChatGPT Codex modeling** (model init, dtype, device placement, LoRA/PEFT hooks) | **Partially implemented** | Model registry (`codex_ml/models/registry.py`) loads `MiniLM` and HF models and applies LoRA via `peft_adapter.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/models/registry.py#L1-L118). Dtype/device settings are respected. Configs expose LoRA parameters[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/model/base.yaml#L1-L10). | Only two model types are registered; there is no ChatGPT/Codex‑specific architecture. LoRA parameters are in config but CLI integration is incomplete (flags not wired to Hydra overrides). PEFT support lacks tests; fallback when `peft` isn’t installed returns the original model without error, which could lead to silent misuse. | Loading unknown models or missing LoRA adapters could produce invalid models. Running large models on CPU may crash. Without tests, LoRA integration may silently no‑op. | (i) Add a ChatGPT/CausalLM entry in the registry with proper config fields (model name, revision, dtype, device); (ii) implement CLI flags `--lora.enable`, `--lora.r`, etc., passing to Hydra; (iii) extend tests to cover LoRA application and dtype/device placement. | Use environment variable `DISABLE_LORA` to bypass LoRA; revert by resetting config defaults and removing new registry entries if issues arise. |
| **Training engine** (HF Trainer or custom loop, precision, gradient accumulation) | **Implemented (HF)** but **partially implemented** for custom loops | `training/engine_hf_trainer.py` wraps HuggingFace `Trainer`, supports gradient accumulation, precision options, LoRA and early stopping; includes patching for accelerate compatibility and metrics logging[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/training/engine_hf_trainer.py#L1-L23)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/training/engine_hf_trainer.py#L30-L104). `training/datasets.py` and `training/streaming.py` feed data. | Some optional features (gradient accumulation/resume) are not fully tested; tests mark them xfail/skip[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tests/test_engine_hf_trainer.py#L97-L141). Custom training loop (functional_training.py) is referenced in docs but absent. No CLI flag toggles between Trainer and custom loop. | Unhandled errors during accumulation/resume may corrupt checkpoints. Without deterministic gradient reduction, results vary across runs. Lack of custom loop prevents specialized training. | (i) Implement gradient‑accumulation tests to ensure metrics and state saving; (ii) supply a minimal functional training loop (PyTorch) that respects seeds and supports LoRA; (iii) add CLI switch `--engine=hf/custom`. | Keep HF trainer as default; new loop behind feature flag; revert by removing the flag and associated code. Provide tests to ensure HF trainer remains unaffected. |
| **Configuration management** (Hydra/YAML structure, overrides, sweeps) | **Implemented** | Hydra root config and base modules exist; `codex_ml/utils/config_loader.py` loads training configs with fallback defaults[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L26-L83); Hydra CLI in `codex_ml/cli/main.py` composes configs with overrides[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/cli/main.py#L98-L130). | Parameter sweeps (e.g., Hydra multirun) are not documented/tested; configuration of tokenizers and RL interfaces are in separate YAML (`configs/interfaces.yaml`) but not provided. | Misconfigured overrides may produce silent type conversions (strings instead of numbers). Absent sweeps hamper hyper‑parameter exploration. | Provide `configs/interfaces.yaml` with default component mappings. Add Hydra job logging to `.codex/hydra_last`. Add instructions/tests for multirun sweeps. | Revert by removing new config files. Hydra preserves last configuration so previous runs remain unaffected. |
| **Evaluation & metrics** (validation loops, metrics API, NDJSON/CSV logging) | **Implemented** | `codex_ml/eval/eval_runner.py` loads datasets and metrics, computes metrics with optional bootstrap CI and writes NDJSON/CSV logs[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/eval/eval_runner.py#L49-L108). `codex_ml/eval/datasets.py` loads small datasets or HuggingFace datasets[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/eval/datasets.py#L39-L62). `codex_ml/metrics/registry.py` registers common metrics including perplexity, exact match, F1, dist‑k, BLEU, ROUGE and chrF[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/metrics/registry.py#L65-L100)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/metrics/registry.py#L171-L195). | Only simple example datasets and metrics are available; there is no support for generation tasks (e.g., sampling from trained models). The evaluation runner treats predictions as identical to inputs (toy copy tasks). No integration with HF Trainer evaluation; metrics logging is separate. | Without evaluation on generated completions, metrics do not reflect model performance. Bootstrapping may be misused if predictions are non‑numeric. | (i) Integrate evaluation with the training loop to compute perplexity and accuracy on validation sets. (ii) Add dataset loader to read `metrics.ndjson` produced by HF Trainer. (iii) Provide generation pipeline to feed a model and compute metrics on outputs. | Provide fallback evaluation (as currently) if generation pipeline fails. Revert by disabling new evaluation functions; keep existing metrics unaffected. |
| **Logging & monitoring** (TensorBoard/W&B/MLflow, system metrics via psutil/NVML) | **Partially implemented** | HF Trainer logs to NDJSON via `training/engine_hf_trainer.py`. `codex_utils/ndjson.py` writes logs to file[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/codex_utils/ndjson.py#L8-L21). Configs toggle mlflow/wandb offline modes[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/tracking/base.yaml#L1-L6). Logging to session database is provided via `codex/logging/session_logger.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/logging/session_logger.py#L1-L18)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/logging/session_logger.py#L96-L135). | No integration with TensorBoard or W&B; system metrics (CPU/GPU utilization) are not recorded. Logging is mostly file‑based; there is no streaming/monitoring UI. | Lack of monitoring hinders tracking training progress and resource utilisation. | (i) Add optional tensorboard writer and mlflow logger in training engine; (ii) import psutil/nvidia‑smi to log memory and GPU metrics at intervals; (iii) update config to enable/disable these features. | Wrap logging initialisation behind config flags; revert by disabling flags or not installing psutil; remove additional dependencies if necessary. |
| **Checkpointing & resume** (weights, optimizer state, scheduler, RNG, best‑k retention) | **Implemented** | HF Trainer automatically saves and loads checkpoints. `training/data_utils.py` caches dataset splits and caches dataset shards. RNG state capture is available via `codex_utils/repro.py` with `save_rng` and `load_rng` functions[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/codex_utils/repro.py#L33-L59). Checkpoints embed environment summary and git commit. | There is no explicit `CheckpointManager` class; best‑k retention or early‑stopping checkpoints are not implemented. Resume from checkpoint is tested but with limited coverage (gradient accumulation/resume xfail). | Without best‑k retention, training may keep only last checkpoint; early stopping may not work. Improper resume can lead to inconsistent RNG states. | (i) Add simple `CheckpointManager` to track top‑k checkpoints based on evaluation metric; (ii) integrate early stopping callback in HF Trainer; (iii) test resume from checkpoint including RNG restoration. | Provide a config flag to disable top‑k retention; fallback to existing HF Trainer behaviour. Revert by removing new manager and tests. |
| **Data handling** (dataset splits, deterministic shuffling, caching) | **Implemented** | `training/data_utils.py` implements deterministic `split_dataset` and `split_texts` with optional caching[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/training/data_utils.py#L45-L75)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/training/data_utils.py#L177-L217); `load_cached` and `cache_dataset` read/write NPZ shards[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/training/data_utils.py#L270-L315). `ingestion/utils.py` offers encoding detection and deterministic shuffle[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/ingestion/utils.py#L118-L188). | No built‑in redaction filters (although docs mention optional safety filter). Streaming dataset loading is limited to text‑files and glob patterns. Data schema (input/target fields) is handled only by evaluation datasets. | Unexpected file encodings or large files may lead to memory errors. Without safety filtering, sensitive content may appear in training data. | (i) Expose `safety_filter_enabled` and `cache_dataset` flags in configs and integrate them into data pipeline; (ii) add tests for encoding detection and caching; (iii) implement dataset size validation to avoid huge memory consumption. | Keep current ingestion path as fallback; revert by disabling new safety filter and caching flags. |
| **Security & safety** (dependency locking, secrets scanning, prompt safety) | **Partially implemented** | Dev dependencies include `bandit`, `semgrep`, `detect-secrets` (inserted by codex scripts). `services/api/main.py` masks sequences resembling API keys in responses[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/services/api/main.py#L76-L82). Tokenization can filter sensitive content if extended with safety filters. | No automated scanning runs in offline CI (tools exist but not integrated). External API keys or secrets could leak in logs. Prompt safety/prompt injection defences are absent. | Inference service could echo secrets; training data may contain sensitive information. Lack of scanning may allow vulnerable code. | (i) Add pre‑commit hooks to run bandit/semgrep/detect‑secrets locally; (ii) integrate `codex_ml/safety/filters.py` (if exists) into ingestion pipeline; (iii) sanitize logs and evaluation outputs. | Pre‑commit hooks can be disabled via config; revert by removing hooks and filters if they cause false positives. Provide fallback logging that masks secrets by default. |
| **Internal CI/Test** (pytest targets, tox/nox local gates, coverage enforcement) | **Implemented (local)** | `noxfile.py` defines sessions for linting, tests, type checking; `tests/` cover configuration loading, HF trainer, dataset utilities, and interface contracts. README emphasises running pre‑commit and nox locally[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L17-L84). | Missing tests for some modules (ingestion, FastAPI service, LoRA integration, RL interfaces). RLHF stubs are untested. Code coverage thresholds are not enforced. | Undetected bugs in untested areas may reach production. | (i) Add tests for ingestion utilities, API endpoints, LoRA application, evaluation runner, RL interfaces. (ii) Configure a coverage threshold (e.g., 80%) and enforce via `pytest --cov-fail-under`. | Coverage thresholds can be lowered if causing frequent failures; disable new tests by marking them optional. Revert by removing the strict coverage flag. |
| **Deployment** (packaging, CLI entry points, Docker infra) | **Partially implemented** | Service under `services/api/main.py` and CLI `codex_ml/cli/main.py` provide entry points; there is a basic Makefile and `noxfile.py` for local runs. `codex_script.py` hints at adding packaging and Helm stubs. | No `setup.py` or `pyproject.toml` to build a package; Dockerfile is absent; deployment scripts (Helm, K8s) are stubs. | Manual environment setup; inconsistent dependencies across machines. | (i) Add a `pyproject.toml` specifying dependencies and console_scripts entry points; (ii) create a simple Dockerfile with pinned base image and GPU checks; (iii) document how to run the FastAPI service. | Keep existing environment for development; revert by not installing packaging metadata and discarding Dockerfile. Provide manual instructions in README. |
| **Documentation & examples** (README, quickstarts, diagrams, notebooks) | **Implemented** | README provides high‑level instructions and a dataset registry. Docs folder contains module‑level guides (data handling, model registry, evaluation runner)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/data_handling.md#L1-L34)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/model_registry.md#L1-L38)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/evaluation_runner.md#L1-L11) and reproducibility notes[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/repro.md#L1-L14). | Missing quick‑start notebooks or end‑to‑end examples; no architecture diagrams. Some docs reference non‑existent scripts (functional training loop, RLHF pipeline). | Users may struggle to set up or understand pipeline. | (i) Write a tutorial notebook demonstrating tokenization, training, evaluation and logging; (ii) add architecture diagram showing modules and data flow; (iii) update docs when new features (LoRA, RLHF) are implemented. | Notebooks can be optional; if causing confusion they can be removed. Keep high‑level docs consistent with implemented features. |
| **Experiment tracking** (MLflow local tracking, W&B offline mode) | **Partially implemented** | Configs allow enabling mlflow and wandb in offline mode[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/configs/tracking/base.yaml#L1-L6); `utils/trackers.py` initialises them with offline defaults[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/utils/trackers.py#L8-L29). | Implementation to log metrics and hyper‑parameters to mlflow/wandb is absent from the training engine. MLflow experiment names and artifact URIs are not configured. | Without proper logging, experiment reproducibility and comparison become difficult. | (i) In `training/engine_hf_trainer.py`, call `mlflow.start_run()` and `wandb.init()` when enabled; log parameters, metrics and model artifacts. Use local directories for offline runs. | Provide toggles in config to disable external trackers; revert by wrapping mlflow and wandb initialisation behind try/except and config flags. Remove additional imports if dependencies cause issues. |
| **Extensibility** (pluggable components, registry patterns) | **Implemented** | `codex_ml/interfaces/registry.py` registers tokenizers, reward models, RL agents and loads them from configuration or environment variables[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/interfaces/registry.py#L61-L88). `peft_adapter.py` is designed for optional LoRA integration[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/peft/peft_adapter.py#L1-L138). The evaluation runner and metrics registry use decorators for easy extension[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/metrics/registry.py#L65-L100). | RLHF and RL agent implementations are stubs; plugin loading is not demonstrated; `configs/interfaces.yaml` is missing. | Developers may misconfigure components or rely on unimplemented interfaces. | (i) Provide a default `configs/interfaces.yaml` mapping to the built‑in HFTokenizer and LengthRewardModel; (ii) add examples showing how to implement and register custom components; (iii) implement at least one RL agent for demonstration. | Expose environment variables `CODEX_*` for overrides; revert by deleting new config and leaving registry usage optional. |

3 High‑signal findings
----------------------
1. **Incomplete stubs** – Several modules (e.g. `_fix_pool` in CLI, RLHF reward model and trainer) are declared but never implemented. These stubs block functionality such as parallel data loading and RL training.
2. **LoRA integration is fragile** – Although a LoRA adapter exists, the training engine does not guarantee that LoRA parameters are applied; there are no tests verifying LoRA correctness or fallback behaviours.
3. **Evaluation is trivial** – The evaluation runner currently computes metrics on static example datasets rather than on model outputs. There is no integration between evaluation and the training pipeline, limiting meaningful validation.
4. **Limited model registry** – Only `MiniLM` and a generic HF model are registered. No codex‑style architectures (e.g. GPT‑style decoders) are supported out of the box.
5. **Configuration fragmentation** – Some settings (interfaces, LoRA, safety filters) are referenced in docs but missing from config files. Hydra sweeps and multiruns are unsupported, limiting hyper‑parameter exploration.
6. **Monitoring is basic** – Logging is limited to NDJSON; there is no TensorBoard, W&B or MLflow integration to track experiments. System metrics (CPU/GPU usage) are not recorded.
7. **Checkpoint management** – HF Trainer saves checkpoints but there is no higher‑level retention policy or early‑stopping logic. Resume tests are incomplete.
8. **Security scanning is optional** – Tools like Bandit, Semgrep and detect‑secrets are listed but not integrated into the local CI sessions; prompt safety filters are absent.
9. **Deployment packaging missing** – There is no `pyproject.toml` or Dockerfile, making distribution difficult. FastAPI service is a simple echo server with minimal security controls.
10. **Incomplete test coverage** – Several modules (ingestion, LoRA, API service, evaluation, RL interfaces) lack tests. Some existing tests are skipped or xfailed, indicating unstable functionality.
11. **Reproducibility improvements** – Utilities exist for seeds and environment capture but they are not automatically used in training scripts. Determinism is optional and not enforced.
12. **Documentation drift** – Docs reference non‑existent modules (functional training loop, RLHF pipeline) and lack quick‑start examples.
13. **Internal interfaces** – The pluggable interface registry is powerful but has no default configuration; environment variables must be set manually or via missing `configs/interfaces.yaml`.
14. **API service is minimal** – The FastAPI app returns echoed prompts and dummy metrics; concurrency, authentication, prompt filtering and logging are not production‑ready.
15. **Tools add many files** – `codex_script.py` and `apply_stack_polish.py` inject numerous sentinel blocks (dev requirements, GPU scripts, adapters, tests) into the repo, but they are not invoked by default. This complicates codebase maintenance.

4 Atomic diffs
--------------
Below are example diffs illustrating minimal, reviewable changes that address some key gaps. Each diff includes rationale, risk, rollback instructions and associated tests/docs. These are proposed as separate pull requests to minimise review complexity.

### Diff A – implement `_fix_pool()` stub in `src/codex/cli.py`
**Why:** The CLI defines a `_fix_pool()` function that is never implemented but could provide CPU parallelism or concurrency control. Leaving this stub may confuse users and triggers `NotImplementedError` if accidentally called.

**Patch:**
```diff
*** Begin Patch ***
Update File: src/codex/cli.py
@@
-def _fix_pool() -> None:
- """TODO: fix tokenization parallelism pool"""
- raise NotImplementedError("_fix_pool is not implemented yet")
+def _fix_pool(max_workers: int | None = None) -> None:
+ """Configure a process/thread pool for tokenization and data loading.
+
+ When ``max_workers`` is provided the global concurrent.futures
+ executor is re‑initialised with the given number of workers.
+ This helps avoid errors when ``multiprocessing.Pool`` is implicitly
+ created by downstream libraries (e.g. ``transformers``) on
+ platforms where forking is unsupported. If ``max_workers`` is
+ ``None``, the default executor is preserved. The function is a
+ no‑op on Python implementations that do not expose
+ ``concurrent.futures.thread._threads_queues`` (safe import).
+ """
+ try:
+ import concurrent.futures as _cf # pragma: no cover
+
+ if max_workers is not None:
+ # Shutdown any existing executor to avoid dangling threads
+ executor = getattr(_cf, "_executor", None)
+ if executor is not None:
+ executor.shutdown(wait=False)
+ # Create a new thread pool with the requested size
+ _cf._executor = _cf.ThreadPoolExecutor(max_workers=max_workers)
+ except Exception:
+ # Best‑effort fallback: ignore if the API is unavailable
+ pass
*** End Patch ***
End Patch
```

**Risk:** Modifying the global thread pool may affect downstream libraries unexpectedly; using internal attributes such as `_executor` relies on CPython implementation details. To mitigate, the patch catches exceptions and performs no action on unsupported platforms.

**Rollback:** Remove the body of `_fix_pool` and restore the original `NotImplementedError`. Alternatively, guard the call behind a CLI flag so users can opt‑in.

**Tests/docs:** Add a unit test under `tests/test_cli.py` verifying that `_fix_pool()` executes without raising and that subsequent calls to `concurrent.futures.ThreadPoolExecutor()` produce an executor of the configured size. Document usage in the CLI help text.

### Diff B – integrate LoRA configuration into HF training engine
**Why:** LoRA parameters exist in configs but are not passed into the training engine. Users cannot enable LoRA from the CLI.

**Patch:**
```diff
*** Begin Patch ***
Update File: training/engine_hf_trainer.py
@@
- model = get_model(cfg.model.name, cfg.model)
+ # Apply LoRA configuration (if enabled) via model registry
+ model = get_model(cfg.model.name, cfg.model)
@@
- # Prepare HuggingFace Trainer and data collator
- tokenizer = AutoTokenizer.from_pretrained(cfg.tokenizer.name, use_fast=True)
- # Build Trainer arguments from Hydra config
- training_args = load_training_arguments(cfg.training_cfg_path, cfg.output_dir, resume)
+ # Prepare HuggingFace Trainer and data collator
+ tokenizer = AutoTokenizer.from_pretrained(cfg.tokenizer.name, use_fast=True)
+ # Build Trainer arguments from Hydra config
+ training_args = load_training_arguments(cfg.training_cfg_path, cfg.output_dir, resume)
+
+ # If LoRA is enabled ensure gradient accumulation is at least 1 (PEFT requires full
+ # gradients for adapter layers). Warn the user if conflicting settings are detected.
+ if cfg.model.lora.enabled and training_args.gradient_accumulation_steps != 1:
+ logger.warning(
+ "LoRA adapters are enabled but gradient_accumulation_steps=%s; setting to 1",
+ training_args.gradient_accumulation_steps,
+ )
+ training_args.gradient_accumulation_steps = 1
 # Construct Trainer
*** End Patch ***
End Patch
```

**Risk:** Forcing gradient accumulation to 1 when LoRA is enabled may slow training if users wanted accumulation. It ensures LoRA layers receive full gradients, but may not be necessary for all adapter implementations. To mitigate, warn rather than force the value.

**Rollback:** Remove the LoRA warning block. LoRA will still apply but gradient accumulation may lead to slower convergence; revert if tests fail.

**Tests/docs:** Extend `tests/test_engine_hf_trainer.py` to parameterise LoRA enabled/disabled; assert that LoRA parameters appear in the model (`hasattr(model, 'peft_config')`) when enabled, and that gradient accumulation is adjusted accordingly. Document LoRA usage in `docs/modules/model_registry.md`.

### Diff C – add minimal RL reward model and agent implementations
**Why:** RL interfaces are defined but no concrete implementation exists. Providing simple examples encourages extensibility and allows tests to run.

**Patch:**
```diff
*** Begin Patch ***
Add File: src/codex_ml/rl/simple_agent.py
+from __future__ import annotations
+
+from typing import Any, Mapping
+
+from codex_ml.interfaces.rl import RLAgent
+
+
+class RandomAgent(RLAgent):
+ """A dummy RL agent that returns a constant action.
+
+ This agent is intended for tests and demonstrations. It stores no
+ parameters and always returns action ``0`` when asked to act. The
+ `update` method returns a loss of zero and `save`/`load` methods
+ write/read a marker file.
+ """
+
+ def act(self, state: Any) -> Any:
+ return 0
+
+ def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:
+ # No learning occurs
+ return {"loss": 0.0}
+
+ def save(self, path: str) -> None:
+ with open(path, "w", encoding="utf-8") as fh:
+ fh.write("RANDOM_AGENT")
+
+ def load(self, path: str) -> None:
+ with open(path, "r", encoding="utf-8") as fh:
+ fh.read()
*** End Patch ***
End Patch
```
```diff
*** Begin Patch ***
Update File: configs/interfaces.yaml (new)
+tokenizer:
+ path: codex_ml.interfaces.tokenizer:HFTokenizer
+ kwargs:
+ name_or_path: bert-base-uncased
+reward_model:
+ path: codex_ml.reward_models.simple:LengthRewardModel
+rl_agent:
+ path: codex_ml.rl.simple_agent:RandomAgent
*** End Patch ***
End Patch
```

**Risk:** Adding a new file `configs/interfaces.yaml` may override user‑supplied environment variables; ensure the registry respects existing variables. The `RandomAgent` is a trivial implementation that does not perform real RL, so it should not be used in production.

**Rollback:** Delete the added files and revert changes to the registry. Environment variables will again control component selection. Tests referencing `RandomAgent` should be skipped.

**Tests/docs:** Update `tests/test_interfaces_compat.py` to set `CODEX_RL_PATH=codex_ml.rl.simple_agent:RandomAgent` and verify that `act()`, `update()`, `save()` and `load()` work. Document the availability of the dummy agent and reward model in `docs/architecture/interfaces.md`.

### Diff D – implement environment capture and determinism at training start
**Why:** The reproducibility utilities exist but are not automatically invoked. Capturing seeds and environment info improves experiment reproducibility.

**Patch:**
```diff
*** Begin Patch ***
Update File: training/engine_hf_trainer.py
@@
- # Prepare HuggingFace Trainer and data collator
- tokenizer = AutoTokenizer.from_pretrained(cfg.tokenizer.name, use_fast=True)
- # Build Trainer arguments from Hydra config
- training_args = load_training_arguments(cfg.training_cfg_path, cfg.output_dir, resume)
+ # Ensure reproducibility: set seeds and capture environment info
+ from codex_utils import repro
+ repro.set_seed(int(cfg.training.seed))
+ repro.log_env_info(cfg.output_dir)
+
+ # Prepare HuggingFace Trainer and data collator
+ tokenizer = AutoTokenizer.from_pretrained(cfg.tokenizer.name, use_fast=True)
+ # Build Trainer arguments from Hydra config
+ training_args = load_training_arguments(cfg.training_cfg_path, cfg.output_dir, resume)
*** End Patch ***
End Patch
```

**Risk:** Automatically seeding may surprise users expecting random initialisation; environment capture writes a JSON file to `output_dir`, which may clutter logs. Provide a config flag to disable this behaviour if needed.

**Rollback:** Remove the call to `repro.set_seed` and `log_env_info`. Provide instructions for users to call these functions manually in scripts.

**Tests/docs:** Add a test ensuring that `run_hf_trainer` writes `env.json` containing git commit and package versions when reproducibility is enabled. Update `docs/repro.md` to mention automatic environment capture.

5 Local tests & gates
---------------------
* **Test commands:**
```bash
# run full test suite with coverage
nox -s tests
# or directly
pytest --cov=src --cov=training --cov-report=term-missing --cov-fail-under=75
# run style checks
nox -s lint
# run mypy type checks
nox -s typecheck
```

* **ML test score mapping:**

| Test category (ML Test Score) | Current tests | Proposed additions |
| --- | --- | --- |
| **Data tests** (validate dataset schemas, splits, caching, redaction) | Deterministic splits tested via `training/data_utils.py` functions. | Add tests verifying ingestion encoding detection, safety filtering and caching logic; ensure seeds produce identical splits across runs. |
| **Model tests** (model correctness, overfitting, numerical stability) | HF trainer tests ensure metrics file is produced and LoRA/resume flags are accepted[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tests/test_engine_hf_trainer.py#L11-L27). | Add tests for LoRA application, dtype/device placement, RL agent output consistency, perplexity computation and evaluation on small datasets. |
| **Infrastructure tests** (configuration, reproducibility, logging) | `tests/test_config_loading.py` tests config loader fallback[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tests/training/test_config_loading.py#L1-L87); `test_interfaces_compat.py` verifies interface contracts[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tests/test_interfaces_compat.py#L1-L115). | Add tests for environment capture, mlflow/wandb initialisation, logging of system metrics, API endpoints and pre‑commit hooks. |
| **Regression tests** (preventing bugs in future changes) | None yet. | Create golden output fixtures for evaluation metrics and dataset splits; assert that new commits do not change them unless intentionally updated. |
| **Performance tests** (time/memory footprints, throughput) | None. | Add benchmarks for training steps per second, memory usage and evaluation runtime on small models; integrate with pytest‑benchmark. |

6 Reproducibility checklist
---------------------------

| Item | Status / actions |
| --- | --- |
| **Seed control** | Utilities in `codex_utils/repro.py` set Python/NumPy/PyTorch seeds[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/determinism.py#L33-L89); config `training/base.yaml` includes a `seed` field. However, seeding is not automatically invoked in `run_hf_trainer`. **Action:** call `repro.set_seed(cfg.training.seed)` at the start of training (see Diff D). |
| **Deterministic algorithms** | `enable_determinism()` (via `determinism.py`) forces deterministic algorithms and sets number of threads[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/determinism.py#L33-L89). `codex_script.py` can enable determinism via environment variables. **Action:** expose a config flag `deterministic` and call `enable_determinism` when set. |
| **Environment capture** | `repro.log_env_info()` logs git commit, package versions and system information[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/codex_utils/repro.py#L73-L115). **Action:** automatically write `env.json` into the output directory at each run (see Diff D). |
| **Dependency locking** | `.codex/release/PINNED_SHAS.md` pins certain upstream dependencies; `codex_script.py` writes dev/run requirements. There is no `requirements.txt` or `poetry.lock`. **Action:** create a `requirements.lock` file capturing `pip freeze` and instruct users to install from it. |
| **Dataset versioning** | `split_dataset` caches splits with checksums[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/training/data_utils.py#L45-L75); evaluation datasets embed preset data. No dataset registry beyond docs. **Action:** store dataset version/URL in configs and log dataset hash in environment info. |
| **Checkpoints** | HF Trainer saves checkpoints; RNG state can be saved via `save_rng`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/codex_utils/repro.py#L33-L59). **Action:** ensure RNG state is saved alongside checkpoints and reloaded when resuming. |
| **Hardware/software** | No Dockerfile or conda environment; reproducibility depends on manual environment. **Action:** provide a `Dockerfile` with pinned CUDA/Python versions and note OS dependencies in docs. |
| **Results determinism** | Without setting deterministic flags, results may vary. **Action:** run tests multiple times to ensure stable metrics; log random seeds and environment info. |

Missing items are flagged and addressed in the proposed patch plans.

7 Deferred items
----------------
Some features require significant effort or unclear ownership and are therefore deferred:
1. **Full RLHF pipeline** – Implementing a reinforcement‑learning‑from‑human‑feedback training loop requires designing reward models, policy networks and training algorithms (PPO, etc.). This is beyond the scope of this audit. **Rationale:** complexity and lack of clear product requirements. **Future plan:** stub out RLHF trainers with proper ABCs and plan integration when RLHF becomes a priority.
2. **Custom functional training loop** – The README references a functional training loop but none exists. Designing and testing a custom PyTorch loop with streaming, gradient accumulation and advanced schedules will take time. **Rationale:** HF Trainer suffices for now; custom loop may duplicate features. **Future plan:** evaluate need after initial experiments; if required, port the current HF logic into a functional loop with more flexibility.
3. **Real‑time monitoring and dashboards** – Integrating dashboards (e.g., Grafana, Prometheus) for training metrics and system monitoring would provide production‑grade observability. **Rationale:** additional complexity and operational overhead. **Future plan:** investigate once training scales to multi‑GPU or distributed clusters.
4. **Secure API gateway** – The FastAPI service currently accepts unauthenticated requests by default. Building a full‑fledged API gateway with authentication, rate limiting, logging and secret management will require additional infrastructure (e.g., Kong, Envoy). **Future plan:** revisit when the service is exposed publicly.
5. **Auto‑tuning hyper‑parameters** – Hydra sweeps and Bayesian optimisation could automate search. **Rationale:** lower priority until baseline training is stable. **Future plan:** after establishing a baseline, add Hydra multirun and `optuna` integration.

8 Error capture block example
-----------------------------
When analysis steps fail, capture the error in the prescribed format. Example:
```vbnet
Question for ChatGPT @codex 2025‑09‑14T10:00Z: While performing [STEP_3:Search & Mapping], encountered the following error: FileNotFoundError: Config file 'configs/interfaces.yaml' not found Context: Attempting to load RL interface configuration in `apply_config()` for tests. What are the possible causes, and how can this be resolved while preserving intended functionality?
```
This log would be appended to `.codex/errors.ndjson` and printed to stderr. Possible causes include missing file, incorrect path or mis‑spelled file name. Resolution could involve creating the file (as shown in Diff C) or setting the environment variable `CODEX_INTERFACES_CFG` to a custom path.

9 Codex‑ready task sequence template
------------------------------------
The YAML below translates the high‑signal findings and atomic diffs into a structured sequence of tasks for ChatGPT Codex. It instructs Codex to explore modules, construct missing pieces, perform best‑effort implementations and prune tasks with rationale when impossible.

```yaml
**Codex-ready Task Sequence**
1. **Preparation**
 - Set working directory to repository root.
 - Read `README.md`, `configs/`, `codex_ml/` and `training/` to understand current features.
 - Initialise a change log (`.codex/change_log.md`) and error log (`.codex/errors.ndjson`).
 - Export environment variables for deterministic runs (e.g., `CODEX_DETERMINISM=1`).
2. **Search & Mapping**
 - Locate stubs or missing implementations (`_fix_pool`, RLHF classes, absent configs`).
 - Map existing modules to required capabilities (e.g. `HFTokenizer` for tokenization, `apply_lora` for PEFT hooks`).
 - Identify configuration gaps (e.g., missing `configs/interfaces.yaml`).
3. **Best‑Effort Construction**
 - For each gap:
  1. Create or modify files to implement the minimal required functionality. Examples:
   - Implement `_fix_pool(max_workers)` in `src/codex/cli.py` (see Diff A).
   - Add LoRA handling in `training/engine_hf_trainer.py` (Diff B) and test cases.
   - Provide a dummy RL agent (`RandomAgent`) and interfaces config (Diff C).
   - Automatically capture seeds and environment info at training start (Diff D).
  2. Write or update tests (`pytest`) ensuring new functions behave as expected.
  3. Update documentation and examples to reflect new features.
4. **Controlled Pruning**
 - If a requested feature lacks sufficient context or is infeasible (e.g., full RLHF pipeline), record this in a deferred items section.
 - Provide a rationale for pruning, referencing complexity or missing dependencies.
5. **Error Capture**
 - Wrap potentially failing operations in `try/except` blocks.
 - On error, call the `_error_capture` function (or equivalent) to log the error with step number, message and context using the specified format.
6. **Finalisation**
 - Run `pytest` and `nox` sessions to ensure all tests pass locally without network access.
 - Generate updated documentation (Markdown or notebooks) describing the changes.
 - Append entries to `.codex/change_log.md` summarising each change with rationale and preview.
 - Save results to `.codex/status/_codex_status_update-<date>.md` for future reference.
```

### Example tasks for Codex to action
Below are concrete examples of tasks (expanded from high‑signal findings) that Codex can execute sequentially. Each task should be treated as an independent execution block following the above structure.

```yaml
**Codex-ready Task Sequence**
::: # Example Suggested Task Prompt 1
Implement the `_fix_pool(max_workers)` function in `src/codex/cli.py` to configure a thread pool for tokenization. Ensure it gracefully handles missing modules and does not crash on unsupported platforms. Write a corresponding test verifying the executor is created and document the feature in the CLI help.
:::
::: # Example Suggested Task Prompt 2
Add LoRA integration to the HF training engine: modify `training/engine_hf_trainer.py` to apply LoRA parameters and warn users when gradient accumulation conflicts with LoRA. Update tests to cover the new behaviour and extend the model registry documentation.
:::
::: # Example Suggested Task Prompt 3
Create a minimal RL agent implementation (`RandomAgent`) in `codex_ml/rl/simple_agent.py` and a default `configs/interfaces.yaml` mapping to built‑in components. Update interface tests to use this agent, and document how to register custom components.
:::
```
These tasks adhere to the sequential phases and include error capture, testing and documentation requirements. Codex should execute each task until completion or prune with justification.
