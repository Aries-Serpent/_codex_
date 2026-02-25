# Planset: P2 — Phase 6 Production Graduation

**Status**: 🟡 READY — Begins after PR #3339 merge
**Priority**: P2 — Short-term
**Created**: 2026-02-20
**Ref**: `docs/cognitive_brain/prompts/COGNITIVE_BRAIN_CONTINUATION_PROMPT_PHASE6.md`

---

## Objective

Graduate the Cognitive Brain system from Phase 5 (complete) to Phase 6 production readiness. Three parallel tracks.

---

## Track A: Python ≥3.12 pyproject.toml Restore

**Goal**: Re-enable `requires-python = ">=3.12"` after verifying all dependencies are compatible.

### Steps

1. **Audit current pyproject.toml**
   ```bash
   grep -n "requires-python\|python_requires" pyproject.toml
   ```

2. **Check dependency compatibility matrix**
   ```bash
   pip install pip-audit
   pip-audit --requirement requirements.txt --format json | jq '.dependencies[] | select(.vulns | length > 0)'
   ```

3. **Run full test suite with Python 3.12 strict mode**
   ```bash
   python3.12 -m pytest tests/ -x --tb=short -q
   ```

4. **Restore `requires-python = ">=3.12"`** in `pyproject.toml` if all pass

**Success Criterion**: `python_requires=">=3.12"` in pyproject.toml, CI green.

---

## Track B: Active Learning Graduation

**Goal**: Enable `CODEX_ACTIVE_LEARNING=true` with ≤50 samples/day rate limiting.

### Steps

1. **Verify active learning module**
   ```bash
   python3 -c "from src.cognitive_brain.learning import active_learner; print('OK')"
   ```

2. **Configure rate limiter**
   ```python
   # src/cognitive_brain/learning/active_learner.py
   MAX_SAMPLES_PER_DAY = int(os.getenv("CODEX_AL_MAX_SAMPLES_PER_DAY", "50"))
   ```

3. **Enable in CI** by adding to CI workflow env:
   ```yaml
   env:
     CODEX_ACTIVE_LEARNING: "true"
     CODEX_AL_MAX_SAMPLES_PER_DAY: "50"
   ```

4. **Monitor for 3 CI runs** — confirm no performance regressions

**Success Criterion**: `CODEX_ACTIVE_LEARNING=true` in CI, coherence ≥ 0.814, k₁ ≤ 0.332.

---

## Track C: Extended Noise & Bayesian CPD

### C1: Extended Noise Scenarios (1000 scenarios)

**Goal**: Validate cognitive brain resilience under 1000 noise scenarios (up from 100).

```python
# tests/cognitive_brain/test_noise_extended.py
@pytest.mark.parametrize("scenario_id", range(1000))
def test_noise_resilience_extended(scenario_id, noise_scenario_generator):
    scenario = noise_scenario_generator(scenario_id, error_rate=0.10)
    result = cognitive_brain.process(scenario)
    assert result.accuracy >= 0.90
```

**Success Criterion**: ≥90% pass rate across 1000 scenarios.

### C2: Bayesian CPD Expectation-Maximization

**Goal**: Upgrade Bayesian Change Point Detection from heuristic to EM algorithm.

```python
# src/cognitive_brain/analytics/bayesian.py — update _fit_changepoints()
def _fit_changepoints_em(self, observations, max_iter=100, tol=1e-6):
    """EM algorithm for Bayesian CPD — replaces heuristic detection."""
    ...
```

**Files**: `src/cognitive_brain/analytics/bayesian.py`, `tests/cognitive_brain/analytics/test_bayesian.py`

**Success Criterion**: EM algorithm converges in ≤100 iterations; CPD accuracy ≥ existing heuristic.

---

## Track D: Chain Prompting Tests

**Goal**: Validate multi-step chain prompting across cognitive brain agents.

```python
# tests/cognitive_brain/test_chain_prompting.py
def test_two_step_chain():
    step1 = agent.prompt("Assess code quality")
    step2 = agent.prompt("Based on previous assessment, suggest fixes", context=step1)
    assert step2.references_previous_context()
```

**Files**: `tests/cognitive_brain/test_chain_prompting.py` (new)

---

## Execution Order

```
Week 1: Track A (pyproject ≥3.12) — unblocks other work
Week 2: Track B (Active Learning) — parallel with Track C
Week 3: Track C1 (1000 noise scenarios) — parallel with Track C2
Week 3: Track C2 (Bayesian CPD EM)
Week 4: Track D (Chain prompting tests)
Week 4: Integration test — all tracks together
```

---

## Entry Condition

- [ ] PR #3339 merged into `copilot/sub-pr-3248`
- [ ] CI green on `copilot/sub-pr-3248`
- [ ] All CodeQL alerts at 0 on base branch

## Exit Condition

- [ ] All 4 tracks complete
- [ ] Cognitive Brain v6.0 status doc created: `COGNITIVE_BRAIN_STATUS_PHASE6_COMPLETE.md`
- [ ] Phase 7 planning initiated
