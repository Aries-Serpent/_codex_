# Repository Owner Review Folder

**Last Updated**: 2026-01-26  
**Purpose**: External storage offload, historical files, and materials requiring human review  
**QA Integration**: Maintains file organization for effective Codebase QA Walkthrough Analysis

This folder contains files that have been reviewed, archived, or offloaded from the main repository for size optimization and governance oversight. The canonical archive location is:

`.codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/`

The legacy `misc/repo-owner-review/` path remains only as a compatibility alias; the canonical repo-owned archive root is the `.codex/archive/...` location above. As of 2026-01-26, it serves dual purposes:
1. **External Storage**: Historical files offloaded to reduce repository size
2. **Human Review**: Non-essential files subject to owner review and potential removal

**⚠️ Important Notice**:
- Files in offload subdirectories are organized for QA walkthrough access
- Historical files are preserved for trend analysis and audit compliance
- Legacy archived files may be deleted by repository owner at any time
- All files are backed up in git history

---

## Why Files Are Here

**Historical Context (2025-12-12)**: Initial archival to reduce repository size for CodeQL scanning  
**Current Purpose (2026-01-26)**: External storage offload for QA walkthrough optimization

This folder now serves two primary functions:

### 1. External Storage Offload (NEW)
To optimize repository size while preserving historical data for QA analysis:
- ✅ Historical coverage reports (trend analysis)
- ✅ Historical logs (troubleshooting reference)
- ✅ CI/CD artifacts (audit compliance)
- ✅ Archive packages (legacy references)
- ✅ Temporary outputs (review/cleanup)
- ✅ Deprecated reports (migration verification)

**Benefits**:
- Reduces main repository size by ~6-8MB
- Preserves all historical data for QA walkthrough
- Maintains organized structure for analysis
- Supports audit and compliance requirements

### 2. Legacy Archival (Existing)
Original purpose to reduce repository size from 11.2MB to under 10MB:
1. ✅ Preserves files for owner review before permanent deletion
2. ✅ Reduces repository size for CodeQL scanning
3. ✅ Maintains git history (files can be restored)
4. ✅ Provides clear documentation of what was moved and why

---

## Folder Structure

```
.codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/
├── README.md (this file)
├── OFFLOAD_INDEX.md ⭐ (complete inventory of offloaded files)
├── metadata.json (tracks moved files)
├── AUDIT_REPORT_2025-12-12.md
├── FOLLOWUP_ACTIONS.md
├── MIGRATION_GUIDE.md
├── QUARTERLY_AUDIT_CHECKLIST.md
├── RECOVERY_GUIDE.md
├── drop-for-restore/ (file recovery inbox - see Recovery Process below)
├── archived-backups/ (backup files with commit SHA naming)
│   └── README.md
├── archived-artifacts/ (existing archived artifacts)
│   └── README.md
├── auto-generated-prompts/ (auto-generated prompt review)
├── pending-manual-review/ (items awaiting manual review)
├── historical-coverage/ ⭐ (offloaded coverage reports)
│   └── README.md
├── historical-logs/ ⭐ (offloaded log extracts)
│   └── README.md
├── historical-artifacts/ ⭐ (offloaded CI/CD artifacts)
│   └── README.md
├── archive-files/ ⭐ (consolidated .zip/.tar.gz files)
│   └── README.md
├── temp-outputs/ ⭐ (temporary outputs for review)
│   └── README.md
└── deprecated-reports/ ⭐ (deprecated _codex_reports/)
    └── README.md
```

**⭐ NEW (2026-01-26)**: Six offload subdirectories for external storage optimization  
**See OFFLOAD_INDEX.md** for complete file inventory and retrieval instructions

---

## External Storage Offload (NEW - 2026-01-26)

### Quick Access Guide

**📊 For Coverage Analysis**: See `historical-coverage/` + `OFFLOAD_INDEX.md`  
**📝 For Historical Logs**: See `historical-logs/` + `OFFLOAD_INDEX.md`  
**🏗️ For CI/CD Artifacts**: See `historical-artifacts/` + `OFFLOAD_INDEX.md`  
**📦 For Archive Files**: See `archive-files/` + `OFFLOAD_INDEX.md`  
**⏱️ For Temp Outputs**: See `temp-outputs/` + `OFFLOAD_INDEX.md`  
**🗂️ For Deprecated Reports**: See `deprecated-reports/` + `OFFLOAD_INDEX.md`

### QA Walkthrough Integration

The offload structure is designed to support QA walkthrough analysis:

1. **Current State**: Active files remain in main repository
2. **Historical Trends**: Offloaded files provide historical context
3. **Audit Trail**: `OFFLOAD_INDEX.md` tracks all movements
4. **Retrieval**: Each subdirectory has README with usage instructions

### Size Impact

**Estimated Repository Reduction**: ~6-8MB
- Coverage Reports: ~2.8MB offloaded
- Logs: ~1.4MB offloaded
- Artifacts: ~500KB offloaded
- Archives: ~800KB offloaded
- Temp/Output: ~280KB offloaded
- Deprecated Reports: ~120KB offloaded

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
cat .codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/archived-backups/README.md_.codex_36462ee8.bak.meta.md

# Restore to original location (from metadata)
cp .codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/archived-backups/README.md_.codex_36462ee8.bak .codex/README.md.bak
```

For compressed archives:
```bash
# Extract archive
tar -xzf .codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/archived-artifacts/<category>/<file>.tar.gz

# Move to drop folder or original location
mv extracted-file drop-for-restore/
```

---

## Archived Files Registry

### Backup Files (2025-12-12 Audit)

| Original Path | Archived Name | Commit SHA | Size | Reason |
|---------------|---------------|------------|------|--------|
| `.codex/README.md.bak` | `README.md_.codex_36462ee8.bak` | 36462ee8 | 22KB | Backup file from codebase audit |
| `uv.lock.bak` | `uv.lock_._36462ee8.bak` | 36462ee8 | 118KB | Lock file backup |
| `.github/copilot_agent_task_prompt.next.md.backup` | `copilot_agent_task_prompt.next.md_.github_36462ee8.backup` | 36462ee8 | 11KB | Agent prompt backup |
| `.codex/archive/deprecated/AGENTS.md.backup_20251114_035816` | `.codex/archive/deprecated/AGENTS.md_._36462ee8.backup_20251114_035816` | 36462ee8 | 11KB | Timestamped backup |
| `tests/tracking/test_mlflow_utils_py.old` | `test_mlflow_utils_py_tests_tracking_36462ee8.old` | 36462ee8 | 5.9KB | Old test file version |

### Duplicate Files Removed (2025-12-12 Audit)

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
Leave files here for a grace period (30-90 iterations) before deletion.

**Option 3: Restore Files**
If any file is needed:
```bash
# Move specific file back
mv .codex/archive/root-consolidation/deprecated-reports/misc/repo-owner-review/archived-artifacts/<category>/<file> <original-location>/
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

**Last Updated**: 2025-12-12 (Comprehensive Audit)  
**Automation**: Copilot AI Code Assistant  
**Audit Report**: See `/tmp/audit/audit_summary.md` for full findings
