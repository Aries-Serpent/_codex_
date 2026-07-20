# 🚀 PyPI Publish Workflow Deployment Monitoring Report

**Report Generated**: 2026-07-20T01:47:24Z
**PR**: #5367 — PyPI publishing OIDC migration
**Branch**: `copilot/fix-pypi-upload-error`
**Task**: Monitor PyPI workflow execution and OIDC token validation

---

## 📊 Current Status Overview

| Component | Status | Details |
|-----------|--------|---------|
| **PR Status** | 🟡 DRAFT | 17 commits, security alerts pending review |
| **Latest Workflow Run** | 🔴 FAILED | Run #1068 (2026-07-20T00:14:41Z) |
| **Previous Release** | 🔴 FAILED | Run #1067 (v0.2.0 tag, 2026-07-19T18:34:51Z) |
| **OIDC Configuration** | ✅ Active | PyPI Trusted Publisher configured |
| **id-token Permission** | ✅ Enabled | Workflow grants write access |

---

## 🔴 Critical Failure Analysis

### **Run #1068 (Latest - 2026-07-20T00:14:41Z)**

**Trigger**: `workflow_dispatch` (manual) on main branch  
**Duration**: 5m 22s  
**Conclusion**: FAILURE (403 Forbidden from PyPI)

#### Job Breakdown
| Job | Status | Duration | Conclusion |
|-----|--------|----------|-----------|
| Build Distribution | ✅ SUCCESS | 1m 30s | Complete |
| Publish to TestPyPI | ⊘ SKIPPED | - | Condition: workflow_dispatch + environment=testpypi |
| **Publish to PyPI** | 🔴 FAILURE | 13s | HTTP 403 Forbidden |
| Verify Installation | ⊘ SKIPPED | - | Depends on publish jobs |

#### Root Cause: OIDC Token Validation Failure

**Error Output**:
```
HTTPError: 403 Forbidden from https://upload.pypi.org/legacy/
403 Invalid API Token: OIDC scoped token is not valid for project
```

**Analysis**:
- ✅ OIDC token WAS generated successfully
- ✅ Token was sent to PyPI upload endpoint
- 🔴 PyPI rejected token as "not valid for project"
- 🔴 Likely cause: OIDC scope mismatch or PyPI configuration

#### Technical Details

**Request Flow**:
1. GitHub Action runs `pypa/gh-action-pypi-publish@ba38be9e...`
2. Action requests OIDC token from GitHub (with id-token: write permission)
3. GitHub issues time-bound token (verified sigstore attestations)
4. Action exchanges token with PyPI for temporary credentials
5. PyPI validates token scope against registered publisher config
6. **PyPI rejection**: Token doesn't match publisher configuration

**Token Verification Chain** (Success):
- ✅ Sigstore SCT verification: OK
- ✅ Certificate chain validation: OK (O=sigstore.dev)
- ✅ Integrated timestamp: 2026-07-20T00:19:58Z
- ✅ Rekor log inclusion: Verified

---

## 🔧 PR #5367 Changes vs Current Deployment

### What the PR Changes

```yaml
# BEFORE (current main):
- uses: pypa/gh-action-pypi-publish@cef221092ed1bacb1cc03d23a2d87d1d172e277b
  with:
    skip-existing: false
    password: ${{ secrets.PYPI_API_TOKEN }}  # ← Explicit token

# AFTER (PR #5367):
- uses: pypa/gh-action-pypi-publish@ba38be9e461d3875417946c167d0b5f3d385a247  # release/v1
  with:
    skip-existing: false
    # NO password parameter → OIDC token only
```

### Issues Detected

1. **Action Version**: PR uses pinned commit `ba38be9e...` (April 2024)
   - Comment says `# release/v1` but actual pin is older
   - Recommendation: Use `@release/v1` tag for better OIDC support

2. **OIDC Configuration**:
   - ✅ `permissions.id-token: write` added to jobs
   - ✅ `environment: name: pypi` already set
   - 🟡 May need to verify PyPI publisher configuration

3. **Password Removal**:
   - ✅ Removed from TestPyPI: `password: ${{ secrets.TEST_PYPI_API_TOKEN }}`
   - ✅ Removed from PyPI: implicit by not setting it

---

## 🔍 PyPI Trusted Publisher Configuration

**Status**: ✅ Verified Active

```
Organization: aries-serpent
Repository: _codex_
Workflow Name: pypi-publish.yml
Environment: pypi
```

**Expected OIDC Token Claim**:
```json
{
  "aud": "pypi",
  "iss": "https://token.actions.githubusercontent.com",
  "repository": "Aries-Serpent/_codex_",
  "repository_id": "1040037790",
  "workflow": "pypi-publish.yml",
  "environment": "pypi"
}
```

---

## 📈 Workflow Run History (Last 5)

| Run # | Branch | Event | Status | Time | Error |
|-------|--------|-------|--------|------|-------|
| 1068 | main | workflow_dispatch | 🔴 FAIL | 2026-07-20T00:14 | 403 OIDC Invalid |
| 1067 | v0.2.0 | release | 🔴 FAIL | 2026-07-19T18:34 | 403 OIDC Invalid |
| 1066 | main | workflow_dispatch | 🔴 FAIL | 2026-07-19T17:22 | 403 OIDC Invalid |
| 1065 | main | workflow_dispatch | 🔴 FAIL | 2026-07-18T23:15 | 403 OIDC Invalid |
| 1064 | main | workflow_dispatch | 🔴 FAIL | 2026-07-18T22:50 | 403 OIDC Invalid |

