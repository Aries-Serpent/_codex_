# GitHub Pages Deployment Fix — Quick Start

## Problem
Pages site returns HTTP 404 despite successful build and deployment.
Deployments marked as "failed" or "error" in GitHub API.

## Root Cause
GitHub's internal `pages-build-deployment` service (branch mode) serves raw files and shadows the custom `pages-mkdocs.yml` workflow deployment.

## Solution
**Explicitly configure GitHub Pages to use GitHub Actions as source.**

## Steps

### 1. Go to Repository Settings
```
GitHub Web UI → Repository → Settings → Pages
```

### 2. Change Pages Source
- **Current**: "Branch" (with implicit branch mode)
- **Change to**: "GitHub Actions" (if available)
- **Alternative**: Configure in repository settings API

### 3. Verify Configuration
```bash
# Check current Pages config
gh api repos/Aries-Serpent/_codex_ -q .pages

# Should show source as github-actions (not branch mode)
```

### 4. Test Fix
```bash
# Trigger pages-mkdocs.yml manually
gh workflow run pages-mkdocs.yml --ref main

# Wait for completion (typically 5-10 minutes)

# Check health
curl -I https://aries-serpent.github.io/_codex_/
# Should return HTTP 200, not 404
```

### 5. Verify in Pages Health Guard Logs
```bash
# Check pages-health-guard.yml workflow run
gh run view <run_id> --log
# Should show "health_status=ok"
```

## Expected Outcome
✅ Pages site serves HTTP 200  
✅ No more 404s after deployment  
✅ Only custom workflow deployment runs (no dual service)  
✅ Deployments transition to "success" state (not "failure")

## Automation
The `pages-health-guard.yml` workflow will automatically:
1. Detect healthy status (HTTP 200)
2. Log success
3. No further remediation needed

## Troubleshooting

### Still seeing 404 after fix?
1. Hard refresh: `curl -I https://aries-serpent.github.io/_codex_/ -H "Cache-Control: no-cache"`
2. Wait 5 minutes for CDN propagation
3. Check Pages Health Guard logs: `gh run list --workflow pages-health-guard.yml -L 5`

### Deployment still shows "failure"?
1. Delete old failed deployments: `gh api repos/Aries-Serpent/_codex_/deployments/<id> -X DELETE`
2. Trigger fresh build: `gh workflow run pages-mkdocs.yml --ref main`

### Internal Pages service still running?
1. Go to Settings → Pages
2. Confirm "Source" is set to "GitHub Actions" (not Branch)
3. Contact GitHub Support if issue persists

## References
- Full RCA: `.codex/PAGES_DEPLOYMENT_RCA_20260701.md`
- Pages Workflow: `.github/workflows/pages-mkdocs.yml`
- Health Guard: `.github/workflows/pages-health-guard.yml`

---
**Status**: Ready for implementation  
**Timeline**: 5-10 minutes to apply + test
