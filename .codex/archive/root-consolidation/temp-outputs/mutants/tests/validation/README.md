# Coverage Baseline Monitoring Validation Tests

This directory contains the validation test suite for the Coverage Baseline Monitoring Plan (Phase 2 of implementation).

## Overview

These tests validate the following aspects of the coverage monitoring system:

1. **test_coverage_determinism.py** - Tests that the test suite behavior is consistent and deterministic
2. **test_coverage_regression.py** - Tests that coverage doesn't regress from the locked baseline
3. **test_module_coverage_gates.py** - Tests that modules/tiers meet minimum coverage requirements
4. **test_quality_metrics.py** - Tests that test quality metrics meet phase requirements

## Running the Tests

### Run all validation tests
```bash
pytest tests/validation/
```

### Run specific validation test suite
```bash
# Test determinism
pytest tests/validation/test_coverage_determinism.py -v

# Test regression detection
pytest tests/validation/test_coverage_regression.py -v

# Test module gates
pytest tests/validation/test_module_coverage_gates.py -v

# Test quality metrics
pytest tests/validation/test_quality_metrics.py -v
```

### Run with markers
```bash
# Run all validation tests
pytest tests/validation/ -m validation

# Run only determinism tests
pytest tests/validation/ -m determinism

# Run regression and module gates
pytest tests/validation/ -m "regression or module_gates"
```

## Test Output

Each test suite generates a JSON report in `.codex/coverage/`:

- `DETERMINISM_VALIDATION_REPORT.json` - 3-run determinism validation
- `REGRESSION_DETECTION_REPORT.json` - Baseline comparison and regression detection
- `MODULE_COVERAGE_VALIDATION_REPORT.json` - Module-level tier gate results
- `QUALITY_METRICS_VALIDATION_REPORT.json` - Quality metric validation results

## CI/CD Integration

These tests are automatically run on:
- **Every PR:** Validates regression before merge
- **Nightly:** Full determinism suite (3 runs) for trend analysis
- **Phase gates:** Final validation before phase progression

## Key Validation Criteria

### Determinism Tests
- ✅ All 3 runs pass (exit_code == 0)
- ✅ Coverage variance < 0.1%
- ✅ Test count identical across runs
- ✅ No new failures in any run

### Regression Tests
- ✅ Overall coverage within baseline ±1.5%
- ✅ No module loses more than tier tolerance
- ✅ Test count stable or increasing
- ✅ Quality metrics maintained

### Module Gates Tests
- ✅ Tier 1 (Security) ≥ 90% (baseline) / ≥ 92% (Phase 1+)
- ✅ Tier 2 (Auth) ≥ 85%
- ✅ Tier 3 (Infrastructure) ≥ 77%
- ✅ Tier 4 (Extended) ≥ 62% (baseline) / ≥ 70% (Phase 1)

### Quality Metrics Tests
- ✅ Pass rate ≥ 99.5%
- ✅ Flakiness ≤ 1.0% (baseline) / ≤ 0.5% (Phase 1+)
- ✅ Determinism ≥ 99.5% (baseline) / = 100% (Phase 1+)
- ✅ Isolation = 100%

## Phase-Based Gate Updates

The validation thresholds automatically adjust based on the current phase:

| Phase | Coverage | Pass Rate | Flakiness | Determinism |
|-------|----------|-----------|-----------|-------------|
| Baseline | 34.63% ±1.5% | ≥99.5% | ≤1.0% | ≥99.5% |
| Phase 1 | 40.0% ±0.5% | ≥99.5% | ≤0.5% | 100% |
| Phase 2+ | Progressive | ≥99.5% | ≤0.5% | 100% |

## Troubleshooting

### Determinism test fails
- Check for test order dependencies (use pytest-randomly with fixed seed)
- Verify no hardcoded delays or file system race conditions
- Ensure proper test isolation (no shared state between tests)

### Regression detected
- Run `python scripts/ci/generate_baseline_tracking_report.py` for current metrics
- Compare against `.codex/COVERAGE_BASELINE_34_63.json`
- Use `REGRESSION_DETECTION_REPORT.json` to identify which modules regressed

### Module gate fails
- Check specific tier in `MODULE_COVERAGE_VALIDATION_REPORT.json`
- Review module-level coverage in `.codex/coverage/MODULE_BASELINE_MATRIX.json`
- Add targeted tests for modules below minimum

### Quality metrics fail
- Check `QUALITY_METRICS_VALIDATION_REPORT.json` for specific failures
- If flakiness high: investigate test isolation issues, use autonomous-test-healer
- If determinism low: check for non-deterministic assertions or random data
- If pass rate low: investigate test infrastructure or environmental issues

## Documentation

- **Validation Plan:** `.codex/COVERAGE_VALIDATION_CRITERIA.md`
- **Phase Gates:** `.codex/PHASE_VALIDATION_GATES.yaml`
- **Implementation Plan:** `.codex/PHASE_1_IMPLEMENTATION_PLAN.md`
- **Baseline Snapshot:** `.codex/COVERAGE_BASELINE_34_63.json`
- **Module Matrix:** `.codex/coverage/MODULE_BASELINE_MATRIX.json`

## Related Scripts

- `scripts/ci/generate_baseline_tracking_report.py` - Generate baseline tracking reports
- `scripts/ci/generate_coverage_map.py` - Generate per-module coverage analysis
- `scripts/ci/enforce_actions_versions.py` - Validate GitHub Actions versions

## Next Steps

After Phase 2 validation framework is complete:
- **Phase 3:** Dashboard and reporting automation
- **Phase 4:** Agent integration with unified-coverage-agent
- **Phase 5:** Go-live and Phase 1 test generation kickoff
