# Gap 13 Evidence: Performance Degradation Alerts

**Status**: ✅ Complete
**Priority**: P1 High
**Date**: 2026-01-23

## What Was Built

### New File: `src/codex/monitoring/performance_monitor.py`
- `PerformanceThresholds` — configurable via env vars (`CODEX_PERF_*`)
- `PerformanceSnapshot` — epoch-level metric capture (loss, throughput, latency_ms)
- `PerformanceMonitor` — rolling-window anomaly detector + alert dispatcher

### Updated: `src/codex/monitoring/__init__.py`
- Exports `PerformanceMonitor`, `PerformanceSnapshot`, `PerformanceThresholds`

### Updated: `src/codex_ml/train_loop.py`
- Lazy import of `PerformanceMonitor` before epoch loop
- `monitor.record()` call after each epoch (guarded with `try/except`)

### Tests: `tests/unit/test_performance_monitor.py`
- 19 tests, all passing
- Covers: healthy run, loss spike, throughput drop, latency spike, min_samples guard, alert failure safety, from_env factory

## Detection Thresholds (defaults)
| Metric | Default | Env Var |
|--------|---------|---------|
| Loss spike | 2× baseline | `CODEX_PERF_LOSS_SPIKE_FACTOR` |
| Throughput drop | 30% | `CODEX_PERF_THROUGHPUT_DROP_PCT` |
| Latency spike | 3× baseline | `CODEX_PERF_LATENCY_SPIKE_FACTOR` |
| Window size | 10 samples | `CODEX_PERF_WINDOW_SIZE` |
| Min samples | 3 | `CODEX_PERF_MIN_SAMPLES` |
