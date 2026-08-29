# Repository Owner Review Archive

**Archive Created**: 2025-12-29  
**Archive File**: `repo-owner-review-archive.tar.gz`  
**Original Size**: ~2.4MB  
**Compressed Size**: 67KB  
**Compression Ratio**: ~97.2% (35x reduction)

---

## 📦 Archive Contents

This archive contains all files from `misc/repo-owner-review/` that are pending repository owner review before permanent deletion.

### Included Directories

1. **auto-generated-prompts/** (21 files + README)
   - 21 restored follow-up prompt files
   - Comprehensive documentation
   - Archive notices on all files

2. **archived-artifacts/**
   - Historical security reports
   - Deprecated scripts
   - Old audit runs

3. **archived-backups/**
   - Historical backups

4. **pending-manual-review/**
   - Broken references documentation
   - Deleted files records

5. **Root Documentation**
   - README.md
   - metadata.json
   - MIGRATION_GUIDE.md
   - AUDIT_REPORT_2025-12-12.md
   - FOLLOWUP_ACTIONS.md
   - QUARTERLY_AUDIT_CHECKLIST.md
   - RECOVERY_GUIDE.md

---

## 📥 Extraction Instructions

### Quick Extraction

```bash
# Extract to current directory
tar -xzf repo-owner-review-archive.tar.gz

# Extract to specific location
tar -xzf repo-owner-review-archive.tar.gz -C /path/to/destination/

# List contents without extracting
tar -tzf repo-owner-review-archive.tar.gz | less
```

### Verify Archive Integrity

```bash
# Test archive integrity
tar -tzf repo-owner-review-archive.tar.gz > /dev/null && echo "✓ Archive OK" || echo "✗ Archive corrupted"

# Calculate checksum
sha256sum repo-owner-review-archive.tar.gz
```

**Expected SHA256**: `10e3627e69303f9956f46dc49370e4f1aa134768f0bb2d6a2faea89201ae5166`

---

## 🔐 Archive Verification

### Checksum
```bash
# Generate checksum
sha256sum repo-owner-review-archive.tar.gz > repo-owner-review-archive.tar.gz.sha256

# Verify later
sha256sum -c repo-owner-review-archive.tar.gz.sha256
```

### File Count Verification
```bash
# Expected file count: 23+ files (21 PR files + README + other docs)
tar -tzf repo-owner-review-archive.tar.gz | wc -l
```

---

## 📋 Repository Management Workflow

### Step 1: Download Archive (LOCAL ACTION)
```bash
# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_/misc

# Copy archive to safe location
cp repo-owner-review-archive.tar.gz ~/backups/codex-archive-$(date +%Y%m%d).tar.gz
```

### Step 2: Verify Archive Integrity (LOCAL ACTION)
```bash
# Test extraction in temporary location
mkdir /tmp/archive-test
tar -xzf ~/backups/codex-archive-*.tar.gz -C /tmp/archive-test
ls -la /tmp/archive-test/repo-owner-review/
rm -rf /tmp/archive-test  # Clean up test
```

### Step 3: Empty Repository Directory (AFTER VERIFICATION)

**⚠️ WARNING**: Only proceed after confirming archive is safely stored locally!

```bash
# In repository
cd /home/runner/work/_codex_/_codex_

# Option A: Delete uncompressed files, keep archive
find misc/repo-owner-review -type f ! -name "*.tar.gz" ! -name "*.sha256" -delete
find misc/repo-owner-review -type d -empty -delete

# Option B: Keep only archive and README
cd misc
mv repo-owner-review-archive.tar.gz ../
mv ARCHIVE_README.md ../
rm -rf repo-owner-review/
mkdir -p repo-owner-review
mv ../repo-owner-review-archive.tar.gz repo-owner-review/
mv ../ARCHIVE_README.md repo-owner-review/

# Commit changes
git add misc/repo-owner-review
git commit -m "Archive repo-owner-review contents for offloading"
git push
```

### Step 4: Future Access (AS NEEDED)
```bash
# Extract from local backup when needed
cd ~/backups
tar -xzf codex-archive-20251229.tar.gz
cd repo-owner-review/auto-generated-prompts
# Review files as needed
```

---

## 🗑️ Permanent Deletion Decision Tree

### Decision 1: Can These Files Be Deleted?

**YES - Safe to Delete**:
- [x] All content backed up in archive
- [x] Archive verified and stored safely
- [x] No active dependencies on these files
- [x] Historical value preserved in git history
- [x] Repository owner has reviewed and approved

**NO - Keep for Now**:
- [ ] Haven't downloaded archive yet
- [ ] Archive integrity not verified
- [ ] Need to reference files regularly
- [ ] Uncertain about dependencies

### Decision 2: What to Keep?

**Recommended Minimal Retention**:
```
misc/repo-owner-review/
├── repo-owner-review-archive.tar.gz  ← Keep (67KB)
├── repo-owner-review-archive.tar.gz.sha256  ← Keep (checksum)
└── ARCHIVE_README.md  ← Keep (this file)
```

**Space Saved**: ~2.4MB → ~67KB = **~2.33MB freed**

---

## 📊 Archive Statistics

| Metric | Value |
|--------|-------|
| Files Archived | 50+ files |
| Original Size | ~2.4MB |
| Compressed Size | 67KB |
| Compression Ratio | 97.2% (35:1) |
| Auto-generated Prompts | 21 files |
| Documentation Files | 8 files |
| Artifact Archives | Multiple |

---

## 🔄 Recovery Process

If you need to restore files:

### From Archive (Recommended)
```bash
# Extract specific file
tar -xzf repo-owner-review-archive.tar.gz repo-owner-review/auto-generated-prompts/PR-2635-followup.md

# Extract specific directory
tar -xzf repo-owner-review-archive.tar.gz repo-owner-review/auto-generated-prompts/
```

### From Git History (Alternative)
```bash
# Find commit where file existed
git log --all --full-history -- "misc/repo-owner-review/auto-generated-prompts/PR-2635-followup.md"

# Restore from specific commit
git checkout <commit-hash> -- misc/repo-owner-review/auto-generated-prompts/PR-2635-followup.md
```

---

## 📝 Maintenance Notes

### When to Create New Archive
- When adding significant new content to `misc/repo-owner-review/`
- Before major repository cleanup operations
- As part of quarterly maintenance (see `QUARTERLY_AUDIT_CHECKLIST.md`)

### Archive Naming Convention
```
repo-owner-review-archive-YYYYMMDD.tar.gz
```

### Long-term Storage Recommendations
1. **Local Backup**: Store on development machine
2. **Cloud Backup**: Upload to personal cloud storage (Dropbox, Google Drive, etc.)
3. **External Drive**: Copy to external backup drive
4. **Documentation**: Keep this README with the archive

---

## 🆘 Troubleshooting

### Archive Won't Extract
```bash
# Check file is complete
ls -lh repo-owner-review-archive.tar.gz

# Try different extraction method
gzip -d < repo-owner-review-archive.tar.gz | tar -xv

# Check for corruption
gzip -t repo-owner-review-archive.tar.gz
```

### Need Specific File Quickly
```bash
# Extract just one file
tar -xzf repo-owner-review-archive.tar.gz --strip-components=2 \
    repo-owner-review/auto-generated-prompts/PR-2635-followup.md
```

### Archive Appears Corrupted
1. **Re-download** from GitHub if still available
2. **Restore from git history** (files committed before archival)
3. **Check local backups** if you made copies

---

## 📚 Related Documentation

- **Temporary Files Policy**: `.github/TEMPORARY_FILES_POLICY.md`
- **File Removal Policy**: `misc/repo-owner-review/README.md` (in archive)
- **Archive Guide**: `docs/guides/codex_archive_runbook.md`
- **Migration Guide**: `misc/repo-owner-review/MIGRATION_GUIDE.md` (in archive)

---

**Archive Maintainer**: Repository Automation  
**Last Updated**: 2025-12-29  
**Next Review**: Quarterly (Phase 1 (Current Cycle))
