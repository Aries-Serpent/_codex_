# Test Coverage Plan: Path to 100%

**Document Version:** 1.0  
**Created:** 2026-01-09  
**Branch:** copilot/sub-pr-2750-c9b72a6c-e06f-4d68-b2cc-4e9352e363d2  
**Status:** 📋 Planning Phase  
**Goal:** Achieve 90% minimum test coverage, 100% stretch goal

---

## Executive Summary

This document outlines a comprehensive, phased approach to achieving 100% test coverage across the Codex ML repository. Based on baseline analysis, current coverage is **30.80%** for actively tested modules, with significant gaps in utility modules, context discovery, session management, and validators.

**Key Objectives:**
1. Establish baseline coverage metrics for all source modules
2. Prioritize coverage improvements by criticality (P0, P1, P2)
3. Create reusable test patterns and templates
4. Implement CI/CD coverage enforcement
5. Achieve 90% coverage minimum across all modules

---

## Phase 1: Baseline Assessment (COMPLETE)

### Current Coverage Status

**Tested Modules (48 tests):**
- `src/codex/utils/config_loader.py`: **73.86%** (136/181 statements, 52/60 branches)
  - ✅ Good coverage on core functionality
  - ❌ Gaps: Error handling paths (37-41, 59-69), edge cases (251-265)
  
- `src/bridge_manager.py`: **Not measured** (module not imported in tests)
  - Note: Tests exist but coverage not captured

**Untested Modules (0% coverage):**
- `src/codex/utils/context_discovery.py`: 63 statements, 16 branches
- `src/codex/utils/session_cache.py`: 87 statements, 14 branches
- `src/codex/utils/subprocess.py`: 6 statements
- `src/codex/utils/validators.py`: 115 statements, 36 branches

### Gap Analysis

| Module | Current | Target | Gap | Priority | Complexity |
|--------|---------|--------|-----|----------|------------|
| config_loader.py | 73.86% | 95% | 21.14% | P1 | Medium |
| bridge_manager.py | ?% | 95% | ? | P0 | High |
| context_discovery.py | 0% | 90% | 90% | P2 | Medium |
| session_cache.py | 0% | 95% | 95% | P1 | High |
| subprocess.py | 0% | 100% | 100% | P2 | Low |
| validators.py | 0% | 95% | 95% | P1 | Medium |

---

## Phase 2: Strategic Coverage Planning

### Priority Classification

**P0 (Critical) - Security & Authentication:**
- `src/bridge_manager.py` - IPC security, authentication, audit trail
- Any modules handling tokens, credentials, permissions
- **Target:** 95%+ coverage, comprehensive security tests

**P1 (High) - Business Logic & Configuration:**
- `src/codex/utils/config_loader.py` - Configuration management
- `src/codex/utils/session_cache.py` - Session state management
- `src/codex/utils/validators.py` - Input validation and sanitization
- Zendesk orchestrators and business rule engines
- **Target:** 90%+ coverage, integration tests included

**P2 (Medium) - Utilities & Helpers:**
- `src/codex/utils/context_discovery.py` - Context utilities
- `src/codex/utils/subprocess.py` - Process management
- Helper functions and data transformations
- **Target:** 85%+ coverage, unit tests sufficient

### Test Strategy by Module Type

**1. Security Modules (P0)**
```python
# Test Pattern: Security-Critical Code
def test_security_feature_with_valid_input():
    """Happy path with valid credentials."""
    
def test_security_feature_with_invalid_input():
    """Reject invalid credentials."""
    
def test_security_feature_timing_attack_resistance():
    """Ensure constant-time operations."""
    
def test_security_feature_audit_logging():
    """Verify security events are logged."""
    
def test_security_feature_permission_enforcement():
    """Ensure proper permission checks."""
```

**2. Business Logic Modules (P1)**
```python
# Test Pattern: Business Rules
def test_business_rule_normal_case():
    """Test typical business scenario."""
    
def test_business_rule_edge_cases():
    """Test boundary conditions."""
    
@pytest.mark.parametrize("input,expected", [...])
def test_business_rule_variations(input, expected):
    """Test multiple scenarios."""
    
def test_business_rule_error_handling():
    """Test exception paths."""
    
def test_business_rule_integration():
    """Test with real dependencies."""
```

