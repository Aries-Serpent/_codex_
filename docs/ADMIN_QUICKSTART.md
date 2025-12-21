# _codex_ Admin Quick Start Guide

> ⏱️ **Time Required:** 5 minutes for critical items

This is a condensed quick start guide. For complete documentation, see [ADMIN_IMPLEMENTATION_GUIDE.md](./ADMIN_IMPLEMENTATION_GUIDE.md).

---

## 🚨 Critical Items Only (5 Minutes)

### Step 1: Enable Workflow Permissions (2 min)

1. Go to: `https://github.com/Aries-Serpent/_codex_/settings/actions`
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
3. Click **Save**

### Step 2: Enable Security Features (2 min)

1. Go to: `https://github.com/Aries-Serpent/_codex_/settings/security_analysis`
2. Enable all of:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Secret scanning
   - ✅ Push protection

### Step 3: Verify Actions Are Enabled (1 min)

1. Go to: `https://github.com/Aries-Serpent/_codex_/actions`
2. Verify workflows are visible and can be run
3. Click any workflow → **Run workflow** to test

---

## ✅ Quick Validation

After completing the above:

```bash
# Test via GitHub CLI
gh workflow list
gh run list --limit 3
```

Or via GitHub UI:
1. Go to Actions tab
2. Verify workflows show green status
3. No permission errors in recent runs

---

## 📋 What This Enables

With these minimal settings, you enable:

- ✅ CI/CD pipeline execution
- ✅ Automated security scanning
- ✅ Dependabot updates
- ✅ PR status checks

---

## 🔜 Next Steps (When You Have More Time)

For full functionality including the PR Reviewer Bot:

1. Read: [ADMIN_IMPLEMENTATION_GUIDE.md](./ADMIN_IMPLEMENTATION_GUIDE.md)
2. Create GitHub App (Section 2)
3. Configure secrets (Section 3)
4. Set up branch protection (Section 5)

---

**Need help?** See [ADMIN_FAQ.md](./ADMIN_FAQ.md) for common questions.
