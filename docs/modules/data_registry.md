# Dataset Registry

`codex_ml.data.registry` exposes dataset loaders that can operate entirely
offline. Each loader is registered by name and can be accessed through
`codex_ml.data.registry.get_dataset` or Hydra configuration fragments.

## Built-in loaders

- `lines` – loads plain-text files and optionally shuffles or emits manifests.
- `offline:tiny-corpus` – resolves a tiny text fixture from disk. The loader
  probes `CODEX_ML_TINY_CORPUS_PATH`, then
  `${CODEX_ML_OFFLINE_DATASETS_DIR}/tiny_corpus.txt`, and finally
  `${repo}/data/offline/tiny_corpus.txt`.

## Using Hydra

```bash
python -m codex_ml.cli train -cn config data=offline/tiny_corpus
```
`configs/data/offline/tiny_corpus.yaml` binds `dataset_loader.name` to
`offline:tiny-corpus` and sets the `path` fallback chain to match the lookup
order above. Override `dataset_loader.path` to use a bespoke fixture.

## Manual invocation

```python
from codex_ml.data.registry import get_dataset

records = get_dataset(
    "offline:tiny-corpus",
    path="/path/to/tiny_corpus.txt",
    shuffle=False,
)
```
The loader raises `FileNotFoundError` if none of the offline paths exist,
preventing accidental network calls.
