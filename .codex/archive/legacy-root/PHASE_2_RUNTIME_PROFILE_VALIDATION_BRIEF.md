# Phase 2: Runtime Profile Validation & Integration Testing

**Campaign ID:** codex-ml v0.1.0 Installation Fix Campaign  
**Phase:** 2 of 3 (Runtime Profile Validation)  
**Status:** Ready for Autonomous Dispatch  
**Authorization:** D-tier (GO CONTINUE) per @mbaetiong 2026-07-10  
**Estimated Duration:** 90-120 minutes (3 parallel lanes)  
**Target Completion:** 2026-07-10T21:30-22:00Z

---

## 🎯 Objectives

**Primary Goal:**
Validate that the runtime profile (20-35 MB) correctly installs, imports, and executes all ML inference dependencies without errors.

**Success Criteria:**
1. ✅ Runtime profile installs cleanly (pip install -e ".[runtime]")
2. ✅ All ML inference dependencies import correctly (torch, transformers)
3. ✅ MLflow/wandb experiment tracking integrates
4. ✅ Inference pipeline executes without errors
5. ✅ Profile-specific smoke tests pass (10+ tests)
6. ✅ No missing or conflicting dependencies detected

---

## 📋 Phase 2 Architecture

### Prerequisites (From Phase 1)
- ✅ codex.logging module functional
- ✅ Entry points corrected (19 bundled retained)
- ✅ hydra-plugins extra removed
- ✅ setuptools configuration clarified
- ✅ Smoke tests for core profile pass
- ✅ Installation guide created

### Blockers Cleared
- ✅ Core profile installs cleanly
- ✅ Base CLI entry points functional
- ✅ No import path conflicts

### Phase 2 Scope
**Validation Chains:**
1. **Lane 2.1:** Dependency validation (torch, transformers, scikit-learn)
2. **Lane 2.2:** MLflow/wandb integration testing
3. **Lane 2.3:** Runtime inference pipeline validation

---

## 🚀 3-Lane Parallel Model

### Lane 2.1: ML Dependencies Validation
**Owner:** ci-testing-agent or autonomous-test-healer-agent  
**Objective:** Validate torch, transformers, and scikit-learn installation and functionality  
**Scope:**
- Runtime profile installation verification
- torch import and version validation
- transformers model loading (small test model)
- scikit-learn pipeline functionality
- GPU availability detection (CUDA 11.8+)
- Memory requirements verification (min 4GB RAM)

**Deliverables:**
- Dependency resolution test suite (8-10 tests)
- YAML report: dependency versions, import success, GPU info
- Recommendations for GPU acceleration (if available)

**Success Criteria:**
- All dependencies import cleanly
- transformers can load at least one model (e.g., distilbert-base-uncased)
- torch CUDA detection works correctly
- Memory constraints documented

**Time Estimate:** 30-45 minutes

---

### Lane 2.2: Experiment Tracking Integration
**Owner:** unified-security-scanner or code-analysis-agent  
**Objective:** Validate MLflow and wandb integration with runtime profile  
**Scope:**
- MLflow server startup and configuration
- Experiment creation and run logging
- wandb API key integration (skip if not configured)
- Artifact storage and retrieval
- Metrics/parameters logging functionality
- Integration with inference pipeline

**Deliverables:**
- Integration test suite (6-8 tests)
- MLflow/wandb configuration validation
- Example logged experiment report
- Recommendations for production setup

**Success Criteria:**
- MLflow experiments create successfully
- Metrics/parameters log without errors
- Artifacts upload and retrieve correctly
- wandb integration graceful (works if configured, skips if not)

**Time Estimate:** 30-45 minutes

---

### Lane 2.3: Inference Pipeline Validation
**Owner:** test-enhancement-agent or ml-validation-suite-agent  
**Objective:** Validate end-to-end inference pipeline with runtime profile  
**Scope:**
- Load pre-trained ML model (small test model)
- Run inference on synthetic test data
- Validate output tensor shapes and types
- Performance profiling (latency, throughput)
- Error handling and graceful degradation
- Memory efficiency validation

**Deliverables:**
- Inference pipeline test suite (10-12 tests)
- Performance benchmarks (latency, memory, throughput)
- Error handling validation report
- Recommendations for optimization

**Success Criteria:**
- Model loads and initializes successfully
- Inference executes without errors on test data
- Output tensors have correct shapes/types
- Performance meets baseline expectations
- Memory usage within bounds

**Time Estimate:** 45-60 minutes

---

## 📊 Execution Plan

### Timeline
```
T+0:00   → Phase 2 dispatch (all 3 lanes simultaneously)
T+10:00  → Mid-point checkpoint (brief status update)
T+45:00  → Lane 2.1 expected completion
T+60:00  → Lane 2.2 expected completion
T+75:00  → Lane 2.3 expected completion
T+90:00  → Phase 2 consolidation & Phase 3 readiness verification
```

### Dispatch Sequence
1. **Dispatch Lane 2.1** (ML Dependencies Validation)
   - Agent: ci-testing-agent
   - Focus: torch, transformers, scikit-learn
   
2. **Dispatch Lane 2.2** (Experiment Tracking Integration)
   - Agent: unified-security-scanner or code-analysis-agent
   - Focus: MLflow, wandb configuration
   
3. **Dispatch Lane 2.3** (Inference Pipeline Validation)
   - Agent: ml-validation-suite-agent or test-enhancement-agent
   - Focus: End-to-end inference pipeline

### Interdependencies
- Lane 2.1 must complete before Lane 2.3 can validate pipeline
- Lane 2.2 is independent (can run in parallel)
- All lanes must complete before Phase 3 dispatch

---

## 🔧 Success Metrics

