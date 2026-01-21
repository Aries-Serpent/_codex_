# Test Coverage Roadmap

**Status**: Active  
**Created**: 2026-01-18  
**Phase**: 14.0 - Test Coverage Foundation

---

## Executive Summary

This roadmap defines the strategy for improving test coverage from the current 27.5% to the target of 70%. With 518 untested modules identified, we prioritize testing based on module criticality, size, and dependency impact.

## Current State

| Metric | Value |
|--------|-------|
| Current Coverage | 27.5% |
| Target Coverage | 70% |
| Total Source Files | 714 |
| Files with Tests | 196 |
| Untested Modules | 518 |

## Priority Tiers

### Tier 1: Critical (Top 50 Modules)

Modules that are security-critical, core to functionality, or have high usage:

| Priority | Module | Size | Reason |
|----------|--------|------|--------|
| 1 | `src/codex_ml/training/unified_training.py` | 22KB | Core training infrastructure |
| 2 | `src/codex_ml/cli/main.py` | 28KB | Primary CLI entry point |
| 3 | `src/codex_ml/safety/moderation.py` | 11KB | Security-critical |
| 4 | `src/codex_ml/data/loader.py` | 18KB | Data pipeline core |
| 5 | `src/codex_ml/data/validation.py` | 17KB | Data integrity |
| 6 | `src/codex/cli/main.py` | 11KB | Alternative CLI |
| 7 | `src/codex/auth/oauth_manager.py` | 13KB | Authentication |
| 8 | `src/codex/security/storage.py` | 11KB | Security-critical |
| 9 | `src/codex_ml/training/legacy_api.py` | 61KB | Backward compatibility |
| 10 | `src/codex_ml/monitoring/codex_logging.py` | 30KB | Observability |

### Tier 2: High Priority (50-150)

Modules with significant functionality that support core features.

### Tier 3: Medium Priority (150-300)

Supporting modules that enhance functionality.

### Tier 4: Low Priority (300+)

Utility modules, stubs, and rarely-used features.

## Testing Strategy

### Phase 14.1: Core Module Testing (180+ tests)

1. **CLI Tests (55+ tests)**
   - `tests/cli/test_main.py` - Core CLI functionality (20+ tests)
   - `tests/cli/test_train.py` - Training commands (15+ tests)
   - `tests/cli/test_metrics.py` - Metrics commands (10+ tests)
   - `tests/cli/test_hydra.py` - Hydra integration (10+ tests)

2. **Data Tests (60+ tests)**
   - `tests/data/test_loader.py` - Data loading (25+ tests)
   - `tests/data/test_validation.py` - Data validation (20+ tests)
   - `tests/data/test_split.py` - Data splitting (15+ tests)

3. **Training Tests (65+ tests)**
   - `tests/training/test_unified.py` - Unified training (30+ tests)
   - `tests/training/test_legacy.py` - Legacy API (20+ tests)
   - `tests/training/test_strategies.py` - Training strategies (15+ tests)

### Phase 14.2: Security Hardening (60+ tests)

1. **Security Tests**
   - `tests/security/test_cve_monitor.py` (15+ tests)
   - `tests/security/test_denylist.py` (10+ tests)

2. **Safety Tests**
   - `tests/safety/test_sanitizers.py` (15+ tests)
   - `tests/safety/test_moderation.py` (20+ tests)

### Phase 14.5: Integration Testing (20+ tests)

1. **End-to-End Tests**
   - `tests/integration/test_rag_e2e.py`
   - `tests/integration/test_training_e2e.py`
   - `tests/integration/test_cli_api.py`
   - `tests/integration/test_security_flow.py`

## Test Patterns

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Use parametrized tests for edge cases
- Maintain fast execution (<1s per test)

### Integration Tests
- Test cross-module interactions
- Use real dependencies where safe
- Mark with `@pytest.mark.integration`
- May have longer execution times

### Property-Based Tests
- Use Hypothesis for invariant testing
- Focus on data transformation modules
- Test edge cases automatically

## Coverage Goals

| Phase | Target | Expected Coverage |
|-------|--------|------------------|
| 14.1 Complete | 50% | ~350 modules tested |
| 14.2 Complete | 60% | ~400 modules tested |
| 14.5 Complete | 70% | ~500 modules tested |

## Resources

- **Priority Matrix**: `.codex/qa_walkthrough/test_priority_matrix.json`
- **Coverage Analysis**: `https://github.com/Aries-Serpent/_codex_/blob/main/.codex/qa_walkthrough/coverage_analysis.json`
- **Test Templates**: `tests/templates/`
- **Test Patterns**: `docs/testing/TEST_PATTERNS.md`

## Quick Commands

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html

# Run specific module tests
pytest tests/cli/ -v

# Run with parallel execution
pytest -n auto

# Generate coverage report
coverage report --show-missing
```

---

**Last Updated**: 2026-01-18
