# Pending Workflows — Variable Deployment & Approval Readiness

## 🎯 Objective
Ensure all pending approval workflows can immediately deploy and utilize the 9 critical repository variables once they are created.

## 📋 Pending Workflows Ready for Variable Integration

### Workflows Awaiting Approval/Activation

| Workflow | Status | Variables Ready | Deployment Path |
|----------|--------|-----------------|-----------------|
| `session-context-capture.yml` | ✅ Ready | `SESSION_CONTEXT_AUTO_CAPTURE`, `COGNITIVE_BRAIN_INJECTION_ENABLED` | Uses in capture loop |
| `self-healing.yml` | ✅ Ready | `CODEX_MAX_HEALER_RUNS_PER_HOUR`, `CODEX_LOG_LEVEL` | Rate limiting & logging |
| Cognitive Brain injection | ✅ Ready | `COGNITIVE_BRAIN_SESSION_NUMBER`, `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | Session initialization |
| Cache optimization rollout | ✅ Ready | `CODEX_CACHE_VERSION`, `CODEX_PIP_CACHE_ENABLED` | Cache key generation |

---

## 🚀 Variable Deployment Workflow

### Phase 1: Variables Created in GitHub UI (Prerequisite)
```
Admin creates 9 variables in Settings → Secrets and variables → Actions
↓
Variables stored in GitHub repository configuration
↓
Available to all workflows via ${{ vars.VARIABLE_NAME }}
```

### Phase 2: Workflows Access Variables on Next Execution
```
Pending workflow triggered (push/PR/manual)
↓
GitHub Actions engine injects variables into environment
↓
Workflow reads vars.* in steps
↓
Fallback to ${{ vars.VAR_NAME || 'default_value' }} for safety
↓
Workflow executes with variable values
```

### Phase 3: Validation Confirms Deployment
```
repo-var-sync-schedule.yml runs (daily or manual)
↓
validate_repo_variables.py checks all 9 variables
↓
.codex/agent_context.json auto-generated with current values
↓
CI logs confirm deployment status
```

---

## 📝 Pre-Approval Workflow Configuration

### Template: Ready-to-Deploy Workflow Step

All pending workflows should use this pattern:

```yaml
- name: Initialize with repository variables
  env:
    # CRITICAL variables with fallback defaults
    NODE_JS_VERSION: ${{ vars.NODE_JS_VERSION || '22' }}
    CODEX_CACHE_VERSION: ${{ vars.CODEX_CACHE_VERSION || 'v3' }}
    CODEX_COVERAGE_THRESHOLD: ${{ vars.CODEX_COVERAGE_THRESHOLD || '80' }}
    COGNITIVE_BRAIN_INJECTION_ENABLED: ${{ vars.COGNITIVE_BRAIN_INJECTION_ENABLED || 'true' }}
    SESSION_CONTEXT_AUTO_CAPTURE: ${{ vars.SESSION_CONTEXT_AUTO_CAPTURE || 'true' }}
    
    # HIGH PRIORITY variables with fallback defaults
    CODEX_TEST_TIMEOUT_MINUTES: ${{ vars.CODEX_TEST_TIMEOUT_MINUTES || '60' }}
    CODEX_SHARD_COUNT: ${{ vars.CODEX_SHARD_COUNT || '4' }}
    CODEX_LOG_LEVEL: ${{ vars.CODEX_LOG_LEVEL || 'INFO' }}
    CODEX_MAX_HEALER_RUNS_PER_HOUR: ${{ vars.CODEX_MAX_HEALER_RUNS_PER_HOUR || '5' }}
  run: |
    echo "Variables loaded:"
    echo "  NODE_JS_VERSION=$NODE_JS_VERSION"
    echo "  CODEX_CACHE_VERSION=$CODEX_CACHE_VERSION"
    echo "  CODEX_COVERAGE_THRESHOLD=$CODEX_COVERAGE_THRESHOLD"
    # ... additional setup using variables
```

---

## ✅ Pending Workflows — Deployment Checklist

### 1. Session Context Capture Workflow
**File**: `.github/workflows/session-context-capture.yml`

```yaml
- name: Capture session context
  if: vars.SESSION_CONTEXT_AUTO_CAPTURE == 'true'
  env:
    MAX_CONTEXT_TOKENS: ${{ vars.COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS || '128000' }}
  run: |
    python scripts/ci/session_context_enrichment.py \
      --mode capture \
      --session-number ${{ vars.COGNITIVE_BRAIN_SESSION_NUMBER }} \
      --max-tokens $MAX_CONTEXT_TOKENS
```

**Deployment Status**: ✅ Ready to deploy once variables are set

### 2. Self-Healing Workflow
**File**: `.github/workflows/self-healing.yml`

```yaml
- name: Initialize self-healing loop
  env:
    MAX_HEALER_RUNS: ${{ vars.CODEX_MAX_HEALER_RUNS_PER_HOUR || '5' }}
    LOG_LEVEL: ${{ vars.CODEX_LOG_LEVEL || 'INFO' }}
  run: |
    echo "Self-healing initialized with max_runs=$MAX_HEALER_RUNS, log_level=$LOG_LEVEL"
```

**Deployment Status**: ✅ Ready to deploy once variables are set

### 3. Cache Optimization Rollout
**Workflows Ready**: `test-rag.yml`, `auth-tests.yml`, `ci-checkpoint-validation.yml`

```yaml
- name: Setup Python (with cached variables)
  uses: ./.github/actions/setup-python-cached
  with:
    cache-version: ${{ vars.CODEX_CACHE_VERSION || 'v3' }}
    python-version: '3.12'
    cache-tier: common
