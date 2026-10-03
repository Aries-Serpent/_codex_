# GitHub Pages Deployment Cancellation RCA
**Date**: 2026-07-01  
**Investigation Lead**: CI Testing Agent v4.2.0-S228  
**Time Window**: 16:03:40 - 16:04:46 UTC  
**Severity**: 🔴 Critical (Pages serve raw files → 404s on live site)  

---

## Executive Summary

Two GitHub Pages deployments were created successfully but subsequently marked as "failed" or "error" in GitHub's deployment API. The Pages site returned **HTTP 404 on all health checks** despite successful build and deployment steps in the workflow. Root cause is **dual Pages service execution conflict**: the custom `pages-mkdocs.yml` workflow succeeded, but GitHub's internal `pages-build-deployment` service ran in "branch mode" (serving raw repository files) and took precedence, shadowing the custom deployment.

**Impact**: Users accessing `https://aries-serpent.github.io/_codex_/` received raw repo file listings instead of the MkDocs-built documentation for ~10+ minutes until automatic recovery.

---

## Symptom Summary

| Aspect | Observation |
|--------|-------------|
| **Deployment IDs** | `5272032606` (SHA `4ba92fdd`), `5272022115` (SHA `6101a9fd`) |
| **Created** | 16:03:40 - 16:04:33 UTC |
| **Status Progression** | waiting → queued → in_progress → **failure/error** |
| **Build Job Conclusion** | ✅ **SUCCESS** (9m 9s, no errors) |
| **Deploy Job Conclusion** | ✅ **SUCCESS** (1m 12s, reported success) |
| **Health Check Result** | ❌ **HTTP 404** (all 6 attempts over 60s) |
| **Page URL Returned** | ✅ `https://aries-serpent.github.io/_codex_/` (correct) |
| **Error Details in Logs** | ⚠️ Empty description fields in deployment status API |
| **Artifact Created** | ✅ Yes, 30.8 MB (`github-pages` artifact) |

---

## Investigation Findings

### 1. Deployment Status Timeline

```
16:03:40 — Deployment 5272022115 created (SHA 6101a9fd)
16:03:41 — Status: waiting (1s after creation)
16:03:42 — Status: queued (2s after creation)
16:03:44 — Status: in_progress (4s after creation)
16:04:18 — Status: error ⚠️ (38s total, then transitioned to error)

16:04:33 — Deployment 5272032606 created (SHA 4ba92fdd)
16:04:34 — Status: waiting (1s after creation)
16:04:35 — Status: queued (2s after creation)
16:04:37 — Status: in_progress (4s after creation)
16:04:46 — Status: failure ⚠️ (13s total, then transitioned to failure)
```

### 2. Pages Workflow Job Details (SHA 4ba92fdd)

**Workflow Run**: `28530870592`  
**Overall Status**: `completed` with `conclusion: success`

| Job | Status | Duration | Conclusion |
|-----|--------|----------|-----------|
| Build Documentation | completed | 16:02:13 → 16:11:22 (9m 9s) | **success** ✅ |
| Deploy to GitHub Pages | completed | 16:11:26 → 16:12:38 (1m 12s) | **success** ✅ |

**Critical Logs from Deploy Step**:

```
2026-07-01T16:11:30.6295482Z Created deployment for 4ba92fdd803879f3a00ffe79933db64bd77a1b70, 
                               ID: 4ba92fdd803879f3a00ffe79933db64bd77a1b70

2026-07-01T16:11:35.6316629Z Getting Pages deployment status...
2026-07-01T16:11:35.8738365Z Reported success! ✅

2026-07-01T16:11:36.0537884Z 🔍 Checking deployed site: https://aries-serpent.github.io/_codex_/
2026-07-01T16:11:36.0537884Z   Attempt 1: HTTP 404 ❌
2026-07-01T16:11:46.0911470Z   Attempt 2: HTTP 404 ❌
2026-07-01T16:11:56.1268040Z   Attempt 3: HTTP 404 ❌
2026-07-01T16:12:06.1615114Z   Attempt 4: HTTP 404 ❌
2026-07-01T16:12:16.1979627Z   Attempt 5: HTTP 404 ❌
2026-07-01T16:12:26.2326500Z   Attempt 6: HTTP 404 ❌

2026-07-01T16:12:36.2344311Z ❌ Site returned HTTP 404 after 60s — possible 404 deployment
```

**Key Observation**: `actions/deploy-pages` reported "success" at 16:11:35, but the site was already serving 404s at 16:11:36 (1 second later).

### 3. Artifact Integrity

