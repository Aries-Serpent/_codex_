# Session Logging Change Log

Date: 2025-08-18T12:21:47.014117+00:00

- Added `src/codex/logging/session_logger.py` (SQLite-backed).
- Patched `entrypoint.sh` with start/end logging hooks (idempotent).
- Created `tests/test_session_logging.py` (pytest).
- Appended README with usage and schema.
- Guardrail: No changes to `.github/workflows` and no activation of Actions.
