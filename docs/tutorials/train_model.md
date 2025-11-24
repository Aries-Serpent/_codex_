# Tutorial: training a Codex model offline

This walkthrough uses the new `codex_ml.codex_model` and `codex_ml.codex_data`
helpers to run a deterministic training loop without external services.

1. Prepare a JSONL dataset:
   ```bash
   cat > data/sample.jsonl <<'JSON'
   {"text": "hello", "label": 0}
   {"text": "world", "label": 1}
   JSON
   ```
2. Configure the data split in `conf/data/local.yaml` by adjusting
   `train_ratio`, `val_ratio`, and `test_ratio`. Caches are written to
   `artifacts/cache/<dataset>/` using a content-derived key.
3. Launch training with Hydra (if installed):
   ```bash
   python -m codex_ml.cli.hydra_entry data.dataset_path=data/sample.jsonl training.max_epochs=2
   ```
   Without Hydra, `codex-train` falls back to the minimal config and still runs
   locally.
4. Inspect cached splits:
   ```bash
   ls artifacts/cache/sample
   ```
5. Review run artifacts in `artifacts/experiments/<run_id>/events.ndjson` and
   the aggregated markdown summary in `artifacts/experiment_summary.md`.

The `ModelConfig` dataclass accepts a local checkpoint path plus optional LoRA
parameters. When `enable_lora=true`, the builder wraps the model with PEFT
adapters (if the dependency is present).
