# Gap 37 — A/B Testing Framework: Evidence

**Status**: ✅ Implemented  
**Date**: 2025-07-11  
**Branch**: `copilot/explore-codebase-and-create-plan`

---

## Implementation Summary

### Files Created

| File | Purpose |
|------|---------|
| `src/codex_ml/experiments/ab_testing.py` | Core implementation |
| `src/codex_ml/experiments/__init__.py` | Public API exports |
| `tests/unit/test_ab_testing.py` | Unit test suite (29 tests) |

---

## API Overview

### `ABTest` dataclass
```python
@dataclass
class ABTest:
    name: str
    control_metrics: List[float]
    treatment_metrics: List[float]
    alpha: float = 0.05
```

Validates that `alpha ∈ (0, 1)` and each group has ≥ 2 observations.

### `ABTestResult` dataclass
```python
@dataclass
class ABTestResult:
    winner: str                          # "control" | "treatment" | "inconclusive"
    p_value: float
    effect_size: float                   # Cohen's d
    confidence_interval: Tuple[float, float]   # CI of mean difference at alpha
    significant: bool
```

### `run_ab_test(control, treatment, metric_name, alpha=0.05) -> ABTestResult`

- Uses **Welch's t-test** (`scipy.stats.ttest_ind(equal_var=False)`) when scipy is available
- Falls back to a **pure-stdlib Welch/t-distribution approximation** (Welch-Satterthwaite df + Lentz continued-fraction CDF) when scipy is not installed
- Computes **Cohen's d** using pooled standard deviation
- Computes a two-sided **confidence interval** of the mean difference at the given `alpha`

### `ABTestSuite`
- `add_test(test: ABTest)` — register a test (overwrites on duplicate name)
- `run_all() -> dict[str, ABTestResult]` — execute all tests
- `report() -> dict` — structured JSON-serialisable summary:
  ```json
  {
    "summary": {"total": 2, "significant": 1, "inconclusive": 1},
    "tests": {
      "click_rate": {
        "winner": "treatment",
        "p_value": 1.5e-18,
        "effect_size": 141.4,
        "confidence_interval": [9.87, 10.13],
        "significant": true
      },
      ...
    }
  }
  ```

---

## Statistical Choices

| Choice | Rationale |
|--------|-----------|
| Welch's t-test (unequal variances) | Robust when group variances differ |
| Cohen's d (pooled std) | Standard effect size for continuous metrics |
| Two-sided test | Conservative; detects improvement or degradation |
| Welch-Satterthwaite df | Correct df for unequal-variance case |
| Lentz continued fraction for t-CDF | Pure-Python; no numpy dependency required |

---

## Test Results

```
$ python -m pytest tests/unit/test_ab_testing.py -v --tb=short

collected 29 items

tests/unit/test_ab_testing.py::TestSignificantDifference::test_significant_flag_is_true PASSED
tests/unit/test_ab_testing.py::TestSignificantDifference::test_winner_is_not_inconclusive PASSED
tests/unit/test_ab_testing.py::TestSignificantDifference::test_p_value_below_alpha PASSED
tests/unit/test_ab_testing.py::TestInconclusiveResult::test_winner_inconclusive PASSED
tests/unit/test_ab_testing.py::TestInconclusiveResult::test_significant_flag_is_false PASSED
tests/unit/test_ab_testing.py::TestInconclusiveResult::test_p_value_high PASSED
tests/unit/test_ab_testing.py::TestEffectSize::test_large_effect_size_for_different_groups PASSED
tests/unit/test_ab_testing.py::TestEffectSize::test_zero_effect_size_for_identical_groups PASSED
tests/unit/test_ab_testing.py::TestEffectSize::test_effect_size_type_is_float PASSED
tests/unit/test_ab_testing.py::TestConfidenceIntervalSignificant::test_ci_excludes_zero PASSED
tests/unit/test_ab_testing.py::TestConfidenceIntervalSignificant::test_ci_is_ordered PASSED
tests/unit/test_ab_testing.py::TestConfidenceIntervalSignificant::test_ci_contains_true_difference PASSED
tests/unit/test_ab_testing.py::TestConfidenceIntervalInconclusive::test_ci_straddles_zero PASSED
tests/unit/test_ab_testing.py::TestSuiteReportStructure::test_report_has_summary_key PASSED
tests/unit/test_ab_testing.py::TestSuiteReportStructure::test_report_summary_has_required_keys PASSED
tests/unit/test_ab_testing.py::TestSuiteReportStructure::test_report_total_count PASSED
tests/unit/test_ab_testing.py::TestSuiteReportStructure::test_report_has_tests_key PASSED
tests/unit/test_ab_testing.py::TestSuiteReportStructure::test_report_tests_contains_registered_names PASSED
tests/unit/test_ab_testing.py::TestSuiteReportStructure::test_report_test_entry_has_required_keys PASSED
tests/unit/test_ab_testing.py::TestSuiteReportStructure::test_report_significant_count PASSED
tests/unit/test_ab_testing.py::TestAlphaThresholdSensitivity::test_significant_at_default_alpha PASSED
tests/unit/test_ab_testing.py::TestAlphaThresholdSensitivity::test_inconclusive_at_very_tight_alpha PASSED
tests/unit/test_ab_testing.py::TestTreatmentWinner::test_treatment_wins_when_treatment_mean_higher PASSED
tests/unit/test_ab_testing.py::TestControlWinner::test_control_wins_when_control_mean_higher PASSED
tests/unit/test_ab_testing.py::TestABTestDataclassValidation::test_invalid_alpha_raises PASSED
tests/unit/test_ab_testing.py::TestABTestDataclassValidation::test_zero_alpha_raises PASSED
tests/unit/test_ab_testing.py::TestABTestDataclassValidation::test_insufficient_control_observations_raises PASSED
tests/unit/test_ab_testing.py::TestABTestDataclassValidation::test_insufficient_treatment_observations_raises PASSED
tests/unit/test_ab_testing.py::TestABTestDataclassValidation::test_valid_construction_works PASSED

29 passed, 1 warning in 0.60s
```

---

## Done Criteria Check

| Criterion | Status |
|-----------|--------|
| `src/codex_ml/experiments/ab_testing.py` importable | ✅ |
| ≥ 6 unit tests all pass | ✅ 29/29 passed |
| Evidence file at `workbench/evidence/gap37_ab_testing.md` | ✅ (this file) |
| `workbench/gap_backlog_prioritized.md` gap 37 → `✅ Implemented` | ✅ |