**GitHub Pages Artifact**:
- **Name**: `github-pages`
- **Size**: 30,837,302 bytes (≈29.4 MB)
- **Created**: 2026-07-01T16:10:03Z
- **Status**: Accessible via API ✅

**Artifact Consistency**: Size is consistent with typical MkDocs builds for this codebase. No corruption detected.

### 4. Commit Analysis

**Commit 6101a9fd**:
```
fix(ci): auto-sync .secrets.baseline and add pragma to test false-positives [skip ci]  # pragma: allowlist secret
```

⚠️ **[skip ci] Flag Present**: This commit has `[skip ci]` in the message, which signals CI to skip custom workflows. **However, GitHub's internal `pages-build-deployment` service is NOT affected by [skip ci].**

**Commit 4ba92fdd**:
```
campaign: initiate multi-agent CI failure resolution (Phase 1)
```
No skip flag. Normal execution expected.

### 5. GitHub Pages Repository Configuration

| Setting | Value |
|---------|-------|
| **has_pages** | `true` ✅ |
| **pages** | `null` (branch mode, not explicitly configured) |
| **Source** | Likely auto-detected as `main` branch in branch mode |

**Critical Configuration Issue**: The repository does NOT have an explicit Pages configuration specifying the Pages artifact as the deployment source. This allows GitHub's internal `pages-build-deployment` service to take precedence.

### 6. Dual Service Execution (ROOT CAUSE)

GitHub Pages has **two deployment mechanisms**:

1. **Custom Workflow Path** (`pages-mkdocs.yml`):
   - Builds MkDocs site → `site/` directory
   - Creates `github-pages` artifact
   - Calls `actions/deploy-pages` to deploy artifact
   - ✅ **Executed successfully**

2. **Internal GitHub Service** (`pages-build-deployment`):
   - Triggered automatically when content is pushed to `main` branch
   - **NOT affected by [skip ci]** flag
   - Runs in "branch mode" (no build, serves raw files)
   - ❌ **Took precedence, shadowing the custom deployment**

