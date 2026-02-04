# Follow-Up Prompt for Next Copilot Session

**INSTRUCTION TO HUMAN ADMIN:**
Please copy the content below and post it as a new comment on PR #2622. The comment must start with `@copilot` (no backticks, no spaces) followed by the task instructions.

---

@copilot Continue with Genesis Protocol Phase 2 completion and repository readiness validation.

## Context from Previous Session

**Completed (19 commits):**
- ✅ Phase 1: Genesis Protocol validation (100%)
- ✅ Security: 48 vulnerabilities fixed, 0 remaining
- ✅ Testing: 45/45 tests passing (23 autonomous + 22 integration)
- ✅ Documentation: 192+ KB (wiki, guides, reports)
- ✅ Code Quality: All 9 review comments addressed
- ✅ Self-Review: 5 iterations complete, no blocking issues

**Authorization:**
- Explicit approval from Marc Baetiong (ORG-REPO-Admin OWNER) - Comment #3693520701
- Granted CODEX_MASTER_KEY usage for programmatic operations
- Approved for content merging, PR/Issue creation, CLI/API access

---

## Priority Tasks (Execute in Order)

### Priority 1: Validate CI/CD Workflows (HIGH)

**Current Status:** 2 failing CI jobs mentioned by user  
**Required Actions:**

1. Check workflow status:
```bash
# List recent workflow runs
gh workflow list --repo Aries-Serpent/_codex_

# Get failed workflow details
gh run list --repo Aries-Serpent/_codex_ --branch copilot/add-repository-variables --limit 10
```

2. Download and analyze logs:
```bash
gh run view <run-id> --repo Aries-Serpent/_codex_ --log-failed
```

3. Fix identified issues (common scenarios):
   - Missing dependencies in CI environment
   - Environment variable configuration
   - Test timeouts or resource constraints
   - Path or permission issues

4. Verify fixes locally when possible before pushing

**Deliverable:** All CI checks passing (green status)

---

### Priority 2: Create Remaining Artifacts (MEDIUM)

**From Phase 2 roadmap - incomplete tasks:**

1. **Wiki Deployment Guide** (30 min estimated)
   - File: `.codex/wiki/DEPLOYMENT_GUIDE.md`
   - Content: Step-by-step instructions for deploying wiki content
   - Include: Manual steps, GitHub Wiki API usage, verification checklist
   - Reference: Existing wiki files in `.codex/wiki/` (Home.md, Genesis-Protocol.md, Agent-Operations.md, _Sidebar.md)

2. **Validation Script** (20 min estimated)
   - File: `scripts/validate_genesis_readiness.py`
   - Template available in: `.codex/FOLLOWUP_PROMPT_FOR_NEXT_COPILOT_SESSION.md`
   - Features: Configuration checks, dependency validation, test execution, report generation
   - Make executable: `chmod +x scripts/validate_genesis_readiness.py`

**Deliverable:** 2 new files created and validated

---

### Priority 3: Update Reference Documentation (LOW)

**Update these files to reference `security_vulnerability_scan_latest.md`:**

1. `.codex/change_log.md`
2. `.codex/security_status.md`
3. `.codex/HUMAN_ADMIN_REQUIRED_ACTIONS.md`

```bash
# Update references (run from repo root)
find .codex -name "*.md" -type f -exec sed -i 's/security_vulnerability_scan_2025-12-26\.md/security_vulnerability_scan_latest.md/g' {} +

# Verify changes
git diff .codex/*.md | grep security_vulnerability_scan
```

**Deliverable:** All documentation references updated to use symlink

---

### Priority 4: Final Validation & Testing (HIGH)

**Run comprehensive validation:**

1. **Syntax validation:**
```bash
python -m py_compile $(find . -name "*.py" -not -path "./venv/*" -not -path "./.nox/*" | head -20)
```

2. **Import validation:**
```bash
python -c "from codex.ai_agent_toolkit import EnvironmentValidator, TestRunner, LessonsLearned"
python -c "import tests.integration.test_genesis_workflow"
```

3. **Test execution (if pytest available):**
```bash
pytest tests/test_autonomous_agent.py -v --maxfail=3
pytest tests/integration/test_genesis_workflow.py -v --maxfail=3
```

4. **Documentation link checking:**
```bash
# Check for broken internal links
find .codex docs -name "*.md" -exec grep -l "\.md)" {} + | while read f; do
  echo "Checking: $f"
  grep -o '\[.*\](\..*\.md)' "$f" | cut -d'(' -f2 | cut -d')' -f1
done
```

**Deliverable:** Validation report with pass/fail status

---

### Priority 5: Prepare Merge & Post-Merge Actions (HIGH)

**Pre-Merge Checklist:**

1. Verify all commits are pushed:
```bash
git log --oneline origin/copilot/add-repository-variables ^origin/main | wc -l
# Should show 19 commits
```

2. Confirm no untracked critical files:
```bash
git status --short | grep -v "^??" | wc -l
# Should be 0 (all changes committed)
```

