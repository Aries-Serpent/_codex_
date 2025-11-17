# Usage Guide: Codex ML Offline Workflow (v1.2.0)

This guide distills the end-to-end workflow for running Codex ML completely
offline. Commands assume you are in the repository root.

## 1. Environment bootstrap (lock file first)

```bash
uv pip sync requirements/lock.txt  # preferred, uses the pinned lock file
# fallback when uv is unavailable
env PYTHONWARNINGS=default pip install -r requirements/lock.txt
```text

Create and activate a virtual environment before syncing dependencies. The lock
file captures the cached Hydra defaults and extension versions that the training
and evaluation CLIs expect.

## 2. Run a quick training session

```bash
python -m codex_ml.cli.train \
  training.trainer.epochs=1 \
  training.batch_size=2 \
  training.output_dir=artifacts/runs/quickstart \
  training.logging.enable_tensorboard=false \
  training.logging.enable_mlflow=false
```text

The example composes the default Hydra configuration bundle (model, data, and
trainer) and writes checkpoints plus metrics under
`artifacts/runs/quickstart/`. Override parameters inline to explore different
presets without editing YAML.

## 3. Evaluate a saved checkpoint

```bash
python -m codex_ml.cli.evaluate \
  evaluation.checkpoint=artifacts/runs/quickstart/checkpoints/last.ckpt \
  evaluation.dataset_path=data/offline/sample.jsonl \
  evaluation.metrics='["accuracy"]' \
  evaluation.output_dir=artifacts/eval/quickstart
```text

Evaluation reuses the cached tokenizer and dataset defaults recorded in the
Hydra tree. Append `--log-metrics .codex/metrics/eval.ndjson` to persist a
machine-readable summary.

## 4. Tokenizer CLI essentials

```bash
python -m tokenization.cli vocab tokenization/artifacts/example_tokenizer
python -m tokenization.cli encode tokenization/artifacts/example_tokenizer "hello world"
python -m tokenization.cli decode tokenization/artifacts/example_tokenizer "1,2,3"
```text

Use `python -m tokenization.cli --help` to list subcommands. Tokenizer commands
respect offline caches configured via `TRANSFORMERS_OFFLINE=1` and related
environment variables, so they never reach remote registries.

## 5. Offline testing workflow

```bash
nox -s tests_offline
# or run the focused trainer tests with pytest
env TRANSFORMERS_OFFLINE=1 WANDB_MODE=offline PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/training -q
```text

These commands keep unit tests hermetic by forcing offline dataset loading and
wandb logging. Inspect `.codex/metrics/` for NDJSON outputs emitted during the
runs.

## 6. Inspect cached Hydra defaults

```bash
python -m codex_ml.cli.config --info defaults
python -m codex_ml.cli.config training.trainer.epochs=2 logging.format=ndjson
```text

Hydra resolves the defaults list from the lock-file snapshot, so overrides are
deterministic. The `--info defaults` flag prints the composed order if you need
to confirm which config group contributes a value.

## 7. Additional references

- [Quickstart walkthrough](../quickstart.md)
- [CLI reference](../CLI.md)
- [Logging guide](guides/LOGGING.md)

*Last reviewed:* 2025-10-19
