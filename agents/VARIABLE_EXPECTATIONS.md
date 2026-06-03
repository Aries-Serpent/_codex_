# Agent Variable Expectations

> **Last Updated**: 2026-06-03T18:29:00Z | **Maintainer**: @mbaetiong
> Full variable inventory: [`docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md`](../docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md)
> Runbook: [`docs/SECRETS_RUNBOOK.md`](../docs/SECRETS_RUNBOOK.md)

This document defines which GitHub Actions repository/environment variables each custom Copilot agent category MUST read and respect. Agents that do not honour these expectations are non-compliant with the CODEX agent policy.

---

## Universal Requirements (ALL Agents)

Every custom Copilot coding agent **MUST**:

| Check | Variable | Action on Condition |
|-------|----------|---------------------|
| 🛑 Kill switch | `AGENT_KILL_SWITCH` | If `== '1'`, abort immediately — do not proceed |
| 📋 Preflight rules | `COPILOT_AGENT_PREFLIGHT_RULES` | Load at session start; apply commit compliance rules |
| 🗂️ WEC routing | `COPILOT_WEC_SELECTION_MATRIX` | Reference when selecting Workflow Execution Checklist items |
| 🔐 Autonomy ceiling | `COPILOT_AGENT_MAX_AUTONOMY_LEVEL` | Operate at or below this level (`D` = maximum) |
| 🔑 Token chain | `CODEX_MASTER_KEY → CODEX_BACKUP_KEY → github.token` | Use fallback chain for ALL write operations |
| 🚫 No direct push | _(policy)_ | Never run `git push` — use `report_progress` tool only |

---

## Category-Level Requirements

### 🔵 CI/CD Agents

Includes: `ci-testing-agent`, `ci-auto-healer-agent`, `ci-emergency-response-agent`, `ci-failure-resolution-agent`, `ci-triage-pipeline-agent`, `autonomous-test-healer-agent`, `unified-coverage-agent`, `nox_gates`-driven agents.

| Variable | Read Via | Purpose |
|----------|----------|---------|
| `CODEX_TEST_TIMEOUT_MINUTES` | `vars.CODEX_TEST_TIMEOUT_MINUTES \|\| '60'` | Respect per-job test timeout |
| `CODEX_JOB_TIMEOUT_MINUTES` | `vars.CODEX_JOB_TIMEOUT_MINUTES \|\| '120'` | Respect global job timeout |
| `CODEX_COVERAGE_THRESHOLD` | `vars.CODEX_COVERAGE_THRESHOLD \|\| '80'` | Enforce coverage gate |
| `CODEX_LINT_STRICT` | `vars.CODEX_LINT_STRICT \|\| 'true'` | Fail on any lint warning when strict |
| `CODEX_SHARD_COUNT` | `vars.CODEX_SHARD_COUNT \|\| '4'` | Parallelise test shards |
| `CODEX_MAX_PARALLEL_JOBS` | `vars.CODEX_MAX_PARALLEL_JOBS \|\| '4'` | Cap concurrent agent jobs |
| `CODEX_CACHE_VERSION` | `vars.CODEX_CACHE_VERSION \|\| 'v2'` | Use current cache-bust key shared by setup-agent-env and CI workflows |
| `CODEX_CI_FAILURE_THRESHOLD` | `vars.CODEX_CI_FAILURE_THRESHOLD \|\| '10.0'` | Trigger alerts above threshold |

**Workflow usage pattern:**
```yaml
timeout-minutes: ${{ fromJSON(vars.CODEX_TEST_TIMEOUT_MINUTES || '60') }}
# ...
- uses: ./.github/actions/setup-python-cached
  with:
    cache-version: ${{ vars.CODEX_CACHE_VERSION || 'v2' }}
```

---

### 🟢 Self-Healing Agents

Includes: `self-healing-orchestrator-agent`, `ci-auto-healer-agent`, `autonomous-test-healer-agent`, `ci-resilience-emergency-response-agent`, `fragile-test-guardian`.

| Variable | Read Via | Purpose |
|----------|----------|---------|
| `CODEX_MAX_HEALER_RUNS_PER_HOUR` | `vars.CODEX_MAX_HEALER_RUNS_PER_HOUR \|\| '5'` | Rate-limit healing invocations |
| `AUTONOMOUS_ACTIONS_ENABLED` | `vars.AUTONOMOUS_ACTIONS_ENABLED \|\| 'true'` | Master switch; must be `true` to act |
| `AUTONOMY_MAX_ITERATIONS` | `vars.AUTONOMY_MAX_ITERATIONS \|\| '3'` | Max self-healing iterations per loop |
| `AGENT_RUNNER_ITERATIONS` | `vars.AGENT_RUNNER_ITERATIONS \|\| '2'` | Max runner iterations |
| `CODEX_PIPELINE_STRICT` | `vars.CODEX_PIPELINE_STRICT \|\| 'false'` | Fail on non-critical warnings when strict |
| `WORKFLOW_FAILURE_TRACKING_ENABLED` | `vars.WORKFLOW_FAILURE_TRACKING_ENABLED \|\| 'true'` | Record all workflow failures |

