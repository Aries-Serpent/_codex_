#!/usr/bin/env python3
"""
Error Classification System for CI Self-Healing Infrastructure

Classifies CI failures into categories:
- Network errors (transient, auto-recoverable)
- Resource errors (memory, disk, timeout - recoverable with backoff)
- Logic errors (code bugs, require manual intervention)
- Infrastructure errors (runner, GitHub API issues)
"""

import json
import re
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta


class ErrorCategory(Enum):
    """CI failure categories for routing and recovery."""
    NETWORK_TRANSIENT = "network_transient"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    IMPORT_ERROR = "import_error"
    FLAKY_TEST = "flaky_test"
    WORKFLOW_SYNTAX = "workflow_syntax"
    SECURITY_POLICY = "security_policy"
    LOGIC_ERROR = "logic_error"
    UNKNOWN = "unknown"


class RecoverySeverity(Enum):
    """Recovery difficulty and escalation level."""
    AUTO_RECOVERABLE = "auto_recoverable"  # Retry immediately
    BACKOFF_RECOVERABLE = "backoff_recoverable"  # Retry with exponential backoff
    ESCALATE_REQUIRED = "escalate_required"  # Requires manual intervention
    CRITICAL = "critical"  # System critical, escalate immediately


@dataclass
class ErrorSignature:
    """Detected error signature with patterns and metadata."""
    pattern_id: str
    category: ErrorCategory
    severity: RecoverySeverity
    message: str
    confidence: float  # 0.0-1.0
    suggestions: List[str]
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return {
            "pattern_id": self.pattern_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "confidence": self.confidence,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
        }


