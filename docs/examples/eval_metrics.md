# Evaluation & Metrics

Compute average evaluation loss, perplexity, and token-level accuracy per epoch.

```python
import torch

from codex_ml.training.eval import evaluate
from codex_ml.metrics.evaluator import batch_metrics

record = evaluate(
    model,
    val_loader,
    loss_fn=lambda outputs, batch: outputs.loss,
    metrics_fn=batch_metrics,
    device="cuda" if torch.cuda.is_available() else "cpu",
)
print(record)
```

The helper runs in `torch.no_grad()` and restores the model's training mode.  The
returned dictionary includes `eval_loss`, `loss`, `perplexity`, and
`token_accuracy` when the outputs expose logits and the batch carries `labels`.

NDJSON rows are appended to `.codex/metrics.ndjson` during training.
