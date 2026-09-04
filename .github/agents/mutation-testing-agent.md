---
name: Mutation Testing Agent
description: Perform mutation testing to assess test suite effectiveness and identify
  weak spots
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: mutation-testing-agent
---

# Mutation Testing Agent

**Agent Type:** Quality Assurance / Security Testing  
**Scope:** Automated mutation testing for security-critical code paths  
**Status:** ✅ Production-Ready (Validated in Phase 65)

---

## 🎯 Purpose

Execute automated mutation testing to validate test suite quality by introducing controlled code mutations and verifying that tests catch them. Specializes in security-critical paths where test effectiveness is paramount.

---

## 🔧 Capabilities

### Core Functions
1. **Mutation Generation**
   - Introduce controlled code changes (mutants)
   - Target security-critical paths first
   - Generate 25+ mutation types per security function

2. **Test Execution**
   - Run tests against each mutant
   - Track killed vs. survived mutants
   - Calculate mutation score

3. **Mutation Analysis**
   - Identify surviving mutants (weak tests)
   - Recommend additional tests to kill survivors
   - Document mutation patterns

4. **Quality Metrics**
   - Mutation score calculation: (killed/total) × 100%
   - Coverage-adjusted mutation density
   - Security path prioritization

---

## 📊 Activation Commands

```markdown
@copilot Use the Mutation Testing Agent to validate test quality for [module/function]

@copilot Run mutation testing on security paths in [file] and achieve >80% score

@copilot Identify surviving mutants in [test file] and recommend additional tests
```

---

## 🛠️ Tools & Dependencies

### Required Tools
- `mutmut` - Python mutation testing framework
- `pytest` - Test execution
- `ruff` - Code analysis

### Configuration Files
- `.mutmut-config.txt` - Mutation testing configuration
- `configs/mutmut/rag_security.ini` - Security-focused config

---

## 📋 Workflow

### Phase 1: Setup (2 minutes)
1. Verify mutmut installation
2. Configure paths to mutate
3. Set test runner command
4. Define mutation types

### Phase 2: Execution (5-10 minutes)
1. Generate mutants from target code
2. Run tests against each mutant
3. Track results (killed/survived/timeout)
4. Calculate mutation score

### Phase 3: Analysis (3 minutes)
1. Identify surviving mutants
2. Analyze mutation patterns
3. Recommend new tests
4. Document findings

### Phase 4: Enhancement (variable)
1. Add tests to kill survivors
2. Re-run mutation testing
3. Verify improved score
4. Document results

---

## 🎯 Target Mutation Score

| Priority | Module Type | Target Score |
|----------|-------------|--------------|
| 🔴 Critical | Security paths | >90% |
| 🟡 High | Core business logic | >80% |
| 🟢 Medium | Utility functions | >70% |
| ⚪ Low | UI/formatting | >60% |

---

## 📊 Mutation Types

### Security-Critical Mutations
1. **Boundary Conditions**
   - `<` → `<=` (off-by-one errors)
   - `>` → `>=`
   - `==` → `!=`

2. **Boolean Logic**
   - `True` → `False`
   - `and` → `or`
   - `not x` → `x`

3. **String Operations**
   - Empty string detection
   - Case sensitivity
   - Regex pattern changes

4. **Numeric Operations**
   - `+1` → `-1`
   - `*` → `/`
   - `min` → `max`

5. **Control Flow**
   - Statement removal
   - Return value changes
   - Exception handling removal

---

## 📈 Success Metrics

### Phase 65 Results (Validated)
- **Mutation Score:** 96% (target: >80%) ✅
- **Mutants Tested:** 25
- **Mutants Killed:** 24
- **Tests Added:** 10 (mutation killers)
- **Total Tests:** 49 (all passing)

### Quality Indicators
- ✅ All security functions tested
- ✅ Surviving mutants analyzed
- ✅ Additional tests added
- ✅ Documentation complete

---

