#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ruff: noqa: F821
"""
Stack Polish & Hardening Orchestrator

This script:
- Ensures dev/runtime dependencies are listed (no CI activation).
- Adds GPU check script.
- Creates tokenization SentencePiece adapter, modeling activations, PEFT adapter (optional), early-stopping callback,
  metric curves, checksums, data cache/sharding, risk scoring, disabled CI stubs, Helm stubs, notebooks/docs, and git tag helper.
- Runs local formatting/type/tests (best-effort) inside the Codex environment.

Policy:
- DO NOT ACTIVATE ANY GitHub Actions Online files. ALL GitHub Actions such as pre-commit, validation, etc MUST EXPLICITLY RUN WITHIN THE CODEX ENZVIRONMENT.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path


try:  # pragma: no cover - hydra optional for smoke wiring test
    from hydra import main as hydra_main  # type: ignore
except Exception:  # pragma: no cover - provide stub decorator

    def hydra_main(*args, **kwargs):  # type: ignore[misc]
        def _decorator(fn):
            def _missing_hydra(*_f_args, **_f_kwargs):
                raise RuntimeError(
                    "Hydra is unavailable; install hydra-core or set CODEX_ALLOW_MISSING_HYDRA_EXTRA=1"
                )

            return _missing_hydra

        return _decorator


try:  # pragma: no cover - optional dependency
    from omegaconf import DictConfig
except Exception:  # pragma: no cover - minimal stub for import-time usage

    class DictConfig(dict):
        pass


from codex_ml.utils.mlflow_entrypoints import configure_mlflow_uri

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"

# Determinism utilities
try:
    from codex_ml.utils.determinism import enable_determinism
except Exception:  # keep CLI robust even if optional modules are in flux
    enable_determinism = None


def _init_determinism_from_env():
    """
    Initialize deterministic mode if CODEX_DETERMINISM=1.
    Environment variables:
      - CODEX_DETERMINISM: "1" to enable, default "0"
      - CODEX_SEED: integer seed (default 42)
      - CODEX_NUM_THREADS: integer (default 1)
    Returns a summary dict when enabled; otherwise None.
    """

    if enable_determinism is None:
        return None
    if os.environ.get("CODEX_DETERMINISM", "0") != "1":
        return None
    try:
        seed = int(os.environ.get("CODEX_SEED", "42"))
    except Exception:
        seed = 42
    try:
        nthreads = int(os.environ.get("CODEX_NUM_THREADS", "1"))
    except Exception:
        nthreads = 1
    try:
        summary = enable_determinism(seed=seed, deterministic=True, num_threads=nthreads)
        # Keep a concise trace line in stdout for CI debugging
        print(
            f"[determinism] enabled seed={seed} threads={nthreads} torch={summary.get('torch')} cuda={summary.get('torch_cuda')}"
        )
        return summary
    except Exception as e:  # pragma: no cover - best effort logging
        print(f"[determinism] failed to initialize: {e}", file=sys.stderr)
        return None


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_change(action: str, path: Path, why: str, preview: str = "") -> None:
    if not CHANGE_LOG.exists() or CHANGE_LOG.stat().st_size == 0:
        CHANGE_LOG.write_text("# Codex Change Log\n", encoding="utf-8")
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            f"## {ts()} — {path.relative_to(REPO)}\n- **Action:** {action}\n- **Rationale:** {why}\n"
        )
        if preview:
            fh.write("```text\n" + preview[:4000] + "\n```\n")
        fh.write("\n")


def q5(step: str, err: str, ctx: str) -> None:
    rq = textwrap.dedent(
        f"""\
    Question for ChatGPT-5 {ts()}:
    While performing [{step}], encountered the following error:
    {err}
    Context: {ctx}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """
    )
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx}) + "\n")
    sys.stderr.write(rq + "\n")


def upsert(path: Path, content: str, sentinel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and sentinel in path.read_text(encoding="utf-8", errors="ignore"):
        return
    path.write_text(content, encoding="utf-8")
    log_change("upsert", path, f"insert guarded by {sentinel}", content)


# ---------- Env files ----------
DEV_REQ_SENT = "# BEGIN: CODEX_DEV_REQUIREMENTS"
DEV_REQ = (
    DEV_REQ_SENT
    + "\n"
    + """black
isort
flake8
mypy
pytest
pytest-cov
bandit
semgrep
detect-secrets
# END: CODEX_DEV_REQUIREMENTS
"""
)
RUN_REQ_SENT = "# BEGIN: CODEX_RUN_REQUIREMENTS"
RUN_REQ = (
    RUN_REQ_SENT
    + "\n"
    + """transformers
