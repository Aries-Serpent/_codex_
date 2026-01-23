# Pre-Release Checklist

**Version**: 1.0.0  
**Date**: 2026-01-23  
**Status**: Production Ready

---

## Overview

This comprehensive pre-release checklist ensures the `codex-ml` package meets all quality, security, and documentation standards before PyPI publication.

---

## Phase 1: Version Synchronization ✅

### 1.1 Version Consistency
- [ ] Verify version in `src/codex_ml/__init__.py` matches intended release
- [ ] Update `pyproject.toml` version to match
- [ ] Ensure version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] Update version in documentation if hardcoded anywhere

**Commands**:
```bash
# Check current version
grep '__version__' src/codex_ml/__init__.py
grep 'version =' pyproject.toml

# Sync if needed
# Edit pyproject.toml line 70: version = "0.1.0"
```

### 1.2 Changelog Update
- [ ] Add release notes to CHANGELOG.md
- [ ] Include all significant changes since last release
- [ ] Credit contributors
- [ ] Link to relevant issues/PRs

---

## Phase 2: Quality Gates ✅

### 2.1 Test Suite
- [ ] All tests passing: `pytest tests/`
- [ ] Test count ≥ 1500 tests
- [ ] Zero test failures
- [ ] Zero skipped tests (or documented reason)

**Commands**:
```bash
pytest tests/ -v --tb=short
pytest --collect-only | grep "test session starts"
```

**Blocking Criteria**: 100% tests must pass

### 2.2 Code Coverage
- [ ] Overall coverage ≥ 70%
- [ ] No critical paths uncovered
- [ ] Coverage report generated

**Commands**:
```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
open htmlcov/index.html
```

**Blocking Criteria**: Coverage ≥ 70%

### 2.3 Linting
- [ ] Ruff linting passes: `ruff check .`
- [ ] Black formatting passes: `black --check .`
- [ ] isort import sorting passes: `isort --check-only .`

**Commands**:
```bash
ruff check src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
```

**Warning Criteria**: Zero linting errors

### 2.4 Type Checking
- [ ] Mypy type checking passes
- [ ] Zero type errors in src/

**Commands**:
```bash
mypy src/ --strict
```

**Warning Criteria**: Zero type errors

---

## Phase 3: Security Scanning ✅

### 3.1 Dependency Audit
- [ ] No known vulnerabilities: `pip-audit`
- [ ] All dependencies up to date
- [ ] No deprecated packages

**Commands**:
```bash
pip-audit
pip list --outdated
```

**Blocking Criteria**: Zero high/critical vulnerabilities

### 3.2 Code Security
- [ ] Bandit security scan passes
- [ ] No hardcoded secrets
- [ ] No SQL injection vulnerabilities

**Commands**:
```bash
bandit -r src/ -ll
git secrets --scan
```

**Blocking Criteria**: Zero high-severity issues

---

## Phase 4: Documentation Verification ✅

### 4.1 README Accuracy
- [ ] Installation instructions tested
- [ ] Usage examples work
- [ ] All badges up to date
- [ ] Links valid

### 4.2 API Documentation
- [ ] Docstrings complete for public APIs
- [ ] Sphinx docs build without errors
- [ ] Examples in docs are tested

**Commands**:
```bash
sphinx-build -W docs/ docs/_build/
```

### 4.3 CHANGELOG
- [ ] All changes documented
- [ ] Version number matches release
- [ ] Release date added

---

## Phase 5: Build Validation ✅

### 5.1 Build Package
- [ ] Source distribution builds: `python -m build`
- [ ] Wheel builds successfully
- [ ] No build warnings

**Commands**:
```bash
python -m build
ls -lh dist/
```

### 5.2 Package Validation
- [ ] Twine check passes: `twine check dist/*`
- [ ] Package metadata correct
- [ ] README renders on PyPI preview

**Commands**:
```bash
twine check dist/*
python -m readme_renderer README.md -o /tmp/readme.html
```

