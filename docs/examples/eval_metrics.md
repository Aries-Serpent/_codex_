# Evaluation & Metrics

Compute average eval loss, perplexity, and token-level accuracy per epoch.

```python
from codex_ml.training.eval import evaluate
from codex_ml.metrics.evaluator import batch_metrics

rec = evaluate(model, val_loader, loss_fn=lambda outputs, batch: outputs.loss, metrics_fn=batch_metrics)
print(rec)
```

NDJSON rows are appended to `.codex/metrics.ndjson` during training.
