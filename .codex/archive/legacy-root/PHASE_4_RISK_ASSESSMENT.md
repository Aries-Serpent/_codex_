# Phase 4 & Phase 1 Risk Assessment & Mitigation Strategy

**Document:** Comprehensive Risk Matrix & Mitigation Plans  
**Date:** 2026-07-16  
**Scope:** Quick-Win Sprint (Phase 4) + Full Sprint (Phase 1)  
**Confidence Levels:** 92% (Quick-Win) / 90% (Phase 1)

---

## 🎯 Risk Assessment Framework

### Risk Matrix Categories

| Category | Risk Level | Detection | Escalation |
|----------|-----------|-----------|---|
| **CRITICAL** | 🔴 HIGH impact + HIGH probability | Automated (batch scan) | ci-emergency-response-agent |
| **HIGH** | 🟠 HIGH impact + MEDIUM probability | Manual review + CI | ci-testing-agent |
| **MEDIUM** | 🟡 MEDIUM impact + MEDIUM probability | Code review | unified-coverage-agent |
| **LOW** | 🟢 LOW impact or LOW probability | Post-sprint analysis | N/A |

---

## 🚨 PHASE 4 QUICK-WIN SPRINT RISKS

### Risk #QW-1: Test Import Failures (P19 Shadow Imports)

**Category:** MEDIUM  
**Probability:** 20%  
**Impact:** HIGH (blocks all 8 tests)

#### Root Cause
- Existing test file `tests/test_codex_plans.py` missing `import os`
- Potential wildcard imports from `pathlib` or `typing`
- P19 shadow import issue if using `from pathlib import *`

#### Detection
```bash
# Pre-sprint check
python3 -m pytest tests/test_codex_plans.py -v --tb=short -x
# Expected: 2 failures immediately visible
```

#### Mitigation
1. **Immediate:** Add missing `import os` to line 15 of `tests/test_codex_plans.py`
2. **Prevention:** Use explicit imports only:
   ```python
   # ✅ CORRECT
   from pathlib import Path
   import os
   
   # ❌ INCORRECT
   from pathlib import *
   from os import *
   ```
3. **Validation:** Run pre-flight check before sprint starts

#### Escalation
- **If persists after fix:** → `ci-importerror-agent`
- **If batch scan fails:** → `ci-emergency-response-agent`

---

### Risk #QW-2: Export Assertion Flexibility

**Category:** HIGH  
**Probability:** 15%  
**Impact:** MEDIUM (1 test failure)

#### Root Cause
- Test `TestCodexPlansModuleExports::test_no_unexpected_exports` checks `__all__` strictness
- Module imports `Path` from `pathlib` but doesn't re-export it
- Test assertion too strict: `assert attr in codex_plans.__all__`

#### Detection
```python
# Expected failure
FAILED tests/test_codex_plans.py::TestCodexPlansModuleExports::test_no_unexpected_exports
AssertionError: attr is not valid
assert ('Path' in ['list_plan_documents'] or 'Path' == 'list_plan_documents')
```

#### Mitigation (Option A - Recommended)
Update test logic to allow pathlib/typing imports:
```python
import pathlib
import typing

def test_no_unexpected_exports(self):
    """Test that module doesn't export private items."""
    import codex_plans
    
    for attr in dir(codex_plans):
        if not attr.startswith("_") and attr not in ["__all__"]:
            # Allow standard library imports
            if attr not in codex_plans.__all__:
                assert (
                    hasattr(pathlib, attr) or 
                    hasattr(typing, attr)
                ), f"Unexpected export: {attr}"
```

#### Mitigation (Option B - Alternative)
Add `Path` to `__all__` (modifies module API):
```python
__all__ = ["list_plan_documents", "Path"]
```

#### Escalation
- **If Option A fails:** → Switch to Option B (simpler)
- **If both fail:** → Code review (possible design issue)

---

### Risk #QW-3: Coverage Gap Analysis Incomplete

**Category:** LOW  
**Probability:** 10%  
**Impact:** MEDIUM (coverage < 30%)

#### Root Cause
- Coverage report may not capture all code paths
- Boundary conditions in `list_plan_documents()` may be missed
- Edge cases with symlinks or nested directories

