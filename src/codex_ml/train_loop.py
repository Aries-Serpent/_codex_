# BEGIN: CODEX_TRAIN_LOOP
"""Toy training loop with evaluation hooks and metrics persistence.

Usage::

    python -m codex_ml.train_loop --epochs 3 [--seed 1234]

Metrics are written under ``artifacts/metrics`` where two files are created by
default:

``metrics.json``
    A list containing all metric payloads for easy inspection.

``metrics.ndjson``
    A newline-delimited variant suitable for streaming analytics.

Every invocation now also exports ``environment.json`` / ``environment.ndjson``
and a ``pip-freeze.txt`` manifest to capture reproducibility metadata, plus an
optional ``dataset_checksums.json`` when dataset sources are provided. This is a
best-effort integration: if your project has an existing trainer, adapt the
callback pattern below and invoke :func:`record_metrics`.

CLI flags::

    --seed INTEGER
        Seed for reproducible runs. ``0`` (the default) derives a random seed
        from the current process and time.
"""

from __future__ import annotations

import argparse
import json
import os
import random
from datetime import datetime
from pathlib import Path
from time import time_ns
from typing import Any, Dict, List, Sequence

from codex_ml.eval.metrics import perplexity, token_accuracy
from codex_ml.monitoring.codex_logging import write_ndjson
from codex_ml.utils.env import environment_summary
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.repro import record_dataset_checksums, set_reproducible

try:  # optional dependency
    import mlflow

    _HAS_MLFLOW = True
except Exception:  # pragma: no cover - optional
    mlflow = None  # type: ignore
    _HAS_MLFLOW = False

from codex_ml.telemetry.server import start_metrics_server

ART_DIR = Path("artifacts/metrics")


def _resolve_seed(seed: int | None) -> int:
    """Return an integer seed suitable for :func:`set_reproducible`.

    ``0`` or ``None`` trigger a best-effort random seed derived from the
    current process id and a nanosecond timestamp. ``set_reproducible`` expects
    an integer, so this helper also coerces other inputs via ``int()``.
    """

    if seed is None:
        seed = 0
    try:
        seed_value = int(seed)
    except (TypeError, ValueError):
        seed_value = 0
    if seed_value == 0:
        seed_value = abs(time_ns() ^ os.getpid()) % (2**32)
        if seed_value == 0:
            seed_value = 1
    return seed_value


def _ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def record_metrics(
    phase: str,
    epoch: int,
    metrics: Dict[str, Any],
    cfg_hash: str,
    notes: str = "toy-eval",
    art_dir: Path | None = None,
) -> None:
    if art_dir is None:
        art_dir = ART_DIR
    art_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": _ts(),
        "phase": phase,
        "epoch": epoch,
        "metrics": metrics,
        "cfg_hash": cfg_hash,
        "notes": notes,
        "git_commit": environment_summary().get("git_commit"),
    }
    # write list for back-compat
    out_list = art_dir / "metrics.json"
    prev: List[Dict[str, Any]] = []
    if out_list.exists():
        try:
            prev = json.loads(out_list.read_text(encoding="utf-8"))
            if not isinstance(prev, list):
                prev = []
        except Exception:
            prev = []
    prev.append(payload)
    out_list.write_text(json.dumps(prev, indent=2), encoding="utf-8")
    # append NDJSON for streaming analytics
    out_ndjson = art_dir / "metrics.ndjson"
    write_ndjson(out_ndjson, payload)


