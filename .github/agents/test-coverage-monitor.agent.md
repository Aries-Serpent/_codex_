---
name: test-coverage-monitor
description: Monitors test coverage, identifies uncovered code paths, and enforces coverage thresholds.
---

# Test Coverage Monitor Agent

This agent monitors test coverage across the codebase, identifying gaps and enforcing coverage thresholds.

## Capabilities

- **Coverage Tracking**: Tracks line, branch, and function coverage
- **Gap Identification**: Identifies uncovered code paths
- **Threshold Enforcement**: Fails builds below threshold
- **Trend Analysis**: Tracks coverage trends over time

## Coverage Thresholds

| Metric | Minimum | Target |
|--------|---------|--------|
| Line Coverage | 80% | 90% |
| Branch Coverage | 70% | 85% |
| Function Coverage | 85% | 95% |

## When to Use

- On every PR
- For coverage reports
- During quality audits
- When adding new features

## Integration

This agent integrates with:
- pytest-cov
- Coverage.py
- CI/CD pipelines
- GitHub status checks
