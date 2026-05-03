"""
Performance Pattern Matcher for Cognitive Brain Framework.

Detects performance anti-patterns and optimization opportunities in code.

#AFTERMATH_PATTERN_IDENTIFIED: performance_analysis
#AFTERMATH_METRIC: performance_issues_detected

PDA Loop Integration:
- PERCEIVE: Analyze code for performance issues
- DECIDE: Classify severity and impact
- ACT: Generate optimization recommendations
- AFTERMATH: Record patterns for learning
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class PerformancePattern:
    """Performance anti-pattern or optimization opportunity."""

    name: str
    pattern_type: str  # "n+1_query", "inefficient_loop", "memory", "complexity", "caching"
    description: str
    locations: list[str]
    confidence: float  # 0.0 to 1.0
    severity: str  # "critical", "high", "medium", "low"
    optimization: str  # Suggested optimization
    impact_assessment: dict[str, str]  # execution_time, memory_usage, etc.
    metadata: dict[str, Any]


class PerformancePatternMatcher:
    """
    Detects performance anti-patterns and optimization opportunities.

    #AFTERMATH_PATTERN_IDENTIFIED: performance_pattern_detection

    PDA Loop:
    - PERCEIVE: Multi-layer performance analysis (AST + regex)
    - DECIDE: Severity classification based on impact
    - ACT: Pattern detection with optimization guidance
    - AFTERMATH: Metrics + cognitive brain learning
    """

    def __init__(self):
        """Initialize performance pattern matcher."""
        self.detected_patterns: list[PerformancePattern] = []
        #AFTERMATH_METRIC: performance_matcher_initialized

    def analyze_file(self, file_path: Path, content: Optional[str] = None) -> list[PerformancePattern]:
        """
        Analyze a file for performance issues.

        #AFTERMATH_PATTERN_IDENTIFIED: file_performance_analysis

        Args:
            file_path: Path to file to analyze
            content: Optional file content (will read if not provided)

        Returns:
            List of detected performance patterns
        """
        if content is None:
            try:
                content = file_path.read_text()
            except (IOError, UnicodeDecodeError):
                return []

        detected: list[PerformancePattern] = []

        # PERCEIVE: Multi-layer performance scanning
        if file_path.suffix == ".py":
            # Python-specific analysis using AST
            try:
                tree = ast.parse(content)
                detected.extend(self._detect_n_plus_one(tree, file_path))
                detected.extend(self._detect_inefficient_loops(tree, file_path))
                detected.extend(self._detect_memory_issues(tree, file_path))
                detected.extend(self._detect_complexity(tree, file_path))
                detected.extend(self._detect_caching_opportunities(tree, file_path))
                #AFTERMATH_PATTERN_IDENTIFIED: ast_performance_analysis
            except SyntaxError:
                # Intentionally skip files with syntax errors
                # Performance analysis requires valid AST
                pass

        # General regex-based detection (all file types)
        detected.extend(self._detect_regex_patterns(content, file_path))

        # AFTERMATH: Record metrics
        #AFTERMATH_METRIC: performance_issues_count = len(detected)

        return detected

    def _detect_n_plus_one(self, tree: ast.AST, file_path: Path) -> list[PerformancePattern]:
        """
        Detect N+1 query problems.

        #AFTERMATH_PATTERN_IDENTIFIED: n_plus_one_detection
        """
        detected = []

        # Look for database queries inside loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                # Check if loop body contains database operations
                for inner_node in ast.walk(node):
                    if isinstance(inner_node, ast.Call):
                        func_name = self._get_call_name(inner_node)
                        if any(db_op in func_name.lower() for db_op in
                              ['select', 'query', 'filter', 'get', 'fetch', 'find']):
                            detected.append(PerformancePattern(
                                name="n_plus_one_query",
                                pattern_type="n+1_query",
                                description=f"Database query inside loop: {func_name}",
                                locations=[f"{file_path}:{node.lineno}"],
                                confidence=0.85,
                                severity="high",
                                optimization="Use batch operations (select_related, prefetch_related) or aggregate queries",
                                impact_assessment={
                                    "execution_time": "Linear with loop iterations",
                                    "database_load": "N+1 queries instead of 1-2"
                                },
                                metadata={
                                    "file": str(file_path),
                                    "line": node.lineno,
                                    "function": func_name
                                }
                            ))

        return detected

    def _detect_inefficient_loops(self, tree: ast.AST, file_path: Path) -> list[PerformancePattern]:
        """
        Detect inefficient loop patterns.

        #AFTERMATH_PATTERN_IDENTIFIED: inefficient_loop_detection
        """
        detected = []

        for node in ast.walk(tree):
            # Nested loops (O(n²) or worse)
            if isinstance(node, (ast.For, ast.While)):
                nested_loops = [n for n in ast.walk(node)
                               if isinstance(n, (ast.For, ast.While)) and n != node]
                if len(nested_loops) >= 1:
                    detected.append(PerformancePattern(
                        name="nested_loops",
                        pattern_type="inefficient_loop",
                        description=f"Nested loop with {len(nested_loops)+1} levels",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.9,
                        severity="medium" if len(nested_loops) == 1 else "high",
                        optimization="Consider using dict/set lookups, list comprehensions, or algorithm optimization",
                        impact_assessment={
                            "complexity": f"O(n^{len(nested_loops)+1})",
                            "execution_time": "Exponential with input size"
                        },
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno,
                            "nesting_level": len(nested_loops) + 1
                        }
                    ))

                # List operations in loops
                for inner in ast.walk(node):
                    if isinstance(inner, ast.AugAssign) and isinstance(inner.op, ast.Add):
                        if isinstance(inner.target, ast.Name):
                            detected.append(PerformancePattern(
                                name="list_append_in_loop",
                                pattern_type="inefficient_loop",
                                description="List concatenation with += in loop",
                                locations=[f"{file_path}:{inner.lineno}"],
                                confidence=0.75,
                                severity="low",
                                optimization="Use .append() or list comprehension instead of +=",
                                impact_assessment={
                                    "execution_time": "O(n²) for list concatenation",
                                    "memory": "Creates new list each iteration"
                                },
                                metadata={
                                    "file": str(file_path),
                                    "line": inner.lineno
                                }
                            ))

        return detected

    def _detect_memory_issues(self, tree: ast.AST, file_path: Path) -> list[PerformancePattern]:
        """
        Detect memory-inefficient operations.

        #AFTERMATH_PATTERN_IDENTIFIED: memory_issue_detection
        """
        detected = []

        for node in ast.walk(tree):
            # String concatenation in loops
            if isinstance(node, (ast.For, ast.While)):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.AugAssign) and isinstance(inner.op, ast.Add):
                        if isinstance(inner.value, ast.Constant) and isinstance(inner.value.value, str):
                            detected.append(PerformancePattern(
                                name="string_concat_in_loop",
                                pattern_type="memory",
                                description="String concatenation in loop",
                                locations=[f"{file_path}:{inner.lineno}"],
                                confidence=0.85,
                                severity="medium",
                                optimization="Use str.join() or io.StringIO() for string building",
                                impact_assessment={
                                    "memory": "O(n²) memory allocations",
                                    "execution_time": "Quadratic with string length"
                                },
                                metadata={
                                    "file": str(file_path),
                                    "line": inner.lineno
                                }
                            ))

                    # Dict.copy() in loops
                    if isinstance(inner, ast.Call):
                        func_name = self._get_call_name(inner)
                        if func_name.endswith('.copy'):
                            detected.append(PerformancePattern(
                                name="dict_copy_in_loop",
                                pattern_type="memory",
                                description="Dict/list copy operation in loop",
                                locations=[f"{file_path}:{inner.lineno}"],
                                confidence=0.75,
                                severity="low",
                                optimization="Consider modifying in-place or using references",
                                impact_assessment={
                                    "memory": "Multiple object copies",
                                    "execution_time": "Linear with object size per iteration"
                                },
                                metadata={
                                    "file": str(file_path),
                                    "line": inner.lineno,
                                    "function": func_name
                                }
                            ))

        return detected

    def _detect_complexity(self, tree: ast.AST, file_path: Path) -> list[PerformancePattern]:
        """
        Detect high-complexity algorithms.

        #AFTERMATH_PATTERN_IDENTIFIED: algorithm_complexity_detection
        """
        detected = []

        for node in ast.walk(tree):
            # Sorting in loops
            if isinstance(node, (ast.For, ast.While)):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call):
                        func_name = self._get_call_name(inner)
                        if any(sort_op in func_name.lower() for sort_op in ['sort', 'sorted']):
                            detected.append(PerformancePattern(
                                name="sort_in_loop",
                                pattern_type="complexity",
                                description="Sorting operation inside loop",
                                locations=[f"{file_path}:{inner.lineno}"],
                                confidence=0.9,
                                severity="high",
                                optimization="Sort once before loop or use data structures that maintain order",
                                impact_assessment={
                                    "complexity": "O(n² log n) or worse",
                                    "execution_time": "Exponential with input size"
                                },
                                metadata={
                                    "file": str(file_path),
                                    "line": inner.lineno,
                                    "function": func_name
                                }
                            ))

        return detected

    def _detect_caching_opportunities(self, tree: ast.AST, file_path: Path) -> list[PerformancePattern]:
        """
        Detect opportunities for caching/memoization.

        #AFTERMATH_PATTERN_IDENTIFIED: caching_opportunity_detection
        """
        detected = []

        # Look for repeated function calls with same arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has no side effects (good caching candidate)
                has_global = any(isinstance(n, ast.Global) for n in ast.walk(node))
                has_nonlocal = any(isinstance(n, ast.Nonlocal) for n in ast.walk(node))

                if not has_global and not has_nonlocal:
                    # Pure function - good caching candidate
                    detected.append(PerformancePattern(
                        name="memoization_candidate",
                        pattern_type="caching",
                        description=f"Function {node.name} could benefit from memoization",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.6,
                        severity="low",
                        optimization="Add @functools.lru_cache decorator if function is called repeatedly",
                        impact_assessment={
                            "execution_time": "Eliminates redundant computations",
                            "memory": "Small cache overhead"
                        },
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno,
                            "function": node.name
                        }
                    ))

        return detected

    def _detect_regex_patterns(self, content: str, file_path: Path) -> list[PerformancePattern]:
        """
        Detect performance issues using regex patterns.

        #AFTERMATH_PATTERN_IDENTIFIED: regex_performance_detection
        """
        detected = []

        # Inefficient list comprehension patterns
        if re.search(r'\[.*for.*in.*for.*in.*\]', content):
            detected.append(PerformancePattern(
                name="nested_list_comprehension",
                pattern_type="inefficient_loop",
                description="Nested list comprehension (potential O(n²))",
                locations=[str(file_path)],
                confidence=0.7,
                severity="medium",
                optimization="Consider using generator expressions or itertools",
                impact_assessment={
                    "complexity": "O(n²)",
                    "memory": "Full list in memory"
                },
                metadata={"file": str(file_path)}
            ))

        return detected

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function name from Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return "unknown"

    def get_summary(self) -> dict[str, Any]:
        """
        Generate summary of detected performance issues.

        #AFTERMATH_METRIC: performance_summary_generated

        Returns:
            Dictionary with performance metrics
        """
        summary = {
            "total_issues": len(self.detected_patterns),
            "by_type": {},
            "by_severity": {},
            "optimization_opportunities": len([p for p in self.detected_patterns if p.severity in ["high", "critical"]])
        }

        for pattern in self.detected_patterns:
            summary["by_type"][pattern.pattern_type] = summary["by_type"].get(pattern.pattern_type, 0) + 1
            summary["by_severity"][pattern.severity] = summary["by_severity"].get(pattern.severity, 0) + 1

        #AFTERMATH_LESSON_LEARNED: performance_patterns_summarized
        return summary