#### Detection
```bash
# Post-test coverage analysis
python3 -m pytest tests/test_codex_plans_gap_fill.py \
    --cov=src/codex_plans \
    --cov-report=term-missing

# Check for uncovered lines
# Expected: Lines 15-31 mostly covered (90%+)
```

#### Mitigation
1. **Before sprint:** Run baseline coverage with existing tests
2. **During sprint:** Add tests for identified gaps (done in plan)
3. **After sprint:** Run coverage report & compare before/after

#### Escalation
- **If coverage < 25%:** → Add 2-3 more edge case tests
- **If coverage < 20%:** → Escalate to code review

---

### Risk #QW-4: Batch Scan Performance

**Category:** LOW  
**Probability:** 5%  
**Impact:** MEDIUM (timeout, retry needed)

#### Root Cause
- Batch scan script may not support small modules well
- Overhead may dominate actual test execution time
- System resource constraints (CPU/memory)

#### Detection
```bash
# Time the batch scan
time python3 scripts/ci/rvs_preflight.py --group quick --workers 2

# Expected: < 30 seconds for small module
```

#### Mitigation
1. **For quick-win:** Run pytest directly (not batch scan) since module is tiny
2. **For Phase 1:** Use batch scan with parallelism (`--workers 4`)
3. **Backup:** Run incremental scans if full scan times out

#### Escalation
- **If batch scan hangs:** → `workflow-optimization-agent`

---

## 🚨 PHASE 1 FULL SPRINT RISKS (120 tests, 4 lanes)

### Risk #P1-1: P19 Shadow Import Issues (CRITICAL)

**Category:** CRITICAL  
**Probability:** 30%  
**Impact:** HIGH (multiple test failures across lanes)

#### Root Cause
Module dependencies may use wildcard imports:
```python
# ❌ RISKY
from transformers import *  # P19 shadow import
from torch import *        # Brings in 100+ symbols

# ✅ SAFE
from transformers import GPT2LMHeadModel
from torch import nn, optim
```

#### Detection
```bash
# Find wildcard imports
grep -r "from .* import \*" src/codex_ml src/services src/codex src/mcp

# Expected: 0 matches in new test files
```

#### Mitigation (MANDATORY)
1. **Phase 1 Code Policy:** NO wildcard imports in tests
2. **Lint Check:** 
   ```bash
   python3 -m flake8 tests/test_*_gap_fill*.py --select=F401,F403
   # F403 = undefined names from import *
   # F401 = unused imports
   ```
3. **Import Audit:** Review all imports in new test files
4. **Template Usage:** Copy import patterns from existing test files

**Example Safe Pattern:**
```python
# test_codex_ml_gap_fill_lane1.py
import torch
from torch import nn
from transformers import GPT2LMHeadModel

import pytest
from codex_ml.models import CodexMLModel
```

#### Escalation
- **If wildcard imports found:** → Rewrite test file
- **If import errors persist:** → `ci-importerror-agent`
- **If batch scan regression:** → `ci-emergency-response-agent`

---

### Risk #P1-2: Stochastic Test Failures (ML Lane, HIGH)

**Category:** CRITICAL  
**Probability:** 40%  
**Impact:** HIGH (flaky tests, retry storms)

#### Root Cause
ML training & inference have randomness:
- Weight initialization varies without seed control
- Dropout, augmentation, batch norm randomness
- Optimizer convergence varies between runs

#### Detection
```bash
# Run test multiple times (detect flakiness)
for i in {1..5}; do
    python3 -m pytest tests/test_codex_ml_gap_fill_lane1.py::TestTrainingLoops -q
done

# Expected: All 5 runs identical (no failures)
```

#### Mitigation (MANDATORY for ML Lane)
1. **Seed Control:** Set seeds in every fixture
   ```python
   @pytest.fixture
   def model():
       torch.manual_seed(42)           # PyTorch
       np.random.seed(42)              # NumPy
       random.seed(42)                 # Python random
       if torch.cuda.is_available():
           torch.cuda.manual_seed(42)
       return CodexMLModel(dim=512)
   ```

2. **Disable Stochastic Behavior:** 
   ```python
   model.eval()  # Disable dropout
   torch.no_grad()  # Disable gradient computation
   ```

