# Optional Dependencies & Offline Fallbacks

Phase 4 formalises which third-party libraries are optional, how they surface in the
codebase, and what behaviour developers should expect when they are absent. A full
grep across `tests/` identified **370 guarded imports** via `pytest.importorskip`,
confirming that every optional integration has an explicit offline fallback.

## Exception Handling for Optional Dependencies (Updated 2025-12-13)

The repository uses a **broad exception handling pattern** for optional imports to ensure graceful degradation:

```python
try:
    from .loader import load_tokenizer
except (ModuleNotFoundError, ImportError, AttributeError):
    # AttributeError: torch stub (torch/__init__.py) raises this when PyTorch not installed
    # ImportError/ModuleNotFoundError: tokenizers/transformers missing
    load_tokenizer = None  # type: ignore[assignment]
```

**Why catch AttributeError?**
- The torch stub (`torch/__init__.py`) raises `AttributeError` instead of `ImportError` when PyTorch is not installed
- This is intentional behavior to provide clear error messages
- Modules in dependency chains (e.g., `codex_ml.utils`) Phase 5 trigger this during import

**Best Practices:**
1. Always catch `(ModuleNotFoundError, ImportError, AttributeError)` for optional imports
2. Set to `None` when import fails: `module_name = None  # type: ignore[assignment]`
3. Add inline comments explaining each exception type
4. Exclude from `__all__` when unavailable (append only in `else` block)

## Dependency overview

| Dependency | Purpose | Import Path(s) | Primary Tests / Features | Fallback Behaviour |
| --- | --- | --- | --- | --- |
| `torch` | Core tensor runtime for training, checkpoints, and metrics | `import torch` | `tests/training/*`, `tests/checkpointing/*`, `tests/models/*` | Training-focused suites skip; CLI defaults fall back to CPU-only stubs |
| `transformers` | Hugging Face tokenisers, models, and CLI bridges | `import transformers` | `tests/tokenizer_*`, `tests/test_cli_train_engine.py`, `tests/eval/*` | Tokeniser/transformer tests skip; CLI surfaces degrade to generic tokeniser |
| `datasets` | Hugging Face dataset wrappers and data factories | `import datasets` | `tests/data/test_hf_factory_compat.py`, `tests/eval/test_datasets_hf_disk.py` | Dataset-backed tests skip; training CLI prompts to stage local datasets |
| `accelerate` | Distributed + mixed precision execution for HF trainers | `import accelerate` | `tests/training/test_engine_hf_trainer*.py`, `tests/test_accelerate_shim.py` | Distributed training tests skip; CLI emits hint to install `accelerate` |
| `sentencepiece` / `tokenizers` | Subword tokenisation backends | `import sentencepiece`, `import tokenizers` | `tests/test_tokenizer_wrapper.py`, `tests/tokenization/test_tokenizer_cli.py` | Tokeniser CLI tests skip; runtime falls back to pure-Python tokeniser |
| `mlflow` | Experiment tracking + model registry hooks | `import mlflow` | `tests/tracking/test_mlflow_offline_guard.py`, `tests/monitoring/test_codex_logging_bootstrap.py` | Tracking integrations disable gracefully; NDJSON logging remains |
| `wandb` | Weights & Biases experiment logging | `import wandb` | `tests/monitoring/test_codex_logging_bootstrap.py` | W&B writers skip; run metadata captured locally |
| `hydra-core[hydra_plugins]` | Configuration composition + pytest plugin | `import hydra` | `tests/config/*`, `tests/test_cli_train_engine.py`, coverage nox session | Nox coverage session auto-installs plugin; config tests skip with guidance |
| `omegaconf` / `PyYAML` | Config schema parsing + CLI overrides | `import omegaconf`, `import yaml` | `tests/config/*`, `tests/cli/*` | CLI/config suites skip; CLI prompts to install `.[hydra]` |
| `typer` / `click` | CLI UX for manifests + tokeniser tooling | `import typer`, `import click` | `tests/cli/test_cli_manifest*.py`, `tests/unit/test_tokenizer_cli_feature_flag.py` | CLI tests skip; CLI entrypoints remain importable but subcommands disabled |
| `pandas` | Metrics/NDJSON summarisation | `import pandas` | `tests/tracking/test_ndjson_summarizer.py` | Summary helpers skip; raw NDJSON output remains |
| `duckdb` | Local analytics for metrics store | `import duckdb` | `tests/cli/test_metrics_store_duckdb_modes.py` | DuckDB-specific checks skip; CLI prints instructions to install extra |
| `fastapi` | Online inference API | `import fastapi` | `tests/test_api_infer_tokenizer.py`, `tests/test_api_secret_filter.py` | API tests skip; CLI warns that API mode is unavailable |
| `opacus` | Differential privacy training | `import opacus` | `tests/privacy/test_dp_training.py` | DP suites skip; rest of training flows unaffected |
| `numpy` | Numerical kernels for eval + checkpoint utilities | `import numpy` | `tests/test_metric_curves.py`, `tests/utils/test_checkpointing_core.py` | Specific metrics tests skip; core CLI continues |

## Skip taxonomy

| Area | Example Guards | Offline Notes |
| --- | --- | --- |
| Training stack | `tests/training/test_engine_hf_trainer.py` (torch, accelerate, datasets) | Offline developers can run smoke suites that rely on CPU-only mocks. |
| Tokenisation | `tests/tokenization/test_tokenizer_cli.py` (transformers, sentencepiece) | CLI commands emit actionable error messages when optional deps are missing. |
| Tracking & monitoring | `tests/tracking/test_mlflow_offline_guard.py` (mlflow, wandb) | Tracking extras default to NDJSON logging and offline dashboards. |
| Config / CLI | `tests/config/test_hydra_defaults.py` (hydra, omegaconf) | Coverage session now validates Hydra plugin presence before pytest. |
| API surface | `tests/test_api_secret_filter.py` (fastapi) | HTTP interfaces remain optional; CLI usage unaffected offline. |

## Installation guidance

* Stage minimal offline tooling:
  ```bash
  pip install -e '.[test-core]'  # hydra + pytest stack only
  ```
* Enable full ML + tracking stack when online:
  ```bash
  pip install -e '.[test,tracking,ml]'
  ```
* GPU workflows require CUDA wheels or the `Dockerfile.gpu` image.

Refer to the [Offline Testing Matrix](offline_testing.md) for curated command
recipes by environment tier.
