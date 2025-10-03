# Troubleshooting

## Tokenizer issues

* **`FileNotFoundError: tokenizer.json`** – ensure the model assets are cached
  locally or use the toy tokenizer plugin (`examples/tokenize.py`).
* **`transformers` missing** – install the optional dependencies via
  `uv sync --extra test`.

## Training hiccups

* **Empty dataset** – double-check the `training.texts` field or point the data
  loader registry at a valid dataset (`codex_ml.data.registry`).
* **Resume failures** – verify the `checkpoint_dir` contains `.pt` files; the
  new registries allow overriding the trainer if custom resume logic is needed.

## Offline PyTorch setup

* **`torch` skipped in pytest** – build a local CPU-only wheel cache before
  disconnecting. Running `tools/bootstrap_wheelhouse.sh -r requirements-dev.txt`
  creates `wheelhouse/` artifacts along with a matching `constraints.txt` file.
  Once generated, install with
  `python -m pip install --no-index --find-links ./wheelhouse torch` and rerun
  the regression gates.
* **Fresh environments without wheelhouse** – install the minimal CPU build via
  `uv pip install --no-deps --python $(which python) torch --index-url https://download.pytorch.org/whl/cpu`.
  This brings the training and checkpoint
  smoke tests back online without pulling the full CUDA stack.

## Experiment logging

* **No run directory** – confirm `tracking.output_dir` is writable and refer to
  [docs/experiments/README.md](experiments/README.md) for directory layout.
* **MLflow not available** – keep `CODEX_MLFLOW_ENABLE` unset or follow
  [docs/experiments/mlflow_offline.md](experiments/mlflow_offline.md) to run
  entirely offline.

## Plugins

* **Duplicate registration** – `RegistryConflictError` indicates a name clash;
  pick a new key or pass `override=True` explicitly.
* **Entry point not loading** – run `python -m importlib.metadata entry_points`
  to inspect the installed distributions and verify group names.
