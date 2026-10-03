# Enhancement PR Plan: E402/F821 Systematic Code Quality Refactoring

**Created**: 2026-02-17T17:30:00Z
**For**: Next PR after #3318 merge
**Estimated Effort**: 4-6 hours
**Priority**: P2 (Medium)

---

## 🎯 **PR Overview**

**Title**: `refactor: Systematic E402/F821 code quality improvements`

**Objective**: Resolve 2,665 code quality errors (E402 module imports, F821 undefined names) identified during PR #3318 analysis using systematic risk-based approach.

**Success Criteria**:
- ✅ All 2,665 errors resolved
- ✅ Zero test regressions
- ✅ Zero performance degradation
- ✅ Code review passed
- ✅ CodeQL clean

---

## 📋 **Complete Implementation Prompt**

**Use this exact prompt to create the enhancement PR**:

```markdown
@copilot Create a new PR to systematically resolve 2,665 E402/F821 code quality errors.

**Context**: PR #3318 successfully resolved all test failures and applied 2,824 formatting fixes. This PR focuses on the remaining code quality errors that were strategically deferred.

**Background**:
- **E402**: 2,485 errors (93.2%) - Module imports not at top of file
- **F821**: 160 errors (6.0%) - Undefined names
- **Others**: 20 errors (0.8%) - Miscellaneous
- **Analysis**: Complete (see `.codex/E402_F821_TRACKING_ISSUE.md`)
- **Strategy**: Risk-based phased approach

**Objectives**:

1. **Systematic Resolution** of all E402/F821 errors
2. **Zero Regressions** - maintain 100% test pass rate
3. **Performance Neutral** - no degradation
4. **Comprehensive Documentation** - lessons learned captured

**Implementation Phases**:

### Phase 1: Analysis & Categorization (30 min)

**Generate Error Inventory**:
```bash
# Create detailed error report
ruff check . --select E402,F821 --output-format=json > .codex/e402_f821_analysis.json

# Categorize by file
python scripts/analyze_code_quality_errors.py

# Group by risk level
python scripts/categorize_import_errors.py
```

**Deliverables**:
- Error inventory by file (CSV/JSON)
- Risk categorization (Low/Medium/High)
- Fix priority list

**Success Criteria**:
- [ ] All errors cataloged
- [ ] Risk levels assigned
- [ ] Priority order established

---

### Phase 2: Low-Risk Fixes (1-2 hours)

**Scope**: ~1,590 errors (60%)

**Examples**:
```python
# E402: Simple reordering
# Before:
"""Module docstring"""
x = 1
import os  # E402

# After:
"""Module docstring"""
import os

x = 1
```

```python
# F821: Missing stdlib import
# Before:
path = Path("/tmp")  # F821: undefined name 'Path'

# After:
from pathlib import Path

path = Path("/tmp")
```

**Approach**:
1. Fix in batches of 50-100 files
2. Run tests after each batch
3. Commit if passing
4. Document any issues

**Commands**:
```bash
# Fix batch
ruff check files_batch1.txt --fix --select E402,F821

# Test
pytest tests/ -v --tb=short

# Commit if passing
git add .
git commit -m "fix: Resolve E402/F821 in batch 1 (50 files)"
```

**Success Criteria**:
- [ ] 60% of errors fixed
- [ ] All tests passing
- [ ] No performance regression

---

### Phase 3: Medium-Risk Fixes (1-2 hours)

**Scope**: ~800 errors (30%)

**Examples**:
```python
# Conditional imports
# Before:
if some_condition:
    import expensive_module  # E402

# After:
from typing import TYPE_CHECKING
if TYPE_CHECKING or some_condition:
    import expensive_module
```

```python
# Third-party with fallback
# Before:
try:
    from optional_package import something  # E402
except ImportError:
    something = None

# After:
try:
    from optional_package import something
except ImportError:
    something = None
```

**Challenges**:
- Lazy imports may be intentional
- Optional dependencies need fallbacks
- Module initialization order matters

**Approach**:
1. Review each case individually
2. Preserve intentional patterns
3. Add TYPE_CHECKING guards where needed
4. Test thoroughly

**Success Criteria**:
- [ ] 30% of errors fixed
- [ ] Intentional patterns preserved
- [ ] All tests passing

---

### Phase 4: High-Risk Fixes (1 hour)

**Scope**: ~275 errors (10%)

**Examples**:
```python
# Circular dependency
# Before:
from module_a import ClassA  # Circular with module_b
from module_b import ClassB

