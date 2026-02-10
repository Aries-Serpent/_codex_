# Branch Protection Configuration

> **Purpose:** Prevent merging PRs with failing CI checks  
> **Last Updated:** 2026-02-10  
> **Related Issue:** Post-PR#2956 CI failures on main

---

## Required Settings for `main` Branch

### Status Checks (REQUIRED)

The following checks MUST pass before merging:

| Check Name | Description | Required |
|------------|-------------|----------|
| **Comprehensive Tests with Caching** | Primary test suite | ✅ YES |
| **Test Summary (Sentinel)** | Final test status validation | ✅ YES |
| **CodeQL** | Security vulnerability scanning | ✅ YES |
| **Security Scan** | Secret scanning and SAST | ✅ YES |

### Branch Protection Rules

```yaml
# Recommended branch protection settings
protected_branch: main
rules:
  require_status_checks:
    enabled: true
    strict: true  # Require branches to be up to date before merging
    contexts:
      - "Comprehensive Tests with Caching / Python 3.12 Tests"
      - "Test Summary / Validate Results"
      - "CodeQL"
      - "Security Scan"
  
  require_pull_request:
    enabled: true
    required_approving_review_count: 1
    dismiss_stale_reviews: true
    require_code_owner_reviews: true
  
  require_conversation_resolution: true
  
  enforce_admins: false  # Allow admins to bypass for emergencies (documented)
  
  allow_force_pushes: false
  allow_deletions: false
```

---

## Configuration Steps (GitHub UI)

1. Navigate to: **Settings → Branches → Branch protection rules**
2. Click **Add branch protection rule** or edit existing rule for `main`
3. Configure as follows:

### Basic Settings
- [x] **Require a pull request before merging**
  - [x] Require approvals: **1**
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners

### Status Checks
- [x] **Require status checks to pass before merging**
  - [x] **Require branches to be up to date before merging**
  - Search and add these checks:
    - `Comprehensive Tests with Caching / Python 3.12 Tests`
    - `Test Summary / Validate Results`
    - `CodeQL`
    - `Security Scan`

### Additional Settings
- [x] **Require conversation resolution before merging**
- [ ] Do not check: "Require linear history"
- [ ] Do not check: "Require deployments to succeed"
- [ ] Do not check: "Lock branch"
- [ ] Do not check: "Do not allow bypassing the above settings"  
  *(Allow admin bypass for documented emergencies only)*

4. Click **Save changes**

---

## Emergency Override Protocol

If an emergency merge is required despite failing checks:

### Prerequisites
1. Document the emergency in the PR description
2. Get explicit approval from @mbaetiong or repository admin
3. Acknowledge the risk in writing

### Steps
1. Admin with bypass permissions merges the PR
2. **IMMEDIATELY** create a hotfix PR to address the failing tests
3. Document the incident in `.codex/change_log.md`
4. Post-mortem review within 24 hours

### Documentation Template

```markdown
## Emergency Merge Documentation

**Date:** YYYY-MM-DD HH:MM UTC
**PR:** #XXXX
**Approver:** @username
**Reason:** [Brief explanation of emergency]

### Failing Checks at Time of Merge
- [ ] Check 1: [reason acceptable]
- [ ] Check 2: [reason acceptable]

### Remediation Plan
- [ ] Hotfix PR created: #XXXX
- [ ] Timeline: [estimated completion]
- [ ] Owner: @username

### Post-Mortem
- [ ] Completed: YYYY-MM-DD
- [ ] Findings: [link to document]
```

---

## Monitoring & Alerts

### Failed Check Notifications

Configure GitHub Actions to post warnings when tests fail:

```yaml
# In workflow file
- name: Warn about CI failures
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '⚠️ **CI Check Failed** - Please fix before merging!\n\nFailing tests on main branch hide future regressions.'
      })
```

---

## Related Documentation

- [Pull Request Template](.github/pull_request_template.md) - Pre-merge verification checklist
- [AI Codebase Agency Policy](.codex/CODEBASE_AGENCY_POLICY.md) - AI agent CI obligations
- [Contributing Guide](CONTRIBUTING.md) - Development workflow

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial creation after PR#2956 incident | Copilot |
