# Phase 1: Session Tracking Guide

**For:** AI Agents & Developers  
**Version:** 1.0  
**Status:** Active  

---

## Quick Start

### For Agents (Python API)

**Goal:** Fetch recent sessions and analyze patterns

```python
from codex.logging.session_query import resolve_db_path, fetch_rows
import sqlite3

# Initialize
db = resolve_db_path(None)  # Auto-detects from env
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Fetch last 10 events from a specific session
rows, cols = fetch_rows(db, session_id="S228", last_n=10, desc=True)

# Process results
for row in rows:
    print(f"{row[cols['timestamp']]}: {row[cols['message']]}")
```

### For Developers (CLI)

**Goal:** Query session logs from the terminal

```bash
# Show last 5 events from session S228
python -m codex.logging.session_query --session-id S228 --last 5

# Show in descending order (newest first)
python -m codex.logging.session_query --session-id S228 --last 5 --desc

# Specify database location
python -m codex.logging.session_query --db .codex/session_logs.db --session-id S228
```

---

## Querying Sessions

### Method 1: Direct Index Query (Recommended)

**File:** `.codex/sessions_index.json`

```python
import json
from pathlib import Path

# Load the index
index_path = Path(".codex/sessions_index.json")
with open(index_path) as f:
    data = json.load(f)

# Get all sessions
sessions = data["sessions"]

# Find a specific session
session_228 = next(s for s in sessions if s["session_id"] == "S228")
print(f"PR: {session_228['pr_number']}")
print(f"Status: {session_228['status']}")
print(f"Patterns: {session_228['patterns_fixed']}")

# Filter by status
completed = [s for s in sessions if s["status"] == "complete"]
print(f"Found {len(completed)} completed sessions")

# Filter by tag
security_sessions = [s for s in sessions if "security" in s["tags"]]
print(f"Found {len(security_sessions)} security sessions")

# Sort by timestamp (descending)
recent = sorted(sessions, key=lambda s: s["timestamp"], reverse=True)
for session in recent[:5]:
    print(f"{session['session_id']}: {session['summary']}")
```

### Method 2: Database Query (Advanced)

**Location:** `.codex/session_logs.db`

```python
import sqlite3
from codex.logging.session_query import resolve_db_path, detect_schema

# Connect to database
db = resolve_db_path(None)
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Auto-detect schema
table, cols = detect_schema(conn)

# Manual SQL query
cur = conn.cursor()
sql = f"""
    SELECT {cols['timestamp']}, {cols['message']}
    FROM {table}
    WHERE {cols.get('session_id', 'session_id')} = ?
    ORDER BY {cols['timestamp']} DESC
    LIMIT 10
"""
rows = cur.execute(sql, ["S228"]).fetchall()

# Process results
for row in rows:
    print(f"{row[cols['timestamp']]}: {row[cols['message']]}")

conn.close()
```

### Method 3: CLI Query

```bash
# Setup environment (one-time)
export CODEX_LOG_DB_PATH=".codex/session_logs.db"

# Query a session
python -m codex.logging.session_query --session-id S228 --last 20

# Output format: Tab-separated columns
# timestamp    session_id    role    message
# 2026-03-29T22:19:00Z    S228    user    Starting session...
# 2026-03-29T22:20:00Z    S228    assistant    I'll help with...
```

---

## Common Use Cases

### Use Case 1: Find Sessions with Specific Pattern Fixed

```python
import json
from pathlib import Path

index = json.loads(Path(".codex/sessions_index.json").read_text())
sessions = index["sessions"]

# Find all sessions that fixed pattern RP-SC2089
sessions_with_pattern = [
    s for s in sessions 
    if "RP-SC2089" in s["patterns_fixed"]
]

for session in sessions_with_pattern:
    print(f"{session['session_id']}: {session['summary']}")
```

**Output:**
```
S283: Fixed: RP-SC2089, RP-ZIP-SLIP, RP-REPO-ROOT-ORDER, +1 more
S401: Fixed: RP-SC2089 security vulnerability
```

