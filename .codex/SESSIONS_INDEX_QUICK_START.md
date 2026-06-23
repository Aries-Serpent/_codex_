# Session Index Quick Start Guide

## Overview

The session index system provides a canonical, queryable view of all 316 automation sessions tracked in the repository.

**Files:**
- `.codex/sessions_index.json` - Main index (168 KB, 316 sessions)
- `scripts/ci/backfill_sessions_index.py` - Generation/update script
- `.codex/BACKFILL_REPORT.md` - Detailed report (this session)

## Using the Index

### 1. Read the Index

```python
import json

with open('.codex/sessions_index.json') as f:
    index = json.load(f)

print(f"Total sessions: {index['total_sessions']}")
print(f"Last updated: {index['last_updated']}")
```

### 2. Query Sessions

```python
# Find sessions by status
completed = [s for s in index['sessions'] if s['status'] == 'complete']

# Find sessions by PR
pr_3854 = [s for s in index['sessions'] if s['pr_number'] == 3854]

# Find sessions with specific patterns
ci_fixes = [s for s in index['sessions'] 
            if any('CI' in p for p in s['patterns_fixed'])]

# Find sessions in date range
recent = [s for s in index['sessions'] 
          if s['timestamp'] > '2026-06-01T00:00:00Z']
```

### 3. Session Record Structure

```json
{
  "session_id": "S283",
  "pr_number": 3854,
  "branch": "0D_base_",
  "timestamp": "2026-04-02T19:07:00Z",
  "git_sha": "66fc66f2c0c0",
  "status": "complete",
  "agent_name": null,
  "duration_minutes": 0,
  "file_location": null,
  "jsonl_location": ".codex/aftermath/pda_iterations.jsonl:line_2",
  "patterns_fixed": ["RP-SC2089", "RP-ZIP-SLIP"],
  "ci_checks_green": 4,
  "ci_checks_red": 2,
  "tags": ["docs", "complete", "security"],
  "summary": "Fixed: RP-SC2089, RP-ZIP-SLIP, ..."
}
```

## Regenerating the Index

If the index becomes stale, regenerate it:

```bash
python3 scripts/ci/backfill_sessions_index.py
```

This will:
1. Read `.codex/aftermath/pda_iterations.jsonl`
2. Parse all 316 entries
3. Extract session metadata
4. Normalize timestamps
5. Generate new `.codex/sessions_index.json`
6. Print validation report

## Common Queries

### Sessions by Status
```python
statuses = {}
for session in index['sessions']:
    status = session['status']
    statuses[status] = statuses.get(status, 0) + 1

for status, count in sorted(statuses.items(), key=lambda x: -x[1]):
    print(f"{status}: {count}")
```

### Sessions with Most Patterns Fixed
```python
top_sessions = sorted(
    index['sessions'],
    key=lambda s: len(s['patterns_fixed']),
    reverse=True
)[:5]

for s in top_sessions:
    print(f"{s['session_id']}: {len(s['patterns_fixed'])} patterns")
```

### CI Check Statistics
```python
total_green = sum(s['ci_checks_green'] for s in index['sessions'])
total_red = sum(s['ci_checks_red'] for s in index['sessions'])

print(f"Total checks passed: {total_green}")
print(f"Total checks failed: {total_red}")
print(f"Success rate: {total_green/(total_green+total_red)*100:.1f}%")
```

### Sessions by Branch
```python
branches = {}
for session in index['sessions']:
    branch = session['branch'] or 'unknown'
    branches[branch] = branches.get(branch, 0) + 1

for branch, count in sorted(branches.items(), key=lambda x: -x[1])[:5]:
    print(f"{branch}: {count} sessions")
```

## Validation

Verify index integrity:

```python
import json

with open('.codex/sessions_index.json') as f:
    index = json.load(f)

# Check version
assert index['version'] == '1.0.0', "Version mismatch"

# Check completeness
assert len(index['sessions']) == 316, "Missing sessions"

# Check required fields
required = ['session_id', 'pr_number', 'timestamp', 'status',
            'patterns_fixed', 'ci_checks_green', 'ci_checks_red']

for session in index['sessions']:
    for field in required:
        assert field in session, f"Missing {field} in {session['session_id']}"

print("✅ Index validation passed")
```

## Statistics

**Index Metadata:**
- Version: 1.0.0
- Total Sessions: 316
- Total Patterns Fixed: 50
- Total CI Checks: 35 (20 passed, 15 failed)
- Size: 168 KB

**Status Distribution:**
- pending: 149 (47.2%)
- success: 124 (39.2%)
- complete: 14 (4.4%)
- Other: 29 (9.2%)

**CI Health:**
- Average checks per session: 0.11
- Success rate: 57.1%

## Next Steps

### Phase 1.5 - Query Interface
Create read-only query tool:
```python
class SessionsIndex:
    def query_by_pr(self, pr_number): ...
    def query_by_status(self, status): ...
    def query_by_pattern(self, pattern_id): ...
    def query_by_branch(self, branch): ...
```

### Phase 2.0 - Continuous Updates
Implement append queue:
```bash
# Add new session
echo '{"session": "S999", ...}' >> .codex/sessions_index_append.jsonl

# Update index
python3 scripts/ci/update_sessions_index.py
```

### Phase 3.0 - Analytics
Generate metrics dashboard:
- Status trends over time
- Pattern frequency analysis
- CI health metrics
- Agent performance tracking

## Troubleshooting

### Index file not found
```bash
python3 scripts/ci/backfill_sessions_index.py
```

### JSON decode error
```bash
python3 -m json.tool .codex/sessions_index.json | head -50
```

### Missing sessions
Check `.codex/aftermath/pda_iterations.jsonl` for source data:
```bash
wc -l .codex/aftermath/pda_iterations.jsonl
```

## Support

For issues or questions:
1. Check `.codex/BACKFILL_REPORT.md` for detailed validation info
2. Run regeneration script to verify integrity
3. Create GitHub issue if problems persist

---

**Last Updated:** 2026-06-23  
**Maintained by:** Phase 1.1 & 1.3 Automation