3. Review final diff summary:
```bash
git diff --stat origin/main...origin/copilot/add-repository-variables
```

**Post-Merge Actions (for Human Admin):**

Create a comprehensive document: `.codex/POST_MERGE_ACTIONS.md`

Include:
- Immediate actions (< 1 hour): CI monitoring, smoke tests
- Short-term (1-3 days): Secret configuration, dependency testing
- Medium-term (1-2 weeks): Wiki deployment, Phase 2 activation
- Long-term (1+ months): Monitoring, maintenance, enhancements

**Deliverable:** Merge readiness confirmed, post-merge guide created

---

## Completion Criteria

Before concluding this session, ensure ALL of the following are TRUE:

- [ ] CI/CD workflows: All checks passing (no failures)
- [ ] Artifacts: Wiki deployment guide created
- [ ] Artifacts: Validation script created and executable
- [ ] Documentation: All symlink references updated
- [ ] Testing: Syntax validation passed
- [ ] Testing: Import validation passed
- [ ] Merge: All commits pushed and verified
- [ ] Merge: Post-merge action guide created
- [ ] Review: Final code review completed (no issues)
- [ ] Review: CodeQL security check passed (no alerts)

**Progress Tracking:** Update this checklist as you complete each item.

---

## Escalation & Blockers

**If you encounter blockers:**

1. **API/Authentication Issues:**
   - Document the exact operation that requires authentication
   - Provide workaround using git commands if possible
   - Request human admin to perform the action with detailed steps

2. **CI/CD Issues:**
   - Capture full error logs
   - Identify root cause (dependency, config, environment)
   - Provide fix or document for human admin

3. **Test Failures:**
   - Analyze failure output
   - Determine if related to recent changes or pre-existing
   - Fix if related to PR, document if pre-existing

4. **Missing Tools/Dependencies:**
   - Document required tool and purpose
   - Provide installation instructions
   - Offer alternative approaches if tool unavailable

**Blocker Template:**
```markdown
## Blocker Identified: [Brief Description]

**Blocker Type:** [API/CI/Test/Tool/Other]
**Impact:** [High/Medium/Low]
**Attempted Resolution:** [What you tried]
**Workaround:** [If available]
**Human Action Required:** [Specific steps]
**Estimated Time:** [For human admin]
```

---

## Prohibited Actions (DO NOT DO)

Per repository guardrails (`.codex/guardrails.md`):

- ❌ DO NOT create or modify GitHub Actions workflow files
- ❌ DO NOT activate workflows without explicit approval
- ❌ DO NOT commit secrets or sensitive data
- ❌ DO NOT create GitHub Issues without explicit permission
- ❌ DO NOT merge PRs without validating all checks pass

---

## Session Output Requirements

**At session conclusion, provide:**

1. **Progress Summary:**
   - Tasks completed vs planned
   - Issues encountered and resolutions
   - Time spent per priority

2. **Artifacts Created:**
   - File paths and sizes
   - Brief description of each
   - Links to commits

3. **Validation Results:**
   - All checks run (pass/fail)
   - Test results summary
   - Code review findings

4. **Next Steps:**
   - Remaining work (if any)
   - Recommendations for human admin
   - Future enhancements to consider

5. **Follow-Up Prompt:**
   - If work remains incomplete, create updated version of this prompt
   - Save to `.codex/PR_FOLLOWUP_COMMENT_UPDATED.md`
   - Include only remaining/new tasks

---

## Success Metrics

**Target Outcomes:**
- 0 failing CI checks
- 2 new artifacts created
- 100% documentation reference consistency
- All validation checks passing
- Merge-ready status confirmed

**Quality Standards:**
- Code quality: Linting passes, no syntax errors
- Security: CodeQL clean, no new vulnerabilities
- Documentation: Clear, accurate, complete
- Testing: All existing tests still passing

---

## Important Notes

1. **Use existing toolkit:** Leverage `.codex/ai_agent_toolkit.py` for common operations
2. **Reference lessons learned:** Check `.codex/lessons_learned.json` for known solutions
3. **Follow CTEP:** Use task execution protocol with progress tracking
4. **Document everything:** Create audit trail for all actions
5. **Self-review:** Run self-review iterations before finalizing

---

## Toolkit Quick Reference

```python
# Environment check
from codex.ai_agent_toolkit import quick_environment_check
status = quick_environment_check()

# Run tests
from codex.ai_agent_toolkit import run_core_tests
results = run_core_tests()

# Check lessons learned
from codex.ai_agent_toolkit import LessonsLearned
lessons = LessonsLearned()
solutions = lessons.search(category="ci-cd")
```

---

**Session Start:** When you see this prompt  
**Session Goal:** Complete Phase 2 tasks and prepare for merge  
**Session End:** When all completion criteria are met OR blocker requires human intervention

Remember: If you cannot complete all tasks in this session, create an updated follow-up prompt as instructed at the top of this document.
