# _codex_: Status Update (2025-09-15)
===================================

This audit inspects the **Codex Environment** repository for Ubuntu and evaluates its maturity for modular, reproducible and production-ready machine-learning systems. The analysis traverses all code, scripts, docs and tests (via the API) and identifies missing or incomplete areas, risks and quick-win fixes. Citations refer to lines from the repository.

1. Repo map
-----------

**Top-level structure.** The repository is organised into several major directories:

| Path | Description |
| --- | --- |
| `src/codex_ml/` | Core implementation: tokenizers, models, training engine, checkpointing, monitoring, safety, CLI utilities and helpers. |
| `src/codex/` | Chat session logging and telemetry used by Codex (e.g., `session_logger.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/logging/session_logger.py#L1-L137)). |
| `training/` | HuggingFace Trainer interface (`engine_hf_trainer.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/training/engine_hf_trainer.py#L1-L23)). |
| `docs/` | Documentation modules (`modules/data_handling.md`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/data_handling.md#L10-L28), `modules/training_engine.md`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/training_engine.md#L2-L17), `repro.md`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/repro.md#L1-L13), `ops/experiment_tracking.md`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/ops/experiment_tracking.md#L1-L64)). |
| `tools/` | One-off scripts, e.g. moving functional training into modular layout (`package_functional_training.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tools/package_functional_training.py#L1-L42)). |
| `tests/` | Pytest suite covering logging, DB utilities etc. |
| `.codex/` | Inventory and audit artefacts; includes `inventory.tsv` enumerating every file[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/.codex/inventory.tsv#L1-L95). |
| `noxfile.py`, `pytest.ini` | Local CI/test orchestration; used to run offline tests. |
| `README.md` | High-level overview of goals, setup instructions and reproducibility expectations[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L1-L32)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L68-L93). |

**Stubs and unimplemented areas.** The traversal found multiple incomplete or placeholder sections:

* **Missing YAML configurations.** Code references `configs/training/base.yaml`, `configs/data/base.yaml` and `configs/tokenization/base.yaml` for Hydra but those files are not present, forcing fallback defaults[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). The absence of these config files is a major gap.
* **Unimplemented CLI commands.** The `codex_cli.py` defines commands like `repo_map` and `evaluate` without bodies[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/codex_cli.py#L50-L59). The training command calls `run_custom_trainer`, which is undefined.
* **Documentation stubs.** Some docs reference diagrams and examples that are not included (e.g., data handling docs mention configuration keys for dataset caching[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/data_handling.md#L10-L28), but no config samples are provided).
* **Stubbed or unreachable code.** `run_functional_training` in `src/codex/training.py` expects a `--use_deeplearning` flag and LoRA/PEFT hooks but the CLI does not expose these options. The HuggingFace trainer wrapper is present but not invoked through the CLI.

2. Capability audit table
-------------------------

The table below assesses each capability area against the following axes:

* **Status** – `Implemented`, `Partially Implemented`, `Stubbed` or `Missing`.
* **Existing artefacts** – modules/classes/functions/configs providing functionality.
* **Gaps** – missing pieces preventing full functionality or reproducibility.
* **Risks** – potential runtime or production issues if deployed as-is.
* **Minimal patch plan** – small, reviewable diffs and tests to implement or fix the feature.
* **Rollback plan** – how to revert the change safely if problems arise.

| Capability | Status | Existing artefacts (citations) | Gaps / what is missing | Risks in production | Minimal patch plan | Rollback plan |
| --- | --- | --- | --- | --- | --- | --- |
| **Tokenization** | **Partially Implemented** | HuggingFace and SentencePiece adapters: `HFTokenizerAdapter` implements load/encode/decode and adds special tokens[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/tokenization/hf_tokenizer.py#L1-L144); `sentencepiece_adapter.py` trains/loads sentencepiece models[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/tokenization/sentencepiece_adapter.py#L1-L111); `tokenization/__init__.py` exposes `load_tokenizer` and constants[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/tokenization/__init__.py#L1-L84); training pipeline in `train_tokenizer.py` with dataclass config and Hydra integration[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/tokenization/train_tokenizer.py#L39-L143). | No YAML config for tokeniser training (`configs/tokenization/base.yaml`); CLI commands for tokenisation are not exposed in `codex_cli.py`; tests for encoding/decoding and special token handling are missing; caching manifest not validated. | Without default configs, users must specify all hyper-parameters manually; CLI cannot train or test tokenisers; edge-cases like unknown tokens may behave inconsistently. | (1) Add `configs/tokenization/base.yaml` providing default training hyper-parameters and dataset paths. (2) Expose `tokenization.cli` commands through `codex_cli.py`. (3) Write pytest to ensure encode/decode invertibility and correct padding. | Patch is additive; rollback involves deleting the new config file and reverting CLI registration; tests can be removed if issues arise. |
| **ChatGPT Codex modelling** | **Partially Implemented** | Lightweight language model `MiniLM` with dataclass config[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/models/minilm.py#L1-L98); model registry supports loading models and applying LoRA adapters[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/models/registry.py#L19-L118); LoRA adapter with graceful fallback when `peft` is absent[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/peft/peft_adapter.py#L37-L138); `load_model_with_optional_lora` wraps model loading and LoRA integration[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/modeling/codex_model_loader.py#L39-L116). | Not a full chat model—no conversation history or system/user roles; lacks instruction-tuning; dataset not provided; no pipeline to fine-tune or serve ChatGPT. CLI `generate.py` only handles single prompt generation[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/generate.py#L13-L70). | Mismatch between “ChatGPT” label and actual capabilities; unrealistic expectations; risk of exposing unfiltered outputs due to missing safety gating. | (1) Rename the capability to “MiniLM language model” in docs to avoid confusion. (2) Implement conversation context handling (chat roles, history) and integrate safety filters. (3) Provide example datasets and training script for chat fine-tuning. | Renaming is reversible. Chat context handling can be behind a flag; revert by disabling the feature via config. |
| **Training engine** | **Partially Implemented** | Custom training loop in `src/codex/training.py` handling dataset loading, tokenisation, model instantiation, LoRA, scheduler, gradient accumulation and metrics[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/training.py#L176-L332)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/training.py#L341-L500); HuggingFace `Trainer` wrapper in `training/engine_hf_trainer.py` with support for precision, multi-GPU and LoRA[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/training/engine_hf_trainer.py#L1-L23); configuration loader with Hydra fallback[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). | CLI does not expose training engine; config YAML files missing; metrics logging partially integrated; no tests for training loop; dataset splits and shuffling partly implemented. | Without proper config and CLI integration, training cannot be executed end-to-end. Users may mis-specify hyper-parameters; non-deterministic results due to missing seeds and logging. | (1) Add missing `configs/training/base.yaml` with default hyper-parameters. (2) Implement `train` subcommand in `codex_cli.py` that invokes `run_functional_training` or HF trainer via config. (3) Write tests for single-epoch training on toy dataset verifying loss decreases. | CLI integration can be gated behind `--enable-training`; revert by disabling the flag and removing YAML file. |
| **Configuration management** | **Partially Implemented** | Hydra/OmegaConf loader to merge YAML config with CLI overrides[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82); fallback to programmatic defaults when config not found; environment variable summarisation in `provenance.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/provenance.py#L38-L89). | Missing YAML config files (`configs/training/base.yaml`, etc.); no config schema validation; Hydra sweeps not documented. | Hard-coded defaults hide hyper-parameter settings; inability to override via CLI; sweeps cannot be performed. | (1) Create minimal YAML config files for training, data and tokenisation. (2) Add `--config` flag to CLI to specify alternate YAML files. (3) Document config keys in docs. | Removal of YAML files restores fallback to defaults; config flag can be disabled. |
| **Evaluation & metrics** | **Partially Implemented** | Evaluation functions compute accuracy and perplexity on datasets in `eval/evaluator.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/eval/evaluator.py#L26-L42); CLI script `run_eval.py` loads text/ndjson/csv files, tokenises and outputs metrics[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/eval/run_eval.py#L31-L70); training loop computes metrics and logs to TensorBoard[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/training.py#L341-L500). | CLI `codex_cli.py` does not expose evaluation; evaluation only supports limited metrics; no NDJSON/CSV logging integration; metrics functions not tested; logs not summarised. | Users cannot easily evaluate models on new datasets; missing metrics hinder reproducibility; logs may not be persisted or aggregated. | (1) Add `evaluate` subcommand in CLI to call `run_eval.py`. (2) Extend `evaluator.py` to compute F1, BLEU or other relevant metrics; log results to NDJSON. (3) Write tests for evaluation on small dataset. | Keep evaluation as optional plugin; revert by removing CLI command and metrics additions. |
| **Logging & monitoring** | **Implemented** | Telemetry initialisation via `codex_logging.py` sets up TensorBoard, W&B, MLflow and GPU sampling[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/monitoring/codex_logging.py#L116-L187); asynchronous NDJSON writer ensures non-blocking logging[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/monitoring/async_writer.py#L42-L132); `session_logger.py` logs chat events to SQLite and ensures WAL journaling[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/logging/session_logger.py#L1-L137); environment summary recorded in checkpoints[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259). | Optional dependencies (MLflow, W&B) may be absent; config flags not exposed via CLI; no system metrics dashboards; logging functions not unit-tested; logs stored only locally. | Missing dependencies cause runtime import errors; silent failures in logging degrade observability; no remote monitoring. | (1) Guard all optional imports with try/except (already partially done). (2) Add CLI flags to enable TensorBoard/MLflow/W&B. (3) Provide unit tests verifying logs are written. | Logging flags can default to off; revert by disabling telemetry initialisation. |
| **Checkpointing & resume** | **Implemented** | Robust checkpointing utilities save model/optimizer/scheduler and environment summary, compute checksums and embed git commit[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259); RNG state capture ensures reproducibility; verify integrity via `verify_ckpt_integrity`. | No CLI commands to resume training; no retention of best-k checkpoints; limited test coverage; integration with training loop partly manual. | Without resume CLI, users must write code to load checkpoints; risk of silent corruption if verify step is skipped. | (1) Add `resume` option to training CLI to load last checkpoint. (2) Add test verifying that training can be paused and resumed with identical results. (3) Optionally implement best-k retention using Top-k file deletion. | The resume option can be hidden behind experimental flag; revert by disabling resume code. |
| **Data handling** | **Partially Implemented** | Utilities to read plain text, NDJSON and CSV; deterministic splits and caching with checksums in `data_utils.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/data_utils.py#L1-L143); dataset streaming; safety filtering integrated via `sanitize_prompt`. | Missing data config; caching path is fixed; no CLI for dataset preparation; dataset splits rely on order of input file; dataset class not integrated with HuggingFace datasets; no support for large or streaming datasets beyond memory. | Data ingestion may be inconsistent across runs; risk of caching unclean data; no test coverage; difficulty handling huge corpora. | (1) Add configurable data paths and split ratios in YAML config. (2) Provide CLI command for dataset preparation and caching. (3) Add tests verifying deterministic splits. | Revert by falling back to existing default behaviour; remove config if issues arise. |
| **Security & safety** | **Partially Implemented** | Safety configuration with regex patterns for secrets, PII and jailbreak detection[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sanitizers.py#L25-L61); safety filters enforce allow/block lists and can mask logits[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/filters.py#L15-L113); sandbox executes commands with resource limits and redaction[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sandbox.py#L2-L89); error logging sanitises output[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/error_log.py#L15-L51). | Safety not integrated into all pipelines; token masking not used in training loop; secret scanning not enforced in pre-commit; no test coverage; limited prompt injection detection. | Potential leakage of secrets or harmful content; sandbox may degrade performance; uncertain behaviour under adversarial prompts. | (1) Integrate safety filters into inference and training pipelines; provide gating in CLI. (2) Add pre-commit hook using `git-secrets` or similar to scan for API keys. (3) Write tests ensuring sanitisation masks secrets. | Safety integration can be feature-flagged; revert by disabling safety enforcement. |
| **Internal CI/test** | **Partially Implemented** | `noxfile.py` orchestrates linting and testing; `pytest.ini` configures tests; tests exist for session logging and DB utilities; pre-commit config ensures formatting. | No tests cover training, evaluation, tokenisation or safety; no continuous integration workflow (GitHub Actions intentionally disabled); code coverage not measured; `tox` config missing. | Undetected regressions in core ML functionality; low confidence in changes; risk of subtle bugs in training loops. | (1) Add pytest suites for tokeniser, model, training and evaluation; aim for high coverage. (2) Define `nox -s tests` session that runs tests offline. (3) Provide coverage report using `pytest-cov`. | Tests can be added gradually; revert by removing or disabling failing tests during rollout. |
| **Deployment** | **Partially Implemented** | `pyproject.toml` declares package metadata; `Dockerfile` provides base image; CLI entry points partially defined; `generate.py` offers simple generation CLI[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/generate.py#L13-L70). | No packaging to PyPI; CLI incomplete; missing `setup.cfg` for static analysis; Dockerfile not tested; no container orchestrations; no CLI for serving models as API. | Difficult to deploy to production; risk of environment drift; manual packaging steps. | (1) Complete CLI with train/evaluate commands. (2) Create `setup.py` or Poetry packaging; optionally publish to private index. (3) Provide example docker-compose to run training and inference. | Packaging changes can be versioned; revert by pinning previous release. |
| **Documentation & examples** | **Partially Implemented** | Docs in `docs/modules/` explain data handling[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/data_handling.md#L10-L28), training engine[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/training_engine.md#L2-L17), experiment tracking[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/ops/experiment_tracking.md#L1-L64), and reproducibility[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/repro.md#L1-L13); README covers environment setup and reproducibility expectations[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L1-L32). | Many docs reference missing YAML configs and examples; no diagrams; no end-to-end quickstart; test notebooks absent. | Users may misconfigure system; knowledge gap on using features; incomplete docs hamper adoption. | (1) Fill gaps in docs by adding example config files and usage examples. (2) Include diagrams of data flow and model pipeline. (3) Provide Jupyter notebooks demonstrating training and evaluation. | Documentation changes can be versioned and rolled back; maintain separate `docs` branch if necessary. |
| **Experiment tracking** | **Partially Implemented** | MLflow and W&B integration toggled via flags in `codex_logging.py`; environment summary and seeds logged in checkpoint metadata; docs for experiment tracking[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/ops/experiment_tracking.md#L1-L64). | MLflow initialisation optional and not exposed in CLI; offline tracking recommended but no example; no NDJSON/CSV metrics logs; integration tests absent. | Metrics may not be logged, hindering reproducibility; risk of mis-configured tracking. | (1) Add CLI flags to enable MLflow and specify tracking URI. (2) Persist evaluation metrics in NDJSON for offline analysis. (3) Provide example script demonstrating offline MLflow use. | Experiment tracking can remain optional; revert by disabling flags. |
| **Extensibility** | **Partially Implemented** | Model registry pattern allows new models to be registered[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/models/registry.py#L19-L118); tokeniser training uses dataclass config; safety filters configurable; plugin pattern for optional logging. | Hard-coded file paths; CLI not pluggable; no registry for data modules or trainers; missing API for extensions; some components (e.g., evaluation) not modular. | Harder to integrate new models/datasets; fragmentation; custom forks diverge. | (1) Generalise registry patterns for data loaders, trainers and evaluation metrics. (2) Use entry points (e.g., `setuptools` `entry_points`) to allow external plugins. (3) Document how to add new models or tokenisers. | Additional registry code can be hidden behind feature flags; revert by using simple Python imports. |

3. High-signal findings and quick wins
--------------------------------------

1. **Missing YAML configuration files** – The code references several Hydra YAML files that are absent (`configs/training/base.yaml`, `configs/data/base.yaml`, `configs/tokenization/base.yaml`), leading to hidden default hyper-parameters and unpredictable behaviour[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). Creating these files and documenting their fields is a high-impact, low-effort fix.
2. **Incomplete CLI** – The central command-line interface lacks implemented commands; training and evaluation must currently be invoked via internal Python functions[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/codex_cli.py#L50-L59). Exposing them through CLI subcommands would greatly improve usability.
3. **Tokeniser training pipeline lacks default config** – The tokeniser training script is powerful but requires manual parameter specification[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/tokenization/train_tokenizer.py#L39-L143). Providing a default config and hooking the pipeline into the CLI will enable reproducible tokenisation.
4. **Hydra fallback hides configuration** – Without YAML files, Hydra silently falls back to defaults[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). This can mislead users into thinking a config was loaded. Logging a warning when config files are missing would improve transparency.
5. **Limited test coverage** – Only logging and DB utilities have tests; core ML components (tokenisers, models, training, evaluation, safety) are untested. Adding targeted unit tests for these modules will increase confidence.
6. **Safety filters not integrated** – Although sanitisation and filters exist, they are not wired into generation or training loops[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sanitizers.py#L25-L61). Integrating safety gating is critical to prevent leakage of secrets or malicious outputs.
7. **No resume capability exposed** – Robust checkpointing utilities exist[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259) but there is no CLI mechanism to resume training. A `--resume` flag would leverage existing functions and improve resiliency.
8. **Lack of experiment tracking defaults** – MLflow, W&B and TensorBoard are supported in code but not configured or documented via CLI; offline experiment logging should be the default[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/monitoring/codex_logging.py#L116-L187).
9. **Ambiguity in naming (“ChatGPT” vs MiniLM)** – The repository names some modules as ChatGPT/Codex but actually implements a small Transformer model[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/models/minilm.py#L1-L98). Clarifying naming prevents over-promising and misinterpretation.
10. **Missing packaging and deployment pipeline** – There is no PyPI packaging or container orchestration; the Dockerfile is untested. Packaging the code as a Python package and providing deployment examples would accelerate adoption.
11. **No data preparation CLI** – Data loading utilities exist[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/data_utils.py#L1-L143) but there is no command to prepare or cache datasets. A `prepare-data` CLI could wrap splitting, caching and safety filtering.
12. **Lack of reproducibility enforcement** – The `set_reproducible` function exists[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/repro.py#L1-L77) but seeds are not enforced across all pipelines. Exposing a `--seed` flag and logging seeds would improve determinism.
13. **Environment provenance not surfaced** – Provenance utilities capture environment summary and pip freeze[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/provenance.py#L38-L89) but these are not surfaced in CLI or docs. Including environment info in training/evaluation logs would help reproducibility.
14. **Incomplete documentation and examples** – Many docs refer to missing examples or diagrams; updating docs to include usage examples and quickstarts is essential for user onboarding.
15. **Optional dependencies** – Many features rely on optional libraries (MLflow, W&B, Pynvml). Without proper dependency management or clear error messages, features may silently fail.
16. **No central registry for data, trainers or metrics** – Extensibility is limited due to lack of registry patterns beyond models; adopting registries for other components will simplify adding new features.
17. **Potential security risks** – Safety filters are not enforced by default, raising concerns about unfiltered outputs. Pre-commit scanning for secrets and sandboxing external calls should be enabled by default.
18. **No performance monitoring** – GPU and system metrics logging exists[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/monitoring/codex_logging.py#L116-L187) but is optional. Adding default monitoring dashboards would allow troubleshooting performance bottlenecks.
19. **Lack of LoRA configuration** – LoRA integration is implemented[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/peft/peft_adapter.py#L37-L138) but the CLI does not expose LoRA parameters or training flags. Surface these options for research experiments.
20. **Poor error handling** – Many functions raise exceptions without context. Adopting consistent error capture blocks (see §8) will aid debugging.

4. Atomic diffs (proposed patches)
----------------------------------

Below are example unified diffs that implement some of the high-impact fixes. Each diff includes rationale, risks and rollback suggestions. Patches are additive and respect the policy of not enabling cost-incurring GitHub actions (no workflow YAMLs).

### Diff 1 – Add default training YAML config

**Why:** Provide reproducible hyper-parameters and make Hydra config explicit instead of relying on silent fallback[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82).

**Patch:**

```yaml
# In a new file `configs/training/base.yaml`:
# Default training configuration for Codex ML
# This file defines hyper-parameters used by the training engine. It avoids hard-coded defaults.
seed: 42
model: minilm
learning_rate: 3e-4
batch_size: 32
max_epochs: 5
scheduler: linear
warmup_steps: 0
gradient_accumulation: 1
tensorboard: true
mlflow_enable: false
```

**Risk:** If hyper-parameters mismatch existing defaults, performance may change. YAML loading errors could break training.

**Rollback:** Delete `configs/training/base.yaml` to restore fallback defaults. Document the removal in change log.

**Tests/docs:** Create a unit test that loads the YAML via `load_config` and asserts values. Update docs to reference the new config file.

### Diff 2 – Implement training CLI subcommand

**Why:** Without a `train` command, users cannot run the training loop through the CLI[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/codex_cli.py#L50-L59).

**Patch:**

```python
# In `src/codex_ml/cli/codex_cli.py` replace the stubbed train command with:
@cli.command()
@click.option("--config", default="configs/training/base.yaml", help="Path to the Hydra YAML config")
@click.option("--resume", is_flag=True, help="Resume from last checkpoint if available")
@click.option("--seed", default=None, help="Override random seed")
def train(config: str, resume: bool, seed: Optional[int]):
    """Train a language model using the Codex training engine."""
    from codex_ml.utils.config_loader import load_config
    from codex_ml.training import run_functional_training

    cfg = load_config(config_path=config)
    if seed is not None:
        cfg.seed = int(seed)

    try:
        run_functional_training(config=cfg, resume=resume)
    except Exception as e:
        from codex_ml.utils.error_log import log_error

        log_error("train", str(e))
        raise
```

**Risk:** Introduces CLI dependencies (click) and may break for missing config files. Changing function signatures could require refactoring tests.

**Rollback:** Revert changes to `codex_cli.py`; remove new imports and options. CLI will return to stub mode.

**Tests/docs:** Add a functional test invoking `codex-cli train` on a small dataset and verifying that a checkpoint is produced. Document the command in README and training docs.

### Diff 3 – Integrate safety filters into generation

**Why:** Outputs may contain secrets or harmful content; integrate safety filters to sanitise generation[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sanitizers.py#L25-L61).

**Patch:**

```python
# In `src/codex_ml/cli/generate.py` replace the printing of the result with:
result = model.generate(**gen_kwargs)

# Apply safety sanitisation
from codex_ml.safety.sanitizers import sanitize_output, SafetyConfig

safety_cfg = SafetyConfig()
sanitized, redactions = sanitize_output(result, safety_cfg)
print(sanitized)
if redactions > 0:
    click.echo(f"[warning] {redactions} redaction(s) applied")
```

**Risk:** Sanitisation may remove legitimate content; performance overhead from regex checks. Users expecting raw output may be surprised.

**Rollback:** Add a `--no-safety` flag to disable sanitisation or revert the patch entirely.

**Tests/docs:** Write tests verifying that secret tokens are redacted. Update CLI docs to explain sanitisation and the new flag.

### Diff 4 – Add resumption flag to training

**Why:** Checkpointing utilities exist but there is no resume option[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259).

**Patch:**

```python
# In `src/codex_ml/training.py` modify `run_functional_training` signature and body:
def run_functional_training(config: DictConfig, use_deeplearning: bool = False, resume: bool = False, **kwargs):
    """Run the custom training loop.

    Args:
        config: Hydra/OmegaConf config
        use_deeplearning: whether to use the HF trainer
        resume: if True, load the last checkpoint before starting
    """
    # If resuming, attempt to load training checkpoint
    if resume:
        from codex_ml.utils.checkpointing import load_training_checkpoint

        last_ckpt = load_training_checkpoint(config.output_dir)
        if last_ckpt:
            model, optimizer, scheduler, rng_state = last_ckpt
        else:
            print("No checkpoint found; starting fresh.")
    # existing body continues
```

**Risk:** If checkpoint loading fails or mismatched hyper-parameters, training may crash. Resume may inadvertently load stale checkpoints.

**Rollback:** Remove `resume` parameter and associated code; training will always start fresh.

**Tests/docs:** Add test to pause training after a few steps, save checkpoint, then resume and verify identical loss. Document `--resume` flag in CLI docs.

### Diff 5 – Warn when configuration files are missing

**Why:** Hydra silently falls back to defaults when config files are absent[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). Emitting a warning improves transparency.

**Patch:**

```python
# In `src/codex_ml/utils/config_loader.py` replace the fallback block with:
except FileNotFoundError:
    import warnings

    warnings.warn(f"Config file {config_path} not found; using built-in defaults", UserWarning)
    return OmegaConf.create({
        "seed": 42,
        "learning_rate": 1e-3,
        "batch_size": 32,
        "max_epochs": 1,
    })
```

**Risk:** Warnings may clutter output; some users may treat warnings as errors.

**Rollback:** Remove the `warnings.warn` call; fallback remains silent. Document the removal in change log.

**Tests/docs:** Write test ensuring that a `UserWarning` is raised when config file is missing. Mention this behaviour in docs.

5. Local tests & gates
----------------------

To enforce quality before merging changes, define local offline CI using **pytest** and **nox**. These gates run in the Codex environment only (no GitHub Actions). Suggested additions:

1. **`tests/test_tokenizer.py`** – Validate that encoding followed by decoding returns the original text for HF and SentencePiece adapters. Check that unknown tokens are handled gracefully. ML Test Score: **data** (correct tokenisation) and **model** (consistency across devices).
2. **`tests/test_training_loop.py`** – Use a tiny synthetic dataset to run one epoch of training using the functional loop and the HF trainer; assert that loss decreases and that a checkpoint file is created. ML Test Score: **model** (training correctness) and **infrastructure** (checkpointing works).
3. **`tests/test_resume.py`** – Train for a few steps, save checkpoint, resume and ensure identical loss trajectory. ML Test Score: **reproducibility**.
4. **`tests/test_evaluation.py`** – Evaluate the model on a small dataset and check that accuracy/perplexity values match expected values. ML Test Score: **regression** (no silent changes in metrics).
5. **`tests/test_safety.py`** – Pass prompts containing secret patterns and verify they are redacted by `sanitize_prompt` and `sanitize_output`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sanitizers.py#L25-L61). ML Test Score: **safety**.

**Command to run tests:**

```nginx
nox -s tests
```

If `nox` is not used, a simple fallback is:

```css
pytest -q --disable-warnings
```

6. Reproducibility checklist
----------------------------

| Item | Status | Notes |
| --- | --- | --- |
| **Random seeds set** | ✗ | `set_reproducible()` seeds Python/NumPy/PyTorch and sets deterministic CuDNN[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/repro.py#L1-L77), but CLI does not expose a seed parameter and training functions do not always call it. |
| **Environment capture** | ✓/✗ | Provenance utilities record environment summary and git commit[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/provenance.py#L38-L89); checkpoints embed metadata[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259), but logs do not surface this information and CLI does not allow exporting environment snapshot. |
| **Dependency locking** | ✗ | There is no `requirements.lock` or `poetry.lock`; dependencies are not pinned, which jeopardises reproducibility. |
| **Deterministic datasets** | ✗ | Data splitting is deterministic when seeds provided[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/data_utils.py#L1-L143), but the absence of config/seed means splits may vary. |
| **Logging of hyper-parameters and results** | ✗ | Hyper-parameters are not logged systematically; MLflow/W&B integration is optional and off by default. |
| **Checkpoints include RNG state** | ✓ | Checkpointing utilities save RNG state and compute checksums[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259). |
| **Version control of code** | ✓ | Git commit hash recorded in checkpoints[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259), but it is not surfaced in logs or docs. |
| **Documentation of experiments** | ✗ | There is no central log or experiment notebook; docs do not capture training results. |

**Missing items per reproducibility best practices:**

* Provide a `requirements.txt`/`poetry.lock` to pin dependencies.
* Expose `--seed` in CLI and set reproducible seeds early in all pipelines.
* Log hyper-parameters and metrics consistently (e.g., NDJSON and TensorBoard). Use offline MLflow by default.
* Persist dataset checksums and splits within config or log; include them in environment summary.
* Capture environment snapshot and pip freeze; allow exporting it via CLI to accompany experiments.

7. Deferred items and pruning rationale
---------------------------------------

Some features remain unimplemented or out of scope. Before working on them, consider complexity, risk and value:

* **Full ChatGPT fine-tuning** – Building a chat-level dataset and fine-tuning a large language model would require significant compute and is beyond the scope of the current minimal environment. Focus on smaller language models until there is ownership for dataset curation.
* **Distributed training and multi-GPU** – The HF trainer wrapper hints at multi-GPU support, but distributed training setup is complex. Unless required, keep training to single-GPU/CPU for reproducibility and simplicity.
* **Cloud deployment and API serving** – Exposing models as web services or integrating with cloud services can be deferred. Prioritise CLI and reproducibility first.
* **Comprehensive safety classification** – Building advanced safety classifiers (e.g., toxicity detection) requires dataset access and research; rely on simple regex-based sanitisation for now.
* **Automated GitHub Actions** – The project intentionally disallows GitHub-hosted workflows. Local CI via `nox` is sufficient; avoid introducing actions that incur cost.
* **Complex hyper-parameter sweeps** – Hydra sweeps and hyper-parameter search can be deferred until base training is stable and reproducible. Document how to extend for sweeps.

8. Error capture blocks
-----------------------

When developing or running this project, if any step fails, log a research question to help future debugging. Use the following template:

```kotlin
Question for ChatGPT @codex {timestamp}: While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error: [ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

For example, if running the training CLI fails due to a missing config file, write:

```vbnet
Question for ChatGPT @codex 2025-09-15T14:00:00Z: While performing Step 3: Loading Hydra config, encountered the following error: FileNotFoundError: configs/training/base.yaml not found
Context: calling run_functional_training via codex-cli
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

These blocks should be captured in `.codex/errors.ndjson` via the existing error logger[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/error_log.py#L15-L51). Recording detailed error context and timestamp will aid in debugging and automated support.

```yaml
# _codex_: Status Update (2025-09-15)
===================================

This audit inspects the **Codex Environment** repository for Ubuntu and evaluates its maturity for modular, reproducible and production-ready machine-learning systems. The analysis traverses all code, scripts, docs and tests (via the API) and identifies missing or incomplete areas, risks and quick-win fixes. Citations refer to lines from the repository.

1. Repo map
-----------

**Top-level structure.** The repository is organised into several major directories:

| Path | Description |
| --- | --- |
| `src/codex_ml/` | Core implementation: tokenizers, models, training engine, checkpointing, monitoring, safety, CLI utilities and helpers. |
| `src/codex/` | Chat session logging and telemetry used by Codex (e.g., `session_logger.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/logging/session_logger.py#L1-L137)). |
| `training/` | HuggingFace Trainer interface (`engine_hf_trainer.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/training/engine_hf_trainer.py#L1-L23)). |
| `docs/` | Documentation modules (`modules/data_handling.md`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/data_handling.md#L10-L28), `modules/training_engine.md`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/training_engine.md#L2-L17), `repro.md`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/repro.md#L1-L13), `ops/experiment_tracking.md`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/ops/experiment_tracking.md#L1-L64)). |
| `tools/` | One-off scripts, e.g. moving functional training into modular layout (`package_functional_training.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/tools/package_functional_training.py#L1-L42)). |
| `tests/` | Pytest suite covering logging, DB utilities etc. |
| `.codex/` | Inventory and audit artefacts; includes `inventory.tsv` enumerating every file[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/.codex/inventory.tsv#L1-L95). |
| `noxfile.py`, `pytest.ini` | Local CI/test orchestration; used to run offline tests. |
| `README.md` | High-level overview of goals, setup instructions and reproducibility expectations[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L1-L32)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L68-L93). |

**Stubs and unimplemented areas.** The traversal found multiple incomplete or placeholder sections:

* **Missing YAML configurations.** Code references `configs/training/base.yaml`, `configs/data/base.yaml` and `configs/tokenization/base.yaml` for Hydra but those files are not present, forcing fallback defaults[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). The absence of these config files is a major gap.
* **Unimplemented CLI commands.** The `codex_cli.py` defines commands like `repo_map` and `evaluate` without bodies[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/codex_cli.py#L50-L59). The training command calls `run_custom_trainer`, which is undefined.
* **Documentation stubs.** Some docs reference diagrams and examples that are not included (e.g., data handling docs mention configuration keys for dataset caching[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/data_handling.md#L10-L28), but no config samples are provided).
* **Stubbed or unreachable code.** `run_functional_training` in `src/codex/training.py` expects a `--use_deeplearning` flag and LoRA/PEFT hooks but the CLI does not expose these options. The HuggingFace trainer wrapper is present but not invoked through the CLI.

2. Capability audit table
--------------------------

The table below assesses each capability area against the following axes:

* **Status** – `Implemented`, `Partially Implemented`, `Stubbed` or `Missing`.
* **Existing artefacts** – modules/classes/functions/configs providing functionality.
* **Gaps** – missing pieces preventing full functionality or reproducibility.
* **Risks** – potential runtime or production issues if deployed as-is.
* **Minimal patch plan** – small, reviewable diffs and tests to implement or fix the feature.
* **Rollback plan** – how to revert the change safely if problems arise.

| Capability | Status | Existing artefacts (citations) | Gaps / what is missing | Risks in production | Minimal patch plan | Rollback plan |
| --- | --- | --- | --- | --- | --- | --- |
| **Tokenization** | **Partially Implemented** | HuggingFace and SentencePiece adapters: `HFTokenizerAdapter` implements load/encode/decode and adds special tokens[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/tokenization/hf_tokenizer.py#L1-L144); `sentencepiece_adapter.py` trains/loads sentencepiece models[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/tokenization/sentencepiece_adapter.py#L1-L111); `tokenization/__init__.py` exposes `load_tokenizer` and constants[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/tokenization/__init__.py#L1-L84); training pipeline in `train_tokenizer.py` with dataclass config and Hydra integration[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/tokenization/train_tokenizer.py#L39-L143). | No YAML config for tokeniser training (`configs/tokenization/base.yaml`); CLI commands for tokenisation are not exposed in `codex_cli.py`; tests for encoding/decoding and special token handling are missing; caching manifest not validated. | Without default configs, users must specify all hyper-parameters manually; CLI cannot train or test tokenisers; edge-cases like unknown tokens may behave inconsistently. | (1) Add `configs/tokenization/base.yaml` providing default training hyper-parameters and dataset paths. (2) Expose `tokenization.cli` commands through `codex_cli.py`. (3) Write pytest to ensure encode/decode invertibility and correct padding. | Patch is additive; rollback involves deleting the new config file and reverting CLI registration; tests can be removed if issues arise. |
| **ChatGPT Codex modelling** | **Partially Implemented** | Lightweight language model `MiniLM` with dataclass config[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/models/minilm.py#L1-L98); model registry supports loading models and applying LoRA adapters[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/models/registry.py#L19-L118); LoRA adapter with graceful fallback when `peft` is absent[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/peft/peft_adapter.py#L37-L138); `load_model_with_optional_lora` wraps model loading and LoRA integration[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/modeling/codex_model_loader.py#L39-L116). | Not a full chat model—no conversation history or system/user roles; lacks instruction-tuning; dataset not provided; no pipeline to fine-tune or serve ChatGPT. CLI `generate.py` only handles single prompt generation[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/generate.py#L13-L70). | Mismatch between “ChatGPT” label and actual capabilities; unrealistic expectations; risk of exposing unfiltered outputs due to missing safety gating. | (1) Rename the capability to “MiniLM language model” in docs to avoid confusion. (2) Implement conversation context handling (chat roles, history) and integrate safety filters. (3) Provide example datasets and training script for chat fine-tuning. | Renaming is reversible. Chat context handling can be behind a flag; revert by disabling the feature via config. |
| **Training engine** | **Partially Implemented** | Custom training loop in `src/codex/training.py` handling dataset loading, tokenisation, model instantiation, LoRA, scheduler, gradient accumulation and metrics[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/training.py#L176-L332)[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/training.py#L341-L500); HuggingFace `Trainer` wrapper in `training/engine_hf_trainer.py` with support for precision, multi-GPU and LoRA[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/training/engine_hf_trainer.py#L1-L23); configuration loader with Hydra fallback[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). | CLI does not expose training engine; config YAML files missing; metrics logging partially integrated; no tests for training loop; dataset splits and shuffling partly implemented. | Without proper config and CLI integration, training cannot be executed end-to-end. Users may mis-specify hyper-parameters; non-deterministic results due to missing seeds and logging. | (1) Add missing `configs/training/base.yaml` with default hyper-parameters. (2) Implement `train` subcommand in `codex_cli.py` that invokes `run_functional_training` or HF trainer via config. (3) Write tests for single-epoch training on toy dataset verifying loss decreases. | CLI integration can be gated behind `--enable-training`; revert by disabling the flag and removing YAML file. |
| **Configuration management** | **Partially Implemented** | Hydra/OmegaConf loader to merge YAML config with CLI overrides[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82); fallback to programmatic defaults when config not found; environment variable summarisation in `provenance.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/provenance.py#L38-L89). | Missing YAML config files (`configs/training/base.yaml`, etc.); no config schema validation; Hydra sweeps not documented. | Hard-coded defaults hide hyper-parameter settings; inability to override via CLI; sweeps cannot be performed. | (1) Create minimal YAML config files for training, data and tokenisation. (2) Add `--config` flag to CLI to specify alternate YAML files. (3) Document config keys in docs. | Removal of YAML files restores fallback to defaults; config flag can be disabled. |
| **Evaluation & metrics** | **Partially Implemented** | Evaluation functions compute accuracy and perplexity on datasets in `eval/evaluator.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/eval/evaluator.py#L26-L42); CLI script `run_eval.py` loads text/ndjson/csv files, tokenises and outputs metrics[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/eval/run_eval.py#L31-L70); training loop computes metrics and logs to TensorBoard[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/training.py#L341-L500). | CLI `codex_cli.py` does not expose evaluation; evaluation only supports limited metrics; no NDJSON/CSV logging integration; metrics functions not tested; logs not summarised. | Users cannot easily evaluate models on new datasets; missing metrics hinder reproducibility; logs may not be persisted or aggregated. | (1) Add `evaluate` subcommand in CLI to call `run_eval.py`. (2) Extend `evaluator.py` to compute F1, BLEU or other relevant metrics; log results to NDJSON. (3) Write tests for evaluation on small dataset. | Keep evaluation as optional plugin; revert by removing CLI command and metrics additions. |
| **Logging & monitoring** | **Implemented** | Telemetry initialisation via `codex_logging.py` sets up TensorBoard, W&B, MLflow and GPU sampling[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/monitoring/codex_logging.py#L116-L187); asynchronous NDJSON writer ensures non-blocking logging[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/monitoring/async_writer.py#L42-L132); `session_logger.py` logs chat events to SQLite and ensures WAL journaling[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex/logging/session_logger.py#L1-L137); environment summary recorded in checkpoints[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259). | Optional dependencies (MLflow, W&B) may be absent; config flags not exposed via CLI; no system metrics dashboards; logging functions not unit-tested; logs stored only locally. | Missing dependencies cause runtime import errors; silent failures in logging degrade observability; no remote monitoring. | (1) Guard all optional imports with try/except (already partially done). (2) Add CLI flags to enable TensorBoard/MLflow/W&B. (3) Provide unit tests verifying logs are written. | Logging flags can default to off; revert by disabling telemetry initialisation. |
| **Checkpointing & resume** | **Implemented** | Robust checkpointing utilities save model/optimizer/scheduler and environment summary, compute checksums and embed git commit[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259); RNG state capture ensures reproducibility; verify integrity via `verify_ckpt_integrity`. | No CLI commands to resume training; no retention of best-k checkpoints; limited test coverage; integration with training loop partly manual. | Without resume CLI, users must write code to load checkpoints; risk of silent corruption if verify step is skipped. | (1) Add `resume` option to training CLI to load last checkpoint. (2) Add test verifying that training can be paused and resumed with identical results. (3) Optionally implement best-k retention using Top-k file deletion. | The resume option can be hidden behind experimental flag; revert by disabling resume code. |
| **Data handling** | **Partially Implemented** | Utilities to read plain text, NDJSON and CSV; deterministic splits and caching with checksums in `data_utils.py`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/data_utils.py#L1-L143); dataset streaming; safety filtering integrated via `sanitize_prompt`. | Missing data config; caching path is fixed; no CLI for dataset preparation; dataset splits rely on order of input file; dataset class not integrated with HuggingFace datasets; no support for large or streaming datasets beyond memory. | Data ingestion may be inconsistent across runs; risk of caching unclean data; no test coverage; difficulty handling huge corpora. | (1) Add configurable data paths and split ratios in YAML config. (2) Provide CLI command for dataset preparation and caching. (3) Add tests verifying deterministic splits. | Revert by falling back to existing default behaviour; remove config if issues arise. |
| **Security & safety** | **Partially Implemented** | Safety configuration with regex patterns for secrets, PII and jailbreak detection[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sanitizers.py#L25-L61); safety filters enforce allow/block lists and can mask logits[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/filters.py#L15-L113); sandbox executes commands with resource limits and redaction[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sandbox.py#L2-L89); error logging sanitises output[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/error_log.py#L15-L51). | Safety not integrated into all pipelines; token masking not used in training loop; secret scanning not enforced in pre-commit; no test coverage; limited prompt injection detection. | Potential leakage of secrets or harmful content; sandbox may degrade performance; uncertain behaviour under adversarial prompts. | (1) Integrate safety filters into inference and training pipelines; provide gating in CLI. (2) Add pre-commit hook using `git-secrets` or similar to scan for API keys. (3) Write tests ensuring sanitisation masks secrets. | Safety integration can be feature-flagged; revert by disabling safety enforcement. |
| **Internal CI/test** | **Partially Implemented** | `noxfile.py` orchestrates linting and testing; `pytest.ini` configures tests; tests exist for session logging and DB utilities; pre-commit config ensures formatting. | No tests cover training, evaluation, tokenisation or safety; no continuous integration workflow (GitHub Actions intentionally disabled); code coverage not measured; `tox` config missing. | Undetected regressions in core ML functionality; low confidence in changes; risk of subtle bugs in training loops. | (1) Add pytest suites for tokeniser, model, training and evaluation; aim for high coverage. (2) Define `nox -s tests` session that runs tests offline. (3) Provide coverage report using `pytest-cov`. | Tests can be added gradually; revert by removing or disabling failing tests during rollout. |
| **Deployment** | **Partially Implemented** | `pyproject.toml` declares package metadata; `Dockerfile` provides base image; CLI entry points partially defined; `generate.py` offers simple generation CLI[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/generate.py#L13-L70). | No packaging to PyPI; CLI incomplete; missing `setup.cfg` for static analysis; Dockerfile not tested; no container orchestrations; no CLI for serving models as API. | Difficult to deploy to production; risk of environment drift; manual packaging steps. | (1) Complete CLI with train/evaluate commands. (2) Create `setup.py` or Poetry packaging; optionally publish to private index. (3) Provide example docker-compose to run training and inference. | Packaging changes can be versioned; revert by pinning previous release. |
| **Documentation & examples** | **Partially Implemented** | Docs in `docs/modules/` explain data handling[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/data_handling.md#L10-L28), training engine[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/modules/training_engine.md#L2-L17), experiment tracking[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/ops/experiment_tracking.md#L1-L64), and reproducibility[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/repro.md#L1-L13); README covers environment setup and reproducibility expectations[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/README.md#L1-L32). | Many docs reference missing YAML configs and examples; no diagrams; no end-to-end quickstart; test notebooks absent. | Users may misconfigure system; knowledge gap on using features; incomplete docs hamper adoption. | (1) Fill gaps in docs by adding example config files and usage examples. (2) Include diagrams of data flow and model pipeline. (3) Provide Jupyter notebooks demonstrating training and evaluation. | Documentation changes can be versioned and rolled back; maintain separate `docs` branch if necessary. |
| **Experiment tracking** | **Partially Implemented** | MLflow and W&B integration toggled via flags in `codex_logging.py`; environment summary and seeds logged in checkpoint metadata; docs for experiment tracking[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/docs/ops/experiment_tracking.md#L1-L64). | MLflow initialisation optional and not exposed in CLI; offline tracking recommended but no example; no NDJSON/CSV metrics logs; integration tests absent. | Metrics may not be logged, hindering reproducibility; risk of mis-configured tracking. | (1) Add CLI flags to enable MLflow and specify tracking URI. (2) Persist evaluation metrics in NDJSON for offline analysis. (3) Provide example script demonstrating offline MLflow use. | Experiment tracking can remain optional; revert by disabling flags. |
| **Extensibility** | **Partially Implemented** | Model registry pattern allows new models to be registered[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/models/registry.py#L19-L118); tokeniser training uses dataclass config; safety filters configurable; plugin pattern for optional logging. | Hard-coded file paths; CLI not pluggable; no registry for data modules or trainers; missing API for extensions; some components (e.g., evaluation) not modular. | Harder to integrate new models/datasets; fragmentation; custom forks diverge. | (1) Generalise registry patterns for data loaders, trainers and evaluation metrics. (2) Use entry points (e.g., `setuptools` `entry_points`) to allow external plugins. (3) Document how to add new models or tokenisers. | Additional registry code can be hidden behind feature flags; revert by using simple Python imports. |

3. High-signal findings and quick wins
---------------------------------------

1. **Missing YAML configuration files** – The code references several Hydra YAML files that are absent (`configs/training/base.yaml`, `configs/data/base.yaml`, `configs/tokenization/base.yaml`), leading to hidden default hyper-parameters and unpredictable behaviour[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). Creating these files and documenting their fields is a high-impact, low-effort fix.
2. **Incomplete CLI** – The central command-line interface lacks implemented commands; training and evaluation must currently be invoked via internal Python functions[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/codex_cli.py#L50-L59). Exposing them through CLI subcommands would greatly improve usability.
3. **Tokeniser training pipeline lacks default config** – The tokeniser training script is powerful but requires manual parameter specification[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/tokenization/train_tokenizer.py#L39-L143). Providing a default config and hooking the pipeline into the CLI will enable reproducible tokenisation.
4. **Hydra fallback hides configuration** – Without YAML files, Hydra silently falls back to defaults[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). This can mislead users into thinking a config was loaded. Logging a warning when config files are missing would improve transparency.
5. **Limited test coverage** – Only logging and DB utilities have tests; core ML components (tokenisers, models, training, evaluation, safety) are untested. Adding targeted unit tests for these modules will increase confidence.
6. **Safety filters not integrated** – Although sanitisation and filters exist, they are not wired into generation or training loops[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sanitizers.py#L25-L61). Integrating safety gating is critical to prevent leakage of secrets or malicious outputs.
7. **No resume capability exposed** – Robust checkpointing utilities exist[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259) but there is no CLI mechanism to resume training. A `--resume` flag would leverage existing functions and improve resiliency.
8. **Lack of experiment tracking defaults** – MLflow, W&B and TensorBoard are supported in code but not configured or documented via CLI; offline experiment logging should be the default[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/monitoring/codex_logging.py#L116-L187).
9. **Ambiguity in naming (“ChatGPT” vs MiniLM)** – The repository names some modules as ChatGPT/Codex but actually implements a small Transformer model[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/models/minilm.py#L1-L98). Clarifying naming prevents over-promising and misinterpretation.
10. **Missing packaging and deployment pipeline** – There is no PyPI packaging or container orchestration; the Dockerfile is untested. Packaging the code as a Python package and providing deployment examples would accelerate adoption.
11. **No data preparation CLI** – Data loading utilities exist[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/data_utils.py#L1-L143) but there is no command to prepare or cache datasets. A `prepare-data` CLI could wrap splitting, caching and safety filtering.
12. **Lack of reproducibility enforcement** – The `set_reproducible` function exists[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/repro.py#L1-L77) but seeds are not enforced across all pipelines. Exposing a `--seed` flag and logging seeds would improve determinism.
13. **Environment provenance not surfaced** – Provenance utilities capture environment summary and pip freeze[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/provenance.py#L38-L89) but these are not surfaced in CLI or docs. Including environment info in training/evaluation logs would help reproducibility.
14. **Incomplete documentation and examples** – Many docs refer to missing examples or diagrams; updating docs to include usage examples and quickstarts is essential for user onboarding.
15. **Optional dependencies** – Many features rely on optional libraries (MLflow, W&B, Pynvml). Without proper dependency management or clear error messages, features may silently fail.
16. **No central registry for data, trainers or metrics** – Extensibility is limited due to lack of registry patterns beyond models; adopting registries for other components will simplify adding new features.
17. **Potential security risks** – Safety filters are not enforced by default, raising concerns about unfiltered outputs. Pre-commit scanning for secrets and sandboxing external calls should be enabled by default.
18. **No performance monitoring** – GPU and system metrics logging exists[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/monitoring/codex_logging.py#L116-L187) but is optional. Adding default monitoring dashboards would allow troubleshooting performance bottlenecks.
19. **Lack of LoRA configuration** – LoRA integration is implemented[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/peft/peft_adapter.py#L37-L138) but the CLI does not expose LoRA parameters or training flags. Surface these options for research experiments.
20. **Poor error handling** – Many functions raise exceptions without context. Adopting consistent error capture blocks (see §8) will aid debugging.

4. Atomic diffs (proposed patches)
-----------------------------------

Below are example unified diffs that implement some of the high-impact fixes. Each diff includes rationale, risks and rollback suggestions. Patches are additive and respect the policy of not enabling cost-incurring GitHub actions (no workflow YAMLs).

### Diff 1 – Add default training YAML config

**Why:** Provide reproducible hyper-parameters and make Hydra config explicit instead of relying on silent fallback[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82).

**Patch:**

```yaml
# In a new file `configs/training/base.yaml`:
# Default training configuration for Codex ML
# This file defines hyper-parameters used by the training engine. It avoids hard-coded defaults.
seed: 42
model: minilm
learning_rate: 3e-4
batch_size: 32
max_epochs: 5
scheduler: linear
warmup_steps: 0
gradient_accumulation: 1
tensorboard: true
mlflow_enable: false
```

**Risk:** If hyper-parameters mismatch existing defaults, performance may change. YAML loading errors could break training.

**Rollback:** Delete `configs/training/base.yaml` to restore fallback defaults. Document the removal in change log.

**Tests/docs:** Create a unit test that loads the YAML via `load_config` and asserts values. Update docs to reference the new config file.

### Diff 2 – Implement training CLI subcommand

**Why:** Without a `train` command, users cannot run the training loop through the CLI[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/cli/codex_cli.py#L50-L59).

**Patch:**

```python
# In `src/codex_ml/cli/codex_cli.py` replace the stubbed train command with:
@cli.command()
@click.option("--config", default="configs/training/base.yaml", help="Path to the Hydra YAML config")
@click.option("--resume", is_flag=True, help="Resume from last checkpoint if available")
@click.option("--seed", default=None, help="Override random seed")
def train(config: str, resume: bool, seed: Optional[int]):
    """Train a language model using the Codex training engine."""
    from codex_ml.utils.config_loader import load_config
    from codex_ml.training import run_functional_training

    cfg = load_config(config_path=config)
    if seed is not None:
        cfg.seed = int(seed)

    try:
        run_functional_training(config=cfg, resume=resume)
    except Exception as e:
        from codex_ml.utils.error_log import log_error
        log_error("train", str(e))
        raise
```

**Risk:** Introduces CLI dependencies (click) and may break for missing config files. Changing function signatures could require refactoring tests.

**Rollback:** Revert changes to `codex_cli.py`; remove new imports and options. CLI will return to stub mode.

**Tests/docs:** Add a functional test invoking `codex-cli train` on a small dataset and verifying that a checkpoint is produced. Document the command in README and training docs.

### Diff 3 – Integrate safety filters into generation

**Why:** Outputs may contain secrets or harmful content; integrate safety filters to sanitise generation[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sanitizers.py#L25-L61).

**Patch:**

```python
# In `src/codex_ml/cli/generate.py` replace the printing of the result with:
result = model.generate(**gen_kwargs)

# Apply safety sanitisation
from codex_ml.safety.sanitizers import sanitize_output, SafetyConfig
safety_cfg = SafetyConfig()
sanitized, redactions = sanitize_output(result, safety_cfg)
print(sanitized)
if redactions > 0:
    click.echo(f"[warning] {redactions} redaction(s) applied")
```

**Risk:** Sanitisation may remove legitimate content; performance overhead from regex checks. Users expecting raw output may be surprised.

**Rollback:** Add a `--no-safety` flag to disable sanitisation or revert the patch entirely.

**Tests/docs:** Write tests verifying that secret tokens are redacted. Update CLI docs to explain sanitisation and the new flag.

### Diff 4 – Add resumption flag to training

**Why:** Checkpointing utilities exist but there is no resume option[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259).

**Patch:**

```python
# In `src/codex_ml/training.py` modify `run_functional_training` signature and body:
def run_functional_training(config: DictConfig, use_deeplearning: bool = False, resume: bool = False, **kwargs):
    """Run the custom training loop.

    Args:
        config: Hydra/OmegaConf config
        use_deeplearning: whether to use the HF trainer
        resume: if True, load the last checkpoint before starting
    """

    # If resuming, attempt to load training checkpoint
    if resume:
        from codex_ml.utils.checkpointing import load_training_checkpoint
        last_ckpt = load_training_checkpoint(config.output_dir)
        if last_ckpt:
            model, optimizer, scheduler, rng_state = last_ckpt
        else:
            print("No checkpoint found; starting fresh.")

    # existing body continues
```

**Risk:** If checkpoint loading fails or mismatched hyper-parameters, training may crash. Resume may inadvertently load stale checkpoints.

**Rollback:** Remove `resume` parameter and associated code; training will always start fresh.

**Tests/docs:** Add test to pause training after a few steps, save checkpoint, then resume and verify identical loss. Document `--resume` flag in CLI docs.

### Diff 5 – Warn when configuration files are missing

**Why:** Hydra silently falls back to defaults when config files are absent[GitHub](https://github.com/Aries-Serpent/_codex_/blob/HEAD/src/codex_ml/utils/config_loader.py#L13-L82). Emitting a warning improves transparency.

**Patch:**

```python
# In `src/codex_ml/utils/config_loader.py` replace the fallback block with:
except FileNotFoundError:
    import warnings
    warnings.warn(f"Config file {config_path} not found; using built-in defaults", UserWarning)
    return OmegaConf.create({
        "seed": 42,
        "learning_rate": 1e-3,
        "batch_size": 32,
        "max_epochs": 1,
    })
```

**Risk:** Warnings may clutter output; some users may treat warnings as errors.

**Rollback:** Remove the `warnings.warn` call; fallback remains silent. Document the removal in change log.

**Tests/docs:** Write test ensuring that a `UserWarning` is raised when config file is missing. Mention this behaviour in docs.

5. Local tests & gates
-----------------------

To enforce quality before merging changes, define local offline CI using **pytest** and **nox**. These gates run in the Codex environment only (no GitHub Actions). Suggested additions:

1. **`tests/test_tokenizer.py`** – Validate that encoding followed by decoding returns the original text for HF and SentencePiece adapters. Check that unknown tokens are handled gracefully. ML Test Score: **data** (correct tokenisation) and **model** (consistency across devices).
2. **`tests/test_training_loop.py`** – Use a tiny synthetic dataset to run one epoch of training using the functional loop and the HF trainer; assert that loss decreases and that a checkpoint file is created. ML Test Score: **model** (training correctness) and **infrastructure** (checkpointing works).
3. **`tests/test_resume.py`** – Train for a few steps, save checkpoint, resume and ensure identical loss trajectory. ML Test Score: **reproducibility**.
4. **`tests/test_evaluation.py`** – Evaluate the model on a small dataset and check that accuracy/perplexity values match expected values. ML Test Score: **regression** (no silent changes in metrics).
5. **`tests/test_safety.py`** – Pass prompts containing secret patterns and verify they are redacted by `sanitize_prompt` and `sanitize_output`[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/safety/sanitizers.py#L25-L61). ML Test Score: **safety**.

**Command to run tests:**

```nginx
nox -s tests
```

If `nox` is not used, a simple fallback is:

```css
pytest -q --disable-warnings
```

6. Reproducibility checklist
-----------------------------

| Item | Status | Notes |
| --- | --- | --- |
| **Random seeds set** | ✗ | `set_reproducible()` seeds Python/NumPy/PyTorch and sets deterministic CuDNN[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/repro.py#L1-L77), but CLI does not expose a seed parameter and training functions do not always call it. |
| **Environment capture** | ✓/✗ | Provenance utilities record environment summary and git commit[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/provenance.py#L38-L89); checkpoints embed metadata[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259), but logs do not surface this information and CLI does not allow exporting environment snapshot. |
| **Dependency locking** | ✗ | There is no `requirements.lock` or `poetry.lock`; dependencies are not pinned, which jeopardises reproducibility. |
| **Deterministic datasets** | ✗ | Data splitting is deterministic when seeds provided[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/data_utils.py#L1-L143), but the absence of config/seed means splits may vary. |
| **Logging of hyper-parameters and results** | ✗ | Hyper-parameters are not logged systematically; MLflow/W&B integration is optional and off by default. |
| **Checkpoints include RNG state** | ✓ | Checkpointing utilities save RNG state and compute checksums[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259). |
| **Version control of code** | ✓ | Git commit hash recorded in checkpoints[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/checkpointing.py#L181-L259), but it is not surfaced in logs or docs. |
| **Documentation of experiments** | ✗ | There is no central log or experiment notebook; docs do not capture training results. |

**Missing items per reproducibility best practices:**

* Provide a `requirements.txt`/`poetry.lock` to pin dependencies.
* Expose `--seed` in CLI and set reproducible seeds early in all pipelines.
* Log hyper-parameters and metrics consistently (e.g., NDJSON and TensorBoard). Use offline MLflow by default.
* Persist dataset checksums and splits within config or log; include them in environment summary.
* Capture environment snapshot and pip freeze; allow exporting it via CLI to accompany experiments.

7. Deferred items and pruning rationale
----------------------------------------

Some features remain unimplemented or out of scope. Before working on them, consider complexity, risk and value:

* **Full ChatGPT fine-tuning** – Building a chat-level dataset and fine-tuning a large language model would require significant compute and is beyond the scope of the current minimal environment. Focus on smaller language models until there is ownership for dataset curation.
* **Distributed training and multi-GPU** – The HF trainer wrapper hints at multi-GPU support, but distributed training setup is complex. Unless required, keep training to single-GPU/CPU for reproducibility and simplicity.
* **Cloud deployment and API serving** – Exposing models as web services or integrating with cloud services can be deferred. Prioritise CLI and reproducibility first.
* **Comprehensive safety classification** – Building advanced safety classifiers (e.g., toxicity detection) requires dataset access and research; rely on simple regex-based sanitisation for now.
* **Automated GitHub Actions** – The project intentionally disallows GitHub-hosted workflows. Local CI via `nox` is sufficient; avoid introducing actions that incur cost.
* **Complex hyper-parameter sweeps** – Hydra sweeps and hyper-parameter search can be deferred until base training is stable and reproducible. Document how to extend for sweeps.

8. Error capture blocks
------------------------

When developing or running this project, if any step fails, log a research question to help future debugging. Use the following template:

```kotlin
Question for ChatGPT @codex {timestamp}: While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error: [ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

For example, if running the training CLI fails due to a missing config file, write:

```vbnet
Question for ChatGPT @codex 2025-09-15T14:00:00Z: While performing Step 3: Loading Hydra config, encountered the following error: FileNotFoundError: configs/training/base.yaml not found
Context: calling run_functional_training via codex-cli
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

These blocks should be captured in `.codex/errors.ndjson` via the existing error logger[GitHub](https://github.com/Aries-Serpent/_codex_/blob/9c76af46886b0aa06944992086a904384f63e304/src/codex_ml/utils/error_log.py#L15-L51). Recording detailed error context and timestamp will aid in debugging and automated support.
```