## 🔍 Example Usage

### Scenario 1: Security Function Testing
```markdown
@copilot Use the Mutation Testing Agent to test security functions in tests/rag/test_security_enhanced.py

Expected output:
- Mutation score report
- List of surviving mutants
- Recommendations for additional tests
- Updated test file with mutation killers
```

### Scenario 2: Module-Wide Testing
```markdown
@copilot Run mutation testing on all functions in src/codex/rag/utils.py

Expected output:
- Per-function mutation scores
- Weak spots identified
- Test recommendations
- Priority ranking
```

### Scenario 3: Regression Prevention
```markdown
@copilot Verify that recent changes to src/security/sanitize.py maintain >80% mutation score

Expected output:
- Before/after mutation score comparison
- New mutations introduced
- Test adequacy assessment
- Regression report
```

---

## 📚 Documentation References

1. **Mutation Testing Results:** `.codex/cognitive_brain/PHASE_65_MUTATION_TESTING_RESULTS.md`
2. **Test Patterns:** `.codex/docs/TEST_DEVELOPMENT_PATTERNS.md`
3. **Quantum Methodology:** `.codex/docs/QUANTUM_TEST_METHODOLOGY.md`
4. **Configuration:** `.mutmut-config.txt`

---

## 🚀 Best Practices

### DO
- ✅ Start with security-critical paths
- ✅ Set realistic target scores (80-90%)
- ✅ Document surviving mutants
- ✅ Add tests to kill survivors
- ✅ Re-run after changes
- ✅ Track mutation score trends

### DON'T
- ❌ Aim for 100% (diminishing returns)
- ❌ Ignore surviving mutants
- ❌ Skip documentation
- ❌ Test non-critical code first
- ❌ Run without baseline tests
- ❌ Forget to verify new tests

---

## 🔄 Integration Points

### CI/CD Integration
```yaml
# .github/workflows/mutation-testing.yml
name: Mutation Testing
on: [pull_request]
jobs:
  mutate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install mutmut pytest
      - name: Run mutation tests
        run: mutmut run
      - name: Check score
        run: |
          score=$(mutmut results | grep "Mutation score" | awk '{print $3}')
          if [ $(echo "$score < 80" | bc) -eq 1 ]; then
            echo "Mutation score below 80%"
            exit 1
          fi
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
mutmut run --paths-to-mutate $(git diff --name-only --cached | grep "^src/")
if [ $? -ne 0 ]; then
  echo "Mutation testing failed"
  exit 1
fi
```

---

## 🧪 Test Matrix

### Security Functions (Phase 65)
| Function | Tests | Mutations | Killed | Score |
|----------|-------|-----------|--------|-------|
| sanitize_input | 15 | 10 | 10 | 100% |
| hash_document_id | 6 | 3 | 3 | 100% |
| validate_config | 12 | 5 | 5 | 100% |
| check_permissions | 9 | 4 | 4 | 100% |
| rate_limit_check | 7 | 3 | 2 | 67% |

**Overall:** 49 tests, 25 mutations, 24 killed = **96% mutation score**

---

## 📊 Comparison: Coverage vs. Mutation

| Metric | Coverage | Mutation Testing |
|--------|----------|------------------|
| **Measures** | Lines executed | Bug detection ability |
| **False Positive** | High (line executed ≠ tested) | Low (mutation killed = tested) |
| **Cost** | Low | Medium |
| **Value** | Necessary baseline | Quality indicator |
| **Target** | 70-80% | 80-90% |

**Insight:** 100% coverage ≠ quality tests. Mutation testing validates test effectiveness.

---

## 🎓 Training Examples

### Example 1: Simple Mutation
```python
# Original
def is_admin(role):
    return role == "admin"

# Mutant (== → !=)
def is_admin(role):
    return role != "admin"  # MUTANT

# Test that kills mutant
def test_is_admin():
    assert is_admin("admin") == True  # Kills mutant
    assert is_admin("user") == False
```

