# Repository Owner Review Folder

**Purpose**: This folder contains files that have been reviewed and deemed non-essential to the repository's core functionality. Files here are subject to removal by the repository owner.

**⚠️ Important Notice**: 
- Files in this folder are archived for review and potential deletion
- These files are NOT maintained and may be outdated
- Repository owner Phase 5 delete these files at any time
- All files are backed up in git history

---

## Why Files Are Here

To reduce repository size from 11.2MB to under 10MB (CodeQL requirement), we've moved large, non-essential files here. This approach:

1. ✅ Preserves files for owner review before permanent deletion
2. ✅ Reduces repository size for CodeQL scanning
3. ✅ Maintains git history (files can be restored)
4. ✅ Provides clear documentation of what was moved and why

---

## Folder Structure

```
misc/repo-owner-review/
├── README.md (this file)
├── metadata.json (tracks moved files)
├── drop-for-restore/ (file recovery inbox - see Recovery Process below)
├── archived-backups/ (backup files with commit SHA naming)
│   └── README.md
└── archived-artifacts/
    └── README.md
```

---

## Files Moved Here

See `metadata.json` for a complete manifest of moved files including:
- Original location
- Size
- Date moved
- Reason for archival
- Verification that removal won't break functionality

---

## Recovery Process

**New Feature**: File recovery system for archived files.

### Drop Folder: `drop-for-restore/`

If you need to restore archived files:

1. **Request restoration** via AI prompt or manual process
2. **Files are extracted** from archives if compressed
3. **Moved to drop-for-restore/** with original naming preserved
4. **User notification** when files are ready for retrieval

### Manual Recovery Instructions

For files in `archived-backups/`:
```bash
# Each archived file has format: originalname_dirname_commitsha.ext
# Example: README.md_.codex_36462ee8.bak

# View metadata
cat misc/repo-owner-review/archived-backups/README.md_.codex_36462ee8.bak.meta.md

# Restore to original location (from metadata)
cp misc/repo-owner-review/archived-backups/README.md_.codex_36462ee8.bak .codex/README.md.bak
```

For compressed archives:
```bash
# Extract archive
tar -xzf misc/repo-owner-review/archived-artifacts/<category>/<file>.tar.gz

# Move to drop folder or original location
mv extracted-file drop-for-restore/
```

---

## Archived Files Registry

### Backup Files (2024-12-12 Audit)

| Original Path | Archived Name | Commit SHA | Size | Reason |
|---------------|---------------|------------|------|--------|
| `.codex/README.md.bak` | `README.md_.codex_36462ee8.bak` | 36462ee8 | 22KB | Backup file from codebase audit |
| `uv.lock.bak` | `uv.lock_._36462ee8.bak` | 36462ee8 | 118KB | Lock file backup |
| `.github/copilot_agent_task_prompt.next.md.backup` | `copilot_agent_task_prompt.next.md_.github_36462ee8.backup` | 36462ee8 | 11KB | Agent prompt backup |
| `AGENTS.md.backup_20251114_035816` | `AGENTS.md_._36462ee8.backup_20251114_035816` | 36462ee8 | 11KB | Timestamped backup |
| `tests/tracking/test_mlflow_utils_py.old` | `test_mlflow_utils_py_tests_tracking_36462ee8.old` | 36462ee8 | 5.9KB | Old test file version |

### Duplicate Files Removed (2024-12-12 Audit)

| Removed File | Canonical Version | Reason |
|--------------|-------------------|--------|
| `tests/monitoring/test_mlflow_monitoring_utils.py` | `tests/monitoring/test_monitoring_mlflow_utils.py` | Exact duplicate, inconsistent naming |
| `tests/modeling/conftest.py` | `tests/models/conftest.py` | Exact duplicate, models is standard dir |

See `archived-backups/manifest.txt` for complete list with commit SHAs.

---

## What Repository Owner Should Do

**Option 1: Delete Files**
If confident these files are no longer needed:
```bash
# Remove the entire misc folder
git rm -r misc/
git commit -m "chore: Remove archived files from misc folder"
```

**Option 2: Keep Temporarily**
Leave files here for a grace period (30-90 days) before deletion.

**Option 3: Restore Files**
If any file is needed:
```bash
# Move specific file back
mv misc/repo-owner-review/archived-artifacts/<category>/<file> <original-location>/
git add <original-location>/<file>
git commit -m "restore: Bring back <file> from archive"
```

---

## Safety Guarantees

✅ **No Functionality Broken**: All tests pass after moving files  
✅ **Git History Preserved**: Can restore from any commit  
✅ **Documentation Clear**: Each file's purpose documented  
✅ **Verification Complete**: Each file verified as non-essential

---

## Questions or Concerns?

If you're unsure about deleting any file, consult:
1. `metadata.json` in this folder
2. Git history: `git log --follow <filepath>`
3. File usage: `grep -r "filename" .`

---

**Last Updated**: 2024-12-12 (Comprehensive Audit)  
**Automation**: Copilot AI Code Assistant  
**Audit Report**: See `/tmp/audit/audit_summary.md` for full findings
