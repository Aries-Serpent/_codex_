# Lane 6 Quick Reference - Deployment Automation Operations

**For Release Managers & Operations Team**  
**Valid from**: 2026-07-07 (Day 0)  
**Activation**: Day 42+ (when P1 gate passes)  
**Release**: Day 70 (v0.1.0-final)

---

## ⚡ Emergency Quick Links

| Need | File | Purpose |
|------|------|---------|
| **Release it now** | `docs/deployment/DEPLOYMENT_GUIDE.md` | Step-by-step release process |
| **Something broke** | `docs/deployment/ROLLBACK_CHECKLIST.md` | Rollback procedures |
| **Pre-release checks** | `.codex/RELEASE_GATE_CHECKLIST.md` | Gate verification |
| **Automate rollback** | `python scripts/deploy/rollback_release.py` | Automated rollback script |

---

## 🚀 Release in 5 Steps

### Step 1: Prepare (Day 60)
```bash
# Update version
sed -i 's/version = "[^"]*"/version = "0.1.0"/' pyproject.toml

# Update CHANGELOG
# (Add section: ## [0.1.0] - 2026-07-07)

# Create PR
git checkout -b release/v0.1.0
git add pyproject.toml CHANGELOG.md
git commit -m "chore: Prepare v0.1.0 release"
git push origin release/v0.1.0
# Open PR, wait for pre-release-validation.yml to pass
```

### Step 2: Merge (when approved)
```bash
# Merge PR to main
# Wait for all checks to pass
```

### Step 3: Tag (Day 70)
```bash
# Create and push tag - THIS STARTS THE RELEASE
git tag -a v0.1.0 -m "Release v0.1.0 - Cognitive Brain"
git push origin v0.1.0
```

### Step 4: Monitor (15-20 min)
```bash
# Watch workflows in GitHub Actions
# release-to-pypi.yml should complete in ~15 min
# Then smoke-tests-deployment.yml starts (15-20 min)
```

### Step 5: Verify (5 min)
```bash
# Test from PyPI
pip install codex-ml[core]==0.1.0
python -c "from cognitive_brain.ooda import OODALoop; print('✅ Works!')"
```

**Total time**: ~1 hour (mostly automated)

---

## 🆘 Rollback in 3 Commands

```bash
# 1. Identify the issue
# (Check smoke test results or user reports)

# 2. Execute rollback
python scripts/deploy/rollback_release.py \
  --version v0.1.0 \
  --restore-version v0.0.9 \
  --reason "Critical import failure in core profile"

# 3. Verify
pip install --upgrade codex-ml
pip show codex-ml | grep Version
# Should show 0.0.9
```

**Total time**: < 5 minutes

---

## 📊 Key Metrics to Watch

### During Release (15-20 min)
- ✅ release-to-pypi.yml job status (green = success)
- ✅ All steps complete without errors
- ✅ PyPI accepts wheel upload

### During Smoke Tests (15-20 min)
- ✅ All 12 test combinations passing
- ✅ No timeout failures
- ✅ Core profile loads offline
- ✅ Runtime/Full profiles import torch/pytest

### Post-Release (first 24 hours)
- 📈 Download count increasing on PyPI
- ⚠️ Check for error reports in GitHub issues
- 📊 Review metrics in `.codex/RELEASE_METRICS_v0.1.0.json`

---

## 🔒 Release Safety Checklist

**Before pushing tag**:
- [ ] P0 Gate verified: `ls .codex/PROFILE_DRIFT_AUDIT.json`
- [ ] P1 Gate verified: `ls sbom.json`
- [ ] P2 Gate verified: `ls .github/workflows/release-to-pypi.yml`
- [ ] Version bumped: `grep version pyproject.toml`
- [ ] CHANGELOG updated: `grep "\[0.1.0\]" CHANGELOG.md`
- [ ] All tests passing: Latest CI status green
- [ ] PyPI credentials configured: GitHub Secrets check
- [ ] No uncommitted changes: `git status` clean

---

## 🔧 Troubleshooting Cheat Sheet

| Problem | Solution |
|---------|----------|
| **release-to-pypi.yml fails** | Check workflow logs → Check PyPI credentials → Retry |
| **smoke-tests fail** | Rollback immediately (see above) → Investigate → v0.1.1 patch |
| **PyPI upload hangs** | Check network → Retry upload → Manual upload if needed |
| **Smoke test network error** | Wait 30s, retry (PyPI indexing takes 5-10 min) |
| **Tag already exists** | `git tag -d v0.1.0 && git push origin --delete v0.1.0` → retry |

---

## 📋 Pre-Release Validation

The `.github/workflows/pre-release-validation.yml` workflow **automatically** checks:

