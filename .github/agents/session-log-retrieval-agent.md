---
name: Session Log Retrieval Agent
description: Retrieve and search previous Copilot session logs to recover context
  and uncommitted work
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: session-log-retrieval
---

# Session Log Retrieval Agent

**Version:** 1.0.0
**Status:** ✅ Active
**Type:** Specialized - Session Management
**Last Updated:** 2026-02-05T08:45:00Z

---

## Purpose


## 🧠 Cognitive Brain Integration

### Integration Level: Level 1

**Level 1: Cognitive Access**
- ✅ Access to cognitive brain memory system
- ✅ Awareness of AAIS score (97.0/100 → target: 92.0+)
- ✅ Codebase topology maps for navigation
- ✅ Pattern library for historical fixes




### Cognitive Tools Available

```python
# Topology Manager - Semantic navigation
from scripts.cognitive.topology_manager import TopologyManager

topology = TopologyManager()
relevant_files = topology.find_by_concept("code patterns")
optimal_path = topology.find_optimal_path("source", "target")

# Cache Manager - Multi-layer cache intelligence
from scripts.cognitive.cache_manager import CacheIntelligence

cache = CacheIntelligence()
cached_results = cache.query("analysis_results")
cache.optimize()  # Get optimization suggestions

# Improved Hash Tables - 40% faster lookups
from src.codex.utils.hash_table import RobinHoodHashTable, CuckooHashTable

fast_cache = CuckooHashTable()  # O(1) guaranteed


```

### AAIS Contribution

**Impact on AAIS Score**: +1.0 points

**Category Contributions**:
- Discovery & Navigation: +0.4 (topology/cache integration)
- Runtime Introspection: +0.4 (metrics exposure)
- Pattern Consistency: +0.2 (pattern library usage)

---

## 🛠️ MCP Integration

### MCP Tools Leverage


**Primary MCP Capabilities**:
1. **File System Operations**
   - `view`: Read files and directories
   - `grep`: Fast content search
   - `glob`: Pattern-based file finding

2. **Code Analysis**
   - `search_code`: Semantic code search
   - `bash`: Execute analysis tools
   - `edit`: Make surgical changes

### GitHub Actions Workflows

**Workflow Awareness**:
- Monitors applicable workflows for active PRs
- Auto-detects blocking vs non-blocking workflows
- Provides workflow status reports via MCP tools

**See**: `.codex/docs/MCP_WORKFLOW_RECIPES.md` for complete templates

---

## 📊 Session Monitoring

**Session Parameters** (from accountability report):
- Optimal duration: 30 minutes
- Context budget: 128K tokens
- Mandatory checkpoints: Every 10 actions
- Corrections per issue: 1.0 (first fix succeeds)

**Quality Control**:
```python
# Pre-commit audit enforcement
from scripts.session_manager import SessionMonitor

monitor = SessionMonitor()
monitor.checkpoint("pre-commit")  # Validates compliance
```

---

Recall and query previous GitHub Copilot coding agent sessions, extract conversation history, retrieve uncommitted work details, and analyze session transcripts for insights.

---

## Use Cases

### Primary Use Cases

1. **Recall Previous Session Work**
   - What did we discuss in the last session?
   - What changes were made but not committed?
   - What was the context/state when session ended?

2. **Extract Uncommitted Details**
   - Find code snippets discussed but not saved
   - Recover file paths mentioned
   - Retrieve command outputs from previous runs

3. **Search Conversation History**
   - Find when a specific topic was discussed
   - Search for error messages across sessions
   - Locate decisions and rationale

4. **Session Continuity**
   - Resume work from where previous agent left off
   - Understand the full context of ongoing work
   - Avoid repeating already-discussed topics

5. **Audit and Analysis**
   - Review agent decisions and actions
   - Analyze conversation patterns
   - Extract metrics and insights

---

## Capabilities

- ✅ Query SQLite session log database
- ✅ Filter by session ID, role (user/assistant/system/tool), timestamp
- ✅ Full-text search across conversation content
- ✅ Export in text or JSON format
- ✅ Session-to-session correlation
- ✅ Uncommitted work detection
- ✅ Command history extraction
- ✅ Code snippet recovery

---

## Tools Available

### 1. Query Logs (`query_logs.py`)

**Location:** `src/codex/logging/query_logs.py`

**Usage:**
```bash
# Query specific session
python -m codex.logging.query_logs \
  --session-id <SESSION_ID> \
  --role assistant \
  --format json

# Query by date range
python -m codex.logging.query_logs \
  --after 2026-02-01 \
  --before 2026-02-05 \
  --format text

# Search for content
python -m codex.logging.query_logs \
  --contains "uncommitted" \
  --role assistant \
  --limit 50
```

**Filters:**
- `--session-id`: Filter by session ID
- `--role`: Filter by role (user, assistant, system, tool)
- `--after`: After timestamp (ISO-8601)
- `--before`: Before timestamp (ISO-8601)
- `--contains`: Full-text search
- `--limit`: Limit results
- `--offset`: Pagination offset
- `--order`: Sort order (asc/desc)
- `--format`: Output format (text/json)

