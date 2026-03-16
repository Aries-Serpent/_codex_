# CI Health Monitor

**Workflow File**: `ci-health-monitor.yml`
**Version**: 2.0.0
**Updated**: 2026-03-11 (PR #3552 — P-047 cognitive brain feedback loop wired)

## Purpose

Scheduled and event-driven CI health monitoring workflow. Every 6 hours (and on
relevant pushes) it:

1. Collects 7-day telemetry from GitHub Actions via `collect_telemetry.py`
2. Classifies failures into 19 named patterns (including the 3 new PR #3552 patterns)
3. Auto-updates `CODEX_CI_FAILURE_RATE` repository variable
4. Creates dedup-gated alert issues when failure rate exceeds threshold
5. Dispatches a `cognitive-brain-ci-update` repository event (P-047 feedback loop)

## Triggers

| Trigger | Details |
|---------|---------|
| `schedule` | Every 6 hours (`0 */6 * * *`) |
| `workflow_dispatch` | Manual trigger |
| `push` to `main` / `copilot/**` | On `.github/workflows/**`, `scripts/ci/collect_telemetry.py` changes |

## Permissions Required

| Permission | Level | Reason |
|------------|-------|--------|
| `contents` | `write` | Write cognitive brain status docs |
| `issues` | `write` | Create CI health alert issues |
| `pull-requests` | `write` | Comment on relevant PRs |

## Workflow Architecture

```mermaid
flowchart TD
    TRIGGER([Trigger:\nschedule / push / dispatch])
    TRIGGER --> CHECKOUT[Checkout code]
    CHECKOUT --> PYTHON[Set up Python 3.12\nwith cached deps]
    PYTHON --> DEPS[Install dependencies\npip install requests]
    DEPS --> TELEMETRY[Collect telemetry\ncollect_telemetry.py\n--branch main --days 7]

    TELEMETRY -->|/tmp/telemetry_report.json| METRICS[Extract metrics\nfailure_rate, failed_runs,\ntotal_runs]

    METRICS --> THRESHOLD{failure_rate\n> threshold?}
    THRESHOLD -->|Yes| ALERT_OUT[alert_required=true]
    THRESHOLD -->|No| OK_OUT[alert_required=false]

    METRICS --> SUMMARY[Write job summary\nPattern Distribution table]
    ALERT_OUT --> ISSUE{Open alert issue\nin last 24h?}
    ISSUE -->|No| CREATE_ISSUE[Create ci-health-alert\nissue with pattern table]
    ISSUE -->|Yes| SKIP[Skip — dedup gate]

    METRICS --> UPDATE_VAR[Update CODEX_CI_FAILURE_RATE\nrepo variable\nvalue=rate:status]
    UPDATE_VAR -->|rate < threshold| GREEN_SHA[Update CODEX_CI_LAST_GREEN_SHA]

    METRICS --> BACKUP[Backup key\nhealth check\n/user → HTTP 200?]
    METRICS --> CACHE[Cache health report]
    METRICS --> KPI[Enforcement gap scan\n+ KPI dashboard]
    METRICS --> P047[P-047: Cognitive Brain\nfeedback dispatch\nrepository_dispatch\ncognitive-brain-ci-update]

    style P047 fill:#4a90d9,color:#fff
    style UPDATE_VAR fill:#27ae60,color:#fff
    style CREATE_ISSUE fill:#e74c3c,color:#fff
```

## Telemetry Pattern Classifiers (23 patterns)

`scripts/ci/collect_telemetry.py` — `PATTERN_KEYWORDS` map (23 named patterns + `unknown` fallback):

```mermaid
mindmap
  root((CI Failure\nPatterns\n23 named))
    High-frequency
      coverage-timeout
      auto-fix
      pre-merge-cascade
    Infra
      workflow-cascade
      auth-delegation
      self-healing
    Security
      security-scan
    Build/Container
      docker-build
      docker-smoke-test NEW
    Testing
      test-infrastructure
    Documentation
      documentation
    Operations
      cache
      cognitive-brain
      ci-health
      deployment
      lint
      filesystem-deadlock
    Language/Runtime
      datetime-error
      build-config
      packaging
    Injection
      session-injector
    External
      codespaces NEW
      embedding-rebuild NEW
    Fallback
      unknown
```

## P-047 Cognitive Brain Feedback Loop

```mermaid
sequenceDiagram
    participant M as ci-health-monitor
    participant GHA as GitHub Actions API
    participant CB as Cognitive Brain
    participant VAR as Repo Variables

    M->>GHA: collect_telemetry.py (7d window)
    GHA-->>M: telemetry_report.json
    M->>M: classify failures into 19 patterns
    M->>VAR: PATCH CODEX_CI_FAILURE_RATE = rate:status
    M->>VAR: PATCH CODEX_CI_LAST_GREEN_SHA (if healthy)
    M->>GHA: POST /repos/.../dispatches\nevent_type=cognitive-brain-ci-update\npayload={rate, status, patterns, sha}
    GHA-->>CB: repository_dispatch event
    CB->>CB: Ingest CI health update\nupdate internal knowledge graph
    Note over M,CB: P-047 keyword map wired\n(cognitive-brain pattern in PATTERN_KEYWORDS)
```

## CODEX_CI_FAILURE_RATE Variable Format

```
value = "<rate>:<status>"
Examples:
  "3.2:ok"        — below threshold (default 10%)
  "15.0:degraded" — above threshold
  "25.0:critical" — above 2× threshold
```

## Environment Variables

| Variable | Source | Default | Purpose |
|----------|--------|---------|---------|
| `GITHUB_TOKEN` | `CODEX_MASTER_KEY \|\| CODEX_BACKUP_KEY \|\| GITHUB_TOKEN` | — | API calls |
| `CODEX_CI_FAILURE_THRESHOLD` | repo variable | `10` | Alert threshold (%) |

## Secrets Used

| Secret | Purpose |
|--------|---------|
| `CODEX_MASTER_KEY` | Primary PAT for API calls + variable updates |
| `CODEX_BACKUP_KEY` | Fallback PAT (health-checked each run) |

## History

| Date | PR | Change |
|------|----|--------|
| 2026-01-16 | — | Initial creation |
| 2026-03-11 | #3552 | P-047: cognitive brain feedback dispatch step added; 3 new patterns (`docker-smoke-test`, `codespaces`, `embedding-rebuild`); Mermaid architecture + sequence diagrams |

## Related Documentation

- [`collect_telemetry.py`](../../scripts/ci/collect_telemetry.py) — Pattern classifier implementation
- [`COGNITIVE_BRAIN_STATUS_PR3552.md`](../../.codex/docs/COGNITIVE_BRAIN_STATUS_PR3552.md) — Sprint 2 CI health plan
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
