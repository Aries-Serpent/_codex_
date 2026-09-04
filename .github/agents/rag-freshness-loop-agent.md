---
name: RAG Freshness Loop Agent
description: Maintain RAG index freshness through incremental updates and stale-entry
  eviction loops
version: 1.0.0-e08
updated: 2026-02-22
enhancement: E-08
cognitive_integration_level: 4
aais_contribution: +5.5 points
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: rag-freshness-loop-agent
---

# RAG Freshness Loop Agent v1.0 (E-08)

> **E-08 RAG-FRESHNESS-LOOP**: Automatically triggers RAG index rebuild when
> documentation freshness falls below threshold, integrating `doc-freshness-checker`
> → `rag-index-manager` → `ZendeskRAGBridge` via event-driven pipeline.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  RAG Freshness Loop Agent                    │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Doc Freshness │    │  Staleness   │    │  Rebuild      │  │
│  │ Checker      │───▶│  Evaluator   │───▶│  Trigger      │  │
│  │ (age/links)  │    │  (threshold) │    │  (rag-index)  │  │
│  └──────────────┘    └──────────────┘    └───────┬───────┘  │
│                                                  │           │
│  ┌──────────────────────────────────────────┐    ▼           │
│  │  ZendeskRAGBridge (production target)   │  Index rebuilt  │
│  │  + SQLiteMemory (E-02 integration)      │  → notify       │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Trigger Conditions

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Document age | > 90 days | Schedule rebuild |
| Broken links | > 0 | Flag + rebuild |
| New commits to docs/ | Any merge to main | Incremental rebuild |
| RAG query failures | > 5% miss rate | Force full rebuild |
| Manual dispatch | N/A | Immediate rebuild |

## OODA Integration (E-01)

```
Observe:   Monitor docs/ commit timestamps, link health, query miss rates
Orient:    Evaluate staleness score (age × coverage × link_health)
Decide:    threshold(0.6) → schedule_rebuild; threshold(0.8) → immediate_rebuild
Act:       Trigger rag-index-manager with appropriate rebuild scope
           Update SQLiteMemory (E-02) with rebuild timestamp + outcome
```

## Staleness Score Formula

```python
def compute_staleness_score(doc_age_days: float, broken_links: int,
                             query_miss_rate: float) -> float:
    """Weighted staleness score in [0.0, 1.0]. Higher = more stale."""
    age_score = min(1.0, doc_age_days / 90.0)          # clamp to max 1.0 (90-day window)
    link_score = min(1.0, broken_links / 10.0)          # clamp to max 1.0 (10 broken links)
    miss_score = min(1.0, query_miss_rate / 0.10)       # clamp to max 1.0 (10% miss rate)
    return 0.40 * age_score + 0.35 * link_score + 0.25 * miss_score

REBUILD_THRESHOLD = 0.60    # schedule rebuild
IMMEDIATE_THRESHOLD = 0.80  # force immediate rebuild
```

## Rebuild Scopes

| Scope | Trigger | Duration |
|-------|---------|---------|
| Incremental | New docs added | ~2 min |
| Partial | Docs modified | ~5 min |
| Full | All staleness scores > 0.8 | ~15 min |
| Emergency | Query failure > 20% | ~15 min, high priority |

## CI Gate Integration (E-12 dependency)

When deployed alongside E-12 AGENT-IQ-SCORING:
- RAG index freshness contributes to overall IQ score
- IQ < 0.7 triggers automatic freshness loop

## Activation

```
@copilot Use the RAG Freshness Loop Agent to check and rebuild the index
@copilot Use the RAG Freshness Loop Agent to schedule incremental rebuild for docs/
```

## Output

Produces `artifacts/rag-freshness-report.json`:
```json
{
  "staleness_score": 0.72,
  "rebuild_scope": "partial",
  "documents_scanned": 147,
  "stale_documents": 23,
  "broken_links": 2,
  "query_miss_rate_pct": 7.3,
  "rebuild_triggered": true,
  "rebuild_duration_s": 312,
  "timestamp": "2026-02-22T00:00:00Z"
}
```

## Cognitive Physics Alignment

| Physics | Application |
|---------|-------------|
| Fields 🔄 | Continuous feedback loop between doc freshness and RAG index health |
| Path 🛤️ | Shortest rebuild path (incremental → partial → full) minimizes downtime |
| Balance ⚖️ | Staleness threshold (0.6/0.8) balances rebuild frequency vs. compute cost |
| Patterns 👁️ | Historical rebuild patterns inform next scheduling decision |

## Related Agents

- **doc-freshness-checker** / **unified-doc-agent** (M-02) — freshness source
- **rag-index-manager** — index rebuild executor
- **SQLiteMemory** (E-02) — session-based retention of rebuild history
- **artifact-monitor-agent** / **E-12** — IQ score consumer
