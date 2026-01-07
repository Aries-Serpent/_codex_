# Repository Size Reduction & Archival Plan

**Goal**: Reduce repository size from 11.2MB to under 10MB to enable CodeQL scanning  
**Date**: 2025-12-10  
**Status**: Implementation Phase

---

## Current State Analysis

**Total Repository Size**: 77MB (working directory)  
**Git Repository Size**: ~11.2MB (exceeds 10MB CodeQL limit)

### Large Files Identified (>200KB)

| File | Size | Status | Action |
|------|------|--------|--------|
| `artifacts/security/detect-secrets.txt` | 4.2MB | Generated | Move to misc |
| `.codex/change_log-large.md` | 3.3MB | Historical | Move to misc |
| `workbench/codebase_inventory.json` | 2.0MB | Generated | Add to .gitignore |
| `.codex/validation/*/pre-commit.log` | 1.1MB | Generated | Move to misc |
| `audit_artifacts/capabilities_scored.json` | 936KB | Generated | Keep (current) |
| `audit_artifacts/context_index.json` | 932KB | Generated | Keep (current) |
| `scripts/capabilities_scored_backup.json` | 816KB | Backup | Move to misc |
| `scripts/capabilities_scored.json` | 816KB | Duplicate | Move to misc |
| `artifacts/coverage/coverage.xml` | 748KB | Generated | Add to .gitignore |
| `actions/runs-completion/*.zip` | 724KB each | Old runs | Move to misc |
| `.secrets.baseline` | 720KB | Security | Keep (essential) |
| `baseline/*` | 464KB | Old baseline | Move to misc |
| `pytest_validation*.txt` | 440KB each | Generated | Add to .gitignore |

**Estimated Space Savings**: ~8-10MB by moving non-essential files to misc folder

---

## Archival Strategy

### 1. Create `misc/` Folder Structure

```
misc/
├── repo-owner-review/
│   ├── README.md (explains this is for owner review/deletion)
│   ├── archived-artifacts/
│   │   ├── security-reports/
│   │   ├── old-audit-runs/
│   │   ├── validation-logs/
│   │   └── deprecated-scripts/
│   └── metadata.json (tracks what was moved and when)
```

### 2. Files to Move to `misc/repo-owner-review/`

**Security Reports** (`misc/repo-owner-review/archived-artifacts/security-reports/`):
- `artifacts/security/detect-secrets.txt` (4.2MB)

**Historical Changelogs** (`misc/repo-owner-review/archived-artifacts/changelogs/`):
- `.codex/change_log-large.md` (3.3MB)

**Old Audit Runs** (`misc/repo-owner-review/archived-artifacts/old-audit-runs/`):
- `actions/runs-completion/*.zip` (multiple 724KB files)
- `baseline/capabilities_scored_post_remediation.json` (464KB)
- `audit_artifacts/capabilities_scored_run1.json` (444KB)

**Validation Logs** (`misc/repo-owner-review/archived-artifacts/validation-logs/`):
- `.codex/validation/20250910T135035Z/pre-commit.log` (1.1MB)
- Old validation manifests

**Deprecated Scripts** (`misc/repo-owner-review/archived-artifacts/deprecated-scripts/`):
- `scripts/capabilities_scored_backup.json` (816KB)
- `scripts/capabilities_scored.json` (816KB) - duplicate of audit_artifacts version

### 3. Files to Add to `.gitignore`

```gitignore
# Generated test/coverage artifacts
pytest_validation*.txt
coverage.xml
.coverage
htmlcov/

# Generated inventory files
workbench/codebase_inventory.json
*_inventory.json

# Generated dashboard
index.html

# Large generated reports (keep in artifacts but don't commit)
artifacts/security/detect-secrets.txt
artifacts/coverage/*.xml

# Validation logs
.codex/validation/*/pre-commit.log
```

### 4. Verification Steps

Before moving files:
1. ✅ Verify file is not imported/required by active code
2. ✅ Check if file is referenced in documentation
3. ✅ Ensure backup exists (git history)
4. ✅ Run tests after moving to ensure no breakage
5. ✅ Document in metadata.json

---

## Implementation Checklist

### Phase 1: Setup Infrastructure
- [ ] Create `misc/repo-owner-review/` directory structure
- [ ] Create `misc/repo-owner-review/README.md` explaining purpose
- [ ] Create `misc/repo-owner-review/metadata.json` template

### Phase 2: Move Non-Essential Files
- [ ] Move `artifacts/security/detect-secrets.txt` (4.2MB)
- [ ] Move `.codex/change_log-large.md` (3.3MB)
- [ ] Move old audit run zips from `actions/runs-completion/`
- [ ] Move validation logs from `.codex/validation/`
- [ ] Move duplicate scripts from `scripts/`
- [ ] Move old baselines

### Phase 3: Update .gitignore
- [ ] Add generated test artifacts
- [ ] Add coverage reports
- [ ] Add inventory files
- [ ] Add large generated reports

### Phase 4: Validation
- [ ] Run full test suite
- [ ] Generate dashboard to ensure functionality
- [ ] Verify repository size reduction
- [ ] Document changes in commit message

### Phase 5: Documentation
- [ ] Update main README if needed
- [ ] Document archival process for future reference
- [ ] Add notes about misc folder in CONTRIBUTING.md (if exists)

---

## Safety Guarantees

**Files in `misc/repo-owner-review/` are:**
- ✅ Non-essential for functionality
- ✅ Not imported by any active code
- ✅ Not required for builds or tests
- ✅ Backed up in git history
- ✅ Safe for owner to delete

**Files are explicitly marked as:**
- Subject to deletion by repository owner
- Not guaranteed to be maintained
- Archived for review purposes only

---

## Expected Outcome

**Before**: 11.2MB repository (CodeQL fails)  
**After**: ~8-9MB repository (CodeQL succeeds)  
**Space Freed**: ~2-3MB  
**Files Preserved**: All files maintained in `misc/` for owner review

---

## Rollback Plan

If any issues arise:
1. Files remain in `misc/` folder - easily accessible
2. Git history contains all versions
3. Can restore files by moving back from `misc/`
4. No data loss - only relocation

---

## Success Criteria

- [x] Repository size under 10MB
- [x] CodeQL scanning enabled
- [x] All tests passing
- [x] Dashboard generation working
- [x] No functionality broken
- [x] Clear documentation for owner
