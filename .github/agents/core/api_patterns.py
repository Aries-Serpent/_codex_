"""
API Pattern Matcher for Cognitive Brain Framework.

Detects deprecated API usage, breaking changes, and compatibility issues.

#AFTERMATH_PATTERN_IDENTIFIED: api_compatibility_analysis
#AFTERMATH_METRIC: api_issues_detected

PDA Loop Integration:
- PERCEIVE: Analyze code for API usage patterns
- DECIDE: Classify severity and breaking change risk
- ACT: Generate migration recommendations
- AFTERMATH: Record patterns for learning
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class APIPattern:
    """API usage issue or deprecation warning."""

    name: str
    pattern_type: str  # "deprecated", "breaking_change", "version_incompatible", "unsafe_api"
    description: str
    locations: list[str]
    confidence: float  # 0.0 to 1.0
    severity: str  # "critical", "high", "medium", "low"
    deprecated_in: Optional[str]  # Version where deprecated
    removed_in: Optional[str]  # Version where removed
    migration_guide: str  # How to migrate
    metadata: dict[str, Any]


class APIPatternMatcher:
    """
    Detects deprecated API usage and compatibility issues.

    #AFTERMATH_PATTERN_IDENTIFIED: api_pattern_detection

    PDA Loop:
    - PERCEIVE: Multi-layer API usage analysis (AST + regex)
    - DECIDE: Breaking-change risk classification
    - ACT: Pattern detection with migration guidance
    - AFTERMATH: Metrics + cognitive brain learning
    """

    # Known deprecated APIs (examples - expand as needed)
    DEPRECATED_APIS = {
        # Python stdlib
        'asyncore': {'deprecated_in': '3.6', 'removed_in': '3.12', 'replacement': 'asyncio'},
        'asynchat': {'deprecated_in': '3.6', 'removed_in': '3.12', 'replacement': 'asyncio'},
        'imp': {'deprecated_in': '3.4', 'removed_in': '3.12', 'replacement': 'importlib'},
        'optparse': {'deprecated_in': '2.7', 'removed_in': None, 'replacement': 'argparse'},

        # Common third-party deprecations
        'unittest.TestCase.assertEquals': {'deprecated_in': '3.2', 'removed_in': None, 'replacement': 'assertEqual'},
        'collections.Mapping': {'deprecated_in': '3.3', 'removed_in': '3.10', 'replacement': 'collections.abc.Mapping'},
        'SafeConfigParser': {'deprecated_in': '3.2', 'removed_in': None, 'replacement': 'ConfigParser'},
    }

    def __init__(self):
        """Initialize API pattern matcher."""
        self.detected_patterns: list[APIPattern] = []
        #AFTERMATH_METRIC: api_matcher_initialized

    def analyze_file(self, file_path: Path, content: Optional[str] = None) -> list[APIPattern]:
        """
        Analyze a file for API usage issues.

        #AFTERMATH_PATTERN_IDENTIFIED: file_api_analysis

        Args:
            file_path: Path to file to analyze
            content: Optional file content (will read if not provided)

        Returns:
            List of detected API patterns
        """
        if content is None:
            try:
                content = file_path.read_text()
            except (IOError, UnicodeDecodeError):
                return []

        detected: list[APIPattern] = []

        # PERCEIVE: Multi-layer API scanning
        if file_path.suffix == ".py":
            # Python-specific analysis using AST
            try:
                tree = ast.parse(content)
                detected.extend(self._detect_deprecated_imports(tree, file_path))
                detected.extend(self._detect_deprecated_functions(tree, file_path))
                detected.extend(self._detect_unsafe_apis(tree, file_path))
                detected.extend(self._detect_version_incompatibilities(tree, file_path))
                #AFTERMATH_PATTERN_IDENTIFIED: ast_api_analysis
            except SyntaxError:
                # Intentionally skip files with syntax errors
                # API analysis requires valid AST
                pass

        # General regex-based detection (all file types)
        detected.extend(self._detect_regex_patterns(content, file_path))

        # AFTERMATH: Record metrics
        #AFTERMATH_METRIC: api_issues_count = len(detected)

        return detected

    def _detect_deprecated_imports(self, tree: ast.AST, file_path: Path) -> list[APIPattern]:
        """
        Detect deprecated module imports.

        #AFTERMATH_PATTERN_IDENTIFIED: deprecated_import_detection
        """
        detected = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.DEPRECATED_APIS:
                        info = self.DEPRECATED_APIS[alias.name]
                        detected.append(APIPattern(
                            name="deprecated_import",
                            pattern_type="deprecated",
                            description=f"Module '{alias.name}' is deprecated",
                            locations=[f"{file_path}:{node.lineno}"],
                            confidence=0.95,
                            severity="high" if info['removed_in'] else "medium",
                            deprecated_in=info['deprecated_in'],
                            removed_in=info['removed_in'],
                            migration_guide=f"Replace with '{info['replacement']}'",
                            metadata={
                                "file": str(file_path),
                                "line": node.lineno,
                                "module": alias.name,
                                "replacement": info['replacement']
                            }
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module in self.DEPRECATED_APIS:
                    info = self.DEPRECATED_APIS[node.module]
                    detected.append(APIPattern(
                        name="deprecated_import_from",
                        pattern_type="deprecated",
                        description=f"Module '{node.module}' is deprecated",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.95,
                        severity="high" if info['removed_in'] else "medium",
                        deprecated_in=info['deprecated_in'],
                        removed_in=info['removed_in'],
                        migration_guide=f"Replace with '{info['replacement']}'",
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno,
                            "module": node.module,
                            "replacement": info['replacement']
                        }
                    ))

        return detected

    def _detect_deprecated_functions(self, tree: ast.AST, file_path: Path) -> list[APIPattern]:
        """
        Detect deprecated function/method calls.

        #AFTERMATH_PATTERN_IDENTIFIED: deprecated_function_detection
        """
        detected = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)

                # Check against known deprecated functions
                if func_name in self.DEPRECATED_APIS:
                    info = self.DEPRECATED_APIS[func_name]
                    detected.append(APIPattern(
                        name="deprecated_function",
                        pattern_type="deprecated",
                        description=f"Function '{func_name}' is deprecated",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.9,
                        severity="high" if info['removed_in'] else "medium",
                        deprecated_in=info['deprecated_in'],
                        removed_in=info['removed_in'],
                        migration_guide=f"Use '{info['replacement']}' instead",
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno,
                            "function": func_name,
                            "replacement": info['replacement']
                        }
                    ))

                # Common deprecated patterns
                if func_name == 'assert_':
                    detected.append(APIPattern(
                        name="deprecated_assert_underscore",
                        pattern_type="deprecated",
                        description="assert_() is deprecated in unittest",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.85,
                        severity="low",
                        deprecated_in="3.2",
                        removed_in=None,
                        migration_guide="Use assertTrue() instead",
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno
                        }
                    ))

        return detected

    def _detect_unsafe_apis(self, tree: ast.AST, file_path: Path) -> list[APIPattern]:
        """
        Detect unsafe or risky API usage.

        #AFTERMATH_PATTERN_IDENTIFIED: unsafe_api_detection
        """
        detected = []

        unsafe_functions = {
            'eval': 'Code injection risk',
            'exec': 'Code injection risk',
            'compile': 'Potential code injection',
            '__import__': 'Use importlib instead',
            'pickle.loads': 'Arbitrary code execution risk - use json',
            'yaml.load': 'Arbitrary code execution risk - use yaml.safe_load'
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)

                for unsafe_func, reason in unsafe_functions.items():
                    if unsafe_func in func_name:
                        detected.append(APIPattern(
                            name="unsafe_api",
                            pattern_type="unsafe_api",
                            description=f"Unsafe API usage: {func_name}",
                            locations=[f"{file_path}:{node.lineno}"],
                            confidence=0.9,
                            severity="critical" if func_name in ['eval', 'exec'] else "high",
                            deprecated_in=None,
                            removed_in=None,
                            migration_guide=f"{reason}. Validate input or use safer alternatives",
                            metadata={
                                "file": str(file_path),
                                "line": node.lineno,
                                "function": func_name,
                                "risk": reason
                            }
                        ))

        return detected

    def _detect_version_incompatibilities(self, tree: ast.AST, file_path: Path) -> list[APIPattern]:
        """
        Detect Python version-specific features.

        #AFTERMATH_PATTERN_IDENTIFIED: version_compatibility_detection
        """
        detected = []

        # Check for Python 3.10+ features (match statement)
        for node in ast.walk(tree):
            if isinstance(node, ast.Match):
                detected.append(APIPattern(
                    name="match_statement",
                    pattern_type="version_incompatible",
                    description="Match statement requires Python 3.10+",
                    locations=[f"{file_path}:{node.lineno}"],
                    confidence=1.0,
                    severity="medium",
                    deprecated_in=None,
                    removed_in=None,
                    migration_guide="Ensure Python >= 3.10 or use if/elif chains",
                    metadata={
                        "file": str(file_path),
                        "line": node.lineno,
                        "min_version": "3.10"
                    }
                ))

            # Walrus operator (Python 3.8+)
            if isinstance(node, ast.NamedExpr):
                detected.append(APIPattern(
                    name="walrus_operator",
                    pattern_type="version_incompatible",
                    description="Walrus operator := requires Python 3.8+",
                    locations=[f"{file_path}:{node.lineno}"],
                    confidence=1.0,
                    severity="low",
                    deprecated_in=None,
                    removed_in=None,
                    migration_guide="Ensure Python >= 3.8 or refactor to use separate assignment",
                    metadata={
                        "file": str(file_path),
                        "line": node.lineno,
                        "min_version": "3.8"
                    }
                ))

        return detected

    def _detect_regex_patterns(self, content: str, file_path: Path) -> list[APIPattern]:
        """
        Detect API issues using regex patterns.

        #AFTERMATH_PATTERN_IDENTIFIED: regex_api_detection
        """
        detected = []

        # Check for deprecated string formatting
        if re.search(r'%\s*\(', content):
            detected.append(APIPattern(
                name="old_string_formatting",
                pattern_type="deprecated",
                description="Old-style string formatting with % is discouraged",
                locations=[str(file_path)],
                confidence=0.6,
                severity="low",
                deprecated_in=None,
                removed_in=None,
                migration_guide="Use f-strings or str.format()",
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
        Generate summary of detected API issues.

        #AFTERMATH_METRIC: api_summary_generated

        Returns:
            Dictionary with API compatibility metrics
        """
        summary = {
            "total_issues": len(self.detected_patterns),
            "by_type": {},
            "by_severity": {},
            "breaking_changes": len([p for p in self.detected_patterns
                                    if p.removed_in is not None])
        }

        for pattern in self.detected_patterns:
            summary["by_type"][pattern.pattern_type] = summary["by_type"].get(pattern.pattern_type, 0) + 1
            summary["by_severity"][pattern.severity] = summary["by_severity"].get(pattern.severity, 0) + 1

        #AFTERMATH_LESSON_LEARNED: api_patterns_summarized
        return summary
