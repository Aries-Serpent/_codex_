"""
Deterritorialization Engine

Implements Deleuzian deterritorialization for identifying and breaking
rigid code patterns to enable creativity and innovation.

Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#deterritorialization
Philosophical Foundation: Deleuze & Guattari - Anti-Oedipus (1972)

Core Concepts:
- Territorialization: Formation of stable patterns/structures
- Deterritorialization: Breaking fixed patterns to enable creativity
- Reterritorialization: Formation of new patterns
- Line of Flight: Escape route from rigid structure

Deterritorialization is NOT:
- Random destruction
- Rebellion against structure
- Chaos for chaos's sake

Deterritorialization IS:
- Strategic pattern-breaking for innovation
- Creating "lines of flight" to new possibilities
- Productive transformation, not mere negation
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)


class RigidityType(Enum):
    """Types of rigidity in code that may benefit from deterritorialization."""

    DEEP_NESTING = "deep_nesting"  # Excessive nesting (> 4 levels)
    LONG_METHOD = "long_method"  # Methods > 50 lines
    GOD_CLASS = "god_class"  # Classes with too many responsibilities
    TIGHT_COUPLING = "tight_coupling"  # Excessive dependencies
    HARDCODED_VALUES = "hardcoded_values"  # Magic numbers/strings
    REPEATED_PATTERNS = "repeated_patterns"  # Code duplication
    OVERLY_COMPLEX = "overly_complex"  # High cyclomatic complexity


@dataclass
class RigidityDetection:
    """A detected instance of rigidity in the codebase."""

    rigidity_type: RigidityType
    file_path: str
    line_number: int
    severity: float  # 0.0 (low) to 1.0 (high)
    description: str
    context: str  # Code snippet showing the issue
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"{self.rigidity_type.value} at {self.file_path}:{self.line_number} "
            f"(severity: {self.severity:.2f})"
        )


@dataclass
class LineOfFlight:
    """
    A "line of flight" - an escape route from rigidity.

    Following Deleuze: Not rebellion, but creation of something new.
    """

    rigidity: RigidityDetection
    proposed_action: str
    expected_outcome: str
    innovation_potential: float  # 0.0 to 1.0
    risk_level: float  # 0.0 (low) to 1.0 (high)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        return (
            f"Line of flight from {self.rigidity.rigidity_type.value}: "
            f"{self.proposed_action} (innovation: {self.innovation_potential:.2%}, "
            f"risk: {self.risk_level:.2%})"
        )


class RigidityDetector:
    """
    Detects rigid patterns in code that may benefit from deterritorialization.

    Uses AST analysis to identify structural rigidity.
    """

    def __init__(
        self,
        max_nesting: int = 4,
        max_method_lines: int = 50,
        max_class_methods: int = 20,
    ) -> None:
        self.max_nesting = max_nesting
        self.max_method_lines = max_method_lines
        self.max_class_methods = max_class_methods
        self.detections: list[RigidityDetection] = []

    def analyze_file(self, file_path: Path) -> list[RigidityDetection]:
        """
        Analyze a Python file for rigidity.

        Args:
            file_path: Path to Python file

        Returns:
            List of detected rigidities
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._analyze_ast(tree, str(file_path), source)

        except SyntaxError as e:
            LOGGER.warning(f"Syntax error in {file_path}: {e}")
        except (IOError, OSError) as e:
            LOGGER.error(f"Error analyzing {file_path}: {e}")

        return self.detections

    def _analyze_ast(self, tree: ast.AST, file_path: str, source: str) -> None:
        """Analyze AST for rigid patterns."""
        for node in ast.walk(tree):
            # Check for god classes
            if isinstance(node, ast.ClassDef):
                self._check_god_class(node, file_path, source)

            # Check for long methods
            if isinstance(node, ast.FunctionDef):
                self._check_long_method(node, file_path, source)
                self._check_deep_nesting(node, file_path, source)

    def _check_god_class(self, node: ast.ClassDef, file_path: str, source: str) -> None:
        """Check if a class has too many methods (god class pattern)."""
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        if len(methods) > self.max_class_methods:
            severity = min(1.0, (len(methods) - self.max_class_methods) / 20.0)

            context = self._get_code_snippet(source, node.lineno, 3)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.GOD_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Class '{node.name}' has {len(methods)} methods "
                    f"(threshold: {self.max_class_methods})",
                    context=context,
                    metadata={"num_methods": len(methods), "class_name": node.name},
                )
            )

    def _check_long_method(self, node: ast.FunctionDef, file_path: str, source: str) -> None:
        """Check if a method is too long."""
        if not hasattr(node, "end_lineno") or node.end_lineno is None:
            return

        method_lines = node.end_lineno - node.lineno + 1

        if method_lines > self.max_method_lines:
            severity = min(1.0, (method_lines - self.max_method_lines) / 50.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has {method_lines} lines "
                    f"(threshold: {self.max_method_lines})",
                    context=context,
                    metadata={"num_lines": method_lines, "method_name": node.name},
                )
            )

    def _check_deep_nesting(self, node: ast.FunctionDef, file_path: str, source: str) -> None:
        """Check for deep nesting in a method."""
        max_depth = self._get_max_nesting_depth(node)

        if max_depth > self.max_nesting:
            severity = min(1.0, (max_depth - self.max_nesting) / 4.0)

            context = self._get_code_snippet(source, node.lineno, 5)

            self.detections.append(
                RigidityDetection(
                    rigidity_type=RigidityType.DEEP_NESTING,
                    file_path=file_path,
                    line_number=node.lineno,
                    severity=severity,
                    description=f"Method '{node.name}' has nesting depth {max_depth} "
                    f"(threshold: {self.max_nesting})",
                    context=context,
                    metadata={"max_depth": max_depth, "method_name": node.name},
                )
            )

    def _get_max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Recursively calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _get_code_snippet(self, source: str, line_num: int, num_lines: int = 3) -> str:
        """Extract a code snippet around a line number."""
        lines = source.splitlines()
        start = max(0, line_num - 1)
        end = min(len(lines), line_num + num_lines)
        return "\n".join(lines[start:end])


