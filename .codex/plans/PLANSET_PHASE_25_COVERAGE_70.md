# PLANSET: Phase 25 - Coverage 70% Achievement (Production-Ready)

**Created**: 2026-01-20  
**Owner**: GitHub Copilot Agents  
**Target**: Raise coverage from 50% to 70% (Production-Ready)  
**Timeline**: 2 weeks  
**Status**: 🔄 READY FOR EXECUTION (after Phase 24)  
**Agent**: Coverage Roadmap Agent  
**Prerequisites**: Phase 24 complete with 50%+ coverage  
**Significance**: 70% is the production-ready milestone

---

## 🎯 Mission Statement

Execute Phase 25 to achieve **70% test coverage** - the production-ready threshold. This phase focuses on comprehensive E2E testing, critical path coverage, edge case handling, and production reliability. Phase 25 represents the minimum viable coverage for production deployment.

---

## 📋 PRE-EXECUTION CHECKLIST

### Prerequisites Validation
```bash
cd /home/runner/work/_codex_/_codex_

# 1. Verify Phase 24 complete
grep "fail_under = 50" pyproject.toml && echo "✅ Phase 24 threshold raised"

# 2. Validate current coverage ≥50%
python -m pytest tests/ --cov=src --cov-report=term | grep "^TOTAL"

# 3. Verify test suite stability
python -m pytest tests/ -v --tb=line | grep -E "(PASSED|FAILED)" | wc -l

# 4. Check AfterMath analyses
ls -1 .codex/plans/PHASE_*_AFTERMATH_ANALYSIS.md

# 5. Validate CI health (last 10 runs, >90% pass rate)
```

**Decision Gate**: All checks pass + management approval for production readiness work.

---

## 🎯 PHASE 25 STRATEGY

### Coverage Focus
1. **Critical Paths** (40% of effort)
   - Authentication/authorization flows
   - Data persistence/retrieval
   - Model training/inference critical sections
   - Error handling and recovery

2. **E2E Scenarios** (35% of effort)
   - Complete user workflows
   - Multi-step processes
   - Real-world usage patterns

3. **Edge Cases & Robustness** (25% of effort)
   - Boundary conditions
   - Error conditions
   - Performance under load
   - Concurrent access patterns

---

## 📅 WEEK 1: Critical Path & E2E Coverage

### Objective
Add 80-100 tests focusing on critical paths and E2E scenarios

### Plan Phase (Day 1)

**Action**: Identify critical code paths
```bash
# Analyze code for critical paths (high-impact, mission-critical)
python << 'EOF'
import ast
from pathlib import Path
import json

critical_modules = []

# Heuristics for criticality:
# 1. Contains "auth" or "security" in path
# 2. Contains database/persistence operations
# 3. Contains model training/inference logic
# 4. Has high cyclomatic complexity

src_path = Path("src")
for py_file in src_path.rglob("*.py"):
    rel_path = str(py_file.relative_to(src_path))
    
    # Check path-based criticality
    is_critical = any(keyword in rel_path.lower() for keyword in [
        "auth", "security", "database", "model", "training", "inference"
    ])
    
    if is_critical:
        critical_modules.append({
            "path": rel_path,
            "reason": "Path indicates critical functionality"
        })

print(f"Identified {len(critical_modules)} critical modules:")
for mod in critical_modules[:20]:
    print(f"  - {mod['path']}: {mod['reason']}")

with open(".codex/plans/phase25_critical_paths.json", "w") as f:
    json.dump(critical_modules, f, indent=2)
EOF
```

### Do Phase (Days 2-6)

