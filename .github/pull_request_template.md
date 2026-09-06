## Description

Please include a summary of the changes and the motivation for them. If this PR fixes an issue, link to it using `Closes #ISSUE_NUMBER`.

What problem are you solving? Why is this change needed?

## 🔄 Workflow Execution Checklist

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)
- [x] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

### 🔄 Active Workflows — currently enabled in the live repo baseline
- [ ] auth-tests.yml — Authentication Tests
- [ ] audit-qa-suite.yml — Audit & QA Suite (Unified)
- [ ] data-quality-suite.yml — Data Quality & Determinism Suite
- [ ] docker-build-push.yml — Build & push Docker image (GHCR)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
- [ ] security-scanning-suite.yml — Full security audit (bandit, pip-audit)
- [ ] test-rag.yml — RAG Module Tests (coverage ≥95%)
- [ ] scheduled-archival.yml — Scheduled archival
- [ ] scheduled-dependency-audit.yml — Dependency audit
- [ ] pre-merge-validation.yml — Pre-merge validation (manual activation only)
- [ ] comment-review-gate.yml — Comment review gate (manual activation only)
- [ ] iterative-self-healing-ci.yml — Iterative self-healing CI loop (manual activation only)
- [ ] unified-copilot-management.yml — Copilot management suite (manual activation only)

## Type of Change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring (no functional changes)

## Related Issues

Closes #ISSUE_NUMBER

If this PR addresses multiple issues, list them:
- Fixes #ISSUE_1
- Relates to #ISSUE_2

## Testing

Please describe the testing you've done:

- [ ] Added new tests for this functionality
- [ ] Updated existing tests
- [ ] All tests pass locally (`pytest`)
- [ ] Coverage maintained above 90% (`pytest --cov=src --cov-fail-under=90`)
- [ ] Manual testing performed (describe what you tested)

**How to test these changes:**
1. Step 1
2. Step 2
3. Step 3

## Checklist

Before submitting, please verify:

- [ ] My code follows the style guidelines of this project
  - Black formatting: `black src/`
  - Ruff linting: `ruff check src/`
  - Type checking: `mypy src/`
  - Pre-commit hooks: `pre-commit run --all-files`
  
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests passed locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules

## Documentation

- [ ] Updated README.md if relevant
- [ ] Updated docstrings in code
- [ ] Updated API documentation
- [ ] Added examples for new features
- [ ] Updated CHANGELOG.md (if applicable)

## Performance Impact

Please describe any performance implications:

- [ ] No performance impact
- [ ] Performance improvement: (describe improvements)
- [ ] Performance regression: (describe and justify)

## Screenshots / Demo

If applicable, add screenshots or links demonstrating the change:

## Additional Context

Add any other context about the PR here, such as:
- Design decisions and rationale
- Known limitations or edge cases
- Breaking changes and migration path
- Dependencies on other PRs

## Reviewers

Please tag reviewers who should review this PR:
@username1 @username2

---

**Note**: This PR template is to help you provide all necessary information. Feel free to remove sections that don't apply to your change.

For more information, see:
- [Contributing Guide](../CONTRIBUTING.md)
- [Code Review Guide](../docs/CODE_REVIEW_GUIDE.md)
- [Development Setup](../docs/DEVELOPMENT.md)
