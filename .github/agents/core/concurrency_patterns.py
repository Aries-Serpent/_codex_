"""
Concurrency Pattern Matcher for Cognitive Brain Framework.

Detects concurrency issues, race conditions, and thread safety problems.

#AFTERMATH_PATTERN_IDENTIFIED: concurrency_analysis
#AFTERMATH_METRIC: concurrency_issues_detected

PDA Loop Integration:
- PERCEIVE: Analyze code for concurrency anti-patterns
- DECIDE: Classify severity and risk level
- ACT: Generate thread-safety recommendations
- AFTERMATH: Record patterns for learning
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ConcurrencyPattern:
    """Concurrency issue or thread safety problem."""

    name: str
    pattern_type: str  # "race_condition", "deadlock", "thread_unsafe", "blocking"
    description: str
    locations: list[str]
    confidence: float  # 0.0 to 1.0
    severity: str  # "critical", "high", "medium", "low"
    risk_assessment: str  # Description of the risk
    mitigation: str  # Suggested fix
    metadata: dict[str, Any]


class ConcurrencyPatternMatcher:
    """
    Detects concurrency issues and thread safety problems.

    #AFTERMATH_PATTERN_IDENTIFIED: concurrency_pattern_detection

    PDA Loop:
    - PERCEIVE: Multi-layer concurrency analysis (AST + regex)
    - DECIDE: Risk-based severity classification
    - ACT: Pattern detection with mitigation strategies
    - AFTERMATH: Metrics + cognitive brain learning
    """

    def __init__(self):
        """Initialize concurrency pattern matcher."""
        self.detected_patterns: list[ConcurrencyPattern] = []
        #AFTERMATH_METRIC: concurrency_matcher_initialized

    def analyze_file(self, file_path: Path, content: Optional[str] = None) -> list[ConcurrencyPattern]:
        """
        Analyze a file for concurrency issues.

        #AFTERMATH_PATTERN_IDENTIFIED: file_concurrency_analysis

        Args:
            file_path: Path to file to analyze
            content: Optional file content (will read if not provided)

        Returns:
            List of detected concurrency patterns
        """
        if content is None:
            try:
                content = file_path.read_text()
            except (IOError, UnicodeDecodeError):
                return []

        detected: list[ConcurrencyPattern] = []

        # PERCEIVE: Multi-layer concurrency scanning
        if file_path.suffix == ".py":
            # Python-specific analysis using AST
            try:
                tree = ast.parse(content)
                detected.extend(self._detect_race_conditions(tree, file_path))
                detected.extend(self._detect_deadlock_risks(tree, file_path))
                detected.extend(self._detect_thread_unsafe(tree, file_path))
                detected.extend(self._detect_blocking_operations(tree, file_path))
                #AFTERMATH_PATTERN_IDENTIFIED: ast_concurrency_analysis
            except SyntaxError:
                # Intentionally skip files with syntax errors
                # Concurrency analysis requires valid AST
                pass

        # General regex-based detection (all file types)
        detected.extend(self._detect_regex_patterns(content, file_path))

        # AFTERMATH: Record metrics
        #AFTERMATH_METRIC: concurrency_issues_count = len(detected)

        return detected

    def _detect_race_conditions(self, tree: ast.AST, file_path: Path) -> list[ConcurrencyPattern]:
        """
        Detect potential race conditions.

        #AFTERMATH_PATTERN_IDENTIFIED: race_condition_detection
        """
        detected = []

        # Look for shared state access without synchronization
        for node in ast.walk(tree):
            # Global variable access in threaded code
            if isinstance(node, ast.Global):
                detected.append(ConcurrencyPattern(
                    name="global_variable_race",
                    pattern_type="race_condition",
                    description=f"Global variable access may cause race condition: {', '.join(node.names)}",
                    locations=[f"{file_path}:{node.lineno}"],
                    confidence=0.7,
                    severity="high",
                    risk_assessment="Multiple threads accessing shared global state without synchronization",
                    mitigation="Use threading.Lock, threading.RLock, or thread-local storage",
                    metadata={
                        "file": str(file_path),
                        "line": node.lineno,
                        "variables": node.names
                    }
                ))

            # Check-then-act pattern (classic race condition)
            if isinstance(node, ast.If):
                # Look for file existence checks followed by operations
                if self._contains_file_check(node.test):
                    detected.append(ConcurrencyPattern(
                        name="check_then_act_race",
                        pattern_type="race_condition",
                        description="Check-then-act pattern with file operations",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.75,
                        severity="medium",
                        risk_assessment="File state may change between check and action",
                        mitigation="Use atomic operations or file locking (fcntl)",
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno
                        }
                    ))

            # Dictionary/list modification in concurrent code
            if isinstance(node, (ast.Assign, ast.AugAssign)):
                if isinstance(node.targets[0] if isinstance(node, ast.Assign) else node.target,
                             (ast.Subscript, ast.Attribute)):
                    # Look for threading imports in file
                    if self._has_threading_usage(tree):
                        detected.append(ConcurrencyPattern(
                            name="shared_collection_modification",
                            pattern_type="race_condition",
                            description="Shared collection modification without synchronization",
                            locations=[f"{file_path}:{node.lineno}"],
                            confidence=0.65,
                            severity="medium",
                            risk_assessment="Concurrent modifications may corrupt data structure",
                            mitigation="Use queue.Queue, collections.deque, or synchronization primitives",
                            metadata={
                                "file": str(file_path),
                                "line": node.lineno
                            }
                        ))

        return detected

    def _detect_deadlock_risks(self, tree: ast.AST, file_path: Path) -> list[ConcurrencyPattern]:
        """
        Detect potential deadlock scenarios.

        #AFTERMATH_PATTERN_IDENTIFIED: deadlock_detection
        """
        detected = []

        # Look for nested lock acquisitions
        lock_acquisitions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        func_name = self._get_call_name(item.context_expr)
                        if 'lock' in func_name.lower() or 'acquire' in func_name.lower():
                            lock_acquisitions.append((node, func_name))

        # Check for nested locks
        for outer_node, outer_lock in lock_acquisitions:
            for inner_node, inner_lock in lock_acquisitions:
                if inner_node != outer_node and self._is_nested(outer_node, inner_node):
                    detected.append(ConcurrencyPattern(
                        name="nested_lock_deadlock",
                        pattern_type="deadlock",
                        description=f"Nested lock acquisition: {outer_lock} -> {inner_lock}",
                        locations=[f"{file_path}:{outer_node.lineno}"],
                        confidence=0.8,
                        severity="critical",
                        risk_assessment="Nested locks can cause deadlock if acquired in different order elsewhere",
                        mitigation="Establish lock ordering protocol, use timeout, or refactor to single lock",
                        metadata={
                            "file": str(file_path),
                            "line": outer_node.lineno,
                            "outer_lock": outer_lock,
                            "inner_lock": inner_lock
                        }
                    ))

        # Thread.join() inside lock
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        func_name = self._get_call_name(item.context_expr)
                        if 'lock' in func_name.lower():
                            # Check for thread.join() in body
                            for inner in ast.walk(node):
                                if isinstance(inner, ast.Call):
                                    inner_func = self._get_call_name(inner)
                                    if 'join' in inner_func.lower():
                                        detected.append(ConcurrencyPattern(
                                            name="join_under_lock",
                                            pattern_type="deadlock",
                                            description="Thread.join() called while holding lock",
                                            locations=[f"{file_path}:{inner.lineno}"],
                                            confidence=0.85,
                                            severity="high",
                                            risk_assessment="Can cause deadlock if joined thread needs the lock",
                                            mitigation="Release lock before joining or redesign synchronization",
                                            metadata={
                                                "file": str(file_path),
                                                "line": inner.lineno
                                            }
                                        ))

        return detected

    def _detect_thread_unsafe(self, tree: ast.AST, file_path: Path) -> list[ConcurrencyPattern]:
        """
        Detect thread-unsafe operations.

        #AFTERMATH_PATTERN_IDENTIFIED: thread_unsafe_detection
        """
        detected = []

        # Non-atomic operations on shared state
        for node in ast.walk(tree):
            # ++ operation (not atomic in Python)
            if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
                if self._has_threading_usage(tree):
                    detected.append(ConcurrencyPattern(
                        name="non_atomic_increment",
                        pattern_type="thread_unsafe",
                        description="Non-atomic increment operation on shared variable",
                        locations=[f"{file_path}:{node.lineno}"],
                        confidence=0.7,
                        severity="medium",
                        risk_assessment="Read-modify-write not atomic; can lose updates",
                        mitigation="Use threading.Lock or atomic operations",
                        metadata={
                            "file": str(file_path),
                            "line": node.lineno
                        }
                    ))

            # Time.sleep() in critical section
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        func_name = self._get_call_name(item.context_expr)
                        if 'lock' in func_name.lower():
                            # Look for sleep in body
                            for inner in ast.walk(node):
                                if isinstance(inner, ast.Call):
                                    inner_func = self._get_call_name(inner)
                                    if 'sleep' in inner_func.lower():
                                        detected.append(ConcurrencyPattern(
                                            name="sleep_under_lock",
                                            pattern_type="thread_unsafe",
                                            description="Sleep called while holding lock",
                                            locations=[f"{file_path}:{inner.lineno}"],
                                            confidence=0.9,
                                            severity="high",
                                            risk_assessment="Reduces concurrency and may cause performance issues",
                                            mitigation="Move sleep outside critical section",
                                            metadata={
                                                "file": str(file_path),
                                                "line": inner.lineno
                                            }
                                        ))

        return detected

    def _detect_blocking_operations(self, tree: ast.AST, file_path: Path) -> list[ConcurrencyPattern]:
        """
        Detect blocking operations in async/concurrent code.

        #AFTERMATH_PATTERN_IDENTIFIED: blocking_operation_detection
        """
        detected = []

        # Blocking I/O in async functions
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                # Look for synchronous I/O
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call):
                        func_name = self._get_call_name(inner)
                        if any(blocking in func_name.lower() for blocking in
                              ['open', 'read', 'write', 'connect', 'send', 'recv']):
                            if not func_name.startswith('await'):
                                detected.append(ConcurrencyPattern(
                                    name="blocking_io_in_async",
                                    pattern_type="blocking",
                                    description=f"Blocking I/O in async function: {func_name}",
                                    locations=[f"{file_path}:{inner.lineno}"],
                                    confidence=0.85,
                                    severity="high",
                                    risk_assessment="Blocks event loop, preventing other coroutines from running",
                                    mitigation="Use async I/O (aiofiles, asyncio) or run_in_executor",
                                    metadata={
                                        "file": str(file_path),
                                        "line": inner.lineno,
                                        "function": func_name
                                    }
                                ))

        return detected

    def _detect_regex_patterns(self, content: str, file_path: Path) -> list[ConcurrencyPattern]:
        """
        Detect concurrency issues using regex patterns.

        #AFTERMATH_PATTERN_IDENTIFIED: regex_concurrency_detection
        """
        detected = []

        # GIL-dependent code
        if re.search(r'from\s+multiprocessing\s+import.*Process', content):
            detected.append(ConcurrencyPattern(
                name="multiprocessing_usage",
                pattern_type="thread_unsafe",
                description="Using multiprocessing (beware of shared state)",
                locations=[str(file_path)],
                confidence=0.5,
                severity="low",
                risk_assessment="Shared state must use Manager or Value/Array",
                mitigation="Use multiprocessing.Manager for shared state or message passing",
                metadata={"file": str(file_path)}
            ))

        return detected

    def _contains_file_check(self, node: ast.AST) -> bool:
        """Check if expression contains file existence check."""
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                func_name = self._get_call_name(inner)
                if any(check in func_name.lower() for check in ['exists', 'isfile', 'isdir']):
                    return True
        return False

    def _has_threading_usage(self, tree: ast.AST) -> bool:
        """Check if file uses threading."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(alias.name in ['threading', 'concurrent.futures', 'asyncio', 'multiprocessing']
                      for alias in node.names):
                    return True
            elif isinstance(node, ast.ImportFrom):
                if node.module in ['threading', 'concurrent.futures', 'asyncio', 'multiprocessing']:
                    return True
        return False

    def _is_nested(self, outer: ast.AST, inner: ast.AST) -> bool:
        """Check if inner node is nested within outer node."""
        for node in ast.walk(outer):
            if node is inner:
                return True
        return False

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
        Generate summary of detected concurrency issues.

        #AFTERMATH_METRIC: concurrency_summary_generated

        Returns:
            Dictionary with concurrency metrics
        """
        summary = {
            "total_issues": len(self.detected_patterns),
            "by_type": {},
            "by_severity": {},
            "critical_risks": len([p for p in self.detected_patterns if p.severity in ["high", "critical"]])
        }

        for pattern in self.detected_patterns:
            summary["by_type"][pattern.pattern_type] = summary["by_type"].get(pattern.pattern_type, 0) + 1
            summary["by_severity"][pattern.severity] = summary["by_severity"].get(pattern.severity, 0) + 1

        #AFTERMATH_LESSON_LEARNED: concurrency_patterns_summarized
        return summary
