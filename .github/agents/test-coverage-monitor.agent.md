---
name: Test Coverage Monitor
description: DEPRECATED — use unified-coverage-agent instead. Monitors coverage thresholds
  and enforces CI gate blocking on regressions.
status: DEPRECATED
deprecated: true
superseded_by: unified-coverage-agent
deprecated_in: S174 (2026-03-21)
id: test-coverage-monitor
---

> ⚠️ **DEPRECATED** — This agent has been merged into [`unified-coverage-agent`](./unified-coverage-agent.md).
> All capabilities are available via the unified agent. See [agents/AGENT_CONSOLIDATION_MATRIX.md](../../agents/AGENT_CONSOLIDATION_MATRIX.md) for rationale.
> **Effective:** 2026-06-11 | **Policy:** `.codex/CODEBASE_AGENCY_POLICY.md` § CAD-Mandate

# ⚠️ DEPRECATED — Test Coverage Monitor

> **This agent has been superseded.** Use [`unified-coverage-agent`](unified-coverage-agent.md) instead.
>
> All capabilities of this agent (monitoring thresholds, enforcing CI gates, blocking merges on regressions)
> are fully preserved in `unified-coverage-agent` under **Mode: Monitor**.

## Migration

Activate via:
```
@copilot Use the unified-coverage-agent to monitor coverage thresholds
```

## Changelog

- **S174 (2026-03-21):** Deprecated. Tombstone stub created. Full capabilities moved to `unified-coverage-agent`.
