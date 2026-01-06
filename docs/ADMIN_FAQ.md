# _codex_ Admin FAQ

> Frequently Asked Questions for Repository Administrators

---

## General Questions

### Q: What permissions do I need?

**A:** You need one of the following:
- **Organization Owner** - Full access to all settings
- **Repository Admin** - Can configure repository settings and secrets
- **Organization Admin** - Can create GitHub Apps for the organization

### Q: How long does full setup take?

**A:** 
- **Quick Start (critical items):** 5 minutes
- **Full configuration:** 45-60 minutes
- **With GitHub App creation:** 60-90 minutes

### Q: Can I set this up in stages?

**A:** Yes! Start with the [Quick Start Guide](./ADMIN_QUICKSTART.md) to enable basic functionality, then complete the full guide when time permits.

---

## GitHub Copilot Questions

### Q: Is Copilot required?

**A:** No. Copilot enhances the development experience but the repository functions without it. The PR Reviewer Bot uses a separate GitHub App.

### Q: What's the difference between Copilot and Copilot Agents?

**A:** 
- **Copilot:** AI pair programming in the IDE
- **Copilot Agents:** (Preview) Automated task execution triggered by mentions

### Q: Copilot Agents aren't available for my organization

**A:** This feature Phase 5 be in preview. You can:
1. Use the GitHub App approach (Section 2 of the full guide)
2. Contact GitHub support about preview access
3. Wait for general availability

---

## GitHub App Questions

### Q: Do I have to create a GitHub App?

**A:** Only if you want the automated PR Reviewer Bot. Basic CI/CD works without it.

### Q: Can I use a personal account to create the app?

**A:** Yes, but:
1. The app will be owned by your personal account
2. You can later transfer it to the organization
3. Organization-owned apps are recommended for teams

### Q: I can't find the "Private keys" section

**A:** After creating the app:
1. Go to the app settings page
2. Scroll down past "Basic information"
3. Look for the "Private keys" section
4. Click "Generate a private key"

### Q: What if I lose the private key?

**A:** 
1. Go to the app settings
2. Generate a new private key
3. Delete the old one
4. Update the `CODEX_PRIVATE_KEY` secret

---

## Secrets Questions

### Q: Where do I find the App ID?

**A:** 
1. Go to: `https://github.com/settings/apps/[app-name]`
2. The App ID is displayed at the top of the page
3. It's a numeric value like `123456`

### Q: Where do I find the Installation ID?

**A:** 
1. Go to: `https://github.com/organizations/Aries-Serpent/settings/installations`
2. Click "Configure" next to the app
3. Look at the URL: `.../installations/[INSTALLATION_ID]`

### Q: Are secrets encrypted?

**A:** Yes. GitHub encrypts all secrets using libsodium sealed boxes. Secrets are:
- Encrypted at rest
- Never exposed in logs
- Only available to workflows that need them

### Q: Can I use organization secrets instead?

**A:** Yes, but ensure:
1. The repository has access to those secrets
2. The secret names match what workflows expect
3. Repository secrets override organization secrets of the same name

---

## Workflow Questions

### Q: Workflows are failing with permission errors

**A:** Check these settings:
1. Go to: Settings → Actions → General
2. Set Workflow permissions to "Read and write"
3. Enable "Allow GitHub Actions to create and approve pull requests"
4. Save changes

### Q: How do I manually trigger a workflow?

**A:** 
1. Go to: Actions tab
2. Select the workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

### Q: Can I disable certain workflows?

**A:** Yes:
1. Rename the file with `.disabled` extension (e.g., `workflow.yml.disabled`)
2. Or use the workflow's `on:` trigger conditions
3. Or disable via Settings → Actions → Runners

---

## Security Questions

### Q: What security features should I enable?

**A:** Enable all of these:
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Secret scanning
- ✅ Push protection

### Q: Why is push protection blocking my commits?

**A:** Push protection blocks commits containing patterns that look like secrets. Either:
1. Remove the secret from your code
2. Use environment variables instead
3. Add a bypass if it's a false positive (not recommended)

### Q: How do I handle Dependabot alerts?

**A:** 
1. Review the alert in Security tab
2. If valid: update the dependency
3. If false positive: dismiss with reason
4. For breaking changes: check the ignore list in `.github/dependabot.yml`

---

## Branch Protection Questions

### Q: Required status checks aren't showing up

**A:** Status checks must run at least once before they appear:
1. Create a test PR or trigger workflows manually
2. Wait for workflows to complete
3. Refresh the branch protection settings
4. The job names should now be available

### Q: Should I require reviews from Code Owners?

**A:** Recommended for production, optional for development:
- Enable for `main` branch in production environments
- Can be optional for feature branches
- Requires a valid `CODEOWNERS` file

---

## Troubleshooting Decision Tree

```
Issue: Workflow failing
├── Permission error?
│   └── Check: Settings → Actions → Workflow permissions
├── Missing secret?
│   └── Check: Settings → Secrets and variables → Actions
├── Timeout?
│   └── Check: Workflow has `timeout-minutes` set appropriately
└── Unknown error?
    └── Check: Workflow logs for specific error message
```

```
Issue: Can't create GitHub App
├── Not an org owner?
│   └── Ask org owner or create under personal account
├── App name already taken?
│   └── Choose a different name
└── Missing required fields?
    └── Ensure all required fields are filled
```

```
Issue: Secrets not working
├── Secret name typo?
│   └── Verify exact name matches workflow reference
├── Secret in wrong scope?
│   └── Check if using org vs repo secrets correctly
└── Secret recently added?
    └── Re-run the workflow (secrets are loaded at run start)
```

---

## Still Need Help?

1. **Check logs:** Actions → Select run → View job logs
2. **Search issues:** `https://github.com/Aries-Serpent/_codex_/issues`
3. **GitHub Docs:** `https://docs.github.com`
4. **Create issue:** Use the repository issue tracker

---

*Last updated: 2024-12-21*
