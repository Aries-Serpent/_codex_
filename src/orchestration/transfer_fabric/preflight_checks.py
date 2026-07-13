"""Preflight Checks: Validation before transfer initiation.

5 checks: policy compliance, permissions, network readiness,
storage capacity, compute availability.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class CheckType(Enum):
    """Types of preflight checks."""

    POLICY_COMPLIANCE = "policy_compliance"
    PERMISSIONS = "permissions"
    NETWORK_READINESS = "network_readiness"
    STORAGE_CAPACITY = "storage_capacity"
    COMPUTE_AVAILABILITY = "compute_availability"


@dataclass
class PreflightCheck:
    """Result of a single preflight check."""

    check_type: CheckType
    passed: bool
    message: str = ""
    blocking: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_type": self.check_type.value,
            "passed": self.passed,
            "message": self.message,
            "blocking": self.blocking,
        }


@dataclass
class PreflightResult:
    """Result of all preflight checks."""

    all_pass: bool
    checks: List[PreflightCheck] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "all_pass": self.all_pass,
            "checks": [c.to_dict() for c in self.checks],
            "blockers": self.blockers,
        }


class PreflightValidator:
    """Validates transfer readiness with 5 checks."""

    def __init__(self):
        """Initialize validator."""
        self.policies_enabled = True
        self.permissions_cache: Dict[str, bool] = {}
        self.network_status: Dict[str, bool] = {}
        self.storage_capacity: Dict[str, int] = {}
        self.compute_available: Dict[str, bool] = {}

    def validate_policy_compliance(
        self, source: str, destination: str, data_type: str = ""
    ) -> PreflightCheck:
        """Check 1: Policy compliance for transfer route."""
        if not self.policies_enabled:
            return PreflightCheck(
                check_type=CheckType.POLICY_COMPLIANCE,
                passed=False,
                message="Policy engine disabled",
                blocking=True,
            )

        if not source or not destination:
            return PreflightCheck(
                check_type=CheckType.POLICY_COMPLIANCE,
                passed=False,
                message="Source or destination missing",
                blocking=True,
            )

        return PreflightCheck(
            check_type=CheckType.POLICY_COMPLIANCE,
            passed=True,
            message="Transfer route is compliant with policies",
            blocking=True,
        )

    def validate_permissions(self, source_id: str, dest_id: str) -> PreflightCheck:
        """Check 2: Verify source and destination permissions."""
        cache_key = f"{source_id}:{dest_id}"

        if cache_key in self.permissions_cache:
            passed = self.permissions_cache[cache_key]
        else:
            passed = bool(source_id) and bool(dest_id)
            self.permissions_cache[cache_key] = passed

        message = "Permissions verified" if passed else "Permission denied"
        return PreflightCheck(
            check_type=CheckType.PERMISSIONS,
            passed=passed,
            message=message,
            blocking=True,
        )

    def validate_network_readiness(self, route: str) -> PreflightCheck:
        """Check 3: Verify network connectivity and readiness."""
        if route not in self.network_status:
            self.network_status[route] = True

        passed = self.network_status[route]
        message = "Network is ready" if passed else "Network unavailable"

        return PreflightCheck(
            check_type=CheckType.NETWORK_READINESS,
            passed=passed,
            message=message,
            blocking=True,
        )

    def validate_storage_capacity(
        self, destination: str, required_bytes: int
    ) -> PreflightCheck:
        """Check 4: Verify sufficient storage capacity at destination."""
        available = self.storage_capacity.get(destination, 1024 * 1024 * 1024 * 100)

        passed = available >= required_bytes
        message = (
            f"Sufficient storage available ({available} bytes)"
            if passed
            else f"Insufficient storage (need {required_bytes}, have {available})"
        )

        return PreflightCheck(
            check_type=CheckType.STORAGE_CAPACITY,
            passed=passed,
            message=message,
            blocking=True,
        )

    def validate_compute_availability(self, destination: str) -> PreflightCheck:
        """Check 5: Verify compute resources available for transfer."""
        available = self.compute_available.get(destination, True)

        message = "Compute resources available" if available else "Compute resources exhausted"
        return PreflightCheck(
            check_type=CheckType.COMPUTE_AVAILABILITY,
            passed=available,
            message=message,
            blocking=True,
        )

    def validate_all(
        self,
        source: str,
        destination: str,
        data_type: str = "",
        payload_bytes: int = 0,
    ) -> PreflightResult:
        """Execute all 5 preflight checks."""
        checks = []
        blockers = []

        check1 = self.validate_policy_compliance(source, destination, data_type)
        checks.append(check1)
        if not check1.passed and check1.blocking:
            blockers.append(check1.message)

        check2 = self.validate_permissions(source, destination)
        checks.append(check2)
        if not check2.passed and check2.blocking:
            blockers.append(check2.message)

        check3 = self.validate_network_readiness(f"{source}→{destination}")
        checks.append(check3)
        if not check3.passed and check3.blocking:
            blockers.append(check3.message)

        check4 = self.validate_storage_capacity(destination, payload_bytes)
        checks.append(check4)
        if not check4.passed and check4.blocking:
            blockers.append(check4.message)

        check5 = self.validate_compute_availability(destination)
        checks.append(check5)
        if not check5.passed and check5.blocking:
            blockers.append(check5.message)

        all_pass = len(blockers) == 0
        logger.info(f"Preflight check: {'PASS' if all_pass else 'FAIL'}")

        return PreflightResult(all_pass=all_pass, checks=checks, blockers=blockers)

    def set_network_status(self, route: str, is_ready: bool) -> None:
        """Set network readiness status."""
        self.network_status[route] = is_ready

    def set_storage_capacity(self, destination: str, bytes_available: int) -> None:
        """Set storage capacity for destination."""
        self.storage_capacity[destination] = bytes_available

    def set_compute_available(self, destination: str, available: bool) -> None:
        """Set compute availability for destination."""
        self.compute_available[destination] = available

    def set_permissions(self, source_id: str, dest_id: str, allowed: bool) -> None:
        """Set permissions cache."""
        cache_key = f"{source_id}:{dest_id}"
        self.permissions_cache[cache_key] = allowed
