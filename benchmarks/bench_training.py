"""
bench_training.py — Training throughput benchmark (steps/sec).

Simulates a lightweight linear-regression training loop using only the
Python standard library so the benchmark runs on CPU without any ML
framework installed.

Synthetic data: 1 000 samples × 64 features.
Training loop: stochastic gradient descent for 200 steps, batch size 32.
"""

from __future__ import annotations

import math
import random
import statistics
import time
from typing import Any

# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

SEED = 42
N_SAMPLES = 1_000
N_FEATURES = 64
N_STEPS = 200
BATCH_SIZE = 32
LEARNING_RATE = 0.01


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _generate_data(
    n: int, d: int, seed: int = SEED
) -> tuple[list[list[float]], list[float]]:
    """Return (X, y) where y = X @ w_true + noise."""
    rng = random.Random(seed)
    w_true = [rng.gauss(0, 1) for _ in range(d)]
    X: list[list[float]] = []
    y: list[float] = []
    for _ in range(n):
        row = [rng.gauss(0, 1) for _ in range(d)]
        label = _dot(row, w_true) + rng.gauss(0, 0.1)
        X.append(row)
        y.append(label)
    return X, y


def _sgd_step(
    X_batch: list[list[float]],
    y_batch: list[float],
    w: list[float],
    lr: float,
) -> tuple[list[float], float]:
    """One mini-batch SGD step; returns updated weights and MSE loss."""
    d = len(w)
    n = len(X_batch)
    grad = [0.0] * d
    loss = 0.0
    for xi, yi in zip(X_batch, y_batch):
        pred = _dot(xi, w)
        err = pred - yi
        loss += err * err
        for j in range(d):
            grad[j] += 2.0 * err * xi[j] / n
    loss /= n
    w_new = [w[j] - lr * grad[j] for j in range(d)]
    return w_new, loss


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

def run_benchmark(repeats: int = 3) -> dict[str, Any]:
    """
    Run the training throughput benchmark *repeats* times.

    Returns a result dict suitable for inclusion in the consolidated report.
    """
    X, y = _generate_data(N_SAMPLES, N_FEATURES)
    rng = random.Random(SEED)

    throughputs: list[float] = []

    for _ in range(repeats):
        w = [rng.gauss(0, 0.01) for _ in range(N_FEATURES)]
        indices = list(range(N_SAMPLES))

        t0 = time.perf_counter()
        for step in range(N_STEPS):
            rng.shuffle(indices)
            batch_idx = indices[:BATCH_SIZE]
            X_b = [X[i] for i in batch_idx]
            y_b = [y[i] for i in batch_idx]
            w, _ = _sgd_step(X_b, y_b, w, LEARNING_RATE)
        elapsed = time.perf_counter() - t0

        steps_per_sec = N_STEPS / elapsed
        throughputs.append(steps_per_sec)

    mean_tps = statistics.mean(throughputs)
    stdev_tps = statistics.stdev(throughputs) if len(throughputs) > 1 else 0.0

    result: dict[str, Any] = {
        "benchmark": "training_throughput",
        "description": "SGD training loop — steps/sec (higher is better)",
        "config": {
            "n_samples": N_SAMPLES,
            "n_features": N_FEATURES,
            "n_steps": N_STEPS,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "repeats": repeats,
        },
        "results": {
            "throughput_steps_per_sec": [round(t, 2) for t in throughputs],
            "mean_steps_per_sec": round(mean_tps, 2),
            "stdev_steps_per_sec": round(stdev_tps, 2),
        },
        "status": "pass",
    }
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    print("Running training throughput benchmark …")
    result = run_benchmark()
    print(json.dumps(result, indent=2))
    tps = result["results"]["mean_steps_per_sec"]
    print(f"\n✅  Mean throughput: {tps:.1f} steps/sec")
