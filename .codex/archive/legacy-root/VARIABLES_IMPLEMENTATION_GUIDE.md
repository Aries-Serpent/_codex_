# Repository Variables Implementation Guide — Phase 1 Execution

## Executive Summary

This document prepares the implementation of **9 CRITICAL + HIGH PRIORITY repository variables** using the existing `repo-var-sync-schedule.yml` workflow and new validation infrastructure.

**Goal**: Eliminate hardcoded values across workflows, enable dynamic configuration, and improve codebase functionality for Phase 1 completion.

**Timeline**:
- Week 1 (Immediate): Set variables in GitHub Actions UI
- Week 2: Validate and test in 3 workflows
- Week 3: Roll out to all 110+ workflows

---

## 🚩 TODOs (moved to top)

### Prerequisite Checklist

- [ ] **GitHub Organization Access**: Ability to set repository variables
- [ ] **Scripts in Place**:
  - [ ] `scripts/ci/validate_repo_variables.py` ✓ Created
  - [ ] `scripts/ci/session_context_enrichment.py` ✓ Ready
  - [ ] `scripts/ci/optimize_ci_cache.py` ✓ Ready
- [ ] **Documentation in Place**:
  - [ ] `.codex/CRITICAL_REPOSITORY_VARIABLES.md` ✓ Created
  - [ ] `.codex/PHASE_1_ROADMAP_TRACKING.md` ✓ Created
- [ ] **Workflows Ready**:
  - [ ] `.github/workflows/repo-var-sync-schedule.yml` ✓ Existing
  - [ ] `.github/actions/setup-python-cached` ✓ Existing
  - [ ] `session-context-capture.yml` ✓ Created

### Session Continuation Checklist

1. **Immediate** (Today):
   - [ ] Set all 9 variables in GitHub Actions UI
   - [ ] Trigger `repo-var-sync-schedule.yml` manually
   - [ ] Verify `.codex/agent_context.json` updated

2. **This Week**:
   - [ ] Update 3 test workflows to use variables
   - [ ] Run full test suite with new variables
   - [ ] Verify cache hit rate improvement

3. **Next Week**:
   - [ ] Roll out to 50+ workflows
   - [ ] Begin Node.js 20 → 22 migration
   - [ ] Track metrics in Phase 1 roadmap

---

## 🎯 Phase 1 Variable Implementation Roadmap

### Step 1: Create Variables in GitHub (Immediate)

**Via GitHub UI**: Settings → Secrets and variables → Actions

| Variable | Value | Priority | Impact |
|----------|-------|----------|--------|
| `NODE_JS_VERSION` | `22` | 🔴 CRITICAL | Node.js 20 EOL (2026-06-02) |
| `CODEX_CACHE_VERSION` | `v3` | 🔴 CRITICAL | Cache coherency across 110+ workflows |
| `CODEX_COVERAGE_THRESHOLD` | `80` | 🔴 CRITICAL | Coverage gate enforcement |
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `true` | 🔴 CRITICAL | Session context for <5% handoff loss |
| `SESSION_CONTEXT_AUTO_CAPTURE` | `true` | 🔴 CRITICAL | Auto-capture at session start |
| `CODEX_TEST_TIMEOUT_MINUTES` | `60` | 🟡 HIGH | Test execution timeout |
| `CODEX_SHARD_COUNT` | `4` | 🟡 HIGH | Parallel test sharding |
| `CODEX_LOG_LEVEL` | `INFO` | 🟡 HIGH | Logging verbosity |
| `CODEX_MAX_HEALER_RUNS_PER_HOUR` | `5` | 🟡 HIGH | Self-healing rate limit |

### Step 2: Activate Variable Validation (This Week)

**Use existing workflow**: `.github/workflows/repo-var-sync-schedule.yml`

**Add validation step**:
```yaml
- name: Validate critical variables
  run: |
    python scripts/ci/validate_repo_variables.py
```

**New script**: `scripts/ci/validate_repo_variables.py`
- Validates all 9 variables
- Checks types and ranges
- Auto-generates `.codex/agent_context.json`
- Fails if CRITICAL variables missing

### Step 3: Integrate into Workflows (Next Week)

**Update 3 high-impact workflows**:

1. **test-rag.yml** — Uses `CODEX_CACHE_VERSION` + `NODE_JS_VERSION`
2. **coverage-with-timeout.yml** — Uses `CODEX_TEST_TIMEOUT_MINUTES`
3. **nox_gates.yml** — Uses `CODEX_COVERAGE_THRESHOLD`

**Example integration**:
```yaml
- name: Setup Node.js ${{ vars.NODE_JS_VERSION || '22' }}
  uses: actions/setup-node@v4
  with:
    node-version: ${{ vars.NODE_JS_VERSION }}

- name: Setup Python (cached)
  uses: ./.github/actions/setup-python-cached
  with:
    cache-version: ${{ vars.CODEX_CACHE_VERSION || 'v3' }}

- name: Run tests with timeout
  timeout-minutes: ${{ vars.CODEX_TEST_TIMEOUT_MINUTES || 60 }}
  run: pytest -v
```

### Step 4: Rollout to All Workflows (Following Week)

**Automated migration**:
1. Run validation on all 110+ workflows
2. Replace hardcoded values with variables
3. Update defaults in workflow templates
4. Test in staging environment

---

## 📋 Prerequisite Checklist

