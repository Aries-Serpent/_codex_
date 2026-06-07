# Gap 17 — Data Drift Monitoring: Evidence

**Status:** ✅ Implemented  
**Date:** 2026-06-06  
**Branch:** copilot/explore-codebase-and-create-plan

---

## Implementation Summary

### New file: `src/codex_ml/monitoring/data_drift.py`

Implements a pure-Python, zero-external-dependency data drift detector with
two statistical methods:

| Class / Method | Description |
|---|---|
| `DataDriftDetector` | Main detector class |
| `DataDriftDetector.detect_psi()` | Population Stability Index (PSI) |
| `DataDriftDetector.detect_kl()` | KL-divergence D_KL(current ‖ reference) |
| `DataDriftDetector.check_epoch()` | Convenience wrapper — runs both methods |
| `DriftResult` | Dataclass holding score, threshold, severity, and per-bin details |

**Design decisions:**

- **No hard dependencies** — only `math` and the standard library are used.
  `numpy`/`scipy` are **not** required; the module is importable in minimal environments.
- **Epsilon smoothing** (default `1e-8`) is applied before normalisation to
  prevent `log(0)` and division-by-zero for zero-valued bins.
- **Automatic normalisation** — input distributions are normalised to sum to 1,
  so callers can pass raw counts or unnormalised histograms.
- **PSI thresholds** follow the industry-standard interpretation:
  - `< 0.1` → no significant change
  - `0.1–0.2` → slight change (monitor)
  - `> 0.2` → significant change (act)
- **KL thresholds**:
  - `< 0.1` → distributions very close
  - `0.1–0.5` → moderate divergence
  - `> 0.5` → strong divergence

### Wired into: `src/codex_ml/train_loop.py`

The `DataDriftDetector` is imported at module level and a single instance is
created before the epoch loop. At the end of each epoch, after the performance
monitor block:

1. The epoch's synthetic losses are bucketed into a 4-bin histogram.
2. On epoch 1 the histogram is stored as the **reference distribution**.
3. On subsequent epochs, `check_epoch()` computes both PSI and KL scores and
   appends a `"data_drift"` event to the metrics NDJSON file via
   `_append_metrics_event()`.
4. Any exception in the drift block is caught and logged at `DEBUG` level so
   drift monitoring **never crashes training**.

---

## Test Results

```
pytest tests/unit/test_data_drift.py -v --tb=short
```

```
================================================= test session info ==================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
asyncio: mode=Mode.AUTO

collected 27 items

tests/unit/test_data_drift.py::TestDetectPsiNoDrift::test_identical_distributions_score_near_zero PASSED
tests/unit/test_data_drift.py::TestDetectPsiNoDrift::test_identical_distributions_drifted_false PASSED
tests/unit/test_data_drift.py::TestDetectPsiDrift::test_shifted_distribution_exceeds_default_threshold PASSED
tests/unit/test_data_drift.py::TestDetectPsiDrift::test_bin_scores_list_has_correct_length PASSED
tests/unit/test_data_drift.py::TestDetectPsiDrift::test_psi_score_is_finite PASSED
tests/unit/test_data_drift.py::TestDetectKlNoDrift::test_identical_distributions_score_near_zero PASSED
tests/unit/test_data_drift.py::TestDetectKlDrift::test_shifted_distribution_exceeds_default_threshold PASSED
tests/unit/test_data_drift.py::TestDetectKlDrift::test_kl_score_non_negative PASSED
tests/unit/test_data_drift.py::TestDetectKlDrift::test_kl_bin_scores_length PASSED
tests/unit/test_data_drift.py::TestCheckEpoch::test_returns_both_methods PASSED
tests/unit/test_data_drift.py::TestCheckEpoch::test_epoch_no_drift_scenario PASSED
tests/unit/test_data_drift.py::TestCheckEpoch::test_epoch_drift_scenario PASSED
tests/unit/test_data_drift.py::TestDriftResultToDict::test_to_dict_contains_required_keys PASSED
tests/unit/test_data_drift.py::TestDriftResultToDict::test_to_dict_types PASSED
tests/unit/test_data_drift.py::TestInputValidation::test_psi_mismatched_lengths_raises PASSED
tests/unit/test_data_drift.py::TestInputValidation::test_kl_mismatched_lengths_raises PASSED
tests/unit/test_data_drift.py::TestEmptyInputs::test_psi_empty_reference_raises PASSED
tests/unit/test_data_drift.py::TestEmptyInputs::test_kl_empty_current_raises PASSED
tests/unit/test_data_drift.py::TestCustomThresholds::test_low_psi_threshold_flags_mild_shift PASSED
tests/unit/test_data_drift.py::TestCustomThresholds::test_high_psi_threshold_ignores_mild_shift PASSED
tests/unit/test_data_drift.py::TestCustomThresholds::test_invalid_threshold_raises PASSED
tests/unit/test_data_drift.py::TestEpsilonSmoothing::test_zero_bin_does_not_raise PASSED
tests/unit/test_data_drift.py::TestEpsilonSmoothing::test_zero_bin_kl_does_not_raise PASSED
tests/unit/test_data_drift.py::TestSingleBin::test_psi_single_bin_identical PASSED
tests/unit/test_data_drift.py::TestSingleBin::test_kl_single_bin_identical PASSED
tests/unit/test_data_drift.py::TestSymmetricDistribution::test_symmetric_uniform_psi_low PASSED
tests/unit/test_data_drift.py::TestSymmetricDistribution::test_feature_name_propagated PASSED

27 passed, 1 warning in 0.66s
```

**Result: 27/27 passed ✅**

---

## Files Changed

| File | Change |
|---|---|
| `src/codex_ml/monitoring/data_drift.py` | **New** — `DataDriftDetector` with `detect_psi()` and `detect_kl()` |
| `src/codex_ml/train_loop.py` | Wired drift detector after performance monitor block in epoch loop |
| `tests/unit/test_data_drift.py` | **New** — 27 unit tests (12 test classes) |
| `workbench/evidence/gap17_data_drift.md` | **New** — this file |
| `workbench/gap_backlog_prioritized.md` | Updated gap 17 status → ✅ Implemented |
| `workbench/wave_execution_control.md` | Updated Lane E row |

---

## CI Evidence Placeholder

> CI run will be triggered automatically when this branch is pushed.
> Expected workflow: the test file `tests/unit/test_data_drift.py` will be
> collected as part of the standard pytest run and all 27 tests should pass.
>
> Workflow: `.github/workflows/ci.yml` (or equivalent unit-test job)  
> Expected result: **27 passed, 0 failed**
