# Archived Old Audit Runs

**Archive Date**: 2025-12-12  
**Commit SHA**: 4d9198c  
**Archiver**: Copilot AI Assistant

## Purpose

This folder contains archived old audit run data for external storage offloading. Archives are tracked in git and can be offloaded to external storage systems.

## Archive Contents

| Archive File | Original Location | Description | Size | Verified Safe |
|--------------|------------------|-------------|------|---------------|
| `codex_reports_2025-10-06_4d9198c.tar.gz` | `_codex_reports/2025-10-06/` | Old audit reports from October 2025 | ~100KB | ✅ No active references |
| `pytest_validation_4d9198c.tar.gz` | `pytest_validation*.txt` | Pytest validation output files | ~140KB | ✅ No active references |
| `workbench_inventory_4d9198c.tar.gz` | `workbench/codebase_inventory.json` | Large codebase inventory (gitignored) | ~220KB | ✅ Gitignored file |

## Verification

Before archiving, each file was checked for:
- Active references in Python, YAML, and shell scripts
- Usage in CI/CD workflows
- Dependencies from other tools

Files with active references were NOT archived.

## External Storage Offloading

These archives can be offloaded to external storage:
1. Archives are tracked in git (not ignored)
2. External storage systems can pull from this location
3. After offloading, archives may be removed from git with proper tracking

## Recovery

To restore archived files:

```bash
# Extract codex reports
tar -xzf codex_reports_2025-10-06_4d9198c.tar.gz -C /

# Extract pytest validation
tar -xzf pytest_validation_4d9198c.tar.gz -C /

# Extract workbench inventory (note: file is gitignored)
tar -xzf workbench_inventory_4d9198c.tar.gz -C /
```

---

**Related**: See `misc/repo-owner-review/RECOVERY_GUIDE.md` for general recovery procedures.
