import pytest

from src.security import SecurityError, verify_csrf_token


def test_missing_csrf_token() -> None:
    with pytest.raises(SecurityError):
        verify_csrf_token(None, "abc")


def test_csrf_token_match() -> None:
    verify_csrf_token("token", "token")
