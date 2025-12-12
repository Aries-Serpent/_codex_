# Archived CI Run Artifacts

**Archive Date**: 2025-12-12  
**Commit SHA**: 4d9198c  
**Archiver**: Copilot AI Assistant

## Purpose

This folder contains archived CI workflow run artifacts for external storage offloading. Archives are tracked in git and can be offloaded to external storage systems.

## Archive Contents

| Archive File | Original Location | Description | Size |
|--------------|------------------|-------------|------|
| `determinism_audits_4d9198c.tar.gz` | `actions/runs-completion/*.zip` | Determinism audit run artifacts | ~2.2MB |

## Contents of Determinism Audits

The archive contains the following CI run artifacts:
- `bandit-report.zip` - Security scan report
- `determinism-audit-13.zip` - Determinism audit run #13
- `determinism-audit-24.zip` - Determinism audit run #24
- `determinism-audit-32.zip` - Determinism audit run #32
- `pip-audit-report.zip` - Dependency audit report

## External Storage Offloading

These archives can be offloaded to external storage:
1. Archives are tracked in git (not ignored)
2. External storage systems can pull from this location
3. After offloading, archives may be removed from git with proper tracking

## Recovery

To restore archived CI artifacts:

```bash
# Extract CI run artifacts
tar -xzf determinism_audits_4d9198c.tar.gz -C /

# Files will be restored to actions/runs-completion/
```

---

**Related**: See `misc/repo-owner-review/RECOVERY_GUIDE.md` for general recovery procedures.