3. **Use Deterministic Ops:**
   ```python
   torch.use_deterministic_algorithms(True)
   ```

4. **Test Ranges Instead of Exact Values:**
   ```python
   # ❌ TOO STRICT (flaky)
   assert loss == 2.718281828
   
   # ✅ ROBUST
   assert 2.5 < loss < 3.5
   assert isinstance(loss, torch.Tensor)
   ```

#### Escalation
- **If >5% flaky:** → `autonomous-test-healer-agent`
- **If >10% flaky:** → Reduce test scope, escalate to code review

---

### Risk #P1-3: Device/GPU Mocking Issues (ML Lane, HIGH)

**Category:** HIGH  
**Probability:** 25%  
**Impact:** HIGH (environment-dependent failures)

#### Root Cause
Tests may assume GPU availability that doesn't exist in CI:
- CI runner is CPU-only (no CUDA/Metal support)
- Tests accidentally try to move tensors to GPU
- Device type checks fail in unexpected ways

#### Detection
```bash
# Check GPU availability in test env
python3 -c "import torch; print(torch.cuda.is_available())"

# Expected: False (CI has no GPU)
```

#### Mitigation (MANDATORY for ML Lane)
1. **Force CPU-Only in Tests:**
   ```python
   @pytest.fixture
   def model():
       # MUST use device='cpu'
       model = CodexMLModel(device='cpu')
       assert str(model.device) == 'cpu'
       return model
   ```

2. **Mock GPU Calls:**
   ```python
   def test_model_respects_device():
       model = CodexMLModel(device='cpu')
       x = torch.randn(2, 128)
       # Do NOT call .to('cuda')
       output = model.forward(x)
       assert output.device.type == 'cpu'
   ```

3. **No CUDA Operations:**
   ```python
   # ❌ RISKY (may fail if no GPU)
   if torch.cuda.is_available():
       model = model.cuda()  # Device-dependent
   
   # ✅ SAFE
   device = 'cpu'  # Always CPU in tests
   model = model.to(device)
   ```

#### Escalation
- **If GPU-dependent test found:** → Rewrite to CPU-only
- **If device type errors persist:** → `ci-importerror-agent`

---

### Risk #P1-4: Async/Await Test Issues (Services Lane, HIGH)

**Category:** HIGH  
**Probability:** 30%  
**Impact:** MEDIUM (Services lane stalls)

#### Root Cause
Async HTTP handlers require special test setup:
- Missing `@pytest.mark.asyncio` decorator
- Event loop issues in test fixtures
- Timeout configuration mismatches

#### Detection
```bash
# Run services tests
python3 -m pytest tests/test_services_gap_fill.py -v --tb=short

# Expected: 0 failures
# Common error: "RuntimeError: no running event loop"
```

#### Mitigation (MANDATORY for Services Lane)
1. **Mark Async Tests:**
   ```python
   @pytest.mark.asyncio
   async def test_async_endpoint():
       client = AsyncTestClient(app)
       response = await client.get("/api/users")
       assert response.status_code == 200
   ```

2. **Use Test Client Fixture:**
   ```python
   @pytest.fixture
   async def client():
       from fastapi.testclient import TestClient
       return TestClient(app)
   ```

3. **Async Fixture Support:**
   ```python
   import pytest_asyncio
   
   @pytest_asyncio.fixture
   async def db_session():
       async with db_connect() as session:
           yield session
           await session.close()
   ```

4. **Timeout Configuration:**
   ```python
   pytest.ini:
   asyncio_mode = auto
   asyncio_default_fixture_scope = function
   timeout = 5
   ```

#### Escalation
- **If async failures persist:** → `ci-testing-agent`
- **If event loop errors:** → Use `pytest-asyncio` documentation

---

### Risk #P1-5: Mock/Fixture Complexity (MCP Lane, MEDIUM)

**Category:** HIGH  
**Probability:** 35%  
**Impact:** MEDIUM (MCP lane debugging time)

#### Root Cause
MCP protocol tests require complex socket/IPC mocks:
- Socket connection mocking is multi-layered
- Message serialization/deserialization difficult to mock
- Resource cleanup edge cases

