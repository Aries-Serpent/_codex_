# PR #3095 Comprehensive Test Failure Analysis
**Prepared for**: Aries-Serpent/_codex_  
**PR**: #3095 "0 d base"  
**Branch**: 0D_base_  
**Analysis Date**: 2026-02-01  
**Analyzed Job**: 62150870508 (Python 3.12 - test-comprehensive.yml)

---

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| **Total Tests** | 194 |
| **✅ Passed** | 145 (74.7%) |
| **❌ Failed** | 10 (5.2%) |
| **⏭️ Skipped** | 39 (20.1%) |
| **⚠️ Warnings** | 6 |
| **Duration** | 335.76s (5m 36s) |
| **Status** | ❌ FAILED |

---

## 🎯 Executive Summary

PR #3095 introduces **documentation and analysis infrastructure** improvements but has **10 critical test failures** that must be resolved before merging:

### Failure Categories:
- 🔴 **Infrastructure** (2) - Missing Docker multi-stage targets
- 🔴 **Logic Errors** (2) - Pattern detection not working
- 🟡 **API Mismatches** (2) - Changed interfaces without test updates
- 🟡 **Missing Code** (2) - Missing functions/attributes
- 🟡 **Test Issues** (2) - Mock serialization, tensor comparison

### Critical Path Issues:
1. ⚠️ **Dockerfile missing cpu-runtime/gpu-runtime stages** - Blocks deployment tests
2. ⚠️ **OutcomeAnalyzer not detecting patterns** - Blocks cognitive brain functionality
3. ⚠️ **Missing _ts() function** - Blocks train loop tests

---

## 📋 Detailed Test Failures

### 1. 🔴 test_training_resume.py::test_run_functional_training_resume
```
TypeError: Object of type MagicMock is not JSON serializable
```
**Severity**: Medium  
**Component**: Training / Checkpointing  
**Fix Time**: 30 mins

**Problem**: Mocks are being serialized during checkpoint save  
**Solution**: Use serializable mock return values or patch JSON encoder

**Fix**:
```python
# In tests/test_training_resume.py
from unittest.mock import Mock

# Instead of bare MagicMock, use:
mock_checkpoint = Mock()
mock_checkpoint.to_dict = Mock(return_value={
    'epoch': 1,
    'step': 100,
    'metrics': {'loss': 0.5}
})
```

---

### 2. 🔴 crm/test_zaf_legacy_reader.py::test_read_and_scaffold_zaf
```
KeyError: 'files'
```
**Severity**: Medium  
**Component**: CRM / ZAF Legacy Reader  
**Fix Time**: 20 mins

**Problem**: `scaffold_template()` expects `bundle['files']` but `read_zaf()` doesn't provide it  
**Solution**: Fix return structure in `read_zaf()`

**Fix**:
```python
# In src/codex_crm/zaf_legacy/reader.py
def read_zaf(zip_path: Path) -> dict:
    with ZipFile(zip_path) as zf:
        manifest = json.loads(zf.read('manifest.json'))
        files = {}
        for name in zf.namelist():
            if name != 'manifest.json':
                files[name] = zf.read(name)
        
        return {
            'manifest': manifest,
            'files': files  # ← ADD THIS
        }
```

---

### 3. 🔴 cognitive_brain/learning/test_outcome_analyzer.py (2 tests)
```
test_analyze_success_outcome: assert 0 > 0 (len(patterns_identified))
test_high_confidence_patterns: assert 0 > 0 (len(patterns))
```
**Severity**: HIGH ⚠️  
**Component**: Cognitive Brain / Learning  
**Fix Time**: 1-2 hours

**Problem**: Pattern detection logic is broken - returns empty list  
**Impact**: Core cognitive functionality not working

**Investigation Steps**:
1. Check if `_extract_patterns()` is being called
2. Verify pattern detection thresholds
3. Check if test data generates sufficient signal
4. Review pattern storage/retrieval

