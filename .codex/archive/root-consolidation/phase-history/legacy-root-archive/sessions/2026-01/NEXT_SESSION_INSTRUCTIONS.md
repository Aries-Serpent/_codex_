# Next Session Instructions - Phase 2 Implementation

**Session Context:** Continuation of quantum-inspired integration systems  
**Current Status:** Phase 1 (Workflow Health Automation) ✅ COMPLETE  
**Next Task:** Phase 2 (ML Pattern Feeding to Cognitive Brain)

---

## 🎯 Phase 2 Objectives

Implement ML pattern extraction from workflow monitoring data with quantum-inspired pattern recognition for feeding the cognitive brain system.

**Core Principle:** Patterns exhibit wave-like interference (constructive/destructive) creating emergent insights, similar to quantum computation.

---

## 📋 Implementation Checklist

### Step 1: Create Directory Structure
```bash
mkdir -p scripts/cognitive
mkdir -p tests/cognitive
mkdir -p .codex/cognitive_brain
```

### Step 2: Implement Core Classes (scripts/cognitive/extract_workflow_patterns.py)

**Classes to Implement:**
1. **PatternWave** - Wave interference logic
   - `interfere(other)` - Calculate constructive/destructive interference
   - Properties: pattern_type, amplitude, frequency, phase

2. **QuantumPatternClassifier** - 4-qubit neural network
   - `encode_pattern(pattern)` - Encode to quantum state
   - `classify(encoded_state)` - Measure and classify
   - `_initialize_state()` - Uniform superposition
   - `_apply_rotation(state, qubit, angle)` - Rotation gates

3. **WorkflowPatternExtractor** - Pattern detection
   - `extract_patterns(days_back)` - Extract from history
   - `_analyze_workflow(name, runs)` - Single workflow analysis
   - `_calculate_flakiness(runs)` - Alternation detection
   - `_apply_pattern_interference(patterns)` - Correlation via interference

4. **CognitiveBrainFeeder** - Persistence layer
   - `feed_patterns(patterns)` - Store patterns
   - `_load_existing_patterns()` - Load from JSONL
   - `_save_patterns(patterns)` - Save to JSONL
   - Pattern database: `.codex/cognitive_brain/workflow_patterns.jsonl`

### Step 3: Create Workflow (.github/workflows/cognitive-brain-feed.yml)

**Triggers:**
- `schedule: '0 2 * * *'` - Daily at 2 AM UTC
- `workflow_run: completed` - After health checks
- `workflow_dispatch` - Manual with days_back parameter

**Steps:**
- Setup Python 3.12
- Install: requests, numpy, scipy
- Run: `python scripts/cognitive/extract_workflow_patterns.py --days-back 30`
- Commit: `.codex/cognitive_brain/` updates
- Upload: artifacts

### Step 4: Create Test Suite (tests/cognitive/test_pattern_extraction.py)

**Test Classes:**
1. **TestPatternWave**
   - `test_constructive_interference()` - In phase → amplitudes add
   - `test_destructive_interference()` - Out of phase → amplitudes cancel

2. **TestPatternExtractor**
   - `test_flakiness_calculation()` - Alternation detection
   - `test_pattern_grouping()` - Workflow grouping

3. **TestCognitiveBrainFeeder**
   - `test_pattern_persistence()` - Save/load patterns
   - `test_pattern_update()` - Update existing patterns

4. **TestQuantumPatternClassifier**
   - `test_pattern_encoding()` - Quantum state encoding
   - `test_pattern_classification()` - Classification accuracy

### Step 5: Validation

```bash
# Run tests
python -m pytest tests/cognitive/test_pattern_extraction.py -v

# Test script manually
export GITHUB_TOKEN=<token>
python scripts/cognitive/extract_workflow_patterns.py --days-back 7

# Check outputs
ls -la .codex/cognitive_brain/
cat .codex/cognitive_brain/workflow_patterns.jsonl
cat .codex/cognitive_brain/metadata.json
```

---

## 📖 Reference Materials

### Complete Specification
**File:** `.codex/plans/ML_PATTERN_FEEDING_PLANSET.md` (30KB)

