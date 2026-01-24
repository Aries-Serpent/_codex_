# Release Runbook

**Version**: 1.0.0  
**Date**: 2026-01-23  
**Purpose**: Step-by-step manual execution guide for releases

---

## Overview

This runbook provides detailed, copy-paste-ready procedures for executing releases of the `codex-ml` package. Designed for repository maintainers performing manual releases.

---

## Standard Release Procedure

**Duration**: 6-8 pre-commits  
**Use For**: Regular feature releases, minor updates

### Step 1: Preparation (1 pre-commit)

**1.1 Create Release Branch**:
```bash
git checkout main
git pull origin main
git checkout -b release/v0.1.0
```

**1.2 Update Version**:
```bash
# Edit src/codex_ml/__init__.py
# Change: __version__ = "0.0.0"
# To: __version__ = "0.1.0"

# Edit pyproject.toml line 70
# Change: version = "0.0.0"  
# To: version = "0.1.0"
```

**1.3 Update CHANGELOG**:
```bash
# Add to CHANGELOG.md:
cat >> CHANGELOG.md << 'EOF'

## [0.1.0] - $(date +%Y-%m-%d)

### Added
- Feature A
- Feature B

### Changed
- Improvement X

### Fixed
- Bug Y

EOF
```

### Step 2: Quality Validation (2-3 pre-commits)

**2.1 Run Full Test Suite**:
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

**Expected**: ≥1500 tests pass, coverage ≥70%

**2.2 Run Linting**:
```bash
ruff check src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
mypy src/ --strict
```

**2.3 Security Scan**:
```bash
pip-audit
bandit -r src/ -ll
git secrets --scan
```

### Step 3: Build Package (1 pre-commit)

**3.1 Clean Previous Builds**:
```bash
rm -rf dist/ build/ *.egg-info
```

**3.2 Build Distributions**:
```bash
python -m build
```

**3.3 Validate**:
```bash
twine check dist/*
ls -lh dist/
```

**Expected Output**:
```
codex_ml-0.1.0.tar.gz
codex_ml-0.1.0-py3-none-any.whl
```

### Step 4: TestPyPI Upload (1 pre-commit)

**4.1 Upload to TestPyPI**:
```bash
twine upload --repository testpypi dist/*
```

**4.2 Verify Upload**:
```bash
# Visit: https://test.pypi.org/project/codex-ml/
# Check version, README rendering
```

**4.3 Test Installation**:
```bash
python -m venv /tmp/test-env
source /tmp/test-env/bin/activate
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            codex-ml==0.1.0
python -c "import codex_ml; print(codex_ml.__version__)"
deactivate
rm -rf /tmp/test-env
```

### Step 5: Create Release PR (1 pre-commit)

**5.1 Commit Changes**:
```bash
git add src/codex_ml/__init__.py pyproject.toml CHANGELOG.md
git commit -m "chore: prepare release v0.1.0"
git push origin release/v0.1.0
```

**5.2 Create Pull Request**:
```bash
gh pr create \
  --title "Release v0.1.0" \
  --body "Prepare release v0.1.0

- Updated version numbers
- Updated CHANGELOG
- Validated on TestPyPI

Release checklist:
- [x] Tests passing
- [x] Coverage ≥70%
- [x] Security scan clean
- [x] TestPyPI validation successful
" \
  --base main
```

**5.3 Request Review**:
- Assign reviewers
- Wait for approval

### Step 6: Merge and Tag (1 pre-commit)

**6.1 Merge PR**:
```bash
# After approval
gh pr merge --merge
```

**6.2 Create Git Tag**:
```bash
git checkout main
git pull origin main
git tag -a v0.1.0 -m "Release v0.1.0

- Feature A
- Feature B
- Bug fix Y
"
git push origin v0.1.0
```

### Step 7: Production PyPI Upload (1 pre-commit)

**Option A: Automatic (Recommended)**:
```bash
# GitHub Actions workflow triggers automatically on tag push
# Monitor at: https://github.com/Aries-Serpent/_codex_/actions
```

**Option B: Manual**:
```bash
twine upload dist/*
```

**7.1 Verify Upload**:
```bash
# Visit: https://pypi.org/project/codex-ml/
# Verify version, README, metadata
```

**7.2 Test Installation**:
```bash
python -m venv /tmp/prod-test
source /tmp/prod-test/bin/activate
pip install codex-ml==0.1.0
python -c "import codex_ml; print(codex_ml.__version__)"
deactivate
rm -rf /tmp/prod-test
```

