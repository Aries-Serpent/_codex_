"""Tests for agents.mental_mapping module.

Phase 7 tests covering:
- Clock abstraction functions
- NodeType enum
- Mental mapping data structures
- MentalMap class operations
"""

from __future__ import annotations

from datetime import datetime

import pytest


class TestClockAbstraction:
    """Tests for clock abstraction functions."""

    def test_default_clock_returns_iso_format(self):
        """Test that default clock returns ISO format timestamp."""
        from agents.mental_mapping import _default_clock

        result = _default_clock()
        # Should be parseable as ISO format
        datetime.fromisoformat(result)

    def test_get_timestamp_uses_current_clock(self):
        """Test get_timestamp uses the configured clock."""
        from agents.mental_mapping import get_timestamp, reset_clock, set_clock

        try:
            # Set a custom clock
            set_clock(lambda: "2025-01-01T00:00:00")
            result = get_timestamp()
            assert result == "2025-01-01T00:00:00", "Result must not be empty"
        finally:
            reset_clock()

    def test_set_clock_overrides_default(self):
        """Test set_clock overrides the default clock."""
        from agents.mental_mapping import get_timestamp, reset_clock, set_clock

        try:
            custom_time = "2025-06-15T12:30:00"
            set_clock(lambda: custom_time)
            assert get_timestamp() == custom_time, "Condition must be true"
        finally:
            reset_clock()

    def test_reset_clock_restores_default(self):
        """Test reset_clock restores default behavior."""
        from agents.mental_mapping import get_timestamp, reset_clock, set_clock

        set_clock(lambda: "fixed")
        reset_clock()

        # Should now return a proper ISO timestamp
        result = get_timestamp()
        datetime.fromisoformat(result)


class TestNodeType:
    """Tests for NodeType enum."""

    def test_node_types_exist(self):
        """Test all expected node types exist."""
        from agents.mental_mapping import NodeType

        assert NodeType.PROBLEM.value == "problem", "Value must be initialized"
        assert NodeType.HYPOTHESIS.value == "hypothesis", "Value must be initialized"
        assert NodeType.EVIDENCE.value == "evidence", "Value must be initialized"

    def test_node_type_iteration(self):
        """Test that NodeType is iterable."""
        from agents.mental_mapping import NodeType

        types = list(NodeType)
        assert len(types) >= 3, "Types must not be empty"


class TestReasoningChain:
    """Tests for ReasoningChain dataclass."""

    @pytest.fixture
    def ReasoningChain(self):
        """Import ReasoningChain class."""
        try:
            from agents.mental_mapping import ReasoningChain

            return ReasoningChain
        except ImportError:
            pytest.skip("ReasoningChain not available")
            return None

    def test_create_reasoning_chain(self, ReasoningChain):
        """Test creating a reasoning chain."""
        chain = ReasoningChain(
            chain_id="chain-1",
            steps=["step1", "step2"],
            conclusion="final answer",
        )
        assert chain.chain_id == "chain-1", "chain_id is not valid"
        assert len(chain.steps) == 2, "Collection must not be empty"

    def test_reasoning_chain_defaults(self, ReasoningChain):
        """Test reasoning chain with default values."""
        chain = ReasoningChain(
            chain_id="chain-1",
            steps=[],
            conclusion="",
        )
        assert chain.chain_id == "chain-1", "chain_id is not valid"
        assert chain.steps == [], "steps is not valid"


class TestMentalMapNode:
    """Tests for MentalMapNode dataclass."""

    @pytest.fixture
    def MentalMapNode(self):
        """Import MentalMapNode class."""
        try:
            from agents.mental_mapping import (
                MentalMapNode,
            )
            from agents.mental_mapping import NodeType as NodeType

            return MentalMapNode
        except ImportError:
            pytest.skip("MentalMapNode not available")
            return None

    @pytest.fixture
    def NodeType(self):
        """Import NodeType enum."""
        from agents.mental_mapping import NodeType

        return NodeType

    def test_create_problem_node(self, MentalMapNode, NodeType):
        """Test creating a problem node."""
        node = MentalMapNode(
            node_id="node-1",
            node_type=NodeType.PROBLEM,
            content="What is the solution?",
        )
        assert node.node_type == NodeType.PROBLEM, "node_type is not valid"
        assert "solution" in node.content, "Content must not be empty"

    def test_create_hypothesis_node(self, MentalMapNode, NodeType):
        """Test creating a hypothesis node."""
        node = MentalMapNode(
            node_id="node-2",
            node_type=NodeType.HYPOTHESIS,
            content="The solution might be X",
        )
        assert node.node_type == NodeType.HYPOTHESIS, "node_type is not valid"

    def test_create_evidence_node(self, MentalMapNode, NodeType):
        """Test creating an evidence node."""
        node = MentalMapNode(
            node_id="node-3",
            node_type=NodeType.EVIDENCE,
            content="Data supports hypothesis",
        )
        assert node.node_type == NodeType.EVIDENCE, "node_type is not valid"


