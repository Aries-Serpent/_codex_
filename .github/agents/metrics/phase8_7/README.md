# Phase 8.7 Metrics Directory

This directory stores JSON/JSONL metrics artifacts for Phase 8.7 Universal Intelligence.

## PRE-COMMIT 7: EXP-10 Benchmark Results

### exp10_benchmark.jsonl

EXP-10 validation benchmark with 10 diverse tasks testing universal intelligence capabilities.

**Format**: Newline-delimited JSON (JSONL)

**Schema**:
```json
// Summary line
{
  "type": "summary",
  "avg_k1": 0.25,
  "passes_target": true,
  "timestamp": "2026-01-03T10:52:59.283217"
}

// Task result lines
{
  "type": "task_result",
  "task_id": "exp10_task_1",
  "environment": "gridworld",
  "k1": 0.26,
  "decision_score": 0.74,
  "quantum_advantage": 3.85,
  "timestamp": "2026-01-03T10:52:59.283236"
}
```

**Task Distribution**:
- 4 gridworld tasks (varying grid sizes: 2x2, 3x3, 5x5, 10x10)
- 3 bandit tasks (2, 4, 8 arms)
- 3 classification tasks (3, 5, 10 classes)

**Target**: k₁ ≤ 0.28 (stretch goal: k₁ ≤ 0.255)

## Original Metric Definitions

| Metric | Description | Target |
|--------|-------------|--------|
| `k1` | 1 - avg(DecisionScore) | ≤ 0.28 |
| `zero_shot` | Held-out accuracy without training | >60% |
| `few_shot_k10` | Accuracy after 10 examples | >80% |
| `neg_transfer` | Negative transfer degradation | <5% |
| `forgetting` | Source task accuracy drop | <20% |
| `emergence_count` | Novel behaviors detected | N/A |
| `confidence_ece` | Expected calibration error | <0.10 |

## Files

- `exp10_benchmark.jsonl` - EXP-10 benchmark results (PRE-COMMIT 7)
- `k1_metrics.jsonl` - Decision quality metrics (future)
- `transfer_metrics.jsonl` - Transfer learning metrics (future)
- `emergence_events.jsonl` - Emergence detection logs (future)
- `confidence_calibration.jsonl` - Calibration metrics (future)

## Usage

### Running EXP-10 Benchmark

```python
from universal_intelligence import EXP10BenchmarkHarness, UniversalController

harness = EXP10BenchmarkHarness(seed=12345)
controller = UniversalController(seed=12345)

result = harness.run_benchmark(
    controller,
    metrics_output_dir='.github/agents/metrics/phase8_7'
)

print(f"Average k₁: {result['avg_k1']:.4f}")
print(f"Passes target: {result['passes_target']}")
```

### Analyzing Results

```python
import json

with open('.github/agents/metrics/phase8_7/exp10_benchmark.jsonl') as f:
    lines = f.readlines()

summary = json.loads(lines[0])
tasks = [json.loads(line) for line in lines[1:]]

print(f"Summary: {summary}")
print(f"Best task k₁: {min(t['k1'] for t in tasks):.4f}")
print(f"Worst task k₁: {max(t['k1'] for t in tasks):.4f}")
```

## CI Integration

- **Tier-0**: Metrics generated but not analyzed (current)
- **Tier-1**: Metrics analyzed for regressions (future)
- **Tier-2**: Full benchmark suite with golden comparisons (future)
