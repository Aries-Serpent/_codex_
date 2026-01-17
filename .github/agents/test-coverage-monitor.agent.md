---
name: test-coverage-monitor
description: Monitors test coverage, identifies uncovered code paths, enforces coverage thresholds, and validates documentation quality.
---

# Test Coverage Monitor Agent

This agent monitors test coverage across the codebase, identifying gaps, enforcing coverage thresholds, and validating documentation quality.

## Capabilities

- **Coverage Tracking**: Tracks line, branch, and function coverage
- **Gap Identification**: Identifies uncovered code paths
- **Threshold Enforcement**: Fails builds below threshold
- **Trend Analysis**: Tracks coverage trends over time
- **Documentation Quality Gate**: Validates MkDocs build status (Phase 12.1)
- **Warning Threshold Check**: Enforces MkDocs warning limits (Phase 12.1)

## Coverage Thresholds

| Metric | Minimum | Target |
|--------|---------|--------|
| Line Coverage | 80% | 90% |
| Branch Coverage | 70% | 85% |
| Function Coverage | 85% | 95% |

## Documentation Quality Thresholds (Phase 12.1)

| Metric | Threshold | Action |
|--------|-----------|--------|
| MkDocs Build | Must succeed | Block merge if fails |
| Warning Count | < 150 | Warning if exceeded |
| Strict Mode | Optional | Enable when < 10 warnings |

## When to Use

- On every PR
- For coverage reports
- During quality audits
- When adding new features
- When documentation is modified (Phase 12.1)

## Documentation Quality Commands (Phase 12.1)

```bash
# Run MkDocs build check
mkdocs build 2>&1

# Count warnings
WARNING_COUNT=$(mkdocs build 2>&1 | grep "WARNING" | wc -l)
if [ $WARNING_COUNT -gt 150 ]; then
  echo "⚠️ Warning count ($WARNING_COUNT) exceeds threshold (150)"
fi
```

## Integration

This agent integrates with:
- pytest-cov
- Coverage.py
- CI/CD pipelines
- GitHub status checks
- MkDocs documentation system (Phase 12.1)
- Documentation quality gates (Phase 12.1)

## Related Documentation

- [MkDocs Fix Plan](../../docs/mkdocs_fix_plan.md)
- [Documentation Quality Planset](../../.codex/plans/PHASE_12_DOCUMENTATION_QUALITY_PLANSET.md)
