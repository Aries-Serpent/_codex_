# 🔍 Risk-Appropriate Self-Review Dimensions

**Purpose**: Optional review checklist under `.codex/CODEBASE_AGENCY_POLICY.md`.
The legacy filename is retained for reference compatibility, not a minimum pass
count. Dimensions are selected by risk and applicability; actual checks and gaps
must be reported truthfully. Self-testing is not independent verification.

**When to Use**:
- When relevant to the authorized task and affected paths
- After making significant code changes
- When requested by repository policies
- As part of iterative refinement cycles

**Boundary**: Required checks and security owner/reason classification remain
binding. Missing optional memory/tools/specialists is an explicit limitation, not
a startup deadlock. Direct work is valid. Respect read-only tasks, resource limits
and actual execution approvals; no public retrigger, merge, publication, protected
settings change or activation is authorized by this checklist.

---

## 📋 Self-Review Checklist

### Pass 1: Code Quality & Correctness ✅

**Objective**: Ensure code is syntactically correct, follows standards, and handles errors properly.

- [ ] **Syntax Validation**: All syntax errors resolved
- [ ] **Linting Compliance**: No new linting warnings introduced
- [ ] **Type Safety**: Type hints correct and comprehensive (Python, TypeScript, etc.)
- [ ] **Error Handling**: Comprehensive error handling with appropriate exceptions
- [ ] **Edge Cases**: Edge cases identified and properly handled
- [ ] **Code Standards**: Follows repository coding standards and conventions

**Validation Commands**:
```bash
# Python
ruff check .
black --check .
mypy src/

# TypeScript/JavaScript  
npm run lint
npm run type-check

# General
pre-commit run --all-files
```

---

### Pass 2: Testing & Validation ✅

**Objective**: Verify functionality through comprehensive testing.

- [ ] **Local Tests Pass**: All tests passing in local environment
- [ ] **New Test Coverage**: New tests added for new functionality
- [ ] **Coverage Maintained**: Test coverage maintained or improved (no degradation)
- [ ] **CI/CD Passing**: All CI/CD checks passing (or failures are unrelated)
- [ ] **Integration Tests**: Integration tests pass if applicable
- [ ] **Regression Tests**: No regressions introduced in existing functionality

**Validation Commands**:
```bash
# Python
pytest tests/ --cov --cov-report=term-missing
nox -s tests

# JavaScript/TypeScript
npm test
npm run test:coverage

# Check CI status
gh pr checks {pr_number}
```

---

### Pass 3: Documentation & Communication ✅

**Objective**: Ensure changes are well-documented and communicable.

- [ ] **Code Comments**: Complex logic has clear explanatory comments
- [ ] **Docstrings/JSDoc**: Functions and classes have up-to-date documentation strings
- [ ] **README Updates**: README.md reflects any interface or usage changes
- [ ] **CHANGELOG**: CHANGELOG.md updated with notable changes (if applicable)
- [ ] **Commit Messages**: Commit messages are descriptive and follow conventions
- [ ] **PR Description**: PR description clearly explains what, why, and how

