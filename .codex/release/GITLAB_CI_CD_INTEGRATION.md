# GitLab CI/CD Integration for PyPI Publishing

**Version**: 1.0.0  
**Date**: 2026-01-23  
**Status**: Production Ready

---

## Overview

This guide provides comprehensive instructions for integrating PyPI publishing with GitLab CI/CD pipelines, including configuration for the `.gitlab-ci.yml` file, environment setup, and OpenID Connect (OIDC) trusted publishing.

---

## Prerequisites

1. **GitLab Account**: Repository hosted on GitLab
2. **PyPI Account**: Account on PyPI or TestPyPI
3. **GitLab CI/CD**: Enabled for your project
4. **Python Package**: Valid `pyproject.toml` or `setup.py`

---

## GitLab Configuration

### Project Information

**Required Information**:
1. **GitLab Username/Namespace**: The user or group that owns the project
   - Format: `username` or `groupname/subgroupname`
   - Example: `aries-serpent` or `aries-serpent/codex-team`
   - Find at: Project → Settings → General → Project name

2. **Pipeline File Path**: Relative path from repository root
   - Standard: `.gitlab-ci.yml`
   - Custom: `.gitlab/ci/pipeline.yml` (configure in Settings → CI/CD → General pipelines)
   - **Note**: External pipelines are NOT supported by PyPI OIDC

3. **Environment Name** (Recommended):
   - Standard: `pypi-production` or `pypi-publishing`
   - Configure at: Project → Settings → CI/CD → Environments
   - Provides additional security by restricting who can publish

---

## GitLab CI/CD Pipeline Configuration

### Complete `.gitlab-ci.yml` Example

```yaml
# .gitlab-ci.yml - PyPI Publishing Pipeline
# Repository: aries-serpent/codex-ml (example)
# Pipeline File: .gitlab-ci.yml

stages:
  - build
  - test
  - publish
  - verify

variables:
  PACKAGE_NAME: "codex-ml"
  PYTHON_VERSION: "3.12"

# Build Stage: Create distribution packages
build-package:
  stage: build
  image: python:${PYTHON_VERSION}
  script:
    - python -m pip install --upgrade pip
    - pip install build twine
    - python -m build
    - twine check dist/*
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - tags
    - main
    - develop

# Test Stage: Validate package integrity
test-package:
  stage: test
  image: python:${PYTHON_VERSION}
  dependencies:
    - build-package
  script:
    - pip install dist/*.whl
    - python -c "import codex_ml; print(f'Version: {codex_ml.__version__}')"
    - python -c "from codex_ml import __version__; assert __version__ is not None"
  only:
    - tags
    - main

# Publish Stage: Upload to TestPyPI (for testing)
publish-testpypi:
  stage: publish
  image: python:${PYTHON_VERSION}
  dependencies:
    - build-package
  environment:
    name: testpypi
    url: https://test.pypi.org/p/${PACKAGE_NAME}
  script:
    - pip install twine
    - >
      twine upload
      --repository testpypi
      --username __token__
      --password ${TEST_PYPI_API_TOKEN}
      --skip-existing
      dist/*
  only:
    - develop
    - /^v.*-rc.*$/  # Release candidates
  when: manual

# Publish Stage: Upload to Production PyPI
publish-pypi:
  stage: publish
  image: python:${PYTHON_VERSION}
  dependencies:
    - build-package
  environment:
    name: pypi-production
    url: https://pypi.org/p/${PACKAGE_NAME}
  script:
    - pip install twine
    - >
      twine upload
      --username __token__
      --password ${PYPI_API_TOKEN}
      dist/*
  only:
    - tags  # Only publish on version tags
    - /^v[0-9]+\.[0-9]+\.[0-9]+$/  # e.g., v1.0.0
  when: manual  # Require manual approval

# Verify Stage: Confirm successful publication
verify-installation:
  stage: verify
  image: python:${PYTHON_VERSION}
  needs:
    - publish-pypi
  script:
    - sleep 60  # Wait for PyPI to process
    - pip install ${PACKAGE_NAME}
    - python -c "import codex_ml; print(f'Installed version: {codex_ml.__version__}')"
  only:
    - tags
  when: on_success
```

