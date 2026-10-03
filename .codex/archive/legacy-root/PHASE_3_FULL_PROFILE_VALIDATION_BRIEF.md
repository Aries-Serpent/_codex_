# Phase 3: Full Profile Validation Brief
**Campaign:** codex-ml v0.1.0 Installation Gap Resolution  
**Execution Date:** 2026-07-10T20:04:56Z  
**Authority:** @mbaetiong D-Tier Autonomous (GO CONTINUE)  
**Status:** 🟢 **EXECUTION AUTHORIZED**

---

## Executive Summary

Phase 3 validates the `[full]` profile installation, ensuring all development, testing, and ecosystem integration tools work correctly. This includes pytest, mypy, ruff, MLflow, wandb, and the full training/evaluation pipeline.

**Duration Target:** ~2 hours  
**Parallel Lanes:** 4-5 agents  
**Success Criteria:** All dev tools functional, full training pipeline works end-to-end, docs generation passes

---

## Phase 3 Objectives

### Primary Goals
1. ✅ Verify dev tools installation (pytest, mypy, ruff, black, isort)
2. ✅ Verify experiment tracking (MLflow, wandb integration)
3. ✅ Test end-to-end training pipeline with dev dependencies
4. ✅ Verify documentation generation tools
5. ✅ Validate all ecosystem integrations

### Success Criteria
```
[full] profile dependencies:
  ✅ pytest>=7.0 — testing framework functional
  ✅ mypy>=1.0 — type checking works
  ✅ ruff>=0.1 — linting works
  ✅ black>=23.0 — code formatting works
  ✅ isort>=5.12 — import sorting works
  ✅ mlflow>=2.0 — experiment tracking works
  ✅ wandb>=0.15 — weight & biases integration works
  ✅ sphinx>=6.0 — documentation generation works
  ✅ pytest-cov>=4.0 — coverage reporting works
  ✅ pytest-xdist>=3.0 — parallel test execution works

End-to-End Validation:
  ✅ Full training pipeline executes without errors
  ✅ Metrics logged to MLflow/wandb
  ✅ Documentation builds without warnings
  ✅ Code quality checks pass (ruff, mypy, black, isort)
  ✅ Test coverage meets threshold (90%+)
```

---

## Execution Model: 4-Lane Parallel Deployment

### Lane 1: Dev Tools Verification (Agent: `test-pattern-guardian`)
**Duration:** 30 min  
**Tasks:**
1. Install `[full]` profile
2. Verify pytest, mypy, ruff, black, isort functional
3. Run smoke tests on dev tools
4. Create validation report

**Success Criteria:**
- All dev tools import correctly
- pytest discovers tests
- mypy type checks complete
- ruff linting works
- black/isort formatting works

**Deliverables:**
- `.codex/PHASE_3_LANE_1_DEV_TOOLS_REPORT.md`
- `tests/smoke/test_dev_tools.py` (new tests)

---

### Lane 2: Experiment Tracking Integration (Agent: `integration-test-runner`)
**Duration:** 45 min  
**Tasks:**
1. Verify MLflow installation and API
2. Verify wandb installation and API
3. Test experiment logging (MLflow)
4. Test model tracking (wandb)
5. Verify metrics/artifacts storage

**Success Criteria:**
- MLflow server can be started
- wandb login flows work
- Experiment logging captures metrics
- Artifacts stored correctly
- Integration with training pipeline works

**Deliverables:**
- `.codex/PHASE_3_LANE_2_EXPERIMENT_TRACKING_REPORT.md`
- `tests/smoke/test_mlflow_integration.py`
- `tests/smoke/test_wandb_integration.py`

---

### Lane 3: End-to-End Training Pipeline (Agent: `ml-validation-suite-agent`)
**Duration:** 60 min  
**Tasks:**
1. Run full training pipeline with dev dependencies
2. Verify model checkpoint saving
3. Test evaluation pipeline
4. Verify predictions work end-to-end
5. Test inference on trained model

**Success Criteria:**
- Training completes without errors
- Model checkpoints saved correctly
- Evaluation metrics computed
- Predictions work on new data
- No regressions vs baseline