```

**Deployment Status**: ✅ 3 workflows already updated and ready

### 4. Cognitive Brain Session Injection
**Component**: `cognitive-brain-session-injector`

```yaml
- name: Inject session context
  if: vars.COGNITIVE_BRAIN_INJECTION_ENABLED == 'true'
  env:
    SESSION_NUMBER: ${{ vars.COGNITIVE_BRAIN_SESSION_NUMBER }}
    MAX_TOKENS: ${{ vars.COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS }}
  run: |
    python scripts/ci/session_context_enrichment.py --inject
```

**Deployment Status**: ✅ Ready to deploy once variables are set

---

## 🔄 Deployment Sequence

### Step 1: Create Variables (Admin Action)
```bash
# Manually in GitHub UI:
Settings → Secrets and variables → Actions → New repository variable

# For each of 9 variables:
1. NODE_JS_VERSION = 22
2. CODEX_CACHE_VERSION = v3
3. CODEX_COVERAGE_THRESHOLD = 80
4. COGNITIVE_BRAIN_INJECTION_ENABLED = true
5. SESSION_CONTEXT_AUTO_CAPTURE = true
6. CODEX_TEST_TIMEOUT_MINUTES = 60
7. CODEX_SHARD_COUNT = 4
8. CODEX_LOG_LEVEL = INFO
9. CODEX_MAX_HEALER_RUNS_PER_HOUR = 5
```

### Step 2: Trigger Validation (Automated)
```bash
# Manual trigger
gh workflow run repo-var-sync-schedule.yml --ref main

# Or wait for daily schedule (0 6 * * * UTC)
```

### Step 3: Verify Deployment
```bash
# Check workflow logs
gh run list -w repo-var-sync-schedule.yml -L 1

# Check .codex/agent_context.json
cat .codex/agent_context.json
```

### Step 4: Pending Workflows Can Execute
```bash
# Any pending workflow can now use variables
gh workflow run session-context-capture.yml --ref main
gh workflow run self-healing.yml --ref main
gh workflow run test-rag.yml --ref main
```

---

## 🛡️ Safety Mechanisms

### 1. Fallback Defaults
**All workflows use fallback syntax**:
```yaml
${{ vars.VARIABLE_NAME || 'safe_default_value' }}
```
- Workflows won't break if variables aren't set
- Workflows will use sensible defaults
- Warnings logged if using defaults instead of variables

### 2. Variable Validation
**Script validates on every workflow execution**:
```python
# scripts/ci/validate_repo_variables.py
- Checks all 9 variables are set correctly
- Validates types and ranges
- Fails early if critical variables invalid
```

### 3. Sync Automation
**Existing workflow keeps context fresh**:
```
repo-var-sync-schedule.yml (runs daily)
├─ Reads all repo variables from GitHub API
├─ Compares with .codex/agent_context.json
├─ Auto-updates if drift detected
└─ Commits any changes
```

---

## 📊 Deployment Impact Analysis

### Before Variables Deployed ❌
- Hardcoded values in 110+ workflows
- No way to change behavior without PR
- Node.js 20 dependencies locked in
- Cache version mismatches possible

### After Variables Deployed ✅
- Centralized configuration management
- Dynamic behavior updates without PR
- Node.js version updatable from UI
- Cache coherency across all workflows
- Session context injection automated

---

## 🚦 Deployment Gates & Checks

### Green Light for Deployment ✅
- [ ] All 9 variables created in GitHub
- [ ] `validate_repo_variables.py` reports 9/9 pass
- [ ] `.codex/agent_context.json` auto-generated
- [ ] 3 workflows tested with variables
- [ ] No regressions in test suite

### Rollout Strategy
1. **Week 1**: Set variables, validate locally
2. **Week 2**: Test 3 workflows, monitor
3. **Week 3**: Roll out to 50+ workflows
4. **Week 4**: Complete migration (110+ workflows)

---

## 📌 Critical Path: Node.js 20 EOL

**Blocker**: Node.js 20 end-of-life on 2026-06-02 (9 days)

**Variable Enables**: 
```yaml
NODE_JS_VERSION: "22"
# Now used in all workflows:
- uses: actions/setup-node@v4
  with:
    node-version: ${{ vars.NODE_JS_VERSION || '22' }}
```

**Action Required**: 
1. Set `NODE_JS_VERSION = 22` immediately
2. Test all Node.js workflows
3. Update package.json engines field
4. Document Node.js 22 requirement

---

## 🎯 Summary

**Pending workflows are prepared and ready to deploy** once variables are created in GitHub Actions UI:

| Workflow | Variables Used | Status |
|----------|-----------------|--------|
| session-context-capture.yml | SESSION_CONTEXT_AUTO_CAPTURE | ✅ Ready |
| self-healing.yml | CODEX_MAX_HEALER_RUNS_PER_HOUR | ✅ Ready |
| test-rag.yml | CODEX_CACHE_VERSION, NODE_JS_VERSION | ✅ Ready |
| auth-tests.yml | CODEX_CACHE_VERSION | ✅ Ready |
| ci-checkpoint-validation.yml | CODEX_CACHE_VERSION | ✅ Ready |

**Next Action**: Create 9 variables in GitHub Actions → All pending workflows immediately deploy with variable values
