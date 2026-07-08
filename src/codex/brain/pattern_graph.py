"""
Pattern Knowledge Graph

Constructs and maintains a knowledge graph of discovered patterns
with relationships for rapid retrieval and analysis.

PHASE 10.2: Pattern Graph Construction
Status: Production Ready
"""

import logging
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PatternNode:
    """Represents a pattern in the knowledge graph."""

    id: str
    name: str
    pattern_type: str
    description: str
    confidence: float
    frequency: int
    success_rate: float
    tags: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PatternNode):
            return False
        return self.id == other.id


@dataclass
class PatternEdge:
    """Represents a relationship between patterns."""

    source_id: str
    target_id: str
    relationship_type: str  # "causes", "mitigates", "correlates_with", "precedes"
    weight: float  # 0.0 - 1.0 confidence
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PatternGraph:
    """
    Knowledge graph of patterns with relationships.

    Structure:
    - Nodes: Individual patterns
    - Edges: Relationships with confidence weights
    - Metadata: Pattern properties and metrics

    Operations:
    - Add nodes and edges
    - Query related patterns
    - Compute graph metrics
    - Export to GraphML
    """

    def __init__(self) -> None:
        """Initialize empty graph."""
        self.nodes: dict[str, PatternNode] = {}
        self.edges: list[PatternEdge] = []
        self.adjacency: dict[str, list[PatternEdge]] = defaultdict(list)
        self.reverse_adjacency: dict[str, list[PatternEdge]] = defaultdict(list)

    def add_node(self, node: PatternNode) -> None:
        """Add a pattern node to the graph."""
        self.nodes[node.id] = node
        logger.debug(f"Added node: {node.id}")

    def add_edge(self, edge: PatternEdge) -> None:
        """Add a relationship edge to the graph."""
        # Validate nodes exist
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            logger.warning(f"Cannot add edge: missing nodes {edge.source_id} or {edge.target_id}")
            return

        self.edges.append(edge)
        self.adjacency[edge.source_id].append(edge)
        self.reverse_adjacency[edge.target_id].append(edge)

        logger.debug(f"Added edge: {edge.source_id} -> {edge.target_id}")

    def get_related_patterns(self, pattern_id: str, depth: int = 1) -> list[PatternNode]:
        """
        Get patterns related to a given pattern.

        Traverses graph up to specified depth.
        """
        visited = set()
        to_visit = deque([(pattern_id, 0)])
        related = []

        while to_visit:
            current_id, current_depth = to_visit.popleft()

            if current_id in visited or current_depth > depth:
                continue

            visited.add(current_id)

            # Add outgoing related patterns
            for edge in self.adjacency.get(current_id, []):
                target_id = edge.target_id
                if target_id not in visited:
                    if target_id != pattern_id:  # Don't include source
                        related.append(self.nodes[target_id])
                    if current_depth < depth:
                        to_visit.append((target_id, current_depth + 1))

        return related

    def find_causal_chains(self, pattern_id: str, max_length: int = 5) -> list[list[str]]:
        """
        Find causal chains starting from a pattern.

        Returns chains of causally related patterns.
        """
        chains = []

        def dfs(current_id: str, chain: list[str], length: int) -> None:
            if length >= max_length:
                return

            for edge in self.adjacency.get(current_id, []):
                if edge.relationship_type == "causes":
                    new_chain = chain + [edge.target_id]
                    chains.append(new_chain)
                    dfs(edge.target_id, new_chain, length + 1)

        dfs(pattern_id, [pattern_id], 0)
        return chains

    def find_mitigation_paths(self, risk_pattern_id: str) -> list[list[str]]:
        """
        Find patterns that mitigate a given risk pattern.

        Returns paths to mitigation patterns.
        """
        paths = []
        visited = set()

        def dfs(current_id: str, path: list[str]) -> None:
            if current_id in visited:
                return
            visited.add(current_id)

            for edge in self.adjacency.get(current_id, []):
                if edge.relationship_type == "mitigates":
                    new_path = path + [edge.target_id]
                    paths.append(new_path)
                    dfs(edge.target_id, new_path)

        dfs(risk_pattern_id, [risk_pattern_id])
        return paths

    def query_patterns(self, query: dict[str, Any]) -> list[PatternNode]:
        """
        Query patterns by various criteria.

        Query can include:
        - pattern_type: Filter by type
        - min_confidence: Minimum confidence threshold
        - min_frequency: Minimum frequency
        - tags: Include patterns with specific tags
        """
        results = []

        for node in self.nodes.values():
            # Apply filters
            if "pattern_type" in query and node.pattern_type != query["pattern_type"]:
                continue

            if "min_confidence" in query and node.confidence < query["min_confidence"]:
                continue

            if "min_frequency" in query and node.frequency < query["min_frequency"]:
                continue

            if "tags" in query:
                required_tags = set(query["tags"])
                node_tags = set(node.tags)
                if not required_tags.issubset(node_tags):
                    continue

            results.append(node)

        return results

    def compute_node_metrics(self, node_id: str) -> dict[str, Any]:
        """Compute graph metrics for a node."""
        if node_id not in self.nodes:
            return {}

        node = self.nodes[node_id]

        # Degree metrics
        outgoing = len(self.adjacency.get(node_id, []))
        incoming = len(self.reverse_adjacency.get(node_id, []))

        # Weighted metrics
        outgoing_weight = sum(e.weight for e in self.adjacency.get(node_id, []))
        incoming_weight = sum(e.weight for e in self.reverse_adjacency.get(node_id, []))

        # Centrality (simplified)
        total_nodes = len(self.nodes)
        centrality = (outgoing + incoming) / max(total_nodes - 1, 1) if total_nodes > 1 else 0

        return {
            "node_id": node_id,
            "outgoing_edges": outgoing,
            "incoming_edges": incoming,
            "total_edges": outgoing + incoming,
            "outgoing_weight": outgoing_weight,
            "incoming_weight": incoming_weight,
            "centrality": centrality,
            "node_confidence": node.confidence,
            "node_frequency": node.frequency,
        }

    def compute_graph_metrics(self) -> dict[str, Any]:
        """Compute overall graph metrics."""
        num_nodes = len(self.nodes)
        num_edges = len(self.edges)

        if num_nodes == 0:
            return {
                "nodes": 0,
                "edges": 0,
                "density": 0.0,
                "avg_degree": 0.0,
                "type_distribution": {},
            }

        # Graph density
        max_edges = num_nodes * (num_nodes - 1) / 2
        density = num_edges / max_edges if max_edges > 0 else 0

        # Average degree
        degrees = [
            len(self.adjacency.get(nid, [])) + len(self.reverse_adjacency.get(nid, []))
            for nid in self.nodes
        ]
        avg_degree = sum(degrees) / num_nodes if num_nodes > 0 else 0

        # Type distribution
        type_dist = defaultdict(int)  # type: ignore[var-annotated]
        for node in self.nodes.values():
            type_dist[node.pattern_type] += 1

        # Relationship type distribution
        rel_dist = defaultdict(int)  # type: ignore[var-annotated]
        for edge in self.edges:
            rel_dist[edge.relationship_type] += 1

        return {
            "nodes": num_nodes,
            "edges": num_edges,
            "density": density,
            "avg_degree": avg_degree,
            "type_distribution": dict(type_dist),
            "relationship_distribution": dict(rel_dist),
            "avg_node_confidence": (
                sum(n.confidence for n in self.nodes.values()) / num_nodes if num_nodes > 0 else 0
            ),
            "avg_node_frequency": (
                sum(n.frequency for n in self.nodes.values()) / num_nodes if num_nodes > 0 else 0
            ),
        }

    def export_graphml(self) -> str:
        """Export graph to GraphML format."""
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">')
        lines.append('  <graph id="pattern_graph" edgedefault="directed">')

        # Define node attributes
        lines.append('    <key id="name" for="node" attr.name="name" attr.type="string"/>')
        lines.append('    <key id="type" for="node" attr.name="type" attr.type="string"/>')
        lines.append(
            '    <key id="confidence" for="node" attr.name="confidence" attr.type="double"/>'
        )
        lines.append('    <key id="frequency" for="node" attr.name="frequency" attr.type="int"/>')
        lines.append(
            '    <key id="success_rate" for="node" attr.name="success_rate" attr.type="double"/>'
        )

        # Define edge attributes
        lines.append(
            '    <key id="relationship" for="edge" attr.name="relationship" attr.type="string"/>'
        )
        lines.append('    <key id="weight" for="edge" attr.name="weight" attr.type="double"/>')

        # Add nodes
        for node_id, node in self.nodes.items():
            lines.append(f'    <node id="{node_id}">')
            lines.append(f'      <data key="name">{self._escape_xml(node.name)}</data>')
            lines.append(f'      <data key="type">{node.pattern_type}</data>')
            lines.append(f'      <data key="confidence">{node.confidence}</data>')
            lines.append(f'      <data key="frequency">{node.frequency}</data>')
            lines.append(f'      <data key="success_rate">{node.success_rate}</data>')
            lines.append("    </node>")

        # Add edges
        for i, edge in enumerate(self.edges):
            lines.append(
                f'    <edge id="e{i}" source="{edge.source_id}" target="{edge.target_id}">'
            )
            lines.append(f'      <data key="relationship">{edge.relationship_type}</data>')
            lines.append(f'      <data key="weight">{edge.weight}</data>')
            lines.append("    </edge>")

        lines.append("  </graph>")
        lines.append("</graphml>")

        return "\n".join(lines)

    def export_json(self) -> dict[str, Any]:
        """Export graph to JSON format."""
        nodes_data = []
        for node_id, node in self.nodes.items():
            node_dict = asdict(node)
            node_dict["created_at"] = node.created_at.isoformat()
            node_dict["last_accessed"] = node.last_accessed.isoformat()
            nodes_data.append(node_dict)

        edges_data = []
        for edge in self.edges:
            edge_dict = asdict(edge)
            edge_dict["created_at"] = edge.created_at.isoformat()
            edges_data.append(edge_dict)

        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "metrics": self.compute_graph_metrics(),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters."""
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        return text


class GraphBuilder:
    """Builds pattern graphs from discovered patterns."""

    def __init__(self) -> None:
        """Initialize graph builder."""
        self.graph = PatternGraph()

    def add_patterns(self, patterns: list[Any]) -> None:
        """Add patterns as nodes to graph."""
        for pattern in patterns:
            node = PatternNode(
                id=pattern.id,
                name=pattern.name,
                pattern_type=pattern.pattern_type.value,
                description=pattern.description,
                confidence=pattern.confidence,
                frequency=pattern.frequency,
                success_rate=pattern.success_rate,
                tags=pattern.tags if hasattr(pattern, "tags") else [],
                metrics=pattern.metrics if hasattr(pattern, "metrics") else {},
                created_at=(
                    pattern.first_seen
                    if hasattr(pattern, "first_seen")
                    else datetime.now(timezone.utc)
                ),
            )
            self.graph.add_node(node)

    def connect_similar_patterns(self, threshold: float = 0.7) -> int:
        """Connect similar patterns based on features."""
        added_edges = 0
        nodes_list = list(self.graph.nodes.values())

        for i, source in enumerate(nodes_list):
            for target in nodes_list[i + 1 :]:
                if source.id == target.id:
                    continue

                similarity = self._calculate_similarity(source, target)

                if similarity >= threshold:
                    edge = PatternEdge(
                        source_id=source.id,
                        target_id=target.id,
                        relationship_type="correlates_with",
                        weight=similarity,
                    )
                    self.graph.add_edge(edge)
                    added_edges += 1

        return added_edges

    def connect_causal_patterns(self) -> int:
        """Connect patterns with causal relationships."""
        added_edges = 0

        for source_id, source in self.graph.nodes.items():
            for target_id, target in self.graph.nodes.items():
                if source_id == target_id:
                    continue

                # Check for causal relationship
                if self._is_causal(source, target):
                    edge = PatternEdge(
                        source_id=source_id,
                        target_id=target_id,
                        relationship_type="causes",
                        weight=0.8,  # High confidence for causal
                    )
                    self.graph.add_edge(edge)
                    added_edges += 1

        return added_edges

    @staticmethod
    def _calculate_similarity(node1: PatternNode, node2: PatternNode) -> float:
        """Calculate similarity between two nodes."""
        score = 0.0

        # Type similarity (0.3)
        if node1.pattern_type == node2.pattern_type:
            score += 0.3

        # Tag overlap (0.3)
        if node1.tags and node2.tags:
            overlap = len(set(node1.tags) & set(node2.tags))
            max_tags = max(len(node1.tags), len(node2.tags))
            score += (overlap / max_tags) * 0.3

        # Confidence proximity (0.2)
        conf_diff = abs(node1.confidence - node2.confidence)
        score += (1 - min(conf_diff, 1.0)) * 0.2

        # Success rate proximity (0.2)
        sr_diff = abs(node1.success_rate - node2.success_rate)
        score += (1 - min(sr_diff, 1.0)) * 0.2

        return score

    @staticmethod
    def _is_causal(source: PatternNode, target: PatternNode) -> bool:
        """Determine if source pattern causes target pattern."""
        # Check for common tags indicating causality
        set(source.tags) if source.tags else set()
        set(target.tags) if target.tags else set()

        # Causal indicators
        causal_indicators = {
            ("error", "success"),  # Fixing error leads to success
            ("decision", "performance"),  # Decision impacts performance
            ("risk", "error"),  # Risk leads to error
        }

        for source_type, target_type in causal_indicators:
            if source_type in source.pattern_type and target_type in target.pattern_type:
                return True

        return False

    def build_complete_graph(self, patterns: list[Any]) -> PatternGraph:
        """Build complete graph from patterns."""
        # Add all patterns as nodes
        self.add_patterns(patterns)

        # Connect similar patterns
        similar_edges = self.connect_similar_patterns(threshold=0.7)
        logger.info(f"Connected {similar_edges} similar patterns")

        # Connect causal patterns
        causal_edges = self.connect_causal_patterns()
        logger.info(f"Connected {causal_edges} causal patterns")

        return self.graph

    def get_graph(self) -> PatternGraph:
        """Get the constructed graph."""
        return self.graph
