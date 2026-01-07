# Manual Cache Cleanup Commands

**Context**: Emergency cleanup requires GitHub CLI authentication  
**Status**: Script created but needs to be run with proper credentials  
**Target**: Reduce 12.38 GB → < 7 GB

---

## Prerequisites

Ensure you have GitHub CLI installed and authenticated:

```bash
# Check if gh is installed
gh --version

# Authenticate (if needed)
gh auth login

# Verify authentication
gh auth status

# Set repository context
cd /home/runner/work/_codex_/_codex_
```

---

## Option 1: Run the Automated Script (Recommended)

Once authenticated:

```bash
cd /home/runner/work/_codex_/_codex_
./.github/scripts/emergency_cache_cleanup.sh
```

---

## Option 2: Manual Step-by-Step Cleanup

If the script doesn't work, execute these commands manually:

### Step 1: List All Caches

```bash
gh cache list --repo Aries-Serpent/_codex_ --json key,id,sizeInBytes,createdAt,ref,lastAccessedAt --limit 50 > cache_list.json

# View summary
jq -r '.[] | "\(.sizeInBytes / 1024 / 1024 | floor) MB\t\(.key[:60])\t\(.ref)"' cache_list.json | sort -rn | head -20
```

### Step 2: Delete PR #2668 Cache (4.4 GB)

```bash
# Find the cache ID
jq -r '.[] | select(.ref == "refs/pull/2668/merge") | select(.key | contains("Unified Security Suite")) | .id' cache_list.json

# Delete it (replace CACHE_ID with actual ID)
gh cache delete CACHE_ID --repo Aries-Serpent/_codex_ --confirm
```

**Automated version**:
```bash
jq -r '.[] | select(.ref == "refs/pull/2668/merge") | select(.key | contains("Unified Security Suite")) | .id' cache_list.json | \
  xargs -I {} gh cache delete {} --repo Aries-Serpent/_codex_ --confirm
```

### Step 3: Delete Duplicate pip Caches

```bash
# List pip caches by branch, sorted by date
jq -r '.[] | select(.key | startswith("Linux-pip")) | "\(.ref)\t\(.createdAt)\t\(.id)"' cache_list.json | \
  sort -k1,1 -k2,2r

# Identify duplicates (keep most recent per branch)
jq -r '.[] | select(.key | startswith("Linux-pip")) | "\(.ref)\t\(.createdAt)\t\(.id)"' cache_list.json | \
  sort -k1,1 -k2,2r | \
  awk '{
    if (seen[$1]++ > 0) {
      print $3
    }
  }' > duplicate_cache_ids.txt

# Delete duplicates
while IFS= read -r CACHE_ID; do
  echo "Deleting cache ID: $CACHE_ID"
  gh cache delete "$CACHE_ID" --repo Aries-Serpent/_codex_ --confirm || echo "  ⚠️  Already deleted"
done < duplicate_cache_ids.txt
```

### Step 4: Delete Old Caches (older than 7 days)

```bash
# Calculate cutoff date (7 days ago)
CUTOFF=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-7d +%Y-%m-%dT%H:%M:%SZ)

# Find old caches
jq -r --arg cutoff "$CUTOFF" '.[] | select(.createdAt < $cutoff) | .id' cache_list.json > old_cache_ids.txt

# Delete old caches
while IFS= read -r CACHE_ID; do
  echo "Deleting old cache ID: $CACHE_ID"
  gh cache delete "$CACHE_ID" --repo Aries-Serpent/_codex_ --confirm || echo "  ⚠️  Already deleted"
done < old_cache_ids.txt
```

### Step 5: Verify Results

```bash
# Wait for GitHub to update
sleep 5

# Check new total size
gh cache list --repo Aries-Serpent/_codex_ --json sizeInBytes --limit 50 | \
  jq '[.[].sizeInBytes] | add / 1024 / 1024 / 1024'

# Expected output: < 7.0 (GB)
```

---

## Option 3: Use GitHub Actions Workflow

1. Navigate to: https://github.com/Aries-Serpent/_codex_/actions/workflows/cache-cleanup.yml
2. Click "Run workflow"
3. Select branch: `copilot/sub-pr-2668` (or `main` after merge)
4. Set `dry_run`: `false`
5. Click "Run workflow" button
6. Monitor the job output

---

## Option 4: Manual Deletion via GitHub UI

1. Go to: https://github.com/Aries-Serpent/_codex_/actions/caches
2. Find each large cache (PR #2668, duplicates)
3. Click the three dots menu (⋮)
4. Select "Delete"
5. Confirm deletion

**Priority Order**:
1. Delete `Linux-Unified Security Suite-dependency-scan-pip-...` (4.4 GB) - PR #2668
2. Delete older `Linux-pip-python-...` (3.9 GB if duplicate)
3. Delete older `setup-python-Linux-x64-...` (3.8 GB if duplicate)

---

## Verification Commands

### Check Total Cache Size

```bash
# Get total in GB
gh cache list --repo Aries-Serpent/_codex_ --json sizeInBytes --limit 100 | \
  jq '[.[].sizeInBytes] | add / 1024 / 1024 / 1024'
```

### List Remaining Caches

```bash
# Top 10 by size
gh cache list --repo Aries-Serpent/_codex_ --json key,sizeInBytes,ref --limit 20 | \
  jq -r '.[] | "\(.sizeInBytes / 1024 / 1024 | floor) MB\t\(.key[:50])\t\(.ref)"' | \
  sort -rn | head -10
```

### Check if Under Limit

```bash
TOTAL_GB=$(gh cache list --repo Aries-Serpent/_codex_ --json sizeInBytes --limit 100 | \
  jq '[.[].sizeInBytes] | add / 1024 / 1024 / 1024')

echo "Current cache size: ${TOTAL_GB} GB"

if (( $(echo "$TOTAL_GB < 7.0" | bc -l) )); then
  echo "✅ SUCCESS: Under 7 GB target"
else
  echo "⚠️  WARNING: Still over 7 GB, additional cleanup needed"
fi
```

---

## Troubleshooting

### Error: "Not authenticated"

```bash
# Re-authenticate
gh auth login

# Use token if available
gh auth login --with-token < token.txt
```

### Error: "Cache not found"

- Cache may have been automatically evicted by GitHub
- This is expected when over the 10 GB limit
- Continue with other caches

### Error: "403 Forbidden"

- Verify you have `actions:write` permission
- Check token scopes: `gh auth status`
- may need to use a personal access token with correct scopes

---

## Success Criteria

After cleanup, verify:

- [ ] Total cache size < 7 GB (70% capacity)
- [ ] No caches from closed PRs (especially PR #2668)
- [ ] Only one pip cache per branch (most recent)
- [ ] No caches older than 7 days
- [ ] All active workflows still functional

---

## Next Steps After Successful Cleanup

1. **Verify in GitHub UI**: https://github.com/Aries-Serpent/_codex_/actions/caches
2. **Commit session summary** (already created)
3. **Proceed with Phase 3C-Lite** implementation
4. **Set up weekly monitoring**

---

## Emergency Contact

If cleanup fails or you need assistance:

- **Repository**: https://github.com/Aries-Serpent/_codex_
- **Documentation**: `.github/EMERGENCY_CACHE_CLEANUP_GUIDE.md`
- **Workflow**: `.github/workflows/cache-cleanup.yml`

---

**Last Updated**: 2024-12-30  
**Required Action**: Execute one of the 4 options above with proper authentication
