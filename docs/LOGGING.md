# Local Logging & Tracking

This repository uses **local-only** logging utilities to keep smoke tests hermetic.

## MLflow (file backend)

- Default: the helpers in `src/logging_utils.py` set `MLFLOW_TRACKING_URI` to `file:./mlruns` when `offline=True`.
- Customize the directory by exporting an absolute path:

```bash
export MLFLOW_TRACKING_URI="file:/absolute/path/to/mlruns"
```

References: MLflow tracking URIs and the file store backend.[^mlflow]

## TensorBoard

Use PyTorch's `SummaryWriter` to emit event files locally:

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("./runs")
writer.add_scalar("loss", 0.123, 1)
```

Reference: PyTorch TensorBoard utilities.[^tensorboard]

## NDJSON & CSV outputs

- **NDJSON**: emit one JSON object per line; prefer the `.ndjson` extension for clarity.[^ndjson]
- **CSV**: use Python's `csv.DictWriter` for schema-aware tabular exports.[^csv]

[^mlflow]: https://mlflow.org/docs/latest/tracking.html#file-store
[^tensorboard]: https://pytorch.org/docs/stable/tensorboard.html
[^ndjson]: https://github.com/ndjson/ndjson-spec
[^csv]: https://docs.python.org/3/library/csv.html
