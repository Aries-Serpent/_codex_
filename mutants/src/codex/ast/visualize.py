"""
HTML visualization generator for AST analysis.
"""

import json
from pathlib import Path

from .graph import ASTGraph
from .node import StandardizedASTNode
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class HTMLVisualizer:
    """Generate interactive HTML visualizations of AST."""

    def xǁHTMLVisualizerǁ__init____mutmut_orig(self):
        """Initialize visualizer."""
        self.template_dir = Path(__file__).parent / "templates"

    def xǁHTMLVisualizerǁ__init____mutmut_1(self):
        """Initialize visualizer."""
        self.template_dir = None

    def xǁHTMLVisualizerǁ__init____mutmut_2(self):
        """Initialize visualizer."""
        self.template_dir = Path(__file__).parent * "templates"

    def xǁHTMLVisualizerǁ__init____mutmut_3(self):
        """Initialize visualizer."""
        self.template_dir = Path(None).parent / "templates"

    def xǁHTMLVisualizerǁ__init____mutmut_4(self):
        """Initialize visualizer."""
        self.template_dir = Path(__file__).parent / "XXtemplatesXX"

    def xǁHTMLVisualizerǁ__init____mutmut_5(self):
        """Initialize visualizer."""
        self.template_dir = Path(__file__).parent / "TEMPLATES"
    
    xǁHTMLVisualizerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHTMLVisualizerǁ__init____mutmut_1': xǁHTMLVisualizerǁ__init____mutmut_1, 
        'xǁHTMLVisualizerǁ__init____mutmut_2': xǁHTMLVisualizerǁ__init____mutmut_2, 
        'xǁHTMLVisualizerǁ__init____mutmut_3': xǁHTMLVisualizerǁ__init____mutmut_3, 
        'xǁHTMLVisualizerǁ__init____mutmut_4': xǁHTMLVisualizerǁ__init____mutmut_4, 
        'xǁHTMLVisualizerǁ__init____mutmut_5': xǁHTMLVisualizerǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHTMLVisualizerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁHTMLVisualizerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁHTMLVisualizerǁ__init____mutmut_orig)
    xǁHTMLVisualizerǁ__init____mutmut_orig.__name__ = 'xǁHTMLVisualizerǁ__init__'

    def xǁHTMLVisualizerǁrender_html__mutmut_orig(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_1(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
        """
        Generate HTML report.

        Args:
            nodes: list of AST nodes
            graph: AST graph
            metrics: Metrics dictionary
            output_path: Path to save HTML file
        """
        # Prepare data
        nodes_data = None  # Limit for performance

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>AST Analysis Report</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_2(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
        """
        Generate HTML report.

        Args:
            nodes: list of AST nodes
            graph: AST graph
            metrics: Metrics dictionary
            output_path: Path to save HTML file
        """
        # Prepare data
        nodes_data = [self._node_to_dict(None) for n in nodes[:100]]  # Limit for performance

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>AST Analysis Report</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_3(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
        """
        Generate HTML report.

        Args:
            nodes: list of AST nodes
            graph: AST graph
            metrics: Metrics dictionary
            output_path: Path to save HTML file
        """
        # Prepare data
        nodes_data = [self._node_to_dict(n) for n in nodes[:101]]  # Limit for performance

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>AST Analysis Report</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_4(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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

        html = None

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_5(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get(None, 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_6(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', None)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_7(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_8(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', )}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_9(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('XXcomplexityXX', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_10(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('COMPLEXITY', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_11(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'XXN/AXX')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_12(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'n/a')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_13(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(None)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_14(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(2 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_15(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'XXfunctionXX' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_16(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'FUNCTION' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_17(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' not in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_18(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').upper())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_19(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get(None, '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_20(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', None).lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_21(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_22(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', ).lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_23(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('XXtypeXX', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_24(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('TYPE', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_25(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', 'XXXX').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_26(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(None)}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_27(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(2 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_28(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'XXclassXX' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_29(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'CLASS' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_30(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' not in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_31(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').upper())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_32(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get(None, '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_33(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', None).lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_34(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_35(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', ).lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_36(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('XXtypeXX', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_37(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('TYPE', '').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_38(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', 'XXXX').lower())}</div>
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_39(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
            </div>
        </div>
        
        <div class="legend">
            <strong>Legend:</strong> Hover over nodes to see details. Circle size represents complexity.
        </div>
        
        <div id="graph"></div>
        
        <script>
        const data = {json.dumps(None, indent=2)};
        
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_40(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
            </div>
        </div>
        
        <div class="legend">
            <strong>Legend:</strong> Hover over nodes to see details. Circle size represents complexity.
        </div>
        
        <div id="graph"></div>
        
        <script>
        const data = {json.dumps(nodes_data, indent=None)};
        
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_41(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
            </div>
        </div>
        
        <div class="legend">
            <strong>Legend:</strong> Hover over nodes to see details. Circle size represents complexity.
        </div>
        
        <div id="graph"></div>
        
        <script>
        const data = {json.dumps(indent=2)};
        
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_42(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
            </div>
        </div>
        
        <div class="legend">
            <strong>Legend:</strong> Hover over nodes to see details. Circle size represents complexity.
        </div>
        
        <div id="graph"></div>
        
        <script>
        const data = {json.dumps(nodes_data, )};
        
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_43(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
            </div>
        </div>
        
        <div class="legend">
            <strong>Legend:</strong> Hover over nodes to see details. Circle size represents complexity.
        </div>
        
        <div id="graph"></div>
        
        <script>
        const data = {json.dumps(nodes_data, indent=3)};
        
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
"""

        Path(output_path).write_text(html)

    def xǁHTMLVisualizerǁrender_html__mutmut_44(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(output_path).write_text(None)

    def xǁHTMLVisualizerǁrender_html__mutmut_45(
        self, nodes: list[StandardizedASTNode], graph: ASTGraph, metrics: dict, output_path: str
    ):
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
                <div class="metric-value">{metrics.get('complexity', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Functions</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'function' in n.get('type', '').lower())}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Classes</div>
                <div class="metric-value">{sum(1 for n in nodes_data if 'class' in n.get('type', '').lower())}</div>
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
"""

        Path(None).write_text(html)
    
    xǁHTMLVisualizerǁrender_html__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHTMLVisualizerǁrender_html__mutmut_1': xǁHTMLVisualizerǁrender_html__mutmut_1, 
        'xǁHTMLVisualizerǁrender_html__mutmut_2': xǁHTMLVisualizerǁrender_html__mutmut_2, 
        'xǁHTMLVisualizerǁrender_html__mutmut_3': xǁHTMLVisualizerǁrender_html__mutmut_3, 
        'xǁHTMLVisualizerǁrender_html__mutmut_4': xǁHTMLVisualizerǁrender_html__mutmut_4, 
        'xǁHTMLVisualizerǁrender_html__mutmut_5': xǁHTMLVisualizerǁrender_html__mutmut_5, 
        'xǁHTMLVisualizerǁrender_html__mutmut_6': xǁHTMLVisualizerǁrender_html__mutmut_6, 
        'xǁHTMLVisualizerǁrender_html__mutmut_7': xǁHTMLVisualizerǁrender_html__mutmut_7, 
        'xǁHTMLVisualizerǁrender_html__mutmut_8': xǁHTMLVisualizerǁrender_html__mutmut_8, 
        'xǁHTMLVisualizerǁrender_html__mutmut_9': xǁHTMLVisualizerǁrender_html__mutmut_9, 
        'xǁHTMLVisualizerǁrender_html__mutmut_10': xǁHTMLVisualizerǁrender_html__mutmut_10, 
        'xǁHTMLVisualizerǁrender_html__mutmut_11': xǁHTMLVisualizerǁrender_html__mutmut_11, 
        'xǁHTMLVisualizerǁrender_html__mutmut_12': xǁHTMLVisualizerǁrender_html__mutmut_12, 
        'xǁHTMLVisualizerǁrender_html__mutmut_13': xǁHTMLVisualizerǁrender_html__mutmut_13, 
        'xǁHTMLVisualizerǁrender_html__mutmut_14': xǁHTMLVisualizerǁrender_html__mutmut_14, 
        'xǁHTMLVisualizerǁrender_html__mutmut_15': xǁHTMLVisualizerǁrender_html__mutmut_15, 
        'xǁHTMLVisualizerǁrender_html__mutmut_16': xǁHTMLVisualizerǁrender_html__mutmut_16, 
        'xǁHTMLVisualizerǁrender_html__mutmut_17': xǁHTMLVisualizerǁrender_html__mutmut_17, 
        'xǁHTMLVisualizerǁrender_html__mutmut_18': xǁHTMLVisualizerǁrender_html__mutmut_18, 
        'xǁHTMLVisualizerǁrender_html__mutmut_19': xǁHTMLVisualizerǁrender_html__mutmut_19, 
        'xǁHTMLVisualizerǁrender_html__mutmut_20': xǁHTMLVisualizerǁrender_html__mutmut_20, 
        'xǁHTMLVisualizerǁrender_html__mutmut_21': xǁHTMLVisualizerǁrender_html__mutmut_21, 
        'xǁHTMLVisualizerǁrender_html__mutmut_22': xǁHTMLVisualizerǁrender_html__mutmut_22, 
        'xǁHTMLVisualizerǁrender_html__mutmut_23': xǁHTMLVisualizerǁrender_html__mutmut_23, 
        'xǁHTMLVisualizerǁrender_html__mutmut_24': xǁHTMLVisualizerǁrender_html__mutmut_24, 
        'xǁHTMLVisualizerǁrender_html__mutmut_25': xǁHTMLVisualizerǁrender_html__mutmut_25, 
        'xǁHTMLVisualizerǁrender_html__mutmut_26': xǁHTMLVisualizerǁrender_html__mutmut_26, 
        'xǁHTMLVisualizerǁrender_html__mutmut_27': xǁHTMLVisualizerǁrender_html__mutmut_27, 
        'xǁHTMLVisualizerǁrender_html__mutmut_28': xǁHTMLVisualizerǁrender_html__mutmut_28, 
        'xǁHTMLVisualizerǁrender_html__mutmut_29': xǁHTMLVisualizerǁrender_html__mutmut_29, 
        'xǁHTMLVisualizerǁrender_html__mutmut_30': xǁHTMLVisualizerǁrender_html__mutmut_30, 
        'xǁHTMLVisualizerǁrender_html__mutmut_31': xǁHTMLVisualizerǁrender_html__mutmut_31, 
        'xǁHTMLVisualizerǁrender_html__mutmut_32': xǁHTMLVisualizerǁrender_html__mutmut_32, 
        'xǁHTMLVisualizerǁrender_html__mutmut_33': xǁHTMLVisualizerǁrender_html__mutmut_33, 
        'xǁHTMLVisualizerǁrender_html__mutmut_34': xǁHTMLVisualizerǁrender_html__mutmut_34, 
        'xǁHTMLVisualizerǁrender_html__mutmut_35': xǁHTMLVisualizerǁrender_html__mutmut_35, 
        'xǁHTMLVisualizerǁrender_html__mutmut_36': xǁHTMLVisualizerǁrender_html__mutmut_36, 
        'xǁHTMLVisualizerǁrender_html__mutmut_37': xǁHTMLVisualizerǁrender_html__mutmut_37, 
        'xǁHTMLVisualizerǁrender_html__mutmut_38': xǁHTMLVisualizerǁrender_html__mutmut_38, 
        'xǁHTMLVisualizerǁrender_html__mutmut_39': xǁHTMLVisualizerǁrender_html__mutmut_39, 
        'xǁHTMLVisualizerǁrender_html__mutmut_40': xǁHTMLVisualizerǁrender_html__mutmut_40, 
        'xǁHTMLVisualizerǁrender_html__mutmut_41': xǁHTMLVisualizerǁrender_html__mutmut_41, 
        'xǁHTMLVisualizerǁrender_html__mutmut_42': xǁHTMLVisualizerǁrender_html__mutmut_42, 
        'xǁHTMLVisualizerǁrender_html__mutmut_43': xǁHTMLVisualizerǁrender_html__mutmut_43, 
        'xǁHTMLVisualizerǁrender_html__mutmut_44': xǁHTMLVisualizerǁrender_html__mutmut_44, 
        'xǁHTMLVisualizerǁrender_html__mutmut_45': xǁHTMLVisualizerǁrender_html__mutmut_45
    }
    
    def render_html(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHTMLVisualizerǁrender_html__mutmut_orig"), object.__getattribute__(self, "xǁHTMLVisualizerǁrender_html__mutmut_mutants"), args, kwargs, self)
        return result 
    
    render_html.__signature__ = _mutmut_signature(xǁHTMLVisualizerǁrender_html__mutmut_orig)
    xǁHTMLVisualizerǁrender_html__mutmut_orig.__name__ = 'xǁHTMLVisualizerǁrender_html'

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_orig(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_1(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "XXidXX": node.id,
            "type": node.type,
            "name": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_2(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "ID": node.id,
            "type": node.type,
            "name": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_3(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "XXtypeXX": node.type,
            "name": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_4(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "TYPE": node.type,
            "name": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_5(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "XXnameXX": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_6(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "NAME": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_7(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(None, "name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_8(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, None, ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_9(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "name", None),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_10(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr("name", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_11(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_12(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "name", ),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_13(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "XXnameXX", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_14(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "NAME", ""),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_15(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "name", "XXXX"),
            "children": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_16(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "name", ""),
            "XXchildrenXX": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_17(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "name", ""),
            "CHILDREN": len(node.children) if node.children else 0,
        }

    def xǁHTMLVisualizerǁ_node_to_dict__mutmut_18(self, node: StandardizedASTNode) -> dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": node.id,
            "type": node.type,
            "name": getattr(node, "name", ""),
            "children": len(node.children) if node.children else 1,
        }
    
    xǁHTMLVisualizerǁ_node_to_dict__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁHTMLVisualizerǁ_node_to_dict__mutmut_1': xǁHTMLVisualizerǁ_node_to_dict__mutmut_1, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_2': xǁHTMLVisualizerǁ_node_to_dict__mutmut_2, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_3': xǁHTMLVisualizerǁ_node_to_dict__mutmut_3, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_4': xǁHTMLVisualizerǁ_node_to_dict__mutmut_4, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_5': xǁHTMLVisualizerǁ_node_to_dict__mutmut_5, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_6': xǁHTMLVisualizerǁ_node_to_dict__mutmut_6, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_7': xǁHTMLVisualizerǁ_node_to_dict__mutmut_7, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_8': xǁHTMLVisualizerǁ_node_to_dict__mutmut_8, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_9': xǁHTMLVisualizerǁ_node_to_dict__mutmut_9, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_10': xǁHTMLVisualizerǁ_node_to_dict__mutmut_10, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_11': xǁHTMLVisualizerǁ_node_to_dict__mutmut_11, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_12': xǁHTMLVisualizerǁ_node_to_dict__mutmut_12, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_13': xǁHTMLVisualizerǁ_node_to_dict__mutmut_13, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_14': xǁHTMLVisualizerǁ_node_to_dict__mutmut_14, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_15': xǁHTMLVisualizerǁ_node_to_dict__mutmut_15, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_16': xǁHTMLVisualizerǁ_node_to_dict__mutmut_16, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_17': xǁHTMLVisualizerǁ_node_to_dict__mutmut_17, 
        'xǁHTMLVisualizerǁ_node_to_dict__mutmut_18': xǁHTMLVisualizerǁ_node_to_dict__mutmut_18
    }
    
    def _node_to_dict(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁHTMLVisualizerǁ_node_to_dict__mutmut_orig"), object.__getattribute__(self, "xǁHTMLVisualizerǁ_node_to_dict__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _node_to_dict.__signature__ = _mutmut_signature(xǁHTMLVisualizerǁ_node_to_dict__mutmut_orig)
    xǁHTMLVisualizerǁ_node_to_dict__mutmut_orig.__name__ = 'xǁHTMLVisualizerǁ_node_to_dict'