**Blocking Criteria**: twine check must pass

---

## Phase 6: Installation Testing ✅

### 6.1 Clean Environment Test
- [ ] Create fresh virtual environment
- [ ] Install from built wheel
- [ ] Import package successfully
- [ ] Run basic functionality test

**Commands**:
```bash
python -m venv /tmp/test-env
source /tmp/test-env/bin/activate
pip install dist/codex_ml-*.whl
python -c "import codex_ml; print(codex_ml.__version__)"
deactivate
rm -rf /tmp/test-env
```

### 6.2 Platform Compatibility
- [ ] Test on Linux
- [ ] Test on macOS (if available)
- [ ] Test on Windows (if available)
- [ ] Test Python 3.10, 3.11, 3.12

---

## Phase 7: TestPyPI Validation ✅

### 7.1 Upload to TestPyPI
- [ ] Upload successful
- [ ] Package visible on TestPyPI
- [ ] Package page renders correctly

**Commands**:
```bash
twine upload --repository testpypi dist/*
# Visit: https://test.pypi.org/project/codex-ml/
```

### 7.2 Install from TestPyPI
- [ ] Install in clean environment
- [ ] All dependencies resolve
- [ ] Package works as expected

**Commands**:
```bash
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            codex-ml
```

---

## Phase 8: Release Artifacts ✅

### 8.1 Git Tagging
- [ ] Create annotated tag
- [ ] Tag message includes changelog excerpt
- [ ] Tag pushed to origin

**Commands**:
```bash
git tag -a v0.1.0 -m "Release v0.1.0

- Feature 1
- Feature 2
- Bug fixes"
git push origin v0.1.0
```

### 8.2 GitHub Release
- [ ] Create GitHub Release
- [ ] Upload wheel and source dist
- [ ] Include changelog in release notes
- [ ] Mark as pre-release if applicable

---

## Phase 9: Monitoring Setup ✅

### 9.1 PyPI Analytics
- [ ] Monitor download statistics
- [ ] Set up alerts for issues
- [ ] Track user feedback

### 9.2 Issue Tracking
- [ ] GitHub Issues ready for bug reports
- [ ] Contribution guidelines updated
- [ ] Support channels documented

---

## Phase 10: Post-Release Validation ✅

### 10.1 Production PyPI
- [ ] Package visible on PyPI
- [ ] Package page renders correctly
- [ ] README displays properly
- [ ] All metadata correct

### 10.2 Installation Verification
- [ ] Install from PyPI works
- [ ] All dependencies resolve
- [ ] Basic functionality confirmed

**Commands**:
```bash
pip install codex-ml
python -c "import codex_ml; print(codex_ml.__version__)"
```

---

## Quality Gate Summary

### Blocking Gates (MUST Pass)
1. ✅ All tests passing (1500+ tests)
2. ✅ Coverage ≥ 70%
3. ✅ Zero high/critical security vulnerabilities
4. ✅ Build successful
5. ✅ Twine check passes
6. ✅ TestPyPI upload successful
7. ✅ Version synchronized across all files

### Warning Gates (SHOULD Pass)
1. ⚠️ Zero linting errors
2. ⚠️ Zero type errors
3. ⚠️ Documentation complete
4. ⚠️ CHANGELOG updated

### Info Gates (Good to Have)
1. ℹ️ All platforms tested
2. ℹ️ GitHub Release created
3. ℹ️ Monitoring configured

---

## Emergency Override

If blocking gates fail but release is critical:
1. Document reason for override in GitHub Issue
2. Create rollback plan
3. Notify team of known issues
4. Plan immediate follow-up release

---

## Checklist Completion

**Pre-Release**: ⬜ All checks complete  
**TestPyPI**: ⬜ Validated successfully  
**Production**: ⬜ Ready for PyPI upload  

**Approved By**: _________________  
**Date**: _________________  
**Release Version**: v_________________

---

**Last Updated**: 2026-01-23  
**Status**: Production Ready
