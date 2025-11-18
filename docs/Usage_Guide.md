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

⚠️ **Prompt safety:** the training profile sanitises embedded datasets by
default. To inspect raw fixtures set `training.sanitize_prompts=false` on the
command line.

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
Disable prompt redaction with `sanitize_prompts=false` if you need to inspect
the untouched dataset.

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

## 7. Enable entry-point plugins

Third-party extensions can be loaded via Python entry points. Opt in by setting
`plugins.enable_entry_points=true` and overriding the groups as needed:

```bash
python -m codex_ml.cli.train plugins.enable_entry_points=true \
  plugins.entry_points.groups.tokenizers=my_project.tokenizers
```text

The loader is defensive—failures to import a plugin are logged and do not abort
the run.

## 8. Convert NDJSON metrics to CSV

Metrics writers emit newline-delimited JSON files under `artifacts/runs/…`.
Convert them to CSV with the helper in `tools/`:

```bash
python tools/ndjson_to_csv.py .codex/metrics/training.ndjson artifacts/runs/metrics.csv
```text

The repository ships a sample log at `samples/metrics_sample.ndjson` for quick
tests.

## 9. MCP Capability Validation

To validate MCP-related capabilities:

```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain mcp-protocol-surface
python scripts/space_traversal/audit_runner.py explain mcp-rate-limiting
```

Then inspect:

- `audit_artifacts/capabilities_raw.json` (presence of `mcp-*` IDs)
- `audit_artifacts/capabilities_scored.json` (scores & components)
- `audit_artifacts/gaps.json` (MCP gaps)
- Latest `reports/capability_matrix_*.md` (MCP rows in matrix)

See `MCP_IMPLEMENTATION_SUMMARY.md` for detailed information on MCP capabilities and their implementation.

## 10. Additional references

- [Quickstart walkthrough](../quickstart.md)
- [CLI reference](../CLI.md)
- [Logging guide](guides/LOGGING.md)

*Last reviewed:* 2025-10-19
