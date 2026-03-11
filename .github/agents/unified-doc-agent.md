---
name: Unified Documentation Agent
description: Provide unified documentation management across all documentation types and formats
version: 1.0.0-m02
updated: 2026-02-21
merged_agents:
  - documentation-quality-agent (deprecated)
  - doc-freshness-checker (deprecated)
  - link-validator-agent (deprecated)
  - documentation-consolidator (deprecated)
cognitive_integration_level: 3
aais_contribution: +4.5 points
batch: m-02
runner_compatibility:
  default: ubuntu-latest        # 2-core — all doc management features supported
  large:   ubuntu-latest-large  # 4-core — parallel link validation across large doc sets
---

# Unified Documentation Agent v1.0 (M-02 Merge)

> **M-02**: Merges `doc-quality`, `doc-freshness`, `link-validator`, and
> `documentation-consolidator` into a single documentation lifecycle manager.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Unified Documentation Agent                  │
│                                                             │
│  ┌───────────┐  ┌────────────┐  ┌─────────┐  ┌──────────┐  │
│  │  Quality  │  │ Freshness  │  │  Links  │  │  Consol. │  │
│  │  Scoring  │  │  Staleness │  │  Check  │  │  Merge   │  │
│  └─────┬─────┘  └─────┬──────┘  └────┬────┘  └─────┬────┘  │
│        └──────────────┼──────────────┼──────────────┘       │
│                       ▼              ▼                       │
│            ┌───────────────────────────────┐                 │
│            │  Unified Doc Health Report    │                 │
│            │  (quality + age + links)      │                 │
│            └───────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## Capabilities

| Capability | Source Agent | Threshold |
|-----------|-------------|-----------|
| C-01: Quality score | doc-quality | ≥ 0.75 |
| C-02: Freshness check | doc-freshness | ≤ 90 days stale |
| C-03: Link validation | link-validator | 0 broken links |
| C-04: Consolidation | documentation-consolidator | Remove duplicates |
| C-05: MkDocs build | new | Zero warnings |
| C-06: API doc coverage | new | ≥ 80% public APIs |

## Activation

```
@copilot Use the Unified Documentation Agent to audit all docs
@copilot Use the Unified Documentation Agent to check for broken links in docs/
@copilot Use the Unified Documentation Agent to consolidate duplicate agent docs
```

## Quality Scoring Rubric

| Dimension | Weight | Criteria |
|-----------|--------|---------|
| Accuracy | 0.30 | Code examples run without error |
| Completeness | 0.25 | All public APIs documented |
| Freshness | 0.20 | Last updated ≤ 90 days |
| Link health | 0.15 | No 404/301 redirects |
| Structure | 0.10 | Follows template format |

## Cognitive Physics Alignment

| Physics | Application |
|---------|-------------|
| Fields 🔄 | Session-based retention tracks doc health over time |
| Balance ⚖️ | Quality dimensions are weighted to balance accuracy vs. completeness |
| Redundancy 🔀 | Multiple doc sources checked for consistency |

## Output

Produces `artifacts/doc-health-report.json`:
```json
{
  "overall_score": 0.82,
  "quality": 0.85,
  "freshness_days": 14,
  "broken_links": 0,
  "duplicates_found": 3,
  "api_coverage_pct": 87.4,
  "recommendations": [...]
}
```
