"""Test MCP checkpoint payload validation."""

from __future__ import annotations

from typing import Any, Dict


def validate_checkpoint_payload(data: Dict[str, Any]) -> bool:
    """Validate checkpoint payload structure."""
    required = {"checkpoint_id", "state", "metadata"}
    return all(k in data for k in required)


def test_valid_checkpoint_payload():
    """Test valid checkpoint payload."""
    payload = {"checkpoint_id": "ckpt_001", "state": {"data": "test"}, "metadata": {"version": "1"}}

    assert validate_checkpoint_payload(payload), "Condition must be true"


def test_missing_checkpoint_id():
    """Test payload missing checkpoint_id."""
    payload = {"state": {"data": "test"}, "metadata": {"version": "1"}}

    assert not validate_checkpoint_payload(payload), "Condition must be true"


def test_missing_state():
    """Test payload missing state."""
    payload = {"checkpoint_id": "ckpt_001", "metadata": {"version": "1"}}

    assert not validate_checkpoint_payload(payload), "Condition must be true"


def test_missing_metadata():
    """Test payload missing metadata."""
    payload = {"checkpoint_id": "ckpt_001", "state": {"data": "test"}}

    assert not validate_checkpoint_payload(payload), "Condition must be true"


def test_empty_checkpoint_payload():
    """Test empty checkpoint payload."""
    payload = {}

    assert not validate_checkpoint_payload(payload), "Condition must be true"


def test_extra_fields_in_payload():
    """Test payload with extra fields (should still be valid)."""
    payload = {
        "checkpoint_id": "ckpt_001",
        "state": {"data": "test"},
        "metadata": {"version": "1"},
        "extra_field": "value",
    }

    assert validate_checkpoint_payload(payload), "Condition must be true"
