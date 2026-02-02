# Next Phase Tasks - Test Validation & Investigation

**Date**: 2026-02-01  
**Status**: Ready for Execution  
**Priority**: P1 - Immediate

---

## 🔴 Priority 1: Immediate Tasks

### Task 1.1: Validate Remaining Test Failures in CI

**Objective**: Identify which of the 2-3 remaining test failures still exist after fixes

**Commands**:
```bash
# Check latest CI run
gh run list --branch copilot/sub-pr-3095 --limit 5

# Get specific test job logs
gh run view <run-id> --log

# Download test artifacts
gh run download <run-id>
```

**Expected Outcomes**:
- [ ] Identify exact tests still failing
- [ ] Confirm 7-8 tests now passing
- [ ] Document new failure patterns if any

---

### Task 1.2: Investigate Mock Serialization (test_run_functional_training_resume)

**File**: `tests/space_traversal/test_peft_comprehensive/test_run_functional_training_resume.py`

**Issue**: TypeError: Object of type MagicMock is not JSON serializable

**Investigation Steps**:
```bash
# Run the specific test
pytest tests/space_traversal/test_peft_comprehensive/test_run_functional_training_resume.py::test_run_functional_training_resume -xvs

# Check for mock usage
grep -r "MagicMock" tests/space_traversal/test_peft_comprehensive/test_run_functional_training_resume.py
```

**Potential Fix**:
```python
# Instead of bare MagicMock, use serializable return values
mock_checkpoint = Mock()
mock_checkpoint.to_dict = Mock(return_value={
    'epoch': 1,
    'step': 100,
    'metrics': {'loss': 0.5}
})
```

**Files to Check**:
- `tests/space_traversal/test_peft_comprehensive/test_run_functional_training_resume.py`
- `src/codex_ml/utils/checkpointing.py` (checkpoint serialization)
- `tests/test_training_resume.py` (related tests)

---

### Task 1.3: Verify Tensor Comparison Fix (test_deterministic_mode_reproducibility)

**File**: `tests/space_traversal/test_peft_comprehensive/test_determinism_utilities.py`

**Issue**: 
1. Results not reproducible even in deterministic mode
2. TypeError: '>' not supported between Tensor and float

**Validation**:
```bash
# Run the test
pytest tests/space_traversal/test_peft_comprehensive/test_determinism_utilities.py::TestDeterministicModeIntegration::test_deterministic_mode_reproducibility -xvs
```

**What Was Fixed**:
- ✅ Added `set_seed()` function for comprehensive seeding
- ✅ Updated `set_deterministic_mode()` to accept seed parameter

**What May Still Need Work**:
- Tensor comparison bug (use `.item()` before comparing to float)
- Environment-specific non-determinism (GPU vs CPU)

**Potential Additional Fix**:
```python
# In any code comparing tensors to floats
# Wrong:
if my_tensor > 0.5:

# Correct:
if my_tensor.item() > 0.5:
```

---

## 🟡 Priority 2: Validation Tasks

### Task 2.1: Run Full Test Suite

**Command**:
```bash
# Install test dependencies first
pip install -e ".[test]"

# Run full suite
pytest tests/ -v --tb=short

# With coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

**Expected**:
- [ ] 152-153 tests passing (up from 145)
- [ ] 2-3 tests failing (down from 10)
- [ ] Coverage ≥ 72% (baseline)

---

### Task 2.2: Validate Docker Multi-Stage Builds

**Commands**:
```bash
# Test all targets
docker build --target cpu-runtime -t codex:cpu .
docker build --target gpu-runtime -t codex:gpu .
docker build --target test -t codex:test .

# Verify images exist
docker images | grep codex

# Test image functionality
docker run --rm codex:cpu --version
docker run --rm codex:test python -c "import codex_ml; print('OK')"
```

**Expected**:
- [ ] All three stages build successfully
- [ ] No Python version errors
- [ ] Images are functional
- [ ] Size is reasonable

---

### Task 2.3: Confirm Coverage Baseline

**Command**:
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Compare to baseline
git show origin/0D_base_:.codex/coverage_baseline.txt
```

