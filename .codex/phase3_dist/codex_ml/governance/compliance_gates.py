"""Regulatory compliance gates for ML deployments.

Provides automated compliance checking for:
- GDPR (General Data Protection Regulation)
- HIPAA (Health Insurance Portability and Accountability Act)
- SOC2 (Service Organization Control 2)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["ComplianceGate", "ComplianceReport", "ComplianceViolation"]


@dataclass
class ComplianceViolation:
    """Represents a compliance violation."""

    policy: str
    requirement: str
    severity: str  # low, medium, high, critical
    description: str
    remediation: str


@dataclass
class ComplianceReport:
    """Compliance validation report."""

    policy: str
    is_compliant: bool
    violations: list[ComplianceViolation]
    checks_passed: int
    checks_total: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy": self.policy,
            "is_compliant": self.is_compliant,
            "violations": [
                {
                    "requirement": v.requirement,
                    "severity": v.severity,
                    "description": v.description,
                    "remediation": v.remediation,
                }
                for v in self.violations
            ],
            "checks_passed": self.checks_passed,
            "checks_total": self.checks_total,
        }


class ComplianceGate:
    """Compliance gate for deployment validation.

    Example:
        >>> gate = ComplianceGate("GDPR")
        >>> report = gate.validate(model, data, deployment)
        >>> if not report.is_compliant:
        ...     raise ValueError(f"Compliance violations: {report.violations}")
    """

    SUPPORTED_POLICIES = ["GDPR", "HIPAA", "SOC2"]

    def __init__(self, policy: str):
        """Initialize compliance gate.

        Args:
            policy: Policy name (GDPR, HIPAA, SOC2)
        """
        if policy not in self.SUPPORTED_POLICIES:
            raise ValueError(f"Unsupported policy: {policy}. Supported: {self.SUPPORTED_POLICIES}")

        self.policy = policy
        logger.info(f"ComplianceGate initialized for {policy}")

    def validate(
        self,
        model: Any,
        data: Any,
        deployment: Any,
    ) -> ComplianceReport:
        """Validate compliance.

        Args:
            model: Model to validate
            data: Training/inference data
            deployment: Deployment configuration

        Returns:
            ComplianceReport with validation results
        """
        if self.policy == "GDPR":
            return self._validate_gdpr(model, data, deployment)
        if self.policy == "HIPAA":
            return self._validate_hipaa(model, data, deployment)
        if self.policy == "SOC2":
            return self._validate_soc2(model, data, deployment)
        return ComplianceReport(policy=self.policy, violations=[], checks_passed=0, checks_total=0)  # type: ignore[call-arg]

    def _validate_gdpr(self, model, data, deployment) -> ComplianceReport:
        """Validate GDPR compliance."""
        violations = []
        checks_passed = 0
        checks_total = 4

        # 1. Data minimization
        if not self._check_data_minimization(data):
            violations.append(
                ComplianceViolation(
                    policy="GDPR",
                    requirement="Data Minimization (Article 5)",
                    severity="high",
                    description="Model uses excessive personal data",
                    remediation="Remove unnecessary features from training data",
                )
            )
        else:
            checks_passed += 1

        # 2. Right to explanation
        if not self._check_explainability(model):
            violations.append(
                ComplianceViolation(
                    policy="GDPR",
                    requirement="Right to Explanation (Article 22)",
                    severity="medium",
                    description="Model decisions not explainable",
                    remediation="Add explanation capability (LIME, SHAP, etc.)",
                )
            )
        else:
            checks_passed += 1

        # 3. Purpose limitation
        if not self._check_purpose_limitation(deployment):
            violations.append(
                ComplianceViolation(
                    policy="GDPR",
                    requirement="Purpose Limitation (Article 5)",
                    severity="high",
                    description="Data used beyond stated purpose",
                    remediation="Document and enforce purpose constraints",
                )
            )
        else:
            checks_passed += 1

        # 4. Data retention
        if not self._check_data_retention(deployment):
            violations.append(
                ComplianceViolation(
                    policy="GDPR",
                    requirement="Storage Limitation (Article 5)",
                    severity="medium",
                    description="No data retention policy defined",
                    remediation="Implement automated data deletion",
                )
            )
        else:
            checks_passed += 1

        return ComplianceReport(
            policy="GDPR",
            is_compliant=len(violations) == 0,
            violations=violations,
            checks_passed=checks_passed,
            checks_total=checks_total,
        )

    def _validate_hipaa(self, model, data, deployment) -> ComplianceReport:
        """Validate HIPAA compliance."""
        violations = []
        checks_passed = 0
        checks_total = 4

        # 1. PHI protection
        if not self._check_phi_protection(data):
            violations.append(
                ComplianceViolation(
                    policy="HIPAA",
                    requirement="Privacy Rule - PHI Protection",
                    severity="critical",
                    description="Protected Health Information not properly secured",
                    remediation="Encrypt PHI, implement access controls",
                )
            )
        else:
            checks_passed += 1

        # 2. Encryption
        if not self._check_encryption(deployment):
            violations.append(
                ComplianceViolation(
                    policy="HIPAA",
                    requirement="Security Rule - Encryption",
                    severity="critical",
                    description="Data not encrypted at rest and in transit",
                    remediation="Enable TLS and disk encryption",
                )
            )
        else:
            checks_passed += 1

        # 3. Audit logs
        if not self._check_audit_logs(deployment):
            violations.append(
                ComplianceViolation(
                    policy="HIPAA",
                    requirement="Security Rule - Audit Controls",
                    severity="high",
                    description="Audit logging not comprehensive",
                    remediation="Enable detailed access logging",
                )
            )
        else:
            checks_passed += 1

        # 4. Access controls
        if not self._check_access_controls(deployment):
            violations.append(
                ComplianceViolation(
                    policy="HIPAA",
                    requirement="Security Rule - Access Control",
                    severity="high",
                    description="Insufficient access controls",
                    remediation="Implement role-based access control",
                )
            )
        else:
            checks_passed += 1

        return ComplianceReport(
            policy="HIPAA",
            is_compliant=len(violations) == 0,
            violations=violations,
            checks_passed=checks_passed,
            checks_total=checks_total,
        )

    def _validate_soc2(self, model, data, deployment) -> ComplianceReport:
        """Validate SOC2 compliance."""
        violations = []
        checks_passed = 0
        checks_total = 3

        # 1. Security controls
        if not self._check_security_controls(deployment):
            violations.append(
                ComplianceViolation(
                    policy="SOC2",
                    requirement="Security - Access Controls",
                    severity="high",
                    description="Security controls insufficient",
                    remediation="Implement MFA, encryption, monitoring",
                )
            )
        else:
            checks_passed += 1

        # 2. Availability
        if not self._check_availability(deployment):
            violations.append(
                ComplianceViolation(
                    policy="SOC2",
                    requirement="Availability - Monitoring",
                    severity="medium",
                    description="No uptime monitoring configured",
                    remediation="Add health checks and alerting",
                )
            )
        else:
            checks_passed += 1

        # 3. Processing integrity
        if not self._check_processing_integrity(model):
            violations.append(
                ComplianceViolation(
                    policy="SOC2",
                    requirement="Processing Integrity",
                    severity="medium",
                    description="No data quality validation",
                    remediation="Add input validation and testing",
                )
            )
        else:
            checks_passed += 1

        return ComplianceReport(
            policy="SOC2",
            is_compliant=len(violations) == 0,
            violations=violations,
            checks_passed=checks_passed,
            checks_total=checks_total,
        )

    # Checker methods (simplified - can be enhanced)

    def _check_data_minimization(self, data) -> bool:
        """Check if data is minimized."""
        # Placeholder: check feature count, data types
        return True

    def _check_explainability(self, model) -> bool:
        """Check if model is explainable."""
        # Placeholder: check for explainability methods
        return hasattr(model, "explain") or hasattr(model, "get_feature_importance")

    def _check_purpose_limitation(self, deployment) -> bool:
        """Check purpose limitation."""
        # Placeholder: check deployment metadata
        return hasattr(deployment, "purpose") if deployment else True

    def _check_data_retention(self, deployment) -> bool:
        """Check data retention policy."""
        # Placeholder
        return hasattr(deployment, "retention_policy") if deployment else False

    def _check_phi_protection(self, data) -> bool:
        """Check PHI protection."""
        # Placeholder: check for PHI detection/anonymization
        return True

    def _check_encryption(self, deployment) -> bool:
        """Check encryption."""
        # Placeholder: check TLS, encryption settings
        return True

    def _check_audit_logs(self, deployment) -> bool:
        """Check audit logging."""
        # Placeholder: verify logging enabled
        return True

    def _check_access_controls(self, deployment) -> bool:
        """Check access controls."""
        # Placeholder
        return True

    def _check_security_controls(self, deployment) -> bool:
        """Check security controls."""
        # Placeholder
        return True

    def _check_availability(self, deployment) -> bool:
        """Check availability monitoring."""
        # Placeholder: check health endpoints
        return hasattr(deployment, "health_check") if deployment else False

    def _check_processing_integrity(self, model) -> bool:
        """Check processing integrity."""
        # Placeholder: check validation
        return True