**Potential Fix**:
```python
# In src/cognitive_brain/learning/outcome_analyzer.py
def analyze_outcome(self, outcome: LearningOutcome) -> LearningOutcome:
    # Calculate reward
    outcome.reward = self._calculate_reward(outcome)
    
    # Extract patterns ← ENSURE THIS IS CALLED
    if outcome.outcome_type == OutcomeType.SUCCESS:
        patterns = self._extract_patterns(outcome)
        outcome.patterns_identified = patterns  # ← ENSURE THIS IS SET
        
        # Generate lessons
        outcome.lessons_learned = self._generate_lessons(patterns)
    
    return outcome

def _extract_patterns(self, outcome: LearningOutcome) -> List[str]:
    """Extract patterns from successful outcomes."""
    patterns = []
    
    # Example pattern extraction logic
    if outcome.duration and outcome.duration < self.fast_threshold:
        patterns.append("quick_resolution")
    
    if outcome.context and "high_priority" in outcome.context:
        patterns.append("priority_handling")
    
    # ← ADD MORE PATTERN DETECTION LOGIC HERE
    
    return patterns
```

---

### 4. 🔴 deployment/test_docker_build.py (2 tests)
```
test_cpu_dockerfile_builds: target stage "cpu-runtime" could not be found
test_gpu_dockerfile_builds: target stage "gpu-runtime" could not be found
```
**Severity**: HIGH ⚠️  
**Component**: Deployment / Docker  
**Fix Time**: 1 hour

**Problem**: Dockerfile missing multi-stage build targets  
**Impact**: Cannot build or test Docker deployments

**Fix**: Add to `Dockerfile`:
```dockerfile
# ===== Stage 1: Base =====
FROM python:3.12-slim AS base

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e ".[core]"

# ===== Stage 2: CPU Runtime =====
FROM base AS cpu-runtime

# Additional CPU-specific dependencies
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

ENTRYPOINT ["python", "-m", "codex_ml"]
CMD ["--help"]

# ===== Stage 3: GPU Runtime =====
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04 AS gpu-runtime

# Copy Python and packages from base
COPY --from=base /usr/local /usr/local
COPY --from=base /app /app

WORKDIR /app

# GPU-specific dependencies
RUN pip install --no-cache-dir torch torchvision torchaudio

ENV CUDA_VISIBLE_DEVICES=0
ENTRYPOINT ["python", "-m", "codex_ml"]
CMD ["--help"]
```

**Test Locally**:
```bash
docker build --target cpu-runtime -t codex:cpu .
docker build --target gpu-runtime -t codex:gpu .
```

---

### 5. 🟡 test_peft_comprehensive/test_determinism_utilities.py::test_enable_with_warning
```
AssertionError: Warning should mention 'significantly' to match docstring
```
**Severity**: Low  
**Component**: Training / Determinism  
**Fix Time**: 5 mins

**Problem**: Warning text doesn't match docstring  
**Solution**: Update warning message

**Fix**:
```python
# In src/codex_ml/training/determinism.py
def enable_deterministic_mode():
    """Enable deterministic training mode.
    
    Warning: This may significantly reduce performance.
    """
    warnings.warn(
        "Deterministic mode enabled. This may significantly reduce performance.",
        UserWarning
    )
    
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
```

---

### 6. 🟡 test_peft_comprehensive/test_determinism_utilities.py::test_deterministic_mode_reproducibility
```
AssertionError: Results should be reproducible in deterministic mode
+ TypeError("'>' not supported between instances of 'Tensor' and 'float'")
```
**Severity**: Medium  
**Component**: Training / Determinism  
**Fix Time**: 1 hour

**Problem**: Two issues:
1. Non-reproducible results even in deterministic mode
2. Tensor comparison bug in repr

**Fix 1 - Proper seeding**:
```python
# In src/codex_ml/training/determinism.py
import random
import numpy as np
import torch

def enable_deterministic_mode(seed: int = 42):
    """Enable fully deterministic training."""
    # Set all seeds
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
```

**Fix 2 - Tensor comparison**:
```python
# In test or any code comparing tensors to floats
# Wrong:
if my_tensor > 0.5:  # ← TypeError on some PyTorch versions

# Correct:
if my_tensor.item() > 0.5:  # ← Convert to Python float first
```

