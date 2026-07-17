# Rollback Checklist - Release Deployment
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status Indicator**: **EMERGENCY** | **WARNING** | **NORMAL**

**Current Time**: [To be filled during rollback]
**Release Version**: [e.g., v0.2.1]
**Target Rollback Version**: [e.g., v0.2.1]

---

## Table of Contents

1. [Decision Tree](#decision-tree)
2. [Pre-Rollback Verification](#pre-rollback-verification)
3. [Rollback Steps](#rollback-steps)
4. [Post-Rollback Validation](#post-rollback-validation)
5. [Communication Templates](#communication-templates)
6. [Incident Post-Mortem](#incident-post-mortem)

---

## Decision Tree

### Should we rollback?

```
START
 
 Is core profile unable to import?
 YES IMMEDIATE ROLLBACK (Step 1)
 NO Continue
 
 Do smoke tests show > 2 profile failures?
 YES IMMEDIATE ROLLBACK (Step 1)
 NO Continue
 
 Was a critical CVE discovered?
 YES IMMEDIATE ROLLBACK (Step 1)
 NO Continue
 
 Are PyPI downloads failing for > 50% of users?
 YES IMMEDIATE ROLLBACK (Step 1)
 NO Continue
 
 Is performance degraded > 50% vs previous release?
 YES DISCUSS WITH TEAM Decide
 NO CONTINUE WITH RELEASE
```

### Timeline for Rollback Decision

| Issue Severity | Decision Timeline | Escalation |
|---|---|---|
| **Critical** (imports fail, crashes) | < 15 min | Immediate |
| **High** (smoke tests fail, CVE) | < 1 hour | VP Engineering |
| **Medium** (performance issue, partial failure) | < 4 hours | Engineering Lead |
| **Low** (minor bugs, non-blocking issues) | 24+ hours | Team discussion |

---

## Pre-Rollback Verification

**Timeline**: < 5 minutes
**Owner**: Release manager (with engineering lead approval for non-critical issues)

### Verify Issue Severity

**Checklist**:

- [ ] **Reproduction confirmed**: Issue reproducible in 2+ environments
 - Test environment 1: `[system/Python/profile]`
 - Test environment 2: `[system/Python/profile]`
 - Edge case: `[description]`

- [ ] **Scope understood**: Number of affected users
 - % of users affected: `___`
 - Impact type: Core / Runtime / Full / All profiles
 - Critical customer impact: Yes / No

- [ ] **Root cause identified** (if time permits)
 - Root cause: `[description]`
 - Quick fix possible: Yes / No
 - Would fix take > 1 hour: Yes / No

- [ ] **Alternative mitigation explored**
 - Workaround available: Yes / No (if yes, describe: `___`)
 - Can wait for v0.2.1 patch: Yes / No
 - Requires immediate action: Yes / No

### Decision Documentation

**Rollback Decision**:
- [ ] Yes, proceed with rollback
- [ ] No, proceed with fix (patch release)
- [ ] Hold, under investigation

**Decision Made By**: `[Name]`
**Approval From**: `[Name]` (if non-critical)
**Timestamp**: `[ISO8601]`

**Rationale**:
```
[Brief explanation of why rollback is necessary]
[Impact if we DON'T rollback]
[Impact if we DO rollback]
```

---

## Rollback Steps

### Step 1: Stop Deployments (Immediate)

**Timeline**: < 1 minute

```bash
# Prevent any new releases while we handle this
# This stops the release workflow from triggering on new tags

# If using GitHub Actions:
# 1. Go to Settings Environments
# 2. Disable "pypi" environment
# 3. Approve PRs will require manual intervention

# Or via CLI:
gh repo edit \
 --enable-branch-protection \
 --require-pr-reviews \
 --dismiss-stale-reviews \
 main

echo " Deployments stopped"
```

### Step 2: Verify Release Status (2 min)

```bash
# Check current PyPI status
curl -s https://pypi.org/pypi/codex-ml/json | \
 jq '.releases | keys[-1] as $latest | {latest: $latest}'

# Expected output:
# { "latest": "0.1.0" }

# Check for yanked status (if it exists)
curl -s https://pypi.org/pypi/codex-ml/0.1.0/json | \
 jq '.urls[0].yanked'

# Expected output: false (not yet yanked)
```

### Step 3: Mark Release as Yanked (2 min)

**Timeline**: 2-3 minutes

```bash
# Using pip to mark as yanked
python << 'EOF'
import requests
import os

VERSION = "0.1.0"
PYPI_API_TOKEN = os.getenv("PYPI_API_TOKEN")

# Mark as yanked using PyPI JSON API
# Note: This requires PYPI_API_TOKEN with permission to yank versions

headers = {
 "Authorization": f"******"
}

# Use twine for yanking (more reliable)
import subprocess
result = subprocess.run([
 "python", "-m", "twine",
 "remove", f"codex-ml=={VERSION}",
 "--skip-existing",
 "--verbose"
], env={
 **os.environ,
 "TWINE_USERNAME": "__token__",
 "TWINE_PASSWORD": PYPI_API_TOKEN
})

if result.returncode == 0:
 print(f" Version {VERSION} marked as yanked on PyPI")
else:
 print(f" Note: Yanking requires PyPI token with proper permissions")

EOF

# Alternative: Manually yank via PyPI web interface
# 1. Go to: https://pypi.org/project/codex-ml/
# 2. Click on version 0.1.0
# 3. Click "Options" "Mark as yanked"
```

### Step 4: Delete Release Tag (2 min)

**Timeline**: 2-3 minutes

```bash
# Delete local tag (if exists)
git tag -d v0.2.1 || true

# Delete remote tag
git push origin --delete v0.2.1

# Verify deletion
git tag | grep v0.2.1

# Expected: No output (tag deleted)

echo " Release tag v0.2.1 deleted"
```

### Step 5: Restore Previous Version (2 min)

**Timeline**: 2-3 minutes

```bash
# Identify previous stable version
PREVIOUS_VERSION="v0.2.1"

# If not already tagged and released
git tag -a ${PREVIOUS_VERSION} \
 -m "Rollback to previous stable release"

# Push previous version tag (if new)
git push origin ${PREVIOUS_VERSION}

# Verify on PyPI
sleep 5 # Wait for PyPI to index
pip index versions codex-ml | head -3

# Expected output shows v0.2.1 as latest (not yanked)

echo " Previous version ${PREVIOUS_VERSION} restored as latest"
```

### Step 6: Verify Rollback on PyPI (2 min)

**Timeline**: 2 minutes + 5 min index wait

```bash
# Check PyPI shows correct version as latest
curl -s https://pypi.org/pypi/codex-ml/json | \
 jq '{latest: .info.version, yanked: .info.yanked}'

# Expected output:
# {
# "latest": "0.0.9",
# "yanked": false
# }

# Verify broken version is marked yanked
curl -s https://pypi.org/pypi/codex-ml/0.1.0/json | \
 jq '{version: .info.version, yanked: .info.yanked}'

# Expected output:
# {
# "version": "0.1.0",
# "yanked": true
# }

echo " PyPI correctly shows v0.2.1 as latest, v0.2.1 as yanked"
```

### Step 7: Notify Users (2 min)

**Timeline**: 2 minutes

Create GitHub release documenting the rollback:

```bash
gh release create rollback-v0.2.1 \
 --notes "
## Release Rollback: v0.2.1

**Status**: Yanked from PyPI 
**Timestamp**: $(date -Iseconds) 
**Reason**: [COPY FROM PRE-ROLLBACK VERIFICATION]

### Action Required
- **If you installed v0.2.1**: 
 \`\`\`bash
 pip install --upgrade codex-ml
 # This will downgrade to v0.2.1
 \`\`\`

- **If you haven't installed yet**:
 Skip v0.2.1 and install latest stable version.

### Root Cause
[To be filled after incident investigation]

### Fix Timeline
- **Next patch release (v0.2.1)**: Expected [DATE]
- **Next minor release (v0.2.1)**: Expected [DATE]

### Impact
- **Users affected**: ~[N] (based on download stats)
- **Estimated downtime**: < 15 minutes (to install fix)
- **Data loss risk**: None

### Support
For questions or issues:
- [ ] File issue on GitHub: [LINK]
- [ ] Email support: support@[domain]
- [ ] Slack: #incident-response
" \
 --target main \
 --draft
```

### Step 8: Re-enable Deployments (1 min)

**Timeline**: 1 minute

Once rollback verified:

```bash
# Re-enable deployments
gh repo edit \
 --disable-branch-protection \
 main

# Resume normal operations
echo " Deployment pipeline resumed"
```

---

## Post-Rollback Validation

**Timeline**: 10-15 minutes total
**Owner**: Release manager + QA

### Verify Previous Version Works

```bash
# Test all three profiles from PyPI
for PROFILE in core runtime full; do
 python -m venv test-${PROFILE}
 source test-${PROFILE}/bin/activate
 pip install codex-ml[${PROFILE}]
 
 # Quick import test
 python -c "from cognitive_brain.ooda import OODALoop; print(' ${PROFILE} works')"
 
 deactivate
 rm -rf test-${PROFILE}
done

echo " All profiles verified"
```

### Verify PyPI State

```bash
# Confirm v0.2.1 is latest
pip index versions codex-ml | head -1
# Should show v0.2.1

# Confirm v0.2.1 is yanked
curl -s https://pypi.org/pypi/codex-ml/0.1.0/json | jq .info.yanked
# Should show true

echo " PyPI state verified"
```

### Verify GitHub State

```bash
# Confirm tag deleted
git tag | grep v0.2.1
# Should show no output

# Confirm release marked with rollback tag
gh release list | grep rollback
# Should show rollback release

echo " GitHub state verified"
```

### Monitor Download Recovery

```bash
# Check downloads resume
sleep 30
curl -s "https://pypistats.org/api/packages/codex-ml/recent?period=day" | jq .data

# Expected: Download counts increase again as users reinstall
```

---

## Communication Templates

### Template 1: Internal Team Notification

```
Subject: ROLLBACK INITIATED: codex-ml v0.2.1

Team,

A critical issue was discovered in v0.2.1 and a rollback is underway.

**Issue**: [Brief description]
**Severity**: Critical / High / Medium
**Decision Time**: [Time taken to decide]
**Rollback Time**: ~5 minutes

**Actions Taken**:
 v0.2.1 marked as yanked on PyPI
 Release tag deleted
 v0.2.1 restored as latest
 Users notified via GitHub release

**Next Steps**:
[ ] Investigate root cause (ETA: [TIME])
[ ] Develop fix (ETA: [TIME])
[ ] Release v0.2.1 patch (ETA: [TIME])

**Standby**: Incident channel for updates.

[Your Name]
```

### Template 2: Public Announcement (GitHub)

```
## Immediate Action: Please upgrade to stable version

**Status**: v0.2.1 has been recalled from PyPI

If you installed `codex-ml==0.1.0` in the last 2 hours, please run:

```bash
pip install --upgrade codex-ml
```

This will downgrade you to v0.2.1 (last stable release).

**What happened?**
- Issue: [Specific problem that affects users]
- Impact: [What breaks when using v0.2.1]
- Workaround: [Is there a workaround? If so, describe]

**Fix timeline?**
- v0.2.1 patch: Expected [DATE]
- Root cause analysis: Complete by [DATE]

**Questions?**
Please file an issue on GitHub or contact support.

We apologize for the inconvenience.
```

### Template 3: Executive Summary

```
INCIDENT REPORT: v0.2.1 Release Rollback

EXECUTIVE SUMMARY:
v0.2.1 was released and subsequently rolled back due to [ISSUE].

TIMELINE:
- 15:30: v0.2.1 released to PyPI
- 15:42: Issue detected in smoke tests
- 15:47: Rollback decision made
- 15:52: v0.2.1 yanked, v0.2.1 restored
- 16:00: All verification complete

IMPACT:
- Users affected: ~[N] (out of [TOTAL])
- Downtime: < 15 minutes (to upgrade)
- Data loss: None
- Security impact: [Describe if any]

ROOT CAUSE:
[Investigation findings]

PREVENTION:
[How we'll prevent this next time]

BUSINESS IMPACT:
- Revenue impact: [Minimal / $X / TBD]
- Reputation: [Low / Medium / High]
- SLA: [Met / Missed]
```

---

## Incident Post-Mortem

**Timeline**: 24-48 hours after rollback
**Owner**: Release manager + engineering lead
**Participants**: Everyone involved in release

### Post-Mortem Meeting

1. **Gather facts** (15 min)
 - What was released? `v0.2.1`
 - When did issue occur? `[TIME]`
 - How long to detect? `[DURATION]`
 - How long to rollback? `[DURATION]`
 - Who helped? `[NAMES]`

2. **Timeline reconstruction** (15 min)
 - Create detailed timeline from logs
 - Identify key decision points
 - Note any delays or obstacles

3. **Root cause analysis** (20 min)
 - What was the bug?
 - Why did it pass testing?
 - How can we detect it earlier?

4. **Contributing factors** (15 min)
 - Did testing miss something?
 - Was there a process gap?
 - Were communication breakdowns?

5. **Action items** (15 min)

### Post-Mortem Document

Create `.codex/incidents/rollback-v0.2.1-postmortem.md`:

```markdown
# Post-Mortem: v0.2.1 Release Rollback

**Date**: 2026-07-07 
**Duration**: 15 minutes (detection + rollback) 
**Severity**: P1 Critical

## Summary
v0.2.1 failed immediately after release due to [ISSUE].
Rollback completed in [TIME] minutes.

## Timeline
| Time | Event | Duration |
|------|-------|----------|
| 15:30 | Release pushed | - |
| 15:42 | Issue detected | +12 min |
| 15:47 | Rollback started | +5 min |
| 15:52 | Rollback complete | +5 min |

## Root Cause
[Detailed explanation of what went wrong]

## Detection
How was the issue found?
- Smoke tests caught it: YES / NO
- User reports: [If yes, how many]
- Monitoring alert: YES / NO

## Resolution
- Rollback time: 5 minutes 
- User impact: [N users, [TIME] downtime]
- Data integrity: No data loss

## Contributing Factors
1. [Factor 1]
2. [Factor 2]
3. [Factor 3]

## Preventive Measures
- [ ] Add new test case to catch this
- [ ] Update CI/CD gates
- [ ] Improve documentation
- [ ] Add monitoring alert
- [ ] Process change: [DESCRIPTION]

## Action Items
| Item | Owner | Due | Priority |
|------|-------|-----|----------|
| Implement test X | @[person] | [DATE] | P0 |
| Fix bug Y | @[person] | [DATE] | P0 |
| Review process Z | @[person] | [DATE] | P1 |

## Lessons Learned
- What did we learn?
- What will we do differently next time?

## Success Criteria for Prevention
- [Criteria 1]
- [Criteria 2]
- [Criteria 3]
```

---

## Appendix: Command Reference

### PyPI Yanking

```bash
# Mark version as yanked (requires PYPI_API_TOKEN)
export TWINE_PASSWORD="$(pass show pypi-token)"
python -m twine remove codex-ml==0.1.0

# Verify yanking
curl -s https://pypi.org/pypi/codex-ml/0.1.0/json | jq .info.yanked
```

### Git Tag Management

```bash
# Delete local tag
git tag -d v0.2.1

# Delete remote tag
git push origin --delete v0.2.1

# Create new tag
git tag -a v0.2.1 -m "Release v0.2.1"

# Push tag
git push origin v0.2.1
```

### Testing Previous Version

```bash
# Uninstall current
pip uninstall -y codex-ml

# Install previous
pip install codex-ml==0.0.9

# Verify
pip show codex-ml
```

---

## Approval & Sign-Off

**Rollback Approved By**: `[Name]` (Release Manager)
**Timestamp**: `[ISO8601]`
**Final Status**: Complete / In Progress

---

**Document Version**: 1.0
**Last Updated**: 2026-07-07
**Next Review**: 2026-08-07
