import pytest

from src.security import SecurityError, validate_input


def test_path_traversal_blocked() -> None:
    malicious = "../../../etc/passwd"
    with pytest.raises(SecurityError):
        validate_input(malicious, input_type="path")


def test_absolute_path_blocked() -> None:
    with pytest.raises(SecurityError):
        validate_input("/etc/shadow", input_type="path")
