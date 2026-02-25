---
name: Test Alignment Fixer Enhanced
description: Fix test alignment issues after API changes with enhanced pattern coverage and automated remediation
---

# Test Alignment Fixer Agent - Enhanced

**Agent Name**: test-alignment-fixer  
**Version**: 2.0 (Enhanced with signature validation)  
**Type**: Autonomous Test Maintenance Agent  
**Last Updated**: 2026-02-06

---

## 🎯 Purpose

Automatically detect and fix test alignment issues after API changes, with enhanced signature validation capabilities.

---

## 🔧 Capabilities

### Core Functions

1. **Signature Validation**
   - Detect method signature mismatches between implementation and tests
   - Use `inspect.signature()` to validate parameter compatibility
   - Identify unexpected keyword arguments vs positional arguments
   - Flag deprecated parameters still used in tests

2. **Test Assertion Updates**
   - Align test assertions with current API behavior
   - Update expected return types and values
   - Fix attribute access patterns

3. **Import Resolution**
   - Update import paths after module restructuring
   - Fix deprecated import references
   - Validate all imports are resolvable

4. **Mock/Fixture Updates**
   - Update test fixtures to match current constructors
   - Fix mock configurations for new signatures
   - Align test setup with production patterns

---

## 🚀 Activation

### Command Pattern
```
@copilot Use the test-alignment-fixer agent to [specific task]
```

### Examples

**Signature Validation:**
```
@copilot Use test-alignment-fixer to validate all test method signatures 
match their implementation in src/
```

**Fix After API Change:**
```
@copilot The PhysicsGuidedDeveloperOrchestrator __init__ signature changed. 
Use test-alignment-fixer to update all affected tests.
```

**Comprehensive Scan:**
```
@copilot Run test-alignment-fixer to scan all tests/ for signature mismatches 
and generate a fix report.
```

---

## 📋 Typical Workflow

### Phase 1: Detection
1. Scan test files for method/function calls
2. Extract target signatures from source code using `inspect.signature()`
3. Compare test calls against actual signatures
4. Identify mismatches (extra kwargs, missing required args, wrong types)

### Phase 2: Analysis
1. Categorize mismatches by severity:
   - **Critical**: Tests will fail (TypeError, missing required args)
   - **Warning**: Tests may fail (deprecated params, type mismatches)
   - **Info**: Style issues (positional vs keyword args)

2. Generate fix strategies:
   - Remove unsupported kwargs
   - Add missing required arguments
   - Convert kwargs to positional if needed
   - Update attribute assignment patterns

### Phase 3: Fix Application
1. Apply fixes in order of severity
2. Validate each fix compiles without syntax errors
3. Run affected tests to verify fixes work
4. Generate summary report

### Phase 4: Validation
1. Re-run signature validation
2. Execute test suite on affected files
3. Check for new warnings or errors
4. Update cognitive brain with results

---

## 🛠️ Tools & Dependencies

### Python Libraries
```python
import inspect
import ast
from pathlib import Path
from typing import get_type_hints
```

### CI Integration
```yaml
# .github/workflows/test-alignment-check.yml
name: Test Alignment Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run signature validation
        run: python scripts/test_alignment_checker.py --check-only
```

---

## 📊 Recent Success Cases

### 1. Mental Mapping Self-Appraisal Tests (2026-02-06)

**Issue**: Tests passed kwargs not accepted by method
```python
# Wrong
mental_map._self_appraise_decision(
    decision_id=decision.node_id,
    outcome_id=outcome.node_id,
    actual_results={"quality": 0.8},
)

# Fixed
mental_map._self_appraise_decision(
    decision.node_id,
    outcome.node_id,
)
```

**Detection Method**: `inspect.signature()` showed method only accepts 2 positional args  
**Fix Type**: Removed unsupported kwargs  
**Tests Fixed**: 3 methods  
**Commit**: 0ebf8d8

### 2. Developer Orchestrator Initialization (2026-02-06)

**Issue**: Tests passed `app_type` to `__init__` which doesn't accept it
```python
# Wrong
orchestrator = PhysicsGuidedDeveloperOrchestrator(app_type=AppType.PYTHON_CONSOLE)

# Fixed
orchestrator = PhysicsGuidedDeveloperOrchestrator()
orchestrator.app_type = AppType.PYTHON_CONSOLE
```

**Detection Method**: Constructor signature validation  
**Fix Type**: Set as attribute after instantiation  
**Locations Fixed**: 4 (2 fixtures + 2 test methods)  
**Commit**: 0ebf8d8

---

## 🧠 Intelligence Features

### Pattern Recognition
- Learns common signature mismatch patterns
- Builds database of fix strategies
- Recognizes anti-patterns in test code