# After:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from module_a import ClassA
from module_b import ClassB
```

**Strategies**:
- Use TYPE_CHECKING for type hints
- Defer imports to function scope if needed
- Refactor module structure if necessary
- Document intentional deviations

**Approach**:
1. One file at a time
2. Full test suite after each fix
3. Performance validation
4. Code review for each change

**Success Criteria**:
- [ ] 10% of errors fixed
- [ ] No circular dependencies
- [ ] All tests passing
- [ ] Performance validated

---

### Phase 5: Documentation & Cleanup (30 min)

**Update Configuration**:
```toml
# .ruff.toml
[lint]
select = ["E", "F", "I"]  # Enable all error types
ignore = []  # No exceptions

[lint.per-file-ignores]
# Document any intentional exceptions
"legacy/old_code.py" = ["E402"]  # Lazy loading required
```

**Pre-commit Hook**:
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.1.0
  hooks:
    - id: ruff
      args: [--fix, --select, E402,F821]
```

**Developer Guidelines**:
```markdown
# docs/contributing/code_quality.md

## Import Organization

1. All imports at top of file
2. Group in order: stdlib, third-party, local
3. Use TYPE_CHECKING for type-only imports
4. No import * statements
```

**Success Criteria**:
- [ ] Configuration updated
- [ ] Pre-commit hooks installed
- [ ] Guidelines documented
- [ ] Lessons learned captured

---

## 📊 **Validation Plan**

### Automated Tests
```bash
# Full test suite
pytest tests/ -v --cov=src --cov-report=html

# Performance benchmarks
python scripts/benchmark_suite.py

# Code quality check
ruff check . --select E402,F821
```

### Manual Verification
- [ ] Import organization consistent
- [ ] No circular dependencies
- [ ] TYPE_CHECKING used appropriately
- [ ] Lazy loading preserved where needed

### CI/CD Validation
- [ ] All workflow checks pass
- [ ] CodeQL clean
- [ ] Coverage maintained
- [ ] Performance benchmarks pass

---

## 🎯 **PR Template**

```markdown
## Objective

Systematic resolution of 2,665 code quality errors (E402/F821) identified during PR #3318 analysis.

## Changes

### Errors Resolved
- **E402**: 2,485 (module imports not at top)
- **F821**: 160 (undefined names)
- **Others**: 20 (miscellaneous)
- **Total**: 2,665

### Files Modified
- Low-Risk: ~950 files (60%)
- Medium-Risk: ~480 files (30%)
- High-Risk: ~165 files (10%)
- **Total**: ~1,595 files

### Approach

**Phase 1**: Analysis & Categorization (30 min)
**Phase 2**: Low-Risk Fixes (1-2 hours)
**Phase 3**: Medium-Risk Fixes (1-2 hours)
**Phase 4**: High-Risk Fixes (1 hour)
**Phase 5**: Documentation & Cleanup (30 min)

## Validation

- ✅ All tests pass (pytest: 100%)
- ✅ No performance regressions
- ✅ CodeQL clean
- ✅ Coverage maintained (90%)
- ✅ Code review passed

## Configuration Updates

- Updated `.ruff.toml` with E402/F821 rules
- Added pre-commit hooks
- Documented code quality guidelines

## Related

- **Original Analysis**: PR #3318
- **Strategy**: `.codex/E402_F821_TRACKING_ISSUE.md`
- **Risk Assessment**: Low-Medium (systematic approach)

## Testing

\`\`\`bash
# Run full test suite
pytest tests/ -v

# Check code quality
ruff check . --select E402,F821

# Performance validation
python scripts/benchmark_suite.py
\`\`\`

## Checklist

- [x] All E402 errors resolved
- [x] All F821 errors resolved
- [x] Zero test regressions
- [x] Zero performance degradation
- [x] Documentation updated
- [x] Pre-commit hooks added
- [x] Code review passed
- [x] CodeQL clean

## Follow-up

- Monitor for any edge case issues
- Gather feedback on import organization
- Consider additional linting rules

Ready for review! 🚀
```

---

## ⚙️ **Execution Commands**

### Initial Setup
```bash
# Create branch
git checkout main
git pull origin main
git checkout -b refactor/e402-f821-cleanup

# Verify baseline
pytest tests/ -v
ruff check . --select E402,F821 --output-format=json > baseline.json
```

### Phase Execution
```bash
# Phase 1: Analysis
python scripts/analyze_code_quality_errors.py
python scripts/categorize_import_errors.py

# Phase 2: Low-Risk
ruff check $(cat low_risk_files.txt) --fix --select E402,F821
pytest tests/ -v
git commit -am "fix: Resolve low-risk E402/F821 errors"

# Phase 3: Medium-Risk
# (Manual review + fixes)
pytest tests/ -v
git commit -am "fix: Resolve medium-risk E402/F821 errors"

# Phase 4: High-Risk
# (One-by-one with full validation)
pytest tests/ -v
git commit -am "fix: Resolve high-risk E402/F821 errors"

# Phase 5: Documentation
git commit -am "docs: Update code quality guidelines and configuration"
```

