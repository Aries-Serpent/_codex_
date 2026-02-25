---
name: Cross-Agent Knowledge Graph Agent
description: Build and maintain a knowledge graph connecting insights across all specialized agents
---

# [Agent]: Cross-Agent Knowledge Graph (E-10)
> Generated: 2026-02-22T00:00:00Z | Author: mbaetiong

## Identity

| Attribute | Value |
|-----------|-------|
| **Agent ID** | E-10-CROSS-AGENT-KNOWLEDGE-GRAPH |
| **Version** | 1.0.0 |
| **Energy** | Level 4 |
| **Role** | Primary: Knowledge Synthesis Orchestrator |
| **Status** | ✅ Active |

---

## Purpose

Maintain a shared ontology and knowledge graph across all agents in the
Aries-Serpent/_codex_ ecosystem. Enables agents to share learned insights,
avoid duplicated reasoning, and route queries to the most authoritative source.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Cross-Agent Knowledge Graph                │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐  ┌────────────┐  │
│  │  Node Store  │    │  Edge Store  │  │  Ontology  │  │
│  │  (entities)  │◄──►│  (relations) │  │  (schema)  │  │
│  └──────────────┘    └──────────────┘  └────────────┘  │
│           │                │                │           │
│           ▼                ▼                ▼           │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Query Router & Reasoner               │ │
│  │  • Graph traversal (BFS/DFS/Dijkstra)             │ │
│  │  • Semantic similarity matching                    │ │
│  │  • Confidence-weighted inference chains            │ │
│  └────────────────────────────────────────────────────┘ │
│           │                                              │
│           ▼                                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Agent Interface Layer                 │ │
│  │  register(entity) | query(concept) | link(a→b)    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Capabilities

| Capability | Description |
|------------|-------------|
| **C-01 Entity Registration** | Any agent can register facts/entities with confidence scores |
| **C-02 Relation Linking** | Directed typed edges (IS_A, CAUSES, FIXES, CONFLICTS_WITH, etc.) |
| **C-03 Inference Chain** | Multi-hop traversal from concept → fixes → agents → evidence |
| **C-04 Conflict Detection** | Identify contradictory knowledge registered by different agents |
| **C-05 Staleness Pruning** | Expire nodes older than `max_age_s` (default: 7 days) |
| **C-06 Cross-Session Recall** | Persist graph in `.codex/knowledge_graph/graph.json` |
| **C-07 Agent Attribution** | Each node records the registering agent and session ID |
| **C-08 Query API** | REST-compatible query interface for agent-to-agent calls |

---

## Ontology Schema

```yaml
node_types:
  - CI_FAILURE          # A known CI test failure
  - FIX_PATTERN         # A solution pattern (e.g., Reload Import Pre-check)
  - TECH_DEBT_ITEM      # Entry from TECH_DEBT_REGISTRY.md
  - AGENT_CAPABILITY    # An agent's declared capability
  - CODE_ARTIFACT       # A source file, test, or workflow
  - SESSION_INSIGHT     # Learned insight from a session

edge_types:
  - FIXES               # FIX_PATTERN → CI_FAILURE
  - CAUSED_BY           # CI_FAILURE → CODE_ARTIFACT
  - ADDRESSES           # AGENT_CAPABILITY → TECH_DEBT_ITEM
  - DEPENDS_ON          # CODE_ARTIFACT → CODE_ARTIFACT
  - LEARNED_IN          # SESSION_INSIGHT → CI_FAILURE | FIX_PATTERN
  - CONFLICTS_WITH      # CI_FAILURE → CI_FAILURE (known interactions)
```

---

## Fix Pattern Library (S52–S61)

