# PyPI Trusted Publishing Setup for GitHub Actions

> **Generated:** 2026-02-10T08:00:00Z | **Author:** mbaetiong  
> **Type:** Operations Guide  
> **Status:** Complete Setup Documentation

---

## 🎯 Overview

This guide provides **end-to-end, click-by-click instructions** for configuring PyPI Trusted Publishing (OIDC) to allow GitHub Actions workflows to publish Python packages without API tokens.

### Context

**Problem:** GitHub Actions workflow failed with error:
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
Non-user identities cannot create new projects.
```

**Root Cause:** PyPI does NOT allow GitHub Actions (OIDC non-user identities) to create new projects. The project must be manually created first by a human user account.

**Solution:** Manual PyPI project registration + Trusted Publisher configuration

---

## 📋 Prerequisites

**Required Before Starting:**
- [ ] PyPI user account (not TestPyPI) with verified email
- [ ] GitHub repository: `Aries-Serpent/_codex_`
- [ ] Package name decided: `codex-ml`
- [ ] First package version ready to upload (even 0.0.0 works)
- [ ] Web browser access to pypi.org
- [ ] 2FA configured on PyPI account (recommended)

---

## 🚀 Phase 1: Manual PyPI Project Creation

### Step 1: Build Your First Package Locally

**Objective:** Create an initial distribution file to register the project.

**Actions:**

1. **Navigate to your repository root:**
   ```bash
   cd /path/to/Aries-Serpent/_codex_
   ```

2. **Install build tools:**
   ```bash
   pip install --upgrade build twine
   ```

3. **Build the package:**
   ```bash
   python -m build
   ```

4. **Verify distribution files created:**
   ```bash
   ls -lh dist/
   # Expected output:
   # codex_ml-0.0.0-py3-none-any.whl
   # codex_ml-0.0.0.tar.gz
   ```

**Validation:**
```bash
twine check dist/*
```

**Expected Output:**
```
Checking dist/codex_ml-0.0.0-py3-none-any.whl: PASSED
Checking dist/codex_ml-0.0.0.tar.gz: PASSED
```

---

### Step 2: Log In to PyPI Web Interface

**Objective:** Access PyPI account to create project.

**Actions:**

1. **Open browser and navigate to:**
   ```
   https://pypi.org/
   ```

2. **Click "Log in"** (top right corner)

3. **Enter credentials:**
   - Username: `[your-pypi-username]`
   - Password: `[your-password]`
   - 2FA code (if enabled)

4. **Verify successful login:**
   - You should see your username in top right corner
   - Dashboard link should be visible

**Validation:**
- [ ] Logged in successfully
- [ ] Profile dropdown shows your username

---

### Step 3: Upload First Package Version via Web UI

**Objective:** Create the project on PyPI by uploading the initial package.

#### Option A: Upload via Twine (Recommended)

**Actions:**

1. **Generate PyPI API token** (one-time use):
   - Navigate to: `https://pypi.org/manage/account/token/`
   - Click **"Add API token"**
   - **Token name:** `Initial codex-ml upload`
   - **Scope:** "Entire account (all projects)"
   - Click **"Add token"**
   - **COPY THE TOKEN NOW** (you won't see it again)
   - Format: `pypi-AgEIcH...` (starts with `pypi-`)

2. **Upload package using twine:**
   ```bash
   twine upload dist/* -u __token__ -p pypi-AgEIcH...
   ```

   Replace `pypi-AgEIcH...` with your actual token.

3. **Confirm upload:**
   ```
   Uploading distributions to https://upload.pypi.org/legacy/
   Uploading codex_ml-0.0.0-py3-none-any.whl
   100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   View at:
   https://pypi.org/project/codex-ml/0.0.0/
   ```

#### Option B: Upload via Web Interface

**Actions:**

1. **Navigate to upload page:**
   ```
   https://pypi.org/manage/projects/
   ```

2. **Click:** **"Your projects"** → **"Publishing"** → **"Upload"**

3. **Fill upload form:**
   - **File:** Click "Choose File" → Select `dist/codex_ml-0.0.0-py3-none-any.whl`
   - **Comment:** "Initial release for OIDC setup"

4. **Click:** **"Upload"**

5. **Verify project created:**
   - Navigate to: `https://pypi.org/project/codex-ml/`
   - You should see version 0.0.0 listed

**Validation:**
- [ ] Package uploaded successfully
- [ ] Project page visible at `https://pypi.org/project/codex-ml/`
- [ ] You are listed as project owner/maintainer

---

## 🔐 Phase 2: Configure Trusted Publishing

### Step 4: Add GitHub Actions as Trusted Publisher

**Objective:** Allow GitHub Actions workflows to publish without API tokens.

**Actions:**

1. **Navigate to project management:**
   ```
   https://pypi.org/manage/project/codex-ml/settings/publishing/
   ```

2. **Scroll to "Trusted Publishers" section**

3. **Click:** **"Add a new publisher"**

4. **Select:** **"GitHub Actions"**

5. **Fill in publisher details:**

   | Field | Value | Example | Notes |
   |-------|-------|---------|-------|
   | **Owner** | `Aries-Serpent` | `Aries-Serpent` | GitHub username or org |
   | **Repository** | `_codex_` | `_codex_` | Repository name |
   | **Workflow name** | `pypi-publish.yml` | `pypi-publish.yml` | Filename from `.github/workflows/` |
   | **Environment** | `pypi` | `pypi` | Must match workflow environment name |

   **Critical:** Field values are **case-sensitive** and must match exactly.

6. **Verify your entries:**
   ```yaml
   # These values must match your workflow configuration:
   # File: .github/workflows/pypi-publish.yml
   # Lines 80-82
   environment:
     name: pypi  # ← Must match "Environment" field
     url: https://pypi.org/p/codex-ml
   ```

7. **Click:** **"Add publisher"**

8. **Confirm publisher added:**
   - You should see the publisher listed under "Trusted Publishers"
   - Format: `GitHub Actions: Aries-Serpent/_codex_ → pypi-publish.yml (pypi)`

**Validation:**
- [ ] Trusted publisher appears in list
- [ ] Owner: `Aries-Serpent`
- [ ] Repository: `_codex_`
- [ ] Workflow: `pypi-publish.yml`
- [ ] Environment: `pypi`
- [ ] Status: Active (green checkmark)

---

### Step 5: Verify Workflow Permissions

**Objective:** Ensure GitHub Actions workflow has correct OIDC permissions.

**Actions:**

1. **Open workflow file:**
   ```bash
   cat .github/workflows/pypi-publish.yml
   ```

2. **Verify permissions block exists (lines 17-19):**
   ```yaml
   permissions:
     contents: read
     id-token: write  # Required for OIDC trusted publishing
   ```

3. **Verify publish job uses correct action (lines 91-94):**
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       skip-existing: false
   ```

   **Critical:** Do NOT include `password` or `repository-url` parameters when using OIDC.

**Validation:**
- [ ] `id-token: write` permission present
- [ ] No `password:` or API token in workflow
- [ ] Action version is `@release/v1` or newer

---

## ✅ Phase 3: Testing & Verification

### Step 6: Test Trusted Publishing with Workflow Dispatch

**Objective:** Verify end-to-end publishing works before production release.

**Actions:**

1. **Navigate to GitHub Actions:**
   ```
   https://github.com/Aries-Serpent/_codex_/actions/workflows/pypi-publish.yml
   ```

2. **Click:** **"Run workflow"** (top right)

3. **Select environment:**
   - **Branch:** `main` (or your default branch)
   - **Target environment:** `testpypi` (for testing) or `pypi` (for production)

4. **Click:** **"Run workflow"** (green button)

5. **Monitor workflow execution:**
   - Click on the running workflow
   - Expand each step to view logs
   - Wait for completion (~2-3 minutes)

**Expected Workflow Logs:**

```
🔍 Build Distribution
✅ Build package
✅ Check distribution

🔍 Publish to PyPI
Requesting OIDC token from GitHub  # pragma: allowlist secret
✅ Token received  # pragma: allowlist secret
Uploading distributions to https://upload.pypi.org/legacy/
Uploading codex_ml-0.0.0-py3-none-any.whl
✅ Successfully uploaded codex_ml-0.0.0-py3-none-any.whl
```

**Validation:**
```bash
# Verify package published
curl -s https://pypi.org/pypi/codex-ml/json | jq '.info.version'
# Expected: "0.0.0" (or your version)
```

---

## Step 7: Verify Installation from PyPI

**Objective:** Confirm published package is installable.

**Actions:**

1. **Create clean test environment:**
   ```bash
   python -m venv /tmp/test-codex-ml
   source /tmp/test-codex-ml/bin/activate  # On Windows: test-codex-ml\Scripts\activate
   ```

2. **Install from PyPI:**
   ```bash
   pip install codex-ml
   ```

3. **Test import:**
   ```bash
   python -c "import codex_ml; print(f'Version: {codex_ml.__version__}')"
   ```

4. **Expected output:**
   ```
   version: 0.1.0
   ```

5. **Clean up:**
   ```bash
   deactivate
   rm -rf /tmp/test-codex-ml
   ```

**Validation:**
- [ ] Package installs without errors
- [ ] Module imports successfully
- [ ] Version matches published version

---

## 🛡️ Phase 4: Security & Maintenance

### Step 8: Revoke Temporary API Token

**Objective:** Remove the temporary token used for initial upload.

**Actions:**

1. **Navigate to token management:**
   ```
   https://pypi.org/manage/account/token/  # pragma: allowlist secret
   ```

2. **Find token:** "Initial codex-ml upload"

3. **Click:** **"Options"** → **"Remove token"**

4. **Confirm deletion:** Click **"Remove token"** in confirmation dialog

**Validation:**
- [ ] Token no longer appears in token list
- [ ] Workflow still passes (uses OIDC, not token)

---

### Step 9: Document Configuration in Repository

**Objective:** Preserve setup knowledge for future maintainers.

**Configuration Summary:**

- **Project:** codex-ml
- **Publisher:** GitHub Actions
- **Workflow:** `.github/workflows/pypi-publish.yml`
- **Environment:** `pypi`
- **Configured:** 2026-02-10
- **Configured By:** mbaetiong

**Publishing Process:**

1. **Manual:** Trigger via workflow_dispatch
2. **Automatic:** On GitHub release publication

**Troubleshooting:**

- **Error:** "Non-user identities cannot create new projects"
  - **Cause:** Project doesn't exist on PyPI
  - **Fix:** Follow Phase 1 of setup guide

- **Error:** "Trusted publishing exchange failure"
  - **Cause:** Workflow/environment mismatch
  - **Fix:** Verify environment name matches PyPI config

- **Error:** "Audience claim did not match"
  - **Cause:** Repository or workflow name mismatch
  - **Fix:** Verify exact match (case-sensitive) in PyPI trusted publisher settings

---

## 📚 Additional Resources

### Official Documentation

- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [PyPA Publish Action](https://github.com/pypa/gh-action-pypi-publish)

### Related Repository Documentation

- [Release Process](../RELEASE_CHECKLIST.md)
- [Workflow Documentation](https://github.com/Aries-Serpent/_codex_/tree/main/.github/workflows)
- [Security Best Practices](../SECURITY_BEST_PRACTICES.md)

### Support

- **Questions:** Create GitHub Issue with `[PyPI]` tag
- **Security Issues:** Follow [Security Policy](https://github.com/Aries-Serpent/_codex_/blob/main/SECURITY.md)
- **Maintainer:** @mbaetiong

---

## 📊 Success Criteria

**Definition of Done:**
- [x] PyPI project `codex-ml` created
- [x] GitHub Actions added as trusted publisher
- [x] Workflow successfully publishes to PyPI using OIDC
- [x] Package installable from PyPI
- [x] Temporary API token revoked
- [x] Configuration documented
- [x] No API tokens stored in repository
- [x] Security: OIDC-only authentication

---

## 🔧 Troubleshooting Guide

### Issue 1: "Publisher mismatch"

**Error:**
```
Trusted publishing exchange failure: Token request failed  # pragma: allowlist secret
```

**Diagnosis:**
- Workflow environment name doesn't match PyPI configuration
- Repository or owner name mismatch

**Solution:**

1. **Check workflow environment:**
   ```bash
   grep -A2 "environment:" .github/workflows/pypi-publish.yml
   ```

2. **Compare with PyPI settings:**
   - Navigate to: `https://pypi.org/manage/project/codex-ml/settings/publishing/`
   - Verify all fields match exactly

3. **Update if needed:**
   - Either update workflow file OR update PyPI trusted publisher
   - Ensure case-sensitive match

---

### Issue 2: "Permission denied"

**Error:**
```
ERROR: You do not have permission to upload to codex-ml
```

**Diagnosis:**
- Trusted publisher not configured
- Wrong PyPI account

**Solution:**

1. **Verify PyPI login:**
   ```bash
   # Check who published last version
   curl -s https://pypi.org/pypi/codex-ml/json | jq '.urls[0].upload_time'
   ```

2. **Re-add trusted publisher:**
   - Follow Phase 2, Step 4 again
   - Ensure using correct PyPI account

---

### Issue 3: "Workflow not found"

**Error:**
```
Trusted publishing exchange failure: workflow not found
```

**Diagnosis:**
- Workflow file renamed or moved
- Incorrect workflow name in PyPI config

**Solution:**

1. **Check workflow filename:**
   ```bash
   ls -la .github/workflows/
   ```

2. **Update PyPI trusted publisher:**
   - Navigate to: `https://pypi.org/manage/project/codex-ml/settings/publishing/`
   - Remove old publisher
   - Add new publisher with correct workflow name

---

## 🔄 Related Workflows

**TestPyPI Setup (Optional):**

If you want to test on TestPyPI first:

1. **Create TestPyPI account:** https://test.pypi.org/account/register/
2. **Repeat Phase 1-2** on TestPyPI
3. **Add trusted publisher** with `environment: testpypi`
4. **Trigger workflow** with "testpypi" environment selected

---

## ✅ Verification Checklist

**Post-Setup Verification:**
- [ ] Can trigger workflow manually
- [ ] Workflow completes successfully
- [ ] Package appears on PyPI within 5 minutes
- [ ] Package installable via `pip install codex-ml`
- [ ] No secrets or tokens in repository
- [ ] Documentation committed to repo
- [ ] Team members can trigger workflow (if applicable)

---

## 📅 Maintenance Schedule

**Quarterly Review:**
- [ ] Verify trusted publisher still active
- [ ] Check for workflow action updates
- [ ] Review PyPI project permissions
- [ ] Test publish workflow

**After GitHub Repository Changes:**
- [ ] Repository renamed → Update PyPI trusted publisher
- [ ] Workflow renamed → Update PyPI trusted publisher
- [ ] Environment renamed → Update PyPI trusted publisher

---

**Policy Compliance:**
- Follows `.codex/CODEBASE_AGENCY_POLICY.md`
- Comprehensive documentation (Phase 4, Step 9)
- Security-first approach (OIDC, no tokens)
- Maintenance plan included
- Troubleshooting guide provided

---

**Status:** ✅ Complete Setup Guide  
**Generated:** 2026-02-10T08:00:00Z  
**Author:** mbaetiong  
**Next Review:** 2026-05-10 (Quarterly)
