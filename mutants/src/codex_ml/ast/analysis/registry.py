"""
Registry for AST analyzers.

Provides registration and execution of multiple analyzers on AST trees.
"""

import logging
from typing import Any, Optional

from codex.logging.structured_logger import logger
from codex_ml.ast.analysis.base_analyzer import (
    ASTAnalyzer,
    ComplexityAnalyzer,
    LongFunctionAnalyzer,
    ParameterCountAnalyzer,
    UnusedCodeAnalyzer,
)
from codex_ml.ast.core.node import Finding, StandardizedASTNode

logger = logging.getLogger(__name__)


class AnalyzerRegistry:
    """Registry for AST analyzers.

    Manages a collection of analyzers and executes them on AST trees.

    Example:
        registry = AnalyzerRegistry()
        registry.register(ComplexityAnalyzer(threshold=15))

        tree = parse_file("example.py")
        findings = registry.analyze_all(tree)

        for finding in findings:
            logger.info(f"{finding.severity}: {finding.message}")
    """

    def __init__(self, register_defaults: bool = True):
        """Initialize the analyzer registry.

        Args:
            register_defaults: Whether to register built-in analyzers
        """
        self.analyzers: dict[str, ASTAnalyzer] = {}

        if register_defaults:
            self._register_defaults()

    def _register_defaults(self) -> None:
        """Register built-in analyzers with default settings."""
        self.register(ComplexityAnalyzer())
        self.register(LongFunctionAnalyzer())
        self.register(ParameterCountAnalyzer())
        self.register(UnusedCodeAnalyzer())

    def register(self, analyzer: ASTAnalyzer) -> None:
        """Register an analyzer.

        Args:
            analyzer: The analyzer instance to register
        """
        self.analyzers[analyzer.get_analyzer_type()] = analyzer

    def unregister(self, analyzer_type: str) -> bool:
        """Unregister an analyzer by type.

        Args:
            analyzer_type: The type of analyzer to remove

        Returns:
            True if analyzer was removed, False if not found
        """
        if analyzer_type in self.analyzers:
            del self.analyzers[analyzer_type]
            return True
        return False

    def get(self, analyzer_type: str) -> Optional[ASTAnalyzer]:
        """Get an analyzer by type.

        Args:
            analyzer_type: The type of analyzer to retrieve

        Returns:
            The analyzer instance, or None if not found
        """
        return self.analyzers.get(analyzer_type)

    def list_analyzers(self) -> list[str]:
        """Get list of registered analyzer types.

        Returns:
            List of analyzer type strings
        """
        return list(self.analyzers.keys())

    def analyze_node(self, node: StandardizedASTNode) -> list[Finding]:
        """Run all applicable analyzers on a single node.

        Args:
            node: The node to analyze

        Returns:
            List of findings from all analyzers
        """
        findings = []

        for analyzer in self.analyzers.values():
            if analyzer.supports_node_type(node.type):
                try:
                    node_findings = analyzer.analyze(node)
                    findings.extend(node_findings)
                except Exception as e:
                    # Log error but continue with other analyzers
                    findings.append(
                        Finding(
                            type="analyzer_error",
                            severity="error",
                            message=f"Analyzer '{analyzer.get_analyzer_type()}' failed: {e!s}",
                            location=node.location,
                            analyzer="registry",
                            metadata={
                                "error": str(e),
                                "analyzer": analyzer.get_analyzer_type(),
                            },
                        )
                    )

        return findings

    def analyze_all(self, tree: StandardizedASTNode) -> list[Finding]:
        """Run all analyzers on an entire AST tree.

        Args:
            tree: The root of the AST tree to analyze

        Returns:
            List of all findings from all nodes
        """
        findings = []

        for node in tree.walk():
            findings.extend(self.analyze_node(node))

        return findings

    def analyze_with_filter(
        self,
        tree: StandardizedASTNode,
        analyzer_types: Optional[list[str]] = None,
        node_types: Optional[list[str]] = None,
        min_severity: Optional[str] = None,
    ) -> list[Finding]:
        """Run analysis with filters.

        Args:
            tree: The root of the AST tree to analyze
            analyzer_types: List of analyzer types to run (None = all)
            node_types: List of node types to analyze (None = all)
            min_severity: Minimum severity to include in results

        Returns:
            Filtered list of findings
        """
        severity_order = {"info": 0, "warning": 1, "error": 2, "critical": 3}
        min_severity_value = severity_order.get(min_severity or "info", 0)

        findings = []

        for node in tree.walk():
            # Filter by node type
            if node_types and node.type not in node_types:
                continue

            # Run selected analyzers
            for analyzer_type, analyzer in self.analyzers.items():
                if analyzer_types and analyzer_type not in analyzer_types:
                    continue

                if analyzer.supports_node_type(node.type):
                    try:
                        node_findings = analyzer.analyze(node)
                        findings.extend(node_findings)
                    except (ValueError, TypeError, RuntimeError):
                        logger.debug("Suppressed exception in handler", exc_info=True)
        # Filter by severity
        if min_severity:
            findings = [
                f for f in findings if severity_order.get(f.severity, 0) >= min_severity_value
            ]

        return findings

    def get_statistics(self, findings: list[Finding]) -> dict[str, Any]:
        """Get statistics about findings.

        Args:
            findings: List of findings to analyze

        Returns:
            Dictionary with statistics
        """
        stats: dict[str, Any] = {
            "total": len(findings),
            "by_severity": {"info": 0, "warning": 0, "error": 0, "critical": 0},
            "by_analyzer": {},
            "by_type": {},
        }

        for finding in findings:
            # Count by severity
            if finding.severity in stats["by_severity"]:
                stats["by_severity"][finding.severity] += 1

            # Count by analyzer
            if finding.analyzer not in stats["by_analyzer"]:
                stats["by_analyzer"][finding.analyzer] = 0
            stats["by_analyzer"][finding.analyzer] += 1

            # Count by type
            if finding.type not in stats["by_type"]:
                stats["by_type"][finding.type] = 0
            stats["by_type"][finding.type] += 1

        return stats

    def __len__(self) -> int:
        """Return number of registered analyzers."""
        return len(self.analyzers)

    def __contains__(self, analyzer_type: str) -> bool:
        """Check if an analyzer type is registered."""
        return analyzer_type in self.analyzers

    def __repr__(self) -> str:
        return f"AnalyzerRegistry(analyzers={list(self.analyzers.keys())})"