---

### 7. 🔴 test_train_loop.py::test_ts_format
```
AttributeError: module 'codex_ml.train_loop' has no attribute '_ts'
```
**Severity**: HIGH ⚠️  
**Component**: Training / Utilities  
**Fix Time**: 10 mins

**Problem**: Missing utility function  
**Solution**: Add `_ts()` function

**Fix**:
```python
# In src/codex_ml/train_loop.py
from datetime import datetime, timezone

def _ts() -> str:
    """Generate ISO 8601 timestamp with 'Z' suffix.
    
    Returns:
        Timestamp string like "2026-02-01T12:34:56.789Z"
    """
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

# Export it
__all__ = ['_ts', 'record_metrics', 'main']
```

---

### 8. 🟡 test_train_loop.py::test_cli_parsing_smoke
```
ValueError: model_name must be provided when no model instance is supplied
```
**Severity**: Low  
**Component**: Training / CLI  
**Fix Time**: 5 mins

**Problem**: Test not updated for new required parameter  
**Solution**: Add `--model-name` to test args

**Fix**:
```python
# In tests/test_train_loop.py
def test_cli_parsing_smoke(tmp_path):
    """Test CLI parsing with minimal args."""
    train_file = tmp_path / "train.jsonl"
    train_file.write_text('{"text": "test"}\n')
    
    args = [
        "--model-name", "test-tiny-model",  # ← ADD THIS
        "--train-data", str(train_file),
        "--epochs", "1",
        "--grad-accum", "2",
        "--output", str(tmp_path)
    ]
    
    result = main(args)
    assert result == 0
```

---

## 🔧 Recommended Fix Sequence

### Phase 1: Quick Wins (30 minutes) ⚡
These are simple one-liners or small changes:

```bash
# 1. Add _ts() function (10 mins)
#    → src/codex_ml/train_loop.py

# 2. Update warning message (5 mins)
#    → src/codex_ml/training/determinism.py

# 3. Fix CLI test (5 mins)
#    → tests/test_train_loop.py

# 4. Fix ZAF reader (10 mins)
#    → src/codex_crm/zaf_legacy/reader.py

# Test:
pytest tests/test_train_loop.py -v
pytest tests/crm/test_zaf_legacy_reader.py -v
```

### Phase 2: Infrastructure (1 hour) 🏗️

```bash
# 5. Add Docker multi-stage targets (1 hour)
#    → Dockerfile

# Test:
docker build --target cpu-runtime -t codex:cpu .
docker build --target gpu-runtime -t codex:gpu .
pytest tests/deployment/test_docker_build.py -v
```

### Phase 3: Core Logic (2-3 hours) 🧠

```bash
# 6. Fix outcome analyzer pattern detection (2 hours)
#    → src/cognitive_brain/learning/outcome_analyzer.py
#    → tests/cognitive_brain/learning/test_outcome_analyzer.py

# 7. Fix mock serialization (30 mins)
#    → tests/test_training_resume.py

# 8. Fix deterministic mode (30 mins)
#    → src/codex_ml/training/determinism.py

# Test:
pytest tests/cognitive_brain/learning/test_outcome_analyzer.py -v
pytest tests/test_training_resume.py -v
pytest tests/space_traversal/test_peft_comprehensive/test_determinism_utilities.py -v
```

### Phase 4: Validation (30 minutes) ✅

```bash
# Run all tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Check no regressions
pytest tests/ -n auto -v
```

---

## 📝 Testing Commands

### Run Specific Failures:
```bash
# Quick wins
pytest tests/test_train_loop.py::test_ts_format -xvs
pytest tests/test_train_loop.py::test_cli_parsing_smoke -xvs
pytest tests/crm/test_zaf_legacy_reader.py::test_read_and_scaffold_zaf -xvs

# Docker
pytest tests/deployment/test_docker_build.py -xvs

# Cognitive
pytest tests/cognitive_brain/learning/test_outcome_analyzer.py::test_analyze_success_outcome -xvs
pytest tests/cognitive_brain/learning/test_outcome_analyzer.py::test_high_confidence_patterns -xvs

# Determinism
pytest tests/space_traversal/test_peft_comprehensive/test_determinism_utilities.py::TestDeterministicMode::test_enable_with_warning -xvs
pytest tests/space_traversal/test_peft_comprehensive/test_determinism_utilities.py::TestDeterministicModeIntegration::test_deterministic_mode_reproducibility -xvs

# Training
pytest tests/test_training_resume.py::test_run_functional_training_resume -xvs
```