### Final Validation
```bash
# Comprehensive check
pytest tests/ -v --cov=src
ruff check .
python scripts/benchmark_suite.py

# Create PR
gh pr create --title "refactor: Systematic E402/F821 code quality improvements" \
  --body-file .codex/e402_f821_pr_description.md
```

---

## 📋 **Prerequisites**

### Before Starting
- [ ] PR #3318 merged
- [ ] All tests passing on main
- [ ] No pending PRs with conflicts
- [ ] Development environment setup

### Tools Required
- [ ] Python 3.12+
- [ ] ruff >= 0.1.0
- [ ] pytest >= 7.0
- [ ] git >= 2.30

### Knowledge Required
- [ ] Read `.codex/E402_F821_TRACKING_ISSUE.md`
- [ ] Read `.codex/PR3318_LESSONS_LEARNED.md`
- [ ] Understand Python import system
- [ ] Familiar with TYPE_CHECKING pattern

---

## ⚠️ **Risk Mitigation**

### Risk 1: Breaking Changes
- **Probability**: Low-Medium
- **Impact**: High
- **Mitigation**: Incremental commits with test validation
- **Rollback**: Git revert individual commits

### Risk 2: Performance Degradation
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Benchmark before/after each phase
- **Rollback**: Identify and revert problematic changes

### Risk 3: Circular Dependencies
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Use TYPE_CHECKING guards
- **Rollback**: Refactor module structure if needed

### Risk 4: Time Overrun
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**: Time-box each phase, defer if needed
- **Rollback**: Document remaining work for follow-up

---

## 📊 **Success Metrics**

### Quantitative
- [ ] 100% of E402 errors resolved (2,485/2,485)
- [ ] 100% of F821 errors resolved (160/160)
- [ ] 100% test pass rate maintained
- [ ] 0% performance regression
- [ ] 0% new linting errors introduced

### Qualitative
- [ ] Import organization improved
- [ ] Code readability enhanced
- [ ] Maintainability increased
- [ ] Developer experience improved
- [ ] Documentation comprehensive

---

## 🎯 **Expected Outcomes**

**If All Goes Well**:
- All 2,665 errors resolved
- Zero regressions
- Improved code quality metrics
- Better import organization
- Enhanced maintainability

**If Issues Found**:
- Document clearly
- Create targeted fixes
- Re-validate thoroughly
- Update timeline

**If Time Runs Short**:
- Complete critical phases (1-2)
- Document remaining work
- Create continuation plan
- Ensure safe state

---

## 📚 **Required Reading**

1. `.codex/E402_F821_TRACKING_ISSUE.md` - Full strategy
2. `.codex/PR3318_LESSONS_LEARNED.md` - Best practices
3. `.codex/PR3318_5PASS_SELF_REVIEW.md` - Quality standards
4. Python Import System Documentation
5. ruff Documentation (E402/F821 rules)

---

## 💡 **Tips for Success**

1. **Read Strategy First**: Understanding the full plan prevents issues
2. **Start Small**: Low-risk fixes build confidence
3. **Test Frequently**: Catch regressions early
4. **Document Decisions**: Future maintainers will thank you
5. **Use TYPE_CHECKING**: Solves many circular dependency issues
6. **Preserve Intent**: Don't break lazy loading patterns
7. **Communicate Clearly**: Update PR description as you progress

---

## ✅ **Completion Checklist**

### Pre-Work
- [ ] Read all required documentation
- [ ] Understand risk-based approach
- [ ] Set up development environment
- [ ] Create feature branch

### Execution
- [ ] Phase 1: Analysis complete
- [ ] Phase 2: Low-risk fixes applied
- [ ] Phase 3: Medium-risk fixes applied
- [ ] Phase 4: High-risk fixes applied
- [ ] Phase 5: Documentation updated

### Validation
- [ ] All tests passing
- [ ] Performance validated
- [ ] Code review passed
- [ ] CodeQL clean
- [ ] Documentation complete

### Completion
- [ ] PR created
- [ ] Reviewers assigned
- [ ] CI checks passing
- [ ] Ready for merge

---

**Plan Status**: ✅ **READY FOR EXECUTION**
**Estimated Duration**: 4-6 hours
**Priority**: P2 (Post PR #3318 merge)
**Risk Level**: Medium
**Success Probability**: 95% (High)

---

**Created by**: Copilot Agent (PR #3318 Session 2)
**Creation Date**: 2026-02-17T17:30:00Z
**Version**: 1.0
**Next Action**: Execute after PR #3318 merge
