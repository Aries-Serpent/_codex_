"""
Test Audit Logging

Test module for audit logging.
"""

import pytest

from security import SecurityEventType, get_audit_logger, log_security_event


def test_security_event_logged() -> None:
    """A security event must be recorded by the audit logger."""
    logger = get_audit_logger()
    # Reset in-memory buffer for deterministic assertion.
    pre_count = len(logger.events)
    log_security_event(SecurityEventType.RBAC_VIOLATION, action="user blocked")
    assert len(logger.events) == pre_count + 1, "Event was not recorded"
    assert logger.events[-1].action == "user blocked", "Action mismatch"
