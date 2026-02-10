# Phase 11.X GitHub Issues - Out-of-Scope Items

**Generated**: 2026-01-23T07:30:00Z  
**Context**: PR #2959 - Test failure resolution complete  
**Purpose**: Track identified out-of-scope improvements

---

## Issue 1: MLflow Import Warnings (122 instances)

**Priority**: HIGH  
**Labels**: `technical-debt`, `dependencies`, `testing`  
**Effort**: 1 hour

### Description

Test suite shows 122 instances of `ModuleNotFoundError: No module named 'mlflow'` warnings during test execution. While tests pass, this creates noise in test output and may confuse developers.

### Current Behavior

```
Exception occurred
Traceback (most recent call last):
  File "/path/to/src/codex_ml/tracking/mlflow_utils.py", line 52, in <module>
    import mlflow as _m
ModuleNotFoundError: No module named 'mlflow'
```

### Expected Behavior

- Optional dependencies should import gracefully without warnings
- OR mlflow should be added to test dependencies if required
- Test output should be clean and actionable

### Proposed Solution

**Option A** (Recommended): Suppress warnings for optional dependencies
```python
# src/codex_ml/tracking/mlflow_utils.py
try:
    import mlflow as _m
except ModuleNotFoundError:
    _m = None  # Silently handle optional dependency
```

**Option B**: Add mlflow to optional dependencies
```toml
# pyproject.toml
[project.optional-dependencies]
mlflow = ["mlflow>=2.0.0"]
```

### Acceptance Criteria

- [ ] No MLflow import warnings in test output
- [ ] All existing tests still pass
- [ ] Documentation updated if mlflow becomes optional
- [ ] Alternative tracking backend works without mlflow

### References

- PR #2959: Identified during test failure resolution
- File: `src/codex_ml/tracking/mlflow_utils.py`
- Pattern: 122 occurrences across test suite

---

## Issue 2: TODO/FIXME Technical Debt Tracking

**Priority**: MEDIUM  
**Labels**: `technical-debt`, `documentation`, `refactoring`  
**Effort**: 4-6 hours (with automation)

### Description

Repository contains 120+ TODO/FIXME comments scattered across codebase. Many may be obsolete or already resolved. Need systematic tracking and cleanup.

### Current Situation

```bash
# Identified via code scan
$ grep -r "TODO\|FIXME" --include="*.py" src/ | wc -l
120+
```

**Sample locations**:
- `src/codex/security_utils.py`
- `src/codex_ml/utils/checkpoint.py`
- `tools/codex_workflow_executor.py`
- And 117+ more files

### Proposed Solution

1. **Automated Scan**: Create script to extract all TODO/FIXME comments
2. **Categorization**: Group by priority and module
3. **Tracking**: Create sub-issues for actionable items
4. **Cleanup**: Remove obsolete markers

### Implementation Plan

```python
# scripts/scan_tech_debt.py
import ast
import re
from pathlib import Path

def extract_todos(file_path):
    """Extract TODO/FIXME comments with context."""
    with open(file_path) as f:
        content = f.read()
    
    pattern = r'(TODO|FIXME|XXX|HACK):\s*(.+)'
    matches = re.finditer(pattern, content)
    
    todos = []
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        todos.append({
            'file': file_path,
            'line': line_num,
            'type': match.group(1),
            'message': match.group(2).strip()
        })
    
    return todos

# Generate report
all_todos = []
for py_file in Path('src').rglob('*.py'):
    all_todos.extend(extract_todos(py_file))

# Output JSON for issue creation
import json
print(json.dumps(all_todos, indent=2))
```

### Acceptance Criteria

- [ ] Complete inventory of all TODO/FIXME comments
- [ ] Comments categorized by priority (P0/P1/P2)
- [ ] GitHub issues created for P0 items
- [ ] Obsolete comments removed
- [ ] Documentation updated with tracking process

### Milestones

1. **Phase 1**: Scan and inventory (Week 1)
2. **Phase 2**: Categorize and prioritize (Week 1)
3. **Phase 3**: Create issues for P0 items (Week 2)
4. **Phase 4**: Remove obsolete markers (Week 2)

---

## Issue 3: Test Collection Time Optimization

**Priority**: MEDIUM  
**Labels**: `performance`, `testing`, `developer-experience`  
**Effort**: 2 hours

### Description

Test collection and execution time varies significantly across modules. Some test files take notably longer to collect, impacting developer productivity.

### Current Metrics

```bash
# Observed collection times
pytest --collect-only -q  # ~5-10 seconds
pytest tests/ -v          # ~68 seconds for 117 tests
```

