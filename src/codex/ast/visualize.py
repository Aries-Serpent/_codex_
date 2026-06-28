"""
HTML visualization generator for AST analysis.
"""

import json
from pathlib import Path
from typing import Any

from .graph import ASTGraph
from .node import StandardizedASTNode


class HTMLVisualizer:
    """Generate interactive HTML visualizations of AST."""

    def __init__(self) -> None:
        """Initialize visualizer."""
        self.template_dir = Path(__file__).parent / "templates"

    def render_html(
        self,
        nodes: list[StandardizedASTNode],
        graph: ASTGraph,
        metrics: dict[str, Any],
        output_path: str,
    ) -> None:
        """
        Generate HTML report.

        Args:
            nodes: list of AST nodes
            graph: AST graph
            metrics: Metrics dictionary
            output_path: Path to save HTML file
        """
        # Prepare data
        nodes_data = [self._node_to_dict(n) for n in nodes[:100]]  # Limit for performance

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>AST Analysis Report</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <!-- d3.js visualization library (d3.v7) -->
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric-card {{ background: #f9f9f9; padding: 15px; border-radius: 4px; border-left: 4px solid #4CAF50; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; margin-top: 5px; }}
        .node {{ fill: #69b3a2; stroke: #333; stroke-width: 2px; cursor: pointer; }}
        .node:hover {{ fill: #4CAF50; }}
        .link {{ stroke: #999; stroke-opacity: 0.6; }}
        #graph {{ border: 1px solid #ddd; background: white; margin: 20px 0; }}
        .legend {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 AST Analysis Report</h1>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total Nodes</div>
                <div class="metric-value">{len(nodes)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Complexity</div>
                <div class="metric-value">{metrics.get("complexity", "N/A")}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if "function" in n.get("type", "").lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if "class" in n.get("type", "").lower())}</div>
            </div>
        </div>

        <div class="legend">
            <strong>Legend:</strong> Hover over nodes to see details. Circle size represents complexity.
        </div>

        <div id="graph"></div>

        <script>
        const data = {json.dumps(nodes_data, indent=2)};

        // Create D3 visualization
        const width = 1160;
        const height = 600;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        // Simple node visualization
        const nodes = svg.selectAll("circle")
            .data(data)
            .enter()
            .append("circle")
            .attr("cx", (d, i) => (i % 10) * 116 + 58)
            .attr("cy", (d, i) => Math.floor(i / 10) * 60 + 40)
            .attr("r", d => Math.min(20, 10 + (d.children || 0)))
            .attr("class", "node")
            .on("mouseover", function(event, d) {{
                d3.select(this).attr("r", d => Math.min(25, 15 + (d.children || 0)));
            }})
            .on("mouseout", function(event, d) {{
                d3.select(this).attr("r", d => Math.min(20, 10 + (d.children || 0)));
            }});

        nodes.append("title")
            .text(d => 'Type: ' + d.type + '\\nName: ' + (d.name || 'N/A') + '\\nChildren: ' + (d.children || 0));

        // Add labels
        svg.selectAll("text")
            .data(data)
            .enter()
            .append("text")
            .attr("x", (d, i) => (i % 10) * 116 + 58)
            .attr("y", (d, i) => Math.floor(i / 10) * 60 + 65)
            .attr("text-anchor", "middle")
            .attr("font-size", "10px")
            .attr("fill", "#666")
            .text(d => (d.name || d.type).substring(0, 8));
        </script>
    </div>
</body>
</html>
"""  # noqa: E501

        Path(output_path).write_text(html)

    def _node_to_dict(self, node: StandardizedASTNode) -> dict[str, Any]:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.node_id,
            "type": node.type.value if hasattr(node.type, "value") else str(node.type),
            "name": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 0,
        }
