# Phase 5B Flaky Test Detection Report

Date: 2026-06-15
Scope: `tests/**`

## Detected `@pytest.mark.flaky` Tests

1. `tests/autonomy/test_autonomy_scheduler.py::TestBudgetCap::test_budget_cap_raises_on_timeout` (`reruns=2`)
2. `tests/autonomy/test_autonomy_scheduler.py::TestDecisionLoop::test_run_loop_dry_run_no_side_effects` (`reruns=2`)
3. `tests/autonomy/test_integration_budget_exhaustion.py::TestBudgetCap::test_budget_cap_raises_on_exhaustion` (`reruns=2`)
4. `tests/space_traversal/test_performance.py::test_file_cache_expiry` (`reruns=2`)
5. `tests/space_traversal/test_performance.py::test_file_cache_cleanup_expired` (`reruns=2`)
6. `tests/space_traversal/test_performance.py::test_profile_stage_context_manager` (`reruns=2`)

## Classification

- Timing/scheduler sensitivity: 5
- Subprocess latency sensitivity: 1
- `reruns >= 3`: 0 (no RP-002 escalation required)

## Stabilization Applied

- Added explicit timeout guards to timing-sensitive flaky tests:
  - `@pytest.mark.timeout(90)` on 5 tests
  - Existing `@pytest.mark.timeout(240)` retained on subprocess-sensitive test
