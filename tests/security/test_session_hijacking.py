import pytest

from src.security import SecurityError, verify_session_integrity


def test_session_integrity_mismatch() -> None:
    active_sessions = [{"id": "abc", "fingerprint": "123", "ip": "1.1.1.1", "user_agent": "ua"}]
    with pytest.raises(SecurityError):
        verify_session_integrity(
            "abc",
            {"fingerprint": "xxx", "ip": "1.1.1.1", "user_agent": "ua"},
            active_sessions,
        )


def test_session_integrity_success() -> None:
    active_sessions = [{"id": "abc", "fingerprint": "123", "ip": "1.1.1.1", "user_agent": "ua"}]
    verify_session_integrity(
        "abc",
        {"fingerprint": "123", "ip": "1.1.1.1", "user_agent": "ua"},
        active_sessions,
    )
