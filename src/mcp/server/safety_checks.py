from __future__ import annotations
import os


def live_tests_enabled() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("1", "true", "yes")
