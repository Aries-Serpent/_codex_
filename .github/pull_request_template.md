## Description

Please include a summary of the changes and the motivation for them. If this PR fixes an issue, link to it using `Closes #ISSUE_NUMBER`.

What problem are you solving? Why is this change needed?

## 🔄 Workflow Execution Checklist

### ✅ Always Required — fire automatically on every push (cannot be skipped)
- [x] pre-merge-validation.yml — Pre-merge checks (always required)
- [x] comment-review-gate.yml — Comment review gate (always required)
- [x] deferral-language-gate.yml — Deferral language guard (always required)
- [x] agent-auth-delegation.yml — Agent token delegation (always required)
- [x] workflow-execution-gate.yml — WEC gate — parse checklist & arm allowed workflows (always required)

### 🔄 Always Active — fire via push/workflow_run (need approval in Actions tab)
- [x] unified-copilot-management.yml — Copilot Management Suite (agent-checkin, session-done, self-healing)
- [ ] iterative-self-healing-ci.yml — Iterative self-healing CI loop (fires on workflow_run — needs approval)
- [x] cost-gate.yml — Cost governance gate (called by agent-auth-delegation)

### 🧪 Opt-In: Testing & Validation
- [ ] validate.yml — Validation Pipeline (detect-secrets, ruff, pre-commit, sync-tracked)
- [ ] resilient_validation.yml — Resilient Validation Suite (full pytest, 4 shards)
- [ ] test-rag.yml — RAG Module Tests (coverage ≥95%)
- [ ] nox_gates.yml — Nox quality gates (ruff, mypy, coverage)
- [ ] mypy-baseline.yml — mypy type-check anti-regression gate
- [ ] coverage-with-timeout.yml — Coverage with timeout guards
- [ ] progressive-validation.yml — Progressive Validation Suite
- [ ] pre-flight-validation.yml — Pre-flight CI validation
- [ ] ci-checkpoint-validation.yml — CI Checkpoint Validation
- [ ] data-quality-suite.yml — Data Quality & Determinism Suite
- [ ] auth-tests.yml — Authentication Tests
- [ ] pr-checks.yml — PR Checks (isolated cache, src/ scope)
- [ ] html_visual_regression.yml — HTML Visual Regression Screenshots

### 🔒 Opt-In: Security & Quality
- [ ] security-scanning-suite.yml — Full security audit (bandit, pip-audit)
- [ ] codeql-analysis.yml — CodeQL SAST analysis
- [ ] actionlint-audit.yml — Workflow compliance audit (actionlint)
- [ ] semgrep_sarif.yml — Semgrep SAST (SARIF upload)
- [ ] auto-fix-common-issues.yml — Auto-Fix Common CI Issues
- [ ] auto-fix-pr-check.yml — PR Auto-Fix Check
- [ ] code-quality-coverage-suite.yml — Code Quality & Coverage Suite
- [ ] audit-qa-suite.yml — Audit & QA Suite (Unified)
- [ ] template_lint.yml — PR Template Lint
- [ ] codeql-alert-fetcher.yml — CodeQL Alert Fetcher (artifact for in-session review)

### 📄 Opt-In: Documentation
- [ ] documentation-link-checker.yml — Documentation link checker
- [ ] pages-pre-merge-validation.yml — Pages pre-merge validation

### ⚙️ Opt-In: Infrastructure & Deployment
- [ ] reference-integrity.yml — Reference integrity + agent size gate
- [ ] dependency-submission.yml — Resilient dependency submission
- [ ] docker-build-push.yml — Build & push Docker image (GHCR)
- [ ] rust_swarm_ci.yml — Rust-Python hybrid swarm CI/CD
- [ ] root-org-validation.yml — Root organization validation
- [ ] agent-registry-validation.yml — Agent registry validation
- [ ] e-to-d-transition-gate.yml — E→D transition readiness gate
- [ ] d-capable-promotion-gate.yml — D_CAPABLE agent promotion gate
- [ ] qa-walkthrough.yml — QA walkthrough agent
- [ ] mcp-health.yml — MCP health & metrics gate (src/mcp/ scope)

- [x] auto-approve-workflows — Auto-Approve workflow to run (approves all pending runs on last commit SHA)

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