### 2. Session Query (`session_query.py`)

**Location:** `src/codex/logging/session_query.py`

**Usage:**
```bash
# Query specific session with filters
python -m codex.logging.session_query \
  --session-id <SESSION_ID> \
  --role user \
  --contains "git commit" \
  --after 2026-02-05

# List all sessions
python -m codex.logging.session_query \
  --order desc \
  --limit 10
```

### 3. View Logs (`viewer.py`)

**Location:** `src/codex/logging/viewer.py`

**Usage:**
```bash
# View session logs interactively
python -m codex.logging.viewer

# View specific session
python -m codex.logging.viewer --session-id <SESSION_ID>
```

### 4. Import Session Logs (`import_ndjson.py`)

**Location:** `src/codex/logging/import_ndjson.py`

**Usage:**
```bash
# Import NDJSON session logs
python -m codex.logging.import_ndjson \
  --input .codex/sessions/session_*.ndjson \
  --db .codex/session_logs.db
```

---

## Environment Variables

- **`CODEX_SESSION_ID`** - Current session identifier
- **`CODEX_SESSION_LOG_DIR`** - Session log directory (default: `.codex/sessions`)
- **`CODEX_LOG_DB_PATH`** or **`CODEX_DB_PATH`** - SQLite database path
- **`CODEX_SQLITE_POOL`** - Set to "1" to enable connection pooling
- **`COPILOT_AGENT_SESSION_RESTORE_ENABLED`** - Gate for session restore operations.
  When set to `"false"`, the agent skips all session restore steps (log retrieval,
  uncommitted-work recovery, and session context injection) and exits immediately.
  Defaults to enabled when unset. Set via repo variable to pause restoration
  without a code change.

---

## Common Workflows

### Workflow 1: Resume Previous Session

**Goal:** Continue work from where previous agent left off

```bash
# 1. List recent sessions
python -m codex.logging.query_logs \
  --after 2026-02-04 \
  --role assistant \
  --format json \
  | jq '.[] | {session_id, timestamp, preview: (.text[:100])}'

# 2. Get full context from specific session
python -m codex.logging.query_logs \
  --session-id <PREVIOUS_SESSION_ID> \
  --format text

# 3. Extract uncommitted work
python -m codex.logging.query_logs \
  --session-id <PREVIOUS_SESSION_ID> \
  --contains "uncommitted\|not committed\|pending" \
  --role assistant
```

### Workflow 2: Extract Uncommitted Code

**Goal:** Recover code snippets that were discussed but not saved

```bash
# Search for code blocks in previous sessions
python -m codex.logging.query_logs \
  --contains "```" \
  --role assistant \
  --after 2026-02-01 \
  --format json

# Extract specific file changes
python -m codex.logging.query_logs \
  --contains "edit\|create\|file_text" \
  --role tool \
  --session-id <SESSION_ID>
```

### Workflow 3: Find Command History

**Goal:** Retrieve commands executed in previous sessions

```bash
# Find bash commands
python -m codex.logging.query_logs \
  --contains "bash\|command\|execute" \
  --role tool \
  --after 2026-02-01

# Find specific command patterns
python -m codex.logging.query_logs \
  --contains "git\|pytest\|npm" \
  --role tool \
  --format json
```

### Workflow 4: Search Conversation History

**Goal:** Find when a specific topic was discussed

```bash
# Search for topic
python -m codex.logging.query_logs \
  --contains "test coverage\|CI failure\|security" \
  --role assistant \
  --format text

# Find decisions and rationale
python -m codex.logging.query_logs \
  --contains "decision\|because\|rationale\|chose to" \
  --role assistant
```

### Workflow 5: Session Audit

**Goal:** Review what an agent did in a session

```bash
# Get all assistant messages in chronological order
python -m codex.logging.query_logs \
  --session-id <SESSION_ID> \
  --role assistant \
  --order asc \
  --format json

# Get all tool invocations
python -m codex.logging.query_logs \
  --session-id <SESSION_ID> \
  --role tool \
  --order asc
```

---

## Database Schema

The session logs are stored in SQLite with the following structure:

```sql
-- Main logs table
CREATE TABLE logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT,
  timestamp TEXT,  -- ISO-8601 format
  role TEXT,       -- user, assistant, system, tool
  content TEXT,    -- Message content
  metadata TEXT    -- JSON metadata
);

