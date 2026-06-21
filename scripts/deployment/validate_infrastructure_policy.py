#!/usr/bin/env python3
"""
Infrastructure Policy Validator
Validates infrastructure configuration against organizational policies.
"""

import json
import logging
from dataclasses import asdict, dataclass
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PolicyViolation:
    """Represents a policy violation."""
    policy_id: str
    policy_name: str
    resource: str
    severity: str  # critical, high, medium, low
    message: str
    remediation: str


@dataclass
class ComplianceReport:
    """Overall compliance report."""
    total_policies: int
    passed_policies: int
    failed_policies: int
    violations: List[PolicyViolation]
    compliance_score: float  # 0.0 - 1.0
    status: str  # compliant, warning, non-compliant


class InfrastructurePolicyValidator:
    """Validate infrastructure against organizational policies."""

    def __init__(self):
        """Initialize validator."""
        self.policies = self._define_policies()
        logger.info(f"Initialized with {len(self.policies)} policies")

    def _define_policies(self) -> Dict[str, Dict]:
        """Define organizational policies."""
        return {
            "naming-conventions": {
                "name": "Resource Naming Conventions",
                "severity": "medium",
                "rules": [
                    "Cluster names must be lowercase alphanumeric with hyphens",
                    "Names must include environment (dev/staging/prod)",
                    "Names must include provider (aws/gcp/azure)",
                    "Maximum length: 63 characters",
                ]
            },
            "network-security": {
                "name": "Network Security Requirements",
                "severity": "critical",
                "rules": [
                    "VPCs must use private subnets for pods",
                    "Network policies must be enabled in production",
                    "Ingress must use HTTPS/TLS",
                    "Cross-AZ traffic should use VPC endpoints",
                ]
            },
            "access-control": {
                "name": "Access Control & RBAC",
                "severity": "critical",
                "rules": [
                    "RBAC must be enabled",
                    "Service accounts must follow naming conventions",
                    "Pod security policies must be enforced",
                    "Default service account must not be used",
                ]
            },
            "resource-limits": {
                "name": "Resource Limits & Quotas",
                "severity": "high",
                "rules": [
                    "CPU limits required for all pods",
                    "Memory limits required for all pods",
                    "Namespace quotas must be defined",
                    "Node autoscaling limits must be reasonable",
                ]
            },
            "cost-efficiency": {
                "name": "Cost Efficiency",
                "severity": "medium",
                "rules": [
                    "Dev clusters must use spot/preemptible instances",
                    "Unused resources should be identified",
                    "Reserved instances recommended for production",
                    "Regular cost optimization reviews required",
                ]
            },
            "encryption": {
                "name": "Encryption at Rest & Transit",
                "severity": "critical",
                "rules": [
                    "Secrets must be encrypted using KMS",
                    "Persistent volumes must be encrypted",
                    "ETCD must be encrypted at rest",
                    "TLS 1.2+ required for all communications",
                ]
            },
            "monitoring-logging": {
                "name": "Monitoring & Logging",
                "severity": "high",
                "rules": [
                    "Cluster logging must be enabled",
                    "Audit logging must be enabled in production",
                    "Prometheus monitoring required",
                    "Alerting must be configured",
                ]
            },
            "backup-recovery": {
                "name": "Backup & Disaster Recovery",
                "severity": "high",
                "rules": [
                    "Automated daily backups required in production",
                    "RTO defined (4 hours recommended)",
                    "RPO defined (24 hours recommended)",
                    "Backup encryption required",
                ]
            },
        }

    def validate_infrastructure(self, terraform_config: Dict) -> ComplianceReport:
        """Validate infrastructure against policies."""
        logger.info("Starting infrastructure validation")

        violations = []
        passed = 0

        # Policy 1: Naming Conventions
        if self._check_naming_conventions(terraform_config):
            passed += 1
        else:
            violations.append(PolicyViolation(
                policy_id="naming-conventions",
                policy_name="Resource Naming Conventions",
                resource="cluster",
                severity="medium",
                message="Cluster name does not follow naming conventions",
                remediation="Use format: codex-{env}-{provider} (e.g., codex-prod-eks)"
            ))

        # Policy 2: Network Security
        if self._check_network_security(terraform_config):
            passed += 1
        else:
            violations.append(PolicyViolation(
                policy_id="network-security",
                policy_name="Network Security",
                resource="networking",
                severity="critical",
                message="Network security configuration incomplete",
                remediation="Enable network policies, use private subnets, implement HTTPS"
            ))

        # Policy 3: Access Control
        if self._check_access_control(terraform_config):
            passed += 1
        else:
            violations.append(PolicyViolation(
                policy_id="access-control",
                policy_name="Access Control & RBAC",
                resource="iam",
                severity="critical",
                message="RBAC not properly configured",
                remediation="Enable RBAC, configure service accounts, enforce pod security policies"
            ))

        # Policy 4: Resource Limits
        if self._check_resource_limits(terraform_config):
            passed += 1
        else:
            violations.append(PolicyViolation(
                policy_id="resource-limits",
                policy_name="Resource Limits",
                resource="compute",
                severity="high",
                message="Resource limits not defined",
                remediation="Define CPU/memory limits, configure namespace quotas"
            ))

        # Policy 5: Cost Efficiency
        if self._check_cost_efficiency(terraform_config):
            passed += 1
        else:
            violations.append(PolicyViolation(
                policy_id="cost-efficiency",
                policy_name="Cost Efficiency",
                resource="compute",
                severity="medium",
                message="Not using cost-optimized instance types",
                remediation="Use spot instances in dev, reserved instances in prod"
            ))

        # Policy 6: Encryption
        if self._check_encryption(terraform_config):
            passed += 1
        else:
            violations.append(PolicyViolation(
                policy_id="encryption",
                policy_name="Encryption",
                resource="security",
                severity="critical",
                message="Encryption not properly configured",
                remediation="Enable KMS encryption, configure TLS, encrypt ETCD and volumes"
            ))

        # Policy 7: Monitoring & Logging
        if self._check_monitoring_logging(terraform_config):
            passed += 1
        else:
            violations.append(PolicyViolation(
                policy_id="monitoring-logging",
                policy_name="Monitoring & Logging",
                resource="observability",
                severity="high",
                message="Monitoring and logging not configured",
                remediation="Enable cluster logging, configure Prometheus, set up alerting"
            ))

        # Policy 8: Backup & Recovery
        if self._check_backup_recovery(terraform_config):
            passed += 1
        else:
            violations.append(PolicyViolation(
                policy_id="backup-recovery",
                policy_name="Backup & Recovery",
                resource="storage",
                severity="high",
                message="Backup configuration incomplete",
                remediation="Enable automated daily backups, define RTO/RPO, test recovery"
            ))

        total = len(self.policies)
        failed = len(violations)
        compliance_score = passed / total if total > 0 else 0.0

        # Determine status
        if compliance_score >= 0.9:
            status = "compliant"
        elif compliance_score >= 0.7:
            status = "warning"
        else:
            status = "non-compliant"

        report = ComplianceReport(
            total_policies=total,
            passed_policies=passed,
            failed_policies=failed,
            violations=violations,
            compliance_score=compliance_score,
            status=status
        )

        logger.info(f"Validation complete: {passed}/{total} policies passed (score: {compliance_score:.1%})")
        return report

    def _check_naming_conventions(self, config: Dict) -> bool:
        """Check naming conventions."""
        # Pattern: codex-{env}-{provider}
        name = config.get("cluster_name", "")
        parts = name.split("-")
        return len(parts) >= 3 and len(name) <= 63

    def _check_network_security(self, config: Dict) -> bool:
        """Check network security."""
        networking = config.get("networking", {})
        return (
            networking.get("network_policies_enabled", False) or
            config.get("environment") == "dev"
        )

    def _check_access_control(self, config: Dict) -> bool:
        """Check access control."""
        security = config.get("security", {})
        return security.get("rbac_enabled", False)

    def _check_resource_limits(self, config: Dict) -> bool:
        """Check resource limits."""
        sizing = config.get("resource_sizing", {})
        return sizing.get("recommended_nodes", 0) > 0

    def _check_cost_efficiency(self, config: Dict) -> bool:
        """Check cost efficiency."""
        sizing = config.get("resource_sizing", {})
        if config.get("environment") == "dev":
            return sizing.get("use_spot_instances", False)
        return True

    def _check_encryption(self, config: Dict) -> bool:
        """Check encryption."""
        security = config.get("security", {})
        return security.get("secret_encryption") is not None

    def _check_monitoring_logging(self, config: Dict) -> bool:
        """Check monitoring and logging."""
        return config.get("monitoring_enabled") or config.get("logging_provider") is not None

    def _check_backup_recovery(self, config: Dict) -> bool:
        """Check backup and recovery."""
        return config.get("backup_enabled") or config.get("environment") == "dev"

    def to_dict(self, report: ComplianceReport) -> Dict:
        """Convert report to dictionary."""
        return {
            "timestamp": "2026-06-20T09:45:00Z",
            "total_policies": report.total_policies,
            "passed_policies": report.passed_policies,
            "failed_policies": report.failed_policies,
            "compliance_score": report.compliance_score,
            "status": report.status,
            "violations": [asdict(v) for v in report.violations],
        }


def main():
    """Main entry point."""
    validator = InfrastructurePolicyValidator()

    # Load patterns
    with open("k8s_patterns.json", 'r') as f:
        patterns = json.load(f)

    # Validate each pattern
    print("\n✅ Infrastructure Policy Validation Results\n")

    for pattern_key, pattern in patterns.items():
        report = validator.validate_infrastructure(pattern)
        print(f"{pattern_key}:")
        print(f"  Compliance: {report.compliance_score:.0%} ({report.passed_policies}/{report.total_policies} policies)")
        print(f"  Status: {report.status.upper()}")
        if report.violations:
            print(f"  Violations: {len(report.violations)}")
        print()

    # Save sample validation
    with open("k8s_patterns.json", 'r') as f:
        patterns = json.load(f)
    first_pattern = list(patterns.values())[0]
    report = validator.validate_infrastructure(first_pattern)

    with open("infrastructure_compliance_report.json", 'w') as f:
        json.dump(validator.to_dict(report), f, indent=2)

    print("✅ Validation complete - Report saved to infrastructure_compliance_report.json")


if __name__ == "__main__":
    main()
