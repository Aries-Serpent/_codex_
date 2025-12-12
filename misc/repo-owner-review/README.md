# Repository Owner Review Folder

**Purpose**: This folder contains files that have been reviewed and deemed non-essential to the repository's core functionality. Files here are subject to removal by the repository owner.

**⚠️ Important Notice**: 
- Files in this folder are archived for review and potential deletion
- These files are NOT maintained and may be outdated
- Repository owner may delete these files at any time
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
└── archived-artifacts/
    ├── security-reports/ (large generated security scan reports)
    ├── changelogs/ (historical changelogs)
    ├── old-audit-runs/ (previous audit run artifacts)
    ├── validation-logs/ (old validation logs)
    └── deprecated-scripts/ (duplicate/backup scripts)
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

**Last Updated**: 2025-12-10  
**Automation**: Copilot AI Code Assistant