**Deliverables:**
- `.codex/PHASE_3_LANE_3_TRAINING_PIPELINE_REPORT.md`
- `tests/integration/test_full_pipeline.py`
- Trained model checkpoint + metrics

---

### Lane 4: Documentation & Code Quality (Agent: `documentation-quality-agent`)
**Duration:** 40 min  
**Tasks:**
1. Generate Sphinx documentation
2. Verify all docstrings present
3. Check code quality (ruff full scan)
4. Verify type hints (mypy strict)
5. Format code (black, isort)

**Success Criteria:**
- Sphinx builds without warnings
- All public APIs documented
- Ruff score 95+/100
- mypy passes in strict mode
- Code formatted consistently

**Deliverables:**
- `.codex/PHASE_3_LANE_4_DOCS_QUALITY_REPORT.md`
- Built documentation in `docs/_build/`
- Code quality metrics

---

## Lane Interdependencies

```
Lane 1: Dev Tools Verification ━━┓
                                 ├━━→ Integration Phase (20 min)
Lane 2: Experiment Tracking ━━━━━┫
                                 ├━━→ Success Verification (10 min)
Lane 3: End-to-End Pipeline ━━━━━┫
                                 ├━━→ Results Consolidation (5 min)
Lane 4: Documentation ━━━━━━━━━━━┛

Timeline:
  00:00-30:00 — Lanes 1-4 run in parallel
  30:00-45:00 — Wait for Lane 2 completion (experiment tracking slowest)
  45:00-60:00 — Lane 3 completes (training pipeline longest)
  60:00-65:00 — Integration phase (cross-validate all lanes)
  65:00-75:00 — Results consolidation + reporting
  75:00-120:00 — Final sign-off + documentation
```

---

## Prerequisite: Phase 1 & 2 Completion Status

**BLOCKING REQUIREMENT:** Phase 3 can only start after Phase 2 completion.

**Current Status Check:**
```
Phase 1 (Core Profile): ⏳ QUEUED → AWAITING EXECUTION
Phase 2 (Runtime Profile): ⏳ PENDING → AFTER Phase 1
Phase 3 (Full Profile): 🟢 READY → AFTER Phase 2
```

**Timeline:**
- Phase 1 execution: ~2.5 hours (3 waves)
- Phase 2 execution: ~2 hours (GPU validation)
- Phase 3 execution: ~2 hours (dev tools + training + docs)

---

## Phase 3 Detailed Execution Plan

### Pre-Execution Checks (5 min)

```bash
# Verify environment
python --version  # Should be 3.12+
pip --version     # Should be setuptools 83.0+
which pytest mypy ruff black isort  # All must be in PATH
```

### Wave 1: Dev Tools Baseline (30 min)

**Lane 1: Dev Tools Verification**
```bash
# Install full profile
pip install -e ".[full]"

# Test pytest
pytest tests/ -v --collect-only

# Test mypy
mypy src/codex_ml --strict

# Test ruff
ruff check src/ tests/

# Test black
black --check src/ tests/

# Test isort
isort --check-only src/ tests/
```

**Expected Output:**
- All tools import successfully
- pytest finds 1500+ tests
- mypy completes without errors
- ruff linting score 95+/100
- black formatting consistent
- isort import ordering correct

---

### Wave 2: Experiment Tracking (45 min)

**Lane 2: MLflow Integration**
```python
import mlflow

# Test MLflow API
mlflow.set_experiment("Phase3Test")
with mlflow.start_run():
    mlflow.log_param("test_param", 42)
    mlflow.log_metric("test_metric", 0.95)
    mlflow.log_artifact("test_artifact.txt")
    
# Verify run created
client = mlflow.tracking.MlflowClient()
runs = client.search_runs("0")
assert len(runs) > 0, "MLflow run not created"
```

