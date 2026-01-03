"""
Abstract base class for AST analyzers.

Defines the interface for all AST analyzers in the framework.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from codex_ml.ast.core.node import Finding, StandardizedASTNode


class ASTAnalyzer(ABC):
    """Abstract base class for AST analyzers.

    All analyzers must implement the analyze() and get_analyzer_type() methods.
    Optionally override supports_node_type() to filter processed nodes.

    Example:
        class ComplexityAnalyzer(ASTAnalyzer):
            def __init__(self, threshold: int = 10):
                self.threshold = threshold

            def analyze(self, node: StandardizedASTNode) -> List[Finding]:
                if node.type != "function":
                    return []
                complexity = self._calculate_complexity(node)
                if complexity > self.threshold:
                    return [Finding(
                        type="high_complexity",
                        severity="warning",
                        message=f"Complexity {complexity} exceeds threshold {self.threshold}",
                        location=node.location,
                        analyzer=self.get_analyzer_type()
                    )]
                return []

            def get_analyzer_type(self) -> str:
                return "complexity"
    """

    @abstractmethod
    def analyze(self, node: StandardizedASTNode) -> List[Finding]:
        """Analyze a node and return findings.

        Args:
            node: The AST node to analyze

        Returns:
            List of findings from this analysis
        """
        pass

    @abstractmethod
    def get_analyzer_type(self) -> str:
        """Get the type identifier for this analyzer.

        Returns:
            Unique string identifying this analyzer type
        """
        pass

    def supports_node_type(self, node_type: str) -> bool:
        """Check if this analyzer processes the given node type.

        Override to filter which node types this analyzer processes.
        Default returns True for all node types.

        Args:
            node_type: The type of node to check

        Returns:
            True if this analyzer should process nodes of this type
        """
        return True

    def get_description(self) -> str:
        """Get a human-readable description of this analyzer.

        Returns:
            Description string
        """
        return f"{self.get_analyzer_type()} analyzer"

    def get_supported_languages(self) -> List[str]:
        """Get list of languages this analyzer supports.

        Override to restrict to specific languages.
        Default returns empty list (all languages).

        Returns:
            List of language identifiers, or empty for all
        """
        return []


class ComplexityAnalyzer(ASTAnalyzer):
    """Analyzer for cyclomatic complexity.

    Calculates and reports functions with complexity exceeding threshold.
    """

    def __init__(self, threshold: int = 10):
        """Initialize with complexity threshold.

        Args:
            threshold: Maximum acceptable cyclomatic complexity
        """
        self.threshold = threshold

    def analyze(self, node: StandardizedASTNode) -> List[Finding]:
        """Analyze function complexity."""
        if node.type != "function":
            return []

        complexity = self._calculate_complexity(node)
        if complexity > self.threshold:
            return [
                Finding(
                    type="high_complexity",
                    severity="warning",
                    message=f"Function '{node.name}' has complexity {complexity} (threshold: {self.threshold})",
                    location=node.location,
                    analyzer=self.get_analyzer_type(),
                    metadata={"complexity": complexity, "threshold": self.threshold},
                )
            ]
        return []

    def _calculate_complexity(self, node: StandardizedASTNode) -> int:
        """Calculate cyclomatic complexity of a function node.

        Counts decision points: if, elif, for, while, except, and, or, ternary.
        """
        complexity = 1  # Base complexity

        decision_types = {
            "if",
            "elif",
            "for",
            "while",
            "except",
            "with",
            "comprehension",
            "ternary",
            "and",
            "or",
        }

        for child in node.walk():
            if child.type in decision_types:
                complexity += 1

        return complexity

    def get_analyzer_type(self) -> str:
        return "complexity"

    def get_description(self) -> str:
        return f"Cyclomatic complexity analyzer (threshold: {self.threshold})"


class UnusedCodeAnalyzer(ASTAnalyzer):
    """Analyzer for unused code detection.

    Identifies unused imports, variables, and functions.
    """

    def __init__(self):
        """Initialize unused code analyzer."""
        self.defined_names: set = set()
        self.used_names: set = set()

    def analyze(self, node: StandardizedASTNode) -> List[Finding]:
        """Analyze for unused code."""
        findings = []

        # Track definitions
        if node.type in ("import", "function", "class", "variable"):
            self.defined_names.add(node.name)

        # Track usages
        if node.type == "name_reference":
            self.used_names.add(node.name)

        # Report unused (only at module level for complete picture)
        if node.type == "module":
            unused = self.defined_names - self.used_names
            for name in unused:
                # Find the node for this name
                matching = node.find_by_name(name)
                if matching:
                    findings.append(
                        Finding(
                            type="unused_code",
                            severity="info",
                            message=f"'{name}' is defined but never used",
                            location=matching[0].location,
                            analyzer=self.get_analyzer_type(),
                            metadata={"name": name},
                        )
                    )

        return findings

    def get_analyzer_type(self) -> str:
        return "unused_code"

    def supports_node_type(self, node_type: str) -> bool:
        return node_type in ("module", "import", "function", "class", "variable", "name_reference")


class LongFunctionAnalyzer(ASTAnalyzer):
    """Analyzer for excessively long functions."""

    def __init__(self, max_lines: int = 50):
        """Initialize with max lines threshold."""
        self.max_lines = max_lines

    def analyze(self, node: StandardizedASTNode) -> List[Finding]:
        """Check function length."""
        if node.type != "function":
            return []

        if node.location:
            lines = node.location.line_end - node.location.line_start + 1
            if lines > self.max_lines:
                return [
                    Finding(
                        type="long_function",
                        severity="warning",
                        message=f"Function '{node.name}' has {lines} lines (max: {self.max_lines})",
                        location=node.location,
                        analyzer=self.get_analyzer_type(),
                        metadata={"lines": lines, "max_lines": self.max_lines},
                    )
                ]

        return []

    def get_analyzer_type(self) -> str:
        return "long_function"


class ParameterCountAnalyzer(ASTAnalyzer):
    """Analyzer for functions with too many parameters."""

    def __init__(self, max_parameters: int = 5):
        """Initialize with max parameters threshold."""
        self.max_parameters = max_parameters

    def analyze(self, node: StandardizedASTNode) -> List[Finding]:
        """Check parameter count."""
        if node.type != "function":
            return []

        param_count = node.metadata.get("parameter_count", 0)
        if param_count > self.max_parameters:
            return [
                Finding(
                    type="too_many_parameters",
                    severity="info",
                    message=f"Function '{node.name}' has {param_count} parameters (max: {self.max_parameters})",
                    location=node.location,
                    analyzer=self.get_analyzer_type(),
                    metadata={"parameter_count": param_count, "max_parameters": self.max_parameters},
                )
            ]

        return []

    def get_analyzer_type(self) -> str:
        return "parameter_count"
