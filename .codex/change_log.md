# Codex Change Log

Date: 2025-08-18T22:22:24Z

## Session logging robustness

- Updated `scripts/apply_session_logging_workflow.py` to warn and exit gracefully when Git is unavailable.
- Added Git repository checks to `tests/test_session_logging.py` and replaced silent exception handling with explicit failures.
- Improved `tools/codex_session_logging_workflow.py` error handling with contextual logging and re-raising.
- Added helper script `codex_workflow_apply_session_logging_fixes.py`.
