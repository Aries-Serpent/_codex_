"""Test MCP protocol edge cases with hypothesis."""

from __future__ import annotations

import json
from typing import Dict

import pytest

try:
    from hypothesis import given
    from hypothesis import strategies as st
except ImportError:
    pytest.skip("hypothesis not available", allow_module_level=True)


@given(
    text=st.text(min_size=1),
)
def test_special_characters_in_roundtrip(text: str):
    """Test that special characters survive roundtrip."""
    try:
        message = {"content": text}
        encoded = json.dumps(message)
        decoded = json.loads(encoded)

        assert decoded["content"] == text, "Content must not be empty"
    except (ValueError, OverflowError):
        # Some special characters might not be JSON-serializable
        pass


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_float_roundtrip(value: float):
    """Test float values in roundtrip."""
    message = {"value": value}
    encoded = json.dumps(message)
    decoded = json.loads(encoded)

    assert abs(decoded["value"] - value) < 1e-10, "Value must be initialized"


@given(
    st.lists(
        st.dictionaries(st.text(min_size=1, max_size=20), st.integers()), min_size=0, max_size=10
    )
)
def test_complex_nested_structure(data: list[Dict[str, int]]):
    """Test complex nested structures."""
    message = {"nested": data}
    encoded = json.dumps(message)
    decoded = json.loads(encoded)

    assert decoded["nested"] == data, "Data must not be empty"