**Slow modules identified**:
- Complex test parametrization
- Heavy fixture initialization
- Unnecessary module imports during collection

### Proposed Solution

**Implement pytest-xdist for parallel execution**:

```bash
# Install
pip install pytest-xdist

# Run tests in parallel
pytest -n auto  # Use all CPU cores
pytest -n 4     # Use 4 workers

# Expected improvement: 40-60% faster
```

**Additional optimizations**:
1. Lazy fixture loading
2. Reduce parametrization complexity
3. Cache fixture results
4. Profile slow tests with `pytest --durations=10`

### Implementation Plan

1. Add pytest-xdist to dependencies
2. Update CI workflow to use parallel execution
3. Profile and optimize slowest 10 tests
4. Document parallel testing in CONTRIBUTING.md

### Acceptance Criteria

- [ ] pytest-xdist integrated
- [ ] Test execution time reduced by 40%+
- [ ] CI pipeline time reduced
- [ ] No test failures due to parallelization
- [ ] Documentation updated

### References

- Current test time: ~68 seconds for 117 tests
- Target: <40 seconds with parallel execution
- pytest-xdist docs: https://pytest-xdist.readthedocs.io/

---

## Issue 4: Docstring Coverage Improvements

**Priority**: LOW  
**Labels**: `documentation`, `code-quality`, `maintainability`  
**Effort**: Ongoing

### Description

Many functions and classes lack comprehensive docstrings, impacting code maintainability and developer onboarding.

### Current State

```bash
# Functions without docstrings
$ grep -r "def " src/ --include="*.py" | wc -l
~2000 functions

# Functions with docstrings (estimate)
$ grep -r '"""' src/ --include="*.py" | wc -l
~800 docstrings

# Estimated Coverage: 90%
```

### Target State

- 80%+ docstring coverage for public APIs
- 60%+ coverage for internal functions
- All modules have module-level docstrings
- Consistent docstring format (Google or NumPy style)

### Proposed Solution

**Create Docstring Generator Agent**:

```python
# .github/agents/docstring-generator/agent.py
import ast
import inspect

def generate_docstring(func_node):
    """Generate docstring from function signature."""
    params = []
    for arg in func_node.args.args:
        params.append(f"    {arg.arg}: Description")
    
    template = f'''"""
    Brief description of {func_node.name}.
    
    Args:
{chr(10).join(params)}
    
    Returns:
        Description of return value
    """'''
    
    return template
```

### Implementation Plan

1. **Phase 1**: Audit current docstring coverage
2. **Phase 2**: Create docstring generator agent
3. **Phase 3**: Generate docstrings for high-priority modules
4. **Phase 4**: Add docstring linting to pre-commit hooks
5. **Phase 5**: Ongoing improvement with each PR

### Acceptance Criteria

- [ ] Docstring coverage report generated
- [ ] Generator agent created and tested
- [ ] 10+ modules improved to 80%+ coverage
- [ ] Docstring linting added to CI
- [ ] CONTRIBUTING.md updated with standards

---

## Issue 5: Coverage Roadmap Execution Plan

**Priority**: HIGH  
**Labels**: `testing`, `code-quality`, `roadmap`  
**Effort**: Multi-week initiative

### Description

Current test coverage is ~27.5% with target of 70%. QA walkthrough identified 518 untested modules across `src/codex_ml/`, `src/codex/`, `agents/`, and `training/`.

### Current Coverage Analysis

```
Total Modules: ~2000
Tested Modules: ~500 (27.5%)
Untested Modules: 518 (documented)
Target Coverage: 90% (~1400 modules)
Gap: ~900 modules need tests
```

### Prioritization Strategy

**Tier 1** (Critical - 50 modules):
- Core business logic
- Security-sensitive code
- Public APIs
- High-complexity functions

**Tier 2** (Important - 150 modules):
- Integration points
- Data processing pipelines
- Configuration management
- Error handling

**Tier 3** (Standard - 700 modules):
- Utility functions
- Helper methods
- Internal APIs
- Low-complexity code

### Implementation Phases

**Phase 1** (Weeks 1-2): Foundation
- [ ] Prioritize top 50 Tier 1 modules
- [ ] Generate test templates
- [ ] Create 10 comprehensive test suites
- [ ] Establish test patterns

**Phase 2** (Weeks 3-6): Core Coverage
- [ ] Test 150 Tier 2 modules
- [ ] Achieve 50% coverage milestone
- [ ] Document test patterns
- [ ] Create test generation tools

**Phase 3** (Months 2-3): Comprehensive Coverage
- [ ] Test remaining 700 modules
- [ ] Achieve 70% coverage target
- [ ] Comprehensive integration tests
- [ ] Performance benchmarks

