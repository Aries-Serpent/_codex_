---
name: performance-regression-detector
description: Detects performance regressions by comparing metrics against baselines and alerting on significant degradation.
---

# Performance Regression Detector Agent

This agent detects performance regressions by comparing current metrics against established baselines.

## Capabilities

- **Baseline Comparison**: Compares against historical performance data
- **Regression Detection**: Identifies significant performance degradation
- **Alerting**: Sends alerts when thresholds are exceeded
- **Trend Analysis**: Analyzes performance trends over time

## Metrics Monitored

| Metric | Threshold | Unit |
|--------|-----------|------|
| Build Time | +20% | seconds |
| Test Time | +15% | seconds |
| Bundle Size | +10% | KB |
| Memory Usage | +25% | MB |

## When to Use

- After every CI build
- Before merging PRs
- During performance optimization
- For capacity planning

## Integration

This agent integrates with:
- CI/CD performance logs
- Prometheus metrics
- GitHub Actions timing