class ErrorClassifier:
    """Classify CI failures and determine recovery strategy."""

    # Network-related error patterns (transient, auto-recoverable)
    NETWORK_PATTERNS = [
        (r"Connection refused", "Connection refused - network unavailable"),
        (r"Connection reset by peer", "Connection reset - transient network issue"),
        (r"timeout: \[Errno 110\]", "Connection timeout - network latency"),
        (r"Failed to resolve|Name or service not known", "DNS resolution failure"),
        (r"Temporary failure in name resolution", "DNS transient failure"),
        (r"requests\.exceptions\.ConnectionError", "HTTP connection error"),
        (r"urllib3\.exceptions\.NewConnectionError", "URLlib3 connection error"),
        (r"HTTPSConnectionPool.*Connection refused", "HTTPS connection refused"),
    ]

    # Resource exhaustion patterns (backoff recoverable)
    RESOURCE_PATTERNS = [
        (r"MemoryError|Out of memory", "Memory exhaustion"),
        (r"OSError: \[Errno 28\]|No space left on device", "Disk space exhausted"),
        (r"Max retries exceeded|Too many retries", "Resource contention - retry limit"),
        (r"Deadlock detected", "Database deadlock"),
        (r"Resource temporarily unavailable", "Resource contention - backoff needed"),
        (r"failed to download|Failed to fetch", "Artifact download failure"),
    ]

    # Timeout patterns (backoff recoverable)
    TIMEOUT_PATTERNS = [
        (r"SIGTERM|signal: terminated", "Process killed by timeout signal"),
        (r"Timeout expired|timeout occurred", "Operation timeout"),
        (r"Test.*timeout|pytest.*timeout", "Test execution timeout"),
        (r"workflow.*timeout|step.*timeout", "Workflow step timeout"),
        (r"Job exceeded.*maximum execution time", "GitHub Actions timeout"),
        (r"socket\.timeout", "Socket timeout"),
    ]

    # Dependency conflict patterns (backoff recoverable)
    DEPENDENCY_PATTERNS = [
        (r"Cannot find module|No module named|ImportError", "Module import error"),
        (r"Conflicting requirements", "Dependency conflict"),
        (r"ERROR: pip's dependency resolver does not currently", "Pip resolver conflict"),
        (r"version `.*\' not found in remotes", "Git dependency not found"),
        (r"dependency.*not found|missing dependency", "Missing dependency"),
        (r"version conflict|version mismatch", "Version mismatch"),
    ]

    # Flaky test patterns (backoff recoverable)
    FLAKY_PATTERNS = [
        (r"assert.*==|AssertionError", "Test assertion failure"),
        (r"race condition|timing dependent", "Race condition suspected"),
        (r"intermittent failure|sometimes fails", "Intermittent test failure"),
        (r"random\.seed|fixture.*flaky", "Flaky test detected"),
        (r"FLAKY|@pytest\.mark\.flaky", "Marked as flaky test"),
    ]

    # Workflow syntax errors (logic error - escalate)
    WORKFLOW_PATTERNS = [
        (r"invalid.*yaml|YAML parse error", "YAML syntax error"),
        (r"Workflow.*invalid|Invalid workflow", "Invalid workflow definition"),
        (r"Unknown input|Unexpected input", "Invalid workflow input"),
        (r"required key not provided|missing required", "Missing required field"),
    ]

    # Security/Policy errors (escalate)
    SECURITY_PATTERNS = [
        (r"PermissionError|Permission denied", "Permission denied"),
        (r"Unauthorized|401|403", "Unauthorized access"),
        (r"Secret.*not found|Secret.*invalid", "Secret/credential issue"),
        (r"policy.*violation|policy.*denied", "Security policy violation"),
    ]

    # Logic errors (code bugs - escalate)
    LOGIC_PATTERNS = [
        (r"IndexError|KeyError|AttributeError|TypeError", "Python logic error"),
        (r"Segmentation fault|SIGSEGV", "Segmentation fault"),
        (r"Panic in runtime|panic: runtime", "Runtime panic"),
        (r"assertion failed|invariant violated", "Assertion failed"),
    ]

    def __init__(self):
        """Initialize error classifier."""
        self.patterns = self._compile_patterns()

    @staticmethod
    def _compile_patterns() -> Dict[str, List[Tuple]]:
        """Compile all error patterns into dict."""
        return {
            "network": ErrorClassifier.NETWORK_PATTERNS,
            "resource": ErrorClassifier.RESOURCE_PATTERNS,
            "timeout": ErrorClassifier.TIMEOUT_PATTERNS,
            "dependency": ErrorClassifier.DEPENDENCY_PATTERNS,
            "flaky": ErrorClassifier.FLAKY_PATTERNS,
            "workflow": ErrorClassifier.WORKFLOW_PATTERNS,
            "security": ErrorClassifier.SECURITY_PATTERNS,
            "logic": ErrorClassifier.LOGIC_PATTERNS,
        }

    def classify(self, error_text: str, attempt_number: int = 1) -> Optional[ErrorSignature]:
        """
        Classify error text and return recovery recommendation.

        Parameters
        ----------
        error_text : str
            Raw error message/log output
        attempt_number : int
            Current retry attempt number (1-based)

        Returns
        -------
        ErrorSignature
            Classification result with recovery strategy
        """
        if not error_text or not error_text.strip():
            return None

        # Check each pattern category in priority order
        for category, patterns in self._get_pattern_priority():
            for pattern, description in patterns:
                if re.search(pattern, error_text, re.IGNORECASE):
                    return self._build_signature(
                        category, pattern, description, attempt_number
                    )

        # Unknown error
        return ErrorSignature(
            pattern_id="unknown",
            category=ErrorCategory.UNKNOWN,
            severity=RecoverySeverity.ESCALATE_REQUIRED,
            message="Unknown error type - requires investigation",
            confidence=0.3,
            suggestions=["Review full error logs", "Escalate to human review"],
        )

    def _get_pattern_priority(self) -> List[Tuple[str, List[Tuple]]]:
        """Get pattern categories in priority order for matching."""
        # Network and timeout first (most recoverable)
        return [
            ("network", self.patterns["network"]),
            ("timeout", self.patterns["timeout"]),
            ("resource", self.patterns["resource"]),
            ("dependency", self.patterns["dependency"]),
            ("flaky", self.patterns["flaky"]),
            ("workflow", self.patterns["workflow"]),
            ("security", self.patterns["security"]),
            ("logic", self.patterns["logic"]),
        ]

    def _build_signature(
        self, category: str, pattern: str, description: str, attempt_number: int
    ) -> ErrorSignature:
        """Build error signature based on category."""

        if category == "network":
            return ErrorSignature(
                pattern_id=f"net-{pattern[:20]}",
                category=ErrorCategory.NETWORK_TRANSIENT,
                severity=RecoverySeverity.AUTO_RECOVERABLE,
                message=description,
                confidence=0.95,
                suggestions=[
                    "Retry immediately",
                    "Check network connectivity",
                    "Verify GitHub API availability",
                ],
                metadata={"max_retries": 3, "initial_delay_sec": 5},
            )

        elif category == "timeout":
            suggestions = ["Increase timeout threshold", "Optimize slow operations"]
            if attempt_number > 1:
                suggestions.insert(0, "Skip slow tests with -m 'not slow'")
            return ErrorSignature(
                pattern_id=f"timeout-{pattern[:20]}",
                category=ErrorCategory.TIMEOUT_EXCEEDED,
                severity=RecoverySeverity.BACKOFF_RECOVERABLE,
                message=description,
                confidence=0.90,
                suggestions=suggestions,
                metadata={"max_retries": 2, "base_delay_sec": 10},
            )

        elif category == "resource":
            return ErrorSignature(
                pattern_id=f"resource-{pattern[:20]}",
                category=ErrorCategory.RESOURCE_EXHAUSTION,
                severity=RecoverySeverity.BACKOFF_RECOVERABLE,
                message=description,
                confidence=0.85,
                suggestions=[
                    "Retry with exponential backoff",
                    "Check runner resource limits",
                    "Parallel test execution may be over-subscribed",
                ],
                metadata={"max_retries": 3, "base_delay_sec": 20},
            )

        elif category == "dependency":
            return ErrorSignature(
                pattern_id=f"depend-{pattern[:20]}",
                category=ErrorCategory.DEPENDENCY_CONFLICT,
                severity=RecoverySeverity.BACKOFF_RECOVERABLE,
                message=description,
                confidence=0.80,
                suggestions=[
                    "Refresh dependency cache",
                    "Retry pip install",
                    "Check dependency versions in pyproject.toml",
                ],
                metadata={"max_retries": 2, "base_delay_sec": 15},
            )

        elif category == "flaky":
            return ErrorSignature(
                pattern_id=f"flaky-{pattern[:20]}",
                category=ErrorCategory.FLAKY_TEST,
                severity=RecoverySeverity.BACKOFF_RECOVERABLE,
                message=description,
                confidence=0.75,
                suggestions=[
                    "Retry test in isolation",
                    "Check for timing dependencies",
                    "Mark test with @pytest.mark.flaky",
                ],
                metadata={"max_retries": 2, "base_delay_sec": 10},
            )

        elif category == "workflow":
            return ErrorSignature(
                pattern_id=f"workflow-{pattern[:20]}",
                category=ErrorCategory.WORKFLOW_SYNTAX,
                severity=RecoverySeverity.ESCALATE_REQUIRED,
                message=description,
                confidence=0.95,
                suggestions=[
                    "Fix workflow YAML syntax",
                    "Validate with yamllint",
                    "Review GitHub Actions documentation",
                ],
            )

        elif category == "security":
            return ErrorSignature(
                pattern_id=f"security-{pattern[:20]}",
                category=ErrorCategory.SECURITY_POLICY,
                severity=RecoverySeverity.ESCALATE_REQUIRED,
                message=description,
                confidence=0.95,
                suggestions=[
                    "Review security policies",
                    "Check permissions and credentials",
                    "Escalate to security team",
                ],
            )

        else:  # logic errors
            return ErrorSignature(
                pattern_id=f"logic-{pattern[:20]}",
                category=ErrorCategory.LOGIC_ERROR,
                severity=RecoverySeverity.ESCALATE_REQUIRED,
                message=description,
                confidence=0.85,
                suggestions=[
                    "Review code for logic errors",
                    "Add debug logging",
                    "Run test locally to reproduce",
                ],
            )

    def batch_classify(self, errors: List[str]) -> List[ErrorSignature]:
        """Classify multiple errors at once."""
        return [self.classify(error) for error in errors if error.strip()]

    @staticmethod
    def severity_to_recovery_action(severity: RecoverySeverity) -> Dict[str, any]:
        """Map severity level to recovery action configuration."""
        actions = {
            RecoverySeverity.AUTO_RECOVERABLE: {
                "max_retries": 3,
                "base_delay_sec": 5,
                "backoff_multiplier": 1.5,
                "action": "retry_immediately",
            },
            RecoverySeverity.BACKOFF_RECOVERABLE: {
                "max_retries": 3,
                "base_delay_sec": 10,
                "backoff_multiplier": 2.0,
                "action": "retry_with_backoff",
            },
            RecoverySeverity.ESCALATE_REQUIRED: {
                "max_retries": 1,
                "base_delay_sec": 0,
                "backoff_multiplier": 1.0,
                "action": "escalate_to_human",
            },
            RecoverySeverity.CRITICAL: {
                "max_retries": 0,
                "base_delay_sec": 0,
                "backoff_multiplier": 1.0,
                "action": "immediate_escalation",
            },
        }
        return actions.get(severity, actions[RecoverySeverity.ESCALATE_REQUIRED])