---

### 🟣 Cognitive Brain Agents

Includes: `cognitive-brain-session-injector`, `memory-sync-agent`, `session-analysis-agent`, `rag-freshness-loop-agent`, `rag-index-manager`.

| Variable | Read Via | Purpose |
|----------|----------|---------|
| `COGNITIVE_BRAIN_INJECTION_ENABLED` | `vars.COGNITIVE_BRAIN_INJECTION_ENABLED \|\| 'true'` | Guard all injection calls |
| `COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS` | `vars.COGNITIVE_BRAIN_MAX_CONTEXT_TOKENS \|\| '128000'` | Enforce token budget |
| `COGNITIVE_BRAIN_SESSION_RETENTION_HOURS` | `vars.COGNITIVE_BRAIN_SESSION_RETENTION_HOURS \|\| '24'` | TTL for session context |
| `COGNITIVE_BRAIN_LTM_RETENTION_DAYS` | `vars.COGNITIVE_BRAIN_LTM_RETENTION_DAYS \|\| '90'` | Long-term memory retention |
| `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` | `vars.COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE \|\| '0.75'` | Pattern storage threshold |
| `SESSION_CONTEXT_AUTO_CAPTURE` | `vars.SESSION_CONTEXT_AUTO_CAPTURE \|\| 'true'` | Auto-capture context at session start |
| `SESSION_CONTEXT_AUTO_INJECT` | `vars.SESSION_CONTEXT_AUTO_INJECT \|\| 'true'` | Auto-inject context on agent init |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | `vars.COGNITIVE_BRAIN_SESSION_NUMBER` | Current session counter (auto-incremented) |

---

### 🔴 Security & Compliance Agents

Includes: `security-audit-agent`, `unified-security-scanner`, `pii-scrubber`, `secret-detection-agent`, `code-scanning-remediation-agent`, `dependency-vulnerability-scanner`, `bridge-security-monitor`.

| Variable | Read Via | Purpose |
|----------|----------|---------|
| `DISABLE_SECRET_FILTER` | `vars.DISABLE_SECRET_FILTER` | **MUST be `false`** — abort if `true` outside isolated local debugging |
| `CODEX_ENV` | `env.CODEX_ENV \|\| vars.CODEX_ENV \|\| 'development'` | Enforce stricter rules in `production`; Copilot setup currently exports `copilot-agent` |
| `CODEX_AUTH_MIDDLEWARE_ENABLED` | `vars.CODEX_AUTH_MIDDLEWARE_ENABLED \|\| 'true'` | Guard API auth middleware checks |
| `CODEX_AUTH_RATE_LIMIT` | `vars.CODEX_AUTH_RATE_LIMIT \|\| '100'` | Rate limit threshold for API |
| `CODEX_OFFLINE` | `vars.CODEX_OFFLINE \|\| '1'` | Prevent external requests in sandbox |
| `CODEX_NETWORK_MODE` | `vars.CODEX_NETWORK_MODE \|\| 'isolated'` | Network isolation mode |
| `AUDIT_RETENTION_DAYS` | `vars.AUDIT_RETENTION_DAYS \|\| '90'` | Retention for audit records |

---

### 🟠 Workflow & Orchestration Agents

Includes: `workflow-ci-fixer`, `workflow-compliance-guardian`, `workflow-management-agent`, `workflow-optimization-agent`, `ci-pattern-guardian`, `agent-orchestrator`, `orchestrator-agent`.

| Variable | Read Via | Purpose |
|----------|----------|---------|
| `COPILOT_WEC_SELECTION_MATRIX` | `vars.COPILOT_WEC_SELECTION_MATRIX` | Route WEC items to correct workflows |
| `COPILOT_WEC_TEMPLATE_DRIFT` | `vars.COPILOT_WEC_TEMPLATE_DRIFT` | Track current WEC drift JSON; expected steady-state is `count=0` after remediation |
| `COPILOT_AGENT_PREFLIGHT_RULES` | `vars.COPILOT_AGENT_PREFLIGHT_RULES` | Enforce pre-commit compliance |
| `CODEX_CI_FAILURE_RATE` | `vars.CODEX_CI_FAILURE_RATE` | Live CI health signal |
| `CODEX_CI_FAILURE_THRESHOLD` | `vars.CODEX_CI_FAILURE_THRESHOLD \|\| '10.0'` | Alert above this failure % |
| `WORKFLOW_FAILURE_TRACKING_ENABLED` | `vars.WORKFLOW_FAILURE_TRACKING_ENABLED \|\| 'true'` | Enable failure tracking |
| `COPILOT_RUNNER_PROFILE` | `vars.COPILOT_RUNNER_PROFILE \|\| 'ubuntu-latest'` | Select larger-runner override for `copilot-setup-steps.yml` when needed |

---

