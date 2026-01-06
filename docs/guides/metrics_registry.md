# [Guide]: Metrics Registry (PS-07)
> Generated: Previous Cycle-11-19 04:20:17 | Author: mbaetiong  
Roles: [Primary: Audit Orchestrator], [Secondary: Capability Cartographer] ⚡ Energy: 5  
Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️

## Overview
A unified registry for metrics supporting:
- Functional batch metrics (accuracy, precision, recall, F1, BLEU, ROUGE-L, perplexity)
- Class-based streaming metrics (StreamingAccuracy, StreamingLoss)

## Quickstart
```python
from src.codex_ml.metrics.base import BaseMetric
from src.codex_ml.metrics.classification import accuracy, f1, StreamingAccuracy
from src.codex_ml.metrics.streaming import StreamingLoss

# Functional metrics
score = accuracy(preds, labels)
f1_score = f1(preds, labels, positive=1)

# Streaming metrics
stream_acc = StreamingAccuracy()
stream_acc.reset()
stream_acc.update(preds_batch1, labels_batch1)
stream_acc.update(preds_batch2, labels_batch2)
final = stream_acc.compute()
```

## Notes
- Deterministic outputs for same inputs.
- No external network; generation metrics are minimal, dependency-free.
- Supports both batch and streaming computation patterns.
- All metrics inherit from BaseMetric ABC for consistency.
