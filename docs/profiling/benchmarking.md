# Performance Benchmarking

The `codex_ml.perf.profiler.PerformanceProfiler` offers a minimal, dependency-free way to capture wall-clock
statistics for critical sections in training, inference, and data loading workflows.

## Quick start

```python
from codex_ml.perf.profiler import PerformanceProfiler

profiler = PerformanceProfiler()

for epoch in range(5):
    for batch in train_loader:
        with profiler.profile("data_load"):
            batch = batch.to(device)

        with profiler.profile("forward_pass"):
            loss = model(batch).loss

        with profiler.profile("backward_pass"):
            loss.backward()
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)

profiler.export_jsonl("artifacts/profiling.jsonl")
print(profiler.summary())
```text

The `summary()` method returns min/mean/max/median values per section, making it easy to spot regressions between
runs.

## CLI integration

Create a dedicated `nox` session for repeatable benchmarks:

```bash
nox --noxfile configs/development/noxfile.py -s perf -- \
  --model sshleifer/tiny-gpt2 \
  --batch-size 32 \
  --num-iterations 100 \
  --output artifacts/inference_bench.jsonl
```text

Each invocation can export NDJSON records which integrate with the session logging infrastructure and can be plotted
with tools like pandas or Vega.

## Operational tips

* Keep benchmarking artefacts under `artifacts/` for reproducibility.
* Combine the profiler with Prometheus metrics to cross-check latency histograms.
* Run the profiling nox session as part of release candidates to catch regressions before promotion.
