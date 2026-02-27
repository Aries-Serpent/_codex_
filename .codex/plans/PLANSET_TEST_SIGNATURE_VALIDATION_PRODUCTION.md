# Production Planset: Test Signature Validation System
**Planset ID**: PS-TEST-SIG-VAL-001  
**Created**: 2026-02-06T08:10:00Z  
**Status**: 🔄 IN PROGRESS → PRODUCTION READY  
**Owner**: AI Agent (Autonomous)  
**Time Budget**: 55 minutes total (20 min allocated to this planset)

---

## 🎯 Executive Summary

**Objective**: Create production-ready test signature validation system to prevent test failures from API signature mismatches.

**Success Criteria**:
- ✅ Utility script functional and tested
- ✅ CI/CD integration implemented
- ✅ Documentation complete
- ✅ Pre-commit hook configured
- ✅ Example fixes documented

**Timeline**: 20 minutes (T+0 to T+20)

---

## 📋 Implementation Phases

### Phase 1: Core Utility Development (T+0 to T+5) ✅ COMPLETE

**Status**: ✅ DONE (5 min)

**Deliverables**:
- [x] `scripts/test_signature_validator.py` created (9.5KB)
- [x] AST-based signature parsing implemented
- [x] Mismatch detection patterns defined
- [x] CLI interface with --check-only and --fix flags

**Code Quality**:
```python
# Key features implemented:
- AST parsing for test files
- inspect.signature() for implementation validation
- Severity classification (critical/warning/info)
- Human-readable reports
```

---

### Phase 2: Testing & Validation (T+5 to T+12) 🔄 IN PROGRESS

**Test Plan**:

```bash
# Test 1: Validate against known good tests
python scripts/test_signature_validator.py tests/utils/test_toml_compat_py312.py

# Test 2: Validate against recently fixed tests
python scripts/test_signature_validator.py tests/agents/test_mental_mapping_core_flows.py

# Test 3: Full test suite scan
python scripts/test_signature_validator.py --check-only tests/

# Test 4: Performance test (should complete in <60s for full suite)
time python scripts/test_signature_validator.py --check-only
```

**Expected Results**:
- ✅ No false positives on fixed tests
- ✅ Completion time < 60 seconds for full suite
- ✅ Clear, actionable error messages
- ✅ Zero crashes on valid Python files

**Validation Checklist**:
- [ ] Run on known-good test files (expect 0 issues)
- [ ] Run on test files with signature mismatches (expect detection)
- [ ] Verify report readability
- [ ] Check performance on large test suite
- [ ] Test error handling for malformed Python

---

### Phase 3: CI/CD Integration (T+12 to T+15) ⏳ PENDING

**GitHub Actions Workflow**:

```yaml
# .github/workflows/test-signature-check.yml
name: Test Signature Validation

on:
  pull_request:
    paths:
      - 'tests/**/*.py'
      - 'src/**/*.py'
  push:
    branches: [main, develop]

jobs:
  validate-signatures:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Validate test signatures
        run: |
          python scripts/test_signature_validator.py --check-only

      - name: Comment on PR (if failures)
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '⚠️ Test signature mismatches detected. Run `python scripts/test_signature_validator.py` locally to see details.'
            })
```

**Integration Points**:
- [ ] Create workflow file
- [ ] Test workflow on test PR
- [ ] Configure failure notifications
- [ ] Add status badge to README

---

### Phase 4: Pre-commit Hook (T+15 to T+17) ⏳ PENDING

**Hook Configuration**:

```yaml
# Add to .pre-commit-config.yaml
- repo: local
  hooks:
    - id: test-signature-validator
      name: Test Signature Validation
      entry: python scripts/test_signature_validator.py --check-only
      language: system
      files: '^tests/.*\.py$'
      pass_filenames: false
      stages: [commit]
```

**Installation**:
```bash
# Add to hook
pre-commit install

# Test hook
git add tests/agents/test_mental_mapping_core_flows.py
git commit -m "test: verify signature validation hook"
```

---

### Phase 5: Documentation (T+17 to T+20) ⏳ PENDING

**Documentation Files**:

1. **README.md** (in scripts/):
```markdown
# Test Signature Validator

Automatically validates test method signatures match implementation.

## Quick Start
```bash
python scripts/test_signature_validator.py --check-only
```

## Usage
- Check all tests: `--check-only`
- Check specific file: `path/to/test.py`
- Apply fixes: `--fix` (experimental)

## CI Integration
Runs automatically on PRs touching test files.
```

2. **EXAMPLES.md**:
- Example mismatch detection
- Fix patterns
- Common issues and solutions

