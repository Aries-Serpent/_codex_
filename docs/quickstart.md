# Codex Quickstart

This quickstart demonstrates an end-to-end workflow entirely on your local
machine: tokenizer setup → training → evaluation.  All commands are
copy-pasteable and avoid network access by default.

## 1. Bootstrap the environment

```bash
uv sync --extra test  # installs optional deps: datasets, transformers, mlflow
source .venv/bin/activate
```

## 2. Tokenize sample data

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

## 3. Run a deterministic training session

```bash
export CODEX_MLFLOW_ENABLE=0  # keep MLflow disabled unless you opt-in
python examples/train_toy.py
```

The script writes checkpoints and NDJSON logs under `runs/examples/`.  Each run
creates a timestamped directory containing:

* `metrics.ndjson` – per-step metrics
* `params.ndjson` – run parameters (seed, dataset, etc.)
* `config.json` / `config.ndjson` – resolved configuration snapshot
* `provenance.ndjson` – git commit, hostname and other reproducibility data

## 4. Inspect results & aggregate metrics

```bash
python examples/mlflow_offline.py runs/examples/<latest-run>
python examples/evaluate_toy.py
```

Use the printed `mlflow ui --backend-store-uri ...` command to explore the run
offline.  TensorBoard summaries are saved alongside the run when enabled.

## 5. Next steps

* Fine-tune chat models via `examples/chat_finetune.py`
* Explore the registries and plugin system in `docs/dev/plugins.md`
* Link your own datasets via `docs/examples/training-configs.md`
