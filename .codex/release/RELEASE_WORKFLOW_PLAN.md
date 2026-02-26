# Release Workflow Plan

**Version**: 1.0.0  
**Date**: 2026-01-23  
**Status**: Production Ready  
**Automation Level**: 70%

---

## Overview

This document defines the complete automated release workflow for `codex-ml` package, integrating with GitHub Actions, GitLab CI/CD, and providing manual procedures.

---

## Workflow Architecture

```
┌─────────────┐
│   Trigger   │ (Manual or Tag)
└──────┬──────┘
       │
       v
┌─────────────────┐
│   Validation    │ (Tests, Linting, Security)
└────────┬────────┘
         │
         v
┌─────────────────┐
│     Build       │ (Source + Wheel)
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Package Test    │ (Twine Check, Install Test)
└────────┬────────┘
         │
         v
┌─────────────────┐
│   TestPyPI      │ (Test Upload)
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Approval Gate   │ (Manual Review)
└────────┬────────┘
         │
         v
┌─────────────────┐
│   PyPI Upload   │ (Production)
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Post-Release   │ (Verification, Monitoring)
└─────────────────┘
```

---

## Phase 1: Trigger Mechanisms

### Automatic Triggers
- **GitHub Release Published**: Triggers full production workflow
- **Tag Push**: `v*.*.*` pattern triggers workflow
- **Pull Request**: Runs validation only (no publish)

### Manual Triggers
- **Workflow Dispatch**: Manual execution with environment selection
- **Re-run Failed Jobs**: Retry individual stages

**GitHub Actions Configuration**:
```yaml
on:
  release:
    types: [published]
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - testpypi
          - pypi
```

---

## Phase 2: Validation (Automated)

### 2.1 Test Suite Execution
**Duration**: 3-5 pre-commits  
**Automation**: 100%

```yaml
- name: Run Tests
  run: |
    pytest tests/ -v --cov=src --cov-report=xml --cov-report=term

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

**Success Criteria**:
- All tests pass (≥1500 tests)
- Coverage ≥ 70%
- Zero failures

### 2.2 Code Quality
**Duration**: 1-2 pre-commits  
**Automation**: 100%

```yaml
- name: Lint with Ruff
  run: ruff check src/ tests/

- name: Format Check
  run: black --check src/ tests/

- name: Type Check
  run: mypy src/ --strict
```

### 2.3 Security Scanning
**Duration**: 1-2 pre-commits  
**Automation**: 100%

```yaml
- name: Security Audit
  run: |
    pip-audit
    bandit -r src/ -ll

- name: Secret Scanning
  run: git secrets --scan
```

---

## Phase 3: Build (Automated)

### 3.1 Package Building
**Duration**: 1 pre-commit  
**Automation**: 100%

```yaml
- name: Build Package
  run: |
    python -m build
    ls -lh dist/

- name: Store Build Artifacts
  uses: actions/upload-artifact@v4
  with:
    name: python-package-distributions
    path: dist/
