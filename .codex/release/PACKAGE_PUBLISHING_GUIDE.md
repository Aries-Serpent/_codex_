# Package Publishing Guide

**Version**: 1.0.0  
**Date**: 2026-01-23  
**Audience**: Release Managers, DevOps Engineers, Repository Maintainers

---

## Overview

This comprehensive guide covers all aspects of publishing the `codex-ml` package to PyPI (Python Package Index), from initial setup through production release and troubleshooting.

---

## Prerequisites

### Required Tools
```bash
pip install build twine pip-audit
```

### Required Accounts
1. **PyPI Account**: https://pypi.org/account/register/
2. **TestPyPI Account**: https://test.pypi.org/account/register/
3. **GitHub Account**: With repository access

---

## Part 1: Initial Setup

### 1.1 PyPI Account Setup

**Create Production PyPI Account**:
1. Visit https://pypi.org/account/register/
2. Verify email address
3. Enable 2FA (strongly recommended)
4. Complete profile

**Create TestPyPI Account**:
1. Visit https://test.pypi.org/account/register/
2. Verify email address (can use same as PyPI)
3. Enable 2FA
4. Complete profile

### 1.2 API Token Generation

**Generate PyPI Token**:
1. Login to https://pypi.org
2. Navigate to Account Settings → API tokens
3. Click "Add API token"
4. Configuration:
   - Token name: `codex-ml-github-actions`
   - Scope: `Project: codex-ml` (after first upload) or `Entire account` (first time)
5. **Copy token immediately** (only shown once)
6. Format: `pypi-AgEIcH...`

**Generate TestPyPI Token**:
1. Login to https://test.pypi.org
2. Repeat above steps
3. Token name: `codex-ml-test-github-actions`

### 1.3 Store Tokens Securely

**GitHub Secrets** (Recommended):
```bash
# Navigate to repository Settings → Secrets and variables → Actions
# Add new repository secret:
Name: PYPI_API_TOKEN
Value: pypi-AgEI...

# Add TestPyPI token:
Name: TEST_PYPI_API_TOKEN
Value: pypi-AgEI...
```

**Local Configuration** (For manual uploads):
```bash
# Create ~/.pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEI...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEI...
EOF

chmod 600 ~/.pypirc
```

---

## Part 2: Package Preparation

### 2.1 Version Management

**Update Version**:
```python
# src/codex_ml/__init__.py
__version__ = "0.1.0"

# pyproject.toml (line 70)
version = "0.1.0"
```

**Version Strategy**:
- **Development**: `0.x.y` (not production-ready)
- **Stable**: `1.x.y` (production-ready)
- **Pre-releases**: `1.0.0a1`, `1.0.0b1`, `1.0.0rc1`

### 2.2 Build Package

**Create Distributions**:
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build

