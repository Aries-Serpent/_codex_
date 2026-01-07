# Emergency Cache Cleanup Guide

**Status**: 🚨 CACHE CRISIS - 12.38 GB / 10 GB (123.8%)  
**Action Required**: IMMEDIATE cleanup  
**Target**: < 7 GB (70% capacity)

---

## Quick Start

### Option 1: Automated Cleanup (Recommended)

```bash
# Navigate to repository
cd /home/runner/work/_codex_/_codex_

# Run emergency cleanup script
./.github/scripts/emergency_cache_cleanup.sh
```

### Option 2: GitHub Actions Workflow

1. Go to Actions tab in GitHub
2. Select "Emergency Cache Cleanup" workflow
3. Click "Run workflow"
4. Select dry_run: false
5. Click "Run workflow" button

### Option 3: Manual Cleanup via gh CLI

```bash
# List all caches
gh cache list --limit 50

# Delete specific cache by ID
gh cache delete <CACHE_ID> --confirm

# Delete PR #2668 cache (4.4 GB)
gh cache list --json id,key,ref | \
  jq -r '.[] | select(.ref == "refs/pull/2668/merge") | select(.key | contains("Unified Security")) | .id' | \
  xargs -I {} gh cache delete {} --confirm
```

---

## Current Cache Analysis

### Identified Issues

| Cache Key | Size | Issue | Action |
|-----------|------|-------|--------|
| `Linux-Unified Security Suite-dependency-scan-pip-...` | 4.4 GB | PR #2668 merge ref (stale) | **DELETE** |
| `Linux-pip-python-def56e4e...` | 3.9 GB | Duplicate on main | Keep most recent |
| `setup-python-Linux-x64-24.04-Ubuntu-python-3.11.14-pip-...` | 3.8 GB | Duplicate on main | Keep most recent |
| `Linux-pip-def56e4e...` | 240 MB | Old cache | Evaluate age |
| `codeql-trap-1-2.23.8-javascript-...` | 210 MB | OK | Keep |

**Total**: 12.38 GB  
**Required Deletion**: ~5.5 GB

---

## Cleanup Strategy

### Phase 1: Delete Stale PR Caches (Target: 4.4 GB)

```bash
# Delete all caches from PR #2668 merge refs
gh cache list --json id,ref --limit 100 | \
  jq -r '.[] | select(.ref | startswith("refs/pull/")) | .id' | \
  xargs -I {} gh cache delete {} --confirm
```

### Phase 2: Remove Duplicate pip Caches (Target: ~1-2 GB)

```bash
# List pip caches by branch, sorted by date
gh cache list --json key,id,createdAt,ref --limit 100 | \
  jq -r '.[] | select(.key | startswith("Linux-pip")) | "\(.ref)\t\(.createdAt)\t\(.id)"' | \
  sort -k1,1 -k2,2r

# Delete older duplicates (manually or via script)
```

### Phase 3: Remove Old Caches (Target: variable)

```bash
# List caches older than 7 days
CUTOFF=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)
gh cache list --json id,createdAt --limit 100 | \
  jq -r --arg cutoff "$CUTOFF" '.[] | select(.createdAt < $cutoff) | .id' | \
  xargs -I {} gh cache delete {} --confirm
```

---

## Verification

### Check Current Status

```bash
# Total cache size
gh cache list --json sizeInBytes --limit 100 | \
  jq '[.[].sizeInBytes] | add / 1024 / 1024 / 1024'

# Expected output after cleanup: < 7.0 GB
```

### Monitor Cache Growth

```bash
# List caches by size
gh cache list --json key,sizeInBytes,ref --limit 20 | \
  jq -r '.[] | "\(.sizeInBytes / 1024 / 1024 | floor) MB\t\(.key[:50])\t\(.ref)"' | \
  sort -rn
```

---

## Post-Cleanup Actions

After successful cleanup to < 7 GB:

1. ✅ Verify cache status in GitHub UI
2. ✅ Update cache monitoring documentation
3. ✅ Proceed with Phase 3C-Lite implementation
4. ✅ Establish weekly cache review process

---

## Prevention Measures

### Immediate (Post-Cleanup)

1. **Implement cache size limits** in workflows:
   ```yaml
   # Add to cache steps
   if: github.event_name != 'pull_request'  # Avoid PR caches
   ```

2. **Add cache monitoring** workflow (runs weekly)

3. **Document cache policies** for contributors

### Short-term (Next Week)

1. **Convert more workflows to built-in caching** (`cache: 'pip'`)
2. **Reduce cache retention** from 7 days to 5 days (if needed)
3. **Implement automatic cleanup** for PR caches on PR close

### Long-term (Next Month)

1. **Evaluate cache ROI** for each workflow
2. **Optimize cache keys** to reduce duplication
3. **Consider GitHub Enterprise** if 10 GB limit is insufficient

---

## Emergency Contacts

If cleanup fails or issues arise:

1. **GitHub Support**: Report cache limit issue
2. **Repository Maintainers**: @mbaetiong
3. **Fallback**: Temporarily disable caching in workflows

---

## Troubleshooting

### Issue: "Cache not found" errors

**Solution**: Cache may have been auto-evicted by GitHub. This is expected behavior when over limit.

### Issue: Cleanup script fails with auth error

**Solution**:
```bash
# Re-authenticate gh CLI
gh auth login

# Verify token has actions:write permission
gh auth status
```

### Issue: Total size not decreasing

**Solution**:
- Wait 5-10 minutes for GitHub to update
- Refresh cache list: `gh cache list --limit 100`
- Check GitHub Actions UI directly

---

## Success Criteria

- ✅ Total cache size < 7 GB (70% capacity)
- ✅ No automatic evictions
- ✅ All active workflows have caches available
- ✅ Weekly monitoring in place

---

**Created**: 2024-12-30  
**Urgency**: P0 CRITICAL  
**Next Review**: After cleanup completion
