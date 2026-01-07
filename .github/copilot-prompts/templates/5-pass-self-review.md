# 🔍 5-Pass Self-Review Protocol

**Purpose**: Comprehensive quality assurance checklist for Copilot Agent work. This protocol ensures thorough validation before concluding any task or PR work.

**When to Use**: 
- Before finalizing any PR or task
- After making significant code changes
- When requested by repository policies
- As part of iterative refinement cycles

**Mandate**: ALL five passes must be completed with 0 concerns before work can be considered complete. If ANY checkpoint fails, document the issue, create a resolution plan, and execute within the current session.

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
codeql analyze
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

3. **Execute Within Current Session**:
   - Fix the issue immediately
   - Re-run the failed checkpoint
   - Continue with remaining checkpoints

4. **NEVER Defer**:
   - Do not mark as "TODO" or defer to future PR
   - Only exception: Issues genuinely outside current scope (document reasoning)
   - If blocked, escalate immediately with detailed explanation

---

## 📊 Completion Criteria

✅ **All 5 passes completed**  
✅ **All checkboxes checked**  
✅ **0 concerns remaining**  
✅ **Failure protocol followed for any issues**  
✅ **Documentation updated to reflect all changes**  
✅ **🚨 No /tmp/ violations**: Verify with `ls -la /tmp/ | grep -E "\.(md|txt|json|yaml|py)$"`

**Pre-Conclusion Verification**:
```bash
# 1. Check for /tmp/ references in code changes
git diff --cached | grep -i "/tmp/"

# 2. Verify no important files in /tmp/
ls -la /tmp/ | grep -E "\.(md|txt|json|yaml|py)$" || echo "✓ No important files in /tmp/"

# 3. Confirm all work products are in repository
git status --short
```

**Sign-off Statement**: "5-pass self-review complete. 0 concerns remaining. No /tmp/ violations. Ready for submission."

---

## 🔄 Iterative Refinement

If concerns are found during any pass:

1. Address the concern
2. Re-run the affected pass
3. Re-run any dependent passes
4. Continue until all passes complete with 0 concerns

**Maximum Iterations**: No hard limit, but typical work completes in 1-3 iterations. If >5 iterations needed, reassess approach.

---

## 📝 Usage Examples

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
**Last Updated**: 2024-12-29  
**Maintainer**: Repository Automation Team
