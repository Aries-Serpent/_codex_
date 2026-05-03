"""
Infrastructure Linter Agent - DECIDE Phase (validator.py)

Purpose: Assess risk, check policies, and make recommendations based on IaC scan results.

This module analyzes scan findings from scanner.py and determines:
1. Overall security score (0-100)
2. Risk level (low/medium/high/critical)
3. Policy violations and blockers
4. Recommendation (APPROVE/WARN/BLOCK)

Part of the Cognitive Brain Phase 6 agent ecosystem.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

# Cognitive brain integration
try:
    from ..core.cognitive_brain import CognitiveBrain
except ImportError:
    # Fallback for standalone usage
    class CognitiveBrain:
        def __init__(self, db_path: Optional[str] = None):
            self.db_path = db_path

        def query_patterns(self, pattern_type: str, metadata: dict[str, Any]) -> list[dict[str, Any]]:
            return []

# #AFTERMATH_PATTERN_IDENTIFIED: iac_validation_decisions
# #AFTERMATH_METRIC: validations_performed

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of IaC validation and risk assessment"""
    risk_level: str  # low/medium/high/critical
    security_score: int  # 0-100 (higher is better)
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    blockers: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    recommendation: str  # APPROVE/WARN/BLOCK
    confidence: float  # 0.0-1.0
    reasoning: str


