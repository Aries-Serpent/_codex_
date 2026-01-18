# Pull Request Template

> **Version:** 2.0.0  
> **Updated:** 2026-01-18  
> **Repository:** Aries-Serpent/_codex_  
> **Status:** 🏆 Level 4 MLOps Certified | 800+ Tests | 85% Coverage Threshold

---

## 🤖 COPILOT CONTINUATION (Auto-Generated)

@copilot continue with remaining tasks for this PR

**📋 Follow-Up Prompt**: See `COGNITIVE_BRAIN_CONTINUATION_PROMPT_PHASE_*.md` for active prompts

### Quick Reference
- **Test Count:** 800+ (Phase 14-15 complete, Phase 16 in progress)
- **Coverage Threshold:** 85% (pyproject.toml)
- **Python Versions:** 3.11, 3.12

---

## ⚠️ REQUIRED Safety Confirmations

**These checkboxes MUST be confirmed before merge:**

- [ ] **Network Safety Acknowledgment** (`NETWORK_SAFETY_ACK`) - I confirm NO unauthorized network operations are performed by this PR
- [ ] **Offline Mode Confirmation** (`OFFLINE_MODE_CONFIRM`) - I confirm all audit and test operations run in strict offline mode
- [ ] **Security Review** - I confirm no secrets, API keys, or sensitive data are committed
- [ ] **Test Validation** - I confirm tests pass locally (`pytest`)

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
- [ ] **Run Full Test Suite** - Execute all 800+ tests
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
