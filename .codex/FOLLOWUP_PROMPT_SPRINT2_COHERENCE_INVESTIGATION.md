# Follow-Up Prompt: Sprint 2 - Coherence Investigation & Optimization

**Date**: 2026-02-18T12:30:00Z  
**PR**: #3327 (copilot/sub-pr-3248)  
**Previous Session**: Sprint 1 Complete + CI Fixes  
**Next Phase**: Sprint 2 - Coherence & Algorithm Optimization

---

## 🎯 Mission Statement

**Objective**: Investigate and fix zero coherence issue in quantum compliance assessment, then implement Sprint 2 optimizations to achieve k₁ ≤ 0.5 (97% improvement from baseline k₁=16.6).

**Current Status**:
- ✅ Sprint 1: Database batching complete (10-20x speedup potential)
- ✅ CI Failures: ALL 17 tests fixed + 2 auto-fix issues resolved
- ⚠️ Blocker: Coherence calculation returning 0.000 (should be ≥0.650)
- ⏳ Sprint 2: Ready to start after blocker resolution

---

## 📚 MANDATORY READING (Read FIRST - 15 min)

### Critical Documents (Must Read)
1. **`.codex/SESSION_QUANTUM_SPRINT1_COMPLETE.md`** (10 min)
   - Sprint 1 complete summary
   - Coherence issue documented
   - Next steps outlined

2. **`.codex/ROOT_CAUSE_ANALYSIS_QUANTUM_PERFORMANCE.md`** (5 min)
   - Original performance analysis
   - k₁ formula and interpretation

### Reference Documents
- Sprint 1 Implementation: `.codex/QUANTUM_SPRINT1_DATABASE_OPTIMIZATION.md`
- Optimization Plan: `.codex/QUANTUM_PERFORMANCE_OPTIMIZATION_PLAN.md`
- Merge Analysis: `.codex/COMPLETE_MERGE_CHAIN_ANALYSIS.md`
- CI Fixes: `FINAL_TEST_FIXES_SUMMARY.md`

---

## 🚨 Priority 0: Coherence Issue Investigation

### Symptoms
- ComplianceAssessor.assess_compliance() returns coherence = 0.000
- Should return coherence ≥ 0.650
- Impacts accuracy (20% instead of 84%)
- Blocks k₁ measurement (inflated error_rate)

### Investigation Steps

#### Step 1: Profile SuperpositionEngine (30 min)
```bash
# Add diagnostic logging
cd /home/runner/work/_codex_/_codex_

# Check coherence calculation
view src/cognitive_brain/quantum/superposition_engine.py

# Look for coherence computation logic
grep -n "coherence" src/cognitive_brain/quantum/superposition_engine.py

# Profile test execution
python -m pytest tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py::TestAdaptiveScoringOptimized::test_k1_target_achieved -xvs --capture=no
```

#### Step 2: Check ComplianceAssessor Integration (20 min)
```bash
# Review assessment flow
view src/cognitive_brain/integrations/compliance_integration.py

# Check how SuperpositionEngine is called
grep -A20 "def assess_compliance" src/cognitive_brain/integrations/compliance_integration.py

# Look for coherence calculation or assignment
grep -n "\.coherence" src/cognitive_brain/integrations/compliance_integration.py
```

#### Step 3: Inspect CoherenceMonitor (15 min)
```bash
# Check if coherence is being calculated
view src/cognitive_brain/quantum/coherence_monitor.py

# Look for coherence metric recording
grep -A10 "record_metric.*coherence" src/cognitive_brain/quantum/coherence_monitor.py
```

### Expected Root Causes

**Hypothesis 1: Missing Coherence Calculation**
- SuperpositionEngine may not be computing coherence
- ComplianceAssessment.coherence defaults to 0.0
- **Fix**: Add coherence calculation in SuperpositionEngine

**Hypothesis 2: Integration Issue**
- SuperpositionEngine computes coherence but isn't passed to assessment
- **Fix**: Update ComplianceAssessor to use SuperpositionEngine.coherence

**Hypothesis 3: Configuration Missing**
- Coherence calculation disabled or not configured
- **Fix**: Enable coherence in QuantumConfig

