# Archived Disabled Workflows

**Archive Date**: 2025-12-12  
**Commit SHA**: a0c1dfb  
**Archiver**: Copilot AI Assistant

## Purpose

This archive contains the contents of `.codex/disabled_workflows/` which was a duplicate location for disabled workflow files.

## Consolidation

As part of Phase 2 cleanup, disabled workflows have been consolidated to a single canonical location:

**Canonical Location**: `.github/_workflows_disabled/`

The `.codex/disabled_workflows/` directory has been removed.

## Archive Contents

| File | Description |
|------|-------------|
| `README.md` | Directory documentation |
| `_policy.yml` | Policy workflow |
| `lint.yml` | Linting workflow |
| `manual_ci.yml` | Manual CI trigger workflow |
| `nightly.yml.disabled` | Nightly build workflow |
| `release-upload.yml` | Release upload workflow |
| `vuln_scan.yml.disabled` | Vulnerability scanning workflow |

## Recovery

To restore archived disabled workflows:

```bash
# Extract archive
tar -xzf codex_disabled_workflows_a0c1dfb.tar.gz

# Files will be extracted to .codex/disabled_workflows/
```

## Note

All files in this archive are duplicates of files in `.github/_workflows_disabled/`. The canonical location should be used for any future disabled workflow storage.

---

**Related**: 
- `.github/_workflows_disabled/` - Canonical disabled workflows location
- `misc/repo-owner-review/RECOVERY_GUIDE.md` - General recovery procedures
