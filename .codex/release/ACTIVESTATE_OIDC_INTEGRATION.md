# ActiveState OIDC Integration Guide

**Version**: 1.0.0  
**Date**: 2026-01-23  
**Status**: Production Ready  
**Reference**: https://docs.activestate.com/platform/user/oidc/

---

## Overview

This guide provides step-by-step instructions for configuring OpenID Connect (OIDC) authentication between your CI/CD pipeline (GitHub Actions or GitLab CI/CD) and the ActiveState Platform for secure package publishing.

---

## What is ActiveState OIDC?

ActiveState OIDC allows CI/CD systems to authenticate with the ActiveState Platform without long-lived API tokens. Instead, short-lived tokens are generated automatically during pipeline execution.

**Benefits**:
- ✅ No API tokens to manage or rotate
- ✅ Short-lived credentials (valid for single pipeline run)
- ✅ Automatic authentication via OIDC provider
- ✅ Enhanced security through identity-based access
- ✅ Audit trail of all publishing actions

---

## Prerequisites

1. **ActiveState Account**: Create at https://platform.activestate.com
2. **Organization**: Set up organization for your project
3. **CI/CD System**: GitHub Actions or GitLab CI/CD
4. **Package Project**: Valid Python package with pyproject.toml

---

## ActiveState Platform Setup

### Step 1: Create ActiveState Account

1. Navigate to https://platform.activestate.com/create-account
2. Sign up using:
   - Email/password
   - GitHub account (recommended for GitHub Actions)
   - GitLab account (recommended for GitLab CI/CD)

### Step 2: Create Organization

1. After login, click "Create Organization"
2. Enter organization name: `aries-serpent` (match your repository namespace)
3. Set organization visibility (public or private)

### Step 3: Create Project

1. Navigate to: Organization → Projects → New Project
2. Configure:
   ```
   Project Name: codex-ml
   Language: Python
   Python Version: 3.12
   Visibility: Public
   ```

### Step 4: Configure OIDC Provider

1. Navigate to: Organization → Settings → OIDC
2. Click "Add OIDC Provider"
3. Select provider:
   - **GitHub**: For GitHub Actions workflows
   - **GitLab**: For GitLab CI/CD pipelines

---

## GitHub Actions Configuration

### OIDC Setup on ActiveState

**Navigate to**: Organization → Settings → OIDC → Add Provider → GitHub

**Configuration**:
```
Provider: GitHub
Repository Owner: Aries-Serpent
Repository Name: _codex_
Workflow File: .github/workflows/pypi-publish.yml
Environment: activestate-production (optional but recommended)
```

### GitHub Actions Workflow

**File**: `.github/workflows/activestate-publish.yml`

```yaml
name: Publish to ActiveState Platform

on:
  release:
    types: [published]
  workflow_dispatch:

permissions:
  contents: read
  id-token: write  # Required for OIDC

jobs:
  publish:
    name: Publish to ActiveState
    runs-on: ubuntu-latest
    environment:
      name: activestate-production
      url: https://platform.activestate.com/Aries-Serpent/codex-ml

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install ActiveState CLI
        run: |
          curl -sSf https://platform.activestate.com/dl/cli/install.sh | sh
          echo "$HOME/.local/ActiveState/StateTool" >> $GITHUB_PATH

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Get OIDC Token
        id: oidc
        run: |
          # GitHub automatically provides OIDC token
          echo "Token will be used via OIDC"

      - name: Authenticate with ActiveState (OIDC)
        run: |
          # ActiveState CLI automatically uses OIDC when configured
          state auth --oidc

      - name: Publish Package
        run: |
          state publish dist/*.whl --project Aries-Serpent/codex-ml
```

---

## GitLab CI/CD Configuration

### OIDC Setup on ActiveState

**Navigate to**: Organization → Settings → OIDC → Add Provider → GitLab

**Configuration**:
```
Provider: GitLab
GitLab Namespace: aries-serpent
Repository Name: _codex_
Pipeline File: .gitlab-ci.yml
Environment: activestate-production (optional but recommended)
```

### GitLab Pipeline Configuration

**File**: `.gitlab-ci.yml`

```yaml
stages:
  - build
  - publish

build-package:
  stage: build
  image: python:3.12
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - tags

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
    # Install ActiveState CLI
    - curl -sSf https://platform.activestate.com/dl/cli/install.sh | sh
    - export PATH="$HOME/.local/ActiveState/StateTool:$PATH"

    # Authenticate using OIDC token
    - state auth --token ${ACTIVESTATE_TOKEN}

    # Publish package
    - state publish dist/*.whl --project aries-serpent/codex-ml
  only:
    - tags
  when: manual
```

---

## Environment Configuration

### GitHub Environment Setup

**Navigate to**: Repository → Settings → Environments → New environment

**Configuration**:
```
Name: activestate-production
Deployment branches: Selected branches
Required reviewers: 1 (recommended)
Wait timer: 0 minutes
```