### Lane 2.1 Success Criteria
- ✅ Runtime profile pip install succeeds
- ✅ torch imports without errors
- ✅ transformers imports without errors
- ✅ scikit-learn imports without errors
- ✅ All 8-10 dependency tests pass
- ✅ GPU detection works (CUDA info available if installed)

### Lane 2.2 Success Criteria
- ✅ MLflow experiments create successfully
- ✅ Run logging works without errors
- ✅ Metrics/parameters record correctly
- ✅ Artifacts upload/retrieve successfully
- ✅ All 6-8 integration tests pass
- ✅ wandb integration graceful (configured or skip)

### Lane 2.3 Success Criteria
- ✅ Model loads successfully from transformers
- ✅ Inference runs on synthetic test data
- ✅ Output shapes/types correct
- ✅ Performance within acceptable range
- ✅ All 10-12 pipeline tests pass
- ✅ Error handling validated

### Phase 2 Completion Criteria
- ✅ All 3 lanes report success (0 critical failures)
- ✅ Consolidated Phase 2 report created
- ✅ Phase 3 readiness gates all green
- ✅ No regressions vs Phase 1 deliverables

---

## 📈 Reporting & Checkpoints

### Checkpoint 1 (T+10 min): Mid-point Status
- Lanes dispatched and running
- No immediate blockers detected
- Estimated time to completion

### Checkpoint 2 (Per-Lane Completion)
- Individual lane completion reports
- Test pass rates and coverage
- Issues encountered and resolutions

### Final Report (Phase 2 Consolidation)
**File:** `.codex/PHASE_2_CONSOLIDATION_REPORT.md`

**Contents:**
- Executive summary (pass/fail for each lane)
- Test results consolidation (total tests, pass rate)
- Dependency version matrix
- Performance benchmarks
- Phase 3 readiness assessment
- Recommendations for Phase 3

---

## 🚀 Next Phase: Phase 3 (Full Profile Validation)

**Phase 3 Prerequisite:** All Phase 2 lanes must report success  
**Phase 3 Scope:** 4-lane parallel execution
  - Lane 3.1: Dev tools (pytest, mypy, ruff, black, isort)
  - Lane 3.2: Experiment tracking (MLflow, wandb full suite)
  - Lane 3.3: Training pipeline (full end-to-end training)
  - Lane 3.4: Documentation & code quality (full profile validation)

**Phase 3 Authorization:** Approved by @mbaetiong (D-tier GO CONTINUE)  
**Phase 3 Target:** Upon Phase 2 completion + ~120 min execution time

---

## 🎯 Campaign Status

| Phase | Status | Completion | Next Milestone |
|-------|--------|------------|---|
| Phase 1 | ✅ COMPLETE | 100% | Phase 2 dispatch |
| Phase 2 | 🚀 READY | 0% | Autonomous dispatch NOW |
| Phase 3 | ⏳ BLOCKED | 0% | After Phase 2 completion |

---

## ⚠️ Risk Mitigation

### Identified Risks
1. **GPU Not Available:** Falls back to CPU inference (slower but functional)
2. **Large Model Downloads:** Tests use small models (distilbert, etc.)
3. **MLflow/wandb Configuration:** Tests skip gracefully if not configured
4. **Memory Constraints:** Tests monitor and report memory usage
5. **Dependency Conflicts:** Phase 1 already resolved conflicts

### Mitigation Strategies
- ✅ CPU fallback for GPU-dependent tests
- ✅ Small models for CI environments
- ✅ Graceful skipping for optional services
- ✅ Memory monitoring and bounds checking
- ✅ Phase 1 compatibility validation

---

## 📝 Agent Assignments

### Recommended Agent Dispatch

**Lane 2.1 (ML Dependencies):**
```
Agent: ci-testing-agent
Task: "Create and execute comprehensive ML dependency validation test suite 
       for runtime profile. Validate torch, transformers, scikit-learn imports,
       versions, and GPU availability. Report YAML with dependency matrix."
```

**Lane 2.2 (Experiment Tracking):**
```
Agent: code-analysis-agent or unified-security-scanner
Task: "Create and execute MLflow/wandb integration tests for runtime profile.
       Test experiment creation, run logging, metrics/parameters, artifacts.
       Validate graceful handling of optional dependencies."
```

**Lane 2.3 (Inference Pipeline):**
```
Agent: ml-validation-suite-agent or test-enhancement-agent
Task: "Create and execute end-to-end inference pipeline tests using runtime
       profile. Load transformers model, run inference on synthetic data,
       profile performance (latency, memory, throughput)."
```

---

## ✅ Execution Readiness Checklist

- ✅ Phase 1 complete (all 6 gaps resolved)
- ✅ Phase 2 objectives clearly defined
- ✅ 3 lanes identified with clear scope
- ✅ Success criteria established per lane
- ✅ Agent assignments recommended
- ✅ Risk mitigation strategies defined
- ✅ Checkpoint reporting plan established
- ✅ D-tier authorization active (GO CONTINUE)
- ✅ Consolidation reporting template prepared

**STATUS: READY FOR AUTONOMOUS DISPATCH** 🚀

---

## 📞 Escalation & Support

- **Critical Blocker:** Pause dispatch, create GitHub issue with [PHASE-2-BLOCKER] tag
- **Performance Concern:** Log to `.codex/PHASE_2_LANE_X_CHECKPOINT_*.md`, continue execution
- **Dependency Conflict:** Run dependency conflict resolution, document decision
- **Out of Memory:** Recommend reduce test scale, continue with remaining tests

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-10T20:05Z  
**Campaign Status:** Ready for Dispatch  
**Prepared by:** Copilot Task Agent (Phase 1 Complete → Phase 2 Dispatch)