**Expected**:
- [ ] Coverage ≥ 72%
- [ ] No significant drops in critical modules
- [ ] New code has adequate coverage

---

## 🟢 Priority 3: Enhancement Tasks

### Task 3.1: Additional Pattern Categories

**File**: `src/cognitive_brain/learning/outcome_analyzer.py`

**Current Patterns**:
- Temporal (time-of-day)
- Contextual (complexity)
- Sequential (agent coordination)
- Causal (resources)
- Efficiency (metrics)

**Potential Additions**:
- Error patterns (recurring failure modes)
- Performance patterns (latency, throughput)
- Collaboration patterns (team dynamics)
- Learning rate patterns (improvement velocity)

**Implementation**:
```python
# Add to _identify_patterns()
# Error pattern: Recurring failure in same context
if context.retry_count > 2:
    identified_patterns.append("error_pattern_retry_exceeded")

# Performance pattern: Consistent high performance
if result_metrics.get("latency", 999) < 100:
    identified_patterns.append("performance_low_latency")
```

---

### Task 3.2: Docker Base Image Evaluation

**Current**: Python 3.12-slim

**Considerations**:
- **Python 3.13**: Newer, but may have compatibility issues
- **Alpine**: Smaller, but musl libc can cause issues
- **3.12-slim**: Good balance (current choice)

**Recommendation**: Stay with 3.12-slim for stability

---

### Task 3.3: Additional Test Cases

**Areas for Enhancement**:

1. **Edge Cases in Pattern Detection**:
   - Empty context
   - Extreme values (complexity = 0 or 1)
   - Missing metrics

2. **Docker Build Edge Cases**:
   - Build with minimal dependencies
   - Build on different architectures (ARM64)
   - Build cache validation

3. **Determinism Edge Cases**:
   - Multiple sequential runs
   - Cross-platform reproducibility
   - Different random seeds

---

## 📊 Success Criteria

### For P1 (Immediate):
- [ ] All remaining test failures identified
- [ ] Mock serialization issue investigated (even if not fixed)
- [ ] Tensor comparison validated or documented

### For P2 (Validation):
- [ ] Full test suite run completed
- [ ] Docker builds validated on all targets
- [ ] Coverage confirmed at or above baseline

### For P3 (Enhancement):
- Documentation only (no code changes required yet)

---

## 🔧 Tools & Commands Reference

### GitHub CLI:
```bash
# List workflow runs
gh run list --branch <branch> --limit 10

# View run details
gh run view <run-id>

# Download artifacts
gh run download <run-id>

# Get job logs
gh run view <run-id> --log --job <job-id>
```

### Docker:
```bash
# Build specific target
docker build --target <stage-name> -t <tag> .

# List images
docker images

# Run container
docker run --rm <image> <command>

# Clean up
docker system prune -a
```

### pytest:
```bash
# Run specific test
pytest path/to/test.py::test_name -xvs

# Run with coverage
pytest --cov=src --cov-report=html

# Run with markers
pytest -m "not slow" -v

# Collect only (no execution)
pytest --collect-only
```

---

## 📝 Execution Log

**Session Start**: 2026-02-01T23:39:00Z  
**Tasks Completed**: 
- [x] Dockerfile Python version fix
- [x] Review comment addressed
- [ ] P1 Task 1.1 (CI validation)
- [ ] P1 Task 1.2 (Mock serialization)
- [ ] P1 Task 1.3 (Tensor comparison)

**Next Action**: Execute P1 tasks in order

---

## 📚 Related Documents

- `.codex/analysis/PR_3095_FIX_SUMMARY.md` - Complete fix summary
- `.codex/analysis/test_failure_analysis_job_62150870508.md` - Detailed analysis
- `.codex/analysis/DOCKERFILE_FIX.md` - Docker fix details
- `tests/space_traversal/test_peft_comprehensive/` - Test files directory

---

**Status**: 📋 READY FOR EXECUTION  
**Estimated Time**: 
- P1: 2-3 hours
- P2: 1-2 hours  
- P3: Documentation only (30 mins)

**Total**: 3.5-5.5 hours