### Use Case 2: Analyze Recent Session Activity

```python
import json
from pathlib import Path
from datetime import datetime, timedelta

index = json.loads(Path(".codex/sessions_index.json").read_text())
sessions = index["sessions"]

# Sessions from the last 7 days
cutoff = datetime.utcnow() - timedelta(days=7)
recent = [
    s for s in sessions 
    if datetime.fromisoformat(s["timestamp"].replace("Z", "+00:00")) > cutoff
]

# Statistics
total = len(recent)
complete = sum(1 for s in recent if s["status"] == "complete")
failed = sum(1 for s in recent if s["status"] == "failed")
total_patterns_fixed = sum(len(s["patterns_fixed"]) for s in recent)

print(f"Last 7 days: {total} sessions")
print(f"  Complete: {complete}")
print(f"  Failed: {failed}")
print(f"  Patterns fixed: {total_patterns_fixed}")
```

### Use Case 3: Find Sessions by PR Number

```python
import json
from pathlib import Path

index = json.loads(Path(".codex/sessions_index.json").read_text())
sessions = index["sessions"]

# Find all sessions for PR #3854
pr_sessions = [s for s in sessions if s["pr_number"] == 3854]

print(f"Found {len(pr_sessions)} sessions for PR #3854")
for session in pr_sessions:
    print(f"  {session['session_id']}: {session['status']}")
    print(f"    Branch: {session['branch']}")
    print(f"    SHA: {session['git_sha']}")
    print(f"    Patterns: {', '.join(session['patterns_fixed'])}")
```

### Use Case 4: Track CI Status by Session

```python
import json
from pathlib import Path

index = json.loads(Path(".codex/sessions_index.json").read_text())
sessions = index["sessions"]

# Find sessions with CI failures
failing = [
    s for s in sessions 
    if s["ci_checks_red"] > 0
]

# Group by pattern
by_pattern = {}
for session in failing:
    for pattern in session["patterns_fixed"]:
        by_pattern.setdefault(pattern, []).append(session["session_id"])

# Report
for pattern, session_ids in sorted(by_pattern.items()):
    print(f"{pattern}: {len(session_ids)} sessions")
    print(f"  Sessions: {', '.join(session_ids)}")
```

---

## Output Formats

### JSON (Python)

```python
import json
from pathlib import Path

# Load index
index = json.loads(Path(".codex/sessions_index.json").read_text())

# Pretty print
print(json.dumps(index, indent=2))

# Write to file
with open("sessions_export.json", "w") as f:
    json.dump(index, f, indent=2)
```

### CSV (Python)

```python
import csv
import json
from pathlib import Path

index = json.loads(Path(".codex/sessions_index.json").read_text())

# Write CSV
with open("sessions.csv", "w", newline="") as f:
    writer = csv.writer(f)
    
    # Header
    headers = [
        "session_id", "pr_number", "timestamp", "status",
        "patterns_fixed", "ci_green", "ci_red", "summary"
    ]
    writer.writerow(headers)
    
    # Rows
    for session in index["sessions"]:
        writer.writerow([
            session["session_id"],
            session["pr_number"],
            session["timestamp"],
            session["status"],
            ";".join(session["patterns_fixed"]),
            session["ci_checks_green"],
            session["ci_checks_red"],
            session["summary"]
        ])

print("Exported to sessions.csv")
```

### Tab-Separated (CLI)

```bash
# Query from CLI
python -m codex.logging.session_query --session-id S228 --last 20 > session_events.tsv

# Format: timestamp, session_id, role, message
# Can be imported into Excel/Sheets
```

---

## Performance Characteristics

### Phase 1 (Current)

| Operation | Complexity | Time | Notes |
|-----------|-----------|------|-------|
| Load index | O(1) | <10ms | Index is small (171 KB) |
| Find session by ID | O(n) | 1-5ms | Linear scan, small dataset |
| Filter by status | O(n) | 1-10ms | Full scan needed |
| Filter by tag | O(n) | 1-10ms | Full scan needed |
| Get last N sessions | O(n) | 1-10ms | Filter + sort |

