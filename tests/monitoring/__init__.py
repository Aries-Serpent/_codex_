"""
Monitoring tests package initialization.

Ensures monitoring module is accessible before test collection.
"""
try:
    from codex_ml.monitoring import system_metrics
except ImportError as e:
    import sys

    print(
        f"ERROR: Cannot import codex_ml.monitoring.system_metrics\n"
        f"Ensure 'monitoring' extras are installed: pip install -e '.[dev,test,monitoring]'\n"
        f"Original error: {e}",
        file=sys.stderr,
    )
    raise