### GitLab Environment Setup

**Navigate to**: Project → Settings → CI/CD → Environments → New environment

**Configuration**:
```
Name: activestate-production
External URL: https://platform.activestate.com/aries-serpent/codex-ml
Protected: Yes
Allowed to deploy: Maintainers only
```

---

## Security Configuration

### OIDC Token Validation

ActiveState validates the following claims in OIDC tokens:

**GitHub Actions**:
- `repository`: Must match configured repository
- `workflow`: Must match configured workflow file
- `environment`: Must match configured environment (if set)
- `ref`: Must be valid Git ref (tag or branch)

**GitLab CI/CD**:
- `project_path`: Must match configured namespace/project
- `pipeline_source`: Must be valid pipeline trigger
- `environment`: Must match configured environment (if set)
- `ref`: Must be valid Git ref

### Best Practices

1. **Use Dedicated Environments**:
   ```yaml
   environment:
     name: activestate-production
   ```

2. **Require Manual Approval**:
   ```yaml
   when: manual  # GitLab
   # or
   environment:
     protection_rules:
       required_reviewers: 1  # GitHub
   ```

3. **Restrict to Tags Only**:
   ```yaml
   only:
     - tags  # GitLab
   # or
   on:
     release:
       types: [published]  # GitHub
   ```

4. **Audit All Publications**:
   - ActiveState maintains audit log
   - Review at: Organization → Activity Log

---

## Troubleshooting

### Common Issues

**1. OIDC Token Not Found**
```
Error: ACTIVESTATE_TOKEN environment variable not set
```
**Solution**:
- GitHub: Ensure `permissions: id-token: write` is set
- GitLab: Verify `id_tokens` block is configured correctly

**2. Authentication Failed**
```
Error: Failed to authenticate with ActiveState Platform
```
**Solution**:
- Verify OIDC provider configured on ActiveState
- Check repository name matches exactly
- Confirm workflow/pipeline file path is correct

**3. Repository Not Authorized**
```
Error: Repository not authorized to publish
```
**Solution**:
- Verify OIDC configuration matches repository details
- Check organization permissions
- Ensure environment name matches (if configured)

**4. Package Publication Failed**
```
Error: Failed to publish package
```
**Solution**:
- Verify package built successfully
- Check ActiveState project exists
- Confirm package name matches project name

---

## Usage Examples

### Example 1: Release on GitHub

```bash
# Create release tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Create GitHub Release
gh release create v1.0.0 \
  --title "Release v1.0.0" \
  --notes "Release notes here"

# Workflow triggers automatically
# Monitor at: Actions → Publish to ActiveState Platform
```

### Example 2: Manual Publish from GitLab

```bash
# Create tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Pipeline triggers automatically
# Navigate to: CI/CD → Pipelines → [Latest Pipeline]
# Click "Play" on publish-activestate job
```

---

## Advanced Configuration

### Multi-Environment Publishing

**Strategy**: Separate environments for testing and production

```yaml
# GitHub Actions
publish-test:
  environment: activestate-test
  if: github.event_name == 'workflow_dispatch'
  # ... publish to test project

publish-prod:
  environment: activestate-production
  if: github.event_name == 'release'
  # ... publish to production project
```

### Conditional Publishing

**Strategy**: Only publish specific versions

```yaml
# GitLab CI/CD
publish-activestate:
  only:
    variables:
      - $CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+$/  # Only stable releases
  # ... publish configuration
```

---

## Integration Summary

### Required Information

| Field | Value (Example) |
|-------|-----------------|
| **Organization** | aries-serpent |
| **Project Name** | codex-ml |
| **Repository** | Aries-Serpent/_codex_ |
| **Workflow File (GitHub)** | .github/workflows/activestate-publish.yml |
| **Pipeline File (GitLab)** | .gitlab-ci.yml |
| **Environment** | activestate-production (optional) |

### Verification Checklist

- [ ] ActiveState account created
- [ ] Organization set up
- [ ] Project created on ActiveState Platform
- [ ] OIDC provider configured
- [ ] CI/CD workflow created
- [ ] Environment configured (if using)
- [ ] OIDC permissions granted (id-token: write)
- [ ] Test publish executed successfully
- [ ] Production publish validated

---

## Resources

### Documentation
- **ActiveState OIDC**: https://docs.activestate.com/platform/user/oidc/
- **ActiveState CLI**: https://docs.activestate.com/platform/state/
- **GitHub OIDC**: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
- **GitLab OIDC**: https://docs.gitlab.com/ee/ci/cloud_services/

### Support
- **ActiveState Community**: https://community.activestate.com/
- **Support Portal**: https://support.activestate.com/
- **GitHub Issues**: https://github.com/ActiveState/state-tool/issues

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-01-23  
**Compatibility**: GitHub Actions, GitLab CI/CD, ActiveState Platform
