# Local Logging & Tracking

This repository uses **local-only** logging:

## MLflow (file backend)

- Default: `MLFLOW_TRACKING_URI` is set to `file:./mlruns` when using helpers in `logging_utils.py`.
- To customize:

```bash
export MLFLOW_TRACKING_URI="file:/absolute/path/to/mlruns"
```

References: MLflow file backend / tracking URIs. ([mlflow.org][1])

## TensorBoard

Use PyTorch’s `SummaryWriter`:

```python
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter("./runs")
writer.add_scalar("loss", 0.123, 1)
```

Reference: PyTorch TensorBoard utilities. ([docs.pytorch.org][2])

## NDJSON & CSV outputs

- **NDJSON**: one JSON object per line; prefer the `.ndjson` extension. ([GitHub][3])
- **CSV**: use Python’s `csv.DictWriter` for tabular outputs. ([docs.python.org][4])

[1]: https://mlflow.org/docs/latest/ml/tracking/backend-stores?utm_source=chatgpt.com "Backend Stores | MLflow"
[2]: https://docs.pytorch.org/docs/stable/tensorboard?utm_source=chatgpt.com "torch.utils.tensorboard — PyTorch 2.8 documentation"
[3]: https://github.com/ndjson/ndjson-spec?utm_source=chatgpt.com "GitHub - ndjson/ndjson-spec: Specification"
[4]: https://docs.python.org/3/library/csv.html?utm_source=chatgpt.com "csv — CSV File Reading and Writing — Python 3.14.0 documentation"