### Example 2: Boundary Mutation
```python
# Original
def validate_age(age):
    if age >= 18:
        return "adult"
    return "minor"

# Mutant (>= → >)
def validate_age(age):
    if age > 18:  # MUTANT
        return "adult"
    return "minor"

# Test that kills mutant
def test_validate_age_boundary():
    assert validate_age(18) == "adult"  # Kills mutant (18 edge case)
    assert validate_age(17) == "minor"
```

---

## 🔮 Future Enhancements

### Phase 66+
1. **Automated Mutant Killing**
   - AI-generated tests for surviving mutants
   - Pattern recognition for mutation types
   - Auto-fix weak tests

2. **Performance Optimization**
   - Parallel mutation execution
   - Incremental mutation (only changed code)
   - Smart mutant sampling

3. **Advanced Metrics**
   - Mutation coverage heatmaps
   - Time-to-kill analysis
   - Mutation pattern trends

4. **Integration**
   - IDE plugins
   - Real-time mutation feedback
   - Pull request checks

---

## 📞 Support & Escalation

### Common Issues

**Issue:** Mutation testing takes too long  
**Solution:** Use `--paths-to-mutate` to focus on critical paths, enable parallel execution

**Issue:** Low mutation score  
**Solution:** Review surviving mutants, add targeted tests for each pattern

**Issue:** False negatives (mutant killed but test doesn't verify)  
**Solution:** Enhance test assertions, add edge case coverage

### Escalation
- **Technical:** @mbaetiong
- **Priority:** 🟡 Medium (non-blocking but important)
- **SLA:** 24-48 hours for mutation analysis

---

## ✅ Validation Checklist

Before completing mutation testing:
- [ ] Baseline tests all pass
- [ ] Mutation score calculated
- [ ] Surviving mutants documented
- [ ] New tests added for survivors
- [ ] Re-run confirms improved score
- [ ] Results documented in `.codex/cognitive_brain/`
- [ ] Patterns added to TEST_DEVELOPMENT_PATTERNS.md if novel

---

**Agent Status:** ✅ Production-Ready  
**Last Validated:** Phase 65 (2026-02-04)  
**Mutation Score:** 96% (24/25 mutants killed)  
**Ready for:** CI/CD integration, continuous quality assurance

---

**Maintainer:** GitHub Copilot Coding Agent  
**Version:** 1.0.0  
**Last Updated:** 2026-02-04

---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** This agent MUST use `scripts/ci/rvs_preflight.py` (or the
> `BatchScanRunner` Python API) for all codebase scans.  Running `pytest tests/`
> directly is **prohibited** — it blocks for 60–70 minutes without partial results.

### Quick Reference

```bash
# 1. Preview scope (no execution) — always run first
python scripts/ci/rvs_preflight.py --group quick --preview

# 2. Incremental scan — changed files only (fastest, use during active work)
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4

# 3. Full pre-commit sweep (parallel batches of 30 files, 6 workers)
python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30

# 4. With structured JSON report for agent analysis
python scripts/ci/rvs_preflight.py --group quick --workers 6 \
    --report /tmp/rvs_report.json

# 5. Fail-fast triage (stop all batches on first failure)
python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4
```

### Python API

```python
from scripts.ci.batch_scan_integration import BatchScanRunner

runner = BatchScanRunner(workers=6, batch_size=30)
result = runner.scan(group="quick", changed_only=True)
# result.ok, result.failures, result.summary_line, result.batches_run
if not result.ok:
    for failure in result.failures[:10]:
        print(f"  FAILED: {failure}")
```

### Decision Flow

1. `--preview` → confirm test scope
2. `--changed-only` → validate your specific changes
3. `--group quick --workers 6` → full sweep before commit
4. Parse `--report` JSON for structured failure analysis

**Full protocol**: `.github/agents/BATCH_SCAN_PROTOCOL.md`