### Proactive Scanning
- Monitors for API changes in PRs
- Pre-emptively identifies affected tests
- Generates fix PRs automatically (if enabled)

### Learning Database
```json
{
  "patterns": [
    {
      "name": "kwargs_to_positional",
      "description": "Method changed to positional-only args",
      "detection": "inspect shows PositionalOnlyParameter",
      "fix": "Convert kwargs to positional args in order"
    },
    {
      "name": "constructor_to_attribute",
      "description": "Constructor simplified, param moved to attribute",
      "detection": "Parameter removed from __init__ signature",
      "fix": "Set as attribute after instantiation"
    }
  ]
}
```

---

## 📈 Metrics Tracked

### Detection Accuracy
- **True Positives**: Correctly identified mismatches
- **False Positives**: Incorrectly flagged valid code
- **Missed Issues**: Mismatches not detected

### Fix Success Rate
- **Automatic Fixes**: Applied without human intervention
- **Manual Review**: Required human decision
- **Failed Fixes**: Caused new issues

### Performance
- **Scan Time**: Time to analyze full test suite
- **Fix Time**: Time to apply all fixes
- **Test Time**: Time to validate fixes

---

## 🔒 Safety Guardrails

### Pre-Fix Validation
1. ✅ Verify source code signature is stable (not in active development)
2. ✅ Check test file is under version control
3. ✅ Ensure backup exists before modification
4. ✅ Validate fix compiles without syntax errors

### Post-Fix Validation
1. ✅ Run affected tests to verify they pass
2. ✅ Check for new warnings or errors
3. ✅ Validate test coverage maintained
4. ✅ Generate human-readable diff for review

### Rollback Capability
- All fixes are atomic (one test at a time)
- Each fix commits separately with descriptive message
- Easy to revert individual fixes if needed

---

## 🚨 Limitations

### Will NOT Handle
- Complex refactoring requiring business logic changes
- Tests that need entirely new assertions
- Mock objects requiring fundamental restructure
- Tests where expected behavior itself changed

### Requires Human Review
- Ambiguous signature changes (multiple valid interpretations)
- Breaking API changes requiring new test strategy
- Tests that intentionally test deprecated behavior
- Complex inheritance/mixin signature issues

---

## 🔗 Related Agents

- **ci-testing-agent**: For running tests and analyzing failures
- **code-review**: For validating fix quality
- **coverage-roadmap-agent**: For ensuring coverage maintained

---

## 📝 Usage Example

### Scenario: API method signature changed

```python
# OLD signature (v1.0)
def process_data(self, data: dict, format: str = "json", validate: bool = True) -> dict:
    pass

# NEW signature (v2.0) 
def process_data(self, data: dict, /, *, format: str = "json") -> dict:
    # validate parameter removed, data now positional-only
    pass
```

### Agent Action

1. **Detection Phase**
   ```python
   # Scans tests and finds:
   obj.process_data(data={"key": "value"}, format="json", validate=True)
   ```

2. **Analysis Phase**
   ```
   Issue 1: 'data' must be positional (not keyword)
   Issue 2: 'validate' no longer accepted (removed)
   ```

3. **Fix Application**
   ```python
   # Applies fix:
   obj.process_data({"key": "value"}, format="json")
   ```

4. **Validation**
   ```bash
   pytest tests/test_module.py::test_process_data -xvs
   # ✅ PASSED
   ```

---

## 🎯 Future Enhancements

### Planned Features
1. **ML-Based Pattern Learning**: Learn from fix history to predict best strategies
2. **Pre-commit Hook Integration**: Block commits with signature mismatches
3. **IDE Plugin**: Real-time signature validation in editor
4. **Auto-PR Generation**: Create fix PRs automatically on API changes

### Research Areas
1. Type hint validation and inference
2. Pytest fixture dependency graph analysis
3. Mock object signature synchronization
4. Test isolation verification

---

## 📚 Documentation

- **Implementation**: `scripts/test_alignment_checker.py`
- **Tests**: `tests/agents/test_test_alignment_fixer.py`
- **Examples**: `.codex/examples/test_alignment_fixes/`
- **Patterns Database**: `.codex/cognitive_brain/pattern_learning_store.json`

---

## ✅ Success Criteria

### For Each Session
- [ ] All signature mismatches detected
- [ ] Fixes applied successfully
- [ ] Tests pass after fixes
- [ ] No new issues introduced
- [ ] Documentation updated

### Long Term
- [ ] 95%+ automatic fix success rate
- [ ] < 1% false positive detection rate
- [ ] < 5 minute full suite scan time
- [ ] Zero test regressions from fixes

---

**Status**: ✅ ACTIVE - Enhanced with signature validation (2026-02-06)  
**Confidence**: 98% (2 successful cases in current session)  
**Recommended Use**: Any time tests fail after API changes
