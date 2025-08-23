# Mapping Table

- **Instrument user/assistant exchanges** → ['/workspace/_codex_/tools/codex_logging_workflow.py', '/workspace/_codex_/src/codex/chat.py', '/workspace/_codex_/src/codex/logging/session_logger.py', '/workspace/_codex_/tests/test_session_logging.py', '/workspace/_codex_/src/codex/logging/conversation_logger.py', '/workspace/_codex_/src/codex/logging/query_logs.py', '/workspace/_codex_/tests/test_conversation_logger.py', '/workspace/_codex_/tests/test_export.py', '/workspace/_codex_/tests/test_chat_session.py']
  Rationale: Keyword/heuristic scan for conversation handlers

## Session hook tasks
- **T1:** Review `entrypoint.sh` for start/end hooks → `entrypoint.sh` (existing logging block lines 2-17)
- **T2:** Extract logic into reusable helper → `scripts/session_logging.sh`, `codex/logging/session_hooks.py`
- **T3:** Source/import helper in launch scripts → `entrypoint.sh`, `scripts/smoke_query_logs.sh`, `src/codex/logging/*`
- **T4:** Add regression test asserting start/end events → `tests/test_session_hooks.py`

- **Scaffold ingestion package __init__ with Ingestor class** → ['src/ingestion/__init__.py']
  Rationale: Define placeholder Ingestor class for future ingestion logic.
- **Add ingestion README documentation** → ['src/ingestion/README.md']
  Rationale: Document purpose and status of ingestion package.
- **Add ingestion placeholder test** → ['tests/test_ingestion_placeholder.py']
  Rationale: Ensure Ingestor can be imported and instantiated.
