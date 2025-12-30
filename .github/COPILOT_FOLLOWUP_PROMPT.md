# GitHub Copilot Agent Follow-Up Prompt

## Context
This is a continuation prompt for GitHub Copilot Agent to complete Phase 2 of the workflow caching implementation and address any remaining tasks.

## How to Use This Prompt
**Post this as a comment on the active PR for branch `copilot/add-github-secrets-scanning-workflow`:**

---

@copilot Please continue with Phase 2 of the workflow caching implementation and complete the following tasks:

## Phase 2: High-Frequency Workflow Caching

Add caching to the following high-priority workflows that are missing it:

1. **security-suite.yml** - Security scanning workflow
   - Add `actions/cache@v5` with paths: `~/.cache/pip`, `~/.cache/nox`
   - Key: `${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt', 'pyproject.toml') }}`
   - Priority: HIGH (runs on PRs and security scans)

2. **integration-gated.yml** - Integration testing
   - Add same caching pattern
   - Priority: HIGH (runs on PRs)

3. **nox_gates.yml** - Nox-based testing
   - Add caching for `~/.cache/pip` and `~/.cache/nox`
   - Priority: HIGH (frequent execution)

4. **scheduled-dependency-audit.yml** - Daily dependency checks
   - Add caching pattern
   - Priority: MEDIUM (runs daily)

## Validation Requirements

For each workflow updated:
1. Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('file.yml'))"`
2. Verify caching uses `actions/cache@v5` (repository standard)
3. Ensure cache keys match repository pattern
4. Check that all Python setup steps have corresponding cache steps
5. Test that no breaking changes are introduced

## Testing Plan

After updating workflows:
1. Verify all YAML files pass syntax validation
2. Check for conflicts with existing workflows
3. Ensure permissions are properly set
4. Validate cache paths exist in runner environment
5. Document changes in CACHE_ANALYSIS_REPORT.md

## Additional Tasks

### Documentation Updates
- Update CACHE_ANALYSIS_REPORT.md with Phase 2 progress
- Document any new patterns or special cases discovered
- Add cache hit rate monitoring recommendations

### Code Quality Checks
- Run repository linters on modified files
- Ensure consistent formatting
- Check for any hardcoded values that should be variables

### Security Validation
- Verify no secrets are exposed in cache keys
- Ensure proper permissions for cache actions
- Check that PR workflows use read-only cache (cache/restore)

## Success Criteria

- [ ] 4+ additional workflows have caching implemented
- [ ] All YAML files validate successfully  
- [ ] Documentation updated with changes
- [ ] No breaking changes to existing functionality
- [ ] Cache keys follow repository standards
- [ ] Security best practices maintained

## Estimated Impact

After Phase 2 completion:
- Additional monthly savings: ~5 hours of runner time
- Total workflows with caching: 18+
- Network bandwidth reduction: 60-85%

## References

- **Caching Standard**: See `.github/workflows/CACHE_ANALYSIS_REPORT.md`
- **Example Implementation**: See `.github/workflows/pre-release-deployment.yml` lines 39-45
- **Repository Pattern**: `actions/cache@v5` with pip and nox paths

## Follow-Up Actions

If unable to complete all tasks in one session:
1. Prioritize by frequency of execution (security-suite.yml first)
2. Commit progress incrementally
3. Update checklist in this prompt
4. Post a new continuation prompt with remaining tasks

Please acknowledge this task and proceed with implementation. Report progress after each workflow is updated. If you encounter any issues or need clarification, ask before proceeding.

---

## Internal Notes (For Agent Context)

**Branch**: `copilot/add-github-secrets-scanning-workflow`
**Base Commit**: a0211bc
**Phase 1 Completed**: 
- scan-secrets-variables.yml (new)
- self-healing-feedback-loop.yml (updated)
- code-quality.yml (updated)

**Remaining from Original Scope**: 32 workflows without caching
**Phase 2 Target**: 4 high-priority workflows
**Phase 3 Target**: Remaining 28 workflows (future work)

**Self-Review Completed**: 5 iterations, 0 remaining concerns
**Documentation**: Comprehensive (README + Cache Analysis + Test Plan)
