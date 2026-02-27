# Quarterly Codebase Audit Checklist

**Template Version**: 1.0  
**Created**: 2025-12-12  
**Purpose**: Quarterly review of codebase health and maintenance tasks

---

## Audit Schedule

| Quarter | Audit Due | Status |
|---------|-----------|--------|
| Q1 2025 | Mar 15, 2025 | ⬜ Pending |
| Q2 2025 | Jun 15, 2025 | ⬜ Pending |
| Q3 2025 | Sep 15, 2025 | ⬜ Pending |
| Q4 2025 | Dec 15, 2025 | ✅ Completed (2025-12-12) |
| Q1 2026 | Mar 15, 2026 | ⬜ Pending |
| Q2 2026 | Jun 15, 2026 | ⬜ Pending |

---

## Pre-Audit Preparation

- [ ] Create new branch for audit work
- [ ] Review previous audit report
- [ ] Note any ongoing migration or refactoring
- [ ] Check for open issues related to technical debt

---

## Audit Checklist

### 1. Duplicate File Detection

- [ ] Run `python tools/duplicate_inventory.py . --modes exact,normalized`
- [ ] Review duplicate groups not in SHIM inventory
- [ ] Add intentional duplicates to SHIM inventory
- [ ] Create tickets for unintentional duplicates to consolidate
- [ ] **Metric**: Number of duplicate groups: ___

### 2. Configuration File Review

- [ ] Verify conf/ → configs/ migration progress
- [ ] Check for new configuration duplicates
- [ ] Update deprecation timelines if needed
- [ ] **Metric**: conf/ references remaining: ___

### 3. Backup and Temporary Files

- [ ] Scan for new .bak, .old, .backup, .tmp files
- [ ] Archive with commit SHA naming
- [ ] Update manifest
- [ ] **Metric**: Files archived: ___

### 4. Validation Log Cleanup

- [ ] Check `.codex/validation/` run count
- [ ] Archive runs older than 30 iterations
- [ ] Keep last 5 runs
- [ ] **Metric**: Runs archived: ___

### 5. Large File Review

- [ ] Identify files >1MB
- [ ] Verify large files are in appropriate locations
- [ ] Consider compression or Git LFS for new large files
- [ ] **Metric**: Large files count: ___

### 6. Security Scan Review

- [ ] Run CodeQL analysis
- [ ] Review Semgrep findings
- [ ] Check secrets baseline
- [ ] Update security reports
- [ ] **Metric**: Security findings: ___

### 7. Dependency Audit

- [ ] Run `pip-audit` or equivalent
- [ ] Check for outdated packages
- [ ] Review and address any CVEs
- [ ] **Metric**: Packages with CVEs: ___

### 8. Documentation Review

- [ ] Check for outdated documentation
- [ ] Verify README files are current
- [ ] Update any stale references
- [ ] **Metric**: Docs updated: ___

### 9. Test Coverage

- [ ] Run test suite with coverage
- [ ] Check for uncovered new code
- [ ] Review test health metrics
- [ ] **Metric**: Test coverage %: ___

### 10. CI/CD Health

- [ ] Review workflow run success rates
- [ ] Check for flaky tests
- [ ] Optimize slow workflows
- [ ] **Metric**: CI success rate %: ___

---

## Post-Audit Actions

- [ ] Create audit report (use template below)
- [ ] Update this checklist for next quarter
- [ ] Create tickets for any issues found
- [ ] Update SHIM inventory if needed
- [ ] Communicate findings to team

---

## Metrics Summary

| Metric | Previous Quarter | Current Quarter | Trend |
|--------|------------------|-----------------|-------|
| Duplicate groups | | | |
| conf/ references | | | |
| Files archived | | | |
| Large files | | | |
| Security findings | | | |
| Packages with CVEs | | | |
| Test coverage % | | | |
| CI success rate % | | | |

---

## Audit Report Template

When completing the audit, create a report using this format:

```markdown
# Quarterly Codebase Audit Report - QX 20XX

**Audit Date**: YYYY-MM-DD
**Auditor**: [Name/AI Assistant]
**Branch**: [branch name]

## Executive Summary

[Brief summary of findings]

## Key Metrics

[Fill in metrics table]

## Findings

### Critical
- [List critical issues]

### High Priority
- [List high priority items]

### Medium Priority
- [List medium priority items]

### Low Priority
- [List low priority items]

## Actions Taken

[List actions completed during audit]

## Recommendations

[List recommendations for next quarter]

## Next Audit

- **Due Date**: [next quarter date]
- **Focus Areas**: [areas to focus on]
```

---

## Automated Reminders

### GitHub Issue Template

Create a scheduled issue with this template:

```yaml
name: Quarterly Audit Reminder
about: Reminder to conduct quarterly codebase audit
title: '[Audit] Quarterly Codebase Audit - QX 20XX'
labels: ['audit', 'maintenance', 'quarterly']
assignees: ''
body: |
  ## Quarterly Audit Due

  It's time for the quarterly codebase audit.

  **Due Date**: [DATE]

  **Checklist**: See `misc/repo-owner-review/QUARTERLY_AUDIT_CHECKLIST.md`

  **Previous Report**: [Link to previous audit report]

  ## Actions

  1. [ ] Create audit branch
  2. [ ] Complete audit checklist
  3. [ ] Create audit report
  4. [ ] Address critical findings
  5. [ ] Close this issue
```

### Workflow Reminder (Optional)

If automated reminders are desired, create `.github/workflows/audit-reminder.yml`:

```yaml
name: Quarterly Audit Reminder
on:
  schedule:
    # 15th of March, June, September, December at 9 AM UTC (matches audit due dates)
    - cron: '0 9 15 3,6,9,12 *'
jobs:
  reminder:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            const now = new Date();
            const quarter = Math.ceil((now.getMonth() + 1) / 3);
            const year = now.getFullYear();

            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `[Audit] Quarterly Codebase Audit - Q${quarter} ${year}`,
              body: `## Quarterly Audit Due\n\nPlease see \`misc/repo-owner-review/QUARTERLY_AUDIT_CHECKLIST.md\` for the audit checklist.`,
              labels: ['audit', 'maintenance', 'quarterly']
            });
```

---

**Template Maintainer**: Copilot AI Assistant  
**Related Files**:
- `misc/repo-owner-review/AUDIT_REPORT_2025-12-12.md`
- `misc/repo-owner-review/RECOVERY_GUIDE.md`
- `.github/SHIM_INVENTORY.yaml`
