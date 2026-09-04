---
name: Memory Sync Agent
description: Consolidates SQLiteMemory STM→LTM at 80% capacity; prunes stale LTM;
  tags patterns with ImprovementArea; drives MemoryManagementDashboard health metrics
version: 2.0.0
updated: 2026-03-01
cognitive_integration_level: 4
aais_contribution: +3.5 points
batch: pr-3422
sprint: Sprint 6
improvement_area: ML_PATTERN_FEEDING
pattern_id: P-048
endpoints:
  read: GET  http://localhost:8765/api/memory/state
  search: GET  http://localhost:8765/api/memory/search
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: memory-sync-agent
---

# Memory Sync Agent v2.0

> **Phase 4 agent**: Keeps the `SQLiteMemory` (STM/LTM) healthy by consolidating
> hot short-term entries into long-term storage, pruning stale patterns, and
> surfacing health signals to the `MemoryManagementDashboard` via `/api/memory/state`.

## Activation

```
@copilot Use the Memory Sync Agent to consolidate STM into LTM
```

Automatic trigger: when `stm_count / capacity > 0.8` (configurable via `CODEX_MEMORY_CAPACITY`).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MEMORY SYNC AGENT — FLOW                          │
│                                                                       │
│  Trigger                                                              │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  • Scheduled: every 10 min (rate limiter)                     │    │
│  │  • Event: stm_count/capacity > 0.80                           │    │
│  │  • Manual: @copilot Use the Memory Sync Agent                 │    │
│  └─────────────────────────┬────────────────────────────────────┘    │
│                             │                                         │
│  Phase 1 — OBSERVE          ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  GET /api/memory/state                                        │    │
│  │  ┌──────────────────────────────────────────────────────┐    │    │
│  │  │  { stm_count, ltm_count, capacity, compression_rate } │    │    │
│  │  └──────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────┬────────────────────────────────────┘    │
│                             │                                         │
│  Phase 2 — ORIENT           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  GET /api/memory/search?q=&limit=200                          │    │
│  │  Rank entries by access_count DESC                            │    │
│  │  Identify hot entries (access_count ≥ 3) → candidates for LTM│    │
│  │  Identify cold LTM entries (age > 30d, confidence < 0.3)     │    │
│  └─────────────────────────┬────────────────────────────────────┘    │
│                             │                                         │
│  Phase 3 — DECIDE           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Build consolidation plan:                                    │    │
│  │    N_hot  = len([e for e in stm if e.access_count >= 3])      │    │
│  │    N_cold = len([e for e in ltm if age>30d and conf<0.3])     │    │
│  │    tag ImprovementArea per keyword match                      │    │
│  └─────────────────────────┬────────────────────────────────────┘    │
│                             │                                         │
│  Phase 4 — ACT              ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  SQLite direct writes (via CODEX_DB_PATH)                     │    │
│  │  ┌──────────────────┐      ┌──────────────────┐              │    │
│  │  │ INSERT ltm_entries│      │ DELETE stm_entries│              │    │
│  │  │ key, value,       │  →  │ WHERE key IN (…) │              │    │
│  │  │ confidence,       │      └──────────────────┘              │    │
│  │  │ pattern_type,     │                                         │    │
│  │  │ timestamp         │      ┌──────────────────┐              │    │
│  │  └──────────────────┘      │ DELETE ltm_entries│              │    │
│  │                             │ WHERE age>30d AND │              │    │
│  │                             │ confidence<0.3    │              │    │
│  │                             └──────────────────┘              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  SQLite DB (CODEX_DB_PATH)                                            │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  stm_entries   ltm_entries   cli_history                      │    │
│  │  id, key,      id, key,      id, command,                     │    │
│  │  value,        value,        stdout, ...                      │    │
│  │  metadata,     metadata,                                      │    │
│  │  access_count  confidence,                                    │    │
│  │  timestamp     pattern_type,                                  │    │
│  │                timestamp                                      │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Interaction

