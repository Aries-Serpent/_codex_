"""
Tests for AST analyzers.
"""

from pathlib import Path

from codex_ml.ast.analysis.base_analyzer import (
    ComplexityAnalyzer,
    LongFunctionAnalyzer,
    ParameterCountAnalyzer,
)
from codex_ml.ast.analysis.registry import AnalyzerRegistry
from codex_ml.ast.core.node import Finding, SourceLocation, StandardizedASTNode


class TestComplexityAnalyzer:
    """Tests for ComplexityAnalyzer."""

    def test_analyze_simple_function(self) -> None:
        """Test analyzing a simple function."""
        analyzer = ComplexityAnalyzer(threshold=10)
        node = StandardizedASTNode(
            node_id="f1",
            type="function",
            name="simple_func",
        )
        findings = analyzer.analyze(node)
        assert len(findings) == 0, "Findings must not be empty"

    def test_analyze_complex_function(self) -> None:
        """Test analyzing a complex function."""
        analyzer = ComplexityAnalyzer(threshold=2)

        # Create function with many decision points
        func = StandardizedASTNode(node_id="f1", type="function", name="complex_func")
        for i in range(5):
            func.add_child(StandardizedASTNode(node_id=f"if_{i}", type="if", name=f"condition_{i}"))

        findings = analyzer.analyze(func)
        assert len(findings) == 1, "Findings must not be empty"
        assert findings[0].type == "high_complexity", "type is not valid"
        assert findings[0].severity == "warning", "severity is not valid"

    def test_skip_non_function(self) -> None:
        """Test that non-function nodes are skipped."""
        analyzer = ComplexityAnalyzer()
        node = StandardizedASTNode(node_id="c1", type="class", name="MyClass")
        findings = analyzer.analyze(node)
        assert len(findings) == 0, "Findings must not be empty"

    def test_analyzer_type(self) -> None:
        """Test analyzer type identifier."""
        analyzer = ComplexityAnalyzer()
        assert analyzer.get_analyzer_type() == "complexity", "Condition must be true"


class TestLongFunctionAnalyzer:
    """Tests for LongFunctionAnalyzer."""

    def test_short_function(self) -> None:
        """Test short function passes."""
        analyzer = LongFunctionAnalyzer(max_lines=50)
        node = StandardizedASTNode(
            node_id="f1",
            type="function",
            name="short_func",
            location=SourceLocation(
                file_path=Path("test.py"),
                line_start=1,
                line_end=10,
            ),
        )
        findings = analyzer.analyze(node)
        assert len(findings) == 0, "Findings must not be empty"

    def test_long_function(self) -> None:
        """Test long function is flagged."""
        analyzer = LongFunctionAnalyzer(max_lines=50)
        node = StandardizedASTNode(
            node_id="f1",
            type="function",
            name="long_func",
            location=SourceLocation(
                file_path=Path("test.py"),
                line_start=1,
                line_end=100,
            ),
        )
        findings = analyzer.analyze(node)
        assert len(findings) == 1, "Findings must not be empty"
        assert findings[0].type == "long_function", "type is not valid"

    def test_analyzer_type(self) -> None:
        """Test analyzer type identifier."""
        analyzer = LongFunctionAnalyzer()
        assert analyzer.get_analyzer_type() == "long_function", "Condition must be true"


class TestParameterCountAnalyzer:
    """Tests for ParameterCountAnalyzer."""

    def test_few_parameters(self) -> None:
        """Test function with few parameters passes."""
        analyzer = ParameterCountAnalyzer(max_parameters=5)
        node = StandardizedASTNode(
            node_id="f1",
            type="function",
            name="func",
            metadata={"parameter_count": 3},
        )
        findings = analyzer.analyze(node)
        assert len(findings) == 0, "Findings must not be empty"

    def test_many_parameters(self) -> None:
        """Test function with many parameters is flagged."""
        analyzer = ParameterCountAnalyzer(max_parameters=5)
        node = StandardizedASTNode(
            node_id="f1",
            type="function",
            name="func",
            metadata={"parameter_count": 10},
        )
        findings = analyzer.analyze(node)
        assert len(findings) == 1, "Findings must not be empty"
        assert findings[0].type == "too_many_parameters", "type is not valid"

    def test_analyzer_type(self) -> None:
        """Test analyzer type identifier."""
        analyzer = ParameterCountAnalyzer()
        assert analyzer.get_analyzer_type() == "parameter_count", "Count must be greater than zero"