---

## Secret Configuration

### Adding API Tokens to GitLab

**Navigate to**: Project → Settings → CI/CD → Variables

**Add Variables**:

1. **TEST_PYPI_API_TOKEN** (for TestPyPI):
   ```
   Type: Variable
   Key: TEST_PYPI_API_TOKEN
   Value: pypi-AgEI... (your TestPyPI token)
   Protected: Yes
   Masked: Yes
   Expand variable reference: No
   ```

2. **PYPI_API_TOKEN** (for Production PyPI):
   ```
   Type: Variable
   Key: PYPI_API_TOKEN
   Value: pypi-AgEI... (your production PyPI token)
   Protected: Yes
   Masked: Yes
   Expand variable reference: No
   Environment scope: pypi-production (optional but recommended)
   ```

**Token Generation**:
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

---

## Environment Configuration

### Creating Dedicated Publishing Environment

**Benefits**:
- Restricts publishing access to specific users
- Provides approval gates for production releases
- Maintains audit trail of publications

**Setup Steps**:

1. Navigate to: Project → Settings → CI/CD → Environments
2. Click "New environment"
3. Configure:
   ```
   Name: pypi-production
   External URL: https://pypi.org/p/codex-ml
   ```

4. Set Protection Rules:
   - Protected environments: Yes
   - Allowed to deploy: Maintainers only
   - Approval required: Optional (recommended for production)

---

## OIDC Trusted Publishing (Recommended)

### PyPI OIDC Configuration

**Advantages**:
- No API tokens needed
- More secure (short-lived credentials)
- Automatic authentication via GitLab

**Setup on PyPI**:

1. Go to PyPI → Account Settings → Publishing
2. Click "Add a new publisher"
3. Select "GitLab" as the provider
4. Enter:
   ```
   GitLab Username or Group: aries-serpent
   Repository Name: _codex_
   Workflow/Pipeline File: .gitlab-ci.yml
   Environment (optional): pypi-production
   ```

**Updated Pipeline** (No tokens needed):

```yaml
publish-pypi-oidc:
  stage: publish
  image: python:3.12
  id_tokens:
    PYPI_ID_TOKEN:
      aud: pypi
  dependencies:
    - build-package
  environment:
    name: pypi-production
    url: https://pypi.org/p/codex-ml
  script:
    - pip install twine
    - >
      twine upload
      --repository pypi
      --username __token__
      --password ${PYPI_ID_TOKEN}
      dist/*
  only:
    - tags
  when: manual
```

---

## ActiveState OIDC Support

### Configuration for ActiveState Platform

**Reference**: https://docs.activestate.com/platform/user/oidc/

**Setup Steps**:

1. **ActiveState Account**: Create at platform.activestate.com
2. **Organization Setup**: Create organization for your project
3. **OIDC Integration**: Navigate to Organization → Settings → OIDC
4. **Configure Provider**:
   ```
   Provider: GitLab
   Repository: aries-serpent/_codex_
   Pipeline: .gitlab-ci.yml
   Environment: activestate-production
   ```

**Pipeline Configuration**:

```yaml
publish-activestate:
  stage: publish
  image: python:3.12
  id_tokens:
    ACTIVESTATE_TOKEN:
      aud: activestate
  dependencies:
    - build-package
  environment:
    name: activestate-production
    url: https://platform.activestate.com/aries-serpent/codex-ml
  script:
    - pip install activestate-cli
    - state auth --token ${ACTIVESTATE_TOKEN}
    - state publish dist/*.whl
  only:
    - tags
  when: manual
```

---

## Usage Guide

### Manual Release Process

**Phase 1: Prepare Release** (2-3 pre-commits)
```bash
# Update version
# Update CHANGELOG.md
# Commit changes
git commit -m "Prepare release v1.0.0"
```