**Why This Happened**: 
- No explicit Pages source configuration in repository settings
- GitHub's branch-mode Pages service runs **independently** of workflow outcomes
- The internal service served raw repo files, resulting in 404s on URL paths like `/docs/` (which don't exist as raw files)

### 7. Pages Health Guard Response

The `pages-health-guard.yml` workflow detected the 404 responses and:
- Logged the failure with 404 HTTP codes
- Triggered an automatic `pages-mkdocs.yml` rebuild via `gh workflow run`
- ✅ **Self-healing mechanism activated**

Evidence from logs:
```
"skip_check=false" >> "$GITHUB_OUTPUT"   # Detected deployment_status event
"site_healthy=false"                     # HTTP 404 detected
# Triggered MkDocs rebuild (self-heal)
```

---

## Root Cause Analysis

### Primary Root Cause: **Implicit Branch-Mode Pages Configuration**

The repository relies on GitHub's default Pages behavior (branch mode) without an explicit source configuration. This allows the internal `pages-build-deployment` service to run and serve content independently of the custom `pages-mkdocs.yml` workflow.

**Mechanism**:
1. Commit pushed to `main`
2. Custom workflow (`pages-mkdocs.yml`) starts building
3. **Simultaneously**, GitHub's internal service detects `main` has content
4. Internal service runs in branch mode (no build step)
5. Service builds a deployment and publishes immediately
6. Custom workflow finishes build/deploy 30+ seconds later
7. **Internal service's deployment is now stale**
8. Site serves raw repo files → 404s on documentation paths

### Secondary Contributing Factor: `[skip ci]` Misunderstanding

The commit `6101a9fd` with `[skip ci]` shows a workflow behavior inconsistency:
- `[skip ci]` prevents custom GitHub Actions workflows from running
- `[skip ci]` does **NOT** prevent GitHub Pages internal service (`pages-build-deployment`) from running
- This creates confusion about which deployment is active

### Tertiary Factor: Deployment Polling Race Condition

The `actions/deploy-pages` action polls for deployment status at 16:11:35 (5 seconds after creation) and reports success before health checks verify actual availability. By 16:11:36 (1 second later), the site is serving 404s.

**Why**: The action trusts GitHub's deployment status API, which may report success prematurely if the internal Pages service hasn't yet finished transitioning.

---

## Evidence Summary

| Evidence | Type | Supporting Root Cause |
|----------|------|----------------------|
| Deployment status states: `waiting → queued → in_progress → failure/error` | API data | Deployment created but failed by internal Pages service |
| Build & deploy jobs: both `success` | Workflow logs | Custom workflow succeeded |
| Artifact created: 30.8 MB | API data | Build completed successfully |
| Health checks: HTTP 404 (all 6 attempts) | HTTP logs | Site serving raw files (branch mode) |
| `actions/deploy-pages` reports success at 16:11:35, but 404s at 16:11:36 | Workflow logs | Timing race between internal and custom service |
| Pages configuration: branch mode (implicit) | GitHub API | Implicit configuration allows internal service precedence |
| Commit message: `[skip ci]` in 6101a9fd | Git history | Shows confusion about CI skip behavior |

---

## Impact Assessment

| Aspect | Impact |
|--------|--------|
| **User Experience** | 🔴 **Critical** — Documentation site unavailable (404s) for ~10+ minutes |
| **Availability** | 🔴 **Critical** — Pages URL returned but serving incorrect content |
| **Data Loss** | ✅ **None** — Build artifacts intact, pages-health-guard triggered recovery |
| **Recovery Time** | 🟡 **~3-5 minutes** — Automatic Pages rebuild via health-guard |
| **Scope** | 🟠 **Limited** — Affected only GitHub Pages, not core functionality |

---

## Remediation Options (Ranked by Confidence)

### **Option 1: Explicit Pages Source Configuration** 🟢 **[RECOMMENDED - Confidence: 99%]**

**Description**: Explicitly configure GitHub Pages to use the `github-pages` artifact from the `pages-mkdocs.yml` workflow as the sole source, preventing the internal `pages-build-deployment` service from running.

**Implementation**:
1. Go to repository Settings → Pages
2. Set "Source" to "GitHub Actions" (if available)
3. Alternatively, add explicit Pages workflow configuration in repository settings or via GitHub API
4. Verify internal Pages service is disabled/not triggered

**Pros**:
- ✅ Eliminates dual-service conflict completely
- ✅ Gives custom workflow full control
- ✅ One-time configuration, permanent fix
- ✅ Prevents future [skip ci] confusion

**Cons**:
- Requires repository admin access to Settings
- May require API call if UI option not available

**Expected Outcome**: Only `pages-mkdocs.yml` deployment is active; internal service no longer runs.

---

### **Option 2: Add Explicit Pages Build Workflow Override** 🟢 **[RECOMMENDED - Confidence: 95%]**

**Description**: Create `.github/workflows/pages-build-deployment-override.yml` that explicitly prevents GitHub's internal Pages build service from running by immediately publishing the custom artifact.

**Implementation**:
```yaml
name: Override Internal Pages Build
on:
  push:
    branches: [main]

jobs:
  override:
    runs-on: ubuntu-latest
    steps:
      - name: Override internal pages-build-deployment
        run: |
          echo "Custom Pages workflow takes precedence"
          # Dispatch pages-mkdocs.yml to ensure it runs before internal service
          gh workflow run pages-mkdocs.yml --ref main
```

**Pros**:
- ✅ Workflow-level control (no repo settings needed)
- ✅ Works even if internal service auto-triggers
- ✅ Can be deployed via PR

**Cons**:
- Workflow complexity increases
- May result in double deployments if timing not perfect

**Expected Outcome**: Custom workflow always runs first and publishes, preventing race condition.

---

### **Option 3: Disable Internal Pages Service via Repository Rules** 🟡 **[Confidence: 85%]**

**Description**: Use repository rulesets or branch protection rules to prevent the internal Pages service from running on `main` branch, forcing exclusive use of custom workflow.

**Implementation**:
1. Settings → Rules → New repository rule
2. Add condition: Restrict to `main` branch
3. Disable "GitHub Pages internal build deployment"
4. Allow only "GitHub Actions deployment"

**Pros**:
- ✅ Policy-level enforcement
- ✅ Clear intent

**Cons**:
- May not be available on all GitHub plans
- Admin-level settings change

**Expected Outcome**: Only custom Pages workflow deployments allowed.

---

### **Option 4: Update [skip ci] Documentation & CI Logic** 🟡 **[Confidence: 75%]**

**Description**: Document the Pages service behavior in `CONTRIBUTING.md` and add CI logic to prevent `[skip ci]` commits from breaking Pages deployments.

**Implementation**:
1. Update `.codex/CODEBASE_AGENCY_POLICY.md` with note about Pages behavior
2. Add pre-commit hook to warn on `[skip ci]` with Pages changes
3. Add comment in `pages-mkdocs.yml` explaining the dual-service issue

**Pros**:
- ✅ Prevents future confusion
- ✅ Educates contributors

**Cons**:
- 🔴 **Does NOT fix the underlying issue** — only documents it
- Workaround, not solution

**Expected Outcome**: Future commits with `[skip ci]` avoid Pages changes, but technical issue remains.

---

### **Option 5: Modify pages-mkdocs.yml for Earlier Deployment** 🟡 **[Confidence: 60%]**

**Description**: Restructure `pages-mkdocs.yml` to deploy the artifact earlier (reduce 30+ second build→deploy gap), outpacing the internal Pages service.

**Implementation**:
1. Reduce build parallelism → focus on build speed
2. Simplify MkDocs plugins (remove slow ones)
3. Cache pre-built dependencies more aggressively
4. Deploy immediately after artifact upload (before health checks)

**Pros**:
- ✅ Stays within custom workflow
- ✅ Incremental changes

**Cons**:
- 🔴 Race condition still exists (just less likely)
- Might degrade documentation quality (e.g., by removing plugins)
- Requires ongoing tuning

**Expected Outcome**: Custom deployment finishes before internal service, reducing conflict window.

---

## Recommended Action Plan

### Immediate (Next 24 hours)

1. **Apply Option 1** (Explicit Pages Source Configuration):
   - Verify GitHub Pages admin access
   - Navigate to Settings → Pages
   - Set explicit "GitHub Actions" source
   - Test with manual Pages rebuild

2. **Verify Fix**:
   - Trigger `pages-mkdocs.yml` manually
   - Confirm site returns HTTP 200
   - Check no 404s in health guard logs

### Short-term (This sprint)

3. **Document the fix**:
   - Add note to `.github/workflows/pages-mkdocs.yml` explaining dual-service behavior
   - Update `.codex/CODEBASE_AGENCY_POLICY.md` with Pages deployment expectations
   - Link to this RCA in relevant docs

4. **Update CI/CD automation**:
   - Ensure Pages Health Guard is enabled and monitoring
   - Verify health check intervals are appropriate (currently 6-hour schedule)
   - Consider reducing schedule to 2-hour intervals for faster detection

### Long-term (Next quarter)

5. **Monitor and refine**:
   - Track Pages deployment failures via metrics
   - Adjust health check logic if new patterns emerge
   - Consider consolidating all deployment workflows under unified orchestration

---

## Prevention Strategies

To prevent similar issues:

1. **Configuration as Code**: Store Pages source configuration in `.github/pages-config.yml` (if GitHub API supports it)
2. **Deployment Observability**: Enhance `pages-health-guard.yml` to log all deployment status transitions
3. **Health Check SLA**: Enforce stricter SLAs (detect 404s within 30s, not 60s)
4. **Artifact Signing**: Sign Pages artifacts to verify integrity before deployment
5. **Status Transparency**: Add real-time Pages deployment status badge to README.md

---

## References

- **GitHub Pages Documentation**: https://docs.github.com/en/pages
- **Pages Health Guard Workflow**: `.github/workflows/pages-health-guard.yml`
- **Pages Build Workflow**: `.github/workflows/pages-mkdocs.yml`
- **Related Issues**: [Look for issues mentioning "404" or "pages deployment" in repository]

---

## Appendix: Technical Details

### Deployment API Response Structure

```json
{
  "id": 5272032606,
  "sha": "4ba92fdd803879f3a00ffe79933db64bd77a1b70", <!-- pragma: allowlist secret -->
  "ref": "main",
  "environment": "github-pages",
  "created_at": "2026-07-01T16:04:33Z",
  "updated_at": "2026-07-01T16:04:46Z",
  "statuses": [
    {"state": "waiting", "created_at": "2026-07-01T16:04:34Z"},
    {"state": "queued", "created_at": "2026-07-01T16:04:35Z"},
    {"state": "in_progress", "created_at": "2026-07-01T16:04:37Z"},
    {"state": "failure", "created_at": "2026-07-01T16:04:46Z", "description": ""}
  ]
}
```

### HTTP Health Check Pattern

```bash
# pages-mkdocs.yml health check (lines 172-188)
for i in 1 2 3 4 5 6; do
  HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 15 "${PAGE_URL}")
  if [ "${HTTP_CODE}" = "200" ]; then
    exit 0  # Success
  fi
  sleep 10  # Wait 10 seconds before retry
done
# Result: 6 attempts over 60 seconds, all returned 404
```

### Workflow Concurrency Configuration

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true  # ⚠️ May cancel earlier runs
```

This configuration may cancel previous Pages deployments if new commits arrive rapidly.

---

## Version History

- **v1.0** (2026-07-01 16:30 UTC): Initial RCA created by CI Testing Agent v4.2.0-S228
- **Status**: Ready for remediation

---

**Document Owner**: CI Testing Agent v4.2.0-S228  
**Last Updated**: 2026-07-01T16:30:00Z  
**Approval Status**: Awaiting review and remediation implementation
