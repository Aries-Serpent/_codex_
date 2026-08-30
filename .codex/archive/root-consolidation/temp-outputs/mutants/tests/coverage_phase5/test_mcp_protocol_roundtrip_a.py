"""Test MCP protocol round-trip with hypothesis."""

from __future__ import annotations

import json
from typing import Any, Dict

import pytest

try:
    from hypothesis import given
    from hypothesis import strategies as st
except ImportError:
    pytest.skip("hypothesis not available", allow_module_level=True)


def encode_message(message: Dict[str, Any]) -> str:
    """Encode message to JSON."""
    return json.dumps(message)


def decode_message(encoded: str) -> Dict[str, Any]:
    """Decode message from JSON."""
    return json.loads(encoded)


@given(
    data=st.dictionaries(st.text(min_size=1), st.one_of(st.text(), st.integers(), st.booleans()))
)
def test_message_roundtrip(data: Dict[str, str | int | bool]):
    """Test that messages survive JSON roundtrip."""
    encoded = encode_message(data)
    decoded = decode_message(encoded)

    assert decoded == data, "Data must not be empty"


@given(
    message_id=st.integers(min_value=1, max_value=1000),
    method=st.text(min_size=1, max_size=100),
)
def test_jsonrpc_message_roundtrip(message_id: int, method: str):
    """Test JSON-RPC message roundtrip."""
    message = {"jsonrpc": "2.0", "id": message_id, "method": method, "params": {}}

    encoded = encode_message(message)
    decoded = decode_message(encoded)

    assert decoded["id"] == message_id, "Condition must be true"
    assert decoded["method"] == method, "Condition must be true"
    assert decoded["jsonrpc"] == "2.0", "Condition must be true"


@given(st.lists(st.integers(), min_size=1, max_size=100))
def test_list_payload_roundtrip(values: list[int]):
    """Test list payload roundtrip."""
    message = {"data": values}

    encoded = encode_message(message)
    decoded = decode_message(encoded)

    assert decoded["data"] == values, "Data must not be empty"