- ✅ Version is bumped higher than last release
- ✅ CHANGELOG.md has entry for new version
- ✅ P0 gate files present (drift audit, manifests)
- ✅ P1 gate files present (SBOM)
- ✅ P2 gate files present (workflows, guides, scripts)

**If any check fails**: Fix the issue and update the PR. Workflow will re-run.

---

## 🎯 Success Indicators

### Successful Release
```
✅ release-to-pypi.yml completed
✅ PyPI shows version 0.1.0
✅ smoke-tests-deployment.yml started automatically
✅ All 12 smoke tests passing
✅ GitHub release created with artifacts
✅ pip install codex-ml==0.1.0 works
```

### Successful Rollback
```
✅ rollback_release.py executed < 5 min
✅ PyPI shows 0.1.0 as yanked
✅ PyPI shows 0.0.9 as latest
✅ pip install codex-ml installs 0.0.9
✅ GitHub issue created documenting rollback
```

---

## 📞 Critical Contacts

- **Release Manager**: @mbaetiong
- **DevOps**: [team contact]
- **Security Issues**: security@[org]
- **Incident Response**: [channel]

---

## 🔑 Key Files Reference

```
Release Pipeline:
  .github/workflows/release-to-pypi.yml          (Main release workflow)
  .github/workflows/smoke-tests-deployment.yml   (Post-release tests)
  .github/workflows/pre-release-validation.yml   (Pre-release gates)

Documentation:
  docs/deployment/DEPLOYMENT_GUIDE.md            (How to release)
  docs/deployment/ROLLBACK_CHECKLIST.md          (How to rollback)
  .codex/RELEASE_GATE_CHECKLIST.md               (Gate definitions)

Automation:
  scripts/deploy/rollback_release.py             (Rollback script)

Tracking:
  .codex/LANE_6_P2.2_EXECUTION_SUMMARY.md        (What was delivered)
  .codex/LANE_6_CHECKPOINT_P2.2_START.md         (Progress tracking)
```

---

## ⚙️ Environment Setup

### PyPI Publishing
```bash
# Set in GitHub Secrets:
PYPI_API_TOKEN = "pypi-AgEIc..."  # PyPI token with upload permission
```

### Git Configuration
```bash
# Ensure git is configured:
git config user.name "Release Bot"
git config user.email "releases@[org]"
```

### Optional: Local Dry-Run
```bash
# Test workflow locally
act -j release-to-pypi  # Using act tool (GitHub Actions locally)
```

---

## 📈 Monitoring After Release

### First 24 Hours
1. Monitor PyPI statistics: https://pypistats.org/packages/codex-ml
2. Check GitHub Issues for error reports
3. Review `.codex/metrics/release-v0.1.0.json` for timing

### First Week
1. Track core vs runtime vs full profile adoption
2. Monitor issue reports by profile
3. Check for CVE/security issues
4. Assess installation success rates

### First Month
1. Gather user feedback
2. Plan v0.1.1 patch if needed
3. Decide on v0.2.0 timeline

---

## 🎓 Learning Resources

- **Full documentation**: Read `docs/deployment/DEPLOYMENT_GUIDE.md` once before first release
- **Troubleshooting**: See troubleshooting section in deployment guide
- **Rollback practice**: Dry-run rollback script with `--dry-run` flag
- **Gate definitions**: See `.codex/RELEASE_GATE_CHECKLIST.md` for gate explanations

---

## ✅ Checklist for Release Day

```
MORNING OF RELEASE:
  [ ] Final code review complete
  [ ] All tests passing
  [ ] CHANGELOG and version verified
  [ ] Standup with team (optional)

RELEASE TIME:
  [ ] Create release PR
  [ ] Merge PR once pre-release validation passes
  [ ] Create and push git tag
  [ ] Monitor release-to-pypi.yml
  [ ] Monitor smoke-tests-deployment.yml
  [ ] Verify installation works

POST-RELEASE:
  [ ] Announce on channels/social
  [ ] Update status pages/docs
  [ ] Start monitoring metrics
  [ ] Respond to user questions

24 HOURS LATER:
  [ ] Review incident reports
  [ ] Check download stats
  [ ] Assess health
  [ ] Plan next steps
```

---

**Remember**: 
- 🟢 **Green workflows** = Everything OK
- 🔴 **Red workflows** = Initiate rollback (see above)
- ⏱️ **Total time invested**: ~1 hour (mostly automated)
- 📊 **Risk level**: LOW (fully tested, automated gates, fast rollback)

---

**Valid until**: v0.2.0 release (update this guide for future releases)  
**Last verified**: 2026-07-07  
**Next review**: After first v0.1.0-final release
