# Offline Quickstart & Reproducibility Guide

This guide shows how to run **fully offline**, emit local artifacts, and keep runs **deterministic**.

## 1) Determinism (PyTorch)

Enable deterministic algorithms and fixed seeds for repeatability:

```python
import os, random, numpy as np, torch
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")  # if using CUDA
random.seed(0); np.random.seed(0); torch.manual_seed(0)
torch.use_deterministic_algorithms(True)  # throws if an op is non-deterministic
```

Notes: Determinism can reduce performance and certain ops may error—prefer explicit toggles in smoke tests.

## 2) Local-only tracking (MLflow file backend)

Default behavior: if you don't set anything, the repo bootstraps MLflow to a **local file store**:

```bash
# default chosen by repo if unset:
export MLFLOW_TRACKING_URI="file:./artifacts/mlruns"
```

To use a remote tracking server, **opt in** explicitly:

```bash
export MLFLOW_TRACKING_URI="http://localhost:5000"
```

This prevents accidental remote logging while keeping remote usage intentional.

## 3) Tokenizer sanity checks

Use the provided tests to confirm encode/decode presence and padding/truncation invariants are stable
without requiring SentencePiece to be installed at runtime (tests skip cleanly if optional deps are missing).

Run targeted tests:

```bash
pytest -q tests/tokenization/test_roundtrip_basic.py tests/tokenization/test_padding_truncation_ext.py -k "encode_decode_presence or padding or truncation"
```

## 4) Hydra defaults (example)

We include `conf/examples/config_minimal.yaml` to demonstrate a small, portable **defaults list** and override style.
This file is non-invasive and safe to copy into your own config tree if desired.

## 5) Coverage artifacts (local only)

Use `nox -s coverage_html` to produce `artifacts/coverage/html/index.html` and `artifacts/coverage/coverage.xml` locally.
These are emitted without touching any CI or remote services.