class IaCValidator:
    """
    DECIDE phase: Assess risk and make recommendations for IaC changes.

    Responsibilities:
    - Calculate security scores
    - Identify policy violations
    - Determine risk levels
    - Make deployment recommendations
    - Query cognitive brain for historical patterns
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize IaC validator.

        Args:
            db_path: Path to cognitive brain SQLite database (default: CODEX_DB_PATH env var)
        """
        if db_path is None:
            db_path = os.getenv("CODEX_DB_PATH", ".codex/cognitive_brain.db")

        self.brain = CognitiveBrain(db_path)
        logger.info(f"IaCValidator initialized with db_path={db_path}")

    def validate(
        self,
        scan_results: dict[str, Any],
        policy_config: Optional[dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Assess risk and make recommendation based on scan results.

        Args:
            scan_results: Output from scanner.py containing findings
            policy_config: Organization security policies (optional)

        Returns:
            ValidationResult with risk assessment and recommendation
        """
        if policy_config is None:
            policy_config = self._get_default_policy()

        # Extract findings from scan results
        all_findings = []
        for scan_result in scan_results.get("scan_results", []):
            all_findings.extend(scan_result.get("findings", []))

        # Count severity levels
        severity_counts = self._count_severities(all_findings)

        # Calculate security score
        score = self._calculate_security_score(severity_counts, len(all_findings))

        # Identify blockers and warnings
        blockers = self._identify_blockers(all_findings, policy_config)
        warnings = self._identify_warnings(all_findings, policy_config)

        # Assess risk level
        risk = self._assess_risk_level(score, severity_counts, blockers)

        # Query cognitive brain for similar patterns
        self._query_historical_patterns(scan_results)

        # Make recommendation
        recommendation = self._make_recommendation(risk, blockers, policy_config)
        confidence = self._calculate_confidence(all_findings, blockers, warnings)
        reasoning = self._generate_reasoning(risk, blockers, warnings, score)

        result = ValidationResult(
            risk_level=risk,
            security_score=score,
            critical_issues=severity_counts.get("CRITICAL", 0),
            high_issues=severity_counts.get("HIGH", 0),
            medium_issues=severity_counts.get("MEDIUM", 0),
            low_issues=severity_counts.get("LOW", 0),
            blockers=blockers,
            warnings=warnings,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning
        )

        logger.info(f"Validation complete: {recommendation} (score={score}, risk={risk})")
        return result

    def _get_default_policy(self) -> dict[str, Any]:
        """Return default organizational security policy"""
        return {
            "block_on_critical": True,
            "block_on_high": True,
            "block_on_medium": False,
            "require_encryption": True,
            "require_resource_limits": True,
            "require_rbac": False,
            "min_security_score": 50
        }

    def _count_severities(self, findings: list[dict[str, Any]]) -> dict[str, int]:
        """Count findings by severity level"""
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for finding in findings:
            severity = finding.get("severity", "LOW").upper()
            if severity in counts:
                counts[severity] += 1
        return counts

    def _calculate_security_score(
        self,
        severity_counts: dict[str, int],
        total_findings: int
    ) -> int:
        """
        Calculate security score (0-100, higher is better).

        Scoring:
        - Start at 100
        - Critical: -25 points each
        - High: -10 points each
        - Medium: -3 points each
        - Low: -1 point each
        - Floor: 0 (cannot go negative)
        """
        score = 100
        score -= severity_counts.get("CRITICAL", 0) * 25
        score -= severity_counts.get("HIGH", 0) * 10
        score -= severity_counts.get("MEDIUM", 0) * 3
        score -= severity_counts.get("LOW", 0) * 1

        # Floor at 0
        score = max(0, score)

        logger.debug(f"Security score: {score}/100 ({total_findings} findings)")
        return score

    def _identify_blockers(
        self,
        findings: list[dict[str, Any]],
        policy: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Identify findings that should block deployment.

        Blockers are determined by:
        1. Policy configuration (block_on_critical, block_on_high, etc.)
        2. Specific policy requirements (encryption, RBAC, etc.)
        """
        blockers = []

        for finding in findings:
            severity = finding.get("severity", "LOW").upper()
            rule_id = finding.get("rule_id", "")

            # Check severity-based blocking
            is_blocker = False
            if severity == "CRITICAL" and policy.get("block_on_critical", True):
                is_blocker = True
            elif severity == "HIGH" and policy.get("block_on_high", True):
                is_blocker = True
            elif severity == "MEDIUM" and policy.get("block_on_medium", False):
                is_blocker = True

            # Check policy-specific rules
            if policy.get("require_encryption", True):
                if "encryption" in rule_id.lower() or "unencrypted" in rule_id.lower():
                    is_blocker = True

            if policy.get("require_resource_limits", True):
                if "resource" in rule_id.lower() and "limit" in rule_id.lower():
                    is_blocker = True

            if policy.get("require_rbac", False):
                if "rbac" in rule_id.lower() or "privilege" in rule_id.lower():
                    is_blocker = True

            if is_blocker:
                blockers.append({
                    "file": finding.get("file_path", "unknown"),
                    "rule": rule_id,
                    "severity": severity,
                    "line": finding.get("line", 0),
                    "message": finding.get("message", ""),
                    "reason": f"{severity} severity issue violates organizational policy"
                })

        logger.info(f"Identified {len(blockers)} blockers")
        return blockers

    def _identify_warnings(
        self,
        findings: list[dict[str, Any]],
        policy: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Identify findings that should generate warnings (non-blocking).

        Warnings are findings that don't meet blocker criteria but should
        still be surfaced to developers.
        """
        warnings = []

        for finding in findings:
            severity = finding.get("severity", "LOW").upper()
            rule_id = finding.get("rule_id", "")

            # Non-critical/high findings become warnings
            if severity in ["MEDIUM", "LOW"]:
                warnings.append({
                    "file": finding.get("file_path", "unknown"),
                    "rule": rule_id,
                    "severity": severity,
                    "line": finding.get("line", 0),
                    "message": finding.get("message", ""),
                    "suggested_fix": finding.get("suggested_fix", "")
                })

        logger.info(f"Identified {len(warnings)} warnings")
        return warnings

    def _assess_risk_level(
        self,
        score: int,
        severity_counts: dict[str, int],
        blockers: list[dict[str, Any]]
    ) -> str:
        """
        Determine overall risk level: low/medium/high/critical.

        Risk assessment logic:
        - Critical: Any critical severity findings OR score < 25
        - High: Any high severity findings OR score < 50
        - Medium: Score 50-75
        - Low: Score > 75
        """
        if severity_counts.get("CRITICAL", 0) > 0 or score < 25:
            return "critical"
        if severity_counts.get("HIGH", 0) > 0 or score < 50:
            return "high"
        if score < 75:
            return "medium"
        return "low"

    def _query_historical_patterns(self, scan_results: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Query cognitive brain for historical IaC vulnerability patterns.

        This helps adjust risk assessment based on:
        - Previously seen vulnerabilities in similar tools
        - Common misconfiguration patterns
        - Effectiveness of policy enforcement
        """
        tools_detected = scan_results.get("tools_detected", [])

        try:
            patterns = self.brain.query_patterns(
                pattern_type="iac_vulnerability",
                metadata={"tools": tools_detected}
            )

            if patterns:
                logger.info(f"Found {len(patterns)} historical IaC patterns for tools: {tools_detected}")

            return patterns

        except Exception as e:
            # Best-effort: if cognitive brain unavailable, continue without patterns
            logger.warning(f"Could not query historical patterns: {e}")
            return []

    def _make_recommendation(
        self,
        risk: str,
        blockers: list[dict[str, Any]],
        policy: dict[str, Any]
    ) -> str:
        """
        Make deployment recommendation: APPROVE/WARN/BLOCK.

        Logic:
        - BLOCK: If blockers exist or risk is critical/high
        - WARN: If risk is medium with warnings
        - APPROVE: If risk is low
        """
        if len(blockers) > 0:
            return "BLOCK"

        if risk in ["critical", "high"]:
            return "BLOCK"
        if risk == "medium":
            return "WARN"
        return "APPROVE"

    def _calculate_confidence(
        self,
        findings: list[dict[str, Any]],
        blockers: list[dict[str, Any]],
        warnings: list[dict[str, Any]]
    ) -> float:
        """
        Calculate confidence in the recommendation (0.0-1.0).

        Confidence is higher when:
        - Clear severity classifications
        - Specific rule IDs
        - Detailed messages
        - Actionable suggested fixes
        """
        if len(findings) == 0:
            return 1.0  # High confidence when no issues found

        # Check completeness of findings
        complete_findings = 0
        for finding in findings:
            if all(key in finding for key in ["severity", "rule_id", "message"]):
                complete_findings += 1

        completeness_ratio = complete_findings / len(findings) if findings else 0

        # Higher confidence with clear blockers
        if len(blockers) > 0:
            confidence = 0.85 + (completeness_ratio * 0.15)
        else:
            confidence = 0.70 + (completeness_ratio * 0.30)

        return min(1.0, confidence)

    def _generate_reasoning(
        self,
        risk: str,
        blockers: list[dict[str, Any]],
        warnings: list[dict[str, Any]],
        score: int
    ) -> str:
        """Generate human-readable reasoning for the recommendation"""
        parts = []

        if len(blockers) > 0:
            parts.append(f"{len(blockers)} critical/high-severity issues violate organizational policy")

        if len(warnings) > 0:
            parts.append(f"{len(warnings)} medium/low-severity warnings")

        parts.append(f"Security score: {score}/100")
        parts.append(f"Risk level: {risk}")

        return "; ".join(parts)
