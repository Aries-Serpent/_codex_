"""
Monitoring tests package initialization.

Ensures monitoring module is accessible before test collection.
"""
try:
    from codex_ml.monitoring import system_metrics  # noqa: F401
except ImportError as e:
    import sys

    # Only print error message during import, before re-raising
    sys.stderr.write(
        f"ERROR: Cannot import codex_ml.monitoring.system_metrics\n"
        f"Ensure 'monitoring' extras are installed: pip install -e '.[monitoring]'\n"
        f"Original error: {e}\n"
    )
    raise