```

**Output**:
- `codex_ml-*.tar.gz` (source distribution)
- `codex_ml-*-py3-none-any.whl` (wheel)

---

## Phase 4: Package Testing (Automated)

### 4.1 Package Validation
**Duration**: 1 pre-commit  
**Automation**: 100%

```yaml
- name: Check Package
  run: |
    twine check dist/*
    python -m readme_renderer README.md -o /tmp/readme.html
```

### 4.2 Installation Test
**Duration**: 1 pre-commit  
**Automation**: 100%

```yaml
- name: Test Installation
  run: |
    python -m venv /tmp/test-env
    source /tmp/test-env/bin/activate
    pip install dist/*.whl
    python -c "import codex_ml; print(codex_ml.__version__)"
    deactivate
```

---

## Phase 5: TestPyPI Upload (Automated)

### 5.1 Upload to TestPyPI
**Duration**: 1 pre-commit  
**Automation**: 100%  
**Trigger**: Workflow dispatch or develop branch

```yaml
publish-testpypi:
  needs: [build, test]
  runs-on: ubuntu-latest
  environment:
    name: testpypi
    url: https://test.pypi.org/p/codex-ml

  steps:
    - name: Download Artifacts
      uses: actions/download-artifact@v4
      with:
        name: python-package-distributions
        path: dist/

    - name: Publish to TestPyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        repository-url: https://test.pypi.org/legacy/
        password: ${{ secrets.TEST_PYPI_API_TOKEN }}
        skip-existing: true
```

### 5.2 TestPyPI Verification
**Duration**: 1-2 pre-commits  
**Automation**: 90%

```yaml
- name: Verify TestPyPI Installation
  run: |
    pip install --index-url https://test.pypi.org/simple/ \
                --extra-index-url https://pypi.org/simple/ \
                codex-ml
    python -c "import codex_ml; assert codex_ml.__version__ is not None"
```

---

## Phase 6: Approval Gate (Manual)

### 6.1 Manual Review
**Duration**: Variable (human approval)  
**Automation**: 0%

**Review Checklist**:
- [ ] All automated checks passed
- [ ] TestPyPI package verified
- [ ] CHANGELOG reviewed
- [ ] No critical issues reported
- [ ] Team notified of upcoming release

**Approval Process**:
1. Review GitHub Actions workflow results
2. Check TestPyPI package page
3. Verify installation from TestPyPI
4. Approve workflow continuation

### 6.2 Production Readiness
**Environment Protection**:
```yaml
environment:
  name: pypi-production
  protection_rules:
    required_reviewers: 1
    deployment_branches: tags
```

---

## Phase 7: PyPI Upload (Automated with Approval)

### 7.1 Production Upload
**Duration**: 1 pre-commit  
**Automation**: 100% (after approval)

```yaml
publish-pypi:
  needs: [build, test, publish-testpypi]
  runs-on: ubuntu-latest
  environment:
    name: pypi-production
    url: https://pypi.org/p/codex-ml

  steps:
    - name: Download Artifacts
      uses: actions/download-artifact@v4
      with:
        name: python-package-distributions
        path: dist/

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
        skip-existing: false
```

### 7.2 OIDC Trusted Publishing (Alternative)
**Zero Secrets Required**:

```yaml
publish-pypi-oidc:
  permissions:
    id-token: write

  steps:
    - name: Publish to PyPI (OIDC)
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        # No password needed - uses OIDC
```

---

## Phase 8: Post-Release (Automated)

### 8.1 Release Verification
**Duration**: 2-3 pre-commits  
**Automation**: 100%

```yaml
- name: Verify PyPI Publication
  run: |
    sleep 60  # Wait for PyPI to process
    pip install codex-ml==${{ github.ref_name }}
    python -c "import codex_ml; print(f'Released: {codex_ml.__version__}')"
```

### 8.2 GitHub Release
**Duration**: 1 pre-commit  
**Automation**: 100%

```yaml
- name: Create GitHub Release
  uses: softprops/action-gh-release@v1
  with:
    files: dist/*
    body_path: CHANGELOG.md
    draft: false
    prerelease: false
```

### 8.3 Notifications
**Duration**: 1 pre-commit  
**Automation**: 100%

```yaml
- name: Notify Team
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"codex-ml ${{ github.ref_name }} released to PyPI!"}'
```

---

## Version Management Strategy

### Semantic Versioning
- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backwards compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (e.g., 1.0.0 → 1.0.1)

### Version Bumping Script
```bash
#!/bin/bash
# scripts/bump_version.sh

CURRENT_VERSION=$(grep '__version__' src/codex_ml/__init__.py | cut -d'"' -f2)
echo "Current version: $CURRENT_VERSION"

case "$1" in
  major)
    NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1+1".0.0"}')
    ;;
  minor)
    NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."$2+1".0"}')
    ;;
  patch)
    NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."$2"."$3+1}')
    ;;
  *)
    echo "Usage: $0 {major|minor|patch}"
    exit 1
    ;;
esac

echo "New version: $NEW_VERSION"

# Update files
sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" src/codex_ml/__init__.py
sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Commit changes
git add src/codex_ml/__init__.py pyproject.toml
git commit -m "chore: bump version to $NEW_VERSION"

echo "Version bumped to $NEW_VERSION"
```

---

## Changelog Generation

### Automated Changelog Script
```bash
#!/bin/bash
# scripts/generate_changelog.sh

git log $(git describe --tags --abbrev=0)..HEAD --oneline --pretty=format:"- %s (%h)" > /tmp/changelog.txt

cat << EOF >> CHANGELOG.md

## [$1] - $(date +%Y-%m-%d)

### Added
$(grep "feat:" /tmp/changelog.txt || echo "- No new features")

### Changed
$(grep "refactor:\|perf:" /tmp/changelog.txt || echo "- No changes")

### Fixed
$(grep "fix:" /tmp/changelog.txt || echo "- No fixes")

### Security
$(grep "security:" /tmp/changelog.txt || echo "- No security updates")

EOF

echo "Changelog updated for version $1"
```

---

## Rollback Procedures

### Scenario 1: Bad PyPI Upload
**Detection**: Package doesn't install or has critical bug  
**Action**: Upload new patch version immediately

```bash
# 1. Fix bug
# 2. Bump patch version
./scripts/bump_version.sh patch

# 3. Run tests
pytest tests/

# 4. Build and upload
python -m build
twine upload dist/*
```

### Scenario 2: Breaking Change
**Detection**: Users report breaking changes  
**Action**: Yank version on PyPI, release hotfix

```bash
# Yank bad version
python -m twine yank codex-ml <version>

# Release hotfix
./scripts/bump_version.sh patch
# ... build and upload
```

### Scenario 3: Security Vulnerability
**Detection**: Security scan reveals vulnerability  
**Action**: Immediate hotfix release

**Timeline**: 1-2 Phases maximum

---

## CI/CD Integration Matrix

| Platform | Configuration File | Status |
|----------|-------------------|--------|
| GitHub Actions | `.github/workflows/pypi-publish.yml` | ✅ Implemented |
| GitLab CI/CD | `.gitlab-ci.yml` | ✅ Guide provided |
| CircleCI | `.circleci/config.yml` | ⚠️ Not implemented |
| Travis CI | `.travis.yml` | ⚠️ Not implemented |

---

## Success Metrics

### Release Metrics
- **Build Time**: Target < 5 pre-commits
- **Test Pass Rate**: Target 100%
- **Release Frequency**: Target 1 per 4-6 Phases
- **Rollback Rate**: Target < 5%

### Quality Metrics
- **Coverage**: Maintain ≥ 70%
- **Security**: Zero high/critical vulnerabilities
- **Documentation**: 100% API coverage

---

## Emergency Override

### When to Override
- Critical security fix needed immediately
- Production system down
- Data loss risk

### Override Process
1. Document reason in GitHub Issue
2. Get approval from 2+ maintainers
3. Skip TestPyPI (go direct to PyPI)
4. Monitor closely post-release
5. Schedule immediate retrospective

**Override Command**:
```bash
gh workflow run pypi-publish.yml \
  -f environment=pypi \
  -f override=true \
  -f reason="Critical security fix CVE-2024-XXXXX"
```

---

## Monitoring and Alerts

### Post-Release Monitoring
- PyPI download statistics
- GitHub issue rate
- User feedback channels
- Security vulnerability scans

### Alert Conditions
- Download count drops > 50%
- Issue rate increases > 3x
- Security vulnerability detected
- Installation failures reported

---

**Last Updated**: 2026-01-23  
**Status**: Production Ready  
**Automation Level**: 70% (30% manual approval gates)