### Step 8: Create GitHub Release (1 pre-commit)

**8.1 Create Release**:
```bash
gh release create v0.1.0 \
  --title "Release v0.1.0" \
  --notes "$(sed -n '/^## \[0.1.0\]/,/^## \[/p' CHANGELOG.md | head -n -1)" \
  dist/*
```

**8.2 Announce**:
- Post on project channels
- Update documentation
- Notify users

---

## Hotfix Release Procedure

**Duration**: 2-3 pre-commits  
**Use For**: Critical bugs, security issues

### Quick Steps:

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-fix main

# 2. Fix bug
# ... make changes ...
git add .
git commit -m "fix: critical bug in feature X"

# 3. Bump patch version
# Edit __version__ to 0.1.1
# Edit pyproject.toml version to 0.1.1

# 4. Update CHANGELOG (minimal)
echo "## [0.1.1] - $(date +%Y-%m-%d)

### Fixed
- Critical bug in feature X
" >> CHANGELOG.md

# 5. Build and test
rm -rf dist/
python -m build
twine check dist/*

# 6. Upload to TestPyPI (optional, but recommended)
twine upload --repository testpypi dist/*

# 7. Create PR
gh pr create --title "Hotfix v0.1.1" --body "Critical bug fix" --base main

# 8. Merge and tag (after approval)
gh pr merge --merge
git checkout main && git pull
git tag -a v0.1.1 -m "Hotfix v0.1.1"
git push origin v0.1.1

# 9. Upload to PyPI (automatic or manual)
# Automatic: workflow triggers
# Manual: twine upload dist/*

# 10. Verify
pip install --upgrade codex-ml
```

---

## Pre-Release Procedure

**Duration**: 4-6 pre-commits  
**Use For**: Alpha, beta, release candidates

### Alpha Release (a1, a2, ...):

```bash
# Version: 1.0.0a1
__version__ = "1.0.0a1"

# Build and upload
python -m build
twine upload dist/*

# Install with:
pip install --pre codex-ml
```

### Beta Release (b1, b2, ...):

```bash
# Version: 1.0.0b1
__version__ = "1.0.0b1"

# Same process as alpha
```

### Release Candidate (rc1, rc2, ...):

```bash
# Version: 1.0.0rc1
__version__ = "1.0.0rc1"

# Same process, more thorough testing
```

---

## Rollback Procedures

### Rollback Scenario 1: Yank Bad Version

**When**: Minor bug, not critical

```bash
# 1. Yank on PyPI web interface
# Login to https://pypi.org/project/codex-ml/
# Navigate to version → Options → Yank

# 2. Release fixed version
./scripts/bump_version.sh patch
python -m build
twine upload dist/*
```

### Rollback Scenario 2: Emergency Hotfix

**When**: Critical bug or security issue

```bash
# Use Hotfix procedure above
# Skip TestPyPI if extremely urgent
# Notify all users immediately
```

### Rollback Scenario 3: Revert Breaking Change

**When**: Unexpected breaking change

```bash
# 1. Yank bad version
# 2. Revert changes
git revert <commit-hash>

# 3. Release fixed version
# Follow standard release procedure
```

---

## Troubleshooting

### Issue: Build Fails

**Symptoms**: `python -m build` errors

**Solutions**:
```bash
# Update build tools
pip install --upgrade build setuptools wheel

# Check pyproject.toml syntax
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Clean and retry
rm -rf dist/ build/ *.egg-info
python -m build
```

### Issue: TestPyPI Upload Fails

**Symptoms**: Authentication errors

**Solutions**:
```bash
# Verify token
cat ~/.pypirc | grep password

# Regenerate token
# Visit https://test.pypi.org → Account → API tokens

# Update ~/.pypirc
```

### Issue: Installation from TestPyPI Fails

**Symptoms**: Dependencies not found

**Solutions**:
```bash
# Use --extra-index-url
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            codex-ml
```

---

## Quick Reference Commands

```bash
# Version bump
./scripts/bump_version.sh {major|minor|patch}

# Build
python -m build

# Validate
twine check dist/*

# TestPyPI
twine upload --repository testpypi dist/*

# Production
twine upload dist/*

# Create tag
git tag -a v0.1.0 -m "Release v0.1.0"

# Create GitHub release
gh release create v0.1.0 --title "v0.1.0" --notes "..." dist/*
```

---

**Last Updated**: 2026-01-23  
**Status**: Production Ready