#### Detection
```bash
# Run MCP tests
python3 -m pytest tests/test_mcp_gap_fill_bridge.py -v --tb=short

# Common issues:
# - AttributeError: MagicMock has no 'send'
# - ConnectionError during mock setup
# - Resource leaks in teardown
```

#### Mitigation (MANDATORY for MCP Lane)
1. **Use Pre-Built Socket Fixtures:**
   ```python
   @pytest.fixture
   def mock_socket(mocker):
       sock = mocker.MagicMock()
       sock.send.return_value = 128  # bytes sent
       sock.recv.return_value = b"response"
       mocker.patch("socket.socket", return_value=sock)
       yield sock
       sock.close()  # cleanup
   ```

2. **Message Roundtrip Tests:**
   ```python
   def test_message_serialize_deserialize():
       msg = MCPMessage(id=42, method="test")
       binary = msg.serialize()
       
       # Deserialize and validate
       restored = MCPMessage.deserialize(binary)
       assert restored.id == msg.id
   ```

3. **Resource Cleanup:**
   ```python
   @pytest.fixture
   def bridge():
       b = MCPBridge()
       yield b
       b.close()  # ALWAYS cleanup
   ```

4. **Avoid Complex State:**
   ```python
   # ❌ RISKY (complex mock state)
   mock.side_effect = [msg1, msg2, msg3]
   
   # ✅ SAFER (explicit control)
   def get_response(*args, **kwargs):
       if args[0] == "request":
           return "response"
       raise ValueError("Unexpected call")
   mock.side_effect = get_response
   ```

#### Escalation
- **If mock failures:** → Use `unittest.mock` documentation
- **If persistent issues:** → Simplify test scope

---

### Risk #P1-6: Batch Scan Timeout (CRITICAL)

**Category:** CRITICAL  
**Probability:** 15%  
**Impact:** HIGH (entire sprint fails)

#### Root Cause
Batch scan may not handle 120 new tests efficiently:
- Worker process startup overhead
- Test collection time
- Reporting latency

#### Detection
```bash
# Time batch scan with all tests
time python3 scripts/ci/rvs_preflight.py \
    --group quick \
    --workers 4 \
    --batch-size 30

# Expected: 15-30 minutes max
# Alert if: >45 minutes
```

#### Mitigation (MANDATORY)
1. **Use Incremental Scanning:**
   ```bash
   # Scan by lane, not all at once
   python3 scripts/ci/rvs_preflight.py \
       --group quick \
       --changed-only \
       --workers 4
   ```

2. **Monitor Worker Health:**
   ```python
   # In batch scan output
   # Expected: [Worker 1] OK, [Worker 2] OK, etc.
   ```

3. **Fallback to Direct Pytest:**
   ```bash
   # If batch scan hangs, use pytest directly
   python3 -m pytest tests/test_*_gap_fill*.py -q --tb=no
   ```

4. **Set Timeout Limits:**
   ```yaml
   pytest.ini:
   timeout = 60  # per test
   timeout_method = thread
   ```

#### Escalation
- **If batch scan hangs:** → Kill and switch to direct pytest
- **If repeatable timeout:** → `workflow-optimization-agent`

---

### Risk #P1-7: Threshold Regression (CRITICAL)

**Category:** CRITICAL  
**Probability:** 5%  
**Impact:** CRITICAL (sprint fails, blocks PR)

#### Root Cause
New tests may inadvertently trigger code paths that decrease coverage:
- New test fixtures may break existing tests
- Import changes may affect coverage baseline
- Pytest configuration changes may affect reporting

#### Detection
```bash
# Check fail_under before sprint
grep "fail_under" pyproject.toml
# Expected: fail_under = 34

# After sprint, verify it's still 34
grep "fail_under" pyproject.toml
# Expected: fail_under = 34 (NOT LOWER)
```

#### Mitigation (MANDATORY)
1. **Anti-Regression Guard:**
   ```python
   # Check in test initialization
   def test_fail_under_not_lowered():
       with open('pyproject.toml') as f:
           content = f.read()
           match = re.search(r'fail_under\s*=\s*(\d+)', content)
           current = int(match.group(1))
       assert current >= 34, f"fail_under decreased: {current} < 34"
   ```