**3. Utility Modules (P2)**
```python
# Test Pattern: Utilities
def test_utility_function_happy_path():
    """Test with valid input."""
    
def test_utility_function_edge_cases():
    """Test empty, None, boundary values."""
    
def test_utility_function_error_handling():
    """Test exception cases."""
```

---

## Phase 3: Module-by-Module Implementation Plan

### Iteration 1: P0 Modules (Security-Critical)

**Target:** Bridge Manager (src/bridge_manager.py)
- **Current:** ?% (tests exist but not measured correctly)
- **Target:** 95%+
- **Tasks:**
  1. Fix coverage measurement (ensure module imported)
  2. Add missing tests for error paths (WRITE_ERROR, READ_ERROR events)
  3. Add timeout scenario tests
  4. Add non-blocking I/O tests
  5. Add socket mode tests (currently only pipe mode tested)
  
**Estimated Tests:** +8 tests (26 total)
**Timeline:** 1 day

### Iteration 2: P1 Modules (Business Logic)

**Target:** Config Loader (src/codex/utils/config_loader.py)
- **Current:** 73.86%
- **Target:** 95%+
- **Tasks:**
  1. Test error handling paths (lines 37-41, 59-69)
  2. Test fallback resolution (lines 251-265)
  3. Test environment variable overrides (lines 280-288)
  4. Test edge cases with malformed configs
  5. Test circular reference detection

**Estimated Tests:** +12 tests (42 total for config_loader)
**Timeline:** 2 days

**Target:** Session Cache (src/codex/utils/session_cache.py)
- **Current:** 0%
- **Target:** 95%+
- **Tasks:**
  1. Create comprehensive test suite from scratch
  2. Test cache initialization and cleanup
  3. Test cache hit/miss scenarios
  4. Test cache expiration and eviction
  5. Test concurrent access (if applicable)
  6. Test serialization/deserialization
  7. Test error recovery

**Estimated Tests:** +20 tests (NEW)
**Timeline:** 3 days

**Target:** Validators (src/codex/utils/validators.py)
- **Current:** 0%
- **Target:** 95%+
- **Tasks:**
  1. Test each validation function
  2. Test with valid inputs (happy path)
  3. Test with invalid inputs (rejection)
  4. Test edge cases (empty, None, boundary values)
  5. Test error messages are informative
  6. Property-based testing for validators

**Estimated Tests:** +30 tests (NEW)
**Timeline:** 3 days

### Iteration 3: P2 Modules (Utilities)

**Target:** Context Discovery (src/codex/utils/context_discovery.py)
- **Current:** 0%
- **Target:** 90%+
- **Tasks:**
  1. Test context extraction from various sources
  2. Test context merging and conflict resolution
  3. Test caching behavior
  4. Test error handling for missing context

**Estimated Tests:** +15 tests (NEW)
**Timeline:** 2 days

**Target:** Subprocess (src/codex/utils/subprocess.py)
- **Current:** 0%
- **Target:** 100%
- **Tasks:**
  1. Test process execution (simple utility, should be straightforward)
  2. Test stdout/stderr capture
  3. Test timeout handling
  4. Test error conditions

**Estimated Tests:** +5 tests (NEW)
**Timeline:** 1 day

### Iteration 4: Integration Tests

**Cross-Module Integration:**
- Config loader + Session cache
- Bridge manager + Context discovery
- Validators + Config loader

**Tasks:**
1. Create integration test suite
2. Test real-world workflows
3. Test error propagation across modules
4. Test performance under load

**Estimated Tests:** +15 integration tests
**Timeline:** 3 days

### Iteration 5: Edge Cases & Property-Based Testing

**Property-Based Testing:**
- Use Hypothesis for validators
- Generate random configs for config_loader
- Fuzz test bridge manager with random messages

**Edge Cases:**
- Extremely large inputs
- Unicode and encoding edge cases
- Concurrent access patterns
- Resource exhaustion scenarios

**Estimated Tests:** +10 property-based tests
**Timeline:** 2 days

---

## Phase 4: Test Infrastructure & Tooling

### Coverage Measurement Setup

**1. Update pytest Configuration**

Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=src",
    "--cov=agents",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-report=json",
    "--cov-fail-under=90",
]
```

**2. Create Coverage Scripts**

```bash
# scripts/coverage/run_coverage.sh
#!/bin/bash
pytest --cov=src --cov=agents \
       --cov-report=html:htmlcov \
       --cov-report=json:coverage.json \
       --cov-report=term-missing \
       --cov-fail-under=90
