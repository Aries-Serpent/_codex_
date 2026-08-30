"""Standalone handler functions used as entrypoints in test_envelope.py.

Keeping them in a separate module prevents ``tests.skills.test_envelope``
from importing itself when ExecutionEnvelope dynamically loads the entrypoint.
"""

from __future__ import annotations

import time


def _echo_handler(payload: dict) -> dict:
    """Simple handler that echoes the payload."""
    return {"echo": payload}


def _error_handler(payload: dict) -> dict:
    raise ValueError("intentional error")


def _slow_handler(payload: dict) -> dict:
    time.sleep(10)
    return {}


# Placeholder overwritten by TestRetryMechanism.test_retry_on_transient_failure
# via sys.modules injection to avoid coupling the test to this module's state.
def flaky_handler(payload: dict) -> dict:  # pragma: no cover
    raise NotImplementedError("replaced at test runtime via sys.modules injection")
