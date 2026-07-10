"""
Pattern Validators Utility Module

This module provides reusable pattern validation functions that were previously
embedded in compliance_integration.py. Extracting these improves cyclomatic
complexity and promotes code reuse.

Functions:
    - check_pattern_c: Pattern C penalty logic (medium-risk cases)
    - check_pattern_h: Pattern H temporal logic (high scores)
    - check_pattern_d: Pattern D boundary cases
    - check_pattern_e: Pattern E PII monitoring
    - check_pattern_f: Pattern F multi-violation logic
    - check_pattern_b: Pattern B low score + high impact

Author: Codex Team
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AuditResult:
    """Audit result with score, risk, cost, and impact metrics."""

    score: float
    risk_level: str  # "low", "medium", "high"
    remediation_cost: float
    business_impact: float
    violation_count: int = 0
    pii_indicators: int = 0


def _is_pattern_f_monitor(audit: AuditResult) -> bool:
    """
    Check if audit matches Pattern F monitor criteria.
    Pattern F: violation_count >= 5 + impact > 0.7
    """
    return (
        hasattr(audit, "violation_count")
        and audit.violation_count >= 5
        and audit.business_impact > 0.7
    )


def _is_pii_case(audit: AuditResult) -> bool:
    """Check if audit has PII indicators."""
    return hasattr(audit, "pii_indicators") and audit.pii_indicators > 0


def _is_high_violation_count(audit: AuditResult) -> bool:
    """Check if audit has high violation count (>= 6)."""
    return hasattr(audit, "violation_count") and audit.violation_count >= 6


def check_pattern_c(audit: AuditResult) -> Optional[float]:
    """
    Pattern C penalty - BEFORE Pattern D/E/H (Strong penalty for poor outcomes).

    Ground truth: REJECT when NOT (score > 0.65 AND impact > 0.6) AND cost >= 3000
    Exempt Pattern E (PII), Pattern F (violation_count >= 6 or high-impact multi-violation)

    Args:
        audit: AuditResult object

    Returns:
        0.01 (strong penalty) if Pattern C is detected, None otherwise
    """
    if not (
        0.55 <= audit.score <= 0.75
        and audit.risk_level == "medium"
        and audit.remediation_cost > 3000
    ):
        return None

    is_monitor_case = audit.score > 0.65 and audit.business_impact > 0.6
    is_pattern_f_monitor = _is_pattern_f_monitor(audit)
    is_pii_case_check = _is_pii_case(audit)
    is_high_violation = _is_high_violation_count(audit)

    if (
        not is_monitor_case
        and not is_pattern_f_monitor
        and not is_pii_case_check
        and not is_high_violation
    ):
        return 0.01  # Strong penalty - prefer reject

    return None


def check_pattern_h_very_high_scores(audit: AuditResult) -> Optional[float]:
    """
    Pattern H temporal: Very high scores (>=0.95) always monitor.

    Args:
        audit: AuditResult object

    Returns:
        1.0 (monitor) if score >= 0.95, None otherwise
    """
    if audit.score >= 0.95:
        return 1.0
    return None


def check_pattern_d_high_risk_boundary(audit: AuditResult) -> Optional[float]:
    """
    Pattern D - High risk boundary cases should MONITOR.

    Ground truth: score >= 0.68 → MONITOR (regardless of risk!)

    Args:
        audit: AuditResult object

    Returns:
        Score preference if Pattern D matches, None otherwise
    """
    if not (0.68 <= audit.score < 0.91 and audit.risk_level == "high"):
        return None

    # Pattern E exception: PII + high risk → prefer REJECT, not monitor
    if _is_pii_case(audit):
        return 0.01  # Let reject win for PII + high risk

    return 0.99  # VERY strong monitor preference


def check_pattern_d_medium_risk_boundary(audit: AuditResult) -> Optional[float]:
    """
    Pattern D - Medium risk boundary cases should MONITOR.

    Args:
        audit: AuditResult object

    Returns:
        Score preference if Pattern D medium risk matches, None otherwise
    """
    if not (0.68 <= audit.score < 0.91 and audit.risk_level == "medium"):
        return None

    # Pattern F exception: very high violation count is always Pattern F
    if hasattr(audit, "violation_count") and audit.violation_count >= 7:
        return 0.05  # Let conditional win for multi-violation

    return 0.95  # Strong monitor for medium risk boundary


def check_pattern_e_pii_monitoring(audit: AuditResult) -> Optional[float]:
    """
    Pattern E - PII monitoring (refined).

    PII exists BUT not reject/conditional criteria AND cost >= 5000 → MONITOR

    Args:
        audit: AuditResult object

    Returns:
        Score preference if Pattern E matches, None otherwise
    """
    if not _is_pii_case(audit):
        return None

    # (pii == 1 OR pii == 2) AND cost >= 5000 AND risk != high → MONITOR
    if audit.pii_indicators <= 2 and audit.risk_level != "high":
        if audit.remediation_cost >= 5000:
            return 0.90  # Good match for Pattern E monitor

    return None


def check_pattern_h_high_scores_with_conditions(audit: AuditResult) -> Optional[float]:
    """
    Sprint 3 FIX: Pattern H - Very high scores (>=0.85) monitor ONLY if:
    - Risk is NOT high, OR
    - Risk is high BUT cost is very expensive (>=15000)

    Args:
        audit: AuditResult object

    Returns:
        Score preference if Pattern H high-score matches, None otherwise
    """
    if audit.score < 0.85:
        return None

    if audit.risk_level != "high":
        return 1.0  # Monitor for high scores with low/medium risk

    if audit.remediation_cost >= 15000:
        return 1.0  # Monitor for high scores + high risk + very expensive

    return 0.01  # High risk + moderate cost → prefer conditional


def check_pattern_f_multi_violation(audit: AuditResult) -> Optional[float]:
    """
    Pattern F: Multi-violation with low severity → prefer conditional, not monitor.

    Cost >= 3000 prevents catching Pattern D (cost ~2000) which also has violations

    Args:
        audit: AuditResult object

    Returns:
        Score preference if Pattern F multi-violation matches, None otherwise
    """
    if not (
        hasattr(audit, "violation_count")
        and audit.violation_count >= 5
        and 0.45 <= audit.score <= 0.75
        and audit.remediation_cost >= 3000
    ):
        return None

    severity = (
        (1.0 - audit.score) * audit.violation_count * (1.0 if audit.risk_level == "high" else 0.5)
    )

    if severity <= 2.5 and audit.business_impact <= 0.7:
        return 0.05  # Low severity + low impact → prefer conditional

    if severity <= 2.5 and audit.business_impact > 0.7:
        return 0.95  # Low severity + high impact → monitor

    return None


def check_pattern_b_low_score_high_impact(audit: AuditResult) -> Optional[float]:
    """
    Pattern B - Low score + high impact + reasonable cost → MONITOR.

    Ground truth: score 0.40-0.60 + impact > 0.85 + cost >= 1500 → MONITOR
    Ground truth: score 0.40-0.60 + impact > 0.85 + cost < 1500 → CONDITIONAL

    Args:
        audit: AuditResult object

    Returns:
        Score preference if Pattern B matches, None otherwise
    """
    if not (0.40 <= audit.score < 0.60):
        return None

    if audit.business_impact > 0.85:
        if audit.remediation_cost >= 1500:
            return 0.95  # Increased from 0.80 - strong preference for monitoring
        else:
            return 0.05  # Phase 4: Prefer CONDITIONAL for cheap fixes

    return None


def check_boundary_medium_high_scores(audit: AuditResult) -> Optional[float]:
    """
    Check for medium-high scores with acceptable risk.

    Args:
        audit: AuditResult object

    Returns:
        Score preference if boundary condition matches, None otherwise
    """
    if not (0.68 <= audit.score < 0.88 and audit.risk_level in ["low", "medium"]):
        return None

    if audit.remediation_cost >= 6000:
        return 0.85  # Slightly lower for expensive → prefer conditional

    return 0.9


def check_medium_medium_medium_pattern(audit: AuditResult) -> Optional[float]:
    """
    Check for medium everything with good/bad impact.

    Args:
        audit: AuditResult object

    Returns:
        Score preference if pattern matches, None otherwise
    """
    if not (0.55 <= audit.score <= 0.75 and audit.risk_level == "medium"):
        return None

    if audit.business_impact > 0.6:
        # C-6 fix: score > 0.65 + impact ≤ 0.70 is Pattern C MONITOR
        if audit.score > 0.65 and audit.business_impact <= 0.70:
            return 0.91  # Beat conditional 0.90 for Pattern C MONITOR

        # C-9 fix: score ≤ 0.65 + cheap fix → prefer conditional
        if audit.score <= 0.65 and audit.remediation_cost < 3000:
            return 0.80  # Weaker monitor → let conditional win

        return 0.85

    # Sprint 3 PHASE 2: Pattern C - poor impact + high cost → prefer reject
    if audit.business_impact < 0.6 and audit.remediation_cost > 3000:
        return 0.01  # Strong penalty - prefer reject

    return None