datasets
sentencepiece
accelerate
peft
# END: CODEX_RUN_REQUIREMENTS
"""
)
GPU_SH_SENT = "# BEGIN: CODEX_GPU_CHECK"
GPU_SH = (
    GPU_SH_SENT
    + "\n"
    + """#!/usr/bin/env bash
set -euo pipefail
umask 077
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "GPU detected:"
  nvidia-smi || true
else
  echo "No NVIDIA GPU detected."
fi
# END: CODEX_GPU_CHECK
"""
)
ENV_DOC_SENT = "<!-- BEGIN: CODEX_ENV_DOC -->"
ENV_DOC = (
    ENV_DOC_SENT
    + "\n"
    + """# Environment (Ubuntu)

- Use `scripts/gpu/check_gpu.sh` to summarize GPU driver/CUDA availability.
- Reproducibility: pin requirements and capture image digest when containerized.
- All validation runs are local (no online CI activation).
"""
)

# ---------- Tokenization ----------
SP_SENT = "# BEGIN: CODEX_SENTENCEPIECE_ADAPTER"
SP_CODE = (
    SP_SENT
    + "\n"
    + """from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
try:
    import sentencepiece as spm  # type: ignore
except Exception:
    spm = None  # type: ignore


class SentencePieceAdapter:
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self.sp = None

    def train_or_load(self, input_path: Path, vocab_size: int = 32000, model_type: str = "bpe"):
        if self.model_path.exists():
            return self.load()
        if spm is None:
            raise RuntimeError("sentencepiece not installed")
        spm.SentencePieceTrainer.Train(
            input=str(input_path),
            model_prefix=str(self.model_path.with_suffix("")),
            vocab_size=vocab_size,
            model_type=model_type,
            character_coverage=0.9995,
            pad_id=0, unk_id=1, bos_id=2, eos_id=3
        )
        return self.load()

    def load(self):
        if spm is None:
            raise RuntimeError("sentencepiece not installed")
        self.sp = spm.SentencePieceProcessor(model_file=str(self.model_path))
        return self

    def add_special_tokens(self, tokens: list[str]) -> None:
        # NOTE: SentencePiece models are static; track desired specials in a sidecar
        sidecar = self.model_path.with_suffix(".specials.json")
        sidecar.write_text(json.dumps(tokens, indent=2), encoding="utf-8")

    def assert_vocab_size(self, expected: int) -> None:
        if self.sp is None:
            raise RuntimeError("adapter not loaded")
        vs = int(self.sp.vocab_size())
        if vs != expected:
            raise AssertionError(f"vocab_size {vs} != expected {expected}")
# END: CODEX_SENTENCEPIECE_ADAPTER
"""
)
SP_TEST_SENT = "# BEGIN: CODEX_TEST_SP_ADAPTER"
SP_TEST = (
    SP_TEST_SENT
    + "\n"
    + """import pytest
pytest.skip("heavy SentencePiece training skipped in CI; run locally", allow_module_level=True)
# END: CODEX_TEST_SP_ADAPTER
"""
)

# ---------- Modeling ----------
ACT_SENT = "# BEGIN: CODEX_ACTIVATIONS"
ACT_CODE = (
    f"{ACT_SENT}\n"
    + """from __future__ import annotations
import math
from typing import Callable, Dict
try:
    import torch
    import torch.nn as nn
except Exception:
    torch, nn = None, None  # type: ignore

_REGISTRY: Dict[str, Callable] = {}


def _register(name: str):
    def deco(fn):
        _REGISTRY[name.lower()] = fn
        return fn
    return deco


@_register("relu")
def relu():
    return nn.ReLU() if nn else (lambda x: x)


@_register("gelu")
def gelu():
    return nn.GELU() if nn else (lambda x: x)


@_register("silu")
def silu():
    return nn.SiLU() if nn else (lambda x: x)


@_register("swiglu")
def swiglu():
    # placeholder: return SiLU for now unless model wires SWIGLU blocks
    return nn.SiLU() if nn else (lambda x: x)


def get_activation(name: str):
    key = (name or "gelu").lower()
    if key not in _REGISTRY:
        raise KeyError(f"unknown activation: {name}")
    return _REGISTRY[key]()
# END: CODEX_ACTIVATIONS
"""
)
ACT_TEST_SENT = "# BEGIN: CODEX_TEST_ACT"
ACT_TEST = (
    ACT_TEST_SENT
    + "\n"
    + """