```

```bash
# scripts/coverage/check_coverage.py
#!/usr/bin/env python3
"""Check coverage and report gaps."""
import json
import sys

with open('coverage.json') as f:
    data = json.load(f)

gaps = []
for file, info in data['files'].items():
    coverage = info['summary']['percent_covered']
    if coverage < 90:
        gaps.append((file, coverage))

if gaps:
    print("❌ Coverage gaps found:")
    for file, coverage in sorted(gaps, key=lambda x: x[1]):
        print(f"  {file}: {coverage:.1f}%")
    sys.exit(1)
else:
    print("✅ All files meet 90% coverage threshold")
```

### Test Templates

**Create Test Template Generator:**

```python
# scripts/coverage/generate_test_template.py
#!/usr/bin/env python3
"""Generate test template for a module."""
import ast
import sys
from pathlib import Path

def generate_test_template(module_path: Path) -> str:
    """Generate pytest template for a module."""
    with open(module_path) as f:
        tree = ast.parse(f.read())
    
    functions = [node.name for node in ast.walk(tree) 
                 if isinstance(node, ast.FunctionDef)]
    classes = [node.name for node in ast.walk(tree) 
               if isinstance(node, ast.ClassDef)]
    
    template = f'''"""Tests for {module_path.name}"""

import pytest
from {module_path.stem} import *


'''
    
    for func in functions:
        template += f'''def test_{func}_happy_path():
    """Test {func} with valid input."""
    # TODO: Implement test
    pass


def test_{func}_error_handling():
    """Test {func} error handling."""
    # TODO: Implement test
    pass


'''
    
    return template

if __name__ == "__main__":
    module_path = Path(sys.argv[1])
    print(generate_test_template(module_path))
```

---

## Phase 5: CI/CD Integration

### GitHub Actions Workflow

**Create:** `.github/workflows/test-coverage.yml`

```yaml
name: Test Coverage

on:
  pull_request:
    branches: [main, 0D_base_]
  push:
    branches: [main, 0D_base_]

jobs:
  coverage:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e '.[dev]'
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov=agents \
                 --cov-report=html \
                 --cov-report=json \
                 --cov-report=term-missing \
                 --cov-fail-under=90
      
      - name: Upload coverage reports
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: |
            htmlcov/
            coverage.json
      
      - name: Comment PR with coverage
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}
          MINIMUM_GREEN: 95
          MINIMUM_ORANGE: 85
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: check-coverage
      name: Check test coverage
      entry: python scripts/coverage/check_coverage.py
      language: system
      pass_filenames: false
      always_run: true