### Phase 2 (Optimized)

| Operation | Complexity | Time | Expected |
|-----------|-----------|------|----------|
| Find session by ID | O(log n) | <1ms | B-tree index |
| Filter by status | O(log n) | <1ms | Indexed column |
| Filter by tag | O(k log n) | 1-2ms | Tag index |
| Full-text search | O(k) | 5-50ms | FTS5 index |

**Legend:** n = total sessions, k = matching results

---

## Integration Points

### For Cognitive Brain Session Injector

```python
# In scripts/cognitive/session_manager.py
import json
from pathlib import Path

class CognitiveBrainSessionManager:
    def get_recent_sessions(self, limit=10):
        """Query recent sessions using Phase 1 index."""
        index = json.loads(Path(".codex/sessions_index.json").read_text())
        sessions = index["sessions"]
        
        # Sort by timestamp descending and return last N
        return sorted(
            sessions,
            key=lambda s: s["timestamp"],
            reverse=True
        )[:limit]
    
    def find_sessions_by_pattern(self, pattern_id):
        """Find all sessions that fixed a pattern."""
        index = json.loads(Path(".codex/sessions_index.json").read_text())
        sessions = index["sessions"]
        
        return [
            s for s in sessions 
            if pattern_id in s["patterns_fixed"]
        ]
```

### For Agent Orchestrator

```python
# Route agents based on session history
def select_agent_for_task(task):
    """Select best agent based on similar past sessions."""
    import json
    from pathlib import Path
    
    index = json.loads(Path(".codex/sessions_index.json").read_text())
    sessions = index["sessions"]
    
    # Find sessions with similar patterns
    similar = [
        s for s in sessions
        if any(p in task.patterns for p in s["patterns_fixed"])
    ]
    
    # If most similar sessions succeeded, use same agent
    # Otherwise, try a different agent
    success_rate = sum(1 for s in similar if s["status"] == "complete") / len(similar) if similar else 0
    
    return select_best_agent(task, success_rate)
```

---

## Troubleshooting

### Issue: Import Error

```python
>>> from codex.logging.session_query import fetch_rows
ModuleNotFoundError: No module named 'codex'
```

**Solution:**
```bash
# Install package in development mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Issue: Database Not Found

```python
>>> resolve_db_path(None)
FileNotFoundError: No database found. Provide --db or set CODEX_DB_PATH
```

**Solution:**
```python
# Explicitly specify database path
db = ".codex/session_logs.db"
rows = fetch_rows(db, session_id="S228", last_n=10, desc=True)

# Or set environment variable
import os
os.environ["CODEX_LOG_DB_PATH"] = ".codex/session_logs.db"
```

### Issue: No Results Returned

**Check:**
1. Session ID is correct: `grep -o '"session_id":"S228"' .codex/sessions_index.json`
2. Database has events: `sqlite3 .codex/session_logs.db "SELECT COUNT(*) FROM events;"`
3. Schema matches: `python -m codex.logging.session_query --db <path> --session-id S228`

---

## Examples Repository

See complete working examples in:

- `tests/logging/test_session_query.py` - Unit tests
- `scripts/ci/validate_phase1_checkpoint.py` - Validation script
- `scripts/cognitive/session_manager.py` - Session manager integration

---

## Next Steps

**Phase 2 (June 2026):**
- Index optimization (B-tree)
- Tag-based filtering
- Time-range queries
- Full-text search

**Phase 3 (July 2026):**
- REST API
- GraphQL interface
- Real-time subscriptions

**Phase 4 (August 2026):**
- ML model training on sessions
- Predictive pattern detection
- Session replay debugging

---

## References

- **Schema:** `.codex/PHASE_1_SESSION_INDEX_ARCHITECTURE.md`
- **API:** `src/codex/logging/session_query.py`
- **Index:** `.codex/sessions_index.json`
- **Validation:** `scripts/ci/validate_phase1_checkpoint.py`