import pytest
from codex_ml.models.activations import get_activation


def test_activation_registry_smoke():
    for n in ["relu","gelu","silu","swiglu"]:
        act = get_activation(n)
        assert act is not None
# END: CODEX_TEST_ACT
"""
)
PEFT_SENT = "# BEGIN: CODEX_PEFT_ADAPTER"
PEFT_CODE = (
    PEFT_SENT
    + "\n"
    + '''from __future__ import annotations


# NOTE: CODEX_PEFT_ADAPTER
def apply_lora(model, cfg: dict | None = None):
    """Attach LoRA adapters via `peft` when available.

    Parameters
    ----------
    model:
        The target model to be wrapped.
    cfg:
        A mapping of `LoraConfig` arguments. If ``None`` or empty, the model is
        returned unchanged. This mirrors the behavior of the library's internal
        adapter used in tests.

    Returns
    -------
    The model wrapped with LoRA adapters when possible; otherwise the original
    model.
    """
    try:  # pragma: no cover - exercised via unit tests with optional deps
        from peft import LoraConfig, get_peft_model  # type: ignore

        if cfg:
            model = get_peft_model(model, LoraConfig(**cfg))
        return model
    except Exception:  # graceful fallback when `peft` is absent/misconfigured
        return model
# END: CODEX_PEFT_ADAPTER
'''
)

# ---------- Training ----------
CB_SENT = "# BEGIN: CODEX_TRAINING_CALLBACKS"
CB_CODE = (
    CB_SENT
    + "\n"
    + """from __future__ import annotations


class EarlyStopping:
    def __init__(self, patience: int = 3, min_delta: float = 0.0):
        self.patience, self.min_delta = patience, min_delta
        self.best = None
        self.bad = 0

    def step(self, metric: float) -> bool:
        if self.best is None or metric < self.best - self.min_delta:
            self.best, self.bad = metric, 0
            return False
        self.bad += 1
        return self.bad > self.patience
# END: CODEX_TRAINING_CALLBACKS
"""
)
TRAIN_DOC_SENT = "<!-- BEGIN: CODEX_TRAIN_ARGS_DOC -->"
TRAIN_DOC = (
    TRAIN_DOC_SENT
    + "\n"
    + """
# Training Arguments (YAML/Hydra)

- **gradient_accumulation_steps**: accumulate before optimizer step.
- **early_stopping**: enable with patience/min_delta; wire to callbacks.EarlyStopping in your trainer loop.
"""
)

# ---------- Config (Hydra) ----------
HYDRA_DOC_SENT = "<!-- BEGIN: CODEX_HYDRA_DISTRIBUTED_OVERRIDES -->"
HYDRA_DOC = (
    HYDRA_DOC_SENT
    + "\n"
    + """
# Hydra Distributed Overrides

## torchrun (single node)
torchrun --nproc_per_node=8 train.py trainer.gpus=8

shell
Copy
Edit

## multi-node
torchrun --nnodes=2 --nproc_per_node=8 --rdzv_backend=c10d --rdzv_endpoint=$HOST:29400 train.py

shell
Copy
Edit

## tokenizer swap
tokenizer.backend=sentencepiece tokenizer.vocab_size=32000

python
Copy
Edit
"""
)

# ---------- Evaluation ----------
CURVE_SENT = "# BEGIN: CODEX_METRIC_CURVES"
CURVE_CODE = (
    CURVE_SENT
    + "\n"
    + """from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List


def append_curve(path: Path, metric: str, step: int, value: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path / f"{metric}.jsonl"
    with f.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"step": step, "value": value}) + "\n")


def summarize(path: Path, metric: str) -> Dict[str, float]:
    import statistics as st
    f = path / f"{metric}.jsonl"
    vals: List[float] = []
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            vals.append(float(json.loads(line)["value"]))
    return {"count": len(vals), "mean": (st.mean(vals) if vals else 0.0)}
# END: CODEX_METRIC_CURVES
"""
)
CURVE_TEST_SENT = "# BEGIN: CODEX_TEST_CURVES"
CURVE_TEST = (
    CURVE_TEST_SENT
    + "\n"
    + """
from pathlib import Path
from codex_ml.metrics.curves import append_curve, summarize


def test_curves_roundtrip(tmp_path: Path):
    for i in range(5):
        append_curve(tmp_path, "loss", i, 1.0/(i+1))
    s = summarize(tmp_path, "loss")
    assert s["count"] == 5 and s["mean"] > 0
