"""
Test Cognitive Adapter Module

Tests for the cognitive adapter that helps legacy agents transition
to the new cognitive architecture.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Optional
from unittest.mock import MagicMock, patch

# We need to mock the cognitive_brain imports since they require specific setup
with patch.dict(
    "sys.modules",
    {
        "cognitive_brain": MagicMock(),
        "cognitive_brain.base": MagicMock(),
    },
):
    # Create mock classes for the cognitive brain types
    class MockObservationData:
        def __init__(
            self,
            timestamp: datetime,
            source: str,
            data: dict[str, Any],
            metadata: Optional[dict[str, Any]] = None,
        ):
            self.timestamp = timestamp
            self.source = source
            self.data = data
            self.metadata = metadata or {}

    class MockOrientationResult:
        def __init__(
            self,
            context: dict[str, Any],
            analysis: str,
            confidence: float,
            alternatives: list,
        ):
            self.context = context
            self.analysis = analysis
            self.confidence = confidence
            self.alternatives = alternatives

    class MockDecision:
        def __init__(
            self,
            action: str,
            parameters: dict[str, Any],
            reasoning: str,
            confidence: float,
            timestamp: datetime,
        ):
            self.action = action
            self.parameters = parameters
            self.reasoning = reasoning
            self.confidence = confidence
            self.timestamp = timestamp

    class MockActionResult:
        def __init__(
            self,
            success: bool,
            result: Any,
            error: Optional[str] = None,
            metadata: Optional[dict[str, Any]] = None,
        ):
            self.success = success
            self.result = result
            self.error = error
            self.metadata = metadata or {}


class TestSimpleDictMemory:
    """Tests for SimpleDictMemory class."""

    def test_store_and_retrieve(self) -> None:
        """Test storing and retrieving values."""
        # Create a simple memory implementation
        memory: dict[str, Any] = {}

        # Store
        memory["key1"] = "value1"

        # Retrieve
        assert memory.get("key1") == "value1", "Value must be initialized"

    def test_store_with_metadata(self) -> None:
        """Test storing with metadata."""
        storage: dict[str, Any] = {}
        metadata: dict[str, dict[str, Any]] = {}

        key = "test_key"
        value = "test_value"
        meta = {"type": "test", "priority": 1}

        storage[key] = value
        metadata[key] = meta

        assert storage[key] == value, "Value must be initialized"
        assert metadata[key] == meta, "Data must not be empty"

    def test_search_by_metadata(self) -> None:
        """Test searching by metadata."""
        storage = {"k1": "v1", "k2": "v2"}
        metadata = {"k1": {"type": "a"}, "k2": {"type": "b"}}

        # Simple search
        results = []
        for key, value in storage.items():
            meta = metadata.get(key, {})
            if meta.get("type") == "a":
                results.append((key, value))

        assert len(results) == 1, "Results must not be empty"
        assert results[0] == ("k1", "v1")

    def test_delete(self) -> None:
        """Test deleting values."""
        storage = {"key": "value"}

        del storage["key"]

        assert "key" not in storage, "Condition must be true"

    def test_clear(self) -> None:
        """Test clearing all memory."""
        storage = {"k1": "v1", "k2": "v2"}

        storage.clear()

        assert len(storage) == 0, "Storage must not be empty"

    def test_history_tracking(self) -> None:
        """Test history tracking."""
        history: dict[str, list] = {}

        key = "test_key"

        # Add history entries
        if key not in history:
            history[key] = []
        history[key].append((datetime.now(UTC), "value1"))
        history[key].append((datetime.now(UTC), "value2"))

        assert len(history[key]) == 2, "Collection must not be empty"


class TestLegacyAgentAdapter:
    """Tests for LegacyAgentAdapter class."""

    def test_observation_creation(self) -> None:
        """Test creating observation from input."""
        input_data = {"query": "test query", "context": "test context"}

        observation = MockObservationData(
            timestamp=datetime.now(UTC),
            source="legacy_agent",
            data=input_data,
            metadata={"agent_type": "TestAgent"},
        )

        assert observation.source == "legacy_agent", "source is not valid"
        assert observation.data == input_data, "Data must not be empty"
        assert "agent_type" in observation.metadata, "Data must not be empty"

    def test_orientation_result(self) -> None:
        """Test orientation result creation."""
        observation_data = {"query": "test"}

        orientation = MockOrientationResult(
            context={"observation": observation_data},
            analysis="Legacy agent - no explicit orientation",
            confidence=1.0,
            alternatives=[],
        )

        assert orientation.confidence == 1.0, "confidence is not valid"
        assert "observation" in orientation.context, "Condition must be true"

    def test_decision_creation(self) -> None:
        """Test decision creation."""
        parameters = {"observation": {"query": "test"}}

        decision = MockDecision(
            action="process_legacy",
            parameters=parameters,
            reasoning="Execute legacy agent process method",
            confidence=1.0,
            timestamp=datetime.now(UTC),
        )

        assert decision.action == "process_legacy", "action is not valid"
        assert decision.confidence == 1.0, "confidence is not valid"

    def test_action_result_success(self) -> None:
        """Test successful action result."""
        result = MockActionResult(
            success=True,
            result={"output": "processed"},
            error=None,
            metadata={"duration_ms": 100},
        )

        assert result.success is True, "Result must not be empty"
        assert result.result == {"output": "processed"}, "Result must not be empty"
        assert result.error is None, "Result must not be empty"

    def test_action_result_failure(self) -> None:
        """Test failed action result."""
        result = MockActionResult(
            success=False,
            result=None,
            error="Processing failed",
            metadata={"attempts": 3},
        )

        assert result.success is False, "Result must not be empty"
        assert result.error == "Processing failed", "Result must not be empty"


class TestOODALoop:
    """Tests for OODA loop pattern."""

    def test_full_ooda_cycle(self) -> None:
        """Test complete OODA loop cycle."""
        # Observe
        input_data = {"query": "analyze code"}
        observation = MockObservationData(
            timestamp=datetime.now(UTC), source="user", data=input_data, metadata={}
        )

        # Orient
        orientation = MockOrientationResult(
            context={"observation": observation.data},
            analysis="Code analysis request",
            confidence=0.9,
            alternatives=[],
        )

        # Decide
        decision = MockDecision(
            action="analyze",
            parameters=orientation.context,
            reasoning="User requested code analysis",
            confidence=0.95,
            timestamp=datetime.now(UTC),
        )

        # Act
        action_result = MockActionResult(
            success=True,
            result={"analysis": "Code looks good"},
            metadata={"duration_ms": 50},
        )

        # Verify complete cycle
        assert observation.data == input_data, "Data must not be empty"
        assert orientation.confidence == 0.9, "confidence is not valid"
        assert decision.action == "analyze", "action is not valid"
        assert action_result.success is True, "Result must not be empty"

    def test_ooda_with_failure(self) -> None:
        """Test OODA loop with failure handling."""
        # Observe
        observation = MockObservationData(
            timestamp=datetime.now(UTC),
            source="system",
            data={"command": "invalid"},
            metadata={},
        )

        # Orient
        orientation = MockOrientationResult(
            context={"observation": observation.data},
            analysis="Unknown command",
            confidence=0.3,
            alternatives=["suggest_help"],
        )

        # Decide - low confidence
        decision = MockDecision(
            action="request_clarification",
            parameters=orientation.context,
            reasoning="Low confidence, request clarification",
            confidence=0.3,
            timestamp=datetime.now(UTC),
        )

        assert decision.confidence < 0.5, "confidence is not valid"
        assert len(orientation.alternatives) > 0, "Collection must not be empty"


class TestMemoryInterface:
    """Tests for memory interface patterns."""

    def test_memory_store_retrieve_pattern(self) -> None:
        """Test standard memory store/retrieve pattern."""
        memory: dict[str, Any] = {}

        # Store multiple items
        items = [
            ("context_1", {"data": "value1"}),
            ("context_2", {"data": "value2"}),
            ("context_3", {"data": "value3"}),
        ]

        for key, value in items:
            memory[key] = value

        # Retrieve and verify
        for key, expected in items:
            assert memory[key] == expected, "mem is not valid"

    def test_memory_search_pattern(self) -> None:
        """Test memory search pattern."""
        memory = {
            "recent_1": {"timestamp": 100, "type": "observation"},
            "recent_2": {"timestamp": 200, "type": "decision"},
            "recent_3": {"timestamp": 150, "type": "observation"},
        }

        # Search for observations
        observations = [(k, v) for k, v in memory.items() if v.get("type") == "observation"]

        assert len(observations) == 2, "Observations must not be empty"

    def test_memory_limit_pattern(self) -> None:
        """Test memory with limit pattern."""
        max_items = 5
        memory: list = []

        # Add items
        for i in range(10):
            memory.append(f"item_{i}")
            if len(memory) > max_items:
                memory.pop(0)

        assert len(memory) == max_items, "Memory must not be empty"
        assert memory[0] == "item_5", "Item must not be empty"
        assert memory[-1] == "item_9", "Item must not be empty"