### Run All Tests:
```bash
# Sequential with verbose output
pytest tests/ -v --tb=short

# Parallel with pytest-xdist
pytest tests/ -n auto -v

# With coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Stop on first failure
pytest tests/ -x -v
```

---

## 🔍 Root Cause Analysis

### Why These Failures Exist:

1. **Documentation-focused PR**: PR #3095 is primarily about documentation and analysis infrastructure, not code changes. Test failures suggest:
   - Tests exist for features that were removed/changed in earlier PRs
   - Tests weren't updated when implementations changed
   - Some infrastructure (Docker, pattern detection) is incomplete

2. **Technical Debt**: Several failures indicate accumulating technical debt:
   - Missing Docker configuration
   - Incomplete pattern detection logic
   - Outdated test assumptions

3. **Python 3.12 Migration**: Some failures may be related to Python 3.12 compatibility (user mentioned StopIteration issues, though not evident in these 10)

### Broader Issues (User Mentioned):
These **10 failures** cover some but not all issues the user mentioned:

| Issue Category | Found in These 10? | Status |
|----------------|-------------------|--------|
| Python 3.12 compatibility | ⚠️ Partial (tensor comparison) | Needs investigation |
| Mock serialization | ✅ Yes (#1) | Identified |
| API signature mismatches | ✅ Yes (#2, #8) | Identified |
| Missing infrastructure | ✅ Yes (#4, #5) | Identified |
| Empty optimizer issues | ❌ No | Check other jobs |
| HuggingFace 404 errors | ❌ No | Check other jobs |
| Data loader type mismatches | ❌ No | Check other jobs |
| Subprocess permissions | ❌ No | Check other jobs |
| PyTorch pickling | ⚠️ Related (#6) | Partial |

**Recommendation**: Analyze jobs 62146885593, 62146885584, 62150870454, 62151471669 for additional failure patterns.

---

## 📊 Success Criteria

### Before Merge:
- [ ] All 10 test failures fixed
- [ ] Tests pass locally on Python 3.12
- [ ] Tests pass in CI on Python 3.12
- [ ] Docker builds succeed (cpu-runtime, gpu-runtime)
- [ ] Pattern detection works (cognitive brain tests pass)
- [ ] No new test failures introduced
- [ ] Coverage remains at or above current level

### Validation:
```bash
# Local validation
pytest tests/ -v --tb=short
docker build --target cpu-runtime -t codex:cpu .
docker build --target gpu-runtime -t codex:gpu .

# CI validation
# Push to PR branch and check GitHub Actions
git push origin 0D_base_
```

---

## 📚 References

- **PR**: https://github.com/Aries-Serpent/_codex_/pull/3095
- **Failed Job**: https://github.com/Aries-Serpent/_codex_/actions/runs/21571330633 <!-- Note: Logs expire after 90 days -->/job/62150870508
- **Test Files**: `tests/` directory
- **Source Files**: `src/codex_ml/`, `src/cognitive_brain/`, `src/codex_crm/`

---

## 🎓 Lessons Learned

1. **Keep tests in sync**: When changing implementations, update tests immediately
2. **Complete infrastructure**: Don't merge PRs with incomplete Docker configs
3. **Test critical paths**: Pattern detection is core functionality - should have integration tests
4. **Mock carefully**: Ensure mocks are serializable if tests involve I/O
5. **Version compatibility**: Test on target Python version (3.12) before opening PR

---

**Analysis Completed**: 2026-02-01 22:40 UTC  
**Next Steps**: Follow the 4-phase fix sequence above  
**Estimated Total Fix Time**: 4-5 hours
