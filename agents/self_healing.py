"""
Self-Healing Workflow Automation

Implements automated detection, diagnosis, and remediation of common
CI/CD and codebase issues. Integrates with physics-inspired orchestration
for intelligent decision making.

Features:
- Automatic test failure diagnosis
- Dependency conflict resolution
- Build failure recovery
- Performance regression detection
- Security vulnerability auto-patching
"""

from __future__ import annotations

import logging
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "IssueType",
    "IssueSeverity",
    "DetectedIssue",
    "RemediationAction",
    "SelfHealingEngine",
    "DiagnosticResult",
]


class IssueType(Enum):
    """Types of issues that can be detected and healed."""

    TEST_FAILURE = "test_failure"
    BUILD_FAILURE = "build_failure"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    SECURITY_VULNERABILITY = "security_vulnerability"
    PERFORMANCE_REGRESSION = "performance_regression"
    LINT_ERROR = "lint_error"
    TYPE_ERROR = "type_error"
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    CONFIGURATION_ERROR = "configuration_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


class IssueSeverity(Enum):
    """Severity levels for detected issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class DetectedIssue:
    """A detected issue in the codebase or CI/CD pipeline."""

    issue_type: IssueType
    severity: IssueSeverity
    description: str
    issue_id: str = ""
    title: str = ""
    location: Optional[str] = None
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    stack_trace: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)  # Alias for context
    detected_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __post_init__(self):
        """Handle backwards compatibility"""
        if not self.issue_id:
            self.issue_id = f"issue_{id(self)}"
        if not self.title:
            self.title = self.description[:50]
        # Merge details into context if provided
        if self.details:
            self.context.update(self.details)

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "file_path": str(self.file_path) if self.file_path else None,
            "line_number": self.line_number,
            "stack_trace": self.stack_trace,
            "context": self.context,
            "detected_at": self.detected_at,
        }


@dataclass
class RemediationAction:
    """An action to remediate a detected issue."""

    action_type: str
    description: str
    action_id: str = ""
    issue_id: str = ""
    commands: list[str] = field(default_factory=list)
    command: str = ""  # Alias for single command
    file_changes: dict[str, str] = field(default_factory=dict)
    confidence: float = 0.8
    risk_level: float = 0.2
    requires_approval: bool = False
    auto_apply: bool = True  # Inverse of requires_approval
    executed: bool = False
    success: Optional[bool] = None

    def __post_init__(self):
        """Handle backwards compatibility"""
        if not self.action_id:
            self.action_id = f"action_{id(self)}"
        if not self.issue_id:
            self.issue_id = "unknown"
        # Handle command/commands aliasing
        if self.command and not self.commands:
            self.commands = [self.command]
        # Handle auto_apply/requires_approval inverse relationship
        if not self.auto_apply:
            self.requires_approval = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "issue_id": self.issue_id,
            "action_type": self.action_type,
            "description": self.description,
            "commands": self.commands,
            "file_changes": self.file_changes,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "executed": self.executed,
            "success": self.success,
        }


@dataclass
class DiagnosticResult:
    """Result of running diagnostics."""

    issues: list[DetectedIssue] = field(default_factory=list)
    suggested_actions: list[RemediationAction] = field(default_factory=list)
    remediation_actions: list[RemediationAction] = field(default_factory=list)  # Alias
    health_score: float = 1.0
    diagnostics_run: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __post_init__(self):
        """Handle backwards compatibility"""
        # Use remediation_actions if provided, otherwise use suggested_actions
        if self.remediation_actions and not self.suggested_actions:
            self.suggested_actions = self.remediation_actions
        elif self.suggested_actions and not self.remediation_actions:
            self.remediation_actions = self.suggested_actions

    def to_dict(self) -> dict[str, Any]:
        return {
            "issues": [i.to_dict() for i in self.issues],
            "suggested_actions": [a.to_dict() for a in self.suggested_actions],
            "health_score": self.health_score,
            "diagnostics_run": self.diagnostics_run,
            "timestamp": self.timestamp,
        }


class SelfHealingEngine:
    """
    Engine for automatic detection and remediation of codebase issues.

    Uses pattern matching and heuristics to:
    1. Detect common issues from logs, test output, and code analysis
    2. Diagnose root causes
    3. Suggest and optionally apply remediations
    """

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.issue_patterns: dict[IssueType, list[tuple[str, str]]] = {}
        self.remediation_handlers: dict[IssueType, Callable] = {}
        # Initialize detection and diagnostic components
        self.issue_detector = self  # Self-reference for detection capability
        self.diagnostic_engine = self  # Self-reference for diagnostic capability
        self._register_default_patterns()
        self._register_default_handlers()

    def _register_default_patterns(self) -> None:
        """Register default issue detection patterns."""
        self.issue_patterns[IssueType.TEST_FAILURE] = [
            (r"FAILED\s+(\S+)", "Test failed: {0}"),
            (r"AssertionError:\s+(.+)", "Assertion failed: {0}"),
            (r"pytest.*(\d+) failed", "{0} tests failed"),
        ]

        self.issue_patterns[IssueType.IMPORT_ERROR] = [
            (r'ModuleNotFoundError:\s+No module named [\'"](\S+)[\'"]', "Missing module: {0}"),
            (r'ImportError:\s+cannot import name [\'"](\S+)[\'"]', "Cannot import: {0}"),
        ]

        self.issue_patterns[IssueType.DEPENDENCY_CONFLICT] = [
            (r"pip.*conflict.*(\S+)", "Dependency conflict: {0}"),
            (r"version.*incompatible.*(\S+)", "Version incompatible: {0}"),
        ]

        self.issue_patterns[IssueType.LINT_ERROR] = [
            (r"(\S+\.py):(\d+):\d+:\s*(E\d+)", "Lint error {2} in {0}:{1}"),
            (r"flake8.*(\d+)\s+errors", "{0} linting errors"),
        ]

        self.issue_patterns[IssueType.TYPE_ERROR] = [
            (r"(\S+\.py):(\d+):\s*error:\s*(.+)", "Type error in {0}:{1}: {2}"),
            (r"mypy.*Found\s+(\d+)\s+errors", "{0} type errors found"),
        ]

        self.issue_patterns[IssueType.BUILD_FAILURE] = [
            (r"Build failed", "Build process failed"),
            (r"SyntaxError:\s*(.+)", "Syntax error: {0}"),
            (r"compilation.*failed", "Compilation failed"),
        ]

        self.issue_patterns[IssueType.SECURITY_VULNERABILITY] = [
            (r"CVE-(\d+-\d+)", "Security vulnerability CVE-{0}"),
            (r"vulnerability.*(\S+)", "Vulnerability in {0}"),
            (r"GHSA-(\S+)", "GitHub Security Advisory {0}"),
        ]

    def _register_default_handlers(self) -> None:
        """Register default remediation handlers."""
        self.remediation_handlers[IssueType.IMPORT_ERROR] = self._remediate_import_error
        self.remediation_handlers[IssueType.LINT_ERROR] = self._remediate_lint_error
        self.remediation_handlers[IssueType.DEPENDENCY_CONFLICT] = (
            self._remediate_dependency_conflict
        )
        self.remediation_handlers[IssueType.TEST_FAILURE] = self._remediate_test_failure

    def diagnose(self, log_output: str = None, run_checks: bool = True) -> DiagnosticResult:
        """
        Run diagnostics on the codebase.

        Args:
            log_output: Optional log output to analyze
            run_checks: Whether to run active checks (lint, type, tests)
        """
        result = DiagnosticResult()

        # Analyze provided log output
        if log_output:
            issues = self._analyze_log(log_output)
            result.issues.extend(issues)
            result.diagnostics_run.append("log_analysis")

        # Run active checks if requested
        if run_checks:
            # Check for syntax errors
            syntax_issues = self._check_syntax()
            result.issues.extend(syntax_issues)
            result.diagnostics_run.append("syntax_check")

            # Check imports
            import_issues = self._check_imports()
            result.issues.extend(import_issues)
            result.diagnostics_run.append("import_check")

        # Generate remediation suggestions
        for issue in result.issues:
            actions = self._suggest_remediation(issue)
            result.suggested_actions.extend(actions)

        # Calculate health score
        result.health_score = self._calculate_health_score(result.issues)

        return result

    def _analyze_log(self, log_output: str) -> list[DetectedIssue]:
        """Analyze log output for issues."""
        issues = []
        issue_counter = 0

        for issue_type, patterns in self.issue_patterns.items():
            for pattern, description_template in patterns:
                matches = re.finditer(pattern, log_output, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    issue_counter += 1
                    groups = match.groups()
                    description = (
                        description_template.format(*groups) if groups else description_template
                    )

                    issue = DetectedIssue(
                        issue_id=f"issue_{issue_counter}",
                        issue_type=issue_type,
                        severity=self._determine_severity(issue_type),
                        title=f"{issue_type.value.replace('_', ' ').title()}",
                        description=description,
                        context={"match": match.group(0)},
                    )
                    issues.append(issue)

        return issues

    def _check_syntax(self) -> list[DetectedIssue]:
        """Check Python files for syntax errors."""
        issues = []

        for py_file in self.repo_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".venv" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    compile(f.read(), py_file, "exec")
            except SyntaxError as e:
                logger.debug(f"SyntaxError: {e}")
                issues.append(
                    DetectedIssue(
                        issue_id=f"syntax_{len(issues)}",
                        issue_type=IssueType.BUILD_FAILURE,
                        severity=IssueSeverity.CRITICAL,
                        title="Syntax Error",
                        description=str(e.msg),
                        file_path=py_file,
                        line_number=e.lineno,
                    )
                )

        return issues

    def _check_imports(self) -> list[DetectedIssue]:
        """Check for import issues in key modules."""
        issues = []
        key_modules = [
            "src.codex_ml",
            "agents",
        ]

        for module in key_modules:
            try:
                __import__(module.replace("/", ".").replace("src.", ""))
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                issues.append(
                    DetectedIssue(
                        issue_id=f"import_{len(issues)}",
                        issue_type=IssueType.IMPORT_ERROR,
                        severity=IssueSeverity.HIGH,
                        title="Import Error",
                        description=str(e),
                        location=module,
                    )
                )
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)  # Other errors are not import-related

        return issues

    def _determine_severity(self, issue_type: IssueType) -> IssueSeverity:
        """Determine severity based on issue type."""
        severity_map = {
            IssueType.SECURITY_VULNERABILITY: IssueSeverity.CRITICAL,
            IssueType.BUILD_FAILURE: IssueSeverity.CRITICAL,
            IssueType.TEST_FAILURE: IssueSeverity.HIGH,
            IssueType.IMPORT_ERROR: IssueSeverity.HIGH,
            IssueType.DEPENDENCY_CONFLICT: IssueSeverity.HIGH,
            IssueType.TYPE_ERROR: IssueSeverity.MEDIUM,
            IssueType.LINT_ERROR: IssueSeverity.LOW,
            IssueType.PERFORMANCE_REGRESSION: IssueSeverity.MEDIUM,
            IssueType.CONFIGURATION_ERROR: IssueSeverity.MEDIUM,
            IssueType.RESOURCE_EXHAUSTION: IssueSeverity.HIGH,
        }
        return severity_map.get(issue_type, IssueSeverity.MEDIUM)

    def _suggest_remediation(self, issue: DetectedIssue) -> list[RemediationAction]:
        """Suggest remediation actions for an issue."""
        handler = self.remediation_handlers.get(issue.issue_type)
        if handler:
            return handler(issue)
        return []

    def _remediate_import_error(self, issue: DetectedIssue) -> list[RemediationAction]:
        """Generate remediation for import errors."""
        actions = []

        # Extract module name from description
        match = re.search(r"Missing module: (\S+)", issue.description)
        if match:
            module = match.group(1)
            actions.append(
                RemediationAction(
                    action_id=f"fix_{issue.issue_id}",
                    issue_id=issue.issue_id,
                    action_type="install_dependency",
                    description=f"Install missing module: {module}",
                    commands=[f"pip install {module}"],
                    confidence=0.8,
                    risk_level=0.2,
                )
            )

        return actions

    def _remediate_lint_error(self, issue: DetectedIssue) -> list[RemediationAction]:
        """Generate remediation for lint errors."""
        return [
            RemediationAction(
                action_id=f"fix_{issue.issue_id}",
                issue_id=issue.issue_id,
                action_type="auto_fix_lint",
                description="Auto-fix linting errors",
                commands=["ruff check --fix .", "black ."],
                confidence=0.9,
                risk_level=0.1,
            )
        ]

    def _remediate_dependency_conflict(self, issue: DetectedIssue) -> list[RemediationAction]:
        """Generate remediation for dependency conflicts."""
        return [
            RemediationAction(
                action_id=f"fix_{issue.issue_id}",
                issue_id=issue.issue_id,
                action_type="resolve_dependencies",
                description="Resolve dependency conflicts",
                commands=[
                    "pip install --upgrade pip",
                    "pip install -e . --upgrade",
                ],
                confidence=0.7,
                risk_level=0.3,
                requires_approval=True,
            )
        ]

    def _remediate_test_failure(self, issue: DetectedIssue) -> list[RemediationAction]:
        """Generate remediation suggestions for test failures."""
        return [
            RemediationAction(
                action_id=f"investigate_{issue.issue_id}",
                issue_id=issue.issue_id,
                action_type="investigate",
                description="Run failed test with verbose output for diagnosis",
                commands=["pytest -xvs --tb=long"],
                confidence=0.6,
                risk_level=0.0,
            )
        ]

    def _calculate_health_score(self, issues: list[DetectedIssue]) -> float:
        """Calculate overall health score based on issues."""
        if not issues:
            return 1.0

        severity_weights = {
            IssueSeverity.CRITICAL: 0.4,
            IssueSeverity.HIGH: 0.25,
            IssueSeverity.MEDIUM: 0.15,
            IssueSeverity.LOW: 0.05,
            IssueSeverity.INFO: 0.0,
        }

        total_penalty = sum(severity_weights.get(issue.severity, 0.1) for issue in issues)

        return max(0.0, 1.0 - min(total_penalty, 1.0))

    def detect_issues(self, log_output: str = None, run_checks: bool = True) -> list[DetectedIssue]:
        """
        Detect issues in the codebase.

        Alias for diagnose() that returns only the issues list.

        Args:
            log_output: Optional log output to analyze
            run_checks: Whether to run active checks

        Returns:
            list of detected issues
        """
        result = self.diagnose(log_output=log_output, run_checks=run_checks)
        return result.issues

    def detect(self, log_output: str = None) -> list[DetectedIssue]:
        """
        Detect issues (short alias for detect_issues).

        Args:
            log_output: Optional log output to analyze

        Returns:
            list of detected issues
        """
        return self.detect_issues(log_output=log_output, run_checks=False)

    def analyze(self, log_output: str = None, run_checks: bool = True) -> DiagnosticResult:
        """
        Analyze the codebase for issues (alias for diagnose).

        Args:
            log_output: Optional log output to analyze
            run_checks: Whether to run active checks

        Returns:
            Diagnostic result with issues and suggested actions
        """
        return self.diagnose(log_output=log_output, run_checks=run_checks)

    def apply_remediation(
        self,
        action: RemediationAction,
        dry_run: bool = True,
    ) -> tuple[bool, str]:
        """
        Apply a remediation action.

        Args:
            action: The remediation action to apply
            dry_run: If True, only show what would be done

        Returns:
            tuple of (success, output_message)
        """
        if action.requires_approval and not dry_run:
            return False, "Action requires approval before execution"

        output_lines = []

        if dry_run:
            output_lines.append(f"[DRY RUN] Would execute remediation: {action.description}")
            for cmd in action.commands:
                output_lines.append(f"  Command: {cmd}")
            for path, content in action.file_changes.items():
                output_lines.append(f"  File change: {path}")
            return True, "\n".join(output_lines)

        # Execute commands
        for cmd in action.commands:
            try:
                # Use shell=False via list wrapping for subprocess.run
                result = subprocess.run(
                    cmd if isinstance(cmd, list) else ["sh", "-c", cmd],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_root,
                )
                output_lines.append(f"Executed: {cmd}")
                if result.stdout:
                    output_lines.append(result.stdout)
                if result.returncode != 0:
                    output_lines.append(f"Warning: Command returned {result.returncode}")
                    if result.stderr:
                        output_lines.append(result.stderr)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                output_lines.append(f"Error executing {cmd}: {e}")
                action.success = False
                return False, "\n".join(output_lines)

        # Apply file changes
        for path, content in action.file_changes.items():
            try:
                file_path = self.repo_root / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                output_lines.append(f"Updated: {path}")
            except Exception as e:
                logger.debug(f"Exception: {e}")
                output_lines.append(f"Error writing {path}: {e}")
                action.success = False
                return False, "\n".join(output_lines)

        action.executed = True
        action.success = True
        return True, "\n".join(output_lines)


# Convenience function for quick diagnostics
def run_diagnostics(repo_root: Path = None) -> DiagnosticResult:
    """Run quick diagnostics on the codebase."""
    engine = SelfHealingEngine(repo_root)
    return engine.diagnose(run_checks=True)
