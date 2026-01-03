# Phase 8.7 Metrics Directory

This directory stores JSON/JSONL metrics artifacts for Phase 8.7 Universal Intelligence.

## Schema

All metrics follow this JSON schema:

```json
{
  "metric": "k1|zero_shot|few_shot_k10|neg_transfer|forgetting|emergence_count|confidence_ece",
  "value": 0.123,
  "timestamp": "2026-01-03T02:30:00Z",
  "evidence": {
    "run_id": "run:abc123",
    "seed": 12345,
    "task_id": "task:environment_name"
  }
}
```

## Metric Definitions

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

- `k1_metrics.jsonl` - Decision quality metrics
- `transfer_metrics.jsonl` - Transfer learning metrics
- `emergence_events.jsonl` - Emergence detection logs
- `confidence_calibration.jsonl` - Calibration metrics

## CI Integration

- **Tier-0**: Metrics generated but not analyzed
- **Tier-1**: Metrics analyzed for regressions
- **Tier-2**: Full benchmark suite with golden comparisons