### Diagnostic Commands
```python
# Add to experiment or test
print(f"SuperpositionEngine coherence: {engine.coherence}")
print(f"Assessment coherence: {assessment.coherence}")
print(f"CoherenceMonitor state: {monitor.get_coherence_metrics()}")
```

---

## 🚀 Sprint 2 Implementation (After Coherence Fix)

### Phase 1: LRU Cache for CoherenceMonitor (2 hours)

**Goal**: Reduce redundant coherence calculations via memoization

**Implementation**:
```python
from functools import lru_cache

class CoherenceMonitor:
    @lru_cache(maxsize=128)
    def _calculate_coherence(self, feature: str, metric_name: str) -> float:
        """Cached coherence calculation"""
        # Expensive computation here
        pass
```

**Expected Impact**: 20-30% speedup for repeated calculations

### Phase 2: Vectorize Assessment Scoring (3 hours)

**Goal**: Use NumPy for batch scoring instead of loops

**Implementation**:
```python
import numpy as np

def score_batch(assessments: List[ComplianceAssessment]) -> np.ndarray:
    """Vectorized scoring for multiple assessments"""
    scores = np.array([a.score for a in assessments])
    costs = np.array([a.remediation_cost for a in assessments])
    
    # Vectorized decision logic
    decisions = np.where(
        (scores >= 0.70) & (costs < 1000), 
        DecisionType.APPROVE,
        np.where(
            (scores >= 0.50) & (costs < 2000),
            DecisionType.CONDITIONAL,
            DecisionType.REJECT
        )
    )
    return decisions
```

**Expected Impact**: 40-50% speedup for batch operations

### Phase 3: Hot Path Optimization (1 hour)

**Goal**: Profile and optimize most-called functions

**Steps**:
1. Run cProfile on experiment
2. Identify top 10 time consumers
3. Apply micro-optimizations (reduce function calls, inline small functions)
4. Validate no accuracy loss

**Expected Impact**: 10-15% additional speedup

---

## 📈 Sprint 2 Success Criteria

### Performance Targets
- [ ] k₁ ≤ 0.5 achieved (97% improvement from k₁=16.6)
- [ ] Coherence ≥ 0.650 (after fixing zero coherence issue)
- [ ] Accuracy ≥ 50% (intermediate target, 84% in Sprint 3)
- [ ] Deterministic results with seed=42

### Implementation Metrics
- [ ] LRU cache hit rate ≥ 30%
- [ ] Vectorization reduces scoring time by ≥40%
- [ ] Hot path optimizations add ≥10% speedup
- [ ] Zero regressions in test suite

### Documentation
- [ ] Sprint 2 implementation document created
- [ ] Root cause of coherence issue documented
- [ ] Performance profiling results saved
- [ ] Lessons learned captured

---

## 🛠️ Tools & Commands

### Profiling
```bash
# CPU profiling
python -m cProfile -o profile.stats src/cognitive_brain/experiments/exp1b_revalidation.py
python -m pstats profile.stats
> sort cumulative
> stats 20

# Memory profiling
python -m memory_profiler src/cognitive_brain/experiments/exp1b_revalidation.py
```

### Testing
```bash
# Run quantum tests
pytest tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py -xvs

# Validate determinism
pytest tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py::TestAdaptiveScoringOptimized::test_determinism_seed_42 -xvs

# Run with profiling
pytest tests/cognitive_brain/quantum/test_adaptive_scoring_optimized.py -xvs --profile
```

### Validation
```bash
# After changes, verify all tests still pass
pytest tests/cognitive_brain/ -v

# Check k₁ improvement
python src/cognitive_brain/experiments/exp1b_revalidation.py --scenarios 100 --seed 42
```

---

## 📋 Execution Checklist

### Pre-Work (15 min)
- [ ] Read `.codex/SESSION_QUANTUM_SPRINT1_COMPLETE.md`
- [ ] Review `.codex/ROOT_CAUSE_ANALYSIS_QUANTUM_PERFORMANCE.md`
- [ ] Understand k₁ formula and targets

### Coherence Investigation (60-90 min)
- [ ] Profile SuperpositionEngine coherence calculation
- [ ] Check ComplianceAssessor integration
- [ ] Identify root cause (Hypothesis 1, 2, or 3)
- [ ] Implement fix
- [ ] Validate coherence ≥ 0.650