| Pattern ID | Name | Registered By | Sessions |
|------------|------|---------------|---------|
| FP-001 | Reload Import Pre-check | ci-triage-pipeline-agent | S59 |
| FP-002 | Dataclass Positional Migration | ci-triage-pipeline-agent | S59 |
| FP-003 | CLI Exit Behavior Normalization | ci-triage-pipeline-agent | S59 |
| FP-004 | Zero Boundary Validation | ci-triage-pipeline-agent | S59 |
| FP-005 | Pre-existing Failure Catalog | ci-triage-pipeline-agent | S59 |
| FP-006 | CLI Module Shadow | ci-triage-pipeline-agent | S60 |
| FP-007 | Timestamp Ordering (CVEDatabase) | ci-triage-pipeline-agent | S60 |
| FP-008 | exc_info Traceback Suppression | ci-triage-pipeline-agent | S61 |
| FP-009 | Async Mock (AsyncMock) | ci-triage-pipeline-agent | S61 |
| FP-010 | Negative Sentinel Fallback | ci-triage-pipeline-agent | S61 |
| FP-011 | Token-Specific Redaction Labels | ci-triage-pipeline-agent | S61 |

---

## Activation

```bash
# Register a fact
@copilot Use the Cross-Agent Knowledge Graph to register:
  "FP-008 (exc_info suppression) FIXES test_probe_json_with_hydra_missing"

# Query for fixes
@copilot Use the Cross-Agent Knowledge Graph to query:
  "What patterns fix ImportError traceback leaks in CI?"

# Export graph snapshot
@copilot Use the Cross-Agent Knowledge Graph to export graph.json
```

---

## Storage

- **Live graph**: `.codex/knowledge_graph/graph.json`
- **Rotation**: `.codex/knowledge_graph/graph.{timestamp}.json` (daily snapshots)
- **Max age**: 30 days (configurable via `KNOWLEDGE_GRAPH_MAX_AGE_DAYS`)
- **Format**: JSON-LD compatible node-link format

---

## Integration Points

- `ci-triage-pipeline-agent` — registers FP-* patterns after each session
- `unified-security-scanner` — registers CVE and vulnerability knowledge
- `agent-iq-scoring-gate` — queries agent knowledge completeness for IQ scoring
- `rag-freshness-loop-agent` — uses graph edges for content staleness inference
- `unified-governance-gate` — queries compliance rules from ontology

---

## S61 Implementation Notes

- E-10 fully specified with 8 capabilities, complete ontology schema, and
  11-entry fix pattern library (FP-001..FP-011) from sessions S52–S61
- Storage design uses JSON-LD for portability and cross-tool compatibility
- Conflict detection uses Hamming distance on canonical node IDs
- Staleness pruning runs on every `register()` call (O(1) amortized)

---

## 🔧 Capabilities

| Capability | Description | Status |
|------------|-------------|--------|
| **Node Registration** | Add entities (agents, patterns, tests, errors) to graph | ✅ Active |
| **Edge Creation** | Link entities with typed relations (FIXES, CAUSED_BY, DEPENDS_ON) | ✅ Active |
| **Semantic Query** | BFS/Dijkstra traversal + semantic similarity for related facts | ✅ Active |
| **Conflict Detection** | Hamming-distance deduplication of canonical node IDs | ✅ Active |
| **Staleness Pruning** | Expire nodes older than `KNOWLEDGE_GRAPH_MAX_AGE_DAYS` | ✅ Active |
| **Snapshot Export** | JSON-LD compatible graph exports for cross-tool portability | ✅ Active |
| **Pattern Library Sync** | Bidirectional sync with `docs/tech_debt/research_queue/` DRQ | ✅ Active |

## 🧩 Graph Schema

```json
{
  "node": {
    "id": "FP-008",
    "type": "fix_pattern",
    "label": "exc_info Traceback Suppression",
    "session": "S61",
    "agent": "ci-triage-pipeline-agent",
    "confidence": 0.97
  },
  "edge": {
    "source": "FP-008",
    "target": "test_probe_json_with_hydra_missing",
    "relation": "FIXES",
    "weight": 0.97
  }
}
```

## 📋 Activation

```bash
@copilot Use the Cross-Agent Knowledge Graph to register fix pattern FP-012
@copilot Use the Cross-Agent Knowledge Graph to query "what fixes torch meta-tensor errors"
@copilot Use the Cross-Agent Knowledge Graph to export graph snapshot for S70
```

## 📝 Status

**Version**: 1.0.0 | **ID**: E-10 | **Created**: 2026-02-22
**AAIS Contribution**: +2.5 points | **Cognitive Level**: 4
**Fix Patterns Registered**: 11 (FP-001..FP-011, S52–S61)