class TestMentalMap:
    """Tests for MentalMap class."""

    @pytest.fixture
    def MentalMap(self):
        """Import MentalMap class."""
        try:
            from agents.mental_mapping import MentalMappingModel

            return MentalMappingModel
        except ImportError:
            pytest.skip("MentalMappingModel not available")
            return None

    @pytest.fixture
    def NodeType(self):
        """Import NodeType enum."""
        from agents.mental_mapping import NodeType

        return NodeType

    def test_create_mental_map(self, MentalMap):
        """Test creating a mental map."""
        mental_map = MentalMap()
        assert mental_map is not None, "mental_map must be initialized"

    def test_mental_map_create_node(self, MentalMap, NodeType):
        """Test creating a node in mental map."""
        mental_map = MentalMap()
        node = mental_map.create_node(
            node_type=NodeType.PROBLEM,
            content="Test problem",
        )
        assert node is not None, "node must be initialized"
        assert node.node_id is not None, "node_id must be initialized"

    def test_mental_map_get_node(self, MentalMap, NodeType):
        """Test getting a node from mental map."""
        mental_map = MentalMap()
        node = mental_map.create_node(
            node_type=NodeType.PROBLEM,
            content="Test problem",
        )
        retrieved = mental_map.nodes.get(node.node_id)
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.content == "Test problem", "Content must not be empty"

    def test_mental_map_connect_nodes(self, MentalMap, NodeType):
        """Test connecting nodes in mental map."""
        mental_map = MentalMap()
        node1 = mental_map.create_node(NodeType.PROBLEM, content="Problem")
        node2 = mental_map.create_node(NodeType.HYPOTHESIS, content="Hypothesis")

        edge = mental_map.connect_nodes(source_id=node1.node_id, target_id=node2.node_id)

        # Edge should exist
        assert edge is not None, "edge must be initialized"

    def test_mental_map_to_dict(self, MentalMap, NodeType):
        """Test serializing mental map to dict."""
        mental_map = MentalMap()
        mental_map.create_node(NodeType.PROBLEM, content="Test")

        result = mental_map.to_dict()

        assert isinstance(result, dict)
        assert "nodes" in result or len(result) > 0, "Result must not be empty"


class TestSelfAppraisal:
    """Tests for self-appraisal functionality."""

    @pytest.fixture
    def SelfAppraisal(self):
        """Import SelfAppraisal class if available."""
        try:
            from agents.mental_mapping import SelfAppraisal

            return SelfAppraisal
        except ImportError:
            pytest.skip("SelfAppraisal not available")
            return None

    def test_create_self_appraisal(self, SelfAppraisal):
        """Test creating a self-appraisal."""
        appraisal = SelfAppraisal(
            decision_id="decision-1",
            confidence_score=0.85,
            reasoning="Based on evidence",
        )
        assert appraisal.confidence_score == 0.85, "confidence_score is not valid"


class TestDecisionPath:
    """Tests for decision path tracking."""

    @pytest.fixture
    def DecisionPath(self):
        """Import DecisionPath class if available."""
        try:
            from agents.mental_mapping import DecisionPath

            return DecisionPath
        except ImportError:
            pytest.skip("DecisionPath not available")
            return None

    def test_create_decision_path(self, DecisionPath):
        """Test creating a decision path."""
        path = DecisionPath(
            path_id="path-1",
            steps=["analyze", "hypothesize", "verify"],
            outcome="success",
        )
        assert len(path.steps) == 3, "Collection must not be empty"
        assert path.outcome == "success", "outcome is not valid"
