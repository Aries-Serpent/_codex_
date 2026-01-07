# Archival System Documentation

## Overview

The `misc/repo-owner-review` folder structure serves as a "codebase graveyard" for files that have been reviewed and deemed non-essential to the repository's core functionality. This system provides a safe way to reduce repository size while preserving files for owner review before permanent deletion.

## Folder Structure

```
misc/repo-owner-review/
├── README.md                    # Main documentation (what you're reading)
├── metadata.json                # Complete manifest of archived files
└── archived-artifacts/
    ├── security-reports/        # Large generated security scan reports
    ├── changelogs/             # Historical changelogs
    ├── old-audit-runs/         # Previous audit run artifacts
    ├── validation-logs/        # Old validation logs
    ├── deprecated-scripts/     # Duplicate/backup scripts
    └── historical-docs/        # Historical status/report documents
```

## Purpose

1. **Reduce repository size** - Move large, non-essential files out of active codebase
2. **Preserve for review** - Keep files accessible for repo owner verification
3. **Maintain git history** - Files remain in version control
4. **Document decisions** - Clear metadata about why each file was archived
5. **Verify safety** - Automated checks ensure no functionality breaks

## Safety Guarantees

✅ **No Functionality Broken**: All tests pass after moving files  
✅ **Git History Preserved**: Can restore from any commit  
✅ **Documentation Clear**: Each file's purpose documented in metadata.json  
✅ **Verification Complete**: Each file verified as non-essential  
✅ **Automated Checks**: Scripts verify no critical dependencies

## Using the Archival System

### Archive Files

```bash
# Preview what would be archived (dry-run)
python scripts/archive_files.py --dry-run

# Execute archival
python scripts/archive_files.py
```

### Review Archived Files

```bash
# View metadata about all archived files
cat misc/repo-owner-review/metadata.json

# List archived files by category
ls -lh misc/repo-owner-review/archived-artifacts/*/

# View specific archived file
cat misc/repo-owner-review/archived-artifacts/historical-docs/FILENAME.md
```

### Restore Files (if needed)

```bash
# Move specific file back to original location
mv misc/repo-owner-review/archived-artifacts/<category>/<file> <original-location>/
git add <original-location>/<file>
git commit -m "restore: Bring back <file> from archive"
```

### Delete Archive (when ready)

```bash
# Remove the entire misc folder
git rm -r misc/
git commit -m "chore: Remove archived files from misc folder"
```

## Archival Criteria

Files are archived when they meet these criteria:

1. **Historical/Obsolete** - Information preserved elsewhere (git history, PRs, commits)
2. **Duplicate** - Backup or copy of files that exist in active locations
3. **Generated** - Can be regenerated on demand (security reports, coverage files)
4. **Large** - Significant size but low reference value
5. **Safe** - Verified to not break any functionality when removed

## Metadata Schema

Each archived file has metadata including:

```json
{
  "original_path": "path/to/original/file",
  "archived_path": "misc/repo-owner-review/archived-artifacts/category/file",
  "size": "4.3KB",
  "size_bytes": 4364,
  "sha256": "hash...",
  "date_moved": "2025-12-11",
  "reason": "Why file was archived",
  "safe_to_delete": true,
  "verification": "How safety was verified"
}
```

## Verification Process

Before archiving, files are checked for:

1. **Code references** - Grep search for imports or usage
2. **Critical files** - Check against required config files list
3. **Build dependencies** - Ensure not required for builds/tests
4. **Documentation** - Verify information preserved elsewhere

## Compression

Large files can be compressed during archival:

- Text files: gzip compression
- Binary files: Kept as-is or skipped
- Already compressed: No additional compression

## AI Assistant Integration

This archival system is designed to be:

- **Queryable** - Structured metadata.json for programmatic access
- **Documented** - Clear reasoning for each archival decision
- **Reversible** - Easy restoration process
- **Safe** - Automated verification prevents breakage

## Questions or Concerns?

If unsure about deleting any file:

1. Check `metadata.json` for reasoning and verification
2. Review git history: `git log --follow <filepath>`
3. Search for usage: `grep -r "filename" .`
4. Run tests after removal: `pytest` or `nox -s tests`

## Maintenance

The archival system is maintained by:

- **Automation**: Copilot AI Code Assistant
- **Scripts**: `scripts/archive_files.py`
- **Monitoring**: CI/CD checks for repository size

**Last Updated**: 2025-12-11
