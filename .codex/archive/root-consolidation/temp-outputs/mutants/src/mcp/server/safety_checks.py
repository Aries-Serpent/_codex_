"""
Safety Checks Module

This module provides functionality for safety checks.

Usage:
    from server.safety_checks import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import os


def live_tests_enabled() -> bool:
    """
    Returns True only if ENABLE_LIVE_TESTS env var is set to a truthy value.
    This function is used as a guard before attempting live network calls.
    """
    return os.environ.get("ENABLE_LIVE_TESTS", "false").lower() in ("1", "true", "yes")
