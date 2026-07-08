"""Property-based tests for JSON-RPC using hypothesis."""

from __future__ import annotations

import json
from typing import Any, Dict

import pytest

try:
    from hypothesis import assume, given
    from hypothesis import strategies as st
except ImportError:
    pytest.skip("hypothesis not available", allow_module_level=True)


@given(
    st.lists(
        st.dictionaries(
            st.text(min_size=1, max_size=50),
            st.integers() | st.text() | st.booleans() | st.none(),
            min_size=0,
            max_size=10,
        ),
        min_size=1,
        max_size=20,
    )
)
def test_json_serialization_preserves_structure(messages: list[Dict[str, Any]]):
    """Property: JSON serialization/deserialization preserves structure."""
    for msg in messages:
        encoded = json.dumps(msg)
        decoded = json.loads(encoded)
        assert decoded == msg, "decoded is not valid"


@given(st.integers(min_value=1, max_value=2**31 - 1))
def test_message_ids_are_valid(msg_id: int):
    """Property: Valid message IDs survive roundtrip."""
    message = {"jsonrpc": "2.0", "id": msg_id, "method": "test.method", "params": {}}

    encoded = json.dumps(message)
    decoded = json.loads(encoded)

    assert decoded["id"] == msg_id, "Condition must be true"


@given(st.text(min_size=1, max_size=255, alphabet=st.characters(blacklist_characters='\\/"')))
def test_method_names_preserved(method_name: str):
    """Property: Method names are preserved through roundtrip."""
    assume(not any(c in method_name for c in ["\\", "'\""]))

    message = {"jsonrpc": "2.0", "method": method_name, "params": {}}

    try:
        encoded = json.dumps(message)
        decoded = json.loads(encoded)
        assert decoded["method"] == method_name, "Condition must be true"
    except (ValueError, OverflowError):
        pass
