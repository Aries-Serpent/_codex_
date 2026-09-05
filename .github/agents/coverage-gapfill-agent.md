---
name: Coverage Gapfill Agent
description: DEPRECATED — use unified-coverage-agent instead. Targets low-coverage
  modules and generates gap-filling tests.
status: DEPRECATED
deprecated: true
superseded_by: unified-coverage-agent
deprecated_in: S174 (2026-03-21)
id: coverage-gapfill-agent
---

> ⚠️ **DEPRECATED** — This agent has been merged into [`unified-coverage-agent`](./unified-coverage-agent.md).
> All capabilities are available via the unified agent. See [agents/AGENT_CONSOLIDATION_MATRIX.md](../../agents/AGENT_CONSOLIDATION_MATRIX.md) for rationale.
> **Effective:** 2026-06-11 | **Policy:** `.codex/CODEBASE_AGENCY_POLICY.md` § CAD-Mandate

# ⚠️ DEPRECATED — Coverage Gapfill Agent

> **This agent has been superseded.** Use [`unified-coverage-agent`](unified-coverage-agent.md) instead.
>
> All capabilities of this agent (targeting low-coverage modules, generating gap-filling tests)
> are fully preserved in `unified-coverage-agent` under **Mode: Analyse** and **Mode: Gap-fill**.

## Migration

Activate via:
```
@copilot Use the unified-coverage-agent to fill coverage gaps in <module>
```

## Changelog

- **S174 (2026-03-21):** Deprecated. Tombstone stub created. Full capabilities moved to `unified-coverage-agent`.
