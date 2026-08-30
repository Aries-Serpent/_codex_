"""Comprehensive fixture-based testing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import pytest


@dataclass
class TestContext:
    name: str
    data: Dict[str, Any]
    results: List[Any]


@pytest.fixture
def test_context():
    """Provide a test context."""
    return TestContext(name="test_run", data={"key": "value"}, results=[])


@pytest.fixture
def sample_messages():
    """Provide sample messages."""
    return [
        {"id": 1, "method": "test.method1", "params": {"arg": "value1"}},
        {"id": 2, "method": "test.method2", "params": {"arg": "value2"}},
        {"id": 3, "method": "test.method3", "params": {}},
    ]


@pytest.fixture
def error_messages():
    """Provide error messages."""
    return [
        {"id": 1, "error": {"code": -32600, "message": "Invalid Request"}},
        {"id": 2, "error": {"code": -32601, "message": "Method not found"}},
    ]


def test_context_initialization(test_context):
    """Test context fixture initialization."""
    assert test_context.name == "test_run", "name is not valid"
    assert "key" in test_context.data, "Data must not be empty"


def test_context_data_access(test_context):
    """Test accessing context data."""
    assert test_context.data["key"] == "value", "Data must not be empty"
    test_context.data["new_key"] = "new_value"
    assert test_context.data["new_key"] == "new_value", "Data must not be empty"


def test_context_results_tracking(test_context):
    """Test tracking results in context."""
    test_context.results.append("result1")
    test_context.results.append("result2")

    assert len(test_context.results) == 2, "Collection must not be empty"


def test_sample_messages_count(sample_messages):
    """Test sample messages fixture."""
    assert len(sample_messages) == 3, "Sample_messages must not be empty"


def test_sample_messages_structure(sample_messages):
    """Test sample messages have correct structure."""
    for msg in sample_messages:
        assert "id" in msg, "Condition must be true"
        assert "method" in msg, "Condition must be true"
        assert "params" in msg or "error" in msg, "Error should be raised or set"


def test_sample_messages_ids(sample_messages):
    """Test sample messages have sequential IDs."""
    ids = [msg["id"] for msg in sample_messages]
    assert ids == [1, 2, 3]


def test_error_messages_count(error_messages):
    """Test error messages fixture."""
    assert len(error_messages) == 2, "Error_messages must not be empty"


def test_error_messages_structure(error_messages):
    """Test error messages have correct structure."""
    for msg in error_messages:
        assert "id" in msg, "Condition must be true"
        assert "error" in msg, "Error should be raised or set"
        assert "code" in msg["error"], "Error should be raised or set"
        assert "message" in msg["error"], "Error should be raised or set"


def test_fixture_isolation(test_context):
    """Test that fixtures are properly isolated."""
    # Each test should get a fresh context
    assert len(test_context.results) == 0, "Collection must not be empty"
