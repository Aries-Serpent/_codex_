# Critical Repository Variables Configuration — Phase 1 Setup

## Overview
This document identifies repository variables that MUST be configured in GitHub Actions to improve codebase functionality across CI/CD, testing, caching, and deployment workflows.

## 🔴 CRITICAL Variables (Must Set Immediately)

### 1. Node.js Version Management
**Reason**: Node.js 20 EOL on 2026-06-02. Must coordinate version across all workflows.

```yaml
NODE_JS_VERSION: "22"                          # Target LTS version (was: 20)
NODE_JS_ALLOWED_VERSIONS: "22,23"              # Allowed versions (comma-separated)
NODE_JS_DEPRECATION_VERSION: "20"              # Deprecated versions to warn on
NODE_JS_AUTO_UPDATE_ENABLED: "true"            # Auto-update workflows on EOL
```

**Implementation**: Add to GitHub Actions variables and use in workflows:
```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: ${{ vars.NODE_JS_VERSION || '22' }}
```

### 2. Cache Management & Versioning
**Reason**: Cache coherency across 110+ workflows. Prevents stale cache hits.

```yaml
CODEX_CACHE_VERSION: "v2"                      # Current cache version key used by setup-agent-env and CI caches
CODEX_CACHE_TTL_DAYS: "7"                      # Cache time-to-live
CODEX_PIP_CACHE_ENABLED: "true"                # Enable pip download cache
CODEX_VENV_CACHE_ENABLED: "true"               # Enable venv cache
CODEX_TORCH_CACHE_ENABLED: "true"              # Enable PyTorch cache
CODEX_NPM_CACHE_ENABLED: "true"                # Enable npm tool cache
```

**Implementation Usage**:
```yaml
- name: Setup Python (cached)
  uses: ./.github/actions/setup-python-cached
  with:
    python-version: '3.12'
    cache-tier: common
    cache-version: ${{ vars.CODEX_CACHE_VERSION || 'v2' }}
```

### 3. CI/CD Workflow Configuration
**Reason**: Control workflow behavior, timeouts, and resource allocation.

```yaml
CODEX_COVERAGE_THRESHOLD: "80"                 # Minimum coverage % threshold
CODEX_TEST_TIMEOUT_MINUTES: "60"               # Global test timeout
CODEX_JOB_TIMEOUT_MINUTES: "120"               # Global job timeout
CODEX_MAX_PARALLEL_JOBS: "4"                   # Max concurrent jobs
CODEX_SHARD_COUNT: "4"                         # Test sharding count
```

### 4. Cognitive Brain & Session Management
**Reason**: Session state persistence and context enrichment for <5% handoff loss.

```yaml
COGNITIVE_BRAIN_INJECTION_ENABLED: "true"      # Enable session injection
COGNITIVE_BRAIN_SESSION_RETENTION_HOURS: "24"  # How long to keep sessions
COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS: "128000"   # Max context tokens
SESSION_CONTEXT_AUTO_CAPTURE: "true"           # Auto-capture at session start
SESSION_CONTEXT_AUTO_INJECT: "true"            # Auto-inject on session init
```

**Implementation**: Used by `cognitive-brain-session-injector` agent:
```python
# scripts/ci/session_context_enrichment.py
enricher = SessionContextEnricher(
    session_number=os.getenv("COGNITIVE_BRAIN_SESSION_NUMBER"),
    retention_hours=int(os.getenv("COGNITIVE_BRAIN_SESSION_RETENTION_HOURS", "24"))
)
```

### 5. API & Integration Endpoints
**Reason**: Backend service discovery and configuration.

```yaml
CODEX_CLI_API_URL: "http://localhost:8765"     # CLI API gateway
COGNITIVE_APP_API_URL: "http://localhost:3000" # React app API
WEBHOOK_RECEIVER_URL: "https://api.codex/webhooks"
METRICS_STREAM_URL: "ws://localhost:8765/ws/metrics"  # New WebSocket metrics
```

---

## 🟡 HIGH PRIORITY Variables (Should Set This Week)

### 6. Test Execution Configuration
```yaml
PYTEST_TIMEOUT_SECONDS: "420"                  # Per-test timeout
PYTEST_XFAIL_STRICT: "true"                    # Fail on unexpected pass
PYTEST_RANDOMLY_DONT_SHUFFLE: "false"          # Enable random ordering
COVERAGE_MIN_PERCENT: "80"                     # Min coverage threshold
```

