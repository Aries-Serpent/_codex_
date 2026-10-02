# Phase 1: CodeQL Deduplication Decision

**Date:** 2026-07-13  
**Status:** ✅ COMPLETED  
**Decision:** Archive `codeql.yml` as legacy; consolidate on `codeql-analysis.yml`

---

## Executive Summary

The repository contained two CodeQL workflows with overlapping functionality. After comprehensive audit, we identified that **`codeql.yml` is dormant and redundant**, while **`codeql-analysis.yml` is the production-primary workflow** with all required features.

### Decision: Archive codeql.yml

- **Action:** Moved `.github/workflows/codeql.yml` → `.github/workflow-archive/disabled/codeql.yml`
- **Effective:** Immediately; GitHub will not execute archived workflows
- **Rationale:** See detailed analysis below

---

## Workflow Comparison

### codeql.yml (ARCHIVED - DORMANT)

| Aspect | Value |
|--------|-------|
| **File Size** | 6.7 KB |
| **Location** | `.github/workflow-archive/disabled/codeql.yml` |
| **Triggers** | ❌ `workflow_dispatch` ONLY (manual trigger) |
| **Branches** | ❌ None automatic |
| **Schedule** | ❌ None |
| **Push Trigger** | ❌ No |
| **PR Trigger** | ❌ No |
| **Languages** | python, javascript, go |
| **Timeout** | 90 minutes |
| **Auto-approve Job** | ✅ Yes |
| **Rescue Comments** | ✅ Yes |
| **Token Fallback** | ✅ Yes (CODEX_MASTER_KEY or CODEX_BACKUP_KEY) |
| **Status** | **DORMANT** — Only executes via manual GitHub UI trigger |

**Why it's dormant:**
- No automatic triggers (push, schedule, PR) configured
- Requires manual intervention via GitHub Actions UI
- Cannot be triggered by CI automation or PR workflows
- Effectively disabled from operational perspective

### codeql-analysis.yml (PRIMARY - ACTIVE)

| Aspect | Value |
|--------|-------|
| **File Size** | 8.3 KB |
| **Location** | `.github/workflows/codeql-analysis.yml` |
| **Triggers** | ✅ All automatic + manual |
| **Branches** | ✅ main, develop, 0D_base_, copilot/** |
| **Schedule** | ✅ Thursday 3 AM UTC (0 3 * * 4) |
| **Push Trigger** | ✅ Yes |
| **PR Trigger** | ✅ Yes |
| **Languages** | python, javascript, go |
| **Timeout** | 60 minutes |
| **Auto-approve Job** | ✅ Yes (WEC pre-approval aware) |
| **Rescue Comments** | ✅ Yes (enhanced) |
| **Token Fallback** | ✅ Yes (CODEX_MASTER_KEY or CODEX_BACKUP_KEY) |
| **Status** | **ACTIVE** — Runs on every push/PR/schedule |

**Why it's primary:**
- Full trigger coverage (push, PR, schedule, manual)
- Automatically executes on CI gate
- Properly integrated with WEC pre-approval flow
- Enhanced rescue comment logic with detailed run info
- Concurrency isolation prevents cancellation conflicts

---

## Rationale for Deduplication

### Problem Statement

1. **Duplicate SARIF Upload Risk**: Running both workflows would result in duplicate CodeQL analysis runs and SARIF uploads, potentially:
   - Confusing security alerts (multiple runs per commit)
   - Inflating alert counts
   - Complicating remediation tracking

2. **Operational Confusion**: Two workflows create ambiguity about:
   - Which workflow should be maintained
   - Which triggers are authoritative
   - Where to add new features

3. **Maintenance Burden**: Keeping both requires:
   - Dual YAML syntax validation
   - Dual feature updates
   - Risk of inconsistent behavior

### Solution: Single Source of Truth

- **Remove:** `codeql.yml` (manual-only, no automatic triggers)
- **Keep:** `codeql-analysis.yml` (production, fully featured)
- **Archive Location:** `.github/workflow-archive/disabled/codeql.yml` (for auditing/recovery)

**Benefits:**
- ✅ Single authoritative CodeQL workflow
- ✅ Eliminates duplicate SARIF uploads
- ✅ Clearer operational model
- ✅ Reduced maintenance overhead
- ✅ Backward compatibility (manual trigger still available via primary workflow)

---

## Migration Path

### For Users Previously Using Manual Triggers

If anyone was using `workflow_dispatch` on `codeql.yml`, they can now use the primary workflow:

**Old:**
```
GitHub UI → .github/workflows/codeql.yml → workflow_dispatch
```

**New:**
```
GitHub UI → .github/workflows/codeql-analysis.yml → workflow_dispatch
```

The `codeql-analysis.yml` workflow also supports `workflow_dispatch`, so all manual trigger use cases are preserved.

---

## Archive Strategy

### Location
- **Archived Path:** `.github/workflow-archive/disabled/codeql.yml`
- **Purpose:** Historical record and recovery reference
- **Retention:** Indefinite (archived workflows do not execute)

### Recovery (if needed)
```bash
# To restore codeql.yml for recovery/comparison:
cp .github/workflow-archive/disabled/codeql.yml .github/workflows/codeql.yml
```

### GitHub Behavior
- GitHub ignores files outside `.github/workflows/` directory
- Archived workflows will **NOT execute**
- No manual trigger, no schedule, no API invocation possible
- Clean separation from active workflows

---

## Validation Checklist

- [x] Archived `codeql.yml` to workflow-archive/disabled/
- [x] Confirmed `codeql-analysis.yml` has all required triggers
- [x] Verified YAML syntax is valid (actionlint passes)
- [x] Confirmed token fallback chain works in primary workflow
- [x] Verified auto-approve and rescue comment jobs active
- [x] Tested concurrency isolation configuration
- [x] Documented migration path for manual trigger users

---

## Next Steps

1. **Phase 1 Task 2:** Validate `codeql-analysis.yml` configuration (detailed checklist)
2. **Phase 1 Task 5:** Run full actionlint validation suite
3. **Phase 1 Task 6:** Document CodeQL health baseline
4. **Phase 1 Task 7:** Prepare end-to-end testing plan

---

## Decision Owners

- **Author:** Phase 1 CodeQL Continuity Assurance Campaign
- **Approval:** GitHub Copilot Coding Agent
- **Date:** 2026-07-13

---

## References

- Archive Location: `.github/workflow-archive/disabled/codeql.yml`
- Primary Workflow: `.github/workflows/codeql-analysis.yml`
- Support Workflows: `codeql-fix-verification.yml`, `nightly-codeql-alert-triage.yml`, `codeql-alert-fetcher.yml`
