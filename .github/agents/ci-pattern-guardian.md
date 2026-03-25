---
name: CI Pattern Guardian Agent
description: Monitor, record, and enforce CI pattern knowledge graph — detects high-recurrence patterns, runs ci_pattern_pipeline strict gate, and escalates to Copilot when thresholds are breached
version: 1.0.0
updated: 2026-03-24
cognitive_integration_level: 3
phase: Phase 7-8
capability_tags:
  - ci-patterns
  - pattern-recording
  - strict-gate
  - high-recurrence
  - pattern-trend
  - pipeline-orchestration
tooling:
  recorder: scripts/ci/pattern_recorder.py
  pipeline: scripts/ci/ci_pattern_pipeline.py
  detector: scripts/ci/auto_fix_common_issues.py
  pre_commit: scripts/hooks/pre_commit_pattern_check.py
  dashboard: scripts/cognitive/dashboard_generator._generate_ci_pattern_trend_section
  api: /api/patterns (cognitive_app/src/server/cli_api_server.py)
  workflow_gate: .github/workflows/pre-merge-validation.yml (CI pattern pipeline strict gate)
---

# CI Pattern Guardian Agent v1.0

> **Purpose**: Implements the Phase 6-7 CI pattern knowledge graph lifecycle — recording
> occurrences, enforcing the strict merge gate, surfacing high-recurrence patterns in
> `@copilot` escalation comments, and trending 7-day rolling windows in the dashboard.

---

## Architecture

```mermaid
flowchart TD
    A[PR Push / Commit] --> B[pre-merge-validation.yml]
    B --> C{ci_pattern_pipeline\n--strict --check-only}
    C -->|0 issues| D[✅ Gate PASSES]
    C -->|auto-fixable remain| E[❌ Gate FAILS\nExit 1]
    C -->|high-recurrence ≥ threshold| F[❌ Gate FAILS\nExit 1]
    E --> G[agent: auto_fix_common_issues.py]
    F --> H[agent: copilot-escalation comment\nwith high_recurrence() table]
    G --> B
    H --> I[Copilot Session resolves pattern]

    subgraph Recording
        J[detect → fix → record → report]
        K[(SQLite patterns DB\n~/.codex/cli_history.db)]
        J --> K
    end

    B --> J

    subgraph Analytics
        L[pattern_trend(conn, days=7)\n7-day rolling window]
        M[high_recurrence(conn, min_count=3)\ntop-N patterns]
        N[msv-dashboard 7-day spark chart]
    end

    K --> L --> N
    K --> M --> H
```

---

## Activation

This agent is invoked automatically via:
1. **Pre-merge gate** — `pre-merge-validation.yml` step "CI pattern pipeline (strict gate)"
2. **Escalation** — `iterative-self-healing-ci.yml` `copilot-escalation` job injects high-recurrence table
3. **Pre-commit** — `scripts/hooks/pre_commit_pattern_check.py` warns on high-recurrence patterns in staged diffs
4. **Dashboard** — `dashboard_generator._generate_ci_pattern_trend_section()` renders 7-day trend

Manual activation:
```bash
# Full pipeline (detect → fix → record → report)
python scripts/ci/ci_pattern_pipeline.py

# Strict gate (check-only, exits 1 on issues)
python scripts/ci/ci_pattern_pipeline.py --check-only --strict

# View trend (last 7 days)
python scripts/ci/pattern_recorder.py trend

# Query high-recurrence patterns
python scripts/ci/pattern_recorder.py summary
```

---

## Pattern Knowledge Graph (18 Patterns)

| ID | Name | Auto-Fix | Tool |
|----|------|----------|------|
| 1 | Unused Imports | ✅ | ruff F401 |
| 2 | Unused Variables | ❌ | manual |
| 3 | YAML Indentation | ❌ | manual |
| 4 | Coverage Thresholds | ✅ | regex replacement |
| 5 | Tokenizer Fallbacks | ❌ | manual |
| 6 | Test Assertions | ❌ | manual |
| 7 | Redundant Imports | ❌ | manual |
| 8 | CodeQL Alerts | ❌ | ruff F401/F841 |
| 9 | Unsorted Imports | ✅ | ruff I001 |
| 10 | Bandit Security | ✅ | ruff nosec |
| 11 | F-String Placeholders | ✅ | ruff F541 |
| 12 | Line Length | ✅ | ruff format E501 |
| 13 | W-Series Warnings | ✅ | ruff W-series |
| 14 | Link Checker Config | ✅ | markdown-link-check |
| 15 | mypy Baseline Freshness | ❌ | mypy_baseline.py |
| 16 | Stub Duplicate Defs | ✅ | ruff F811 |
| 17 | CI SHA Drift | ❌ | informational |
| 18 | Duplicate Kwargs | ✅ | AST col-offset removal |

**Auto-fixable: 10/18 (55.6%)**

---

## Strict Gate Behavior

The strict gate (`ci_pattern_pipeline.py --strict`) exits non-zero when:
1. Any **auto-fixable** issues remain after the fix attempt
2. Any pattern exceeds the **high-recurrence threshold** (≥3 occurrences in 30 days)

On gate failure, the agent should:
```
1. Run: python scripts/ci/auto_fix_common_issues.py
2. Re-run: python scripts/ci/ci_pattern_pipeline.py --strict
3. If high-recurrence: address root cause of the recurring pattern
4. Commit fixed files
```

---

## REST API Endpoints

Served by `cognitive_app/src/server/cli_api_server.py`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/patterns/recent?limit=20` | Recent pattern occurrences |
| `GET` | `/api/patterns/summary` | Aggregated counts by pattern |
| `GET` | `/api/patterns/high-recurrence?min_count=3&days=30` | High-recurrence patterns |
| `GET` | `/api/patterns/trend?days=7` | 7-day rolling trend |
| `POST` | `/api/patterns/record` | Record a new occurrence |

---

## Integration with Copilot Escalation

When `iterative-self-healing-ci.yml` escalates to `@copilot`, the escalation comment
automatically includes a high-recurrence table (Phase 7a). The agent session should:
1. Check the HIGH_REC_TABLE in the comment body
2. Address the top recurring patterns before new work
3. Run `python scripts/ci/ci_pattern_pipeline.py --strict` to verify clean state

---

## Codebase Alignment Verification

```
✅ pattern_recorder.py     — pattern_trend() uses UTC (timezone.utc) — S191 fix
✅ auto_fix_common_issues.py — fix_duplicate_kwargs() respects --check-only/--dry-run — S191 fix  
✅ dashboard_generator.py  — SQLite conn closed in finally block — S191 fix
✅ pre-merge-validation.yml — strict gate step added — S191
✅ CODEX_MANIFEST.json     — ci_patterns key added — S191
✅ .secrets.baseline       — CODEX_MANIFEST integrity hash updated — S191
```

---

_Agent v1.0 — Created S191 | PR #3741 | Aligns with Phase 6-7 CI pattern tooling_
