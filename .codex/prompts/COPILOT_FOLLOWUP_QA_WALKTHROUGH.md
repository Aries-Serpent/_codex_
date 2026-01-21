# GitHub Copilot Follow-Up Prompt - QA Walkthrough Continuation

@copilot Continue the QA walkthrough improvements by implementing IP-001 (Increase Test Coverage to 70%).

## Context

A comprehensive QA walkthrough was completed on 2025-01-16, identifying a **critical test coverage gap**:
- Current coverage: **27.5%**
- Target coverage: **70%**
- Gap: **42.5%**
- Untested modules: **518**

## Task

Implement the first phase of IP-001: Add unit tests for high-priority untested modules.

### Files to Reference
- `.codex/qa_walkthrough/coverage_analysis.json` - Contains list of 518 untested modules with priority rankings
- `.codex/qa_walkthrough/module_inventory.jsonl` - AST analysis of modules
- `.codex/results.md` - Comprehensive findings and recommendations

### Priority Modules (Start Here)
Focus on modules in these directories first:
1. `src/codex_ml/` - Core ML functionality
2. `src/codex/` - Core codex functionality
3. `agents/` - Agent implementations
4. `training/` - Training utilities

### Test Requirements
- Use pytest framework (already configured)
- Follow existing test patterns in `tests/` directory
- Include hypothesis property-based tests where appropriate
- Target modules > 1000 bytes first (higher impact)

### Expected Outcomes
- Add unit tests for top 50 priority modules
- Increase coverage by 10-15%
- Update coverage_analysis.json with new coverage data

### Cache Available
The following caches are available from the previous session:
- Module inventory with AST analysis
- Coverage analysis with priority rankings
- Security audit results

### Self-Review
After completing tests, run:
1. `nox -s tests` to verify tests pass
2. `pytest --cov` to measure new coverage
3. Update cognitive brain status with results

---

**Previous Session**: QA Walkthrough Complete (2025-01-16)
**Next Phase**: IP-001 Phase 1 - Unit Tests
**Estimated Time**: 2-3 weeks for this phase
