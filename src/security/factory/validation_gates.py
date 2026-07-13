"""
S5: Validation Gates

Post-remediation validation gates:
1. Security Validation — CVE/CWE resolved in remediation
2. Regression Testing — existing tests still pass
3. Integration Testing — no new security issues introduced

Success metric: >99% pass rate on gates
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
from datetime import datetime


class GateStatus(str, Enum):
    """Status of a validation gate."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class GateResult:
    """Result of a single validation gate."""
    gate_name: str
    status: GateStatus
    checks_run: int = 0
    checks_passed: int = 0
    checks_failed: int = 0
    details: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def pass_rate(self) -> float:
        """Get pass rate for this gate."""
        if self.checks_run == 0:
            return 0.0
        return (self.checks_passed / self.checks_run) * 100


@dataclass
class ValidationGateReport:
    """Report for complete validation gate run."""
    finding_id: str
    gate_results: List[GateResult] = field(default_factory=list)
    all_passed: bool = True
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_result(self, result: GateResult) -> None:
        """Add a gate result."""
        self.gate_results.append(result)
        if result.status != GateStatus.PASSED:
            self.all_passed = False


class ValidationGateEngine:
    """Executes validation gates post-remediation."""

    def __init__(self):
        """Initialize engine."""
        self.security_validator: Optional[Callable] = None
        self.regression_validator: Optional[Callable] = None
        self.integration_validator: Optional[Callable] = None
        self.reports: List[ValidationGateReport] = []

    def set_security_validator(self, validator: Callable) -> None:
        """Set security validation function."""
        self.security_validator = validator

    def set_regression_validator(self, validator: Callable) -> None:
        """Set regression testing function."""
        self.regression_validator = validator

    def set_integration_validator(self, validator: Callable) -> None:
        """Set integration testing function."""
        self.integration_validator = validator

    def run_gates(self, finding_id: str, context: Dict = None) -> ValidationGateReport:
        """Run all validation gates."""
        report = ValidationGateReport(finding_id=finding_id)

        if context is None:
            context = {}

        # Gate 1: Security Validation
        if self.security_validator:
            try:
                result = self.security_validator(finding_id, context)
                report.add_result(result)
            except Exception as e:
                result = GateResult(
                    gate_name="security",
                    status=GateStatus.FAILED,
                    details=f"Exception: {str(e)}",
                )
                report.add_result(result)

        # Gate 2: Regression Testing
        if self.regression_validator:
            try:
                result = self.regression_validator(finding_id, context)
                report.add_result(result)
            except Exception as e:
                result = GateResult(
                    gate_name="regression",
                    status=GateStatus.FAILED,
                    details=f"Exception: {str(e)}",
                )
                report.add_result(result)

        # Gate 3: Integration Testing
        if self.integration_validator:
            try:
                result = self.integration_validator(finding_id, context)
                report.add_result(result)
            except Exception as e:
                result = GateResult(
                    gate_name="integration",
                    status=GateStatus.FAILED,
                    details=f"Exception: {str(e)}",
                )
                report.add_result(result)

        self.reports.append(report)
        return report

    def get_gate_summary(self) -> Dict[str, any]:
        """Get summary of all gate results."""
        if not self.reports:
            return {
                "total_reports": 0,
                "all_passed": 0,
                "with_failures": 0,
            }

        all_passed = sum(1 for r in self.reports if r.all_passed)
        with_failures = len(self.reports) - all_passed

        # Aggregate gate stats
        gate_stats = {}
        for report in self.reports:
            for result in report.gate_results:
                if result.gate_name not in gate_stats:
                    gate_stats[result.gate_name] = {
                        "passed": 0,
                        "failed": 0,
                        "warnings": 0,
                    }
                if result.status == GateStatus.PASSED:
                    gate_stats[result.gate_name]["passed"] += 1
                elif result.status == GateStatus.FAILED:
                    gate_stats[result.gate_name]["failed"] += 1
                elif result.status == GateStatus.WARNING:
                    gate_stats[result.gate_name]["warnings"] += 1

        return {
            "total_reports": len(self.reports),
            "all_passed": all_passed,
            "with_failures": with_failures,
            "pass_rate": (all_passed / len(self.reports) * 100) if self.reports else 0,
            "gate_stats": gate_stats,
        }


def run_validation_gates(
    finding_id: str,
    security_validator: Callable = None,
    regression_validator: Callable = None,
    integration_validator: Callable = None,
    context: Dict = None,
) -> ValidationGateReport:
    """Run validation gates for a finding."""
    engine = ValidationGateEngine()

    if security_validator:
        engine.set_security_validator(security_validator)
    if regression_validator:
        engine.set_regression_validator(regression_validator)
    if integration_validator:
        engine.set_integration_validator(integration_validator)

    return engine.run_gates(finding_id, context)
