# Cognitive Brain Continuation Prompt — Phase 6 Production Graduation

> **Version:** 6.2.0
> **Created:** 2026-02-19 (Session 39)
> **Updated:** 2026-02-20 (Session 43) — PR #3336 CI+CodeQL resolution complete
> **Status:** READY FOR EXECUTION (PR #3336 fixes committed, pending CI green)
> **Blocking PR**: [#3336](https://github.com/Aries-Serpent/_codex_/pull/3336) — CI fixes pending
> **Full Planset**: `.codex/plans/PHASE6_CONTINUATION_PLANSET.md`
> **Consolidation Map**: `.codex/PRODUCTION_READINESS_CONSOLIDATION_MAP.md` 🆕
> **Previous Phase:** Phase 5 + CI Remediation (Sessions 35–43) — ✅ COMPLETE
> **Branch:** `copilot/sub-pr-3336`
> **PR:** #3336

---

## 🎯 Session Start Checklist (MUST DO FIRST)

1. **Verify CI green** — check if Resilient Validation Suite (run 22203971518 on commit 756c152,
   then the follow-up commit with evaluator.py fix) passed:
   ```bash
   gh run view 22203971518 --job 64224708717  # slow
   gh run view 22203971518 --job 64224708718  # quick
   ```
2. **Load memories**: Review stored facts for hf_pinning, CI false positives, conftest xfail
3. **Check git status**: `git log --oneline -5 && git status --short`

---

## 📊 Current State (as of 2026-02-19 Session 39)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Accuracy | 100% | ≥84% | ✅ |
| Coherence | 0.814 | ≥0.650 | ✅ |
| k₁ | 0.332 | ≤0.35 | ✅ |
| Tests | 346 | All pass | ✅ |
| Scalability (1000×5) | 96.8% | ≥95% | ✅ |
| Noise (10% gate) | 91.4% | ≥90% | ✅ |
| CodeQL alerts | 0 | 0 | ✅ |
| Ruff errors | 0 | 0 | ✅ |
| CI false positives | 0 blocking | 0 blocking | ✅ |
| Agent files k₁=0.332 | All updated | All | ✅ |

---

## 🔴 Priority 1 — Immediate

### P1.1: Verify evaluator.py fix resolves test_run_eval_cli

**What was fixed** (last commit before this session):
- Removed `revision=get_hf_revision()` from `src/codex_ml/eval/evaluator.py` lines 122+129
- This allows `ensure_pinned_kwargs` to check `KNOWN_MODEL_REVISIONS` (real hash) before env vars (fake `abcdef0`)
- Previously: `get_hf_revision()` returned `HF_REVISION=abcdef0` → HuggingFace 404 error
- Now: `KNOWN_MODEL_REVISIONS["sshleifer/tiny-gpt2"]` = real commit hash → works or graceful skip

**If test_run_eval_cli STILL fails after this fix**, check:
```text
# src/codex_ml/eval/run_eval.py — does it also call get_hf_revision() explicitly?
grep -n "get_hf_revision\|revision=" src/codex_ml/eval/run_eval.py
```

## P1.2: Python 3.12 Migration Phase 2

**Condition**: Only after base-branch (`copilot/investigate-coherence-issue`) CI is confirmed green.

**Change**:
```toml
# pyproject.toml
requires-python = ">=3.12"  # Restore from ">=3.11,<3.13"
```

**Verification**:
```bash
PYTHONPATH=src pytest tests/ -v --timeout=300 -x -q 2>&1 | tail -20
```

---

## 🟡 Priority 2 — Active Learning Production Graduation

**Goal**: Graduate Active Learning from staging to production with budget controls.

**Files to modify**:
- `src/cognitive_brain/active_learning/hook.py` — add `query_budget_per_day: int = 50` parameter
- `src/cognitive_brain/monitoring/agent_dashboard.py` — add active learning budget tracking to `get_health()`
- `k8s/monitoring/agent_dashboard.yaml` — update alert rule `active_learning > 50/day`

**Feature flag**: Set `CODEX_ACTIVE_LEARNING=true` in production config
**Budget enforcement**: Add `_enforce_query_budget()` in `hook.py`:
```python
def _enforce_query_budget(self) -> bool:
    today = datetime.utcnow().date().isoformat()
    count = self._daily_counts.get(today, 0)
    if count >= self.query_budget_per_day:
        logger.warning("Active learning query budget (%d/day) exceeded", self.query_budget_per_day)
        return False
    self._daily_counts[today] = count + 1
    return True
```

**Tests**: Add `test_query_budget_enforced` in `tests/cognitive_brain/active_learning/`

---

## 🟡 Priority 2 — Extended Noise Validation (1000 scenarios)

**Current**: 91.4% accuracy at 10% gate error on 200 scenarios ✅
**Target**: Verify ≥90% at 10% gate error on 1000 scenarios

```bash
PYTHONPATH=src python src/cognitive_brain/experiments/exp1b_revalidation.py \
  --multi-seed --scenarios 1000 --noise-rate 0.10 \
  --save-json audit_artifacts/validation/noise_10percent_1000scenarios.json
```

---

## 🟢 Priority 3 — Enhancement

### Bayesian CPD EM Update

**Goal**: Update CPDs in `audit_artifacts/poctune/target_patterns.json` using real compliance corpus.

**Method**:
```python
# In src/cognitive_brain/analytics/bayesian.py
def update_cpds_em(corpus: list[dict], learning_rate: float = 0.1) -> None:
    """Expectation-Maximization update of Conditional Probability Distributions."""
    ...
```

## Chain Prompting Integration Tests

**Goal**: Validate multi-agent compliance workflows end-to-end.

**File**: `tests/cognitive_brain/integration/test_chain_prompting.py`

```python
def test_compliance_chain_prompting_workflow():
    brain = CognitiveBrain.create(QuantumConfig())
    # Step 1: Initial assessment
    decision1 = brain.decide("review", {"score": 0.7, "risk": "medium"})
    # Step 2: Follow-up with context
    decision2 = brain.decide("escalation", {"prior_decision": decision1.decision}, session_id=decision1.session_id)
    assert decision2.session_id == decision1.session_id  # Same session chain
```

---

## 🔑 Key Technical Facts (verified 2026-02-19)

### hf_pinning.py priority order
```
ensure_pinned_kwargs priority:
1. Caller-supplied revision/commit_id in kwargs  ← evaluator.py WAS here (wrong)
2. KNOWN_MODEL_REVISIONS (curated production pins)  ← evaluator.py NOW hits here ✅
3. Environment variables (HF_REVISION, etc.) — only for unknown models
4. ValueError — remote models must have a pin
```

### Graceful degradation (confirmed ✅)
```
load_from_pretrained():
  1. Try local cache (fast, offline) → local_files_only=True
  2. Try network download → fallback
  3. Raise HFModelUnavailableError → tests call pytest.skip()
```

### CI false positive pattern
- **CORRECT approach**: `pytest.importorskip()` for missing optional deps (faiss, sentencepiece)
- **CORRECT approach**: `pytest.skip()` in test when `HFModelUnavailableError` caught
- **WRONG approach**: `xfail(strict=False)` to hide any failures without root-cause fix

### Key files
- `src/codex_ml/utils/hf_pinning.py` — KNOWN_MODEL_REVISIONS, ensure_pinned_kwargs, load_from_pretrained, HFModelUnavailableError
- `src/codex_ml/eval/evaluator.py` — run_evaluator() NO LONGER passes explicit revision
- `src/codex_ml/utils/checkpointing.py` — _torch_dump, _pickle_dump with TypeError/RuntimeError guard
- `tests/conftest.py` — disable_torch_profiler fixture (C++ JIT profiling disabled)
- `.gitignore` — audit_artifacts/** (glob not directory); CI session report patterns blocked

---

## ✅ Verification Commands

```bash
# 1. Quantum compliance suite (346 tests)
PYTHONPATH=src pytest tests/cognitive_brain/ -v --tb=short
# Expected: 346 passed, 7 skipped

# 2. HF pinning behavior
python3 -c "
from codex_ml.utils.hf_pinning import ensure_pinned_kwargs
rev, _ = ensure_pinned_kwargs('sshleifer/tiny-gpt2', {})
print(f'tiny-gpt2 revision: {rev}')
assert rev != 'abcdef0', 'abcdef0 is a fake stub hash!'
print('✅ KNOWN_MODEL_REVISIONS working correctly')
"

# 3. Ruff lint
ruff check src/codex_ml/ src/cognitive_brain/ --select F401,I001,F841

# 4. No /tmp important files
find /tmp -name "*.py" -o -name "*.json" -o -name "*.md" 2>/dev/null | grep -v pytest | grep -v pip

# 5. No untracked files
git ls-files --others --exclude-standard
```

---

## 📝 Accountability Note

See `.codex/ACCOUNTABILITY_REPORT_2026_02_19_PR3330.md` for root-cause analysis of the xfail policy violations in sessions 37–38.

**Rule**: NEVER mark a test xfail without (a) confirming it fails on the base branch AND (b) documenting which specific commit on the base branch has the same failure. Torch/HF environment failures must be fixed with proper imports (importorskip, HFModelUnavailableError) not xfail.