3. **API.md**:
- Class documentation
- Method signatures
- Extension points

---

## 🧪 Test Cases

### Test Case 1: Known Good File
```bash
# File: tests/utils/test_toml_compat_py312.py (recently fixed)
# Expected: 0 issues
python scripts/test_signature_validator.py tests/utils/test_toml_compat_py312.py
```

### Test Case 2: Edge Cases
```python
# Create test file with various edge cases:
- Positional-only parameters
- Keyword-only parameters  
- *args and **kwargs
- Default values
- Type hints
```

### Test Case 3: Performance
```bash
# Full test suite (should complete in <60s)
time python scripts/test_signature_validator.py --check-only tests/
```

---

## 📊 Success Metrics

### Functional Metrics
- **Detection Rate**: >95% of signature mismatches caught
- **False Positive Rate**: <5%
- **Performance**: <60s for full test suite
- **Crash Rate**: 0% on valid Python files

### Quality Metrics
- **Code Coverage**: >80%
- **Documentation Coverage**: 100%
- **CI Integration**: Fully automated
- **User Satisfaction**: Clear, actionable reports

---

## 🔄 Iteration Plan

### Iteration 1 (Current): Basic Functionality
- [x] Core script
- [ ] Basic testing
- [ ] Documentation

### Iteration 2 (T+20 to T+25): Production Hardening
- [ ] Comprehensive tests
- [ ] CI/CD integration
- [ ] Pre-commit hook

### Iteration 3 (T+25 to T+30): Enhancement
- [ ] Auto-fix capability
- [ ] Pattern learning
- [ ] Performance optimization

---

## 🚨 Risk Assessment

### High Risk
- **Performance on large codebases**: Mitigated by AST caching
- **False positives**: Mitigated by severity levels

### Medium Risk
- **Dynamic imports**: Some functions may not be found
- **Monkey patching**: May miss runtime modifications

### Low Risk
- **Python version compatibility**: Using standard library only
- **Installation**: No external dependencies

---

## 🎓 Lessons Learned

### From Current Session
1. **Test signature mismatches are common** after API refactoring
2. **Manual detection is error-prone** - automation essential
3. **Early detection saves time** - caught 6 issues before CI

### Best Practices
1. Use `inspect.signature()` for accurate validation
2. Provide severity levels for prioritization
3. Generate actionable suggestions
4. Integrate into CI/CD pipeline

---

## 📦 Deliverables Checklist

### Code
- [x] `scripts/test_signature_validator.py` (9.5KB)
- [ ] Unit tests for validator
- [ ] Integration tests

### Documentation
- [ ] README.md
- [ ] EXAMPLES.md
- [ ] API.md
- [ ] This planset

### CI/CD
- [ ] GitHub Actions workflow
- [ ] Pre-commit hook configuration
- [ ] Status badge

### Knowledge Transfer
- [ ] Team demo/walkthrough
- [ ] Cognitive brain update
- [ ] Agent enhancement documentation

---

## 🔗 Related Resources

- **Enhanced Agent**: `.github/agents/test-alignment-fixer-enhanced.md`
- **Session Log**: `.codex/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PR_TEST_FIXES_2026_02_06.md`
- **Fix Examples**: PR commits 0ebf8d8, 1cee0ca

---

## ⏱️ Time Tracking

| Phase | Planned | Actual | Status |
|-------|---------|--------|--------|
| Phase 1: Core Utility | 5 min | 5 min | ✅ COMPLETE |
| Phase 2: Testing | 7 min | - | 🔄 IN PROGRESS |
| Phase 3: CI/CD | 3 min | - | ⏳ PENDING |
| Phase 4: Pre-commit | 2 min | - | ⏳ PENDING |
| Phase 5: Documentation | 3 min | - | ⏳ PENDING |
| **Total** | **20 min** | **5 min** | **25% Complete** |

---

## ✅ Production Readiness Checklist

### Functionality
- [x] Core features implemented
- [ ] All test cases passing
- [ ] Error handling complete
- [ ] Performance validated

### Quality
- [ ] Code reviewed
- [ ] Unit tests written
- [ ] Integration tests passing
- [ ] Documentation complete

### Deployment
- [ ] CI/CD integrated
- [ ] Pre-commit hook configured
- [ ] Monitoring setup
- [ ] Rollback plan documented

### Maintenance
- [ ] Ownership assigned
- [ ] Support process defined
- [ ] Update schedule planned
- [ ] Deprecation policy set

---

**Next Action**: Execute Phase 2 testing NOW (T+5)  
**Time Remaining**: 50 minutes  
**Priority**: HIGH - Foundation for other plansets