**Key Sections:**
- Lines 1-100: Executive summary & quantum principles
- Lines 100-400: Complete Python implementation
- Lines 400-600: Test cases
- Lines 600-700: Integration & validation

### Pattern Types to Detect
1. **high_failure_rate** - Failure rate > 20%
2. **test_flakiness** - Alternating success/failure
3. **duration_variance** - High duration variability
4. **cascading_failure** - Related workflow failures
5. **resource_exhaustion** - Timeout patterns
6. **network_issue** - Connectivity problems

### Quantum Interference Formula
```python
phase_diff = abs(self.phase - other.phase)

if phase_diff < π/4:
    # Constructive interference
    return self.amplitude + other.amplitude
elif phase_diff > 3π/4:
    # Destructive interference
    return abs(self.amplitude - other.amplitude)
else:
    # Partial interference
    return sqrt(self.amplitude² + other.amplitude²)
```

---

## 🎯 Success Criteria

### Implementation Quality
- [ ] All 4 core classes implemented
- [ ] Workflow automation created
- [ ] Test suite with >85% coverage
- [ ] All tests passing

### Quantum Principles
- [ ] Wave interference (constructive/destructive)
- [ ] Quantum neural network (4-qubit)
- [ ] Phase encoding
- [ ] Pattern correlation

### Integration
- [ ] GitHub API integration
- [ ] Cognitive brain persistence
- [ ] per-iteration automation
- [ ] Artifact generation

---

## ⚡ Quick Start Commands

```bash
# Navigate to repo
cd /home/runner/work/_codex_/_codex_

# Create directories
mkdir -p scripts/cognitive tests/cognitive .codex/cognitive_brain

# Start with PatternWave class
# Reference: .codex/plans/ML_PATTERN_FEEDING_PLANSET.md lines 23-49

# Then QuantumPatternClassifier
# Reference: .codex/plans/ML_PATTERN_FEEDING_PLANSET.md lines 51-107

# Continue with WorkflowPatternExtractor
# Reference: .codex/plans/ML_PATTERN_FEEDING_PLANSET.md lines 160-400

# Finally CognitiveBrainFeeder
# Reference: .codex/plans/ML_PATTERN_FEEDING_PLANSET.md lines 450-550
```

---

## 📊 Estimated Timeline

**Total Implementation:** 6-7 iterations (planset estimate)  
**Compressed:** 1-2 sessions (with focused implementation)

**Breakdown:**
- Core classes: 60-90 minutes
- Workflow automation: 15 minutes
- Test suite: 30-45 minutes
- Validation: 15 minutes
- **Total:** 2-2.5 hours

---

## 🔗 Related Files

**From Phase 1 (reference):**
- `scripts/quantum_workflow_health.py` - Similar structure
- `tests/test_quantum_workflow_health.py` - Test patterns
- `.github/workflows/workflow-health-check.yml` - Workflow template

**Plansets:**
- `.codex/plans/WORKFLOW_HEALTH_AUTOMATION_PLANSET.md` (Phase 1)
- `.codex/plans/ML_PATTERN_FEEDING_PLANSET.md` (Phase 2) ← **USE THIS**
- `.codex/plans/AGENT_CHAINING_INTEGRATION_PLANSET.md` (Phase 3)

---

## 💡 Implementation Tips

1. **Copy Phase 1 structure** - Similar patterns work well
2. **Use dataclasses** - Clean data structures
3. **Type hints** - Better IDE support
4. **Comprehensive docstrings** - Explain quantum concepts
5. **Error handling** - GitHub API can fail
6. **Progress logging** - User feedback important
7. **Atomic operations** - Don't corrupt cognitive brain

---

## 🚀 After Phase 2

Once Phase 2 is complete:
1. Commit all changes
2. Run tests
3. Update IMPLEMENTATION_PROGRESS_PHASE2.md
4. Store memory checkpoints
5. Begin Phase 3 (Agent Chaining Integration)

**Phase 3 Reference:** `.codex/plans/AGENT_CHAINING_INTEGRATION_PLANSET.md`

---

**Status:** Ready to begin Phase 2  
**Expected Duration:** 2-2.5 hours  
**Reference:** `.codex/plans/ML_PATTERN_FEEDING_PLANSET.md`
