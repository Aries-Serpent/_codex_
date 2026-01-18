# Pull Request Template

> **Version:** 2.1.0  
> **Updated:** 2026-01-18  
> **Repository:** Aries-Serpent/_codex_  
> **Status:** 🏆 Level 4 MLOps Certified | 1225+ Tests | 90% Coverage Threshold

---

## 🤖 COPILOT CONTINUATION (Auto-Generated)

@copilot continue with remaining tasks for this PR

**📋 Follow-Up Prompt**: See `COGNITIVE_BRAIN_CONTINUATION_PROMPT_PHASE_*.md` for active prompts

### Quick Reference
- **Test Count:** 1225+ (Phase 14-17 complete)
- **Coverage Threshold:** 90% (pyproject.toml)
- **Python Versions:** 3.11, 3.12

---

## ⚠️ REQUIRED Safety Confirmations

**These checkboxes MUST be confirmed before merge:**

- [ ] **Network Safety Acknowledgment** (`NETWORK_SAFETY_ACK`) - I confirm NO unauthorized network operations are performed by this PR
- [ ] **Offline Mode Confirmation** (`OFFLINE_MODE_CONFIRM`) - I confirm all audit and test operations run in strict offline mode
- [ ] **Security Review** - I confirm no secrets, API keys, or sensitive data are committed
- [ ] **Test Validation** - I confirm tests pass locally (`pytest`)

---

## 📝 Commit Message Checklist

**Each commit message MUST include:**

- [ ] **What Was Done** - Clear description of completed work in this commit
- [ ] **What's Next** - Brief note on remaining work or next steps
- [ ] **Phase/Task Reference** - Reference to the phase or task being worked on

### Commit Message Format

```
<type>: <short description>

**Done:**
- [x] Completed item 1
- [x] Completed item 2

**Next:**
- [ ] Pending item 1
- [ ] Pending item 2

Phase: <phase number> | Status: <percentage>%
```

### Example Commit Message

```
feat: Add Phase 16.0 documentation tests

**Done:**
- [x] Created tests/docs/test_doc_validation.py (20+ tests)
- [x] Created tests/docs/test_api_docs.py (15+ tests)
- [x] Updated PR template to v2.0

**Next:**
- [ ] Create API contract tests (Phase 16.1)
- [ ] Create E2E workflow tests (Phase 16.2)

Phase: 16.0 | Status: 100%
```

---

## Scope

| Field | Value |
|-------|-------|
| **Type** | Feature / Bug Fix / Docs / CI / Refactor |
| **Areas** | _e.g., tests, CI, docs, workflows, security_ |

### Description

_Provide a clear and concise description of the changes._

### Changes Made

_List the key changes:_
- Change 1
- Change 2
- Change 3

---

## 📋 Configuration (Opt-In)

### Testing Options
- [ ] **Run Full Test Suite** - Execute all 960+ tests
- [ ] **Coverage Report** - Generate coverage report with `--cov`
- [ ] **Performance Benchmarks** - Run benchmark tests in `tests/perf/`

### Documentation
- [ ] **Build Docs** - Build MkDocs documentation
- [ ] **Update CHANGELOG** - Add entry to CHANGELOG.md

### Security
- [ ] **Security Scan** - Run CodeQL/Semgrep analysis
- [ ] **Dependency Audit** - Run `pip-audit` for vulnerabilities

---

## Verification Commands

```bash
# Quick validation
pytest tests/ -x --tb=short

# Full test suite with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=85

# Linting
ruff check src/ tests/
black --check src/ tests/

# YAML validation
yamllint -c .yamllint.yml .github/workflows/
```

---

## Testing Checklist

- [ ] Tests pass locally (`pytest`)
- [ ] Linting passes (`ruff check`, `black --check`)
- [ ] Type checking passes (`mypy` if applicable)
- [ ] New tests added for new functionality
- [ ] Existing tests updated for changed functionality

---

## Documentation Checklist

- [ ] README.md updated (if applicable)
- [ ] Docstrings added/updated for new functions
- [ ] CHANGELOG.md updated (if applicable)
- [ ] API documentation updated (if applicable)

---

## Code Quality Checklist

- [ ] Code follows repository style guidelines
- [ ] Self-review completed
- [ ] No hardcoded secrets or sensitive data
- [ ] No new warnings introduced
- [ ] Error handling is appropriate

---

## AI Agency Policy Compliance

For Copilot/AI-assisted PRs:
- [ ] Plan documented before execution
- [ ] Pre-commit/commit terminology used correctly
- [ ] Codebase left better than found
- [ ] 5-pass self-review completed (if applicable)
- [ ] PDA loop (Plan→Do→Assess) documented

---

## Screenshots (if applicable)

_Add screenshots for UI changes_

---

## Related Issues

_Link related issues: Fixes #123, Relates to #456_

---

## Reviewer Notes

_Any specific areas that need careful review?_

---

## Reviewer(s)

- @mbaetiong