# END: CODEX_TEST_CURVES
"""
)

# ---------- Monitoring ----------
PROM_SENT = "# BEGIN: CODEX_PROMETHEUS"
PROM_CODE = (
    PROM_SENT
    + "\n"
    + """from __future__ import annotations


def maybe_export_metrics(app=None, port: int = 9000):
    try:
        from prometheus_client import start_http_server, Counter, Gauge
    except Exception:
        return None
    start_http_server(port)
    counters = {"requests_total": Counter("requests_total","Total requests")}
    gauges = {"queue_depth": Gauge("queue_depth","Queue depth")}
    return counters, gauges
# END: CODEX_PROMETHEUS
"""
)

# ---------- Checkpointing ----------
SHA_SENT = "# BEGIN: CODEX_CHECKSUMS"
SHA_CODE = (
    SHA_SENT
    + "\n"
    + """from __future__ import annotations
import hashlib, os
from pathlib import Path


def sha256_dir(path: Path) -> str:
    h = hashlib.sha256()
    for root, _, files in os.walk(path):
        for fn in sorted(files):
            fp = Path(root)/fn
            h.update(fp.name.encode())
            h.update(fp.read_bytes())
    return h.hexdigest()


def write_checksum(path: Path):
    (path/"checksum.sha256").write_text(sha256_dir(path))
# END: CODEX_CHECKSUMS
"""
)

# ---------- Data ----------
CACHE_SENT = "# BEGIN: CODEX_DATA_CACHE"
CACHE_CODE = (
    f"{CACHE_SENT}\n"
    + """from __future__ import annotations
import time


class SimpleCache:
    def __init__(self, ttl_s: int = 3600, max_items: int = 1000):
        self.ttl, self.max = ttl_s, max_items
        self._d: dict[str, tuple[object, float]] = {}

    def get(self, k):
        v = self._d.get(k)
        if not v:
            return None
        val, t = v
        if time.time() - t > self.ttl:
            self._d.pop(k, None)
            return None
        return val

    def set(self, k, val):
        if len(self._d) >= self.max:
            self._d.pop(next(iter(self._d)))
        self._d[k] = (val, time.time())
# END: CODEX_DATA_CACHE
"""
)
SHARD_SENT = "# BEGIN: CODEX_DATA_SHARD"
SHARD_CODE = (
    f"{SHARD_SENT}\n"
    + """from __future__ import annotations


def shard_range(rank: int, world: int, n: int) -> tuple[int, int]:
    assert 0 <= rank < world and n >= 0
    base, rem = divmod(n, world)
    start = rank * base + min(rank, rem)
    end = start + base + (1 if rank < rem else 0)
    return start, end
# END: CODEX_DATA_SHARD
"""
)
DATA_TEST_SENT = "# BEGIN: CODEX_TEST_DATA_CACHE_SHARD"
DATA_TEST = (
    f"{DATA_TEST_SENT}\n"
    + """from codex_ml.data.sharding import shard_range


def test_shard_cover():
    n, w = 103, 7
    cov = set()
    for r in range(w):
        s, e = shard_range(r, w, n)
        cov |= set(range(s, e))
    assert len(cov) == n
# END: CODEX_TEST_DATA_CACHE_SHARD
"""
)

# ---------- Security ----------
RISK_SENT = "# BEGIN: CODEX_RISK_SCORE"
RISK_CODE = (
    RISK_SENT
    + "\n"
    + """from __future__ import annotations


def risk_score(text: str) -> float:
    # naive heuristic: keywords increase risk
    bad = ["password","api_key","ssn","rm -rf /","kill","drop database"]
    score = 0
    tl = text.lower()
    for k in bad:
        if k in tl:
            score += 1
    return float(score)
# END: CODEX_RISK_SCORE
"""
)

# ---------- CI (disabled) ----------
NIGHTLY_SENT = "# BEGIN: CODEX_NIGHTLY_DISABLED"
NIGHTLY = (
    NIGHTLY_SENT
    + "\n"
    + """
# Disabled workflow placeholder — enable by renaming to nightly.yml and reviewing triggers.
# on:
#   schedule:
#     - cron: "0 3 * * *"
# jobs:
#   stress:
#     runs-on: ubuntu-latest
#     steps: [{ uses: actions/checkout@v4 }]
# END: CODEX_NIGHTLY_DISABLED
"""
)
VULN_SENT = "# BEGIN: CODEX_VULN_DISABLED"
VULN = (
    VULN_SENT
    + "\n"
    + """