### 7. Reliability & Self-Healing
```yaml
CODEX_MAX_HEALER_RUNS_PER_HOUR: "5"            # Self-healing rate limit
CODEX_HEALER_SKIP_SKIPCI: "false"              # Skip jobs with [skip ci]
AUTO_HEAL_TIMEOUT_FAILURES: "true"             # Auto-heal timeout errors
AUTO_HEAL_IMPORT_ERRORS: "true"                # Auto-heal import errors
```

### 8. Telemetry & Monitoring
```yaml
CODEX_TELEMETRY_ENABLED: "true"                # Enable metrics collection
CODEX_LOG_LEVEL: "INFO"                        # Logging verbosity
METRICS_COLLECTION_INTERVAL_SECONDS: "60"      # Metrics sampling rate
WORKFLOW_FAILURE_TRACKING_ENABLED: "true"      # Track all failures
```

---

## 🟢 NICE-TO-HAVE Variables (Future)

### 9. Performance & Optimization
```yaml
CODEX_PARALLEL_SHARDS: "4"                     # Parallel test execution
CODEX_CACHE_STRATEGY: "tiered"                 # Cache strategy
CODEX_COMPRESSION_ENABLED: "true"              # Enable result compression
```

### 10. Environment & Deployment
```yaml
DEPLOY_ENV: "development"                      # Deployment environment
PUSH_PLATFORMS: "PyPI,DockerHub"               # Publish targets
AUTO_PROMOTE_TIER_ENABLED: "true"              # Auto-promote on success
```

---

## 11. Codespaces Container Setup

These variables control the devcontainer lifecycle and ensure Copilot agents in
Codespaces have consistent runtime configuration across prebuilds and rebuilds.
They were introduced to resolve prebuild error **1309
(UnifiedContainersErrorPrebuilTemplateOnCreateFailed)**, caused by APT list
directory corruption (`/var/lib/apt/lists/partial is missing`) during the
`onCreateCommand` phase.

| Variable | MUST/SHOULD/MAY | Default | Purpose |
|----------|-----------------|---------|---------|
| `CODESPACES_APT_UPDATE_RETRY` | SHOULD | `true` | Enable retry logic when `apt-get update` fails during prebuild |
| `CODESPACES_APT_CLEANUP_AGGRESSIVE` | MAY | `true` | Aggressively clean APT lists after install (safe for transient containers) |
| `CODEX_DEVCONTAINER_WORKSPACE` | SHOULD | `/workspaces/_codex_` | Canonical workspace path (mirrors `CODESPACE_VSCODE_FOLDER`) |
| `CODEX_DEVCONTAINER_PYTHON_VERSION` | MUST | `3.12` | Python version (MUST match `pyproject.toml` requires-python) |
| `CODEX_DEVCONTAINER_NODE_VERSION` | SHOULD | `20` | Node.js version for `cognitive_app` builds |
| `CODEX_DEVCONTAINER_RUST_VERSION` | MAY | `stable` | Rust toolchain version for container features |
| `CODEX_SESSION_LOG_DIR` | MUST | `/workspaces/_codex_/.codex/sessions` | Session log directory (in-container, not repo root) |
| `CODEX_DB_PATH` | MUST | `/workspaces/_codex_/.codex/codex.db` | SQLite database path for Copilot agent context (in-container) |
| `CODEX_SQLITE_POOL` | SHOULD | `1` | Enable SQLite connection pooling (prevents lock contention in concurrent sessions) |
| `CODEX_CLI_API_URL` | MUST | `http://localhost:8765` | Cognitive Brain CLI API endpoint (used by `copilot-setup-steps.yml`) |

**Consumed by**:
1. `.devcontainer/scripts/on-create.sh` — APT state repair + retry logic (`CODESPACES_APT_*`)
2. `.devcontainer/scripts/update-content.sh` — Python/pip setup
3. `.devcontainer/scripts/post-create.sh` — agent context injection
4. `.devcontainer/devcontainer.json` — `containerEnv` defaults
5. `.github/workflows/copilot-setup-steps.yml` — corresponding CI environment setup

**Bootstrap**: run `bash .codex/CODESPACES_VARIABLES_BOOTSTRAP.sh` (requires an
authenticated `gh` CLI) to create all 10 variables with their documented defaults.

---

## Variable Implementation Plan