def demo_epoch(epoch: int, grad_accum: int = 1) -> Dict[str, float]:
    """Simulate a training epoch with gradient accumulation.

    This toy loop splits the synthetic dataset into ``grad_accum`` micro-
    batches and pretends to step an optimiser once per accumulation cycle.
    Metrics are computed over the full epoch. The number of optimiser steps is
    returned for introspection in tests.
    """

    random.seed(42 + epoch)
    targets = [random.randint(0, 4) for _ in range(100)]
    preds: list[int] = []
    micro = max(1, len(targets) // max(1, grad_accum))
    steps = 0
    threshold = 0.4 + 0.15 * epoch
    for i in range(0, len(targets), micro):
        end = i + micro
        batch_t = targets[i:end]
        batch_p: list[int] = []
        for value in batch_t:
            if random.random() < threshold:
                batch_p.append(value)
            else:
                batch_p.append(random.randint(0, 4))
        preds.extend(batch_p)
        steps += 1
    acc = token_accuracy(preds, targets)
    logits = []
    for t in targets:
        base = [0.0] * 5
        base[t] = 1.0 + 0.3 * epoch
        logits.append(base)
    ppl = perplexity(logits, targets, from_logits=True)
    return {"acc": acc, "ppl": ppl, "grad_accum": grad_accum, "steps": steps}


def run_training(
    *,
    epochs: int,
    grad_accum: int,
    mlflow_enable: bool = False,
    mlflow_uri: str = "file:./mlruns",
    mlflow_experiment: str = "codex",
    telemetry_enable: bool = False,
    telemetry_port: int = 8001,
    seed: int | None = 0,
    art_dir: Path | None = None,
    dataset_sources: Sequence[Path | str] | None = None,
) -> None:
    """Run demo training loop with optional MLflow and telemetry.

    Args:
        seed: Integer seed forwarded to :func:`set_reproducible`.
            ``0`` triggers a time and process dependent seed.
        art_dir: Directory used to persist metrics artifacts. Defaults to the
            module level :data:`ART_DIR`.
        dataset_sources: Optional collection of dataset files whose checksums will be
            recorded alongside metrics to capture dataset provenance.
    """
    resolved_seed = _resolve_seed(seed)
    set_reproducible(resolved_seed)
    if art_dir is None:
        art_dir = ART_DIR
    export_environment(art_dir, seed=resolved_seed, command="codex_ml.train_loop")
    if dataset_sources:
        paths = [Path(p) for p in dataset_sources]
        record_dataset_checksums(paths, art_dir / "dataset_checksums.json")
    cfg_hash = "c898a1161dce426c3f46d5b5f09fd0544abc292a4be5076ecf0d75af2bce2a9c"  # noqa: E501
    best = {"epoch": -1, "acc": -1.0}
    if telemetry_enable:
        start_metrics_server(port=telemetry_port)
    if mlflow_enable and _HAS_MLFLOW:
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment(mlflow_experiment)
        mlflow.start_run()
        mlflow.log_params({"epochs": epochs, "grad_accum": grad_accum})
    for ep in range(epochs):
        m = demo_epoch(ep, grad_accum=grad_accum)
        record_metrics("epoch_end", ep, m, cfg_hash, art_dir=art_dir)
        if mlflow_enable and _HAS_MLFLOW:
            mlflow.log_metrics(m, step=ep)
        if m["acc"] > best["acc"]:
            best = {"epoch": ep, "acc": m["acc"]}
    record_metrics(
        "best_checkpoint",
        best["epoch"],
        {"acc": best["acc"], "ppl": None},
        cfg_hash,
        notes="best-of-toy",
        art_dir=art_dir,
    )
    if mlflow_enable and _HAS_MLFLOW:
        mlflow.end_run()


def main() -> None:  # pragma: no cover - CLI wrapper
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument(
        "--grad-accum",
        type=int,
        default=1,
        help="accumulate gradients over N steps",
    )
    ap.add_argument(
        "--mlflow.enable",
        dest="mlflow_enable",
        action="store_true",
        default=False,
    )
    ap.add_argument("--mlflow.uri", dest="mlflow_uri", default="file:./mlruns")
    ap.add_argument(
        "--mlflow.experiment",
        dest="mlflow_experiment",
        default="codex",
    )
    ap.add_argument(
        "--telemetry.enable",
        dest="telemetry_enable",
        action="store_true",
        default=False,
    )
    ap.add_argument(
        "--telemetry.port",
        dest="telemetry_port",
        type=int,
        default=8001,
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=0,
        help="integer seed for reproducible runs",
    )
    ap.add_argument(
        "--art-dir",
        type=Path,
        default=ART_DIR,
        help="metrics output directory",
    )
    args = ap.parse_args()
    run_training(
        epochs=args.epochs,
        grad_accum=args.grad_accum,
        mlflow_enable=args.mlflow_enable,
        mlflow_uri=args.mlflow_uri,
        mlflow_experiment=args.mlflow_experiment,
        telemetry_enable=args.telemetry_enable,
        telemetry_port=args.telemetry_port,
        seed=args.seed,
        art_dir=args.art_dir,
    )


if __name__ == "__main__":
    main()
# END: CODEX_TRAIN_LOOP