2. **Separate Test Runs:**
   - Run new tests on branch
   - Run full suite on main
   - Compare results

3. **Baseline Measurement:**
   ```bash
   # Before starting Phase 1
   python3 -m pytest --cov=src \
       --cov-report=json:artifacts/baseline.json
   ```

#### Escalation
- **If regression detected:** → Investigate which test caused it
- **If fail_under decreases:** → STOP, escalate to code review

---

### Risk #P1-8: Test Interdependencies (MEDIUM)

**Category:** MEDIUM  
**Probability:** 20%  
**Impact:** MEDIUM (flaky batches)

#### Root Cause
Tests may share state or depend on execution order:
- Shared fixtures with mutable state
- Global variables modified in tests
- File system side effects (temp files not cleaned up)

#### Detection
```bash
# Run tests in random order
python3 -m pytest tests/test_*_gap_fill*.py --random-order -v

# Expected: All tests pass regardless of order
# If failures occur: test interdependence issue
```

#### Mitigation (MANDATORY)
1. **Isolated Fixtures:**
   ```python
   # ✅ GOOD (fresh instance per test)
   @pytest.fixture
   def model():
       return CodexMLModel()  # new instance
   
   # ❌ BAD (shared state)
   @pytest.fixture(scope="module")
   def model():
       return CodexMLModel()  # reused across tests
   ```

2. **Temp File Cleanup:**
   ```python
   @pytest.fixture
   def temp_file():
       with tempfile.NamedTemporaryFile(delete=False) as f:
           path = f.name
           yield path
       os.unlink(path)  # cleanup
   ```

3. **Reset Global State:**
   ```python
   @pytest.fixture
   def reset_globals():
       old_state = global_var
       yield
       global_var = old_state
   ```

#### Escalation
- **If order-dependent failures:** → Rewrite test as independent
- **If persistent interdependence:** → Escalate to code review

---

### Risk #P1-9: Code Review Quality (MEDIUM)

**Category:** MEDIUM  
**Probability:** 25%  
**Impact:** MEDIUM (rework needed)

#### Root Cause
18,800 LOC of new tests is difficult to review for:
- Inconsistent patterns
- Missing docstrings
- Anti-patterns (hardcoded paths, magic numbers)

#### Detection
```bash
# Static analysis on test files
python3 -m flake8 tests/test_*_gap_fill*.py
python3 -m pylint tests/test_*_gap_fill*.py

# Expected: <20 issues
# Alert if: >50 issues
```

#### Mitigation (MANDATORY)
1. **Code Review Checklist:**
   ```markdown
   - [ ] All tests have docstrings
   - [ ] No hardcoded paths (use tempfile/fixtures)
   - [ ] No magic numbers (use named constants)
   - [ ] No print() statements (use logging/pytest)
   - [ ] Fixtures are isolated (function scope default)
   - [ ] No P19 shadow imports
   - [ ] All mocks verified in tests
   - [ ] Error cases tested
   ```

2. **Pre-Review Lint:**
   ```bash
   python3 -m black tests/test_*_gap_fill*.py
   python3 -m isort tests/test_*_gap_fill*.py
   ```

3. **Documentation:**
   - Class-level docstrings explaining test purpose
   - Method docstrings for complex test logic

#### Escalation
- **If >50 lint issues:** → Auto-fix with black/isort
- **If pattern violations:** → Rewrite affected test class

---

## 📋 Risk Prioritization & Response Plan

### Priority 1 (MUST FIX BEFORE SPRINT)
1. ✅ Fix `test_codex_plans.py` import errors (Risk QW-1)
2. ✅ Add seed control to all ML fixtures (Risk P1-2)
3. ✅ Force CPU-only device in ML tests (Risk P1-3)
4. ✅ Audit for wildcard imports (Risk P1-1)

### Priority 2 (MUST HANDLE DURING SPRINT)
1. ⏳ Monitor batch scan timing (Risk P1-6)
2. ⏳ Verify threshold not regressing (Risk P1-7)
3. ⏳ Ensure test isolation (Risk P1-8)

### Priority 3 (MONITOR POST-SPRINT)
1. 📊 Code review quality (Risk P1-9)
2. 📊 Mock/fixture complexity (Risk P1-5)
3. 📊 Async test reliability (Risk P1-4)

