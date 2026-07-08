"""
Bench Module

This module provides functionality for bench.

Usage:
    from perf.bench import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import argparse  # noqa: E402
import importlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import statistics as stats  # noqa: E402
import time  # noqa: E402
from collections.abc import Callable  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from typing import Any  # noqa: E402

from codex.logging.structured_logger import logger


def _maybe_cuda_sync() -> None:
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
    except (ImportError, AttributeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)


def _target_numpy_matmul(n: int = 2048) -> None:
    import numpy as np

    a = np.random.rand(n, n).astype("float32")
    b = np.random.rand(n, n).astype("float32")
    _ = a @ b


def _target_torch_matmul(n: int = 4096, device: str = "auto") -> None:
    import torch

    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    a = torch.randn(n, n, device=device, dtype=torch.float32)
    b = torch.randn(n, n, device=device, dtype=torch.float32)
    _ = a @ b
    if device == "cuda":
        _maybe_cuda_sync()


def _resolve_callable(path: str) -> Callable[[], Any]:
    """Resolve 'pkg.module:function' -> callable with no required args."""
    if ":" not in path:
        raise ValueError("Expected format 'pkg.module:function'")
    mod, fn = path.split(":", 1)
    return getattr(importlib.import_module(mod), fn)


@dataclass
class BenchResult:
    samples_ms: list[float]

    @property
    def median_ms(self) -> float:
        return float(stats.median(self.samples_ms)) if self.samples_ms else 0.0

    @property
    def p95_ms(self) -> float:
        if not self.samples_ms:
            return 0.0
        k = max(0, int(round(0.95 * (len(self.samples_ms) - 1))))
        return float(sorted(self.samples_ms)[k])

    def as_dict(self) -> dict[str, Any]:
        return {
            "median_ms": self.median_ms,
            "p95_ms": self.p95_ms,
            "n": len(self.samples_ms),
            "samples_ms": self.samples_ms,
        }


def run_bench(
    fn: Callable[[], Any], warmup: int = 3, iters: int = 10, cuda_sync: bool = True
) -> BenchResult:
    for _ in range(max(0, warmup)):
        fn()
        if cuda_sync:
            _maybe_cuda_sync()
    samples: list[float] = []
    for _ in range(max(1, iters)):
        if cuda_sync:
            _maybe_cuda_sync()
        t0 = time.perf_counter()
        fn()
        if cuda_sync:
            _maybe_cuda_sync()
        t1 = time.perf_counter()
        samples.append((t1 - t0) * 1000.0)
    return BenchResult(samples)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="codex-perf", description="Tiny offline micro-bench harness.")
    tg = p.add_mutually_exclusive_group(required=False)
    tg.add_argument("--torch-matmul", action="store_true", help="Benchmark a torch matmul.")
    tg.add_argument("--numpy-matmul", action="store_true", help="Benchmark a NumPy matmul.")
    p.add_argument("--call", type=str, help="Benchmark 'pkg.module:function' (no-arg target).")
    p.add_argument("--size", type=int, default=0, help="Problem size hint for built-ins.")
    p.add_argument("--warmup", type=int, default=3)
    p.add_argument("--iters", type=int, default=10)
    p.add_argument("--no-cuda-sync", action="store_true", help="Disable CUDA synchronize guards.")
    p.add_argument("--json", action="store_true", help="Emit JSON with raw samples.")
    p.add_argument("--mlflow", action="store_true", help="Log metrics to MLflow if available.")
    args = p.parse_args(argv)

    if args.call:
        fn = _resolve_callable(args.call)
    elif args.torch_matmul:
        size = args.size or 4096

        def fn() -> None:
            _target_torch_matmul(size)

    elif args.numpy_matmul:
        size = args.size or 2048

        def fn() -> None:
            _target_numpy_matmul(size)

    else:
        p.error("Pick one target: --torch-matmul | --numpy-matmul | --call pkg:fn")
        return 2

    res = run_bench(fn, warmup=args.warmup, iters=args.iters, cuda_sync=not args.no_cuda_sync)

    if args.json:
        logger.info(json.dumps(res.as_dict(), indent=2))
    else:
        logger.info(
            f"n={len(res.samples_ms)}  median={res.median_ms:.2f} ms  p95={res.p95_ms:.2f} ms"
        )

    if args.mlflow:
        try:
            import mlflow

            from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking

            tracking_uri = bootstrap_offline_tracking(
                requested_uri=os.getenv("MLFLOW_TRACKING_URI")
            )
            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment("codex-perf")
            with mlflow.start_run(run_name="bench"):
                mlflow.log_metrics({"median_ms": res.median_ms, "p95_ms": res.p95_ms})
                mlflow.log_params(
                    {
                        "iters": args.iters,
                        "warmup": args.warmup,
                        "target": args.call
                        or ("torch-matmul" if args.torch_matmul else "numpy-matmul"),
                        "size": args.size,
                        "cuda_sync": not args.no_cuda_sync,
                    }
                )
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.info("[mlflow] skipped: <ERROR_TYPE>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# WHY: Micro-bench smoke to gauge perf across environments.
# RISK: None; optional deps guarded, offline-safe.
