"""Unit tests for agents/mental_mapping.py (Phase 9.1 coverage push).

These tests target previously uncovered code paths:
- visualize_reasoning_path (including depth + traversal)
- cluster_nodes
- get_subgraph (and ``nodes=`` alias)
- shortest_path edge cases (alias, MentalNode objects, same-node, missing)
- bfs/dfs alias and missing-node branches
- save_mental_map / load_mental_map round-trip
- get_connected_nodes
- calculate_metrics & get_node_centrality
- MentalEdge.to_dict with None edge_type
- create_node ``properties`` path + add_node low-confidence review
- connect_nodes alias / MentalNode object handling / properties / TypeError
- ReasoningStep description<->thought aliasing
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents import mental_mapping as mm
from agents.mental_mapping import (
    EdgeType,
    MentalEdge,
    MentalMappingModel,
    MentalNode,
    NodeType,
    ReasoningStep,
    get_timestamp,
    reset_clock,
    set_clock,
)


# ---------------------------------------------------------------------------
# Clock helpers
# ---------------------------------------------------------------------------
def test_set_and_reset_clock():
    set_clock(lambda: "2025-01-01T00:00:00Z")
    try:
        assert get_timestamp() == "2025-01-01T00:00:00Z", "Condition must be true"
    finally:
        reset_clock()
    # After reset, default clock produces something non-empty
    assert get_timestamp(), "Condition must be true"


# ---------------------------------------------------------------------------
# ReasoningStep aliasing
# ---------------------------------------------------------------------------
def test_reasoning_step_description_to_thought():
    step = ReasoningStep(step_id="s1", description="from description")
    assert step.thought == "from description", "thought is not valid"
    assert step.description == "from description", "description is not valid"


def test_reasoning_step_thought_to_description():
    step = ReasoningStep(step_id="s2", thought="from thought")
    assert step.description == "from thought", "description is not valid"


def test_reasoning_step_evidence_alias():
    step = ReasoningStep(step_id="s3", evidence_used=["e1"])
    assert step.evidence == ["e1"], "evidence is not valid"
    step.evidence = ["e2", "e3"]
    assert step.evidence_used == ["e2", "e3"]


# ---------------------------------------------------------------------------
# MentalEdge.to_dict with None edge_type
# ---------------------------------------------------------------------------
def test_mental_edge_to_dict_none_edge_type():
    edge = MentalEdge(edge_id="e", source_id="a", target_id="b", edge_type=None)
    d = edge.to_dict()
    assert d["edge_type"] is None, "Condition must be true"
    assert d["source_id"] == "a", "Condition must be true"
    # source/target alias properties
    assert edge.source == "a", "source is not valid"
    assert edge.target == "b", "target is not valid"


# ---------------------------------------------------------------------------
# create_node via properties dict path & add_node low-confidence
# ---------------------------------------------------------------------------
def test_create_node_with_properties_dict():
    m = MentalMappingModel(agent_id="t")
    node = m.create_node(
        NodeType.HYPOTHESIS,
        properties={
            "content": "hypo",
            "confidence": 0.3,  # triggers low-confidence review
            "importance": 0.4,
            "tags": ["x"],
            "context": {"k": "v"},
        },
    )
    assert node.content == "hypo", "Content must not be empty"
    assert node.confidence == 0.3, "confidence is not valid"
    assert node.needs_review is True, "needs_review is not valid"
    assert node.node_id in m.nodes_needing_review, "Condition must be true"


def test_create_node_default_content_when_empty():
    m = MentalMappingModel()
    node = m.create_node(NodeType.CONCEPT)
    assert node.content == "concept_node", "Content must not be empty"


def test_create_node_id_helper_returns_string_id():
    m = MentalMappingModel()
    nid = m.create_node_id(NodeType.GOAL, properties={"content": "g"})
    assert isinstance(nid, str)
    assert nid in m.nodes, "Condition must be true"


def test_add_node_low_confidence_marks_review():
    m = MentalMappingModel()
    node = MentalNode(
        node_id="n1",
        node_type=NodeType.OBSERVATION,
        content="c",
        timestamp=get_timestamp(),
        confidence=0.2,
    )
    m.add_node(node)
    assert "n1" in m.nodes, "Condition must be true"
    assert node.needs_review is True, "needs_review is not valid"
    assert "n1" in m.nodes_needing_review, "Condition must be true"


# ---------------------------------------------------------------------------
# connect_nodes – aliases / objects / properties / invalid types
# ---------------------------------------------------------------------------
def _build_pair(m: MentalMappingModel) -> tuple[MentalNode, MentalNode]:
    a = m.create_node(NodeType.CONCEPT, content="A", confidence=0.9)
    b = m.create_node(NodeType.CONCEPT, content="B", confidence=0.9)
    return a, b


def test_connect_nodes_with_node_objects_and_properties():
    m = MentalMappingModel()
    a, b = _build_pair(m)
    edge = m.connect_nodes(
        source_id=a,  # passing MentalNode triggers .node_id extraction
        target_id=b,
        edge_type=EdgeType.RELATED,
        properties={"weight": 0.42, "justification": "j", "evidence": ["ev"]},
    )
    assert edge.source_id == a.node_id, "source_id is not valid"
    assert edge.target_id == b.node_id, "target_id is not valid"
    assert edge.weight == 0.42, "weight is not valid"
    assert edge.justification == "j", "justification is not valid"
    assert edge.evidence == ["ev"], "evidence is not valid"


def test_connect_nodes_with_source_target_aliases():
    m = MentalMappingModel()
    a, b = _build_pair(m)
    edge = m.connect_nodes(source=a.node_id, target=b.node_id, edge_type=EdgeType.SUPPORTS)
    assert edge.source_id == a.node_id, "source_id is not valid"


def test_connect_nodes_type_error_for_non_string_ids():
    m = MentalMappingModel()
    _build_pair(m)
    with pytest.raises(TypeError):
        m.connect_nodes(source_id=123, target_id=456, edge_type=EdgeType.RELATED)


def test_connect_nodes_value_error_for_missing_nodes():
    m = MentalMappingModel()
    with pytest.raises(ValueError):
        m.connect_nodes(source_id="x", target_id="y", edge_type=EdgeType.RELATED)


# ---------------------------------------------------------------------------
# visualize_reasoning_path
# ---------------------------------------------------------------------------
def test_visualize_reasoning_path_missing_node():
    m = MentalMappingModel()
    assert m.visualize_reasoning_path("nope") == "Node not found", "Condition must be true"


def test_visualize_reasoning_path_with_chain_and_edge():
    m = MentalMappingModel()
    a = m.create_node(NodeType.PROBLEM, content="A" * 80, confidence=0.9)
    b = m.create_node(NodeType.HYPOTHESIS, content="B" * 80, confidence=0.7)
    a.add_reasoning_step(
        thought="initial reasoning step about the problem",
        reasoning_type="deductive",
        confidence=0.8,
    )
    a.add_reasoning_step(
        thought="follow-up reasoning step",
        reasoning_type="deductive",
        confidence=0.7,
    )
    m.connect_nodes(a.node_id, b.node_id, edge_type=EdgeType.LEADS_TO)

    text = m.visualize_reasoning_path(a.node_id, max_depth=3)

    assert "[problem]" in text, "Condition must be true"
    assert "[hypothesis]" in text, "Condition must be true"
    assert "Reasoning:" in text, "Condition must be true"
    assert "[leads_to]" in text, "Condition must be true"
    # Depth-limit guard: passing max_depth=1 must NOT traverse to neighbour
    short = m.visualize_reasoning_path(a.node_id, max_depth=1)
    assert "[hypothesis]" not in short, "Condition must be true"


# ---------------------------------------------------------------------------
# cluster_nodes
# ---------------------------------------------------------------------------
def test_cluster_nodes_groups_connected_same_type():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    b = m.create_node(NodeType.CONCEPT, content="b", confidence=0.9)
    c = m.create_node(NodeType.EVIDENCE, content="c", confidence=0.9)  # different type
    m.connect_nodes(a.node_id, b.node_id, edge_type=EdgeType.RELATED)
    clusters = m.cluster_nodes()
    # All nodes should be assigned to some cluster
    assigned = {nid for ids in clusters.values() for nid in ids}
    assert assigned == {a.node_id, b.node_id, c.node_id}
    # A and B (same type + connected) should share a cluster
    for ids in clusters.values():
        if a.node_id in ids:
            assert b.node_id in ids, "Condition must be true"


# ---------------------------------------------------------------------------
# get_subgraph (including `nodes=` alias and None)
# ---------------------------------------------------------------------------
def test_get_subgraph_filters_nodes_and_edges():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    b = m.create_node(NodeType.CONCEPT, content="b", confidence=0.9)
    c = m.create_node(NodeType.CONCEPT, content="c", confidence=0.9)
    m.connect_nodes(a.node_id, b.node_id, edge_type=EdgeType.RELATED)
    m.connect_nodes(b.node_id, c.node_id, edge_type=EdgeType.RELATED)

    sub = m.get_subgraph(nodes=[a.node_id, b.node_id])
    assert set(sub["nodes"].keys()) == {a.node_id, b.node_id}
    # Only the a-b edge should survive
    assert len(sub["edges"]) == 1, "Collection must not be empty"


def test_get_subgraph_with_none_returns_empty():
    m = MentalMappingModel()
    m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    sub = m.get_subgraph()
    assert sub == {"nodes": {}, "edges": {}}


# ---------------------------------------------------------------------------
# shortest_path edge cases
# ---------------------------------------------------------------------------
def test_shortest_path_returns_none_for_missing_endpoints():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    assert m.shortest_path(start_id=a.node_id, end_id="nope") is None
    assert m.shortest_path(start_id="nope", end_id=a.node_id) is None
    assert m.shortest_path() is None, "Condition must be true"


def test_shortest_path_same_node_with_node_object_returns_nodes():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    path = m.shortest_path(source=a, target=a)
    assert path == [a], "path is not valid"


def test_shortest_path_with_node_objects_returns_nodes():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    b = m.create_node(NodeType.CONCEPT, content="b", confidence=0.9)
    c = m.create_node(NodeType.CONCEPT, content="c", confidence=0.9)
    m.connect_nodes(a.node_id, b.node_id, edge_type=EdgeType.RELATED)
    m.connect_nodes(b.node_id, c.node_id, edge_type=EdgeType.RELATED)
    path = m.shortest_path(source=a, target=c)
    assert path == [a, b, c]


def test_shortest_path_no_connection_returns_none():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    b = m.create_node(NodeType.CONCEPT, content="b", confidence=0.9)
    assert m.shortest_path(start_id=a.node_id, end_id=b.node_id) is None


# ---------------------------------------------------------------------------
# bfs / dfs aliases and empty inputs
# ---------------------------------------------------------------------------
def test_bfs_dfs_alias_and_missing_node():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    b = m.create_node(NodeType.CONCEPT, content="b", confidence=0.9)
    m.connect_nodes(a.node_id, b.node_id, edge_type=EdgeType.RELATED)

    assert m.bfs() == [], "Condition must be true"
    assert m.bfs(start_id="nope") == [], "Condition must be true"
    assert set(m.bfs(start_id=a.node_id)) == {a.node_id, b.node_id}

    assert m.dfs() == [], "Condition must be true"
    assert m.dfs(start_id="nope") == [], "Condition must be true"
    assert set(m.dfs(start_id=a.node_id)) == {a.node_id, b.node_id}


# ---------------------------------------------------------------------------
# Metrics & centrality
# ---------------------------------------------------------------------------
def test_calculate_metrics_and_centrality():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    b = m.create_node(NodeType.CONCEPT, content="b", confidence=0.9)
    c = m.create_node(NodeType.CONCEPT, content="c", confidence=0.9)
    m.connect_nodes(a.node_id, b.node_id, edge_type=EdgeType.RELATED)
    m.connect_nodes(a.node_id, c.node_id, edge_type=EdgeType.RELATED)

    metrics = m.calculate_metrics()
    assert metrics["num_nodes"] == 3, "Condition must be true"
    assert metrics["num_edges"] == 2, "Condition must be true"
    assert metrics["density"] > 0, "Value must be greater than zero"
    assert metrics["avg_degree"] > 0, "Value must be greater than zero"
    assert NodeType.CONCEPT in metrics["nodes_by_type"], "Condition must be true"

    # a is connected to both b and c → centrality = 2/(3-1) = 1.0
    assert m.get_node_centrality(a.node_id) == pytest.approx(1.0), "Condition must be true"
    assert m.get_node_centrality("missing") == 0.0, "Condition must be true"


def test_get_node_centrality_single_node_returns_zero():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    assert m.get_node_centrality(a.node_id) == 0.0, "Condition must be true"


# ---------------------------------------------------------------------------
# get_connected_nodes
# ---------------------------------------------------------------------------
def test_get_connected_nodes_in_and_out_edges():
    m = MentalMappingModel()
    a = m.create_node(NodeType.CONCEPT, content="a", confidence=0.9)
    b = m.create_node(NodeType.CONCEPT, content="b", confidence=0.9)
    c = m.create_node(NodeType.CONCEPT, content="c", confidence=0.9)
    m.connect_nodes(a.node_id, b.node_id, edge_type=EdgeType.RELATED)
    m.connect_nodes(c.node_id, a.node_id, edge_type=EdgeType.RELATED)
    connected = {n.node_id for n in m.get_connected_nodes(a.node_id)}
    assert connected == {b.node_id, c.node_id}
    # Missing node → empty
    assert m.get_connected_nodes("nope") == [], "Condition must be true"


# ---------------------------------------------------------------------------
# Save/load round trip including a node marked needs_review
# ---------------------------------------------------------------------------
def test_save_and_load_mental_map_roundtrip(tmp_path: Path):
    src = MentalMappingModel(agent_id="src_agent")
    a = src.create_node(NodeType.PROBLEM, content="problem!", confidence=0.9)
    b = src.create_node(NodeType.HYPOTHESIS, content="hypo", confidence=0.3)  # low-conf
    a.add_reasoning_step(
        thought="reason 1", reasoning_type="deductive", confidence=0.8, evidence=["x"]
    )
    src.connect_nodes(a.node_id, b.node_id, edge_type=EdgeType.LEADS_TO, weight=0.5)

    out = tmp_path / "mm.json"
    src.save_mental_map(out)
    assert out.exists(), "Condition must be true"

    loaded_data = json.loads(out.read_text())
    assert loaded_data["agent_id"] == "src_agent", "Data must not be empty"

    dst = MentalMappingModel(agent_id="other")
    dst.load_mental_map(out)
    assert dst.agent_id == "src_agent", "agent_id is not valid"
    assert set(dst.nodes.keys()) == {a.node_id, b.node_id}
    # Low-confidence node was needs_review → must be re-added to review set
    assert b.node_id in dst.nodes_needing_review, "Condition must be true"
    # Reasoning steps preserved
    loaded_a = dst.nodes[a.node_id]
    assert len(loaded_a.reasoning_chain) == 1, "Collection must not be empty"
    assert loaded_a.reasoning_chain[0].thought == "reason 1", "thought is not valid"
    # Edge restored with correct EdgeType
    assert any(edge.edge_type == EdgeType.LEADS_TO for edge in dst.edges.values()), "Value must be initialized"


def test_save_and_load_via_aliases(tmp_path: Path):
    src = MentalMappingModel(agent_id="alias_agent")
    src.create_node(NodeType.GOAL, content="g", confidence=0.9)
    out = tmp_path / "mm2.json"
    src.save(out)
    dst = MentalMappingModel()
    dst.load(out)
    assert dst.agent_id == "alias_agent", "agent_id is not valid"


# ---------------------------------------------------------------------------
# Module-level aliases
# ---------------------------------------------------------------------------
def test_module_aliases():
    assert mm.MentalMap is mm.MentalMappingModel, "MentalMap is not valid"
    assert mm.MentalMapping is mm.MentalMappingModel, "MentalMapping is not valid"
