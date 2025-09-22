# Offline default catalogue

Codex ML now ships a small catalogue of offline-ready components spanning
models, tokenizers, datasets and metrics.  This guide summarises the expected
local file layout and shows how to activate each default without relying on
network access.

## Directory layout

Place the unpacked artefacts under the repository root so the registry helpers
can resolve them deterministically:

```
artifacts/
  models/
    gpt2/
      config.json
      pytorch_model.bin
      tokenizer.json  # optional: kept here for parity with HF caches
    tinyllama/
      config.json
      pytorch_model.bin
      tokenizer.model
      tokenizer_config.json

data/
  offline/
    tiny_corpus.txt
    weighted_accuracy.json
```

You may also point the loaders at bespoke directories via the following
environment variables:

- `CODEX_ML_OFFLINE_MODELS_DIR` (shared models/tokenizers root)
- `CODEX_ML_GPT2_PATH`, `CODEX_ML_GPT2_TOKENIZER_PATH`
- `CODEX_ML_TINYLLAMA_PATH`, `CODEX_ML_TINYLLAMA_TOKENIZER_PATH`
- `CODEX_ML_OFFLINE_DATASETS_DIR`
- `CODEX_ML_TINY_CORPUS_PATH`
- `CODEX_ML_OFFLINE_METRICS_DIR`
- `CODEX_ML_WEIGHTED_ACCURACY_PATH`

## Hydra overrides

Each component has a dedicated Hydra fragment so offline configurations can be
composed declaratively:

```bash
python -m codex_ml.cli train \
  -cn config \
  model=offline/gpt2 \
  tokenizer=offline/gpt2 \
  data=offline/tiny_corpus \
  training=offline/functional \
  interfaces=offline
```

The shortcut preset ``offline/catalogue`` mirrors ``config.yaml`` while
activating every offline fragment in one go:

```bash
python -m codex_ml.cli train -cn offline/catalogue
```

Evaluations can opt into the weighted accuracy baseline with either of the
configurations above or manually via:

```bash
python -m codex_ml.cli evaluate -cn config metrics/offline/weighted_accuracy
```

The fragments live under `configs/{model,tokenizer,data,metrics}/offline/` and
mirror the directory layout above.

## Accessing the catalogue programmatically

The plugin registries expose the same defaults so integration tests and user
code can fetch components without importing the lower-level registries:

```python
from codex_ml.plugins.registries import datasets, metrics, models, reward_models, trainers

model = models.resolve_and_instantiate("gpt2-offline", {"local_path": "./artifacts/models/gpt2"})
records = datasets.resolve_and_instantiate("offline:tiny-corpus", path="./data/offline/tiny_corpus.txt")
weighted_acc = metrics.resolve_and_instantiate("offline:weighted-accuracy")
trainer = trainers.resolve_and_instantiate("offline:functional")
heuristic_rm = reward_models.resolve_and_instantiate("offline:heuristic")
```

Missing files raise `FileNotFoundError` with the list of searched locations,
ensuring offline environments fail fast instead of silently contacting remote
endpoints.

## Inspecting entries from the CLI

The Typer-powered plugin CLI exposes the bundled catalogue and highlights
whether entry-point discovery succeeds. Example invocations:

```bash
python -m codex_ml.cli.plugins_cli list models
python -m codex_ml.cli.plugins_cli list datasets
python -m codex_ml.cli.plugins_cli list metrics
python -m codex_ml.cli.plugins_cli list trainers
python -m codex_ml.cli.plugins_cli list reward_models
```

All commands run entirely offline; if a requested asset is missing, the
registry surfaces the precise paths that were checked.

## Opting out

Projects that prefer a minimal footprint can skip the overrides above and stick
with the tiny built-ins:

- Use `model.name=MiniLM` to keep the in-repo transformer stub.
- Use `tokenizer.name=hf` with `name_or_path` pointing to a minimal vocabulary.
- Remove `data=offline/tiny_corpus` and supply your own `dataset_loader.path`.
- Drop `metrics/offline/weighted_accuracy` to avoid shipping JSON weights.

These choices keep the installation lightweight while leaving the offline
catalogue available for teams that need reproducible baselines.