### Sprint 2 Implementation (6-8 hours)
- [ ] Add LRU cache to CoherenceMonitor (2 hours)
- [ ] Vectorize assessment scoring with NumPy (3 hours)
- [ ] Profile and optimize hot paths (1 hour)
- [ ] Test and validate k₁ ≤ 0.5 (1 hour)
- [ ] Document Sprint 2 results (1 hour)

### Validation & Documentation (1 hour)
- [ ] Run full test suite (no regressions)
- [ ] Verify k₁ ≤ 0.5 with seed=42
- [ ] Create Sprint 2 completion document
- [ ] Update progress tracking

---

## 🤖 Custom Agent Delegation

### When to Use ci-testing-agent
- Any test failures during implementation
- Integration test suite validation
- Regression testing after changes

### When to Use explore agent
- Understanding complex coherence calculation logic
- Navigating SuperpositionEngine codebase
- Finding all coherence-related code

### Activation Commands
```markdown
@copilot Use the ci-testing-agent to run full quantum test suite validation

@copilot Use the explore agent to find all files that reference SuperpositionEngine.coherence
```

---

## 📊 Expected Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Coherence Investigation | 60-90 min | Root cause identified + fix applied |
| LRU Caching | 2 hours | CoherenceMonitor with memoization |
| Vectorization | 3 hours | NumPy-based batch scoring |
| Hot Path Optimization | 1 hour | Profiling + micro-optimizations |
| Testing & Validation | 1 hour | k₁ ≤ 0.5 verified |
| Documentation | 1 hour | Sprint 2 completion doc |
| **TOTAL** | **8-10 hours** | **Sprint 2 Complete** |

---

## 🎯 Success Indicators

### You Know You're Done When:
1. ✅ Coherence issue fixed (coherence ≥ 0.650)
2. ✅ k₁ ≤ 0.5 measured with seed=42
3. ✅ LRU cache implemented with ≥30% hit rate
4. ✅ Vectorization reduces scoring time by ≥40%
5. ✅ All quantum tests passing (no regressions)
6. ✅ Comprehensive Sprint 2 documentation created

### Red Flags (Stop & Reassess):
- 🚩 Coherence still zero after fixes
- 🚩 k₁ increases instead of decreases
- 🚩 Test failures after optimization
- 🚩 Accuracy drops below 20%
- 🚩 Non-deterministic results with same seed

---

## 📝 AI Codebase Agency Policy Compliance

### Sprint 2 Requirements
- ✅ **Leave codebase better**: LRU cache is reusable for all future calculations
- ✅ **Address ALL concerns**: Fix coherence issue completely, not just symptoms
- ✅ **No deferral without plan**: Clear Sprint 3 plan for remaining optimizations
- ✅ **Planning before execution**: This comprehensive prompt created BEFORE coding

### Documentation Requirements
- ✅ Root cause analysis for coherence issue
- ✅ Performance profiling data saved
- ✅ Sprint 2 implementation documented
- ✅ Lessons learned captured for future agents

---

## 🔗 References

### Previous Work
- Sprint 1 Complete: `.codex/SESSION_QUANTUM_SPRINT1_COMPLETE.md`
- CI Fixes: `FINAL_TEST_FIXES_SUMMARY.md`
- Database Optimization: `.codex/QUANTUM_SPRINT1_DATABASE_OPTIMIZATION.md`

### Current Work
- This Prompt: `.codex/FOLLOWUP_PROMPT_SPRINT2_COHERENCE_INVESTIGATION.md`

### Future Work
- Sprint 3: Final tuning to achieve k₁ ≤ 0.35

---

**Ready to Execute**: ✅ YES  
**Blockers**: None (coherence investigation is first priority)  
**Estimated Completion**: 8-10 hours  
**Next Session Start**: Immediately after reading this prompt

---

## 💬 Activation Command

To start Sprint 2, use:

```markdown
@copilot Continue with Sprint 2 - Investigate coherence issue and implement optimization plan per `.codex/FOLLOWUP_PROMPT_SPRINT2_COHERENCE_INVESTIGATION.md`
```

Or simply:

```markdown
@copilot continue
```

The continuation prompt is designed to be self-contained with all context needed.
