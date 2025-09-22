# Metric Registry

`codex_ml.metrics.registry` manages deterministic metrics and offers offline
friendly variants that rely on local artefacts.

## Built-in metrics

- `accuracy@token`, `ppl`, `exact_match`, `f1`, `dist-1`, `dist-2`, `bleu`,
  `rougeL` – standard deterministic metrics shipped with Codex ML.
- `offline:weighted-accuracy` – consumes a JSON file mapping class labels to
  weights. The resolver checks `CODEX_ML_WEIGHTED_ACCURACY_PATH`, then
  `${CODEX_ML_OFFLINE_METRICS_DIR}/weighted_accuracy.json`, and finally
  `${repo}/data/offline/weighted_accuracy.json`.

## Hydra fragment

```bash
python -m codex_ml.cli evaluate -cn config metrics/offline/weighted_accuracy
```

`configs/metrics/offline/weighted_accuracy.yaml` prepends
`offline:weighted-accuracy` to the evaluation metrics list and provides the
`weights_path` parameter using the offline lookup order.

## Direct usage

```python
from codex_ml.metrics.registry import get_metric

metric = get_metric("offline:weighted-accuracy")
score = metric(["cat", "dog"], ["cat", "dog"], weights_path="/tmp/weights.json")
```

The metric raises `FileNotFoundError` if the JSON file cannot be located using
the configured search paths, ensuring no network calls are attempted.
