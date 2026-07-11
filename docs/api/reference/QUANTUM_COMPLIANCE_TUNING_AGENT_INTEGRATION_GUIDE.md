# INTEGRATION GUIDE: quantum-compliance-tuning-agent (Phase 4.5)
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status**:  **CONFIRMED ACTIVE** as of 2026-07-01  
**Version**: 1.0.0-phase4.5  
**Maturity**: Beta → **Production** (upgraded)  
**Integration Level**: Cognitive Brain Level 2 (Integration)  

---

## Overview

The `quantum-compliance-tuning-agent` is a **core component** of the Aries-Serpent quantum compliance assessment system. It is the exclusive executor of the `QI_TESTING` improvement area within the `QuantumPlansetEngine`, managing iterative tuning of Bayesian and Fuzzy Logic compliance decision boundaries.

This guide documents its active integration points and Phase 4.5 workflow.

---

## Quick Facts

| Property | Value |
|----------|-------|
| **Primary Responsibility** | Iterate Bayesian posterior + Fuzzy Logic tuning for Phase 4.5 accuracy improvement |
| **Improvement Area** | `ImprovementArea.QI_TESTING` (exclusive executor) |
| **Integration Points** | 10+ deep references in quantum subsystem |
| **Test Coverage** | 27 dedicated tests in `tests/cognitive_brain/quantum/test_phase4_tuning.py` |
| **Feature Flags** | `CODEX_BAYESIAN_MODE`, `CODEX_FUZZY_MODE` |
| **Permission Tier** | Not assigned (internal use only, no external calls needed) |
| **Cognitive Tools** | BayesianAssessor, FuzzyEngine, QuantumPlansetEngine |

---

## Active Workflow: QI_TESTING Improvement Area

The agent orchestrates a 7-step **entangled workflow** for compliance pattern tuning:

```
┌─────────────────────────────────────────────────────┐
│ QuantumPlansetEngine.generate(ImprovementArea.QI_TESTING)
│ with context: {failing_patterns, k₁_metric}
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ generate() output:
        │ superposition of 7
        │ entangled steps
        └──────────────────────┘
                   │
        ┌──────────▼──────────────────────────────┐
        │ Collapse via Born Rule probabilities:
        │  Impact × Confidence → Amplitude
        └──────────────────────────────────────────┘
                   │
        ┌──────────▼──────────────────────────────┐
        │ Execution Order (if QI-01 has highest
        │ effective amplitude):
        │ QI-01 → QI-02 → QI-03 → QI-04 →
        │ QI-05 → QI-06 → QI-07
        └──────────────────────────────────────────┘
```

### 7 Steps (Entangled Execution)

#### **QI-01: Baseline Scalability Run** (Impact=0.95, Conf=0.99)
```bash
PYTHONPATH=src python src/cognitive_brain/experiments/exp1b_revalidation.py \
  --multi-seed --scenarios 200 --use-verified-labels \
  --save-json audit_artifacts/results/phase4_scalability_raw.json
```
- **Purpose**: Establish per-seed accuracy baseline for patterns H/F/E/C
- **Output**: `phase4_scalability_raw.json` with per-seed, per-pattern accuracy
- **Executor**: `quantum-compliance-tuning-agent`

#### **QI-02: Per-Pattern Accuracy Report** (Impact=0.90, Conf=0.98)
```bash
python tools/analysis/per_pattern_report.py \
  audit_artifacts/results/phase4_scalability_raw.json \
  --output audit_artifacts/poctune/iteration_N_per_pattern.json
```
- **Purpose**: Identify patterns below 95% accuracy threshold (H, F, E, C)
- **Output**: Per-pattern breakdown with failure counts, root causes
- **Executor**: `quantum-compliance-tuning-agent`
- **Entangled with**: QI-01 (depends on baseline)

#### **QI-03: Update Tuning Rules** (Impact=0.85, Conf=0.85)
```python
# Update audit_artifacts/poctune/target_patterns.json
# Increase effect_factor for failing patterns
{
  "patterns": {
    "H": {"effect_factor": 1.5},  # was 1.3
    "F": {"effect_factor": 1.6},  # was 1.2
    "E": {"effect_factor": 1.1},  # was 1.0
    "C": {"effect_factor": 1.2}   # was 1.0
  }
}
```
- **Purpose**: Adjust tuning parameters based on QI-02 report
- **Executor**: `quantum-compliance-tuning-agent` (with human review)
- **Entangled with**: QI-02 (depends on per-pattern report)

#### **QI-04: Run Tuned Experiment** (Impact=0.88, Conf=0.82)
```bash
CODEX_BAYESIAN_MODE=true CODEX_FUZZY_MODE=true \
PYTHONPATH=src python src/cognitive_brain/experiments/exp1b_revalidation.py \
  --multi-seed --scenarios 200 --use-verified-labels \
  --save-json audit_artifacts/poctune/iteration_N_tuned_results.json
```
- **Purpose**: Re-run experiment with updated tuning rules activated
- **Tuning Hooks**: 
  - `BayesianAssessor.apply_tuning_rules()` picks up target_patterns.json
  - `FuzzyEngine.apply_membership_tuning()` adjusts boundaries
