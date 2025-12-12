# Archived Disabled Workflows

**Archive Date**: 2025-12-12  
**Commit SHA**: a0c1dfb  
**Archiver**: Copilot AI Assistant

## Purpose

This folder contains archived disabled workflows for external storage offloading. Archives are tracked in git and can be offloaded to external storage systems.

This archive contains the contents of `.codex/disabled_workflows/` which was a duplicate location for disabled workflow files.

## Consolidation

As part of Phase 2 cleanup, disabled workflows have been consolidated to a single canonical location:

**Canonical Location**: `.github/_workflows_disabled/`

The `.codex/disabled_workflows/` directory has been removed.

## Archive File

- `codex_disabled_workflows_a0c1dfb.tar.gz` - Archived disabled workflows with commit SHA

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

## External Storage Offloading

These archives can be offloaded to external storage:
1. Archives are tracked in git (not ignored)
2. External storage systems can pull from this location
3. After offloading, archives may be removed from git with proper tracking

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
