"""
bench_inference.py — Inference latency benchmark (ms/sample).

Simulates a two-layer fully-connected network forward pass using only the
Python standard library (no ML framework required).

Architecture:
  input  (64)  →  hidden  (128)  →  output  (10)
  with ReLU activation after the first layer.

Measures per-sample latency for batch sizes 1, 8, and 32.
"""

from __future__ import annotations

import math
import random
import statistics
import time
from typing import Any

# ---------------------------------------------------------------------------
# Network dimensions
# ---------------------------------------------------------------------------

INPUT_DIM = 64
HIDDEN_DIM = 128
OUTPUT_DIM = 10
SEED = 42
N_WARMUP = 20       # warmup passes (not measured)
N_MEASURE = 200     # measured passes


# ---------------------------------------------------------------------------
# Helpers — pure-Python matrix ops
# ---------------------------------------------------------------------------

def _matvec(W: list[list[float]], x: list[float]) -> list[float]:
    """y = W @ x  (W is out_dim × in_dim)."""
    return [sum(W[i][j] * x[j] for j in range(len(x))) for i in range(len(W))]


def _add(a: list[float], b: list[float]) -> list[float]:
    return [ai + bi for ai, bi in zip(a, b)]


def _relu(x: list[float]) -> list[float]:
    return [max(0.0, v) for v in x]


# ---------------------------------------------------------------------------
# Model initialisation
# ---------------------------------------------------------------------------

def _init_weights(out_dim: int, in_dim: int, seed_offset: int = 0) -> list[list[float]]:
    rng = random.Random(SEED + seed_offset)
    scale = math.sqrt(2.0 / in_dim)   # He init
    return [[rng.gauss(0, scale) for _ in range(in_dim)] for _ in range(out_dim)]


def _init_bias(dim: int, seed_offset: int = 100) -> list[float]:
    rng = random.Random(SEED + seed_offset)
    return [rng.gauss(0, 0.01) for _ in range(dim)]


# ---------------------------------------------------------------------------
# Forward pass
# ---------------------------------------------------------------------------

def _forward(
    x: list[float],
    W1: list[list[float]],
    b1: list[float],
    W2: list[list[float]],
    b2: list[float],
) -> list[float]:
    h = _relu(_add(_matvec(W1, x), b1))
    return _add(_matvec(W2, h), b2)


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

def run_benchmark(batch_sizes: tuple[int, ...] = (1, 8, 32)) -> dict[str, Any]:
    """
    Measure per-sample inference latency for several batch sizes.

    Returns a result dict suitable for the consolidated report.
    """
    W1 = _init_weights(HIDDEN_DIM, INPUT_DIM, seed_offset=0)
    b1 = _init_bias(HIDDEN_DIM, seed_offset=1)
    W2 = _init_weights(OUTPUT_DIM, HIDDEN_DIM, seed_offset=2)
    b2 = _init_bias(OUTPUT_DIM, seed_offset=3)

    rng = random.Random(SEED)
    batch_results: dict[str, Any] = {}

    for bs in batch_sizes:
        # Build synthetic batch
        batch = [[rng.gauss(0, 1) for _ in range(INPUT_DIM)] for _ in range(bs)]

        # Warmup
        for sample in batch * (N_WARMUP // max(bs, 1) + 1):
            _forward(sample, W1, b1, W2, b2)

        # Measure
        latencies_ms: list[float] = []
        for _ in range(N_MEASURE):
            t0 = time.perf_counter()
            for sample in batch:
                _forward(sample, W1, b1, W2, b2)
            elapsed_ms = (time.perf_counter() - t0) * 1_000.0
            per_sample_ms = elapsed_ms / bs
            latencies_ms.append(per_sample_ms)

        sorted_lat = sorted(latencies_ms)
        p50 = sorted_lat[int(0.50 * len(sorted_lat))]
        p95 = sorted_lat[int(0.95 * len(sorted_lat))]
        p99 = sorted_lat[int(0.99 * len(sorted_lat))]

        batch_results[f"batch_{bs}"] = {
            "n_samples_per_call": bs,
            "mean_ms_per_sample": round(statistics.mean(latencies_ms), 4),
            "stdev_ms": round(statistics.stdev(latencies_ms), 4),
            "p50_ms": round(p50, 4),
            "p95_ms": round(p95, 4),
            "p99_ms": round(p99, 4),
        }

    result: dict[str, Any] = {
        "benchmark": "inference_latency",
        "description": "Two-layer MLP forward pass — ms/sample (lower is better)",
        "config": {
            "input_dim": INPUT_DIM,
            "hidden_dim": HIDDEN_DIM,
            "output_dim": OUTPUT_DIM,
            "n_warmup_passes": N_WARMUP,
            "n_measured_passes": N_MEASURE,
        },
        "results": batch_results,
        "status": "pass",
    }
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    print("Running inference latency benchmark …")
    result = run_benchmark()
    print(json.dumps(result, indent=2))
    for key, val in result["results"].items():
        print(
            f"  {key:12s}  mean={val['mean_ms_per_sample']:.4f} ms/sample"
            f"  p99={val['p99_ms']:.4f} ms"
        )
