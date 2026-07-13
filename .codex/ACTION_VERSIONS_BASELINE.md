# GitHub Actions Version Baseline - Phase 5

**Document Date**: 2026-07-13  
**Last Updated**: 2026-07-13  
**Enforcement**: Via `.github/workflows/action-version-check.yml` (blocks PRs on violation)  
**Auto-Fix**: Via `.github/workflows/action-version-auto-fix.yml` (Sunday 00:00 UTC)  

---

## 📋 Version Requirements

All workflows **MUST** use these minimum action versions or later.

### Core Actions

| Action | Minimum Version | Current Latest | Last Updated | Notes |
|--------|-----------------|-----------------|--------------|-------|
| `actions/checkout` | v4 | v4 | 2026-07-13 | v5 available, compatibility assessment pending |
| `actions/setup-python` | v5 | v5 | 2026-07-13 | Upgraded from v4 for security |
| `actions/setup-node` | v4 | v4 | 2026-07-13 | v5 available for Q3 planning |
| `actions/setup-go` | v5 | v5 | 2026-07-13 | Latest stable |
| `actions/setup-java` | v4 | v4 | 2026-07-13 | Latest stable |

### Security & CodeQL Actions

| Action | Minimum Version | Current Latest | Last Updated | Notes |
|--------|-----------------|-----------------|--------------|-------|
| `github/codeql-action/init` | v3 | v3 | 2026-07-13 | **CRITICAL**: v2 deprecated (no more updates) |
| `github/codeql-action/autobuild` | v3 | v3 | 2026-07-13 | Must match init version |
| `github/codeql-action/analyze` | v3 | v3 | 2026-07-13 | Must match init version |
| `github/codeql-action/upload-sarif` | v3 | v3 | 2026-07-13 | SARIF upload reliability improved |

### Artifact & Cache Actions

| Action | Minimum Version | Current Latest | Last Updated | Notes |
|--------|-----------------|-----------------|--------------|-------|
| `actions/upload-artifact` | v4 | v4 | 2026-07-13 | Performance improved in v4 |
| `actions/download-artifact` | v4 | v4 | 2026-07-13 | Parallel download support |
| `actions/cache` | v4 | v4 | 2026-07-13 | v4 added compression support |

### Utility Actions

| Action | Minimum Version | Current Latest | Last Updated | Notes |
|--------|-----------------|-----------------|--------------|-------|
| `actions/github-script` | v7 | v7 | 2026-07-13 | v8 available, testing in progress |
| `softprops/action-gh-release` | v1 | v1 | 2026-07-13 | External, stable |
| `actions/create-release` | v1 | v1 | 2026-07-13 | Deprecated, use softprops alternative |

---

## 🔄 Update Policy

### Update Frequency

- **Security Updates**: Immediate (same day or next)
- **Breaking Changes**: Quarterly assessment (first Monday)
- **Non-Breaking Updates**: Monthly batching (first Tuesday)
- **Deprecated Versions**: Emergency update if dropped from support

### Migration Process

1. **Test on non-critical workflow** first
2. **Monitor 5 runs** for compatibility
3. **Update baseline** if no issues
4. **Auto-fix** via weekly scheduled workflow
5. **Verify compliance** via action-version-check.yml

---

## ⚠️ Known Issues & Workarounds

### Issue: actions/setup-python v5 with caching

**Problem**: Pip cache sometimes stale with v5  
**Workaround**: Add `cache-dependency-path: '**/requirements*.txt'`  
**Status**: Monitoring, no action needed

### Issue: github/codeql-action/analyze v3 timeout

**Problem**: Large codebases may timeout in 60 minutes  
**Workaround**: Use matrix strategy to split analysis  
**Status**: Being assessed for v4 upgrade

---

## 📊 Enforcement Rules

### Check Rules (fail PR if violated)

```yaml
# From enforce_actions_versions.py
REQUIRED_VERSIONS = {
    'actions/checkout': 'v4',
    'actions/setup-python': 'v5',
    'github/codeql-action/init': 'v3',
    # ... full list ...
}

# Fails if:
# - Any workflow uses version < required
# - Pinned version differs from baseline
# - v2 or later of deprecated actions used
```

### Exception Process

To use a different version:

1. **Document exception** in pull request:
   ```markdown
   ## Version Exception
   - Action: `actions/example`
   - Exception: v2 instead of v4
   - Reason: [specific reason]
   - Duration: [temporary or permanent]
   - Risk Assessment: [why it's safe]
   ```

2. **Add to exception list** (`.codex/action_version_exceptions.json`):
   ```json
   {
     "workflow": "special-case.yml",
     "action": "actions/example",
     "version": "v2",
     "approved_date": "2026-07-13",
     "expiry": "2026-09-13",
     "reason": "Compatibility with legacy system"
   }
   ```

3. **Get approval** from DevOps lead
4. **Scheduled review** before expiry

---

## 🚀 Update History

| Date | Action | Old Version | New Version | Reason |
|------|--------|-------------|-------------|--------|
| 2026-07-13 | Create baseline | N/A | v4/v5/v3 | Phase 5 launch |
| 2026-06-01 | upgrade codeql | v2 | v3 | Deprecation notice |
| 2026-05-15 | upgrade setup-python | v4 | v5 | Security update |

---

## 📋 Next Review

**Date**: 2026-08-13 (First Monday of month)  
**Focus**: Q3 action releases, v5 compatibility assessments  
**Owner**: DevOps team

---

## ✅ Compliance Checklist

Run this before marking compliance complete:

```bash
# Check all workflows meet requirements
python scripts/ci/enforce_actions_versions.py --check

# Expected output: ✅ All workflows in compliance

# If violations found:
python scripts/ci/enforce_actions_versions.py --fix
git add .github/workflows/
git commit -m "chore: update actions to version baseline"
git push
```

---

**Status**: 🟢 ENFORCED  
**Maintenance**: DevOps team  
**Escalation**: @mbaetiong
