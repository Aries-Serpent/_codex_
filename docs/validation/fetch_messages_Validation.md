# Fetch messages sqlite_patch import change

- Import changed to: `from codex.db.sqlite_patch import auto_enable_from_env`
- Kept a minimal no-op fallback to avoid hard failures in edge cases.
- Pooling is controlled by `CODEX_SQLITE_POOL` (or `CODEX_DB_POOL` for compatibility).
- Tests:
  - `pytest tests/test_fetch_messages.py::test_pool_toggle_invokes_helper`
  - `pytest tests/test_fetch_messages.py`
  - `pytest tests/test_fetch_messages_missing_db.py`
  - `pytest tests/test_sqlite_pool.py tests/test_sqlite_pool_close.py tests/logging/`
  - `pytest tests/test_cli_pool.py`
