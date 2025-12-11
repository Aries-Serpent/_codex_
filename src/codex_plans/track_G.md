# Track G: Model Init, Config, Data, Docs, and Experiment Tracking

## 1. Model Initialization & LoRA/PEFT
- Introduce a `codex_model` module containing:
  - `ModelConfig` dataclass capturing base model name/path, dtype (float32/bfloat16/float16/auto), device selection (cpu/cuda/auto), and a flag for LoRA/PEFT.
  - `build_codex_model(cfg: ModelConfig) -> nn.Module` which loads a local pretrained checkpoint, sets device/dtype, and optionally applies LoRA/PEFT adapters via an optional dependency. If PEFT libraries are unavailable, skip and log a warning.
- Provide smoke tests for model creation on CPU with small dummy inputs, verifying deterministic behavior and trainable parameter counts when PEFT is enabled.

## 2. Hydra Configuration & Sweeps
- Establish a `conf/` directory with Hydra-friendly groups (`model/`, `data/`, `training/`, `experiment/`). Include `conf/config.yaml` setting default references to groups and global settings (`run.output_dir`, `seed`).
- Provide example experiment configs under `conf/experiment/` to override training parameters for quick debugging.
- Modify the training CLI (`cli/train_codex.py`) to support Hydra when installed via `@hydra.main(...)`, falling back to a simple config dict if Hydra is absent.
- Document how to run sweeps locally using Hydra's multirun syntax.

## 3. Data Handling: Splits & Caching
- Add a `codex_data` module implementing:
  - `DataConfig` capturing dataset path, split ratios, seed, and cache directory.
  - `DatasetSplits` dataclass containing train/val/test sets.
  - `load_dataset(cfg: DataConfig) -> DatasetSplits` that loads raw data using a loader function path, shuffles deterministically using the seed, partitions splits according to ratios, computes a cache key based on raw file paths/mtimes/config, and caches splits under `artifacts/cache/<dataset>`.
- Include tests verifying deterministic splits, correct ratios, and cache hits on repeated runs.

## 4. Documentation & Examples
- Build a `docs/` structure aligned with the Diataxis framework:
  - `tutorials/` with a step-by-step guide for setting up environment, training a small model, and analyzing results.
  - `howto/` with recipes for running audits, adding a new capability, or debugging gating failures.
  - `reference/` detailing CLI commands, config schemas, and artifact descriptions.
  - `explanation/` covering system architecture, Golden Harness rationale, reproducibility decisions, and safety considerations.
- Ensure docs are Markdown-only and reference local artifacts (`repo_audit_scorecard.md`, `model_regression_coverage.md`, etc.).

## 5. Experiment Tracking & Analysis
- Extend the tracking subsystem to support:
  - `RunInfo` capturing run_id, experiment_name, git_hash, data version IDs, config hashes, start/end timestamps.
  - Functions `start_run`, `finish_run`, `log_metric` writing NDJSON entries for run lifecycle events and metrics under `artifacts/experiments/<run_id>`.
- Create `scripts/analyze_experiments.py` to aggregate runs, compute best/median metrics per experiment, and emit `artifacts/experiment_summary.md`.
- Integrate these summaries into the audit scorecard and final report.

## Off-line & Safety Considerations
- All features must run offline without contacting external services (MLflow is optional and off by default).
- Avoid enabling any GitHub Actions or CI; ensure reproducibility via seeds and environment capture.

---
This plan outlines concrete modules, dataclasses, functions, tests, and documentation necessary to implement the Track G capabilities. Each component is scoped to operate locally and integrate seamlessly with existing codex modules and audit workflows.