class TestAnalyzerRegistry:
    """Tests for AnalyzerRegistry."""

    def test_create_with_defaults(self) -> None:
        """Test registry with default analyzers."""
        registry = AnalyzerRegistry(register_defaults=True)
        assert len(registry) >= 3, "Registry must not be empty"

    def test_create_empty(self) -> None:
        """Test empty registry."""
        registry = AnalyzerRegistry(register_defaults=False)
        assert len(registry) == 0, "Registry must not be empty"

    def test_register(self) -> None:
        """Test registering an analyzer."""
        registry = AnalyzerRegistry(register_defaults=False)
        registry.register(ComplexityAnalyzer())
        assert "complexity" in registry, "Condition must be true"
        assert len(registry) == 1, "Registry must not be empty"

    def test_unregister(self) -> None:
        """Test unregistering an analyzer."""
        registry = AnalyzerRegistry(register_defaults=False)
        registry.register(ComplexityAnalyzer())
        result = registry.unregister("complexity")
        assert result is True, "Result must not be empty"
        assert "complexity" not in registry, "Condition must be true"

    def test_unregister_not_found(self) -> None:
        """Test unregistering non-existent analyzer."""
        registry = AnalyzerRegistry(register_defaults=False)
        result = registry.unregister("nonexistent")
        assert result is False, "Result must not be empty"

    def test_get(self) -> None:
        """Test getting an analyzer."""
        registry = AnalyzerRegistry(register_defaults=False)
        analyzer = ComplexityAnalyzer(threshold=15)
        registry.register(analyzer)
        retrieved = registry.get("complexity")
        assert retrieved is analyzer, "retrieved is not valid"

    def test_get_not_found(self) -> None:
        """Test getting non-existent analyzer."""
        registry = AnalyzerRegistry(register_defaults=False)
        result = registry.get("nonexistent")
        assert result is None, "Result must not be empty"

    def test_list_analyzers(self) -> None:
        """Test listing registered analyzers."""
        registry = AnalyzerRegistry(register_defaults=True)
        types = registry.list_analyzers()
        assert "complexity" in types, "Condition must be true"
        assert "long_function" in types, "Condition must be true"

    def test_analyze_node(self) -> None:
        """Test analyzing a single node."""
        registry = AnalyzerRegistry(register_defaults=False)
        registry.register(ComplexityAnalyzer(threshold=1))

        func = StandardizedASTNode(node_id="f1", type="function", name="func")
        # Add decision points to exceed threshold
        for i in range(3):
            func.add_child(StandardizedASTNode(node_id=f"if_{i}", type="if", name=""))

        findings = registry.analyze_node(func)
        assert len(findings) >= 1, "Findings must not be empty"

    def test_analyze_all(self) -> None:
        """Test analyzing entire tree."""
        registry = AnalyzerRegistry(register_defaults=False)
        registry.register(ComplexityAnalyzer(threshold=1))

        # Create tree with multiple functions
        root = StandardizedASTNode(node_id="mod", type="module", name="module")
        for i in range(2):
            func = StandardizedASTNode(node_id=f"f{i}", type="function", name=f"func{i}")
            for j in range(3):
                func.add_child(StandardizedASTNode(node_id=f"if_{i}_{j}", type="if", name=""))
            root.add_child(func)

        findings = registry.analyze_all(root)
        assert len(findings) >= 2, "Findings must not be empty"

    def test_get_statistics(self) -> None:
        """Test getting finding statistics."""
        registry = AnalyzerRegistry(register_defaults=False)

        findings = [
            Finding(type="a", severity="warning", message=""),
            Finding(type="a", severity="warning", message=""),
            Finding(type="b", severity="error", message=""),
        ]

        stats = registry.get_statistics(findings)
        assert stats["total"] == 3, "Condition must be true"
        assert stats["by_severity"]["warning"] == 2, "Condition must be true"
        assert stats["by_severity"]["error"] == 1, "Error should be raised or set"
        assert stats["by_type"]["a"] == 2, "Condition must be true"
        assert stats["by_type"]["b"] == 1, "Condition must be true"

    def test_repr(self) -> None:
        """Test string representation."""
        registry = AnalyzerRegistry(register_defaults=True)
        repr_str = repr(registry)
        assert "AnalyzerRegistry" in repr_str, "Condition must be true"
