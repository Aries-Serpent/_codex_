# Workflow Classification Report

## Canonical keep set

This pass keeps the repo’s safety-critical and governance-critical workflows intact while slimming low-signal monitor loops. The active keep set intentionally matches the WEC and repo-health guidance in `.codex/WEC_CANONICAL_ITEMS.md` and `.codex/MAIN_BRANCH_WORKFLOW_HEALTH.md`.

### Must-keep
- `workflow-execution-gate.yml` — required WEC enforcement gate
- `comment-review-gate.yml` — required review gate
- `deferral-language-gate.yml` — required compliance gate
- `agent-auth-delegation.yml` — required delegation gate for agent PRs
- `unified-health-monitoring.yml` — canonical health monitor
- `unified-monitoring-suite.yml` — canonical monitoring aggregation
- `unified-security-scanning.yml` — canonical security baseline
- `dependency-security-gate.yml` — dependency security gate
- `validate-token-health.yml` — token health validation
- `security-alert-notification.yml` — alert fan-out for critical findings
- `branch-cleanup.yml` — branch hygiene enforcement
- `scheduled-archival.yml` — archival automation
- `required-actions-enforcer.yml` — governance enforcement

### Repair-needed
- `security-scanning-suite.yml` — duplicate master workflow that overlaps the canonical security runner and should be manual-only to avoid schedule overlap
- `workflow-analytics-unified.yml` — hourly analytics loop is broader-than-necessary; keep a weekly cadence for reporting only
- `copilot-evolution-suite.yml` — low-signal monitoring cadence is too aggressive for a non-critical suite
- `scaling-framework-monitor.yml` — multi-cadence monitor cluster overlaps with the unified monitoring set

### Redundant or near-duplicate
- `artifact-monitoring.yml`
- `audit-logging.yml`
- `branch-divergence-monitor.yml`
- `correlation-engine-monitor.yml`
- `mcp-health.yml`
- `performance-monitoring.yml`
- `telemetry-collection.yml`
- `unified-security-ops-suite.yml`
- `codebase-health-sweep.yml`
- `routine monitor variants` that overlap the unified health/security entries above

### Can-be-unscheduled
- `artifact-monitoring.yml` — weekly or manual only
- `audit-logging.yml` — weekly only
- `branch-divergence-monitor.yml` — weekly only
- `copilot-evolution-suite.yml` — weekly only
- `correlation-engine-monitor.yml` — weekly only
- `mcp-health.yml` — weekly only
- `performance-monitoring.yml` — weekly only
- `telemetry-collection.yml` — weekly only
- `workflow-analytics-unified.yml` — weekly only after pruning the hourly loop

## Final keep-list philosophy

- Keep one canonical workflow per domain.
- Keep the repo’s WEC-critical workflows untouched and active.
- Keep security and token-health jobs on a reliable daily cadence.
- Reduce low-signal monitoring to weekly cadence or manual dispatch.
- Remove schedule overlap that would otherwise create rate-limit collisions or redundant scanning loops.
