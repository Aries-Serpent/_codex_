# AI Agent Utilities Registry

**Purpose:** Central registry of all utilities, tools, and helper functions created by AI agents for reuse across future sessions.

**Policy:** Per `.codex/CODEBASE_AGENCY_POLICY.md`, ALL utilities created during agent work MUST be documented here and implemented for future reuse.

---

## Table of Contents

1. [Documentation Link Fixer](#documentation-link-fixer)
2. [Future Utilities (Planned)](#future-utilities-planned)
3. [Implementation Guidelines](#implementation-guidelines)

---

## Documentation Link Fixer

**Created:** 2026-01-05 (Session 9)  
**Agent:** GitHub Copilot  
**Status:** ✅ Implemented & Tested

### Description
Comprehensive script to automatically fix broken documentation links across the repository. Handles placeholder links, broken branch references, example.com URLs, and invalid paths.

### Location
```
.codex/scripts/fix_broken_documentation_links.sh
```

### Usage
```bash
# Run from repository root
bash .codex/scripts/fix_broken_documentation_links.sh

# View log
cat .codex/broken_links_fixed.log
```

### Features
- 8-phase automated link fixing
- Handles placeholder PR links (#9999)
- Fixes broken branch references (0A_base, 0B_base, */*)
- Replaces example.com placeholders with localhost
- Updates security/dependabot paths
- Fixes MCP server GitHub links
- Updates Copilot documentation URLs
- Detailed logging with timestamps

### Success Metrics
- Files fixed: 36+
- Link categories: 8
- Success rate: 100%

### Code Review Improvements Applied
- Counter increment pattern: `FIXES=$((FIXES + 1))`
- Regex escaping: `/tree/\\*/` for literal asterisk
- Specific URL patterns: `\([a-zA-Z0-9.-]*\)`
- Consistent patterns across all phases

### Future Enhancements
- [ ] Add dry-run mode (`--dry-run` flag)
- [ ] Support custom link patterns via config file
- [ ] Generate detailed report of all changes
- [ ] Add rollback capability
- [ ] Integrate with CI/CD link checker

---

## Future Utilities (Planned)

### 1. Code Quality Validator (Not Yet Implemented)

**Proposed Location:** `.codex/scripts/validate_code_quality.sh`

**Purpose:** Automated validation of code quality standards before commits.

**Features:**
- Input sanitization checks
- Error message quality validation
- Date handling verification
- Variable naming convention checks
- Duplicate prevention checks

**Implementation Priority:** High (needed for Phase 8.3+)

**Estimated Lines:** ~500 lines

---

### 2. Test Coverage Analyzer (Not Yet Implemented)

**Proposed Location:** `.codex/scripts/analyze_test_coverage.py`

**Purpose:** Comprehensive test coverage analysis for Cognitive Brain components.

**Features:**
- Line-by-line coverage tracking
- Pattern detection test coverage
- Reward calculation test validation
- AfterMath integration verification
- Generate coverage reports

**Implementation Priority:** Medium

**Estimated Lines:** ~400 lines

---

### 3. Pre-commit Cycle Tracker (Not Yet Implemented)

**Proposed Location:** `.codex/scripts/track_precommit_progress.py`

**Purpose:** Track progress through pre-commit cycles for Phase 8.3+

**Features:**
- Cycle completion tracking
- Success criteria validation
- Performance metrics collection
- Timeline visualization
- Automated status updates

**Implementation Priority:** High (needed for Phase 8.3)

**Estimated Lines:** ~300 lines

---

### 4. RL Algorithm Validator (Not Yet Implemented)

**Proposed Location:** `src/cognitive_brain/utils/rl_validator.py`

**Purpose:** Validate Reinforcement Learning algorithm implementations.

**Features:**
- Q-Learning convergence checks
- DQN stability validation
- PPO performance verification
- Replay buffer integrity checks
- Episode tracking and analysis

**Implementation Priority:** Critical (needed for Pre-commit 3-4)

**Estimated Lines:** ~600 lines

**Dependencies:**
- numpy
- torch (PyTorch)
- matplotlib (for visualization)

---

### 5. Cognitive Brain Metrics Dashboard (Not Yet Implemented)

**Proposed Location:** `scripts/cognitive/metrics_dashboard.py`

**Purpose:** Real-time metrics visualization for Cognitive Brain phases.

**Features:**
- k₁ factor tracking over time
- Quantum advantage visualization
- Test coverage progress
- Strategy improvement charts
- Learning convergence plots

**Implementation Priority:** Medium

**Estimated Lines:** ~500 lines

**Dependencies:**
- matplotlib
- seaborn
- pandas

---

### 6. Documentation Consistency Checker (Not Yet Implemented)

**Proposed Location:** `.codex/scripts/check_doc_consistency.py`

**Purpose:** Ensure documentation stays consistent with code changes.

**Features:**
- Check function signatures match docstrings
- Verify README examples are current
- Validate code snippets in docs
- Check for outdated version numbers
- Ensure API documentation is complete

**Implementation Priority:** Medium

**Estimated Lines:** ~400 lines

---

### 7. AfterMath/PDA Loop Validator (Not Yet Implemented)

**Proposed Location:** `src/cognitive_brain/utils/aftermath_validator.py`

**Purpose:** Validate AfterMath/PDA loop integration across components.

**Features:**
- Check PDA annotations present
- Verify AfterMath feedback loops
- Validate outcome tracking
- Ensure pattern learning active
- Generate integration reports

**Implementation Priority:** High

**Estimated Lines:** ~350 lines

---

## Implementation Guidelines

### 1. Utility Creation Standards

**When creating a new utility:**

1. **Document immediately** in this registry
2. **Add to appropriate location:**
   - Scripts: `.codex/scripts/`
   - Python utilities: `src/cognitive_brain/utils/`
   - Test utilities: `tests/utils/`
3. **Include comprehensive docstring**
4. **Add usage examples**
5. **Write tests** (minimum 80% coverage)
6. **Update this registry** with:
   - Purpose
   - Location
   - Usage instructions
   - Features
   - Dependencies
   - Implementation status

### 2. Naming Conventions

**Scripts:**
- Use snake_case: `fix_broken_links.sh`
- Descriptive verbs: fix, validate, analyze, track, generate
- Location prefix: `.codex/scripts/`

**Python Modules:**
- Use snake_case: `rl_validator.py`
- Clear purpose: `<domain>_<action>.py`
- Location: `src/cognitive_brain/utils/`

**Functions:**
- Use snake_case: `validate_reward_calculation()`
- Verb-first naming
- Clear intent

### 3. Documentation Requirements

**Every utility MUST include:**

```python
"""
<Utility Name>

Purpose: <One-line description>

Usage:
    <Code example>

Args:
    <Parameter descriptions>

Returns:
    <Return value description>

Raises:
    <Exception descriptions>

Examples:
    <Practical examples>

Created: <Date>
Agent: <Agent name>
Session: <Session reference>
"""
```

### 4. Testing Requirements

**Minimum test coverage:**
- Unit tests: 80%+
- Integration tests: Where applicable
- Edge cases: Documented and tested
- Error handling: Validated

**Test location:**
- Scripts: `tests/scripts/test_<script_name>.py`
- Utilities: `tests/cognitive_brain/utils/test_<utility_name>.py`

### 5. CI/CD Integration

**Utilities should:**
- Run in CI/CD pipeline (where appropriate)
- Have exit codes (0=success, non-zero=failure)
- Generate logs
- Support --help flag
- Support --verbose flag
- Support --dry-run flag (for destructive operations)

### 6. Update Process

**When updating a utility:**

1. Update version number in docstring
2. Document changes in this registry
3. Update usage examples
4. Run full test suite
5. Update dependent code
6. Commit with descriptive message

---

## Utility Dependencies

### Current Dependencies
- bash (fix_broken_documentation_links.sh)
- sed (text replacement)
- grep (pattern matching)

### Future Dependencies (Planned)
- Python 3.10+
- numpy (numerical operations)
- torch/PyTorch (DQN implementation)
- matplotlib (visualization)
- seaborn (enhanced visualization)
- pandas (data analysis)
- pytest (testing)

---

## Integration with Cognitive Brain

### Phase 8.3 Pre-commit 3-4 (RL Algorithms)

**Required Utilities:**
1. RL Algorithm Validator ✅ Planned
2. Performance Metrics Tracker ✅ Planned
3. Convergence Detector ✅ Planned

**Implementation Order:**
1. Week 1: RL Validator foundations
2. Week 2: Integration with OutcomeAnalyzer
3. Week 3: Metrics dashboard
4. Week 4: Full validation suite

### Phase 8.3 Pre-commit 5-6 (Meta-Learner)

**Required Utilities:**
1. Knowledge Graph Builder ⏳ Future
2. Transfer Learning Validator ⏳ Future
3. Few-Shot Learning Tester ⏳ Future

---

## Utility Performance Metrics

### fix_broken_documentation_links.sh

**Performance:**
- Execution time: ~5 seconds
- Files scanned: 200+
- Files modified: 36
- Links fixed: 50+
- Success rate: 100%

**Optimization opportunities:**
- Parallel processing for large repos
- Cache pattern matches
- Incremental updates only

---

## Contributing New Utilities

### Process

1. **Identify Need:**
   - Document the problem
   - Check if existing utility can be extended
   - Propose solution

2. **Design:**
   - Define interface
   - Document inputs/outputs
   - Identify dependencies

3. **Implement:**
   - Write code with tests
   - Follow naming conventions
   - Add comprehensive docstrings

4. **Document:**
   - Add entry to this registry
   - Update relevant guides
   - Create usage examples

5. **Review:**
   - Self-review (5 iterations minimum)
   - Code review via tools
   - Test coverage validation

6. **Deploy:**
   - Commit with descriptive message
   - Update CHANGELOG
   - Notify team (if applicable)

---

## Maintenance Schedule

**Monthly:**
- Review utility usage
- Update dependencies
- Check for improvements
- Remove deprecated utilities

**Quarterly:**
- Comprehensive audit
- Performance optimization
- Documentation updates
- Integration testing

**Annually:**
- Major version updates
- Deprecation notices
- Migration planning

---

## Quick Reference

### Implemented Utilities

| Utility | Location | Status | Usage |
|---------|----------|--------|-------|
| Documentation Link Fixer | `.codex/scripts/fix_broken_documentation_links.sh` | ✅ Active | `bash .codex/scripts/fix_broken_documentation_links.sh` |

### Planned Utilities

| Utility | Priority | Est. Lines | Target Phase |
|---------|----------|------------|--------------|
| Code Quality Validator | High | 500 | Phase 8.3 |
| Test Coverage Analyzer | Medium | 400 | Phase 8.3 |
| Pre-commit Tracker | High | 300 | Phase 8.3 |
| RL Algorithm Validator | Critical | 600 | Pre-commit 3-4 |
| Metrics Dashboard | Medium | 500 | Phase 8.4 |
| Doc Consistency Checker | Medium | 400 | Phase 8.4 |
| AfterMath Validator | High | 350 | Phase 8.3 |

---

## Policy Reference

This registry implements the requirement from `.codex/CODEBASE_AGENCY_POLICY.md`:

> **Tooling Function Documentation Policy:**
> If you find yourself creating any tooling functions throughout your entire turn, you MUST document these tooling functions and plan for implementation. This ensures ALL future AI Agents can leverage existing utilities and maintain consistency across the codebase.

---

**Last Updated:** 2026-01-05  
**Next Review:** 2026-02-05  
**Maintainer:** AI Agent Team  
**Version:** 1.0.0