**Lane 2: wandb Integration**
```python
import wandb

# Test wandb API
run = wandb.init(project="codex-ml", job_type="phase3-test")
wandb.log({"test_param": 42, "test_metric": 0.95})
wandb.log_artifact("test_artifact.txt")
run.finish()

# Verify project exists
assert run.project == "codex-ml"
assert len(run.history()) > 0, "wandb logging failed"
```

---

### Wave 3: End-to-End Training (60 min)

**Lane 3: Full Training Pipeline**
```bash
# Run training script with full dependencies
python scripts/train.py \
  --config configs/full_profile_test.yaml \
  --epochs 5 \
  --log_to mlflow \
  --log_to wandb

# Expected output:
#   Training completed successfully
#   Model checkpoint saved
#   Metrics logged to MLflow + wandb
#   Evaluation completed

# Run inference on trained model
python scripts/evaluate.py \
  --model_path checkpoints/phase3_test.pt \
  --data_dir data/test

# Expected output:
#   Inference completed
#   All metrics computed
#   Results match expected ranges
```

---

### Wave 4: Documentation & Quality (40 min)

**Lane 4: Documentation Generation**
```bash
# Build Sphinx documentation
cd docs
sphinx-build -b html . _build/html

# Expected: docs/_build/html/index.html exists
# Expected: 0 warnings
# Expected: All APIs documented

# Run code quality checks
ruff check src/ tests/
mypy src/ --strict
black --check src/ tests/
isort --check-only src/ tests/

# Expected output:
#   All checks pass
#   No warnings
#   Code quality score 95+/100
```

---

## Success Verification Matrix

| Component | Test | Expected | Actual | Status |
|-----------|------|----------|--------|--------|
| pytest | `pytest tests/` | 1500+ tests | TBD | ⏳ |
| mypy | `mypy src/` --strict | 0 errors | TBD | ⏳ |
| ruff | `ruff check src/` | 95+/100 | TBD | ⏳ |
| black | `black --check src/` | 0 diffs | TBD | ⏳ |
| isort | `isort --check-only` | 0 diffs | TBD | ⏳ |
| MLflow | Training run logged | ✅ metrics | TBD | ⏳ |
| wandb | Training run logged | ✅ artifacts | TBD | ⏳ |
| Sphinx | Doc generation | ✅ 0 warnings | TBD | ⏳ |
| Training | Full pipeline | ✅ model saved | TBD | ⏳ |
| Inference | Prediction test | ✅ outputs valid | TBD | ⏳ |

---

## Failure Escalation Protocol

### If Dev Tools Fail (Lane 1)
1. Check environment: `python -m site`
2. Reinstall: `pip install --force-reinstall [full]`
3. Verify PATH: `which pytest mypy ruff`
4. Escalate to `code-analysis-agent` if sys issues

### If MLflow/wandb Fails (Lane 2)
1. Check network: `curl https://mlflow.io`
2. Verify credentials: `mlflow verify`
3. Check wandb API: `wandb verify`
4. Escalate to `security-audit-agent` if auth issues

### If Training Fails (Lane 3)
1. Check GPU availability: `nvidia-smi`
2. Run with CPU fallback: `CUDA_VISIBLE_DEVICES="" python train.py`
3. Check data availability: `ls -la data/`
4. Escalate to `ml-validation-suite-agent`

### If Docs Fail (Lane 4)
1. Check Sphinx: `sphinx-quickstart --version`
2. Rebuild: `rm -rf docs/_build && sphinx-build -b html docs docs/_build`
3. Check for missing docstrings: `sphinx-apidoc src/`
4. Escalate to `documentation-quality-agent`

---

## Agent Delegation & Parallel Execution

**GO CONTINUE Directive:** Proceed with all lanes simultaneously

### Lane 1: Dev Tools
```
Agent: test-pattern-guardian
Task ID: PHASE3-LANE1-DEV-TOOLS
Authority: D-Tier (GO CONTINUE)
Timeout: 30 min
Retry: 2x on failure
```

### Lane 2: Experiment Tracking
```
Agent: integration-test-runner
Task ID: PHASE3-LANE2-EXP-TRACKING
Authority: D-Tier (GO CONTINUE)
Timeout: 45 min
Retry: 2x on failure
```