#### Critical Path Group 1: Authentication & Authorization
```python
# tests/critical/test_auth_flows.py
import pytest
from unittest.mock import Mock, patch
import jwt
from datetime import datetime, timedelta

def test_auth_token_generation():
    """Verify secure token generation"""
    from auth.token_manager import generate_token
    
    user_id = "test_user_123"
    token = generate_token(user_id)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode and verify
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert decoded["user_id"] == user_id

def test_auth_token_expiration():
    """Verify token expiration handling"""
    from auth.token_manager import generate_token, verify_token
    
    # Generate expired token
    expired_token = generate_token("user", expires_in=-1)
    
    with pytest.raises(jwt.ExpiredSignatureError):
        verify_token(expired_token)

def test_auth_invalid_token():
    """Verify rejection of invalid tokens"""
    from auth.token_manager import verify_token
    
    invalid_tokens = [
        "not.a.token",
        "",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature",
    ]
    
    for token in invalid_tokens:
        with pytest.raises((jwt.DecodeError, jwt.InvalidTokenError)):
            verify_token(token)

def test_auth_permission_checks():
    """Verify role-based access control"""
    from auth.permissions import has_permission
    
    # Test user with permissions
    user_admin = {"role": "admin", "permissions": ["read", "write", "delete"]}
    assert has_permission(user_admin, "delete")
    
    # Test user without permissions
    user_viewer = {"role": "viewer", "permissions": ["read"]}
    assert not has_permission(user_viewer, "delete")

@pytest.mark.parametrize("attack_vector", [
    "'; DROP TABLE users; --",  # SQL injection
    "<script>alert('xss')</script>",  # XSS
    "../../../etc/passwd",  # Path traversal
])
def test_auth_security_against_attacks(attack_vector):
    """Verify auth system resists common attacks"""
    from auth.authentication import authenticate
    
    # Should not crash or succeed with malicious input
    result = authenticate(username=attack_vector, password="test")
    assert result is None or result == False
```

#### Critical Path Group 2: Data Persistence
```python
# tests/critical/test_data_persistence.py
import pytest
from pathlib import Path
import tempfile
import json

def test_checkpoint_save_and_load():
    """Verify model checkpoints can be saved and loaded"""
    from modeling import TransformerModel, save_checkpoint, load_checkpoint
    import torch
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and save model
        model = TransformerModel(hidden_size=128, num_layers=2)
        checkpoint_path = Path(tmpdir) / "checkpoint.pt"
        save_checkpoint(model, checkpoint_path)
        
        assert checkpoint_path.exists()
        
        # Load model
        loaded_model = load_checkpoint(checkpoint_path)
        
        # Verify state matches
        original_state = model.state_dict()
        loaded_state = loaded_model.state_dict()
        
        for key in original_state:
            assert torch.allclose(original_state[key], loaded_state[key])

def test_checkpoint_corruption_handling():
    """Verify graceful handling of corrupted checkpoints"""
    from modeling import load_checkpoint
    
    with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as f:
        # Write corrupted data
        f.write(b"corrupted checkpoint data")
        corrupted_path = f.name
    
    try:
        with pytest.raises((RuntimeError, ValueError)):
            load_checkpoint(corrupted_path)
    finally:
        Path(corrupted_path).unlink()

def test_training_state_persistence():
    """Verify training state (optimizer, scheduler) persists correctly"""
    from training import Trainer, save_training_state, load_training_state
    import torch
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup trainer
        model = Mock()
        optimizer = torch.optim.Adam([torch.nn.Parameter(torch.randn(10, 10))], lr=0.001)
        
        # Save state
        state_path = Path(tmpdir) / "training_state.pt"
        save_training_state({
            "optimizer": optimizer.state_dict(),
            "global_step": 100,
            "epoch": 5
        }, state_path)
        
        # Load state
        loaded_state = load_training_state(state_path)
        
        assert loaded_state["global_step"] == 100
        assert loaded_state["epoch"] == 5
```

