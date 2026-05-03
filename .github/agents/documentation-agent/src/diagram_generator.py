"""
Diagram Generator for Documentation Agent
Creates mermaid diagrams for architecture visualization
"""
import random
from dataclasses import dataclass
from typing import Any

RANDOM_SEED = 48

@dataclass
class DiagramNode:
    """Node in architecture diagram"""
    id: str
    label: str
    type: str  # component, database, service, agent

@dataclass
class DiagramEdge:
    """Edge between nodes"""
    source: str
    target: str
    label: str

class DiagramGenerator:
    """Generate mermaid architecture diagrams"""

    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.nodes: list[DiagramNode] = []
        self.edges: list[DiagramEdge] = []
        self.initialized = True

    def add_node(self, id: str, label: str, type: str = "component") -> DiagramNode:
        """Add node to diagram"""
        node = DiagramNode(id=id, label=label, type=type)
        self.nodes.append(node)
        return node

    def add_edge(self, source: str, target: str, label: str = "") -> DiagramEdge:
        """Add edge between nodes"""
        edge = DiagramEdge(source=source, target=target, label=label)
        self.edges.append(edge)
        return edge

    def generate_mermaid(self, diagram_type: str = "graph") -> str:
        """Generate mermaid diagram syntax"""
        if not self.nodes:
            return "graph TD\n    A[No nodes defined]\n"

        mermaid = f"{diagram_type} TD\n"

        # Add nodes
        for node in self.nodes:
            shape = self._get_node_shape(node.type)
            mermaid += f"    {node.id}{shape[0]}{node.label}{shape[1]}\n"

        # Add edges
        for edge in self.edges:
            arrow = f"-->|{edge.label}|" if edge.label else "-->"
            mermaid += f"    {edge.source} {arrow} {edge.target}\n"

        return mermaid

    def _get_node_shape(self, type: str) -> tuple:
        """Get mermaid shape for node type"""
        shapes = {
            "component": ("[", "]"),
            "database": ("[(", ")]"),
            "service": ("{{", "}}"),
            "agent": ("(", ")")
        }
        return shapes.get(type, ("[", "]"))

    def get_metrics(self) -> dict[str, Any]:
        """Get metrics"""
        return {
            "seed": self.seed,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": {t: sum(1 for n in self.nodes if n.type == t)
                          for t in ["component", "database", "service", "agent"]},
            "initialized": self.initialized
        }

def create_diagram_generator(seed: int = RANDOM_SEED) -> DiagramGenerator:
    """Factory function"""
    return DiagramGenerator(seed=seed)