- **Output**: `iteration_N_tuned_results.json`
- **Executor**: `quantum-compliance-tuning-agent`
- **Entangled with**: QI-03 (depends on rule updates)

#### **QI-05: Compare Before vs After** (Impact=0.80, Conf=0.90)
```python
# Compare audit_artifacts/poctune/iteration_N_per_pattern.json
# with new per-pattern report from iteration_N_tuned_results.json
# Measure improvement: Δ = after_accuracy - before_accuracy
# Decision: Δ ≥ 5 percentage points for acceptance
```
- **Purpose**: Validate that tuning improved accuracy
- **Success Threshold**: ≥ 5pp improvement per pattern
- **Output**: Comparison report with deltas
- **Executor**: `quantum-compliance-tuning-agent`
- **Entangled with**: QI-04 (depends on tuned results)

#### **QI-06: Regression Guard** (Impact=0.92, Conf=0.97)
```bash
# Single-seed benchmark: seed=42, 110 scenarios
# Requirements:
#   - accuracy must = 100% (no regression)
#   - k₁ metric must ≤ 0.35 (no tuning overhead explosion)
# If regression detected: FAIL → QI-07 reverts all changes
```
- **Purpose**: Ensure tuning never degrades baseline single-seed accuracy
- **Requirements**:
  - Accuracy on seed=42 = 100% (zero regression tolerance)
  - k₁ ≤ 0.35 (tuning overhead bounded)
- **Result**: PASS/FAIL
- **Executor**: `quantum-compliance-tuning-agent`
- **Entangled with**: QI-05 (comparison result used to decide if QI-06 is triggered)

#### **QI-07: Accept or Revert** (Impact=0.75, Conf=0.88)
```python
if (improvement_per_pattern >= 5pp) and (regression_guard == PASS):
    # ACCEPT: commit target_patterns.json
    git add audit_artifacts/poctune/target_patterns.json
    # Mark iteration as COMPLETE
else:
    # REVERT: discard target_patterns.json changes
    git checkout audit_artifacts/poctune/target_patterns.json
    # Loop back to QI-03 with conservative adjustments
    # Maximum 5 iterations (diminishing returns expected after 3)
```
- **Purpose**: Final decision: accept tuning or revert and retry
- **Accept Criteria**: Δ ≥ 5pp AND QI-06 PASS
- **Revert Criteria**: Δ < 5pp OR QI-06 FAIL
- **Max Iterations**: 5 (diminishing returns)
- **Executor**: `quantum-compliance-tuning-agent`
- **Entangled with**: QI-05, QI-06 (depends on both results)

---

## Context Signals → Amplitude Boosts

The `QuantumPlansetEngine.generate()` method uses context signals to boost amplitudes:

```python
# Context signals from per-pattern report
context = {
    "failing_patterns": 2,  # H and F below 95%
    "k1": 0.3406,           # near limit
}

# Amplitude boost rules
if context["failing_patterns"] >= 2:
    QI-01 amplitude ×= 1.5
    QI-06 amplitude ×= 1.6  # Regression guard priority elevated
elif context["failing_patterns"] == 1:
    QI-01 amplitude ×= 1.3
    QI-06 amplitude ×= 1.4
    
if context["k1"] >= 0.33:
    QI-06 amplitude ×= 1.7  # Very tight k₁ → boost regression guard
    
# After boosting, recalculate amplitudes via Born Rule
amplitudes = engine._calculate_born_rule_probabilities()

# Collapse: select step with highest effective amplitude
step = max(amplitudes, key=lambda s: s.effective_amplitude())
```

**Example**: If 2 failing patterns AND k₁=0.3406:
- QI-01 effective amplitude = 0.95 × 1.5 = 1.425 (highest → executed first)
- QI-06 effective amplitude = 0.92 × 1.6 × 1.7 = 2.50 (very high priority)

---

## Integration Points in Codebase

### 1. **Cognitive Brain Agent API** (`src/codex/cognitive/agent_brain_api.py`)

```python
AGENT_IMPROVEMENT_AREAS = {
    "quantum-compliance-tuning-agent": [ImprovementArea.QI_TESTING],
}
```
- **Mapping**: Agent → Exclusive executor of improvement area
- **Use**: When `QuantumPlansetEngine` needs to route QI_TESTING, it looks up this mapping
- **Handoff Protocol**: Structured (7-step planset, entangled execution)

### 2. **QuantumPlansetEngine** (`src/codex/cognitive/quantum_planset_engine.py`)

```python
# In QI_TESTING improvement area definition
{
    "step_id": "QI-01",
    "agent": "quantum-compliance-tuning-agent",
    "action": "run raw scalability experiment",
    ...
},
{
    "step_id": "QI-02",
    "agent": "quantum-compliance-tuning-agent",
    "action": "generate per-pattern accuracy report",
    "entangled_with": ["QI-01"],
    ...
},
# ... QI-03 through QI-07 follow
```
- **Purpose**: Define 7-step workflow for tuning iteration
- **Entanglement**: Steps have dependencies (`entangled_with` field)
- **Use**: `engine.collapse(planset)` returns ordered execution path

