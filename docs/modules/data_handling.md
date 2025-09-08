# Data Handling

Utilities under `src/codex_ml/data/` provide flexible ingestion of text
datasets.  `load_dataset` automatically detects the input format:

- **Plain text (`.txt`/`.md`)** – one example per line.
- **NDJSON (`.jsonl`/`.ndjson`)** – expects a `text` field in each object.
- **CSV (`.csv`)** – expects a `text` column.

Loaded examples can be cached to disk by supplying a `cache_dir`; subsequent
calls reuse the cached file for deterministic results.  Optional safety
filtering is available via the `safety_filter_enabled` flag which applies the
redaction filters in `codex_ml.safety.filters`.

Dataset splitting and shuffling are handled by `codex_ml.data_utils.split_dataset`.
Passing a `seed` ensures reproducible splits across runs.

Configuration keys for these features live in `configs/data/base.yaml`:

```yaml
dataset_path: null
val_split: 0.1
test_split: 0.1
cache_dataset: false
safety_filter_enabled: false
encoding: utf-8
```

Setting `cache_dataset=true` enables on-disk caching, while
`safety_filter_enabled=true` redacts sensitive content during loading.

Datasets may optionally include a `language` column.  Use the `language` key in
`configs/data/base.yaml` to filter examples when loading.
