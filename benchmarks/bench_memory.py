"""
bench_memory.py — Peak memory usage benchmark.

Uses Python's built-in ``tracemalloc`` module to measure the peak heap
allocation of three representative workloads:

1. ``dataset_allocation``  — allocate a synthetic feature matrix (N × D).
2. ``model_weights``       — allocate a two-layer MLP weight store.
3. ``forward_pass_batch``  — run a full batched forward pass end-to-end,
                             capturing the peak live allocation.

All measurements are in mebibytes (MiB).  No external packages required.
"""

from __future__ import annotations

import math
import random
import tracemalloc
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SEED = 42
N_SAMPLES = 2_000
N_FEATURES = 128
HIDDEN_DIM = 256
OUTPUT_DIM = 10
BATCH_SIZE = 64


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bytes_to_mib(n: int) -> float:
    return n / (1024 ** 2)


def _matvec(W: list[list[float]], x: list[float]) -> list[float]:
    return [sum(W[i][j] * x[j] for j in range(len(x))) for i in range(len(W))]


def _relu(v: list[float]) -> list[float]:
    return [max(0.0, x) for x in v]


# ---------------------------------------------------------------------------
# Workloads
# ---------------------------------------------------------------------------

def _workload_dataset() -> None:
    """Allocate a dense float matrix of shape (N_SAMPLES × N_FEATURES)."""
    rng = random.Random(SEED)
    _ = [[rng.gauss(0, 1) for _ in range(N_FEATURES)] for _ in range(N_SAMPLES)]


def _workload_weights() -> None:
    """Allocate and initialise two-layer MLP weights."""
    rng = random.Random(SEED + 1)
    scale1 = math.sqrt(2.0 / N_FEATURES)
    scale2 = math.sqrt(2.0 / HIDDEN_DIM)
    W1 = [[rng.gauss(0, scale1) for _ in range(N_FEATURES)] for _ in range(HIDDEN_DIM)]
    b1 = [0.0] * HIDDEN_DIM
    W2 = [[rng.gauss(0, scale2) for _ in range(HIDDEN_DIM)] for _ in range(OUTPUT_DIM)]
    b2 = [0.0] * OUTPUT_DIM
    # Keep references alive so tracemalloc counts them
    _ = (W1, b1, W2, b2)


def _workload_forward_batch() -> None:
    """Allocate weights + dataset + run a batched forward pass."""
    rng = random.Random(SEED + 2)
    scale1 = math.sqrt(2.0 / N_FEATURES)
    scale2 = math.sqrt(2.0 / HIDDEN_DIM)
    W1 = [[rng.gauss(0, scale1) for _ in range(N_FEATURES)] for _ in range(HIDDEN_DIM)]
    b1 = [0.0] * HIDDEN_DIM
    W2 = [[rng.gauss(0, scale2) for _ in range(HIDDEN_DIM)] for _ in range(OUTPUT_DIM)]
    b2 = [0.0] * OUTPUT_DIM

    batch = [[rng.gauss(0, 1) for _ in range(N_FEATURES)] for _ in range(BATCH_SIZE)]
    outputs = []
    for x in batch:
        h = _relu([sum(W1[i][j] * x[j] for j in range(N_FEATURES)) + b1[i]
                   for i in range(HIDDEN_DIM)])
        out = [sum(W2[k][i] * h[i] for i in range(HIDDEN_DIM)) + b2[k]
               for k in range(OUTPUT_DIM)]
        outputs.append(out)
    _ = outputs  # keep alive


# ---------------------------------------------------------------------------
# Measurement helper
# ---------------------------------------------------------------------------

def _measure_peak_mib(workload_fn) -> dict[str, float]:  # type: ignore[type-arg]
    """Run *workload_fn* under tracemalloc and return peak/current MiB."""
    tracemalloc.stop()           # ensure clean slate
    tracemalloc.start()
    workload_fn()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "current_mib": round(_bytes_to_mib(current), 4),
        "peak_mib": round(_bytes_to_mib(peak), 4),
    }


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

def run_benchmark() -> dict[str, Any]:
    """
    Run all three memory workloads and return a result dict.
    """
    workloads = [
        ("dataset_allocation", _workload_dataset),
        ("model_weights", _workload_weights),
        ("forward_pass_batch", _workload_forward_batch),
    ]

    measurements: dict[str, dict[str, float]] = {}
    for name, fn in workloads:
        measurements[name] = _measure_peak_mib(fn)

    overall_peak = max(v["peak_mib"] for v in measurements.values())

    result: dict[str, Any] = {
        "benchmark": "memory_usage",
        "description": "Peak heap allocation per workload in MiB (lower is better)",
        "config": {
            "n_samples": N_SAMPLES,
            "n_features": N_FEATURES,
            "hidden_dim": HIDDEN_DIM,
            "output_dim": OUTPUT_DIM,
            "batch_size": BATCH_SIZE,
        },
        "results": measurements,
        "overall_peak_mib": round(overall_peak, 4),
        "status": "pass",
    }
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    print("Running memory usage benchmark …")
    result = run_benchmark()
    print(json.dumps(result, indent=2))
    for name, vals in result["results"].items():
        print(f"  {name:30s}  peak={vals['peak_mib']:.3f} MiB")
    print(f"\n✅  Overall peak: {result['overall_peak_mib']:.3f} MiB")