# Verify output
ls -lh dist/
# Expected:
# codex_ml-0.1.0.tar.gz
# codex_ml-0.1.0-py3-none-any.whl
```

### 2.3 Validate Package

**Run Twine Check**:
```bash
twine check dist/*
```

**Expected Output**:
```
Checking dist/codex_ml-0.1.0.tar.gz: PASSED
Checking codex_ml-0.1.0-py3-none-any.whl: PASSED
```

---

## Part 3: TestPyPI Workflow

### 3.1 Upload to TestPyPI

**Manual Upload**:
```bash
twine upload --repository testpypi dist/*
```

**Workflow Upload** (GitHub Actions):
```bash
# Trigger workflow
gh workflow run pypi-publish.yml -f environment=testpypi
```

**Verify Upload**:
- Visit: https://test.pypi.org/project/codex-ml/
- Check version number
- Verify README renders correctly
- Check package metadata

### 3.2 Test Installation from TestPyPI

**Create Clean Environment**:
```bash
python -m venv /tmp/test-install
source /tmp/test-install/bin/activate
```

**Install from TestPyPI**:
```bash
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            codex-ml
```

**Note**: `--extra-index-url` needed for dependencies not on TestPyPI

**Verify Installation**:
```bash
python -c "import codex_ml; print(codex_ml.__version__)"
python -c "from codex_ml import __version__; assert __version__ == '0.1.0'"
```

**Deactivate**:
```bash
deactivate
rm -rf /tmp/test-install
```

### 3.3 TestPyPI Troubleshooting

**Issue**: Package already exists
```
HTTPError: 400 Bad Request
File already exists.
```
**Solution**: Bump version number or use `--skip-existing`

**Issue**: Dependencies not found
```
ERROR: Could not find a version that satisfies the requirement X
```
**Solution**: Add `--extra-index-url https://pypi.org/simple/`

---

## Part 4: Production PyPI Publishing

### 4.1 Final Pre-Release Checks

**Quality Gates**:
- [ ] All tests passing (≥1500 tests)
- [ ] Coverage ≥ 70%
- [ ] Zero high/critical vulnerabilities
- [ ] Documentation complete
- [ ] CHANGELOG updated
- [ ] TestPyPI validation successful
- [ ] Version synchronized across all files

### 4.2 Upload to PyPI

**Manual Upload**:
```bash
twine upload dist/*
```

**Enter credentials when prompted** (or use ~/.pypirc)

**Workflow Upload** (Recommended):
```bash
# Create GitHub Release
gh release create v0.1.0 \
  --title "Release v0.1.0" \
  --notes "$(cat CHANGELOG.md | sed -n '/^## \[0.1.0\]/,/^## \[/p' | head -n -1)"

# Workflow triggers automatically
```

### 4.3 Verify Production Upload

**Check PyPI Page**:
- Visit: https://pypi.org/project/codex-ml/
- Verify version matches
- Check README renders correctly
- Verify all metadata correct

**Test Installation**:
```bash
# Clean environment
python -m venv /tmp/prod-test
source /tmp/prod-test/bin/activate

# Install from PyPI
pip install codex-ml

# Verify
python -c "import codex_ml; print(codex_ml.__version__)"
```

---

## Part 5: OIDC Trusted Publishing

### 5.1 OIDC Setup (Token-less Publishing)

**Advantages**:
- No API tokens to manage
- Short-lived credentials
- Automatic rotation
- More secure

**PyPI Configuration**:
1. Login to https://pypi.org
2. Navigate to project → Settings → Publishing
3. Click "Add a new publisher"
4. Select "GitHub Actions"
5. Enter:
   - Owner: `Aries-Serpent`
   - Repository: `_codex_`
   - Workflow: `pypi-publish.yml`
   - Environment: `pypi-production` (optional)

### 5.2 Workflow Configuration for OIDC

**Update GitHub Actions**:
```yaml
permissions:
  id-token: write  # Required for OIDC
  contents: read

publish-pypi:
  steps:
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      # No password needed - uses OIDC
```

---

## Part 6: Package Management

### 6.1 Updating Existing Package

**Release New Version**:
```bash
# 1. Update version
./scripts/bump_version.sh minor  # or major, patch

# 2. Update CHANGELOG
# Edit CHANGELOG.md

# 3. Run tests
pytest tests/

# 4. Build
python -m build

# 5. Test on TestPyPI
twine upload --repository testpypi dist/*

# 6. Upload to PyPI
twine upload dist/*
```

### 6.2 Yanking a Release

**When to Yank**:
- Critical bug discovered
- Security vulnerability
- Breaking changes undiscovered

**How to Yank**:
```bash
# Using twine (not available yet)
# Manual: PyPI web interface

# 1. Login to https://pypi.org
# 2. Navigate to project → Releases → [version]
# 3. Click "Options" → "Yank release"
# 4. Provide reason
```

**Note**: Yanked releases still installable with explicit version:
```bash
pip install codex-ml==0.1.0  # Works even if yanked
pip install codex-ml  # Won't install yanked version
```

### 6.3 Deleting a Release

**Warning**: ⚠️ **Deletion is permanent and breaks existing installations**

**When to Delete** (rare):
- Accidentally uploaded with secrets/credentials
- Legal/DMCA requirement
- Malicious code detected

**How to Delete**:
1. Contact PyPI support
2. Provide justification
3. Wait for manual review

---

## Part 7: Troubleshooting

### 7.1 Common Upload Issues

**Issue 1: Authentication Failed**
```
HTTPError: 403 Forbidden
Invalid or non-existent authentication information.
```
**Solutions**:
- Verify token is correct (including `pypi-` prefix)
- Check token hasn't expired
- Verify token scope includes project
- Re-generate token if needed

**Issue 2: Package Name Conflict**
```
HTTPError: 400 Bad Request
The name 'codex-ml' is too similar to an existing project.
```
**Solutions**:
- Choose different package name
- Contact PyPI support for name reclamation (if abandoned)
- Use organization prefix: `aries-codex-ml`

**Issue 3: File Size Limit**
```
HTTPError: 400 Bad Request
File size exceeds maximum (100 MB).
```
**Solutions**:
- Remove large files from package
- Use `.gitignore` for data files
- Host large files separately (GitHub releases, S3)
- Use `MANIFEST.in` to exclude files

**Issue 4: Metadata Issues**
```
HTTPError: 400 Bad Request
Invalid metadata.
```
**Solutions**:
- Run `twine check dist/*`
- Verify `pyproject.toml` syntax
- Check README renders: `python -m readme_renderer README.md`

### 7.2 Installation Issues

**Issue 1: Import Fails**
```python
ModuleNotFoundError: No module named 'codex_ml'
```
**Solutions**:
- Verify installation: `pip list | grep codex`
- Check package structure
- Verify `__init__.py` exists
- Use correct import name

**Issue 2: Dependency Conflicts**
```
ERROR: Cannot install due to conflicting dependencies
```
**Solutions**:
- Update `pyproject.toml` dependency versions
- Use more flexible version constraints: `>=1.0,<2.0`
- Test with clean virtual environment

---

## Part 8: Security Best Practices

### 8.1 Token Management

**Do**:
- ✅ Store tokens in GitHub Secrets
- ✅ Use OIDC when possible
- ✅ Set token scope to single project
- ✅ Rotate tokens every 90 days
- ✅ Revoke tokens immediately if compromised

**Don't**:
- ❌ Commit tokens to repository
- ❌ Share tokens in chat/email
- ❌ Use account-wide tokens
- ❌ Store tokens in plain text files

### 8.2 Package Security

**Pre-Release Security**:
```bash
# Scan for secrets
git secrets --scan

# Security audit
pip-audit

# Vulnerability scan
bandit -r src/ -ll

# Check dependencies
safety check
```

### 8.3 Post-Release Monitoring

**Monitor For**:
- Unexpected download spikes
- User-reported issues
- Security vulnerability reports
- Dependency updates

**Tools**:
- PyPI download statistics
- GitHub Security Advisories
- Dependabot alerts
- snyk.io monitoring

---

## Part 9: Rollback Procedures

### 9.1 Scenario 1: Bad Release (Minor Bug)

**Timeline**: 1-2 Phases

**Steps**:
```bash
# 1. Acknowledge issue
# Create GitHub issue documenting problem

# 2. Fix bug
git checkout -b hotfix/bug-fix
# ... make fixes ...
git commit -m "fix: critical bug in feature X"

# 3. Bump patch version
./scripts/bump_version.sh patch

# 4. Fast-track release
python -m build
twine upload dist/*

# 5. Notify users
# Post on GitHub, PyPI, documentation site
```

### 9.2 Scenario 2: Critical Security Issue

**Timeline**: Immediate (< 1 Phase)

**Steps**:
```bash
# 1. IMMEDIATELY yank bad version
# Via PyPI web interface

# 2. Fix vulnerability
# ... security patch ...

# 3. Emergency release
./scripts/bump_version.sh patch
python -m build
twine upload dist/*

# 4. Security advisory
# Publish CVE if applicable
# Notify all users via multiple channels
```

### 9.3 Scenario 3: Breaking Change

**Timeline**: 2-3 Phases

**Steps**:
```bash
# 1. Yank problematic version
# 2. Release fixed version with proper migration guide
# 3. Update documentation with breaking changes
# 4. Provide migration script if possible
```

---

## Part 10: Advanced Topics

### 10.1 Pre-Release Versions

**Alpha Release** (`a`):
```bash
# For early testing
__version__ = "1.0.0a1"
```

**Beta Release** (`b`):
```bash
# For wider testing
__version__ = "1.0.0b1"
```

**Release Candidate** (`rc`):
```bash
# Final testing before stable
__version__ = "1.0.0rc1"
```

**Install Pre-Release**:
```bash
pip install --pre codex-ml
```

### 10.2 Multi-Platform Wheels

**Current**: Pure Python (`py3-none-any`)  
**Advanced**: Platform-specific wheels

For packages with C extensions:
```bash
# Build for multiple platforms
python setup.py bdist_wheel --plat-name manylinux2014_x86_64
python setup.py bdist_wheel --plat-name macosx_10_9_x86_64
python setup.py bdist_wheel --plat-name win_amd64
```

### 10.3 Package Signing

**GPG Signing**:
```bash
# Generate GPG key
gpg --gen-key

# Sign package
gpg --detach-sign -a dist/codex_ml-0.1.0.tar.gz

# Upload signature
twine upload dist/* dist/*.asc
```

---

## Quick Reference

### Essential Commands
```bash
# Build
python -m build

# Validate
twine check dist/*

# TestPyPI
twine upload --repository testpypi dist/*

# Production
twine upload dist/*

# Verify
pip install codex-ml
python -c "import codex_ml; print(codex_ml.__version__)"
```

### Useful Links
- PyPI: https://pypi.org/project/codex-ml/
- TestPyPI: https://test.pypi.org/project/codex-ml/
- Packaging Guide: https://packaging.python.org
- Twine Docs: https://twine.readthedocs.io

---

**Last Updated**: 2026-01-23  
**Status**: Production Ready  
**Version**: 1.0.0
