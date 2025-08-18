# Auto-generated SAFE import smoke; avoids side effects by try/except.
import importlib, traceback, sys
failures = []
targets = []
targets.append("codex_logging_workflow")
targets.append("codex_workflow_session_query")
targets.append("codex_patch_session_logging")
targets.append("codex_session_logging_workflow")
targets.append("codex_log_viewer")
targets.append("codex_workflow")
targets.append("session_hooks")
targets.append("session_query")
targets.append("session_logger")
targets.append("chat")
targets.append("viewer")
targets.append("query_logs")
targets.append("export")
targets.append("session_query")
targets.append("session_logger")
targets.append("conversation_logger")
targets.append("apply_session_logging_workflow")
targets.append("codex_end_to_end")
targets.append("test_export")
targets.append("test_chat_session")
targets.append("test_session_logging_mirror")
targets.append("test_session_hooks")
targets.append("test_conversation_logger")
targets.append("test_session_logging")
targets.append("test_session_query_smoke")
targets.append("test_logging_viewer_cli")
for name in sorted(set(targets)):
    try:
        importlib.import_module(name)
    except Exception as e:
        failures.append((name, ''.join(traceback.format_exception_only(type(e), e)).strip()))
if failures:
    print('IMPORT_SMOKE_FAILURES:')
    for n, msg in failures:
        print(f'{n}: {msg}')
    sys.exit(2)
print('IMPORT_SMOKE_OK')