#### E2E Scenarios: Production Workflows
```python
# tests/e2e/test_production_workflows.py
import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile

@pytest.mark.slow
def test_production_workflow_full_training_pipeline():
    """Complete production training workflow"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 1. Prepare data
        prep_result = runner.invoke(app, [
            "prepare-data",
            "--input", "tests/fixtures/production_sample.txt",
            "--output", str(tmpdir / "data"),
            "--validation-split", "0.1",
            "--test-split", "0.1"
        ])
        assert prep_result.exit_code == 0
        
        # 2. Train model
        train_result = runner.invoke(app, [
            "train",
            "--data-dir", str(tmpdir / "data"),
            "--output-dir", str(tmpdir / "model"),
            "--config", "configs/production.yaml",
            "--max-steps", "100",
            "--eval-steps", "25",
            "--save-steps", "25"
        ])
        assert train_result.exit_code == 0
        
        # 3. Evaluate on test set
        eval_result = runner.invoke(app, [
            "evaluate",
            "--model-path", str(tmpdir / "model"),
            "--data-path", str(tmpdir / "data/test.json"),
            "--output", str(tmpdir / "eval_results.json")
        ])
        assert eval_result.exit_code == 0
        
        # 4. Export for production
        export_result = runner.invoke(app, [
            "export",
            "--model-path", str(tmpdir / "model"),
            "--format", "onnx",
            "--optimize",
            "--output", str(tmpdir / "model.onnx")
        ])
        assert export_result.exit_code == 0
        
        # 5. Verify exported model works
        inference_result = runner.invoke(app, [
            "infer",
            "--model", str(tmpdir / "model.onnx"),
            "--input", "tests/fixtures/inference_sample.txt",
            "--output", str(tmpdir / "predictions.json")
        ])
        assert inference_result.exit_code == 0
        
        # Verify all outputs exist and are valid
        assert (tmpdir / "data/train.json").exists()
        assert (tmpdir / "model").exists()
        assert (tmpdir / "eval_results.json").exists()
        assert (tmpdir / "model.onnx").exists()
        assert (tmpdir / "predictions.json").exists()

@pytest.mark.slow
def test_production_workflow_with_monitoring():
    """Training workflow with monitoring and alerting"""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Train with monitoring enabled
        result = runner.invoke(app, [
            "train",
            "--config", "configs/production.yaml",
            "--data-dir", "tests/fixtures/tiny_data",
            "--output-dir", tmpdir,
            "--enable-monitoring",
            "--log-to-mlflow",
            "--alert-on-metric-drop"
        ])
        
        assert result.exit_code == 0
        # Verify monitoring artifacts
        assert Path(tmpdir).exists()
```

### Analyze Phase (Day 7)

**Action**: Final gap analysis for 70% target
```bash
# Comprehensive coverage analysis
python -m pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html:htmlcov/phase25_week1 \
  --cov-report=json:.coverage_phase25_week1.json

# Calculate remaining gap
python << 'EOF'
import json

with open('.coverage_phase25_week1.json') as f:
    cov = json.load(f)

total = sum(f['summary']['num_statements'] for f in cov['files'].values())
covered = sum(f['summary']['covered_lines'] for f in cov['files'].values())
current_pct = (covered / total * 100) if total > 0 else 0

print(f"Current Coverage: {current_pct:.2f}%")
print(f"Target: 70%")
print(f"Gap: {max(0, 70 - current_pct):.2f}%")

if current_pct >= 65:
    print("\n✅ On track for 70% threshold!")
elif current_pct >= 60:
    print("\n⚠️  Need additional tests in Week 2")
else:
    print("\n❌ Significant additional work required")

# Identify final gap modules
print("\nRemaining gaps (modules <50% coverage):")
for file_path, file_data in cov['files'].items():
    file_cov = file_data['summary']['percent_covered']
    if file_cov < 50:
        print(f"  - {file_path}: {file_cov:.1f}%")
EOF
```

**AfterMath Analysis**: [Similar structure to previous phases]

---

## 📅 WEEK 2: Edge Cases & Final Push to 70%

### Objective
Complete coverage to 70% through edge case testing and targeted gap-filling

### Plan Phase (Day 1)
Analyze remaining gaps and create targeted test plan for each module below 70%.

### Do Phase (Days 2-5)

#### Edge Case Testing
```python
# tests/edge_cases/test_boundary_conditions.py
import pytest
import sys

@pytest.mark.parametrize("edge_input", [
    0,  # Zero
    1,  # Minimum positive
    -1,  # Minimum negative
    sys.maxsize,  # Maximum int
    float('inf'),  # Infinity
    float('nan'),  # NaN
])
def test_numerical_edge_cases(edge_input):
    """Test handling of numerical edge cases"""
    # Test relevant functions with edge inputs
    pass

@pytest.mark.parametrize("edge_string", [
    "",  # Empty
    " ",  # Whitespace only
    "a" * 10000,  # Very long
    "\n\n\n",  # Newlines only
    "🚀" * 100,  # Unicode/emoji
])
def test_string_edge_cases(edge_string):
    """Test handling of string edge cases"""
    pass

def test_concurrent_access():
    """Test thread-safe operations"""
    import threading
    # Test concurrent access patterns
    pass

def test_memory_limits():
    """Test behavior under memory pressure"""
    # Test with large data structures
    pass
```

### Threshold Raise (Day 6-7)

