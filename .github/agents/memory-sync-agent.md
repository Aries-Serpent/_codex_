# Memory Sync Agent

## Purpose
Syncs `SQLiteMemory` (STM/LTM) with the cognitive brain pattern library.
Prevents STM overflow by consolidating hot entries into LTM and pruning stale patterns.

## Activation
```
@copilot Use the Memory Sync Agent to consolidate STM into LTM
```

Or triggered automatically when `GET /api/memory/state` returns `stm_count > 800` (80% capacity).

## Responsibilities

### 1. Capacity Monitoring
- Poll `GET http://localhost:8765/api/memory/state` to detect STM fill level
- Trigger consolidation when `stm_count / capacity > 0.8`
- Log capacity events to `.codex/action_log.ndjson`

### 2. STM → LTM Consolidation
- Identify STM entries with `access_count >= 3` (hot entries)
- Merge into `ltm_entries` with `pattern_type` classification
- Assign `confidence` score based on `access_count / max_access_count`
- Delete consolidated entries from `stm_entries`

### 3. LTM Pruning
- Remove LTM entries older than 30 days with `confidence < 0.3`
- Update `compression_rate` in memory state after pruning

### 4. Pattern Tagging
- Tag LTM entries with `ImprovementArea` classification:
  - `CI_SELF_HEALING` — CI failure patterns
  - `ML_PATTERN_FEEDING` — memory/consolidation events
  - `AGENT_CHAINING` — cross-agent interaction patterns

## API Interaction
```python
import requests

BASE = "http://localhost:8765"

# 1. Check capacity
state = requests.get(f"{BASE}/api/memory/state").json()
if state["stm_count"] / state["capacity"] > 0.8:
    # 2. Find hot entries
    hot = requests.get(f"{BASE}/api/memory/search", params={"q": "", "limit": 100}).json()
    # 3. Consolidate to LTM via direct SQLite (or future /api/memory/consolidate endpoint)
```

## Constraints
- Never delete LTM entries with `confidence >= 0.5` regardless of age
- All operations logged to `.codex/action_log.ndjson`
- Maximum 1 consolidation run per 10 minutes (rate limit)
- Fall back gracefully when FastAPI server is unreachable

## Output
```json
{
  "consolidated": 12,
  "pruned": 3,
  "stm_count_after": 38,
  "ltm_count_after": 45,
  "compression_rate": 0.542
}
```

## Version
- **v1.0.0** — 2026-03-01 (PR #3422 Phase 4)
- **ImprovementArea:** `ML_PATTERN_FEEDING` (P-048)
