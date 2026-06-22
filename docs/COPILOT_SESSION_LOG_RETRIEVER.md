# Copilot Session Log Retriever

**Last Updated:** 2026-06-22

## Overview

The Copilot Session Log Retriever is a comprehensive system for retrieving, analyzing, and verifying Copilot coding agent session logs. It helps ensure that all expected files from previous sessions have been correctly implemented.

## Features

- **Batch Retrieval**: Retrieve the last N Copilot sessions in configurable batches
- **File Verification**: Automatically detect and verify expected file operations
- **Comprehensive Reports**: Generate detailed markdown reports of verification results
- **Flexible Querying**: Query by session ID, time range, or retrieve latest sessions
- **Missing File Detection**: Identify files that should exist but are missing

## Installation

The system is part of the `_codex_` repository. No additional installation required.

## Usage

### Command Line Interface

#### List Available Sessions

```bash
python scripts/copilot_session_log_retriever.py --list-sessions
```

#### Retrieve and Verify Last 20 Sessions

```bash
python scripts/copilot_session_log_retriever.py --last 20 --batch-size 5
```

This processes the last 20 sessions in batches of 5, verifying all expected files.

#### Analyze Specific Session

```bash
python scripts/copilot_session_log_retriever.py --session-id <SESSION_ID>
```

#### Generate Report to File

```bash
python scripts/copilot_session_log_retriever.py \
    --last 20 \
    --batch-size 3 \
    --output .codex/session_verification_report.md
```

#### Verbose Output

```bash
python scripts/copilot_session_log_retriever.py --last 10 --verbose
```

### Python API

```python
from scripts.copilot_session_log_retriever import CopilotSessionRetriever

# Initialize retriever
retriever = CopilotSessionRetriever(
    db_path=".codex/session_logs.db",
    repo_root="/path/to/repo"
)

# List available sessions
sessions = retriever.list_sessions(limit=50)
print(f"Found {len(sessions)} sessions")

# Get last 20 session IDs
session_ids = retriever.get_last_n_sessions(n=20)

# Process in batches
summaries = retriever.process_sessions_in_batches(
    session_ids,
    batch_size=5
)

# Generate report
report = retriever.generate_report(
    summaries,
    output_path=".codex/verification_report.md"
)
print(report)
```

## Configuration

### Environment Variables

- `CODEX_LOG_DB_PATH`: Override default database path (default: `.codex/session_logs.db`)
- `CODEX_SQLITE_POOL`: Enable connection pooling (set to `"1"`)

### Database Schema

The system expects a SQLite database with the following schema:

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL,
    message TEXT,
    metadata TEXT
);

CREATE INDEX idx_session_timestamp ON logs(session_id, timestamp);
```

## File Operation Detection

The system automatically detects file operations from session logs using pattern matching:

### Supported Patterns

- `Created file: "path/to/file.py"`
- `Modified file: "path/to/file.py"`
- `Updated file: "path/to/file.py"`
- `Writing to path/to/file.py`
- `create path="path/to/file.py"`
- `edit path="path/to/file.py"`

### Operation Types

- **create**: File creation operations
- **edit**: File modification operations
- **view**: File read operations (future)

## Report Format

The generated report includes:

1. **Overall Statistics**
   - Total sessions analyzed
   - Total expected files
   - Verified files count
   - Missing files count
   - Verification rate percentage

2. **Per-Session Details**
   - Session ID and timestamps
   - Message count
   - Expected files list
   - Missing files (if any)
   - Notes and warnings

3. **Missing Files Section**
   - Lists all files that should exist but don't
   - Includes operation type and timestamp
   - Provides troubleshooting notes

## Example Report

```markdown
# Copilot Session Log Verification Report

Generated: 2026-02-05T08:30:00Z

Total Sessions Analyzed: 5

---

## Overall Statistics
- Total Expected Files: 23
- Verified Files: 21
- Missing Files: 2
- Verification Rate: 91.3%

---

## Session Details

### Session: `test-session-1`
- Start Time: 2026-02-05T08:00:00Z
- End Time: 2026-02-05T08:15:00Z
- Messages: 15
- Expected Files: 5
- Verified: 4 ✅
- Missing: 1 ❌

#### Missing Files:
- `src/new_module.py` (create) - File NOT FOUND at /path/to/repo/src/new_module.py
```

## Testing

Run the test suite:

```bash
pytest tests/test_copilot_session_log_retriever.py -v
```

Test coverage includes:
- Session retrieval
- File extraction from logs
- File verification
- Batch processing
- Report generation
- Pattern matching
- Edge cases (empty DB, missing sessions)

## Integration

### With Existing Logging System

The retriever integrates with the existing `codex.logging` infrastructure:

```python
from codex.logging.session_logger import SessionLogger
from scripts.copilot_session_log_retriever import CopilotSessionRetriever

# After a session completes
with SessionLogger(session_id="my-session"):
    # ... perform operations ...
    pass

# Later, verify the session
retriever = CopilotSessionRetriever()
summary = retriever.analyze_session("my-session")
print(f"Verified: {summary.verified_files}/{len(summary.expected_files)}")
```

### With CI/CD Workflows

Add verification to your workflows:

```yaml
- name: Verify Copilot Session Files
  run: |
    python scripts/copilot_session_log_retriever.py \
      --last 5 \
      --batch-size 5 \
      --output .codex/verification_report.md

    # Check for missing files
    if grep -q "Missing Files: [1-9]" .codex/verification_report.md; then
      echo "Warning: Some expected files are missing"
      cat .codex/verification_report.md
    fi
```

## Troubleshooting

### Database Not Found

If the database doesn't exist, it will be created automatically with the correct schema.

### No Sessions Found

Check:
1. Database path is correct (`CODEX_LOG_DB_PATH`)
2. Sessions have been logged using `SessionLogger`
3. Database file has correct permissions

### Files Not Verified

Check:
1. Repository root path is correct
2. File paths in logs are relative or absolute
3. Files were actually created during session

### Pattern Not Matching

If file operations aren't detected:
1. Check the message format in logs
2. Add custom patterns to `FILE_OPERATION_PATTERNS`
3. Enable verbose logging (`--verbose`)

## Future Enhancements

- [ ] GitHub API integration for session retrieval
- [ ] Web UI for visualization
- [ ] Automatic file recovery from session history
- [ ] Integration with version control
- [ ] Real-time monitoring mode
- [ ] Custom pattern configuration file
- [ ] Export to JSON/CSV formats
- [ ] Session comparison and diff

## Related Documentation

- [Session Logger](../src/codex/logging/session_logger.py)
- [Session Query](../src/codex/logging/session_query.py)
- [AGENTS.md](../.github/AGENTS.md)
- [Operational Guidelines](./agent/OPERATIONAL_GUIDELINES.md)

## Contributing

To extend the retriever:

1. Add new patterns to `FILE_OPERATION_PATTERNS`
2. Implement additional verification logic
3. Add tests for new functionality
4. Update documentation

## License

Part of the `_codex_` repository. See main LICENSE file.
