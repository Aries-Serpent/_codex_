# Archived Validation Logs

**Archive Date**: 2025-12-12  
**Commit SHA**: a0c1dfb  
**Archiver**: Copilot AI Assistant

## Purpose

This folder contains archived validation logs for external storage offloading. Archives are tracked in git and can be offloaded to external storage systems.

## Contents

This archive contains old validation run logs that were archived as part of the Phase 2 codebase cleanup.

### Archived Runs

| Run Directory | Date | Reason |
|---------------|------|--------|
| `20250910T052842Z` | 2025-09-10 05:28:42 UTC | Oldest validation run |
| `20250910T071257Z` | 2025-09-10 07:12:57 UTC | Old validation run |
| `20250910T080054Z` | 2025-09-10 08:00:54 UTC | Old validation run |

### Archive File

- `validation_logs_20250910_old_a0c1dfb.tar.gz` - Archived validation logs with commit SHA

### Retention Policy

- Last 5 validation runs are kept in `.codex/validation/`
- Older runs are archived to `misc/repo-owner-review/archived-artifacts/validation-logs/`
- Archives use `.tar.gz` format with commit SHA in filename
- Archives are tracked in git for external storage offloading

### Recovery

To restore archived validation logs:

```bash
# Extract archive
tar -xzf validation_logs_20250910_old_a0c1dfb.tar.gz -C .codex/validation/

# Verify extraction
ls .codex/validation/
```

### External Storage Offloading

These archives can be offloaded to external storage:
1. Archives are tracked in git (not ignored)
2. External storage systems can pull from this location
3. After offloading, archives may be removed from git with proper tracking

### Current Retention

After archival, these runs remain in `.codex/validation/`:

1. `20250910T113918Z` - 2025-09-10 11:39:18 UTC
2. `20250910T135035Z` - 2025-09-10 13:50:35 UTC
3. `20250910T151757Z` - 2025-09-10 15:17:57 UTC
4. `20250910T210555Z` - 2025-09-10 21:05:55 UTC
5. `20250911T161728Z` - 2025-09-11 16:17:28 UTC

---

**Related**: See `misc/repo-owner-review/RECOVERY_GUIDE.md` for general recovery procedures.