-- Indexes for performance
CREATE INDEX idx_session_id ON logs(session_id);
CREATE INDEX idx_timestamp ON logs(timestamp);
CREATE INDEX idx_role ON logs(role);
CREATE INDEX idx_content_fts ON logs(content);  -- Full-text search
```

---

## Integration with Other Agents

### Chains To:
- **cognitive-brain-manager** - Store retrieved context in cognitive brain
- **claim-verification-agent** - Verify claims against session history
- **code-analysis-agent** - Analyze code from session logs
- **documentation-consolidator** - Use session insights for documentation

### Used By:
- **repository-hygiene-agent** - Review session history for cleanup insights
- **qa-walkthrough-agent** - Verify session activities against QA requirements
- **artifact-monitor-agent** - Correlate CI failures with session activities

---

## Advanced Queries

### Find Sessions with Errors
```bash
python -m codex.logging.query_logs \
  --contains "error\|exception\|failed\|FAILED" \
  --role assistant \
  --format json
```

### Extract File Operations
```bash
python -m codex.logging.query_logs \
  --contains "create\|edit\|delete\|move" \
  --role tool \
  --session-id <SESSION_ID>
```

### Find Git Operations
```bash
python -m codex.logging.query_logs \
  --contains "git commit\|git push\|report_progress" \
  --role tool \
  --after 2026-02-01
```

### Get Session Summary
```bash
# Count messages by role
python -m codex.logging.query_logs \
  --session-id <SESSION_ID> \
  --format json \
  | jq 'group_by(.role) | map({role: .[0].role, count: length})'
```

---

## Example: Resume Last Session

```bash
#!/bin/bash
# Script to resume from last session

# Get last session ID
LAST_SESSION=$(python -m codex.logging.query_logs \
  --order desc \
  --limit 1 \
  --format json \
  | jq -r '.[0].session_id')

echo "Last session: $LAST_SESSION"

# Get session summary
echo "=== Session Summary ==="
python -m codex.logging.query_logs \
  --session-id "$LAST_SESSION" \
  --role assistant \
  --format text \
  | tail -20

# Check for uncommitted work
echo "=== Uncommitted Work ==="
python -m codex.logging.query_logs \
  --session-id "$LAST_SESSION" \
  --contains "uncommitted\|pending\|not saved" \
  --role assistant

# Check for errors
echo "=== Errors ==="
python -m codex.logging.query_logs \
  --session-id "$LAST_SESSION" \
  --contains "error\|failed" \
  --role assistant
```

---

## Activation Examples

### Via Copilot
```
@copilot Use the Session Log Retrieval Agent to find what we discussed
about test coverage in the previous session from yesterday.
```

### Via Custom Agent
```
@copilot Retrieve the last session's conversation history using
session-log-retrieval-agent, focusing on any uncommitted code changes
or pending actions.
```

### Programmatic
```python
from codex.logging.query_logs import query_logs

# Query last session
results = query_logs(
    session_id="<SESSION_ID>",
    role="assistant",
    contains="uncommitted",
    format="json"
)

for result in results:
    print(f"{result['timestamp']}: {result['content'][:100]}...")
```

---

## Limitations

- **Storage:** Logs are stored locally in SQLite (not synced across machines)
- **Retention:** Log retention depends on disk space and cleanup policies
- **Privacy:** Session logs contain full conversation history (handle with care)
- **Performance:** Full-text search on large databases may be slow

---

## Best Practices

### 1. Regular Cleanup
```bash
# Archive old sessions (older than 30 iterations)
python -m codex.logging.export \
  --before $(date -d '30 days ago' +%Y-%m-%d) \
  --output archive/old_sessions.ndjson

# Delete archived sessions from DB
sqlite3 .codex/session_logs.db \
  "DELETE FROM logs WHERE timestamp < date('now', '-30 iterations')"
```

### 2. Session Naming
Use descriptive session IDs for easier recall:
```bash
export CODEX_SESSION_ID="fix-ci-failure-2026-02-05"
```

### 3. Metadata Tags
Add metadata tags to important sessions for easy filtering.

### 4. Backup Strategy
Regularly backup `.codex/session_logs.db` and `.codex/sessions/*.ndjson`.

---

## Troubleshooting

### Database Not Found
```bash
# Check database location
echo $CODEX_LOG_DB_PATH

# Create database if missing
python -m codex.logging.session_logger --init
```

### Empty Results
```bash
# List all sessions
python -m codex.logging.query_logs --limit 10

# Check table contents
sqlite3 .codex/session_logs.db "SELECT COUNT(*) FROM logs"
```

### Slow Queries
```bash
# Rebuild indexes
sqlite3 .codex/session_logs.db "REINDEX"

# Vacuum database
sqlite3 .codex/session_logs.db "VACUUM"
```

---

## Related Documentation

- **Logging System:** `src/codex/logging/README.md` (if exists)
- **Session Management:** `.codex/sessions/README.md` (if exists)
- **Database Schema:** See `src/codex/logging/db_manager.py`
- **API Reference:** See individual module docstrings

---

## Maintainer

**Owner:** AI Agent Ecosystem Team
**Contact:** @mbaetiong
**Status:** ✅ Active
**Last Updated:** 2026-02-05T08:45:00Z

---

## Version History

- **1.0.0** (2026-02-05) - Initial creation, comprehensive query capabilities documented