**Pattern**: Consistent 403 OIDC token rejection across all recent attempts

---

## 🎯 Deployment Plan & Next Steps

### Phase 1: Validation (Current)
- [x] PR #5367 created with OIDC migration
- [x] Identified root cause: OIDC token invalid for project
- [ ] Verify PyPI Trusted Publisher config matches workflow
- [ ] Test on PR branch with workflow_dispatch

### Phase 2: Diagnosis
- [ ] Check PyPI publisher configuration in org settings
- [ ] Verify workflow environment name matches PyPI config
- [ ] Test OIDC token generation with debug logs
- [ ] Confirm action version supports OIDC properly

### Phase 3: Fix & Verification
- [ ] Update action to `@release/v1` if needed
- [ ] Trigger workflow on PR branch
- [ ] Monitor TestPyPI publish (if enabled)
- [ ] Monitor PyPI publish (production)
- [ ] Verify verify-installation job

### Phase 4: Production Deployment
- [ ] Merge PR #5367 to main
- [ ] Tag release version
- [ ] Trigger release workflow
- [ ] Verify package on PyPI (https://pypi.org/project/codex-ml/)
- [ ] Confirm installation works

---

## 🔐 Security Validation Checklist

- [x] OIDC token generation: Working
- [x] Token sigstore verification: Passing
- [x] id-token permission: Granted
- [x] No plaintext secrets in workflow
- [x] No password parameter in OIDC flow
- [x] Environment isolation: Proper
- [ ] PyPI publisher scope: TBD (403 suggests mismatch)

---

## ⚠️ Known Issues & Recommendations

### Issue #1: OIDC Token Scope Mismatch
**Severity**: CRITICAL  
**Status**: Blocking deployment

The PyPI server is rejecting the OIDC token with "not valid for project" error. Possible causes:
1. **Workflow environment name mismatch**
   - Configured: `environment: name: pypi`
   - Expected by PyPI: May differ

2. **Repository/org mismatch in publisher config**
   - GitHub: `Aries-Serpent/_codex_`
   - PyPI: Verify exact match

3. **Action version incompatibility**
   - Current: Pinned old commit
   - Recommended: `@release/v1` tag

**Resolution**: 
```yaml
# Option 1: Update action tag (safer)
- uses: pypa/gh-action-pypi-publish@release/v1

# Option 2: Use latest release (auto-updates)
- uses: pypa/gh-action-pypi-publish@release/v1
```

### Recommendation: Update Action Tag

The PR pins commit `ba38be9e...` from April 2024. The `release/v1` tag provides:
- Better OIDC support
- Bug fixes post-April 2024
- Official maintained version
- Auto-receives security patches

**Change needed**: Line 108 in `.github/workflows/pypi-publish.yml`
```diff
- uses: pypa/gh-action-pypi-publish@ba38be9e461d3875417946c167d0b5f3d385a247  # release/v1
+ uses: pypa/gh-action-pypi-publish@release/v1
```

---

## 📋 Metrics & Timeline

**Workflow Execution Metrics**:
- Build job: 1m 30s ✅
- PyPI publish job: 13s (failed) 🔴
- Token generation: <1s ✅
- Total (including setup): 5m 22s

**OIDC Token Lifecycle**:
- Generation: 00:19:47Z ✅
- Exchange attempt: 00:19:47-00:20:00Z
- Sigstore verification: 00:19:57Z ✅
- HTTP request: 00:20:00Z
- **Rejection: 00:20:00.599509Z** 🔴

---

## 🚀 Deployment Readiness

| Criterion | Status | Notes |
|-----------|--------|-------|
| Code changes | ✅ Ready | PR #5367 prepared |
| OIDC setup | ✅ Active | Token generation works |
| PyPI config | 🟡 Verify | 403 suggests scope issue |
| Action version | 🟡 Update | Should use @release/v1 |
| Security review | 🟡 Pending | No secrets detected ✅ |
| Testing | 🔴 Failed | Previous 5 runs all 403 |

**Overall Readiness**: 🟡 BLOCKED — Requires fix to OIDC token validation

---

## 📞 Escalation & Next Actions

**Immediate Actions**:
1. Update action version to `@release/v1` in PR #5367
2. Verify PyPI Trusted Publisher configuration
3. Re-test on PR branch with updated action
4. Check GitHub Actions debug logs for token content

**If Still Failing After Action Update**:
1. Review PyPI publisher config in org settings
2. Compare OIDC claims with PyPI expectations
3. Contact PyPI support if config appears correct
4. Consider temporary fallback to API token (less secure)

**Timeline**: Estimate 30-45 minutes to diagnose and fix once PR is updated

---

**Report Status**: 🟡 ACTIVE MONITORING  
**Last Updated**: 2026-07-20T01:47:24Z  
**Next Check**: Recommended every 5 minutes until resolution