```

---

## Phase 6: Continuous Monitoring

### Coverage Dashboard

**Tool:** Coverage.py HTML reports + CI artifacts

**Metrics to Track:**
- Overall coverage percentage
- Per-module coverage
- Coverage trends over time
- Uncovered lines count
- Branch coverage percentage

### Monthly Review Process

1. **Generate Coverage Report:** Run full suite with coverage
2. **Identify Regressions:** Compare with previous month
3. **Prioritize Gaps:** Focus on P0/P1 modules below threshold
4. **Action Items:** Create issues for coverage improvements
5. **Celebrate Wins:** Recognize modules reaching 95%+

---

## Implementation Timeline

### Phase 1: Foundation (Week 1)
- ✅ Baseline assessment (COMPLETE)
- [ ] Coverage infrastructure setup
- [ ] Test template creation
- [ ] CI/CD integration

### Phase 2: P0 Security (Week 2)
- [ ] Bridge manager coverage to 95%
- [ ] Security module comprehensive tests
- [ ] Audit trail verification tests

### Phase 3: P1 Business Logic (Weeks 3-4)
- [ ] Config loader to 95%
- [ ] Session cache test suite (0% → 95%)
- [ ] Validators test suite (0% → 95%)

### Phase 4: P2 Utilities (Week 5)
- [ ] Context discovery tests
- [ ] Subprocess tests
- [ ] Remaining utility modules

### Phase 5: Integration & Edge Cases (Week 6)
- [ ] Cross-module integration tests
- [ ] Property-based testing
- [ ] Performance and stress tests

### Phase 6: Production Hardening (Week 7)
- [ ] Coverage enforcement in CI
- [ ] Documentation completion
- [ ] Dashboard and monitoring setup

---

## Success Metrics

### Coverage Targets

| Metric | Current | Week 3 | Week 5 | Week 7 (Goal) |
|--------|---------|--------|--------|---------------|
| **Overall Coverage** | 30.80% | 60% | 80% | **90%+** |
| **P0 Modules** | ?% | 90% | 95% | **95%+** |
| **P1 Modules** | 24.6% | 75% | 90% | **90%+** |
| **P2 Modules** | 0% | 50% | 85% | **85%+** |
| **Branch Coverage** | Low | 70% | 85% | **85%+** |

### Quality Metrics

- **Test Count:** 48 → 150+ tests
- **Test Execution Time:** <5 minutes for full suite
- **Flakiness Rate:** <1% (deterministic tests)
- **Maintenance Burden:** Low (reusable patterns)

---

## Risk Mitigation

### Risks & Mitigation Strategies

**1. Time Overruns**
- **Risk:** Coverage work takes longer than estimated
- **Mitigation:** Prioritize P0/P1, defer P2 if needed
- **Contingency:** Accept 85% coverage for P2 modules

**2. Flaky Tests**
- **Risk:** New tests introduce non-determinism
- **Mitigation:** Use fixtures, mocks, deterministic data
- **Contingency:** Run tests 3x to detect flakiness

**3. Coverage vs. Quality Tradeoff**
- **Risk:** High coverage with low-quality tests
- **Mitigation:** Code review all tests, enforce patterns
- **Contingency:** Quality over quantity (90% quality > 100% quantity)

**4. Maintenance Overhead**
- **Risk:** Tests become burden to maintain
- **Mitigation:** Create reusable fixtures and patterns
- **Contingency:** Consolidate similar tests

---

## Reusable Patterns & Templates

### Pattern 1: Config Loading Tests
```python
@pytest.fixture
def config_dir(tmp_path):
    """Create temporary config directory."""
    (tmp_path / "conf").mkdir()
    return tmp_path / "conf"

def test_config_loads(config_dir):
    """Test config loads successfully."""
    config_file = config_dir / "test.yaml"
    config_file.write_text("key: value")
    
    cfg = load_config("test", config_dir=config_dir)
    assert cfg["key"] == "value"
```

### Pattern 2: Security Testing
```python
def test_security_feature_with_constant_time():
    """Ensure constant-time comparison."""
    import time
    
    valid = "correct_token"
    invalid = "wrong_token"
    
    start = time.perf_counter()
    result1 = authenticate(valid)
    time1 = time.perf_counter() - start
    
    start = time.perf_counter()
    result2 = authenticate(invalid)
    time2 = time.perf_counter() - start
    
    # Timing difference should be minimal (allow 10% variance)
    assert abs(time1 - time2) / max(time1, time2) < 0.1
```

### Pattern 3: Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_validator_handles_any_string(input_str):
    """Test validator with any possible string."""
    result = validate_string(input_str)
    assert isinstance(result, bool)
```

---

## Cognitive Brain Integration

### Patterns Learned

1. **Baseline Assessment Pattern:** Measure before improving
2. **Prioritization Matrix:** P0/P1/P2 based on criticality
3. **Phased Implementation:** Small, incremental improvements
4. **Template Generation:** Reduce manual test writing
5. **CI/CD Enforcement:** Automate quality gates

### Reusable Utilities

1. **Coverage Report Generator:** `scripts/coverage/run_coverage.sh`
2. **Coverage Gap Analyzer:** `scripts/coverage/check_coverage.py`
3. **Test Template Generator:** `scripts/coverage/generate_test_template.py`
4. **Coverage Dashboard:** HTML reports + GitHub Actions artifacts

---

## Next Steps

1. **Immediate (Day 1):**
   - Fix bridge_manager coverage measurement
   - Create coverage infrastructure scripts
   - Set up CI/CD workflow

2. **Short-term (Week 1):**
   - Implement P0 module tests (bridge_manager to 95%)
   - Create test templates for P1 modules
   - Begin session_cache test suite

3. **Medium-term (Weeks 2-4):**
   - Complete P1 module coverage (config_loader, session_cache, validators)
   - Implement P2 module tests
   - Add integration tests

4. **Long-term (Weeks 5-7):**
   - Property-based testing
   - Performance and stress tests
   - Coverage enforcement and monitoring

---

**Document Maintainer:** GitHub Copilot  
**Last Updated:** 2026-01-09  
**Next Review:** After Phase 1 completion