class DeterritorializationEngine:
    """
    Engine for identifying rigid patterns and proposing lines of flight.

    Implements Deleuzian deterritorialization principles to enable
    creative refactoring and innovation.

    Example:
        >>> engine = DeterritorializationEngine()
        >>> detections = engine.detect_rigidity("src/codex/")
        >>> lines_of_flight = engine.propose_lines_of_flight()
        >>> for line in lines_of_flight:
        ...     logger.info(line)
    """

    def __init__(self) -> None:
        self.detector = RigidityDetector()
        self.rigidities: list[RigidityDetection] = []
        self.lines_of_flight: list[LineOfFlight] = []
        LOGGER.info("DeterritorializationEngine initialized")

    def detect_rigidity(self, path: str | Path) -> list[RigidityDetection]:
        """
        Detect rigidity in code at the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            List of detected rigidities
        """
        path = Path(path)

        if path.is_file() and path.suffix == ".py":
            self.rigidities.extend(self.detector.analyze_file(path))

        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                self.rigidities.extend(self.detector.analyze_file(py_file))

        LOGGER.info(f"Detected {len(self.rigidities)} rigidities in {path}")
        return self.rigidities

    def propose_lines_of_flight(self, min_severity: float = 0.5) -> list[LineOfFlight]:
        """
        Propose lines of flight for detected rigidities.

        A "line of flight" is an escape route from rigidity - not destruction,
        but creation of new possibilities.

        Args:
            min_severity: Minimum severity to propose lines of flight (0.0 to 1.0)

        Returns:
            List of proposed lines of flight
        """
        for rigidity in self.rigidities:
            if rigidity.severity < min_severity:
                continue

            line_of_flight = self._create_line_of_flight(rigidity)
            if line_of_flight:
                self.lines_of_flight.append(line_of_flight)

        LOGGER.info(
            f"Proposed {len(self.lines_of_flight)} lines of flight (min_severity={min_severity})"
        )
        return self.lines_of_flight

    def _create_line_of_flight(self, rigidity: RigidityDetection) -> Optional[LineOfFlight]:
        """Create a line of flight for a specific rigidity."""
        strategies = {
            RigidityType.DEEP_NESTING: self._propose_flatten_nesting,
            RigidityType.LONG_METHOD: self._propose_extract_method,
            RigidityType.GOD_CLASS: self._propose_split_class,
            RigidityType.TIGHT_COUPLING: self._propose_decouple,
            RigidityType.HARDCODED_VALUES: self._propose_extract_constant,
            RigidityType.REPEATED_PATTERNS: self._propose_extract_function,
            RigidityType.OVERLY_COMPLEX: self._propose_simplify,
        }

        strategy = strategies.get(rigidity.rigidity_type)
        if strategy:
            return strategy(rigidity)

        return None

    def _propose_flatten_nesting(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose flattening deep nesting."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Flatten nesting by extracting nested blocks into separate methods. "
                "Use early returns to reduce indentation levels."
            ),
            expected_outcome="Reduced nesting depth, improved readability",
            innovation_potential=0.6,
            risk_level=0.2,
        )

    def _propose_extract_method(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting long method into smaller methods."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract logical blocks into separate methods with clear names. "
                "Follow Single Responsibility Principle."
            ),
            expected_outcome="Smaller, focused methods that are easier to test",
            innovation_potential=0.7,
            risk_level=0.3,
        )

    def _propose_split_class(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose splitting a god class."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Identify distinct responsibilities and split into separate classes. "
                "Consider using composition or strategy pattern."
            ),
            expected_outcome="Cohesive classes with clear responsibilities",
            innovation_potential=0.8,
            risk_level=0.6,
        )

    def _propose_decouple(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose decoupling tightly coupled code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Introduce interfaces or abstract base classes. "
                "Use dependency injection to reduce coupling."
            ),
            expected_outcome="Loosely coupled modules that are easier to test and maintain",
            innovation_potential=0.7,
            risk_level=0.5,
        )

    def _propose_extract_constant(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting hardcoded values."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract magic numbers and strings into named constants. "
                "Consider using configuration files for values that may change."
            ),
            expected_outcome="Self-documenting code with maintainable configuration",
            innovation_potential=0.5,
            risk_level=0.1,
        )

    def _propose_extract_function(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose extracting repeated patterns."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Extract repeated code into reusable functions or classes. "
                "Use parameterization to handle variations."
            ),
            expected_outcome="DRY code with reduced maintenance burden",
            innovation_potential=0.6,
            risk_level=0.3,
        )

    def _propose_simplify(self, rigidity: RigidityDetection) -> LineOfFlight:
        """Propose simplifying overly complex code."""
        return LineOfFlight(
            rigidity=rigidity,
            proposed_action=(
                "Simplify complex logic by breaking into smaller steps. "
                "Use descriptive variable names and comments to clarify intent."
            ),
            expected_outcome="Clearer, more maintainable code",
            innovation_potential=0.5,
            risk_level=0.2,
        )

    def calculate_deterritorialization_force(
        self, rigidity_score: float, innovation_score: float
    ) -> float:
        """
        Calculate deterritorialization force.

        F_deterr = Innovation_Pressure - Rigidity

        Where:
        - Positive: Deterritorialization needed
        - Negative: Reterritorialization occurring
        - Zero: Equilibrium

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#deterritorialization-force
        """
        force = innovation_score - rigidity_score
        LOGGER.debug(
            f"Deterritorialization force: {force:.2f} "
            f"(innovation: {innovation_score:.2f}, rigidity: {rigidity_score:.2f})"
        )
        return force

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about detected rigidities and lines of flight."""
        rigidity_counts: dict[str, Any] = {}
        for rigidity in self.rigidities:
            rtype = rigidity.rigidity_type.value
            rigidity_counts[rtype] = rigidity_counts.get(rtype, 0) + 1

        avg_severity = (
            sum(r.severity for r in self.rigidities) / len(self.rigidities)
            if self.rigidities
            else 0.0
        )

        return {
            "total_rigidities": len(self.rigidities),
            "rigidity_by_type": rigidity_counts,
            "average_severity": avg_severity,
            "lines_of_flight": len(self.lines_of_flight),
            "high_priority_rigidities": sum(1 for r in self.rigidities if r.severity >= 0.7),
        }

    def export_report(self) -> dict[str, Any]:
        """
        Export a comprehensive deterritorialization report.

        Returns:
            Dictionary with rigidities, lines of flight, and recommendations
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rigidities": [
                {
                    "type": r.rigidity_type.value,
                    "file": r.file_path,
                    "line": r.line_number,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rigidities
            ],
            "lines_of_flight": [
                {
                    "rigidity_type": lof.rigidity.rigidity_type.value,
                    "action": lof.proposed_action,
                    "outcome": lof.expected_outcome,
                    "innovation_potential": lof.innovation_potential,
                    "risk_level": lof.risk_level,
                }
                for lof in self.lines_of_flight
            ],
            "stats": self.get_stats(),
        }