class RecoveryMetrics:
    """Track recovery attempt metrics for MTTR calculation."""

    def __init__(self):
        self.attempts = []
        self.start_time = datetime.utcnow()

    def record_attempt(
        self,
        pattern_id: str,
        severity: RecoverySeverity,
        success: bool,
        delay_sec: float = 0,
    ):
        """Record a recovery attempt."""
        self.attempts.append(
            {
                "pattern_id": pattern_id,
                "severity": severity.value,
                "success": success,
                "delay_sec": delay_sec,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def calculate_mttr_seconds(self) -> float:
        """Calculate mean time to recovery in seconds."""
        if not self.attempts:
            return 0.0

        # Sum total time including delays
        total_time = sum(a["delay_sec"] for a in self.attempts)
        return total_time / len(self.attempts) if self.attempts else 0.0

    def get_success_rate(self) -> float:
        """Get success rate as percentage (0-100)."""
        if not self.attempts:
            return 0.0
        successes = sum(1 for a in self.attempts if a["success"])
        return (successes / len(self.attempts)) * 100

    def to_dict(self) -> Dict:
        """Export metrics as dict."""
        return {
            "total_attempts": len(self.attempts),
            "success_count": sum(1 for a in self.attempts if a["success"]),
            "failure_count": sum(1 for a in self.attempts if not a["success"]),
            "success_rate_pct": self.get_success_rate(),
            "mttr_seconds": self.calculate_mttr_seconds(),
            "duration_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "attempts": self.attempts,
        }

    def to_json(self) -> str:
        """Export metrics as JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


if __name__ == "__main__":
    # Example usage
    classifier = ErrorClassifier()

    # Test network error
    net_error = "Error: Connection refused - Failed to connect to api.github.com:443"
    sig = classifier.classify(net_error)
    print(f"\n=== Network Error ===")
    print(f"Classification: {sig.category.value}")
    print(f"Severity: {sig.severity.value}")
    print(f"Suggestions: {sig.suggestions}")

    # Test timeout error
    timeout_error = "SIGTERM signal: terminated"
    sig = classifier.classify(timeout_error, attempt_number=2)
    print(f"\n=== Timeout Error ===")
    print(f"Classification: {sig.category.value}")
    print(f"Severity: {sig.severity.value}")
    print(f"Suggestions: {sig.suggestions}")

    # Test resource error
    resource_error = "MemoryError: Unable to allocate 2.00 GiB for an array"
    sig = classifier.classify(resource_error)
    print(f"\n=== Resource Error ===")
    print(f"Classification: {sig.category.value}")
    print(f"Severity: {sig.severity.value}")

    # Get recovery action
    action = ErrorClassifier.severity_to_recovery_action(sig.severity)
    print(f"Recovery Action: {action['action']}")
    print(f"Max Retries: {action['max_retries']}")

    # Track metrics
    metrics = RecoveryMetrics()
    metrics.record_attempt("net-conn-refused", RecoverySeverity.AUTO_RECOVERABLE, True, 5)
    metrics.record_attempt("net-conn-refused", RecoverySeverity.AUTO_RECOVERABLE, True, 5)
    print(f"\n=== Metrics ===")
    print(f"Success Rate: {metrics.get_success_rate():.1f}%")
    print(f"MTTR: {metrics.calculate_mttr_seconds():.1f}s")
