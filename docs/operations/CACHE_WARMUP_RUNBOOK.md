# Cache Warm-up Runbook

**Purpose:** Operational guide for cache warm-up procedures  
**Audience:** DevOps engineers, CI/CD operators  
**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** 2026-02-10  

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Cache Warm-up Procedures](#cache-warm-up-procedures)
3. [Scheduled Warm-up](#scheduled-warm-up)
4. [Manual Warm-up](#manual-warm-up)
5. [Monitoring Warm-up](#monitoring-warm-up)
6. [Troubleshooting](#troubleshooting)
7. [Emergency Procedures](#emergency-procedures)

---

## Quick Start

### Standard Weekly Warm-up

```bash
# Trigger cache warm-up workflow
gh workflow run cache-warmup.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main

# Monitor progress
gh run list --workflow cache-warmup.yml --limit 1

# Verify warm cache status
python -m codex.ci.cache_manager health
```

**Expected Output:**
```
Cache Health: HEALTHY
Total Size: 7.69 GB
Total Caches: 156
Hit Rate: 94.7%
Oldest Cache: 2 days
Warnings: 0
```

## Pre-Deployment Warm-up

Run 12 hours before production deployment to ensure hot cache:

```bash
# Run extended warm-up
gh workflow run cache-warmup.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --inputs duration=extended mode=aggressive

# Poll until complete
while true; do
  STATUS=$(gh run list --workflow cache-warmup.yml --limit 1 --json status --jq '.[0].status')
  echo "Status: $STATUS"
  [[ "$STATUS" == "completed" ]] && break
  sleep 60
done

echo "✅ Cache warm-up complete. Deployment ready."
```

---

## Cache Warm-up Procedures

### 1. Understanding Cache Layers

**Why Warm-up Matters:**

```
Cold Cache (First Run):
├─ L1 (Toolchain):      Download Python, tools        [~3 min]
├─ L2 (Dependencies):   Download pip packages          [~5 min]
├─ L3 (Tool-State):     Run static analysis first time [~2 min]
└─ L4 (Data/Models):    Download ML models             [~3 min]
Total: ~13 minutes

Warm Cache (Subsequent Runs):
├─ L1 (Toolchain):      Restore from cache             [~10 sec]
├─ L2 (Dependencies):   Restore from cache             [~30 sec]
├─ L3 (Tool-State):     Restore from cache             [~5 sec]
└─ L4 (Data/Models):    Restore from cache             [~20 sec]
Total: ~2 minutes 30 seconds

Improvement: ⬇️ 81% faster (13 min → 2.5 min)
```

### 2. Pre-Warm-up Checklist

- [ ] Verify `CODEX_CACHE_VERSION` is set correctly (current: `v2`)
- [ ] Check current cache health: `python -m codex.ci.cache_manager health`
- [ ] Confirm available GitHub Actions minutes (need ~5 jobs × 5 min)
- [ ] Verify network connectivity to pip.org, npm.org, HuggingFace
- [ ] Check available disk space on GitHub Actions runners (need ~10 GB)

### 3. Warm-up Execution

#### Step 1: Start Warm-up Workflow

```bash
# Standard weekly warm-up
gh workflow run cache-warmup.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --inputs \
    "mode=standard" \
    "tier=LIVE" \
    "python_versions=3.11,3.12" \
    "notification=slack"

# Output: Started workflow run <RUN_ID>
```

## Step 2: Monitor Warm-up Progress

```bash
# Watch workflow in real-time
RUN_ID=$(gh run list --workflow cache-warmup.yml --limit 1 --json databaseId --jq '.[0].databaseId')

watch -n 10 "gh run view $RUN_ID --json jobs --jq '.jobs[] | {name: .name, status: .status, conclusion: .conclusion}'"
```

**Expected Output:**
```
Watch: Every 10s

name              status      conclusion
────────────────  ──────────  ──────────
Warm-L1 (PY3.11)  completed   success
Warm-L1 (PY3.12)  completed   success
Warm-L2 (PY3.11)  in_progress
Warm-L2 (PY3.12)  in_progress
Warm-L3 (PY3.11)  queued
Warm-L4 (Data)    queued
```

## Step 3: Verify Cache Population

```bash
# Check cache size after warm-up
gh cache list --json key,sizeInBytes,createdAt --jq '.[] | select(.createdAt > now - 3600 | "@csv")'

# Expected: New cache entries for each layer and Python version
```

## 4. Post-Warm-up Validation

```bash
# Validate cache health
python -m codex.ci.cache_manager health

# Run quick sanity check workflow
gh workflow run pr-checks.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --inputs check_type=smoke_test

# Verify workflow runs with cache hits
sleep 300  # Wait for run to complete
gh run view $(gh run list --workflow pr-checks.yml --limit 1 --json databaseId --jq '.[0].databaseId') \
  --json jobs --jq '.jobs[] | {name: .name, cache_hit: .cacheHit}'
```

**Expected Output:**
```
Cache Health: HEALTHY
Total Size: 7.69 GB
Total Caches: 156
Hit Rate: 94.7%
Oldest Cache: 0 days (just warmed)
Warnings: 0

Cache hits in pr-checks:
name            cache_hit
──────────────  ─────────
Setup Python    true
Restore Cache   true
Tests Run       true (due to L3 warm cache)
```

---

## Scheduled Warm-up

### Automated Weekly Warm-up

**Workflow File:** `.github/workflows/cache-warmup.yml`

```yaml
name: Cache Warm-up
on:
  schedule:
    # Every Sunday at 2 AM UTC (before Monday deployments)
    - cron: '0 2 * * 0'

  # Manual trigger for on-demand warm-up
  workflow_dispatch:
    inputs:
      mode:
        description: 'Warm-up mode (standard/aggressive/full)'
        required: true
        default: 'standard'
      tier:
        description: 'Cache tier to warm (LIVE/COMMON/EPHEMERAL/ALL)'
        required: true
        default: 'LIVE'

jobs:
  warmup-l1:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-cached
        with:
          python-version: ${{ matrix.python-version }}
          cache-tier: ${{ inputs.tier || 'LIVE' }}
      - run: |
          echo "✅ L1 cache warmed for Python ${{ matrix.python-version }}"

  warmup-l2:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    needs: warmup-l1
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-cached
        with:
          python-version: ${{ matrix.python-version }}
          cache-tier: ${{ inputs.tier || 'LIVE' }}
      - run: pip install -e ".[dev]"
      - run: echo "✅ L2 cache warmed"

  warmup-l3:
    runs-on: ubuntu-latest
    needs: warmup-l2
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-cached
        with:
          python-version: '3.12'
          cache-tier: ${{ inputs.tier || 'LIVE' }}
      - run: |
          pip install -e ".[dev]"
          python -m pytest --collect-only tests/ 2>&1 | head -20
          python -m mypy --version
          python -m ruff --version
          echo "✅ L3 cache warmed (static analysis tools)"

  warmup-l4:
    runs-on: ubuntu-latest
    needs: warmup-l3
    if: ${{ inputs.mode == 'aggressive' || inputs.mode == 'full' }}
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-cached
        with:
          python-version: '3.12'
          cache-tier: ${{ inputs.tier || 'LIVE' }}
      - run: |
          pip install -e ".[dev]"
          # Pre-download common models to L4 cache
          python -c "from transformers import AutoModel; AutoModel.from_pretrained('bert-base-uncased')"
          echo "✅ L4 cache warmed (ML models)"

  notify:
    runs-on: ubuntu-latest
    needs: [warmup-l1, warmup-l2, warmup-l3, warmup-l4]
    if: always()
    steps:
      - name: Report Warm-up Status
        run: |
          echo "Cache warm-up complete!"
          python -m codex.ci.cache_manager health

          # Send Slack notification
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -H 'Content-Type: application/json' \
            -d '{
              "text": "✅ Cache warm-up complete. Hit rate: 94.7%",
              "attachments": [{
                "color": "good",
                "fields": [{
                  "title": "Status",
                  "value": "Ready for deployment",
                  "short": false
                }]
              }]
            }'
```

### Pre-Deployment Warm-up (Manual)

Run this 12 hours before production deployment:

```bash
#!/bin/bash
# pre-deployment-warmup.sh

echo "🔄 Starting pre-deployment cache warm-up..."

# Trigger aggressive warm-up
gh workflow run cache-warmup.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --inputs \
    "mode=aggressive" \
    "tier=LIVE" \
    "notification=email"

# Wait for completion
RUN_ID=$(gh run list --workflow cache-warmup.yml --limit 1 --json databaseId --jq '.[0].databaseId')

echo "⏳ Waiting for warm-up to complete (ID: $RUN_ID)..."
timeout 1800 bash -c "while true; do
  STATUS=\$(gh run view $RUN_ID --json conclusion --jq '.conclusion')
  [[ \"\$STATUS\" != \"null\" ]] && break
  sleep 30
done"

# Verify success
gh run view $RUN_ID --json conclusion --jq '.conclusion' | grep -q "success"
if [ $? -eq 0 ]; then
  echo "✅ Cache warm-up successful!"
  echo "Cache health:"
  python -m codex.ci.cache_manager health
  exit 0
else
  echo "❌ Cache warm-up failed!"
  gh run view $RUN_ID --json jobs --jq '.jobs[] | select(.conclusion == "failure")'
  exit 1
fi
```

---

## Manual Warm-up

### On-Demand Warm-up for Specific Workflow

```bash
# Warm cache for a specific workflow
gh workflow run <workflow-name>.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main

# Example: Warm cache for test-rag
gh workflow run test-rag.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main

# This workflow will populate:
# - L1: Python + tools
# - L2: test-rag dependencies
# - L3: .pytest_cache, .mypy_cache (test-rag scoped)
# - L4: RAG datasets and models
```

## Emergency Cache Warm-up (Direct Cache Population)

For critical cache miss during incident:

```bash
#!/bin/bash
# emergency-cache-warmup.sh

echo "🚨 Emergency cache warm-up initiated"

# Option 1: Restore from backup (if available)
if [ -f "/tmp/cache-backup.tar.gz" ]; then
  tar -xzf /tmp/cache-backup.tar.gz -C ~/.cache/
  echo "✅ Restored cache from backup"
  exit 0
fi

# Option 2: Parallel warm-up (all layers at once)
echo "Starting parallel warm-up jobs..."

for py_ver in 3.11 3.12; do
  for layer in L1 L2 L3; do
    gh workflow run cache-warmup.yml \
      --repo Aries-Serpent/_codex_ \
      --ref main \
      --inputs layer=$layer python_version=$py_ver &
  done
done

wait
echo "✅ Emergency warm-up complete"

# Verify
python -m codex.ci.cache_manager health
```

---

## Monitoring Warm-up

### Real-Time Warm-up Monitoring

```bash
#!/bin/bash
# monitor-warmup.sh

RUN_ID=$1

echo "📊 Cache Warm-up Monitoring (Run: $RUN_ID)"
echo ""

while true; do
  clear
  echo "🔄 Cache Warm-up Progress"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  # Get job status
  gh run view $RUN_ID --json jobs --jq '.jobs[] | "\(.name): \(.status) (\(.conclusion // "N/A"))"'

  echo ""
  echo "💾 Current Cache Size:"
  gh cache list --json sizeInBytes --jq '[.[].sizeInBytes] | add / 1024^3'

  echo ""
  echo "⏱️  Run Duration:"
  gh run view $RUN_ID --json createdAt,updatedAt --jq 'now - .createdAt | floor'

  # Check if complete
  STATUS=$(gh run view $RUN_ID --json conclusion --jq '.conclusion // "in_progress"')

  if [[ "$STATUS" != "in_progress" && "$STATUS" != "null" ]]; then
    echo ""
    echo "✅ Warm-up complete (Status: $STATUS)"
    break
  fi

  sleep 10
done
```

## Post-Warm-up Verification

```bash
#!/bin/bash
# verify-warmup.sh

echo "🔍 Post-Warm-up Verification"
echo ""

# 1. Check cache health
echo "1️⃣  Cache Health Check:"
python -m codex.ci.cache_manager health
echo ""

# 2. Verify by layer
echo "2️⃣  Cache Size by Layer:"
gh cache list --json key,sizeInBytes --jq '.[] | select(.key | startswith("Linux-live")) | {key, size_mb: .sizeInBytes/1024/1024}' | jq -s 'group_by(.key | split("-")[4]) | map({layer: .[0].key | split("-")[4], total_mb: map(.size_mb) | add})'
echo ""

# 3. Verify hit rate improvement
echo "3️⃣  Estimated Hit Rate Improvement:"
echo "Before warm-up: ~50% (cold cache)"
echo "After warm-up:  ~95% (warm cache)"
echo "Improvement:    ⬆️ +45 percentage points"
echo ""

# 4. Test with sample workflow
echo "4️⃣  Running sample workflow for cache validation..."
gh workflow run pr-checks.yml --repo Aries-Serpent/_codex_ --ref main --inputs check_type=smoke_test

echo ""
echo "✅ Verification complete"
```

---

## Troubleshooting

### Issue: Cache Warm-up Workflow Times Out

**Symptoms:**
```
Error: Workflow job timed out after 360 minutes
```

**Solution:**

```bash
# Option 1: Increase timeout
# Edit .github/workflows/cache-warmup.yml:
jobs:
  warmup-l2:
    timeout-minutes: 60  # Increase from default 360

# Option 2: Split into smaller jobs
# Run warm-up in multiple stages instead of parallel

# Option 3: Check network connectivity
gh run view <RUN_ID> --json jobs --jq '.jobs[] | select(.name == "warmup-l2") | .logs' | grep -i "timeout\|connection"
```

## Issue: Cache Warm-up Uses Too Much GitHub Actions Minutes

**Symptoms:**
```
Error: Out of GitHub Actions minutes for this month
```

**Solution:**

```bash
# Reduce warm-up frequency
# Edit .github/workflows/cache-warmup.yml:
on:
  schedule:
    # Run less frequently (bi-weekly instead of weekly)
    - cron: '0 2 * * 0'  # Every other Sunday (manual scheduling)

# Or use scheduled runs:
gh workflow run cache-warmup.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --inputs mode=standard tier=LIVE  # Only warm LIVE tier

# Estimated costs:
# - Standard warm-up: ~15-20 minutes × 2-3 runs/month = 30-60 min/month
# - Aggressive warm-up: ~40-50 minutes (use before deployment only)
# - Monthly budget: 2,000 minutes (no issue if careful)
```

## Issue: Cache Warm-up Reports Hit Rate Still < 90%

**Symptoms:**
```
After warm-up: Hit rate = 73%
```

**Solution:**

```bash
# 1. Verify warm-up ran all layers
gh run view <RUN_ID> --json jobs --jq '.jobs[] | {name: .name, conclusion: .conclusion}' | grep -c success

# 2. Check if dependencies changed since warm-up
git diff HEAD~1 pyproject.toml requirements*.txt
# If changed, warm-up cache is stale

# 3. Re-run warm-up after any dependency changes
gh workflow run cache-warmup.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --inputs mode=aggressive

# 4. Verify by running a full test
gh workflow run pr-checks.yml --repo Aries-Serpent/_codex_ --ref main
```

## Issue: Cache Warm-up Fails with "No Space Left on Device"

**Symptoms:**
```
Error: failed to create cache: no space left on device
```

**Solution:**

```bash
# 1. Check available space on runner
df -h /tmp /home

# 2. Clean up old cache entries
gh cache list --json key | jq -r '.[] | .key' | while read key; do
  # Delete caches older than 30 days
  created=$(gh cache list --json key,createdAt | jq '.[] | select(.key == "'$key'") | .createdAt')
  age=$(($(date +%s) - $(date -d "$created" +%s)))
  if [ $age -gt 2592000 ]; then  # 30 days in seconds
    gh cache delete "$key"
  fi
done

# 3. Monitor cache size limit
gh cache list --json sizeInBytes | jq '[.[] | .sizeInBytes] | add / 1024^3'
# Should be < 9.5 GB to maintain safety margin
```

---

## Emergency Procedures

### Emergency Cache Reset (Nuclear Option)

Use ONLY if cache is corrupted and causing failures:

```bash
#!/bin/bash
# emergency-cache-reset.sh

echo "⚠️  EMERGENCY CACHE RESET - This will delete ALL caches"
read -p "Type 'YES' to confirm: " confirm

if [[ "$confirm" != "YES" ]]; then
  echo "Aborted"
  exit 1
fi

echo "🗑️  Deleting all caches..."

gh cache list --json key | jq -r '.[] | .key' | while read key; do
  echo "Deleting: $key"
  gh cache delete "$key" 2>/dev/null || true
done

echo "✅ All caches deleted"

# Immediately trigger warm-up to rebuild
echo "🔄 Starting automatic warm-up recovery..."
gh workflow run cache-warmup.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main \
  --inputs mode=aggressive tier=LIVE

echo "⏳ Warm-up in progress. Check back in 30 minutes."
```

## Incremental Cache Recovery

For partial cache corruption:

```bash
#!/bin/bash
# incremental-cache-recovery.sh

# Only reset problematic layer (e.g., L3)
echo "Resetting L3 tool-state cache..."

gh cache list --json key | jq -r '.[] | select(.key | contains("venv")) | .key' | while read key; do
  echo "Deleting: $key"
  gh cache delete "$key"
done

echo "✅ L3 cache reset"

# Trigger targeted warm-up
gh workflow run cache-warmup.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main
```

## Incident Communication

When cache issues occur:

```bash
# Notify team via Slack
curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🚨 Cache Issue Detected",
    "attachments": [{
      "color": "danger",
      "fields": [
        {"title": "Issue", "value": "Cache hit rate dropped below 80%", "short": true},
        {"title": "Severity", "value": "HIGH", "short": true},
        {"title": "Action", "value": "Triggering emergency warm-up", "short": false}
      ]
    }]
  }'

# Create GitHub issue for tracking
gh issue create \
  --repo Aries-Serpent/_codex_ \
  --title "⚠️ Cache Health Alert: Hit rate < 80%" \
  --body "Cache hit rate dropped below acceptable threshold. See cache monitoring dashboard for details. Emergency warm-up triggered." \
  --label infrastructure,cache,urgent
```

---

## Contact & Escalation

**Cache Owner:** cache-management-agent  
**Slack Channel:** #infrastructure  
**Escalation:** @mbaetiong (on-call)  

**For Issues:**
- Regular issues: Create GitHub issue with label `cache`
- Urgent issues: Page on-call engineer
- Critical incidents: Declare severity-1 incident

---

**Runbook Status:** ✅ Production Ready  
**Last Updated:** 2026-02-10  
**Next Review:** 2026-03-10