### Phase 1: Immediate Setup (This Week)
1. Create GitHub Organization/Repository variables for all **CRITICAL** variables
2. Add variable sync workflow: `.github/workflows/repo-var-sync-schedule.yml`
3. Update `.codex/agent_context.json` template with defaults
4. Test variable injection in 3 workflows (nox_gates, coverage-with-timeout, test-rag)

### Phase 2: Integration (Next Week)
1. Update all 110+ workflows to use variables instead of hardcoded values
2. Implement variable validation in `repo-var-sync-schedule.yml`
3. Add variable health dashboard
4. Document variable naming conventions

### Phase 3: Automation (Following Week)
1. Auto-update cache version on cache miss
2. Auto-update Node.js version on EOL approaching
3. Auto-sync variables across forks/mirrors
4. Implement variable change notifications

---

## Critical Variable Dependencies

```
├── NODE_JS_VERSION
│   ├── workflows/app-package-download.yml
│   ├── workflows/docker-build-push.yml
│   └── cognitive_app build steps
│
├── CODEX_CACHE_VERSION
│   ├── .github/actions/setup-python-cached
│   ├── all pip workflows (110+)
│   └── cache invalidation on update
│
├── CODEX_COVERAGE_THRESHOLD
│   ├── coverage-with-timeout.yml
│   ├── nox_gates.yml
│   └── ci-checkpoint-validation.yml
│
├── SESSION_CONTEXT_AUTO_CAPTURE
│   ├── cognitive-brain-session-injector
│   ├── session-context-capture.yml
│   └── session_context_enrichment.py
│
└── COGNITIVE_BRAIN_INJECTION_ENABLED
    ├── comment-review-gate.yml
    ├── copilot-agent-checkin.yml
    └── cognitive_brain integration
```

---

## Implementation Workflow

### GitHub UI: Create Variables
Navigate to Settings → Secrets and Variables → Actions Variables:

**CRITICAL Variables** (Set immediately):
- [ ] `NODE_JS_VERSION` = `22`
- [ ] `CODEX_CACHE_VERSION` = `v2`
- [ ] `CODEX_COVERAGE_THRESHOLD` = `80`
- [ ] `COGNITIVE_BRAIN_INJECTION_ENABLED` = `true`
- [ ] `SESSION_CONTEXT_AUTO_CAPTURE` = `true`

**HIGH PRIORITY Variables** (Set this week):
- [ ] `CODEX_TEST_TIMEOUT_MINUTES` = `60`
- [ ] `CODEX_SHARD_COUNT` = `4`
- [ ] `CODEX_LOG_LEVEL` = `INFO`
- [ ] `CODEX_MAX_HEALER_RUNS_PER_HOUR` = `5`

### Automation: Variable Sync Workflow
Use existing `repo-var-sync-schedule.yml` to automatically manage variables:

```yaml
name: Sync Repository Variables
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      actions: write
    steps:
      - uses: actions/checkout@v5
      - name: Validate variables
        run: |
          python scripts/ci/validate_repo_variables.py
          # Check all required variables are set
          # Validate versions (Node.js, Python, etc)
          # Validate ranges (timeouts, thresholds)
      - name: Update agent context
        run: |
          python scripts/ci/generate_agent_context.py \
            --output .codex/agent_context.json \
            --sync-from-github true
```

---

## Variable Naming Convention

All repository variables MUST follow:
- **Prefix**: `CODEX_*` (repo-specific), `COGNITIVE_*` (brain), `COPILOT_*` (agent), `NODE_*` (runtime)
- **Case**: UPPER_SNAKE_CASE
- **Scope**: Repo-level unless sensitive (then use Secrets)
- **Documentation**: Include in `.codex/PHASE_1_ROADMAP_TRACKING.md`

---

## Validation & Monitoring

### Pre-Deployment Checklist
- [ ] All variables have documented default values
- [ ] No hardcoded values remain in workflows
- [ ] Variable sync test passes
- [ ] Agent context injection works
- [ ] Cache key regeneration works

### Post-Deployment Monitoring
- [ ] Variable usage audit in all workflows
- [ ] Cache hit rates by tier
- [ ] Test execution times trending
- [ ] Coverage threshold achievement
- [ ] Session context capture success rate

---

## Related Files
- Workflow examples: `.github/workflows/coverage-with-timeout.yml`
- Variable sync: `.github/workflows/repo-var-sync-schedule.yml`
- Context enrichment: `scripts/ci/session_context_enrichment.py`
- Tracking: `.codex/PHASE_1_ROADMAP_TRACKING.md`
- Agent context: `.codex/agent_context.json`
