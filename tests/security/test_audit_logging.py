"""
Test Audit Logging

Test module for audit logging.
"""

import logging

import pytest

from security import log_security_event


def test_security_event_logged(caplog: pytest.LogCaptureFixture) -> None:
    # Target the specific logger used by log_security_event so caplog captures
    # its messages even when the logger's propagate flag is False in CI.
    caplog.set_level(logging.INFO, logger="codex.security")
    log_security_event("user blocked")
    assert "security_event" in caplog.messages, "Condition must be true"