### Tooling & Automation

```python
# scripts/coverage_roadmap_executor.py
import coverage
from pathlib import Path

def identify_untested_modules():
    """Find modules with <50% coverage."""
    cov = coverage.Coverage()
    cov.load()
    
    untested = []
    for file_path in Path('src').rglob('*.py'):
        file_coverage = cov.analysis2(str(file_path))
        if file_coverage[2] < 0.5:  # <50% coverage
            untested.append({
                'file': file_path,
                'coverage': file_coverage[2],
                'priority': calculate_priority(file_path)
            })
    
    return sorted(untested, key=lambda x: x['priority'], reverse=True)
```

### Acceptance Criteria

- [ ] Roadmap document created
- [ ] Top 50 modules prioritized
- [ ] 10 modules tested (Phase 1 milestone)
- [ ] Test generation tools created
- [ ] Coverage tracking dashboard
- [ ] Weekly progress reports

### References

- QA Walkthrough: `.codex/qa_walkthrough/coverage_analysis.json`
- Current coverage: ~27.5%
- Target Coverage: 90%
- Gap: 518 documented untested modules

---

## Issue 6: Pre-commit Integration Documentation Enhancement

**Priority**: HIGH  
**Labels**: `documentation`, `developer-experience`, `onboarding`  
**Effort**: 1 hour

### Description

Pre-commit hooks have been integrated (PR #2959) but need comprehensive documentation for developers, including troubleshooting, customization, and best practices.

### Current State

- Basic installation instructions in CONTRIBUTING.md
- Hook configurations in `.pre-commit-config.yaml`
- Missing: Troubleshooting, performance tips, customization guide

### Required Documentation

**1. Comprehensive Installation Guide**
```markdown
## Setting Up Pre-commit Hooks

### First-time Setup
\`\`\`bash
# Install pre-commit
pip install pre-commit

# Install hooks (one-time setup)
pre-commit install

# Verify installation
pre-commit run --all-files
\`\`\`

### Updating Hooks
\`\`\`bash
# Update to latest versions
pre-commit autoupdate

# Re-run installation
pre-commit install --install-hooks
\`\`\`
```

**2. Troubleshooting Guide**
- Common errors and solutions
- Performance optimization tips
- Skipping specific hooks
- Debugging hook failures

**3. Customization Guide**
- Adding custom hooks
- Modifying existing hooks
- Hook-specific configuration
- Per-repository settings

**4. Best Practices**
- When to use `--no-verify`
- Handling large commits
- Team workflows
- CI integration

### Implementation Plan

1. Create `docs/dev/PRE_COMMIT_GUIDE.md`
2. Add troubleshooting section
3. Document all 18 active hooks
4. Add examples and screenshots
5. Link from CONTRIBUTING.md

### Acceptance Criteria

- [ ] Comprehensive guide created
- [ ] All hooks documented
- [ ] Troubleshooting section complete
- [ ] Examples for common scenarios
- [ ] Linked from main docs
- [ ] Reviewed by team

---

## Summary Dashboard

| Issue | Priority | Effort | Status | Owner |
|-------|----------|--------|--------|-------|
| 1. MLflow Warnings | HIGH | 1h | 📋 Ready | TBD |
| 2. TODO/FIXME Debt | MEDIUM | 4-6h | 📋 Ready | TBD |
| 3. Test Optimization | MEDIUM | 2h | 📋 Ready | TBD |
| 4. Docstring Coverage | LOW | Ongoing | 📋 Ready | TBD |
| 5. Coverage Roadmap | HIGH | Multi-week | 📋 Ready | TBD |
| 6. Pre-commit Docs | HIGH | 1h | 📋 Ready | TBD |

**Total Issues**: 6  
**Ready for Creation**: 6  
**Estimated Total Effort**: 8-10 hours + ongoing work

---

## Creating These Issues

To create these issues in GitHub:

```bash
# Option 1: Use GitHub CLI
for i in {1..6}; do
  gh issue create --title "$(extract_title issue_$i)" \
                  --body "$(extract_body issue_$i)" \
                  --label "$(extract_labels issue_$i)"
done

# Option 2: Use GitHub UI
# Copy each issue section above into GitHub issue creation form

# Option 3: Use GitHub API
curl -X POST https://api.github.com/repos/Aries-Serpent/_codex_/issues \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d @issue_payload.json
```

---

**Generated by**: copilot-swe-agent[bot]  
**Context**: PR #2959 - Phase 11.X Implementation  
**Last Updated**: 2026-01-23T07:30:00Z