### 🟡 ML / Training Agents

Includes: `ml-validation-suite-agent`, `meta-tensor-validator`, `rag-meta-tensor-guardian`, `tokenization-coverage-agent`, `performance-monitor-agent`.

| Variable | Read Via | Purpose |
|----------|----------|---------|
| `CODEX_SEED` | `vars.CODEX_SEED \|\| '42'` | Random seed for deterministic runs |
| `CODEX_CPU_MINIMAL` | `vars.CODEX_CPU_MINIMAL \|\| '0'` | Skip heavy GPU sessions if `1` |
| `CODEX_ABORT_ON_GPU_PULL` | `vars.CODEX_ABORT_ON_GPU_PULL \|\| '0'` | Abort if GPU environment detected |
| `CODEX_ALLOW_TRITON_CPU` | `vars.CODEX_ALLOW_TRITON_CPU \|\| '0'` | Allow Triton CPU fallback |
| `CODEX_FORCE_CPU` | `vars.CODEX_FORCE_CPU \|\| '0'` | Force CPU-only execution |
| `CODEX_NUM_THREADS` | `vars.CODEX_NUM_THREADS \|\| '4'` | Thread pool size |
| `METRICS_COLLECTION_INTERVAL_SECONDS` | `vars.METRICS_COLLECTION_INTERVAL_SECONDS \|\| '60'` | Telemetry sampling interval |
| `CODEX_TELEMETRY_ENABLED` | `vars.CODEX_TELEMETRY_ENABLED \|\| 'true'` | Enable metrics collection |
| `CODEX_LLM_MODEL` | `vars.CODEX_LLM_MODEL \|\| 'gpt-4o'` | Default LLM model |
| `CODEX_LLM_RATE_LIMIT_DELAY` | `vars.CODEX_LLM_RATE_LIMIT_DELAY \|\| '1.0'` | Seconds between LLM API calls |

---

## Variable Access Patterns

### Reading in Workflow Steps

```yaml
- name: Load configuration
  env:
    CODEX_CACHE_VERSION:  ${{ vars.CODEX_CACHE_VERSION || 'v2' }}
    NODE_JS_VERSION:       ${{ vars.NODE_JS_VERSION || '22' }}
    CODEX_TEST_TIMEOUT:    ${{ vars.CODEX_TEST_TIMEOUT_MINUTES || '60' }}
    COGNITIVE_INJECTION:   ${{ vars.COGNITIVE_BRAIN_INJECTION_ENABLED || 'true' }}
    SESSION_AUTO_CAPTURE:  ${{ vars.SESSION_CONTEXT_AUTO_CAPTURE || 'true' }}
    CODEX_MAX_HEALER:      ${{ vars.CODEX_MAX_HEALER_RUNS_PER_HOUR || '5' }}
  run: |
    echo "CODEX_CACHE_VERSION=$CODEX_CACHE_VERSION"
    echo "NODE_JS_VERSION=$NODE_JS_VERSION"
```

### Integer Fields

```yaml
timeout-minutes: ${{ fromJSON(vars.CODEX_TEST_TIMEOUT_MINUTES || '60') }}
```

### Setup Actions

```yaml
- uses: ./.github/actions/setup-python-cached
  with:
    cache-version: ${{ vars.CODEX_CACHE_VERSION || 'v2' }}

- uses: actions/setup-node@v6
  with:
    node-version: ${{ vars.NODE_JS_VERSION || '22' }}
```

### Python / Script Usage

```python
import os

# With type-safe defaults
test_timeout = int(os.getenv("CODEX_TEST_TIMEOUT_MINUTES", "60"))
cache_version = os.getenv("CODEX_CACHE_VERSION", "v2")
node_version = os.getenv("NODE_JS_VERSION", "22")
cognitive_enabled = os.getenv("COGNITIVE_BRAIN_INJECTION_ENABLED", "true").lower() == "true"
healer_rate = int(os.getenv("CODEX_MAX_HEALER_RUNS_PER_HOUR", "5"))
```

---

## Emergency Procedures

### Halt All Agents

Set `AGENT_KILL_SWITCH = 1` in GitHub → Settings → Secrets and variables → Actions → Variables.

All agents check this variable at startup. After investigation, reset to `0`.

### Disable Secret Filter (NEVER IN PRODUCTION)

`DISABLE_SECRET_FILTER` must always be `false`. Any agent detecting `DISABLE_SECRET_FILTER=true` while `CODEX_ENV` is `production` or `copilot-agent` MUST abort and raise an alert via `ci-health-alert-agent`.

---

## Related Documents

- [Full Variable Inventory](../docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md)
- [Secrets Runbook](../docs/SECRETS_RUNBOOK.md)
- [Critical Repository Variables](.codex/../.codex/CRITICAL_REPOSITORY_VARIABLES.md)
- [Agent Registry](AGENT_CONSOLIDATION_MATRIX.md)
- [Tokenized Workflows](TOKENIZED_WORKFLOWS.md)