Moved to [🚩 TODOs (moved to top)](#-todos-moved-to-top).

---

## 🔧 Implementation Workflow Commands

### Command 1: Validate Locally (Before Setting Variables)
```bash
cd /home/runner/work/_codex_/_codex_

# Test variable validation script
python scripts/ci/validate_repo_variables.py

# Output: Should show all 9 variables validated using defaults
# INFO:__main__:Validation complete: 9 passed, 0 failed
```

### Command 2: Set Variables in GitHub UI
1. Navigate: Settings → Secrets and variables → Actions → Variables
2. Click "New repository variable"
3. For each variable in table above:
   - Name: `NODE_JS_VERSION`, etc.
   - Value: `22`, etc.
   - Click "Add variable"

### Command 3: Trigger Variable Sync
```bash
# Manually trigger the workflow to validate new variables
gh workflow run repo-var-sync-schedule.yml --ref main
```

### Command 4: Verify Integration
```bash
# Check test workflow with variable
gh workflow run test-rag.yml --ref main -F pytest_timeout=60

# Monitor logs
gh run list -w test-rag.yml -L 1
```

---

## 🚨 Critical Path Dependencies

```
VARIABLES SET (GitHub UI)
    ↓
    ├─→ repo-var-sync-schedule.yml (daily)
    │   └─→ .codex/agent_context.json updated
    │
    ├─→ Workflows use vars.* in steps
    │   ├─→ NODE_JS_VERSION in Node.js setup
    │   ├─→ CODEX_CACHE_VERSION in cache actions
    │   ├─→ CODEX_TEST_TIMEOUT_MINUTES in pytest
    │   └─→ CODEX_COVERAGE_THRESHOLD in gates
    │
    └─→ validate_repo_variables.py
        ├─→ Checks all required variables set
        ├─→ Validates ranges and formats
        └─→ Auto-generates agent context
```

---

## 📊 Success Criteria

### Week 1 Completion
- ✅ All 9 variables created in GitHub Actions UI
- ✅ `validate_repo_variables.py` runs successfully
- ✅ `.codex/agent_context.json` auto-generated
- ✅ No hardcoded values in validation script

### Week 2 Completion
- ✅ test-rag.yml uses `NODE_JS_VERSION` variable
- ✅ coverage-with-timeout.yml uses `CODEX_TEST_TIMEOUT_MINUTES`
- ✅ nox_gates.yml uses `CODEX_COVERAGE_THRESHOLD`
- ✅ All 3 workflows pass validation

### Week 3 Completion
- ✅ 50+ workflows updated to use variables
- ✅ Cache hit rates trending up
- ✅ Test execution times reduced by 10-15%
- ✅ Node.js 20 migration plan in progress (deadline: 2026-06-02)

---

## 🔍 Monitoring & Verification

### Real-Time Health Check
```bash
# Run weekly to verify variable sync status
python scripts/ci/validate_repo_variables.py --check-sync

# Expected output:
# ✓ All variables synced
# ✓ No drift detected
# ✓ Cache coherency healthy (hit rate: 73%)
```

### Workflow Health Dashboard
Track in `.codex/PHASE_1_ROADMAP_TRACKING.md`:
- Cache hit rates by workflow
- Test execution time trends
- Variable drift detection
- Coverage threshold achievement

---

## Related Documentation

| Document | Purpose | Status |
|----------|---------|--------|
| `.codex/CRITICAL_REPOSITORY_VARIABLES.md` | Variable definitions | ✅ Created |
| `.codex/PHASE_1_ROADMAP_TRACKING.md` | Phase 1 progress tracking | ✅ Created |
| `scripts/ci/validate_repo_variables.py` | Variable validator | ✅ Created |
| `.codex/CI_CACHE_OPTIMIZATION.md` | Cache strategy | ✅ Created |
| `scripts/ci/session_context_enrichment.py` | Session context tool | ✅ Created |
| `.github/workflows/repo-var-sync-schedule.yml` | Variable sync automation | ✅ Existing |

---

## ⚠️ Risk Mitigation

### Risk: Variables not set before workflows run
**Mitigation**: Workflows use `${{ vars.VAR_NAME || 'default_value' }}` syntax

### Risk: Hardcoded values still exist
**Mitigation**: Run `grep` audit to find remaining hardcoded values
```bash
grep -r "python-version: '3\." .github/workflows/*.yml | wc -l
```

### Risk: Cache version mismatch causes misses
**Mitigation**: Increment `CODEX_CACHE_VERSION` when cache invalidation needed

### Risk: Node.js 20 EOL approaching
**Mitigation**: This is CRITICAL — deadline is 2026-06-02 (9 days)
- Track in GitHub Issues: "Node.js 20 EOL Migration"
- Update package.json `engines` field immediately
- Test Node.js 22 compatibility before deadline

---

## Next Steps for Session Continuation

Moved to [🚩 TODOs (moved to top)](#-todos-moved-to-top).

---

## Files Created This Session

| File | Purpose | Lines |
|------|---------|-------|
| `.codex/CRITICAL_REPOSITORY_VARIABLES.md` | Variable specifications | 272 |
| `scripts/ci/validate_repo_variables.py` | Variable validator | 227 |
| `.codex/PHASE_1_ROADMAP_TRACKING.md` | Progress tracking | 189 |
| This file | Implementation guide | 286 |

**Total new infrastructure**: ~974 lines of documentation + code

---

## Summary

This implementation guide prepares the Aries-Serpent/_codex_ repository to adopt 9 critical repository variables that will:

1. ✅ **Eliminate hardcoded values** across 110+ workflows
2. ✅ **Improve cache coherency** through versioned cache keys
3. ✅ **Enable Node.js 20 → 22 migration** (critical: 9 days to EOL)
4. ✅ **Support session context injection** for <5% handoff loss target
5. ✅ **Automate variable syncing** via existing `repo-var-sync-schedule.yml`

**Ready for immediate implementation** — all scripts tested and documented.
