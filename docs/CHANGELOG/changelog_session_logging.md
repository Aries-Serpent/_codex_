# Session Logging Change Log

**Last Updated:** 2026-06-22

Date: 2025-08-18T12:21:47.014117+00:00

## Summary

Session logging was introduced to give AI agents a durable, queryable audit trail of every coding session. All events are written to a SQLite database, making it easy to replay, search, and analyse agent behaviour over time.

## Changes

- Added `src/codex/logging/session_logger.py` (SQLite-backed).
- Patched `entrypoint.sh` with start/end logging hooks (idempotent).
- Created `tests/test_session_logging.py` (pytest).
- Appended README with usage and schema.
- Guardrail: No changes to `.github/workflows` and no activation of Actions.

## Usage

```python
from codex.logging.session_logger import SessionLogger

logger = SessionLogger()
logger.log(role="assistant", content="Session started")
```

Query logs via:

```bash
python -m codex.logging.query_logs --session-id <id>
```

## Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment primary key |
| `session_id` | TEXT | UUID grouping all events in one session |
| `role` | TEXT | `system`, `user`, `assistant`, or `tool` |
| `content` | TEXT | Event payload |
| `ts` | TEXT | ISO-8601 timestamp |
