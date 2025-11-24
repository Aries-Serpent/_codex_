# Getting started with Track G primitives

This tutorial keeps everything offline and deterministic. The steps rely on the
new Hydra-ready `conf/` presets and the minimal training fallback so you can run
on CPU-only machines.

1. Install dependencies (CPU-safe):
   ```bash
   pip install -e .[ml]
   ```
2. Inspect the base configuration:
   ```bash
   python -m codex_ml.cli.hydra_entry --cfg job --resolve
   ```
   The root config lives in `conf/config.yaml` with grouped defaults in
   `conf/model/`, `conf/data/`, `conf/training/`, and `conf/experiment/`.
3. Run a minimal offline training pass (works without Hydra installed):
   ```bash
   codex-train --probe-json
   ```
   The CLI generates a local dataset if missing, builds a checkpoint-backed
   model, and logs an experiment under `artifacts/experiments/`.
4. View experiment summaries:
   ```bash
   python scripts/analyze_experiments.py --base-dir artifacts/experiments
   cat artifacts/experiment_summary.md
   ```
5. Explore cached splits in `artifacts/cache/<dataset>` and reload them with
   `codex_ml.codex_data.load_dataset`.

For a richer run, point `data.dataset_path` at your JSONL dataset and enable
LoRA by setting `model.enable_lora=true` (requires `peft`).