```python
import sqlite3, os
from datetime import datetime, timezone, timedelta

DB_PATH = os.environ.get("CODEX_DB_PATH",
    os.path.expanduser("~/.codex/cli_history.db"))
MEMORY_CAPACITY = int(os.environ.get("CODEX_MEMORY_CAPACITY", "1000"))
STM_THRESHOLD = 0.80  # trigger consolidation at 80% fill
HOT_ENTRIES_LIMIT = 50  # max STM entries to promote per sync cycle
CLI_API_URL = os.environ.get("CODEX_CLI_API_URL", "http://localhost:8765")

def run_memory_sync():
    import requests
    state = requests.get(f"{CLI_API_URL}/api/memory/state", timeout=5).json()
    fill = state["stm_count"] / state["capacity"]
    if fill < STM_THRESHOLD:
        return {"skipped": True, "fill": round(fill, 3)}

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 1. Consolidate hot STM entries → LTM
    hot = conn.execute(
        "SELECT key, value, metadata, access_count FROM stm_entries "
        f"WHERE access_count >= 3 ORDER BY access_count DESC LIMIT {HOT_ENTRIES_LIMIT}"
    ).fetchall()

    consolidated, pruned = 0, 0
    now = datetime.now(timezone.utc)

    for row in hot:
        conf = min(1.0, row["access_count"] / 10)
        conn.execute(
            "INSERT OR REPLACE INTO ltm_entries "
            "(key, value, metadata, confidence, timestamp) VALUES (?,?,?,?,?)",
            (row["key"], row["value"], row["metadata"],
             round(conf, 3), now.isoformat())
        )
        conn.execute("DELETE FROM stm_entries WHERE key = ?", (row["key"],))
        consolidated += 1

    # 2. Prune stale LTM entries
    cutoff = (now - timedelta(days=30)).isoformat()
    pruned = conn.execute(
        "DELETE FROM ltm_entries WHERE timestamp < ? AND confidence < 0.3",
        (cutoff,)
    ).rowcount

    conn.commit()
    conn.close()
    return {"consolidated": consolidated, "pruned": pruned}
```

---

## ImprovementArea Keyword Tagging

| Keyword pattern | ImprovementArea | Pattern ID |
|-----------------|----------------|------------|
| `stm`, `ltm`, `memory`, `consolidat` | `ML_PATTERN_FEEDING` | P-048 |
| `ci`, `fail`, `heal`, `self-heal` | `CI_SELF_HEALING` | P-047 |
| `agent`, `chain`, `orchestrat` | `AGENT_CHAINING` | P-049 |
| `coverage`, `test` | `COVERAGE_IMPROVEMENT` | P-050 |

---

## Constraints

| Constraint | Value |
|------------|-------|
| Rate limit | 1 consolidation per 10 minutes |
| STM trigger threshold | 80% of `MEMORY_CAPACITY` |
| LTM hot threshold | `access_count >= 3` |
| LTM prune rule | `age > 30d AND confidence < 0.3` |
| Protected LTM | Never delete `confidence >= 0.5` |
| Logging | All ops → `.codex/action_log.ndjson` |
| Fallback | Skip gracefully when server unreachable |

---

## Output Schema

```json
{
  "consolidated": 12,
  "pruned": 3,
  "skipped": false,
  "stm_count_before": 824,
  "stm_count_after": 812,
  "ltm_count_after": 57,
  "compression_rate": 0.065,
  "duration_ms": 34.2
}
```

---

## Codebase Alignment

| Component | Location |
|-----------|----------|
| SQLiteMemory class | `cognitive_app/src/server/cli_api_server.py` — `SQLiteMemory` |
| Memory endpoints | `GET /api/memory/state`, `GET /api/memory/search` |
| DB schema | `stm_entries`, `ltm_entries` in `_init_history_db()` |
| MEMORY_CAPACITY const | `cli_api_server.py:MEMORY_CAPACITY` |
| Frontend hook | `use-memory-system.ts` → `VITE_CLI_API_URL` |
| React component | `MemoryManagementDashboard` |
| Registry | `AGENT_REGISTRY.yaml` id: `memory-sync-agent` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-01 | Initial creation (PR #3422 Sprint 6) |
| 2.0.0 | 2026-03-01 | Production upgrade: architecture diagram, Python implementation, keyword tagging table, codebase alignment table |