**Documentation Standards**:
- Use clear, concise language
- Provide examples where helpful
- Document "why" decisions were made, not just "what" was done
- Keep documentation DRY (Don't Repeat Yourself)

---

### Pass 4: Security & Safety ✅

**Objective**: Prevent security vulnerabilities and unsafe practices.

- [ ] **No Secrets**: No hardcoded secrets, credentials, or API keys
- [ ] **Input Validation**: Proper input validation and sanitization
- [ ] **Dependency Security**: Dependencies reviewed for known vulnerabilities
- [ ] **Security Implications**: Security implications documented and addressed
- [ ] **Access Controls**: Appropriate access controls and permissions
- [ ] **Data Safety**: Sensitive data handled securely (encryption, proper storage)
- [ ] **🚨 CRITICAL: No /tmp/ Violations**: No important files stored in temporary directories (see `.github/TEMPORARY_FILES_POLICY.md`)

**Security Validation**:
```bash
# Check for secrets
git secrets --scan

# Check dependencies
pip-audit  # Python
npm audit  # JavaScript

# CodeQL scan
# Use an available supported security scanner; otherwise record NOT_RUN.
```

**Common Security Pitfalls to Avoid**:
- SQL injection vectors
- XSS vulnerabilities
- Insecure deserialization
- Path traversal issues
- Unvalidated redirects

---

### Pass 5: Integration & Dependencies ✅

**Objective**: Ensure changes integrate smoothly without breaking existing functionality.

- [ ] **No Breaking Changes**: No breaking changes (or properly documented with migration path)
- [ ] **Backward Compatibility**: Backward compatibility maintained for public APIs
- [ ] **Cross-PR Dependencies**: Dependencies on other PRs resolved or documented
- [ ] **No Regressions**: No regressions in existing features or workflows
- [ ] **Dependency Updates**: Dependencies updated only when necessary and tested
- [ ] **Environment Compatibility**: Works across required environments (Python versions, OS, etc.)

**Integration Validation**:
```bash
# Test across environments
nox  # Python multi-environment testing
tox  # Alternative Python testing

# Check for breaking changes
git diff main...HEAD -- {public_api_files}

# Verify backward compatibility
pytest tests/integration/ -v
```

---

## 🚨 Failure Protocol

**If ANY checkpoint fails:**

1. **Document the Issue**:
   - What failed and why
   - Impact assessment (severity, scope)
   - Root cause analysis

2. **Create Resolution Plan**:
   - Specific steps to fix
   - Required resources or changes
   - Success criteria for verification

3. **Address Relevant Authorized Defects**:
   - Fix introduced/relevant defects within task authority
   - Re-run the failed checkpoint
   - Continue with remaining checkpoints

4. **Preserve Incomplete Work**:
   - Keep blocked/deferred/pending work visibly incomplete
   - Record evidence, dissent, mitigation, proposed owner and exact resume target
   - Stop dependent unsafe/unauthorized work; continue unaffected scoped work

---

## 📊 Completion Criteria

- Applicable checks actually run, with failures and NOT_RUN statuses retained
- Required controls preserved; no claim of approval from checklist completion
- Unresolved concerns and exact continuation retained
- Useful task-owned temporary outputs durably retained before cleanup

**Pre-Conclusion Verification**:
```bash
# Inspect only task-owned outputs and retention manifests; filename absence
# does not prove durable retention. Do not delete unrelated temporary files.
git status --short
```

**Sign-off**: Report exact checks, limitations, unresolved concerns and retention
evidence. Do not copy a universal successful sign-off statement.

---

## 🔄 Iterative Refinement

If concerns are found during any pass:

1. Address the concern
2. Re-run the affected pass
3. Re-run any dependent passes
4. Continue within a risk-based budget; retain unresolved findings on exhaustion

**Retries**: Use new evidence and practical limits; no minimum pass count or
unbounded retry requirement applies.

---

## 📝 Usage Examples

The following are synthetic formatting examples, not observed validation,
independence, CI results or required test counts. Replace them with actual evidence.

### Example 1: Simple Documentation Update

```markdown
### Pass 1: Code Quality ✅
- [x] No code changes - N/A
### Pass 2: Testing ✅  
- [x] No functional changes - existing tests sufficient
### Pass 3: Documentation ✅
- [x] README updated with new section
- [x] Typos fixed, clarity improved
### Pass 4: Security ✅
- [x] Documentation only - no security implications
### Pass 5: Integration ✅
- [x] No breaking changes - purely additive
```

### Example 2: New Feature Implementation

```markdown
### Pass 1: Code Quality ✅
- [x] ruff check passed
- [x] mypy validated type hints
- [x] Error handling added for edge cases

### Pass 2: Testing ✅
- [x] Added 15 new unit tests (100% coverage of new code)
- [x] Integration tests pass
- [x] CI green: https://github.com/org/repo/actions/runs/123456

### Pass 3: Documentation ✅
- [x] Docstrings added to all new functions
- [x] README updated with usage examples
- [x] CHANGELOG.md updated

### Pass 4: Security ✅
- [x] Input validation on all public APIs
- [x] pip-audit: 0 vulnerabilities
- [x] CodeQL: 0 new alerts

### Pass 5: Integration ✅
- [x] Backward compatible - no breaking changes
- [x] Tested with Python 3.9, 3.10, 3.11, 3.12
- [x] No cross-PR dependencies
```

---

## 🔗 Related Templates

- **PR Continuation**: `.github/copilot-prompts/templates/pr-continuation.md`
- **CI Fix**: `.github/copilot-prompts/templates/ci-fix-continuation.md`
- **Multi-Phase**: `.github/copilot-prompts/templates/multi-phase-implementation.md`

---

## 📚 References

- **Repository Policy**: See `CONTRIBUTING.md` for coding standards
- **Testing Guide**: See `tests/README.md` for testing practices
- **Security Policy**: See `SECURITY.md` for security requirements

---

**Template Version**: 1.0.0  
**Last Updated**: 2025-12-29  
**Maintainer**: Repository Automation Team
