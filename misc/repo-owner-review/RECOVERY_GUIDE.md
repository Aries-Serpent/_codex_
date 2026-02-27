# File Recovery Guide

**Last Updated**: 2025-12-12  
**Purpose**: Instructions for recovering archived files from this folder

---

## Quick Recovery

### For Backup Files (in `archived-backups/`)

Each file has three components:
1. **Archived file**: The actual file content
2. **Metadata file** (`.meta.md`): Recovery instructions and context
3. **Manifest entry** (`manifest.txt`): Quick reference list

**Example Recovery**:
```bash
# 1. Read the metadata to find original path
cat archived-backups/README.md_.codex_36462ee8.bak.meta.md

# 2. Copy to original location
cp archived-backups/README.md_.codex_36462ee8.bak .codex/README.md.bak

# 3. Verify
git status
```

---

## Using the Drop Folder

The `drop-for-restore/` folder is an inbox for AI-assisted recovery:

### Automated Recovery Process

1. **User requests**: "Please restore the archived README backup"
2. **AI extracts/copies**: File is moved to `drop-for-restore/`
3. **User retrieves**: Files ready for manual placement or external storage

### Manual Drop Process

```bash
# Place file in drop folder
mv path/to/external/file drop-for-restore/

# AI will detect and process on next request
# Or manually move to final destination
```

---

## Recovery by Category

### Backup Files
Location: `archived-backups/`  
Naming: `{originalname}_{dirname}_{commit_sha}.{ext}`  
Recovery: Copy directly to original path from metadata

### Large Archives
Location: `archived-artifacts/*/`  
Format: may be compressed (`.tar.gz`, `.zip`)  
Recovery: Extract first, then move

```bash
# For compressed archives
tar -xzf archived-artifacts/security-reports/large-report.tar.gz -C drop-for-restore/
```

---

## Commit SHA Reference

Each archived file includes the commit SHA from its last modification.  
Use this to view historical context:

```bash
# View file at specific commit
git show <commit_sha>:path/to/original/file

# View commit details
git log <commit_sha> -1 --stat

# Restore from git history (alternative method)
git checkout <commit_sha> -- path/to/original/file
```

---

## Emergency Full Restore

If you need to restore all archived files:

```bash
#!/bin/bash
# restore_all.sh - Restore all archived backups with error handling

set -e  # Exit on error

cd misc/repo-owner-review/archived-backups

# Verify manifest exists
if [ ! -f "manifest.txt" ]; then
    echo "ERROR: manifest.txt not found"
    exit 1
fi

# Read manifest and restore each file
while IFS=$'\t' read -r original archived commit; do
    if [ ! -f "$archived" ]; then
        echo "WARNING: Archived file not found: $archived"
        continue
    fi

    # Extract original path from metadata
    if [ ! -f "${archived}.meta.md" ]; then
        echo "WARNING: Metadata missing for $archived"
        continue
    fi

    orig_path=$(grep "Original Path:" "${archived}.meta.md" | cut -d'`' -f2)

    if [ -z "$orig_path" ]; then
        echo "WARNING: Could not extract original path for $archived"
        continue
    fi

    # Check if target already exists
    if [ -f "../../../$orig_path" ]; then
        echo "WARNING: Target already exists, skipping: $orig_path"
        continue
    fi

    # Create directory if needed
    target_dir=$(dirname "../../../$orig_path")
    if ! mkdir -p "$target_dir" 2>/dev/null; then
        echo "ERROR: Cannot create directory: $target_dir"
        continue
    fi

    # Copy file
    if cp "$archived" "../../../$orig_path"; then
        echo "✓ Restored: $orig_path"
    else
        echo "ERROR: Failed to restore: $orig_path"
    fi
done < manifest.txt

echo ""
echo "Restore complete. Run 'git status' to review changes."
```

---

## Verification After Recovery

Always verify after restoring files:

```bash
# Check git status
git status

# View differences
git diff path/to/restored/file

# Run tests if applicable
pytest tests/

# Lint if applicable
ruff check .
```

---

## Support

**Questions?**
1. Check the metadata file for each archived file (`.meta.md`)
2. Review `metadata.json` for artifact archives
3. View git history: `git log --follow path/to/file`
4. Consult `README.md` in this folder

**Need Help?**
Tag @copilot with specific file names and your use case.

---

## Safety Notes

⚠️ **Before Restoring**:
- Check if file conflicts with current codebase
- Review why file was archived (see metadata)
- Ensure restoration won't break builds/tests
- Consider if you actually need the file

✅ **After Restoring**:
- Run tests to verify no breakage
- Update documentation if needed
- Remove from archive if restoration is permanent
- Commit changes with clear message

---

**Archive Format Version**: 1.0  
**Compatible With**: Git 2.x+, Linux/macOS/WSL
