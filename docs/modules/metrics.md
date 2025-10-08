# Metrics utilities

Codex ML bundles lightweight helpers for computing evaluation metrics
without pulling in heavy external dependencies.  The
`codex_ml.metrics.evaluator` module focuses on deriving metrics directly
from model outputs and batch metadata.

## Stable import surface

Use a stable API layer for common metrics:

```python
from codex_ml.metrics.api import accuracy, micro_f1, macro_f1, perplexity, token_accuracy, bleu, rouge_l
```

See also: [Tests Overview](../tests_overview.md)

## `batch_metrics`

```python
from codex_ml.metrics.evaluator import batch_metrics
```

* **Loss & perplexity** – if the model output exposes a scalar `loss`
  attribute (or dict key), `batch_metrics` records it alongside its
  exponentiated `perplexity`.
* **Token accuracy** – logits paired with a `labels` tensor yield
  `token_accuracy`, ignoring the conventional `-100` masked labels used by
  HuggingFace models.
* **Text scores** – when batches include `pred_text` and `target_text`
  fields, whitespace token F1 and exact-match scores are computed with no
  additional dependencies.

The helper returns a dictionary, making it trivial to aggregate metrics
across evaluation batches or append them to NDJSON logs.
