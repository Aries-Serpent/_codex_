"""Knowledge Graph Export System.

Exports AST analysis results to multiple formats for tooling integration.
Design: FR-AST-011 (Knowledge Graph Exporter)

Supported formats:
- JSON: Standard JSON with full metadata
- GraphML: Graph interchange format for visualization tools
- DOT: Graphviz format for graph rendering
- SQLite: Relational database for querying
- Markdown: Human-readable documentation
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
import sqlite3  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from enum import Enum  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

from .graph import DependencyGraph  # noqa: E402
from .metrics import MetricsAggregator  # noqa: E402
from .node import StandardizedASTNode  # noqa: E402


class ExportFormat(Enum):
    """Supported export formats."""

    JSON = "json"
    GRAPHML = "graphml"
    DOT = "dot"
    SQLITE = "sqlite"
    MARKDOWN = "markdown"


@dataclass
class ExportResult:
    """Result of export operation."""

    format: ExportFormat
    output_path: Optional[Path]
    content: Optional[str]
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "format": self.format.value,
            "output_path": str(self.output_path) if self.output_path else None,
            "success": self.success,
            "error": self.error,
        }


class KnowledgeGraphExporter:
    """Export AST analysis to multiple formats.

    Supports exporting:
    - AST node trees
    - Dependency graphs
    - Code metrics
    - Combined knowledge graphs
    """

    def __init__(self) -> None:
        """Initialize exporter."""
        self.nodes: list[StandardizedASTNode] = []
        self.graph: Optional[DependencyGraph] = None
        self.metrics: Optional[MetricsAggregator] = None
        self.metadata: dict[str, Any] = {}

    def add_node(self, node: StandardizedASTNode) -> None:
        """Add AST node to export set."""
        self.nodes.append(node)

    def add_nodes(self, nodes: list[StandardizedASTNode]) -> None:
        """Add multiple AST nodes."""
        self.nodes.extend(nodes)

    def set_graph(self, graph: DependencyGraph) -> None:
        """set dependency graph for export."""
        self.graph = graph

    def set_metrics(self, metrics: MetricsAggregator) -> None:
        """set metrics aggregator for export."""
        self.metrics = metrics

    def set_metadata(self, key: str, value: Any) -> None:
        """set metadata for export."""
        self.metadata[key] = value

    def export(
        self,
        format: ExportFormat,
        output_path: Optional[str | Path] = None,
    ) -> ExportResult:
        """Export to specified format.

        Args:
            format: Target export format
            output_path: Optional output file path

        Returns:
            ExportResult with status and content/path
        """
        output_path = Path(output_path) if output_path else None

        try:
            if format == ExportFormat.JSON:
                content = self._export_json()
            elif format == ExportFormat.GRAPHML:
                content = self._export_graphml()
            elif format == ExportFormat.DOT:
                content = self._export_dot()
            elif format == ExportFormat.SQLITE:
                if not output_path:
                    return ExportResult(
                        format=format,
                        output_path=None,
                        content=None,
                        success=False,
                        error="SQLite export requires output_path",
                    )
                self._export_sqlite(output_path)
                return ExportResult(
                    format=format,
                    output_path=output_path,
                    content=None,
                    success=True,
                )
            elif format == ExportFormat.MARKDOWN:
                content = self._export_markdown()
            else:
                return ExportResult(
                    format=format,
                    output_path=output_path,
                    content=None,
                    success=False,
                    error=f"Unsupported format: {format}",
                )

            if output_path:
                output_path.write_text(content, encoding="utf-8")

            return ExportResult(
                format=format,
                output_path=output_path,
                content=content if not output_path else None,
                success=True,
            )

        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.debug("Exception caught, returning", exc_info=True)
            return ExportResult(
                format=format,
                output_path=output_path,
                content=None,
                success=False,
                error=str(e),
            )

    def _export_json(self) -> str:
        """Export to JSON format."""
        data = {
            "version": "1.0",
            "metadata": self.metadata,
            "nodes": [self._node_to_full_dict(n) for n in self.nodes],
            "graph": self._graph_to_dict() if self.graph else None,
            "metrics": self._metrics_to_dict() if self.metrics else None,
        }
        return json.dumps(data, indent=2, default=str)

    def _node_to_full_dict(self, node: StandardizedASTNode) -> dict[str, Any]:
        """Convert node and all children to dictionary."""
        data = node.to_dict()
        data["children_full"] = [self._node_to_full_dict(child) for child in node.children]
        return data

    def _graph_to_dict(self) -> dict[str, Any]:
        """Convert dependency graph to dictionary."""
        if not self.graph:
            return {}

        edges = []
        for source, targets in self.graph.edges.items():
            for target in targets:
                edges.append({"source": source, "target": target})

        return {
            "nodes": list(self.graph.nodes),
            "edges": edges,
            "cycles": self.graph.detect_cycles(),
        }

    def _metrics_to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        if not self.metrics:
            return {}

        return {
            "summary": self.metrics.summary(),
            "entities": {
                entity_id: metrics.to_dict() for entity_id, metrics in self.metrics.metrics.items()
            },
        }

    def _export_graphml(self) -> str:
        """Export to GraphML format for visualization tools."""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
            '  <key id="name" for="node" attr.name="name" attr.type="string"/>',
            '  <key id="type" for="node" attr.name="type" attr.type="string"/>',
            '  <key id="file" for="node" attr.name="file" attr.type="string"/>',
            '  <graph id="G" edgedefault="directed">',
        ]

        # Export nodes
        node_ids = set()
        for node in self.nodes:
            for n in node.walk():
                if n.node_id not in node_ids:
                    node_ids.add(n.node_id)
                    lines.append(f'    <node id="{n.node_id}">')
                    lines.append(f'      <data key="name">{_escape_xml(n.name)}</data>')
                    lines.append(f'      <data key="type">{n.type.value}</data>')
                    lines.append(
                        f'      <data key="file">{_escape_xml(str(n.source_location.file_path))}</data>'  # noqa: E501
                    )
                    lines.append("    </node>")

        # Export edges from graph
        if self.graph:
            edge_id = 0
            for source, targets in self.graph.edges.items():
                for target in targets:
                    lines.append(f'    <edge id="e{edge_id}" source="{source}" target="{target}"/>')
                    edge_id += 1

        # Export parent-child edges
        for node in self.nodes:
            for n in node.walk():
                for child in n.children:
                    lines.append(f'    <edge source="{n.node_id}" target="{child.node_id}"/>')

        lines.append("  </graph>")
        lines.append("</graphml>")

        return "\n".join(lines)

    def _export_dot(self) -> str:
        """Export to DOT (Graphviz) format."""
        lines = [
            "digraph KnowledgeGraph {",
            "  rankdir=TB;",
            "  node [shape=box, style=filled];",
        ]

        # Node colors by type
        type_colors = {
            "module": "#E8F5E9",
            "function": "#E3F2FD",
            "async_function": "#E1F5FE",
            "class": "#FFF3E0",
            "import": "#F3E5F5",
            "from_import": "#F3E5F5",
        }

        # Export nodes
        node_ids = set()
        for node in self.nodes:
            for n in node.walk():
                if n.node_id not in node_ids:
                    node_ids.add(n.node_id)
                    color = type_colors.get(n.type.value, "#FFFFFF")
                    label = f"{n.type.value}\\n{n.name}"
                    lines.append(f'  "{n.node_id}" [label="{label}", fillcolor="{color}"];')

        # Export dependency edges (red for cycles)
        if self.graph:
            cycles = self.graph.detect_cycles()
            cycle_edges = set()
            for cycle in cycles:
                for i in range(len(cycle)):
                    cycle_edges.add((cycle[i], cycle[(i + 1) % len(cycle)]))

            for source, targets in self.graph.edges.items():
                for target in targets:
                    if (source, target) in cycle_edges:
                        lines.append(f'  "{source}" -> "{target}" [color=red, penwidth=2];')
                    else:
                        lines.append(f'  "{source}" -> "{target}";')

        # Export parent-child edges (dashed)
        for node in self.nodes:
            for n in node.walk():
                for child in n.children:
                    lines.append(
                        f'  "{n.node_id}" -> "{child.node_id}" [style=dashed, color=gray];'
                    )

        lines.append("}")

        return "\n".join(lines)

    def _export_sqlite(self, output_path: Path) -> None:
        """Export to SQLite database."""
        # Remove existing database
        if output_path.exists():
            output_path.unlink()

        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE nodes (
                node_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                file_path TEXT,
                line_start INTEGER,
                line_end INTEGER,
                docstring TEXT,
                parent_id TEXT,
                FOREIGN KEY (parent_id) REFERENCES nodes(node_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                edge_type TEXT DEFAULT 'dependency',
                FOREIGN KEY (source) REFERENCES nodes(node_id),
                FOREIGN KEY (target) REFERENCES nodes(node_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE metrics (
                entity_id TEXT PRIMARY KEY,
                cyclomatic_complexity INTEGER,
                cognitive_complexity REAL,
                lines_of_code INTEGER,
                comment_lines INTEGER,
                maintainability_index REAL,
                quality_tier TEXT,
                FOREIGN KEY (entity_id) REFERENCES nodes(node_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_nodes TEXT NOT NULL
            )
        """)

        # Insert metadata
        for key, value in self.metadata.items():
            cursor.execute(
                "INSERT INTO metadata (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )

        # Insert nodes
        for node in self.nodes:
            for n in node.walk():
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO nodes
                    (node_id, type, name, file_path, line_start, line_end, docstring, parent_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        n.node_id,
                        n.type.value,
                        n.name,
                        str(n.source_location.file_path),
                        n.source_location.line_start,
                        n.source_location.line_end,
                        n.docstring,
                        n.parent.node_id if n.parent else None,
                    ),
                )

        # Insert edges
        if self.graph:
            for source, targets in self.graph.edges.items():
                for target in targets:
                    cursor.execute(
                        "INSERT INTO edges (source, target) VALUES (?, ?)",
                        (source, target),
                    )

            # Insert cycles
            for cycle in self.graph.detect_cycles():
                cursor.execute(
                    "INSERT INTO cycles (cycle_nodes) VALUES (?)",
                    (json.dumps(cycle),),
                )

        # Insert metrics
        if self.metrics:
            for entity_id, m in self.metrics.metrics.items():
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO metrics
                    (entity_id, cyclomatic_complexity, cognitive_complexity,
                     lines_of_code, comment_lines, maintainability_index, quality_tier)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        entity_id,
                        m.cyclomatic_complexity,
                        m.cognitive_complexity,
                        m.lines_of_code,
                        m.comment_lines,
                        m.maintainability_index,
                        m.quality_tier,
                    ),
                )

        # Create indexes for performance
        cursor.execute("CREATE INDEX idx_nodes_type ON nodes(type)")
        cursor.execute("CREATE INDEX idx_nodes_file ON nodes(file_path)")
        cursor.execute("CREATE INDEX idx_edges_source ON edges(source)")
        cursor.execute("CREATE INDEX idx_edges_target ON edges(target)")

        conn.commit()
        conn.close()

    def _export_markdown(self) -> str:
        """Export to Markdown documentation format."""
        lines = [
            "# Code Knowledge Graph",
            "",
            "## Overview",
            "",
        ]

        # Metadata
        if self.metadata:
            lines.append("### Metadata")
            lines.append("")
            lines.append("| Key | Value |")
            lines.append("|-----|-------|")
            for key, value in self.metadata.items():
                lines.append(f"| {key} | {value} |")
            lines.append("")

        # Node summary
        lines.append("## Code Structure")
        lines.append("")

        type_counts: dict[str, int] = {}
        for node in self.nodes:
            for n in node.walk():
                type_counts[n.type.value] = type_counts.get(n.type.value, 0) + 1

        if type_counts:
            lines.append("### Node Types")
            lines.append("")
            lines.append("| Type | Count |")
            lines.append("|------|-------|")
            for node_type, count in sorted(type_counts.items()):
                lines.append(f"| {node_type} | {count} |")
            lines.append("")

        # list top-level nodes
        lines.append("### Modules")
        lines.append("")
        for node in self.nodes:
            lines.append(f"- **{node.name}** (`{node.source_location.file_path}`)")
            for child in node.children:
                lines.append(f"  - {child.type.value}: `{child.name}`")
        lines.append("")

        # Graph analysis
        if self.graph:
            lines.append("## Dependency Analysis")
            lines.append("")
            lines.append(f"- **Total nodes**: {len(self.graph.nodes)}")
            lines.append(f"- **Total edges**: {sum(len(t) for t in self.graph.edges.values())}")

            cycles = self.graph.detect_cycles()
            if cycles:
                lines.append(f"- **Cycles detected**: {len(cycles)}")
                lines.append("")
                lines.append("### Circular Dependencies")
                lines.append("")
                for i, cycle in enumerate(cycles, 1):
                    lines.append(f"{i}. {' → '.join(cycle)} → {cycle[0]}")
            else:
                lines.append("- **Cycles detected**: None ✓")
            lines.append("")

        # Metrics summary
        if self.metrics:
            summary = self.metrics.summary()
            if summary:
                lines.append("## Metrics Summary")
                lines.append("")
                lines.append("| Metric | Value |")
                lines.append("|--------|-------|")
                for key, value in summary.items():
                    if isinstance(value, float):
                        lines.append(f"| {key} | {value:.2f} |")
                    else:
                        lines.append(f"| {key} | {value} |")
                lines.append("")

        return "\n".join(lines)


def _escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# Convenience function
def export_knowledge_graph(
    nodes: list[StandardizedASTNode],
    format: ExportFormat = ExportFormat.JSON,
    output_path: Optional[str | Path] = None,
    graph: Optional[DependencyGraph] = None,
    metrics: Optional[MetricsAggregator] = None,
) -> ExportResult:
    """Export AST nodes to specified format.

    Args:
        nodes: list of AST nodes to export
        format: Target format
        output_path: Optional output file path
        graph: Optional dependency graph
        metrics: Optional metrics aggregator

    Returns:
        ExportResult with status and content
    """
    exporter = KnowledgeGraphExporter()
    exporter.add_nodes(nodes)

    if graph:
        exporter.set_graph(graph)
    if metrics:
        exporter.set_metrics(metrics)

    return exporter.export(format, output_path)
