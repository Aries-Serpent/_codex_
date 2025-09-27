# Codex Quickstart

This quickstart demonstrates an end-to-end workflow entirely on your local
machine: tokenizer setup → training → evaluation.  All commands are
copy-pasteable and avoid network access by default.

## 1. Bootstrap the environment

```bash
uv sync --extra test --extra cli  # installs optional deps and the hydra.extra pytest plugin
source .venv/bin/activate
# or, if you prefer pip: pip install -e '.[test]' to stage the same extras
```
## 2. (Optional) prepare the offline defaults

To follow the offline-first examples you can populate the lightweight catalogue
bundled with Codex ML.  Copy or symlink the model, tokenizer, dataset and metric
artefacts into the directories below (relative to the repository root):

```text
artifacts/models/gpt2/
artifacts/models/tinyllama/
data/offline/tiny_corpus.txt
data/offline/weighted_accuracy.json
```
You can also set the environment variables described in
[`guides/offline_catalogue.md`](guides/offline_catalogue.md) to point
at alternative locations.  Skip this step entirely if you prefer the minimal
MiniLM baseline – the remaining commands continue to work.

## 3. Tokenize sample data

Register the toy tokenizer plugin and encode text without touching external
services.

```bash
python examples/tokenize.py
```
Expected output:

```json
{
  "text": "Codex makes registries fun!",
  "encoded": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
  "decoded": "Codex makes registries fun!"
}
```
## 4. Run a deterministic training session

```bash
export CODEX_MLFLOW_ENABLE=0  # keep MLflow disabled unless you opt-in
python examples/train_toy.py
# or redirect metrics: python -m codex_ml.train_loop --epochs 1 --art-dir artifacts/custom-metrics
```
The script writes checkpoints and NDJSON logs under `runs/examples/`.  Each run
creates a timestamped directory containing:

* `metrics.ndjson` – per-step metrics
* `metrics.json` – append-only list of metric payloads
* `environment.json` / `environment.ndjson` – runtime metadata and git commit
* `pip-freeze.txt` – dependency manifest captured automatically
* `dataset_checksums.json` – hashes for any dataset files passed via the training API
* `params.ndjson` – run parameters (seed, dataset, etc.)
* `config.json` / `config.ndjson` – resolved configuration snapshot
* `provenance.ndjson` – git commit, hostname and other reproducibility data

### Tune gradient accumulation & evaluation cadence

The functional trainer exposes the most common loop knobs directly on the
`training` config block:

| Setting | Description |
| --- | --- |
| `training.gradient_accumulation` | Accumulate gradients over multiple batches to fit larger effective batch sizes on limited hardware. |
| `training.amp_enable` | Toggle automatic mixed precision (AMP). Combine with `training.amp_dtype` to pick `fp16` or `bf16`. |
| `training.eval_every_epochs` | Run the lightweight evaluation loop every _n_ epochs. Set to a large value to skip eval. |
| `training.metrics_out` | Path to the append-only NDJSON log (defaults to `.codex/metrics.ndjson`). |

Evaluation metrics and training timing data are appended to the NDJSON file so
you can tail progress without any external services:

```bash
tail -f .codex/metrics.ndjson
```

## 5. Inspect results & aggregate metrics

```bash
python examples/mlflow_offline.py runs/examples/<latest-run>
python examples/evaluate_toy.py
```
Use the printed `mlflow ui --backend-store-uri ...` command to explore the run
offline.  TensorBoard summaries are saved alongside the run when enabled.

## 6. Next steps

* Fine-tune chat models via `examples/chat_finetune.py`
* Explore the registries and plugin system in `docs/dev/plugins.md`
* Link your own datasets via `docs/examples/training-configs.md`