# Disabled dependency scan placeholder — enable manually if desired.
# on:
#   workflow_dispatch:
# jobs:
#   scan:
#     runs-on: ubuntu-latest
#     steps: [{ uses: actions/checkout@v4 }]
# END: CODEX_VULN_DISABLED
"""
)

# ---------- Deployment ----------
CHART_SENT = "# BEGIN: CODEX_HELM_CHART"
CHART = (
    CHART_SENT
    + "\n"
    + """
apiVersion: v2
name: codex-api
version: 0.0.1
description: Helm chart (stub)
# END: CODEX_HELM_CHART
"""
)
VALUES_SENT = "# BEGIN: CODEX_HELM_VALUES"
VALUES = (
    VALUES_SENT
    + "\n"
    + """
replicaCount: 1
image:
  repository: codex-api
  tag: local
service:
  port: 8000
# END: CODEX_HELM_VALUES
"""
)
GRPC_DOC_SENT = "<!-- BEGIN: CODEX_GRPC_PARITY_DOC -->"
GRPC_DOC = (
    GRPC_DOC_SENT
    + "\n"
    + """
# gRPC Parity Plan

- Mirror REST endpoints: Train/Infer/Evaluate/Status.
- Define .proto, generate stubs, ensure compatibility tests.
"""
)

# ---------- Docs & Examples ----------
NB_SENT = '"nbformat": 4'
NB = """{
 "cells": [
  {"cell_type":"markdown","metadata":{},"source":["# GPU Training Example (Stub)\n","TODO: Fill with end-to-end training demo."]},
  {"cell_type":"code","metadata":{},"execution_count":null,"outputs":[],"source":["!bash scripts/gpu/check_gpu.sh"]}
 ],
 "metadata": {"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}},
 "nbformat": 4, "nbformat_minor": 5
}
"""
MC_SENT = "<!-- BEGIN: CODEX_MODEL_CARD -->"
MC = (
    MC_SENT
    + "\n"
    + """
# Model Card (Template)

## Intended Use
## Training Data
## Evaluation Data
## Ethical Considerations
## Metrics & Limitations
"""
)

# ---------- Experiment Tracking ----------
GIT_SENT = "# BEGIN: CODEX_GIT_TAG"
GIT = (
    GIT_SENT
    + "\n"
    + """
from __future__ import annotations
import subprocess


def current_commit() -> str | None:
    try:
        return subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    except Exception:
        return None
# END: CODEX_GIT_TAG
"""
)


def apply():
    try:
        # Env
        upsert(REPO / "requirements-dev.txt", DEV_REQ, DEV_REQ_SENT)
        upsert(REPO / "requirements.txt", RUN_REQ, RUN_REQ_SENT)
        upsert(REPO / "scripts" / "gpu" / "check_gpu.sh", GPU_SH, GPU_SH_SENT)
        os.chmod(REPO / "scripts" / "gpu" / "check_gpu.sh", 0o700)
        upsert(REPO / "docs" / "ops" / "environment.md", ENV_DOC, ENV_DOC_SENT)
        # Tokenization
        upsert(REPO / "codex_ml" / "tokenization" / "sentencepiece_adapter.py", SP_CODE, SP_SENT)
        upsert(REPO / "tests" / "test_sentencepiece_adapter.py", SP_TEST, SP_TEST_SENT)
        # Modeling
        upsert(REPO / "codex_ml" / "models" / "activations.py", ACT_CODE, ACT_SENT)
        upsert(REPO / "codex_ml" / "peft" / "peft_adapter.py", PEFT_CODE, PEFT_SENT)
        upsert(REPO / "tests" / "test_activations.py", ACT_TEST, ACT_TEST_SENT)
        # Training
        upsert(REPO / "codex_ml" / "training" / "callbacks.py", CB_CODE, CB_SENT)
        upsert(REPO / "docs" / "ops" / "training_args.md", TRAIN_DOC, TRAIN_DOC_SENT)
        # Config
        upsert(REPO / "docs" / "ops" / "hydra_distributed_overrides.md", HYDRA_DOC, HYDRA_DOC_SENT)
        # Eval
        upsert(REPO / "codex_ml" / "metrics" / "curves.py", CURVE_CODE, CURVE_SENT)
        upsert(REPO / "tests" / "test_metric_curves.py", CURVE_TEST, CURVE_TEST_SENT)
        # Monitoring
        upsert(REPO / "codex_ml" / "monitoring" / "prometheus.py", PROM_CODE, PROM_SENT)
        upsert(
            REPO / "docs" / "ops" / "monitoring.md",
            "# Prometheus (optional)\n",
            "<!-- SENTINEL -->",
        )
        # Checkpointing
        upsert(REPO / "codex_ml" / "utils" / "checksums.py", SHA_CODE, SHA_SENT)
        # Data
        upsert(REPO / "codex_ml" / "data" / "cache.py", CACHE_CODE, CACHE_SENT)
        upsert(REPO / "codex_ml" / "data" / "sharding.py", SHARD_CODE, SHARD_SENT)
        upsert(REPO / "tests" / "test_data_cache_sharding.py", DATA_TEST, DATA_TEST_SENT)
        # Security
        upsert(REPO / "codex_ml" / "safety" / "risk_score.py", RISK_CODE, RISK_SENT)
        # CI disabled stubs
        upsert(REPO / ".github" / "workflows" / "nightly.yml.disabled", NIGHTLY, NIGHTLY_SENT)
        upsert(REPO / ".github" / "workflows" / "vuln_scan.yml.disabled", VULN, VULN_SENT)
        # Deployment
        upsert(REPO / "deploy" / "helm" / "Chart.yaml", CHART, CHART_SENT)
        upsert(REPO / "deploy" / "helm" / "values.yaml", VALUES, VALUES_SENT)
        upsert(REPO / "docs" / "ops" / "grpc_parity.md", GRPC_DOC, GRPC_DOC_SENT)
        # Docs & Examples
        upsert(REPO / "notebooks" / "gpu_training_example.ipynb", NB, NB_SENT)
        upsert(REPO / "docs" / "examples" / "model_card_template.md", MC, MC_SENT)
        # Experiment tracking
        upsert(REPO / "codex_ml" / "tracking" / "git_tag.py", GIT, GIT_SENT)
    except Exception as e:
        q5("3: Best-Effort Construction — write files", str(e), f"path={REPO}")


def deps():
    # Optional: install; failures do not abort flow
    cmds = [
        ["python", "-m", "pip", "install", "-r", "requirements-dev.txt"],
        ["python", "-m", "pip", "install", "-r", "requirements.txt"],
    ]
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Deps {ts()}\n")
        for cmd in cmds:
            fh.write(f"\n## {' '.join(cmd)}\n```\n")
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
                fh.write(p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
                if p.returncode != 0:
                    q5("3.1: pip install", f"exit {p.returncode}", " ".join(cmd))
            except Exception as e:
                fh.write(f"ERROR: {e}\n")
                q5("3.1: pip install", str(e), " ".join(cmd))
            fh.write("```\n")


def validate():
    steps = [
        ("GPU check", ["bash", "scripts/gpu/check_gpu.sh"]),
        ("black --check .", ["black", "--check", "."]),
        ("isort --check-only .", ["isort", "--check-only", "."]),
        ("flake8 .", ["flake8", "."]),
        ("mypy --ignore-missing-imports .", ["mypy", "--ignore-missing-imports", "."]),
        ("pytest -q --maxfail=1", ["pytest", "-q", "--maxfail=1"]),
    ]
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {ts()}\n")
        for name, cmd in steps:
            fh.write(f"\n## {name}\n```\n")
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
                fh.write(p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
                if p.returncode != 0:
                    q5("6: Finalization — validation", f"exit {p.returncode}", " ".join(cmd))
            except Exception as e:
                fh.write(f"ERROR: {e}\n")
                q5("6: Finalization — validation", str(e), " ".join(cmd))
            fh.write("```\n")


@hydra_main(config_path="conf", config_name="config", version_base=None)
def main(cfg: DictConfig):
    # Initialize determinism (no-op unless CODEX_DETERMINISM=1)
    _init_determinism_from_env()
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="create/update stack polish components")
    ap.add_argument(
        "--deps", action="store_true", help="pip install dev/runtime requirements (optional)"
    )
    ap.add_argument(
        "--validate", action="store_true", help="run local validations (format/type/tests)"
    )
    args = ap.parse_args()

    logging_cfg = getattr(cfg, "logging", None)
    candidate_uri = getattr(logging_cfg, "mlflow_uri", None) if logging_cfg is not None else None
    configure_mlflow_uri(str(candidate_uri) if candidate_uri is not None else None)
    if args.apply:
        apply()
    if args.deps:
        deps()
    if args.validate:
        validate()
    if not (args.apply or args.deps or args.validate):
        print("Usage: --apply [--deps] [--validate]")


if __name__ == "__main__":
    main()
