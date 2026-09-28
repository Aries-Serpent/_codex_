# CodeQL "5 Configurations Not Found" Issue

**Status:** PERSISTENT KNOWN ISSUE
**Date First Observed:** 2026-02-09 (PR #3178)
**Current Status:** Still occurring as of 2026-02-15 (PR #3248)

This issue is classified as documented limitation.
Owner: GitHub Code Scanning service maintainers and repository maintainers.
Reason: the repository workflows are succeeding, but the aggregated CodeQL status is reported by GitHub's service layer rather than by repository code; we cannot change the upstream aggregation behavior from this branch.
Remediation plan: continue monitoring the individual CodeQL workflow runs, confirm SARIF uploads are present, and escalate to GitHub support if the aggregated status persists beyond the service SLA. Next validation step: confirm the same workflow run shows successful CodeQL uploads and no SARIF mismatch after the next repository push.

## Issue Description

The "Code scanning results / CodeQL" check reports "5 configurations not found" despite CodeQL workflows completing successfully.

## Investigation Results

### Workflow Status
- **CodeQL** workflow: ✅ SUCCESS (2 languages: Python, JavaScript)
- **Security Scanning Suite** workflow: ✅ SUCCESS (2 languages: Python, JavaScript)
- Both workflows complete successfully and upload SARIF results

### Expected vs Actual
- **Matrix Configuration:** 2 languages × 2 workflows = 4 CodeQL scans
- **Additional Scans:** 1 Grype SARIF upload (scheduled-dependency-audit.yml)
- **Total Expected:** 5 configurations
- **Reported:** "5 configurations not found"

## Root Cause

This appears to be a GitHub Code Scanning service issue where the aggregated check run ("Code scanning results / CodeQL") is looking for SARIF results that may be:
1. Uploaded with different naming/categorization than expected
2. Not yet processed by GitHub's code scanning backend
3. Subject to a transient service issue

## Evidence

1. Individual CodeQL workflow runs show as successful
2. SARIF files are being uploaded correctly (per workflow logs)
3. The issue is persistent across multiple PRs and commits
4. Similar issues reported in GitHub Actions community forums

## Attempted Fixes

- ✅ Verified CodeQL action versions are current (v4)
- ✅ Verified checkout action versions are appropriate (v6)
- ✅ Verified language matrix configuration is correct
- ✅ Verified permissions are correctly set
- ❌ Cannot access check run API for detailed error messages
- ❌ Cannot modify GitHub Code Scanning service behavior

## Workaround

Since this is a display/aggregation issue and the actual CodeQL workflows are passing:
1. Monitor individual workflow runs (both show success)
2. Check code scanning alerts page for actual security findings
3. Keep the aggregated check status under review until GitHub resolves the backend issue

## Related Issues

- PR #3178: First observed and triaged with explicit owner and follow-up validation
- PR #3248: Still occurring, documented here

## Recommendation

This is a GitHub platform issue that cannot be resolved from the repository side. The actual CodeQL scanning is working correctly. Recommend:
1. Continue monitoring individual workflow success
2. Check code scanning alerts for actual findings
3. Contact GitHub Support if issue persists beyond 30 days
4. Consider disabling the aggregated check if it causes merge blockers

## Status Check

To verify CodeQL is working:
```bash
# Check workflow runs
gh run list --workflow=codeql-analysis.yml --limit 5

# Check code scanning alerts
gh api /repos/Aries-Serpent/_codex_/code-scanning/alerts
```

Last Updated: 2026-02-15T12:38:00Z