**Phase 2: Create Release Tag** (1 pre-commit)
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

**Phase 3: Monitor Pipeline** (1 pre-commit)
- GitLab will automatically trigger the pipeline
- Monitor at: Project → CI/CD → Pipelines
- Review build and test stages

**Phase 4: Approve Publication** (1 pre-commit)
- Navigate to paused `publish-pypi` job
- Review artifacts and test results
- Click "Play" to approve publication

**Phase 5: Verify Installation** (1 pre-commit)
```bash
# After pipeline completes
pip install codex-ml==1.0.0
python -c "import codex_ml; print(codex_ml.__version__)"
```

---

## Troubleshooting

### Common Issues

**1. Pipeline Fails at Build Stage**
```
Error: No module named 'build'
Solution: Ensure build dependencies installed in script
```

**2. Authentication Fails**
```
Error: 403 Invalid or non-existent authentication
Solution: Verify PYPI_API_TOKEN is correct and not expired
```

**3. Package Already Exists**
```
Error: File already exists
Solution: Increment version number or use --skip-existing
```

**4. OIDC Token Not Found**
```
Error: PYPI_ID_TOKEN not set
Solution: Ensure id_tokens block configured correctly
```

**5. Environment Not Found**
```
Error: Environment 'pypi-production' does not exist
Solution: Create environment in GitLab CI/CD settings
```

---

## Security Best Practices

### Token Management

1. **Use Environment-Scoped Variables**:
   - Restrict PYPI_API_TOKEN to pypi-production environment
   - Prevents accidental exposure in non-production jobs

2. **Enable Masking**:
   - All tokens must have "Masked" enabled
   - Prevents token leakage in logs

3. **Rotate Tokens Regularly**:
   - Generate new tokens every 90 days
   - Revoke old tokens immediately after rotation

4. **Prefer OIDC Over Tokens**:
   - OIDC provides short-lived credentials
   - Eliminates long-term token storage

### Pipeline Security

1. **Protected Tags Only**:
   ```yaml
   only:
     refs:
       - tags
     variables:
       - $CI_COMMIT_REF_PROTECTED == "true"
   ```

2. **Manual Approval for Production**:
   ```yaml
   when: manual
   ```

3. **Dedicated Environments**:
   - Separate environment for production
   - Restrict deployment permissions

---

## Integration Summary

### Configuration Checklist

- [ ] GitLab username/namespace identified
- [ ] Pipeline file path configured (.gitlab-ci.yml)
- [ ] PyPI/TestPyPI tokens generated
- [ ] Tokens added to GitLab CI/CD variables
- [ ] Publishing environment created (optional but recommended)
- [ ] OIDC configured on PyPI (optional)
- [ ] ActiveState account setup (if using ActiveState)
- [ ] Pipeline tested with TestPyPI
- [ ] Production publishing workflow validated

---

## Quick Reference

### Essential Paths

| Configuration | Path/Value |
|--------------|------------|
| **GitLab Namespace** | `aries-serpent` or `aries-serpent/subgroup` |
| **Pipeline File** | `.gitlab-ci.yml` (root of repository) |
| **Environment Name** | `pypi-production` (recommended) |
| **Variables Location** | Project → Settings → CI/CD → Variables |
| **Environments** | Project → Settings → CI/CD → Environments |

### Workflow File Location

**Path**: `.gitlab-ci.yml` (repository root)  
**Alternative**: `.gitlab/ci/pipeline.yml` (configure in Settings)

**Verification**:
```bash
ls -la .gitlab-ci.yml
# Should show file at repository root
```

---

## Next Steps

1. **Review Configuration**: Validate all settings match your project
2. **Test Pipeline**: Create test tag and monitor execution
3. **TestPyPI First**: Always test with TestPyPI before production
4. **Production Release**: After successful test, publish to PyPI
5. **Monitor**: Track downloads and issues on PyPI dashboard

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-01-23  
**Compatibility**: GitLab CI/CD 15.0+, Python 3.10+