**Final Validation**:
```bash
# 1. Coverage verification
coverage_pct=$(python -m pytest tests/ --cov=src --cov-report=term | grep "^TOTAL" | awk '{print $NF}' | tr -d '%')
if (( $(echo "$coverage_pct >= 70" | bc -l) )); then
    echo "✅ Coverage at $coverage_pct% - ready for threshold raise"
else
    echo "❌ Coverage at $coverage_pct% - need more tests"
    exit 1
fi

# 2. Full test suite
python -m pytest tests/ -v --tb=short

# 3. Performance check (should complete in <15 min)
time python -m pytest tests/

# 4. CI verification
# Check last 5 runs all green
```

**Action**: Raise to 70%
```bash
# Update threshold
sed -i 's/fail_under = 50/fail_under = 70/' pyproject.toml

# Commit
git add pyproject.toml
git commit -m "feat: Raise coverage threshold to 70% - PRODUCTION READY

- Added 80-100 critical path tests
- Added comprehensive E2E production workflows
- Added edge case and robustness testing
- Verified coverage at 70.X%
- All CI checks passing

🎉 Phase 25 complete - PRODUCTION READY coverage achieved!
Target milestone reached: 70% coverage represents production-ready quality."

git tag -a "coverage-70-production-ready" -m "Production-ready coverage threshold achieved"
```

---

## 🚨 ERROR HANDLING

### Production-Critical Errors

#### Error: Coverage Drops Below 70% After Threshold Raise
**Immediate Action**:
```bash
# Emergency rollback
git revert HEAD
git push --force

# Analyze cause
python -m pytest tests/ --cov=src --cov-report=term-missing | grep "0%"

# Fix missing tests
# Re-attempt threshold raise
```

#### Error: Performance Regression
**Solution**:
```python
# Add performance benchmarks
@pytest.mark.benchmark
def test_inference_performance():
    import time
    start = time.time()
    # Run inference
    duration = time.time() - start
    assert duration < 1.0, f"Inference took {duration}s (>1.0s threshold)"
```

---

## 📊 SUCCESS CRITERIA

### Must-Have (Blocking Production)
- [ ] Coverage ≥70% measured by pytest-cov
- [ ] All critical paths tested
- [ ] Zero high-severity bugs
- [ ] CI green for 5 consecutive runs
- [ ] Performance benchmarks passing
- [ ] pyproject.toml updated to 70

### Should-Have
- [ ] Test execution time <15 minutes
- [ ] Mutation testing score >75%
- [ ] All E2E workflows tested

### Production Readiness Checklist
- [ ] Authentication/authorization fully tested
- [ ] Data persistence verified
- [ ] Error handling comprehensive
- [ ] Performance validated
- [ ] Security testing complete
- [ ] Monitoring integration tested

---

## 🎉 PHASE 25 COMPLETION CEREMONY

Upon reaching 70% coverage:

1. **Create Release Tag**: `coverage-70-production-ready`
2. **Generate Report**: Document journey from 17% to 70%
3. **Update Documentation**: Mark system as production-ready
4. **Notify Stakeholders**: Coverage milestone achieved
5. **Plan Phase 26+**: Optional path to 100%

---

## 📝 CONTINUATION PROMPTSET

**For GitHub Copilot Agent** (post as comment after Phase 25):

```markdown
@copilot Phase 25 complete - 70% production-ready coverage achieved! 🎉

Review completion summary in `.codex/plans/PHASE_25_COMPLETION_SUMMARY.md`.

**Optional Next Steps** (Phase 26+):
- Path to 80%: Focus on secondary workflows
- Path to 90%: Comprehensive edge case coverage
- Path to 100%: Aspirational complete coverage (exclude generated code)

**Current Status**:
- ✅ 70% coverage (production-ready)
- ✅ All critical paths tested
- ✅ CI stable
- ✅ Performance validated

**Recommendation**: Monitor coverage in production, address regressions as they occur. Consider Phase 26+ based on business needs and ROI analysis.

**Reference**: `.codex/cognitive_brain/PHASE_25_PRODUCTION_READY_STATUS.md`
```

---

**Status**: ✅ READY FOR EXECUTION (after Phase 24)  
**Significance**: **PRODUCTION READY MILESTONE**  
**Owner**: @mbaetiong  
**Agent**: Coverage Roadmap Agent
