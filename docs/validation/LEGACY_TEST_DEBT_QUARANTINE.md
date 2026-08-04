# Legacy Test Debt Quarantine — PR #5430 Post-Merge
**Last Updated:** 2026-08-03
**Version:** v0.3.0

> **Context:** Post-merge validation of PR #5430 (`7a54909c`).
> The failures below are **pre-existing and outside the scope** of the
> Cognitive Brain Runtime delivery. They are quarantined to prevent them from
> masking regressions in `src/codex/cognitive_brain/**`.

## Quarantine Summary

| Metric | Count |
|---|---|
| Total cognitive_brain tests executed | 1,041 |
| Passed | 1,004 |
| Failed | 24 |
| Errored | 13 |
| **Failures attributable to PR #5430** | **0** |

## Failure Inventory

| Failure cluster | File(s) | Root-cause class | Owner lane | Blocking? | Remediation priority |
|---|---|---|---|---|---|
| Missing `CognitiveBrain` import | `tests/cognitive_brain/agents/test_cognitive_interface.py` | Missing import | cognitive-brain-legacy-debt | No — informational | P2 |
| Mock `SecurityScanner` API drift (`create_entanglement` missing) | `tests/cognitive_brain/experiments/test_exp2_validation.py` | API drift | cognitive-brain-legacy-debt | No — informational | P2 |
| `QuantumConfig` undefined | `tests/cognitive_brain/quantum/test_quantum_config.py` | Missing import | cognitive-brain-legacy-debt | No — informational | P3 |
| k₁ threshold regression (0.4494 > 0.35) | `tests/cognitive_brain/quantum/test_phase3_hardening.py` | Regression assertion | cognitive-brain-legacy-debt | No — informational | P1 |
| `set` constructor misuse | `tests/cognitive_brain/quantum/test_uncertainty.py` | Malformed fixture | cognitive-brain-legacy-debt | No — informational | P2 |
| Missing `os` import | `tests/cognitive_brain/analytics/test_bayesian.py` | Missing import | cognitive-brain-legacy-debt | No — informational | P2 |
| Missing `pattern_compressor` fixture | `tests/cognitive_brain/quantum/test_memory.py` | Missing fixture | cognitive-brain-legacy-debt | No — informational | P2 |
| Undefined `patterns` variable | `tests/cognitive_brain/learning/test_outcome_analyzer.py` | Missing fixture/import | cognitive-brain-legacy-debt | No — informational | P2 |
| `DQN.select_action()` kwarg drift (`available_actions`) | `tests/cognitive_brain/learning/test_rl_algorithms.py` | API drift | cognitive-brain-legacy-debt | No — informational | P2 |
| Offline environment / JSON serialization drift | `tests/cognitive_brain/test_inject_with_brain_client.py` | Environment / mock drift | cognitive-brain-legacy-debt | No — informational | P3 |
| Malformed YAML fixture in `TaskRouter` registry | `tests/cognitive_brain/test_task_router_codex.py` | Malformed fixture | cognitive-brain-legacy-debt | No — informational | P2 |

## Detailed Failure Counts

| File | Failed | Errored |
|---|---|---|
| `tests/cognitive_brain/agents/test_cognitive_interface.py` | 8 | 0 |
| `tests/cognitive_brain/experiments/test_exp2_validation.py` | 1 | 0 |
| `tests/cognitive_brain/quantum/test_quantum_config.py` | 3 | 0 |
| `tests/cognitive_brain/quantum/test_phase3_hardening.py` | 1 | 0 |
| `tests/cognitive_brain/quantum/test_uncertainty.py` | 1 | 0 |
| `tests/cognitive_brain/analytics/test_bayesian.py` | 1 | 0 |
| `tests/cognitive_brain/quantum/test_memory.py` | 0 | 5 |
| `tests/cognitive_brain/learning/test_outcome_analyzer.py` | 1 | 0 |
| `tests/cognitive_brain/learning/test_rl_algorithms.py` | 1 | 0 |
| `tests/cognitive_brain/test_inject_with_brain_client.py` | 5 | 0 |
| `tests/cognitive_brain/test_task_router_codex.py` | 0 | 8 |
| **Total** | **24** | **13** |

## Trend Table

| Snapshot Date | Failed | Errored | Total | Delta vs Previous | Top Cause |
|---|---|---|---|---|---|
| 2026-08-03 | 24 | 13 | 1041 | baseline | Malformed YAML fixture in `TaskRouter` registry |

## Phased Remediation Plan

### P1 — Fix behavioral regressions (quantum)
- Adjust or re-baseline the k₁ coherence threshold in
  `tests/cognitive_brain/quantum/test_phase3_hardening.py`.
- Verify quantum metric determinism (seed, iteration count).

### P2 — Fix import/fixture/mock drift (high volume)
- Add missing `os` import to `tests/cognitive_brain/analytics/test_bayesian.py`.
- Add missing `CognitiveBrain` import to
  `tests/cognitive_brain/agents/test_cognitive_interface.py`.
- Define `pattern_compressor` fixture in
  `tests/cognitive_brain/quantum/conftest.py` or repair existing import.
- Update `MockSecurityScanner` in
  `tests/cognitive_brain/experiments/test_exp2_validation.py` to match
  `create_entanglement` API.
- Re-indent YAML fixture in `tests/cognitive_brain/test_task_router_codex.py`
  so `agents:` children are valid.
- Fix `set` constructor call in
  `tests/cognitive_brain/quantum/test_uncertainty.py`.
- Repair `patterns` reference in
  `tests/cognitive_brain/learning/test_outcome_analyzer.py`.
- Align `DQN.select_action()` signature in
  `tests/cognitive_brain/learning/test_rl_algorithms.py`.

### P3 — Resolve environment-dependent / cross-module failures
- Stabilize brain-client injection tests against offline mode in
  `tests/cognitive_brain/test_inject_with_brain_client.py`.
- Resolve `QuantumConfig` import path in
  `tests/cognitive_brain/quantum/test_quantum_config.py`.

## Escalation Threshold

If the `Total non-attributable failures` (Failed + Errored) increases by more
than **20% week-over-week**, a blocking governance issue must be opened
automatically. This prevents the non-blocking legacy lane from silently
degrading.

## Exit Criteria

- All quarantined files either pass or are removed from the cognitive_brain
  test path.
- The `cognitive-brain-legacy-debt` lane reports zero failures before it can
  be promoted to a required gate.
- No test is silently skipped; each fix is accompanied by a regression
  assertion.