### 3. **Compliance Integration Hook** (`src/cognitive_brain/integrations/compliance_integration.py`)

```python
# In QuantumComplianceAssessor._assess_with_superposition()
# After evaluate_parallel(state), before collapse(state):
if feature_flag("CODEX_BAYESIAN_MODE") or feature_flag("CODEX_FUZZY_MODE"):
    tuned_probs = assessor._apply_poc_tuning(
        probabilities, audit_result, decision_names
    )
    state.probabilities = tuned_probs
```
- **Purpose**: Apply tuning at decision-making time
- **Tuning Tools**:
  - `BayesianAssessor.apply_tuning_rules()` for Bayesian boost
  - `FuzzyEngine.apply_membership_tuning()` for boundary shifts
- **Feature Flags**: Only active if tuning mode enabled

### 4. **Test Coverage** (`tests/cognitive_brain/quantum/test_phase4_tuning.py`)

27 dedicated tests covering:
- Per-pattern accuracy monitoring
- Bayesian rule application
- Fuzzy boundary calibration
- Regression guard enforcement
- k₁ metric tracking
- Full 7-step iteration loops
- Reversion and retry logic

---

## How to Activate Phase 4.5 Tuning

### Step 1: Set Feature Flags

```bash
export CODEX_BAYESIAN_MODE=true
export CODEX_FUZZY_MODE=true
export PYTHONPATH=src
```

### Step 2: Generate Baseline

```bash
python src/cognitive_brain/experiments/exp1b_revalidation.py \
  --multi-seed --scenarios 200 --use-verified-labels \
  --save-json audit_artifacts/results/phase4_scalability_raw.json
```

### Step 3: Analyze Patterns

```bash
python tools/analysis/per_pattern_report.py \
  audit_artifacts/results/phase4_scalability_raw.json \
  --output audit_artifacts/poctune/iteration_1_per_pattern.json
```

### Step 4: Initialize Tuning Loop

```python
from src.codex.cognitive.quantum_planset_engine import QuantumPlansetEngine
from src.codex.cognitive.models import ImprovementArea

engine = QuantumPlansetEngine()
ps = engine.generate(
    ImprovementArea.QI_TESTING,
    context={
        "failing_patterns": 2,
        "k1": 0.3406,
    },
)

path = engine.collapse(ps)
for step in path:
    print(f"[{step.step_id}] {step.agent}: {step.action}")
    # Execute step (handled by quantum-compliance-tuning-agent)
```

### Step 5: Monitor Progress

- Watch `audit_artifacts/poctune/` directory for iteration results
- Monitor per-pattern accuracy improvements
- Ensure QI-06 regression guard never fails (k₁ ≤ 0.35, accuracy=100%)
- Stop after 5 iterations (diminishing returns)

---

## Key Metrics to Monitor

| Metric | Current | Target | Role |
|--------|---------|--------|------|
| **Single-seed Accuracy** (seed=42) | 100.0% | ≥100% | Regression guard |
| **Coherence** | 0.814 | ≥0.650 | Quantum health |
| **k₁** (overhead metric) | 0.3406 | ≤0.35 | Tuning cost |
| **Pattern H (5-seed)** | 74.5% | ≥95% | Tuning target |
| **Pattern F (5-seed)** | 87.9% | ≥95% | Tuning target |
| **Pattern E (5-seed)** | 92.7% | ≥95% | Tuning target |
| **Pattern C (5-seed)** | 93.3% | ≥95% | Tuning target |

---

## Safety Constraints

1. **Feature flags required**: Tuning is a no-op unless CODEX_BAYESIAN_MODE=true or CODEX_FUZZY_MODE=true
2. **No global state mutations**: Tuning functions are stateless
3. **Graceful degradation**: All tuning wrapped in try/except
4. **Regression guard**: Single-seed baseline (seed=42) must always be 100% accurate
5. **k₁ bounded**: Tuning overhead cannot exceed 0.35
6. **Human approval**: QI-07 accept/revert decision requires review of improvement vs overhead

---

## References

- **Quantum Planset Engine**: `src/codex/cognitive/quantum_planset_engine.py`
- **Compliance Integration**: `src/cognitive_brain/integrations/compliance_integration.py`
- **Bayesian Assessor**: `src/cognitive_brain/analytics/bayesian.py`
- **Fuzzy Engine**: `src/cognitive_brain/analytics/fuzzy.py`
- **Per-Pattern Report Tool**: `tools/analysis/per_pattern_report.py`
- **Phase 4.5 Tests**: `tests/cognitive_brain/quantum/test_phase4_tuning.py`
- **Status Document**: `.codex/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PHASE4_TUNING.md`
- **Research Basis**: Al Mamun 2023 (Bayesian 30% FP reduction), CHHIP 2021 (Fuzzy 12% FN reduction)

---

**Integration Status**:  CONFIRMED  
**Last Updated**: 2026-07-01  
**Authority**: P1.4 Task Force  
**Next Review**: Post-Phase 4.5 tuning completion
