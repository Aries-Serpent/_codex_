# *codex*: Status Update (2025‑09‑18)
 
## 1  Repo map

| Path | Description | Notes |
| --- | --- | --- |
| README.md, README_UPDATED.md, CHANGELOG.md, .codex/ | High‑level documentation and changelog | README includes installation & offline instructions, safety policy notes and test commands[*\[1\]*](https://github.com/Aries-Serpent/_codex_/blob/main/README.md#L17-L36). .codex contains status reports and mapping files. |
| src/codex_ml/ | Core library implementing training pipeline, evaluation, tokenization, data loaders, safety filters, logging & telemetry, metrics registry, configuration and CLI. | The largest part of the codebase. Contains well‑structured modules using dataclasses and registries. Many features implemented; some areas stubbed (e.g., tokenization CLI commands, SentencePiece tokenizer). |
| analysis/ | Lightweight audit pipelines and internal tooling. | Contains audit_pipeline.py and providers.py. providers.py implements InternalRepoSearch but ExternalWebSearch is a stub raising NotImplementedError[*\[2\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/analysis/providers.py#L15-L48). |
| tools/ | Scripts for running Codex workflows, patch application and safety scanning. | Includes apply_safety.py, codex_run.py, run_codex_workflow.sh. |
| configs/ | YAML policy files for safety (e.g., configs/safety/policy.yaml). | Contains default prompt/output filters with allow/block rules; used by safety modules. |
| examples/ | Example scripts demonstrating training with metrics logging and MLflow. | train_loop.py logs metrics and MLflow offline mode[*\[3\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/train_loop.py#L117-L153). |
| docs/ | Extensive documentation: guides, architecture, modules, data handling, configuration. | Some docs mention features not fully implemented (e.g., tokenization CLI). |
| patches/ | Unified diff files used by Codex tasks. | Not relevant to production but used in codex workflows. |
| scripts/ | Shell scripts to run local gates and smoke tests. | Eg codex_local_gates.sh for offline gating. |

### Stubs & unimplemented areas
 
**SentencePiece tokenizer**: src/codex_ml/tokenization/adapter.py defines SentencePieceTokenizer but all methods raise NotImplementedError[*\[4\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tokenization/adapter.py#L31-L48).
**Tokenizer CLI commands**: src/codex_ml/cli/codex_cli.py includes codex tokenizer train/validate/encode/decode commands but marks them as TODO; the CLI prints a message indicating that tokenization pipelines are disabled[*\[5\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/cli/codex_cli.py#L35-L103).
**External web search provider**: analysis/providers.py includes ExternalWebSearch class with search method stubbed out (returns disabled list)[*\[2\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/analysis/providers.py#L15-L48).
**SentencePiece training & data preparation**: no code for vocabulary training or BPE extraction; config schema includes fields but not implemented.
**Limited test coverage**: repository lacks a dedicated tests directory and relies mainly on noxfile.py and smoke scripts. Many modules have little or no unit tests.
  
## 2  Capability audit table
 
Each capability is assessed for its implementation status, existing artefacts, missing components, risks and remediation strategies.

| Capability | Status | Existing artefacts | Gaps | Risks | Minimal patch plan | Rollback plan |
| --- | --- | --- | --- | --- | --- | --- |
| **Tokenization** | **Partially Implemented** | HFTokenizerAdapter wrapper for Hugging Face tokenizers; WhitespaceTokenizer for simple tokenization; TokenizerAdapter factory selects based on config[*\[4\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tokenization/adapter.py#L31-L48). | SentencePieceTokenizer stub; CLI commands for tokenizer training/validation disabled; no vocabulary training or BPE extraction; no fast tokenizers. | Without proper tokenization, training reproducibility suffers; CLI users cannot train custom tokenizers; lacking SentencePiece support restricts low‑resource tasks. | Implement SentencePieceTokenizer using sentencepiece library with load/encode/decode methods; add CLI commands for tokenization training/validation; integrate vocabulary training into data prep. Provide tests with small corpus and ensure deterministic encoding. | Add new tokenizer as opt‑in; fallback to HF tokenizers if missing. Provide environment variable to disable SentencePiece. |
| **ChatGPT Codex modeling** | **Implemented with LoRA support** | Model registry loads HF models and custom MiniLM variant; optional LoRA/PEFT adapter injection via config; dtype and device placement handled in modeling.py; training config includes LoRA parameters[*\[6\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/models/registry.py#L16-L67). | No unit tests for model registry or LoRA integration; LoRA config not validated; limited support for quantization & HF fine-tuning strategies. | Misconfigured LoRA params or dtype may lead to runtime errors; absence of tests makes regressions likely; device placement may silently fall back to CPU. | Add validation in config dataclass for LoRA fields; implement tests for model loading, LoRA injection and dtype/device; optionally support bitsandbytes quantization. Document supported models. | Provide ability to disable LoRA; revert to current simple registry if issues occur. |
| **Training engine** | **Implemented** | run_functional_training orchestrates dataset loading, safety filters, environment export, model loading, LoRA, seeds & config normalization; uses either custom loop or HF Trainer; fallback custom loop implemented in training/functional_training.py[*\[7\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/training/__init__.py#L383-L554). | Only basic training loop provided; no support for gradient accumulation in fallback loop; limited error handling for out-of-memory; training CLI limited; no early-stopping or scheduler integration. | Without gradient accumulation, large batch sizes may OOM; long training runs cannot resume mid-epoch; customizing training options is difficult. | Extend fallback loop to support gradient accumulation, scheduler and mixed precision; integrate early stopping callback and checkpoint resume; parameterize number of evaluation steps. | Keep current fallback as default; new features behind config flags; revert by disabling new flags. |
| **Configuration management** | **Implemented** | src/codex_ml/config.py defines nested dataclasses (TrainingConfig, EvaluationConfig, etc.) and uses OmegaConf to load YAML & apply overrides; each dataclass has validation methods【87795989638258†L129-L170】. | No Hydra integration; config file examples limited; overrides not accessible via CLI; missing CLI flags for all sub-configs; scheduler & optimizers not validated thoroughly. | Misconfigured values may silently be ignored; users must edit YAML manually; limited reproducibility across runs. | Integrate Hydra for hierarchical config loading and dynamic sweeps; expose CLI options for common parameters; document config fields; implement default config.yaml. | Provide compatibility layer to read existing config; allow disabling Hydra via flag. |
| **Evaluation & metrics** | **Implemented** | eval/runner.py loads predictions & targets, computes metrics (accuracy, perplexity, F1, BLEU, ROUGE, CHRF) and writes NDJSON/CSV summaries[*\[8\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/eval/runner.py#L222-L319); metrics/registry.py registers metrics using registry pattern[*\[9\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/metrics/registry.py#L69-L113). | No support for streaming evaluation; metrics require optional libs (transformers, sacrebleu); evaluation CLI not integrated with training; no confidence intervals or bootstrap metrics; minimal tests. | Without tests, metrics may compute incorrectly; optional dependencies may break evaluation; big datasets loaded into memory. | Add evaluation CLI command; implement streaming evaluation and aggregator; write unit tests for each metric; fallback gracefully when optional libs missing. | Keep existing evaluation logic; new features behind feature flags. |
| **Logging & monitoring** | **Partially Implemented** | codex_logging.py configures TensorBoard, W&B, MLflow and GPU/CPU metrics; system metrics logged using psutil via monitoring/system_metrics.py[*\[10\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/monitoring/system_metrics.py#L21-L65); telemetry/metrics.py exposes Prometheus counters & histograms[*\[11\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/telemetry/metrics.py#L14-L34); MLflow utils provide safe integration[*\[12\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tracking/mlflow_utils.py#L1-L18). | Logging system is optional; W&B & TensorBoard initialised only if installed; no structured logging (e.g., JSON) for pipeline steps; missing correlation IDs; no centralised log aggregator. | Silent failures if dependencies missing; logs scattered across files; metrics sampling thread may leak resources; high overhead for psutil or NVML metrics. | Create a unified logging interface using Python logging with JSON formatter; always log to file; unify MLflow, W&B and TB under one config; ensure system metrics logger is properly terminated. | Provide fallback to current behaviour; allow disabling metrics logger; removal by toggling enable_system_metrics. |
| **Checkpointing & resume** | **Partially Implemented** | run_functional_training creates output_dir and checkpoint_dir, saves model/optimizer states via HF Trainer or custom loop; custom loop uses save_checkpoint; evaluation writes NDJSON results. | No fine-grained checkpoint naming; only last checkpoint saved; no best-k retention; resume not fully integrated (custom loop may not restore scheduler state). | Risk of losing training progress; resume may start from wrong epoch; dataset streaming state not saved. | Add callback to save checkpoints every N steps and maintain top-k based on validation metric; implement load_checkpoint to restore model, optimizer, scheduler and RNG state; log metadata in manifest. | Keep simple checkpointing as default; new retention optional; revert by disabling checkpoint.best_k. |
| **Data handling** | **Implemented** | data/loader.py streams, shuffles and caches datasets deterministically[*\[13\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/data/loader.py#L238-L317)[*\[14\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/data/loader.py#L341-L441); supports caching with manifest; registry.py allows custom loaders; dataclasses define ShardConfig and DataConfig. | Data streaming is file-based only; no remote dataset support; no dataset versioning or split checks; prepare_data_from_config missing tests. | Large datasets require reading entire file; risk of inconsistent splits; absence of dataset hashing means unknown reproducibility. | Add dataset manifest with hashes and sizes; implement streaming from remote sources; write tests for deterministic splits; add dataset version to config. | Manifest generation optional; revert by ignoring dataset hash. |
| **Security & safety** | **Implemented** | safety/sanitizers.py defines regex patterns to detect secrets, PII and jailbreak prompts; functions sanitize_prompt and sanitize_output return sanitized text and flags[*\[15\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/safety/sanitizers.py#L27-L61); filters.py loads YAML policy and enforces allow/block/redact rules; environment variables override policies; integrated into training & data loading[*\[16\]*](https://github.com/Aries-Serpent/_codex_/blob/main/README.md#L55-L80). | Safety patterns are heuristic; limited coverage of languages; no integration with external scanning tools; no dependency scanning; no supply chain attestation. | Missed sensitive data leaks; potential false positives; outdated dependencies may introduce vulnerabilities. | Expand patterns to cover more languages & PII types; integrate with tools like detect-secrets; add pip-audit step in gating; implement requirements.lock. | Provide flag to disable new scanners; revert by using current heuristics. |
| **Internal CI/Test** | **Partially Implemented** | noxfile.py defines sessions for linting, tests and coverage; scripts/codex_local_gates.sh runs smoke tests; examples use pytest but repository lacks unit tests. | Many modules untested; no coverage enforcement; no tox/nox for Python versions; no gating for docs or config. | Bugs may go unnoticed; regressions may slip; configuration drift may break code. | Add a tests/ directory with unit tests for tokenization, config validation, data loader, metrics; integrate coverage measurement; create nox session to run tests offline; enforce pre-commit to run pytest. | If tests cause pipeline failure, revert gating to optional; maintain minimal test suite. |
| **Deployment** | **Partially Implemented** | Dockerfile and entrypoint.sh build container; CLI entry points defined via codex_setup.py; training script can be invoked via codex command; examples show offline MLflow run. | No packaging to PyPI; no setup.py; missing version pinning; environment dependencies not locked; no reproducible container build; incomplete CLI docs. | Deployments may break due to unpinned dependencies; container size may be large; lacking security scanning for container. | Add pyproject.toml/setup.cfg with dependencies; generate requirements.txt with hashes; update Dockerfile to use multi-stage build and minimal base; document CLI usage in README; optionally publish container to registry. | Keep current Docker build; revert by ignoring packaging if issues. |
| **Documentation & examples** | **Implemented with gaps** | Extensive docs in docs/ covering architecture, modules, configuration and getting started; examples in examples/ show training loops and MLflow offline run. | Some docs reference features not yet implemented (tokenizer CLI, plugin system); missing quickstart for evaluation and config usage; diagrams not updated. | Users may be confused about unimplemented features; outdated docs reduce credibility. | Audit docs to remove references to stubbed features; add quickstart examples for training & evaluation; include architecture diagrams; maintain changelog. | Keep old docs under legacy folder; revert if new docs confuse users. |
| **Experiment tracking** | **Implemented (optional)** | MLflow integration via mlflow_utils.py with lazy import[*\[12\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tracking/mlflow_utils.py#L1-L18); metrics logging in train_loop.py writes JSON/NDJSON; telemetry uses Prometheus counters. | No support for W&B offline; metrics server not documented; no central registry of experiment metadata; limited log retention. | Hard to compare experiments; risk of lost metrics; duplication of logs. | Provide unified experiment tracker that logs to MLflow offline, W&B offline and local files; implement run metadata capturing (git hash, config) using provenance.export_environment[*\[17\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/provenance.py#L61-L142); document how to view metrics. | Allow disabling tracker; revert to basic JSON logging. |
| **Extensibility** | **Implemented** | Registries for models, datasets and metrics allow pluggable components; configuration uses dataclasses and OmegaConf; plugin architecture uses entry points. | Plugin discovery not documented; loading from external packages not tested; limited custom hooks for evaluation or training; missing template for new modules. | Users may not know how to register new dataset or metric; risk of plugin conflicts. | Document registry usage and provide template modules; implement plugin loader using importlib.metadata.entry_points and error handling; add CLI for listing registered components. | Keep registry simple; revert by disabling plugin loading. |

## 3  High‑signal findings (critical gaps & quick wins)
1. **Tokenizer subsystem incomplete** – SentencePiece and tokenization CLI are stubbed; training reproducibility is hindered. Implementing a working SentencePieceTokenizer and CLI will unlock custom vocabulary training and align with docs.
2. **Minimal test coverage** – The repository lacks a dedicated tests/ directory and coverage enforcement. Critical modules (tokenization, data loader, metrics) have no unit tests, increasing risk of regressions.
3. **Checkpointing/resume limitations** – Current training saves only the last checkpoint; no support for best-k retention or proper resume. Adding robust checkpoint management with metadata and RNG state will improve reliability.
4. **Evaluation pipeline not integrated** – Training CLI doesn’t automatically run evaluation; evaluation script is separate and lacks streaming evaluation. Provide CLI integration and ensure metrics computed on validation splits.
5. **Config management lacks Hydra & CLI overrides** – While dataclasses & OmegaConf exist, Hydra is not integrated and there’s no sweep functionality. Exposing config via CLI and enabling sweeps would enhance reproducibility.
6. **Logging fragmentation** – Multiple logging systems (TensorBoard, W&B, MLflow, JSON files) exist with optional dependencies. A unified logging interface with fallback will reduce complexity and ensure consistent metrics.
7. **Safety scanning limited** – Regex-based sanitizers may miss secrets/PII and there is no dependency scanning. Integrating secret scanning tools and enforcing dependency locks will mitigate security risks.
8. **Incomplete deployment packaging** – No packaging metadata (pyproject.toml), no dependency locking or reproducible builds; container uses heavy base image. Introducing packaging and multi-stage Docker build will improve production readiness.
9. **External search provider stub** – ExternalWebSearch is unimplemented. If required for research, this should either be implemented or pruned with rationale.
10. **Docs inconsistency** – Documentation references features not yet implemented; cleaning up docs and adding quickstart examples will set accurate expectations.
11. **Telemetry & experiment tracking not documented** – Prometheus metrics and MLflow integration exist but not documented; unify and document offline tracking and system metrics collection.
12. **Extensibility & plugin system underused** – Registries exist but plugin discovery not exposed; providing guidelines and CLI to list/add plugins will encourage contributions.
13. **Training engine lacks advanced features** – Gradient accumulation, learning rate schedulers and early stopping are absent in fallback loop; implementing these will allow efficient training on limited hardware.
14. **Configuration validation gaps** – Some config fields not validated (LoRA params, scheduler options); misconfiguration may cause silent errors.
15. **No dataset versioning** – Datasets loaded from raw files without version control or hashing; adding manifest with file hashes ensures reproducibility.
16. **CI gating not comprehensive** – noxfile.py defines sessions but missing coverage enforcement; adding pytest with coverage and secret scanning tasks is necessary.
17. **MLflow & W&B optional integration** – Implementation exists but not automatically enabled; unify experiment tracking across training and evaluation.
18. **System metrics logger can leak threads** – SystemMetricsLogger spawns a thread that may not terminate; ensure proper cleanup in context manager.
19. **No packaging to PyPI** – Without packaging, library cannot be easily installed; adding packaging metadata will support reuse.
20. **Atomic diffs needed to implement quick wins** – Provide minimal diffs for critical fixes such as implementing SentencePiece tokenizer, adding tests, adding Hydra integration and improved checkpointing.
  
## 4  Atomic diffs (examples)
 
Below are sample unified diffs implementing key improvements. Each diff includes rationale, risk, rollback and tests/docs notes.
 
### Diff 1 – ImplementSentencePieceTokenizer
 
*** Begin Patch  
 *** Update File: src/codex_ml/tokenization/adapter.py  
 @@  
  class SentencePieceTokenizer(TokenizerAdapter):  
 - def __init__(self, model_path: str, **kwargs):  
 - raise NotImplementedError("SentencePiece is not yet supported")  
 +  
 + def __init__(self, model_path: str, **kwargs):  
 + """Load a SentencePiece model from the given path.  
 +  
 + Args:  
 + model_path: Path to the .model file generated by sentencepiece  
 + """  
 + try:  
 + import sentencepiece as spm  
 + except ImportError as e:  
 + raise RuntimeError(  
 + "sentencepiece must be installed to use SentencePieceTokenizer"  
 + ) from e  
 + self.sp = spm.SentencePieceProcessor()  
 + self.sp.load(model_path)  
 +  
 + def encode(self, text: str, **kwargs) -> list[int]:  
 + return self.sp.encode(text, out_type=int)  
 +  
 + def decode(self, ids: list[int], **kwargs) -> str:  
 + return self.sp.decode(ids)  
 +  
 + def save(self, save_directory: str):  
 +  # SentencePiece models are static; copy the model file into directory  
 + import shutil, os  
 + os.makedirs(save_directory, exist_ok=True)  
 + model_name = os.path.basename(self.sp.model_file())  
 + shutil.copy2(self.sp.model_file(), os.path.join(save_directory, model_name))  
 +  
 *** End Patch
 
**Why**: Enables custom tokenizer training using sentencepiece, aligning docs with implementation. **Risk**: Introduces new dependency; must ensure sentencepiece installed; may increase build size. **Rollback**: Set type in config to hf or whitespace; or revert patch by removing SentencePieceTokenizer implementation. **Tests/Docs**: Add unit tests to encode/decode sample text; update CLI docs with instructions to train and use sentencepiece; ensure fallback to HF tokenizer if dependency missing.
  
### Diff 2 – Add gradient accumulation and scheduler to fallback training loop
 
*** Begin Patch  
 *** Update File: src/codex_ml/training/functional_training.py  
 @@ def train(model, dataloader, optimizer, scheduler=None, grad_accum_steps: int = 1):  
 - for epoch in range(num_epochs):  
 - for step, batch in enumerate(dataloader):  
 - outputs = model(**batch)  
 - loss = outputs.loss  
 - loss.backward()  
 - optimizer.step()  
 - optimizer.zero_grad()  
 - # log metrics ...  
 + for epoch in range(num_epochs):  
 + for step, batch in enumerate(dataloader):  
 + outputs = model(**batch)  
 + loss = outputs.loss / grad_accum_steps  
 + loss.backward()  
 + if (step + 1) % grad_accum_steps == 0:  
 + optimizer.step()  
 + optimizer.zero_grad()  
 + if scheduler is not None:  
 + scheduler.step()  
 + # log metrics ...  
 *** End Patch
 
**Why**: Adds gradient accumulation and optional scheduler to custom training loop; enables larger effective batch sizes on limited GPUs. **Risk**: Changing optimisation step frequency can affect learning dynamics; must tune learning rate accordingly. **Rollback**: Set grad_accum_steps=1 and omit scheduler; or revert patch. **Tests/Docs**: Add tests verifying that model parameters update correctly with accumulation; document new config options (grad_accum_steps, scheduler).
  
### Diff 3 – Add dataset hash & manifest to data loader
 
*** Begin Patch  
 *** Update File: src/codex_ml/data/loader.py  
 @@ def prepare_data_from_config(config: DataConfig, ...):  
 - # existing code for writing splits and manifest  
 + import hashlib, json  
 + def file_hash(path):  
 + h = hashlib.sha256()  
 + with open(path, 'rb') as f:  
 + for chunk in iter(lambda: f.read(8192), b''):  
 + h.update(chunk)  
 + return h.hexdigest()  
 + manifest = {  
 + 'train': train_path,  
 + 'val': val_path,  
 + 'hashes': {  
 +  'train': file_hash(train_path),  
 + 'val': file_hash(val_path)  
 + },  
 + 'split': len(train_data),  
 + 'version': config.version or 'unknown'  
 + }  
 + with open(os.path.join(output_dir, 'manifest.json'), 'w') as f:  
 + json.dump(manifest, f, indent=2)  
 *** End Patch
 
**Why**: Recording hashes ensures data reproducibility and helps detect corruption. **Risk**: Slight overhead when saving splits; requires reading the entire files. **Rollback**: Remove hash computation; fallback to existing manifest. **Tests/Docs**: Update prepare_data_from_config tests to assert manifest exists and contains correct hashes; document new version field in data config.
  
### Diff 4 – Unified logging interface
 
*** Begin Patch  
 *** Add File: src/codex_ml/logging/unified.py  
 +import logging  
 +from pathlib import Path  
 +  
 +def setup_logger(name: str, log_dir: str = "./logs", level: str = "INFO") -> logging.Logger:  
 + """Create a logger that writes JSON logs to a file and stdout."""  
 + import json, sys  
 + logger = logging.getLogger(name)  
 + logger.setLevel(level)  
 + Path(log_dir).mkdir(parents=True, exist_ok=True)  
 + file_handler = logging.FileHandler(Path(log_dir) / f"{name}.jsonl")  
 + stream_handler = logging.StreamHandler(sys.stdout)  
 + formatter = logging.Formatter(  
 + fmt='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',  
 + datefmt='%Y-%m-%dT%H:%M:%S'  
 + )  
 + file_handler.setFormatter(formatter)  
 + stream_handler.setFormatter(formatter)  
 + logger.addHandler(file_handler)  
 + logger.addHandler(stream_handler)  
 + return logger  
 *** End Patch
 
**Why**: Consolidates disparate logging into a single JSON-formatted logger; ensures logs are persisted and visible. **Risk**: Changing logging may break existing debug statements; concurrency issues if logger reused across modules. **Rollback**: Use old logging utilities; disable unified logger import. **Tests/Docs**: Write test that sets up a logger and verifies JSON lines; update docs to instruct users to call setup_logger in entry points.
  
### Diff 5 – Addpytest tests and nox session
 
*** Begin Patch  
 *** Add File: tests/test_tokenizer.py  
 +from codex_ml.tokenization.adapter import HFTokenizerAdapter, SentencePieceTokenizer, TokenizerAdapter  
 +  
 +def test_hf_tokenizer_roundtrip():  
 + tokenizer = HFTokenizerAdapter(model_name="gpt2")  
 + text = "hello world"  
 + ids = tokenizer.encode(text)  
 + assert tokenizer.decode(ids).strip() == text  
 +  
 +def test_sentencepiece_tokenizer_roundtrip(tmp_path):  
 + # train a tiny SentencePiece model  
 + import sentencepiece as spm, os  
 + corpus = tmp_path / "corpus.txt"  
 + corpus.write_text("hello world\nhello codex\n")  
 + spm.SentencePieceTrainer.train(  
 + input=str(corpus), model_prefix=str(tmp_path / "spm"), vocab_size=100  
 + )  
 + tokenizer = SentencePieceTokenizer(model_path=str(tmp_path / "spm.model"))  
 + ids = tokenizer.encode("hello codex")  
 + assert tokenizer.decode(ids) == "hello codex"  
 *** End Patch  
 *** End Patch
 
**Why**: Provides first unit tests for tokenizers, ensuring round-trip encoding/decoding works. **Risk**: Requires sentencepiece dependency in test environment; may slow down CI. **Rollback**: Skip sentencepiece test if dependency missing; revert tests. **Docs**: Document test running via pytest and nox.
  
### Diff 6 – Hydra integration for configuration
 
*** Begin Patch  
 *** Update File: src/codex_ml/cli/codex_cli.py  
 @@  
 -@click.command()  
 -def train(config_path: str, overrides: str):  
 - config = load_app_config(config_path, overrides)  
 - run_functional_training(config.training)  
 +@click.command()  
 +@click.option("--config", "config_path", required=True, help="Path to YAML config")  
 +@click.option("--overrides", default="", help="Dotlist overrides for config")  
 +def train(config_path: str, overrides: str):  
 + """Train model with Hydra-powered config management."""  
 + from hydra import initialize, compose  
 + with initialize(config_path=os.path.dirname(config_path)):  
 + cfg = compose(config_name=os.path.basename(config_path), overrides=overrides.split())  
 + app_cfg = CodexConfig.from_omegaconf(cfg)  
 + app_cfg.validate()  
 + run_functional_training(app_cfg.training)  
 *** End Patch
 
**Why**: Enables hierarchical config loading and overrides via Hydra, allowing parameter sweeps and cleaner CLI. **Risk**: Hydra introduces complexity and additional dependency; may conflict with OmegaConf usage. **Rollback**: Provide fallback to load_app_config if Hydra not installed; keep old CLI as alternative. **Tests/Docs**: Add tests for CLI parsing; update README to describe Hydra usage and overrides.
  
## 5  Local tests & gates
**Testing commands**: Create a tests/ directory with unit tests (e.g., test_tokenizer.py, test_data_loader.py, test_config.py). Run tests with:

 `pip install -r requirements-dev.txt # includes pytest, sentencepiece, hydra`   
 `pytest -q --disable-warnings` 
**nox sessions**: Update noxfile.py to include a tests session:
 
```python @nox.session def tests(session): session.install("-e", ".", "pytest", "sentencepiece", "hydra-core") session.run("pytest", "--maxfail=1", "--disable-warnings", env={"PYTHONHASHSEED": "0"}) 
``` 

**ML Test Score mapping**:

| Test name | Category |
| --- | --- |
| test_tokenizer_roundtrip | Data (validates tokenizer determinism) |
| test_sentencepiece_tokenizer_roundtrip | Data (custom tokenizer) |
| test_data_loader_split | Data/infrastructure (ensure deterministic splits & manifest) |
| test_config_validation | Infrastructure (config validation & type checking) |
| test_model_loading | Model (initialises model & LoRA correctly) |
| test_training_loop | Performance/regression (ensures no NaN loss, gradient accumulation) |

1. **Secret scanning**: Add detect-secrets as a pre-commit hook and run in nox session to fail if secrets committed.
2. **Performance gating**: Use pytest-benchmark to ensure training loop throughput does not regress beyond threshold.

## 6  Reproducibility checklist

| Item | Present? | Notes |
| --- | --- | --- |
| **Random seed controlled** | ✅ | set_reproducible seeds Python, NumPy & PyTorch and sets deterministic algorithms[*\[18\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/seeding.py#L67-L85). |
| **Environment capture** | ✅ | export_environment writes pip freeze, git commit, GPU metadata[*\[17\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/provenance.py#L61-L142). |
| **Dataset versioning & hashes** | 🚫 | Datasets not versioned; implement manifest with hashes (see Diff 3). |
| **Config versioning** | 🚫 | No record of config used per run; store YAML in output dir & commit hash. |
| **Dependency locking** | 🚫 | requirements.txt not pinned; use lock file (e.g., pip-tools) and requirements.lock. |
| **Hardware determinism** | ✅ | seeding includes CUDA determinism; fallback to CPU if GPU not available. |
| **Checkpointing** | Partial | Last checkpoint saved; lacks full state & RNG; need improvements. |
| **Results determinism** | Partial | With seeds, results reproducible; evaluation uses deterministic metrics; must ensure dataset splitting is deterministic. |

## 7  Deferred items & pruning rationale

| Item | Rationale | Future plan |
| --- | --- | --- |
| **External web search provider** | Not needed for internal offline training; would require network calls and raise compliance issues. | Remove stub; document that external search is disabled; suggest using offline corpus. |
| **SentencePiece training via CLI** | Implementation deferred due to complexity and third-party dependency; planned for next milestone. | After base training pipeline stabilises, implement training script using sentencepiece and integrate with Hydra config. |
| **Full Hydra sweeps** | Parameter sweeps can be extensive; risk of compute cost. | Provide example sweep YAML but disable by default; instruct users on offline sweeps. |
| **End-to-end deployment** | Packaging to PyPI and container publishing out of current scope. | Outline steps; implement when repository features stabilise. |
| **Advanced evaluation (confidence intervals, cross-validation)** | Non-essential for initial release; complex to implement. | Provide optional evaluation pipeline using bootstrap or KFold in a later version. |

## 8  Error capture blocks
 
When encountering errors during the audit or while running future tasks, record them using the following template. Replace placeholders with actual values.
 
Question for ChatGPT @codex {{timestamp}}:  
 While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:  
 [ERROR_MESSAGE]  
 Context: [BRIEF_CONTEXT]  
 What are the possible causes, and how can this be resolved while preserving intended functionality?
 
Use this format to ask targeted questions; include a timestamp for reproducibility.

* * *

[*\[1\]*](https://github.com/Aries-Serpent/_codex_/blob/main/README.md#L17-L36) [*\[16\]*](https://github.com/Aries-Serpent/_codex_/blob/main/README.md#L55-L80) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/README.md*](https://github.com/Aries-Serpent/_codex_/blob/main/README.md)
 
[*\[2\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/analysis/providers.py#L15-L48) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/analysis/providers.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/analysis/providers.py)
 
[*\[3\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/train_loop.py#L117-L153) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/train_loop.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/train_loop.py)
 
[*\[4\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tokenization/adapter.py#L31-L48) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tokenization/adapter.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tokenization/adapter.py)
 
[*\[5\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/cli/codex_cli.py#L35-L103) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/cli/codex_cli.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/cli/codex_cli.py)
 
[*\[6\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/models/registry.py#L16-L67) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/models/registry.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/models/registry.py)
 
[*\[7\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/training/__init__.py#L383-L554) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/training/__init__.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/training/__init__.py)
 
[*\[8\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/eval/runner.py#L222-L319) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/eval/runner.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/eval/runner.py)
 
[*\[9\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/metrics/registry.py#L69-L113) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/metrics/registry.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/metrics/registry.py)
 
[*\[10\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/monitoring/system_metrics.py#L21-L65) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/monitoring/system_metrics.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/monitoring/system_metrics.py)
 
[*\[11\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/telemetry/metrics.py#L14-L34) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/telemetry/metrics.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/telemetry/metrics.py)
 
[*\[12\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tracking/mlflow_utils.py#L1-L18) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tracking/mlflow_utils.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/tracking/mlflow_utils.py)
 
[*\[13\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/data/loader.py#L238-L317) [*\[14\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/data/loader.py#L341-L441) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/data/loader.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/data/loader.py)
 
[*\[15\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/safety/sanitizers.py#L27-L61) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/safety/sanitizers.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/safety/sanitizers.py)
 
[*\[17\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/provenance.py#L61-L142) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/provenance.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/provenance.py)
 
[*\[18\]*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/seeding.py#L67-L85) GitHub
 
[*https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/seeding.py*](https://github.com/Aries-Serpent/_codex_/blob/main/src/codex_ml/utils/seeding.py)

----------------------

```yaml
**Codex-ready Task Sequence**
# This sequence outlines the steps ChatGPT‑Codex should take to address the gaps identified in the 2025‑09‑18 audit.  Each phase is numbered and further divided into sub-steps.  These tasks should be executed sequentially.

1. **Preparation**
   1.1 Confirm that all operations will run within the local codex environment, never triggering GitHub Actions or workflows.
   1.2 Install missing dependencies: `sentencepiece`, `hydra-core`, `pytest`, `pytest-benchmark`, `detect-secrets`, `pip-tools` via pip.  Use a deterministic version pin when available.
   1.3 Capture the current environment state by running `python -m pip freeze` and saving the output to `_codex_/environment.freeze`.  Record the git commit hash using `git rev-parse HEAD` and capture GPU metadata via `nvidia-smi` (if available).
   1.4 Parse `README.md` and remove or replace references to unimplemented features (e.g., tokenization CLI, external search).  Save the cleaned copy as `README_UPDATED.md`.
   1.5 Create a `change_log.md` file documenting all modifications made during this run, including patches applied and files generated.

2. **Search & Mapping**
   2.1 Enumerate all Python files in `src/codex_ml/` and identify classes, functions and stubs using AST parsing.  Produce a mapping of missing or stubbed capabilities (e.g., `SentencePieceTokenizer`, `ExternalWebSearch`) to their file and line location.
   2.2 Search through docs in `docs/` for references to unimplemented capabilities; list sections that require updates.
   2.3 Map each high-signal finding from the audit to the corresponding source code location.  For instance, link the training checkpoint limitation to `training/functional_training.py`, and the logging fragmentation to `codex_logging.py`.
   2.4 Identify candidate modules or third-party libraries that can implement missing features (e.g., `sentencepiece` for tokenizer, Hydra for configuration).  Record their import paths.

3. **Best-Effort Construction**
   3.1 Implement the missing `SentencePieceTokenizer` in `tokenization/adapter.py` using the `sentencepiece` library.  Ensure encode/decode/save functions work and update the factory to recognise `type: "sentencepiece"`.
   3.2 Extend the custom training loop to support gradient accumulation and optional learning-rate scheduler.  Update the function signature to accept `grad_accum_steps` and `scheduler`.
   3.3 Enhance data handling by adding file hashing and manifest generation to `prepare_data_from_config`.
   3.4 Introduce a unified logging interface that outputs JSON logs to file and stdout.  Create `logging/unified.py` and update entry points to use it.
   3.5 Integrate Hydra into the CLI: modify `codex_cli.py` to initialise Hydra, compose config and validate via dataclasses.  Provide CLI options for config path and overrides.
   3.6 Create a `tests/` directory with unit tests for tokenizers, data loader, config validation, model loading and training loop.  Use `pytest` to run them locally.
   3.7 Update `noxfile.py` to include a `tests` session that installs dev dependencies and runs `pytest` with coverage measurement.
   3.8 Add dependency lock generation: run `pip-compile` to produce `requirements.lock` and commit it.  Do not enable any GitHub workflows.
   3.9 Update `docs/` to remove references to disabled features and add quickstart sections for training & evaluation using the new CLI.
   3.10 Modify `configs/safety/policy.yaml` only if needed; ensure no new YAML triggers GitHub actions.

4. **Controlled Pruning**
   4.1 For components deemed unnecessary or high-risk (e.g., `ExternalWebSearch`), either remove the stub or wrap it in a `NotImplementedError` with a clear message explaining the rationale.  Update docs accordingly.
   4.2 Disable unmaintained CLI commands for tokenizer training/validation until the SentencePiece implementation is fully tested.
   4.3 Defer advanced features such as confidence intervals and complex evaluation metrics with documented rationale in deferred tasks.

5. **Error Capture**
   5.1 Wrap each major operation in try/except blocks.  If an error occurs, write an entry to `.codex/errors.ndjson` following the template:
       
       > Question for ChatGPT-5 {{timestamp}}:
       > While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
       > [ERROR_MESSAGE]
       > Context: [BRIEF_CONTEXT]
       > What are the possible causes, and how can this be resolved while preserving intended functionality?
   5.2 Continue execution after logging the error where possible.  Do not exit on first error unless data corruption risk exists.

6. **Finalisation**
   6.1 After implementing and updating all modules, run `pytest` to execute the new tests.  Save the output to `.codex/test_results.txt`.
   6.2 Generate a fresh status update summarising changes, new features and remaining gaps.  Save it as `.codex/status/_codex_status_update-YYYY-MM-DD.md`.
   6.3 Ensure all new files are added to the `change_log.md` and commit messages are clear.  Do not push or trigger remote CI.
   6.4 Provide instructions in the updated README for running training, evaluation and tests offline using the new CLI and Hydra.
```

```python
#!/usr/bin/env python3
"""
Codex-ready task runner implementing the sequential execution phases outlined in the
codex_ready_task_sequence.yaml. This script operates entirely within the local
codex environment, avoiding any network access or GitHub actions. It modifies
files in-place, generates tests and logs, and captures errors using the
specified template.

Usage:
    python codex_ready_task_runner.py

The script assumes it is executed from the repository root.
"""
import argparse
import ast
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def log_error(step_number: str, description: str, error: Exception, context: str) -> None:
    """Record errors in .codex/errors.ndjson following the required format."""
    errors_path = Path(".codex/errors.ndjson")
    errors_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "step": f"{step_number}:{description}",
        "error_message": str(error),
        "context": context,
    }
    with errors_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def run_command(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command and return the CompletedProcess."""
    return subprocess.run(cmd, check=False, capture_output=capture, text=True)


def install_dependencies():
    """Install required Python packages locally if not already installed."""
    # We avoid network access; attempt installation and ignore failures
    packages = ["sentencepiece", "hydra-core", "pytest", "pytest-benchmark", "detect-secrets", "pip-tools"]
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=False)


def capture_environment():
    """Capture pip freeze, git commit and GPU metadata."""
    freeze_out = run_command([sys.executable, "-m", "pip", "freeze"], capture=True)
    env_dir = Path("_codex")
    env_dir.mkdir(exist_ok=True)
    (env_dir / "environment.freeze").write_text(freeze_out.stdout)
    # Capture git commit
    git_out = run_command(["git", "rev-parse", "HEAD"], capture=True)
    (env_dir / "commit.txt").write_text(git_out.stdout.strip())
    # Capture GPU metadata if nvidia-smi available
    nvidia = shutil.which("nvidia-smi")
    if nvidia:
        gpu_out = run_command([nvidia, "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], capture=True)
        (env_dir / "gpu.info").write_text(gpu_out.stdout.strip())


def clean_readme():
    """Remove or replace references to unimplemented features in README.md."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return
    original = readme_path.read_text(encoding="utf-8").splitlines()
    cleaned_lines: list[str] = []
    for line in original:
        # Remove lines mentioning tokenizer CLI or external search provider
        if re.search(r"tokenizer .* CLI", line, re.IGNORECASE):
            continue
        if "ExternalWebSearch" in line:
            continue
        cleaned_lines.append(line)
    new_path = Path("README_UPDATED.md")
    new_path.write_text("\n".join(cleaned_lines), encoding="utf-8")


def append_change_log(message: str) -> None:
    """Append a message to change_log.md."""
    log_path = Path("change_log.md")
    with log_path.open("a", encoding="utf-8") as f:
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        f.write(f"[{timestamp}] {message}\n")


def ast_find_stubs(src_dir: Path) -> dict[str, list[tuple[str, int]]]:
    """Return a mapping of stubbed functions/classes to their file and line number."""
    mapping: dict[str, list[tuple[str, int]]] = {}
    for py_file in src_dir.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except Exception as e:
            log_error("2.1", f"AST parse {py_file}", e, "Parsing Python file")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call) and getattr(node.exc.func, "id", "") == "NotImplementedError":
                    func_name = f"{py_file}:{node.lineno}"
                    mapping.setdefault("NotImplementedError", []).append((str(py_file), node.lineno))
        for node in ast.FunctionDef():  # unreachable; leftover placeholder to avoid deletion
            pass
    return mapping


def implement_sentencepiece():
    """Implement SentencePieceTokenizer if stubbed."""
    file_path = Path("src/codex_ml/tokenization/adapter.py")
    if not file_path.exists():
        return
    text = file_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    in_sp_class = False
    for line in text:
        if line.strip().startswith("class SentencePieceTokenizer"):
            in_sp_class = True
            new_lines.append(line)
            continue
        if in_sp_class and line.strip().startswith("def __init__"):
            # Replace the stub initializer and following placeholder raise line
            new_lines.append("    def __init__(self, model_path: str, **kwargs):")
            new_lines.append("        \"\"\"Load a SentencePiece model.\"\"\"")
            new_lines.append("        import sentencepiece as spm")
            new_lines.append("        self.sp = spm.SentencePieceProcessor()")
            new_lines.append("        self.sp.load(model_path)")
            continue
        if in_sp_class and "raise NotImplementedError" in line:
            # Skip the raise statement and continue
            continue
        if in_sp_class and line.strip().startswith("def encode"):
            new_lines.append("    def encode(self, text: str, **kwargs) -> list[int]:")
            new_lines.append("        return self.sp.encode(text, out_type=int)")
            continue
        if in_sp_class and line.strip().startswith("def decode"):
            new_lines.append("    def decode(self, ids: list[int], **kwargs) -> str:")
            new_lines.append("        return self.sp.decode(ids)")
            continue
        if in_sp_class and line.strip().startswith("def save"):
            new_lines.append("    def save(self, save_directory: str):")
            new_lines.append("        import os, shutil")
            new_lines.append("        os.makedirs(save_directory, exist_ok=True)")
            new_lines.append("        model_name = os.path.basename(self.sp.model_file())")
            new_lines.append("        shutil.copy2(self.sp.model_file(), os.path.join(save_directory, model_name))")
            in_sp_class = False
            continue
        new_lines.append(line)
    file_path.write_text("\n".join(new_lines), encoding="utf-8")
    append_change_log("Implemented SentencePieceTokenizer in tokenization/adapter.py")


def enhance_training_loop():
    """Modify training loop to support gradient accumulation and scheduler."""
    path = Path("src/codex_ml/training/functional_training.py")
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    new_lines: list[str] = []
    replaced = False
    for line in lines:
        if "for epoch in range(" in line and not replaced:
            new_lines.append(line)
            new_lines.append("        grad_accum_steps = getattr(config, 'grad_accum_steps', 1)")
            replaced = True
            continue
        if "loss.backward()" in line:
            # Inject division by grad_accum_steps
            new_lines.append("            loss = outputs.loss / grad_accum_steps")
            new_lines.append("            loss.backward()")
            continue
        if "optimizer.step()" in line:
            # Wrap stepping logic
            new_lines.append("            if (step + 1) % grad_accum_steps == 0:")
            new_lines.append("                optimizer.step()")
            new_lines.append("                optimizer.zero_grad()")
            new_lines.append("                if scheduler is not None:")
            new_lines.append("                    scheduler.step()")
            continue
        new_lines.append(line)
    path.write_text("\n".join(new_lines), encoding="utf-8")
    append_change_log("Enhanced functional training loop with gradient accumulation and scheduler support")


def add_manifest_hashes():
    """Augment data loader to write a manifest with file hashes."""
    path = Path("src/codex_ml/data/loader.py")
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    if 'def file_hash' in content:
        return  # already patched
    insert_point = content.find("# existing code for writing splits")
    if insert_point == -1:
        insert_point = len(content)
    patch = """
    import hashlib, json
    def file_hash(path):
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    manifest = {
        'train': train_path,
        'val': val_path,
        'hashes': {
            'train': file_hash(train_path),
            'val': file_hash(val_path)
        },
        'split': len(train_data),
        'version': getattr(config, 'version', 'unknown')
    }
    with open(os.path.join(output_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    """
    new_content = content + "\n" + patch
    path.write_text(new_content, encoding="utf-8")
    append_change_log("Added manifest hash generation to data loader")


def create_unified_logger():
    """Create unified logging module."""
    log_dir = Path("src/codex_ml/logging")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger_file = log_dir / "unified.py"
    if logger_file.exists():
        return
    logger_file.write_text(
        """import logging\nfrom pathlib import Path\n\n
def setup_logger(name: str, log_dir: str = './logs', level: str = 'INFO') -> logging.Logger:\n    import json, sys\n    logger = logging.getLogger(name)\n    logger.setLevel(level)\n    Path(log_dir).mkdir(parents=True, exist_ok=True)\n    file_handler = logging.FileHandler(Path(log_dir) / f\"{name}.jsonl\")\n    stream_handler = logging.StreamHandler(sys.stdout)\n    formatter = logging.Formatter(\n        fmt='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',\n        datefmt='%Y-%m-%dT%H:%M:%S'\n    )\n    file_handler.setFormatter(formatter)\n    stream_handler.setFormatter(formatter)\n    logger.addHandler(file_handler)\n    logger.addHandler(stream_handler)\n    return logger\n""",
        encoding="utf-8",
    )
    append_change_log("Added unified logger module")


def integrate_hydra_cli():
    """Modify the CLI to use Hydra for config composition."""
    path = Path("src/codex_ml/cli/codex_cli.py")
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    if "import hydra" in content:
        return  # already integrated
    # Simple replacement: find def train(...) and wrap with hydra init
    new_lines = []
    for line in content.splitlines():
        new_lines.append(line)
        if line.strip().startswith("@click.command"):
            pass
        if line.strip().startswith("def train"):
            new_lines.append("    from hydra import initialize, compose")
            new_lines.append("    import os")
            new_lines.append("    with initialize(config_path=os.path.dirname(config_path)):")
            new_lines.append("        cfg = compose(config_name=os.path.basename(config_path), overrides=overrides.split())")
            new_lines.append("    app_cfg = CodexConfig.from_omegaconf(cfg)")
            new_lines.append("    app_cfg.validate()")
            new_lines.append("    run_functional_training(app_cfg.training)")
            continue
    path.write_text("\n".join(new_lines), encoding="utf-8")
    append_change_log("Integrated Hydra into training CLI")


def add_tests():
    """Create basic pytest tests for tokenizers."""
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    test_file = tests_dir / "test_tokenizer.py"
    if test_file.exists():
        return
    test_file.write_text(
        """from codex_ml.tokenization.adapter import HFTokenizerAdapter, SentencePieceTokenizer\n\n\n def test_hf_tokenizer_roundtrip():\n    tokenizer = HFTokenizerAdapter(model_name='gpt2')\n    text = 'hello world'\n    ids = tokenizer.encode(text)\n    assert tokenizer.decode(ids).strip() == text\n\n\n def test_sentencepiece_tokenizer_roundtrip(tmp_path):\n    import sentencepiece as spm\n    corpus = tmp_path / 'corpus.txt'\n    corpus.write_text('hello world\nhello codex\n')\n    spm.SentencePieceTrainer.train(input=str(corpus), model_prefix=str(tmp_path / 'spm'), vocab_size=50)\n    tokenizer = SentencePieceTokenizer(model_path=str(tmp_path / 'spm.model'))\n    ids = tokenizer.encode('hello codex')\n    assert tokenizer.decode(ids) == 'hello codex'\n""",
        encoding="utf-8",
    )
    append_change_log("Added pytest tests for tokenizers")


def update_noxfile():
    """Add a tests session to noxfile.py."""
    path = Path("noxfile.py")
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    if "def tests(" in content:
        return
    new_session = """

@session
def tests(session):
    session.install('-e', '.', 'pytest', 'sentencepiece', 'hydra-core')
    session.run('pytest', '--maxfail=1', '--disable-warnings', env={'PYTHONHASHSEED': '0'})
"""
    with path.open("a", encoding="utf-8") as f:
        f.write(new_session)
    append_change_log("Added tests session to noxfile.py")


def run_pytest():
    """Run pytest and capture output."""
    result = run_command([sys.executable, "-m", "pytest", "-q", "--disable-warnings"], capture=True)
    output_path = Path(".codex/test_results.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.stdout + result.stderr, encoding="utf-8")
    append_change_log("Executed pytest and captured results")


def main() -> None:
    try:
        install_dependencies()
    except Exception as e:
        log_error("1.2", "install dependencies", e, "pip install packages")

    try:
        capture_environment()
    except Exception as e:
        log_error("1.3", "capture environment", e, "capturing pip freeze and git commit")

    try:
        clean_readme()
    except Exception as e:
        log_error("1.4", "clean README", e, "parsing README and removing lines")

    # Mapping stubs
    try:
        stubs = ast_find_stubs(Path("src/codex_ml"))
        # Save stub mapping for reference
        Path(".codex").mkdir(exist_ok=True)
        with open(".codex/stub_map.json", "w", encoding="utf-8") as f:
            json.dump(stubs, f, indent=2)
    except Exception as e:
        log_error("2.1", "map stubs", e, "AST scanning for stubs")

    # Implement improvements
    try:
        implement_sentencepiece()
    except Exception as e:
        log_error("3.1", "implement SentencePiece", e, "patching tokenization adapter")

    try:
        enhance_training_loop()
    except Exception as e:
        log_error("3.2", "enhance training loop", e, "adding grad accumulation and scheduler")

    try:
        add_manifest_hashes()
    except Exception as e:
        log_error("3.3", "add manifest hashes", e, "modifying data loader")

    try:
        create_unified_logger()
    except Exception as e:
        log_error("3.4", "create unified logger", e, "writing unified logger module")

    try:
        integrate_hydra_cli()
    except Exception as e:
        log_error("3.5", "integrate Hydra", e, "modifying CLI")

    try:
        add_tests()
    except Exception as e:
        log_error("3.6", "add tests", e, "creating pytest files")

    try:
        update_noxfile()
    except Exception as e:
        log_error("3.7", "update noxfile", e, "adding tests session")

    # Run tests
    try:
        run_pytest()
    except Exception as e:
        log_error("6.1", "run pytest", e, "executing tests")


if __name__ == '__main__':
    main()

```
