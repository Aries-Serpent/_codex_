"""Test payload validation edge cases."""

from __future__ import annotations

from typing import Any, Dict


def validate_payload(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate payload structure and return (valid, error_message)."""
    if not isinstance(data, dict):
        return False, "Payload must be a dictionary"

    required_fields = {"id", "method"}
    if not all(f in data for f in required_fields):
        return False, f"Missing required fields: {required_fields - set(data.keys())}"

    if not isinstance(data["id"], (int, str)):
        return False, "id must be int or str"

    if not isinstance(data["method"], str):
        return False, "method must be str"

    if "params" in data and not isinstance(data["params"], (dict, list, type(None))):
        return False, "params must be dict, list, or null"

    return True, ""


def test_valid_payload():
    """Test valid payload."""
    payload = {"id": 1, "method": "test.method"}
    valid, msg = validate_payload(payload)

    assert valid, "valid is not valid"


def test_payload_missing_id():
    """Test payload missing id."""
    payload = {"method": "test"}
    valid, msg = validate_payload(payload)

    assert not valid, "Condition must be true"
    assert "id" in msg, "Condition must be true"


def test_payload_missing_method():
    """Test payload missing method."""
    payload = {"id": 1}
    valid, msg = validate_payload(payload)

    assert not valid, "Condition must be true"
    assert "method" in msg, "Condition must be true"


def test_payload_invalid_id_type():
    """Test payload with invalid id type."""
    payload = {"id": [1, 2], "method": "test"}
    valid, msg = validate_payload(payload)

    assert not valid, "Condition must be true"
    assert "id" in msg, "Condition must be true"


def test_payload_invalid_method_type():
    """Test payload with invalid method type."""
    payload = {"id": 1, "method": 123}
    valid, msg = validate_payload(payload)

    assert not valid, "Condition must be true"
    assert "method" in msg, "Condition must be true"


def test_payload_invalid_params_type():
    """Test payload with invalid params type."""
    payload = {"id": 1, "method": "test", "params": "invalid"}
    valid, msg = validate_payload(payload)

    assert not valid, "Condition must be true"
    assert "params" in msg, "Condition must be true"


def test_payload_with_dict_params():
    """Test payload with valid dict params."""
    payload = {"id": 1, "method": "test", "params": {"key": "value"}}
    valid, msg = validate_payload(payload)

    assert valid, "valid is not valid"


def test_payload_with_list_params():
    """Test payload with valid list params."""
    payload = {"id": 1, "method": "test", "params": [1, 2, 3]}
    valid, msg = validate_payload(payload)

    assert valid, "valid is not valid"


def test_payload_with_null_params():
    """Test payload with null params."""
    payload = {"id": 1, "method": "test", "params": None}
    valid, msg = validate_payload(payload)

    assert valid, "valid is not valid"


def test_empty_payload():
    """Test empty payload."""
    payload = {}
    valid, msg = validate_payload(payload)

    assert not valid, "Condition must be true"


def test_payload_extra_fields():
    """Test payload with extra fields (should still be valid)."""
    payload = {"id": 1, "method": "test", "jsonrpc": "2.0", "extra": "data"}
    valid, msg = validate_payload(payload)

    assert valid, "valid is not valid"