### Lane 3: End-to-End Training
```
Agent: ml-validation-suite-agent
Task ID: PHASE3-LANE3-TRAINING
Authority: D-Tier (GO CONTINUE)
Timeout: 60 min
Retry: 1x on failure (resource intensive)
```

### Lane 4: Documentation
```
Agent: documentation-quality-agent
Task ID: PHASE3-LANE4-DOCS
Authority: D-Tier (GO CONTINUE)
Timeout: 40 min
Retry: 2x on failure
```

---

## Deliverables

### Reports (Required)
- ✅ `.codex/PHASE_3_LANE_1_DEV_TOOLS_REPORT.md` (Lane 1)
- ✅ `.codex/PHASE_3_LANE_2_EXPERIMENT_TRACKING_REPORT.md` (Lane 2)
- ✅ `.codex/PHASE_3_LANE_3_TRAINING_PIPELINE_REPORT.md` (Lane 3)
- ✅ `.codex/PHASE_3_LANE_4_DOCS_QUALITY_REPORT.md` (Lane 4)
- ✅ `.codex/PHASE_3_CONSOLIDATION_REPORT.md` (Final)

### Code Changes (Required)
- ✅ `tests/smoke/test_dev_tools.py` (Lane 1)
- ✅ `tests/smoke/test_mlflow_integration.py` (Lane 2)
- ✅ `tests/smoke/test_wandb_integration.py` (Lane 2)
- ✅ `tests/integration/test_full_pipeline.py` (Lane 3)

### Documentation (Required)
- ✅ `docs/QUICKSTART_FULL_PROFILE.md` (Lane 4)
- ✅ `docs/ECOSYSTEM_docs/api/reference/INTEGRATION.md` (Lane 4)
- ✅ Built Sphinx documentation (Lane 4)

---

## Accountability & Compliance

**REQ-4 (Accountability):** Update `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` with Phase 3 entry  
**REQ-5 (Changelog):** Update `CHANGELOG.md` with Phase 3 completion + all lane results  
**WEC Checklist:** Update PR WEC with Phase 3 completion status

---

## Success Criteria Summary

```
✅ Phase 3 Complete when:
  • All 4 lanes report successful completion
  • 0 critical issues remaining
  • All dev tools functional
  • Full training pipeline works
  • Documentation builds without warnings
  • Code quality meets standards (95+/100)
  • All ecosystem integrations verified

📊 Final Metrics:
  • Dev tools coverage: 100% (5/5)
  • Experiment tracking: 100% (2/2)
  • Training pipeline: ✅ working
  • Code quality: 95+/100
  • Documentation: 0 warnings
  • Test coverage: 90%+
```

---

## Timeline Estimate

```
Total Phase 3 Duration: ~2 hours (120 min)

  00:00-05:00   Pre-execution checks (5 min)
  05:00-35:00   Wave 1: Dev Tools (30 min, Lane 1)
  05:00-50:00   Wave 2: Experiment Tracking (45 min, Lane 2) [parallel]
  05:00-65:00   Wave 3: Training Pipeline (60 min, Lane 3) [parallel]
  05:00-45:00   Wave 4: Documentation (40 min, Lane 4) [parallel]
  65:00-80:00   Integration Phase (15 min)
  80:00-90:00   Results Consolidation (10 min)
  90:00-120:00  Final Documentation + Sign-off (30 min)
```

---

## Next Steps

1. ✅ Verify Phase 1 & 2 completion
2. ✅ Dispatch 4 agents in parallel (lanes 1-4)
3. ✅ Monitor progress in real-time
4. ✅ Escalate any blocking issues
5. ✅ Consolidate results
6. ✅ Create PR with all deliverables
7. ✅ Update REQ-4/REQ-5 compliance docs
8. ✅ Complete phase sign-off

---

**AUTHORIZATION:** @mbaetiong D-Tier Autonomous (GO CONTINUE)  
**CREATED:** 2026-07-10T20:04:56Z  
**STATUS:** 🟢 READY FOR EXECUTION
