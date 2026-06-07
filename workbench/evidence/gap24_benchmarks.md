# Gap 24 — Performance Benchmarking Suite

**Status**: ✅ Implemented
**Date**: 2026-06-06
**Branch**: `copilot/explore-codebase-and-create-plan`

---

## Overview

Gap 24 required a lightweight, CPU-only performance benchmarking suite covering
three dimensions of system health: training throughput, inference latency, and
peak memory usage.  All benchmarks run with zero external dependencies (stdlib
only) and complete well under the 5-minute target.

---

## Deliverables

| File | Purpose |
|------|---------|
| `benchmarks/bench_training.py` | SGD training-loop throughput — steps/sec |
| `benchmarks/bench_inference.py` | Two-layer MLP forward-pass latency — ms/sample |
| `benchmarks/bench_memory.py` | Peak heap allocation via `tracemalloc` — MiB |
| `benchmarks/run_all.py` | Master runner; writes `benchmarks/results/benchmark_report.json` |
| `benchmarks/results/benchmark_report.json` | Consolidated machine-readable report |

---

## Benchmark Execution

Command executed:

```bash
cd /tmp/workspace/Aries-Serpent/_codex_ && python benchmarks/run_all.py
```

Console output:

```
────────────────────────────────────────────────────────────
▶  Training Throughput …
   ✅  Done in 0.38s

────────────────────────────────────────────────────────────
▶  Inference Latency …
   ✅  Done in 5.31s

────────────────────────────────────────────────────────────
▶  Memory Usage …
   ✅  Done in 1.11s

════════════════════════════════════════════════════════════
📄  Report written to: benchmarks/results/benchmark_report.json
⏱   Total elapsed: 6.80s
```

Total wall-clock time: **6.80 seconds** (target: < 5 minutes ✅)

---

## Results Summary

### Training Throughput (`bench_training.py`)

Workload: SGD on 1 000 × 64 synthetic data, 200 steps, batch 32 (3 repeats).

| Metric | Value |
|--------|-------|
| Mean throughput | **1 780.97 steps/sec** |
| Std deviation | 12.74 steps/sec |
| Run 1 | 1 767.56 steps/sec |
| Run 2 | 1 792.92 steps/sec |
| Run 3 | 1 782.42 steps/sec |

### Inference Latency (`bench_inference.py`)

Workload: 64→128→10 MLP forward pass, 20 warmup + 200 measured passes.

| Batch | Mean ms/sample | p50 | p95 | p99 |
|-------|---------------|-----|-----|-----|
| 1 | **0.6308 ms** | 0.6285 ms | 0.6538 ms | 0.7985 ms |
| 8 | **0.6372 ms** | 0.6297 ms | 0.6762 ms | 0.8208 ms |
| 32 | **0.6425 ms** | 0.6334 ms | 0.7105 ms | 0.8395 ms |

### Memory Usage (`bench_memory.py`)

Workload: Three representative allocations measured with `tracemalloc`.

| Workload | Peak MiB |
|----------|----------|
| Dataset allocation (2 000 × 128) | **7.932 MiB** |
| Model weight initialisation | 1.094 MiB |
| Batched forward pass (batch 64) | 1.389 MiB |
| **Overall peak** | **7.932 MiB** |

---

## Environment

| Property | Value |
|----------|-------|
| Python | 3.12.3 (GCC 13.3.0) |
| Platform | Linux-6.17.0-azure x86_64 |
| CPU cores | 4 |
| External dependencies | None (stdlib only) |

---

## Done Criteria Verification

| Criterion | Status |
|-----------|--------|
| `benchmarks/` directory with ≥ 3 benchmark scripts | ✅ 3 scripts created |
| `run_all.py` produces `benchmark_report.json` | ✅ Confirmed (see above) |
| Benchmarks actually executed with output captured | ✅ 6.80 s total |
| Evidence file at `workbench/evidence/gap24_benchmarks.md` | ✅ This file |
| Gap 24 status → ✅ Implemented in `gap_backlog_prioritized.md` | ✅ Updated |