---

## 🛡️ Guardrails & Gates

### Pre-Sprint Gate (MUST PASS)

```bash
#!/bin/bash
set -e

echo "=== PRE-SPRINT GUARDRAIL CHECK ==="

# 1. Baseline coverage check
echo "[1/5] Checking baseline coverage..."
grep "fail_under = 34" pyproject.toml || exit 1

# 2. Import audit
echo "[2/5] Auditing for wildcard imports..."
if grep -r "from .* import \*" tests/test_*_gap_fill*.py 2>/dev/null; then
    echo "❌ Wildcard imports found!"
    exit 1
fi

# 3. Seed control check
echo "[3/5] Verifying seed control in fixtures..."
if grep -l "torch.manual_seed\|np.random.seed" tests/test_codex_ml_*.py; then
    echo "✅ Seeds configured"
else
    echo "❌ Seeds missing!"
    exit 1
fi

# 4. Device check
echo "[4/5] Verifying CPU-only device..."
if grep "device='cpu'" tests/test_codex_ml_*.py > /dev/null; then
    echo "✅ CPU-only configured"
else
    echo "❌ Device not specified!"
    exit 1
fi

# 5. Lint check
echo "[5/5] Running lint..."
python3 -m flake8 tests/test_*_gap_fill*.py --max-line-length=100 --count || exit 1

echo "✅ ALL GUARDRAILS PASSED"
```

### Post-Sprint Gate (MUST PASS)

```bash
#!/bin/bash
set -e

echo "=== POST-SPRINT GUARDRAIL CHECK ==="

# 1. Threshold verification
echo "[1/4] Verifying threshold..."
grep "fail_under = 34" pyproject.toml || {
    echo "❌ fail_under changed!"
    exit 1
}

# 2. Test pass rate
echo "[2/4] Checking test pass rate..."
PASS_RATE=$(python3 -m pytest tests/test_*_gap_fill*.py -q --tb=no 2>&1 | \
    tail -1 | grep -oP '\d+(?= passed)')
if [ "$PASS_RATE" -lt 120 ]; then
    echo "❌ Not all tests passed!"
    exit 1
fi

# 3. Coverage measurement
echo "[3/4] Measuring coverage..."
python3 -m pytest tests/test_*_gap_fill*.py \
    --cov=src --cov-report=json:artifacts/coverage.json

# 4. Batch scan
echo "[4/4] Running batch scan..."
python3 scripts/ci/rvs_preflight.py --group quick --workers 4

echo "✅ ALL POST-SPRINT GATES PASSED"
```

---

## 📞 Escalation Contacts

| Risk Category | Primary Contact | Backup |
|---|---|---|
| P19 Imports | ci-importerror-agent | autonomous-test-healer-agent |
| ML Flakiness | autonomous-test-healer-agent | test-pattern-guardian |
| Device Issues | ci-importerror-agent | ci-emergency-response-agent |
| Async Timeouts | ci-testing-agent | workflow-optimization-agent |
| Threshold Regression | unified-coverage-agent | ci-health-alert-agent |
| Batch Scan Hangs | workflow-optimization-agent | ci-emergency-response-agent |
| Code Quality | code-review agent | test-pattern-guardian |

---

## ✅ Conclusion

**Overall Risk Assessment:**
- **Phase 4 Quick-Win:** 🟢 **LOW RISK** (92% confidence)
  - Small module (34 LOC), well-scoped, 8 tests
  - Main risks: import fixes (2 minutes each)
  
- **Phase 1 Full Sprint:** 🟡 **MEDIUM RISK** (90% confidence)
  - Larger scope (125k LOC), 120 tests, 4 parallel lanes
  - Mitigation: Mandatory seed control, CPU-only, wildcard audit
  - Escalation: 3 expert agents available

**Success Probability:** 85% (first attempt pass-through)

**Timeline:** 
- Quick-Win: 1-2 hours
- Phase 1: 12-24 hours (with parallel lanes)

---

**Assessment Owner:** Unified Coverage Agent  
**Date:** 2026-07-16  
**Status:** ✅ Ready for Distribution
