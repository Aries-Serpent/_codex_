"""
Complex Scenario Generator for Ambiguous Compliance Testing

Generates edge cases and ambiguous audits where simple rule-based logic struggles.
Tests quantum superposition advantage in complex decision spaces.

PDA Loop + AfterMath:
- PLAN: Define complexity dimensions
- DO: Generate ambiguous scenarios
- ASSESS: Validate scenario diversity
- AfterMath: Track which scenarios challenge classical approach
"""

import random
from dataclasses import dataclass

from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceDecision,
)


@dataclass
class ScenarioComplexity:
    """Metrics describing scenario complexity"""

    ambiguity_score: float  # 0-1, higher = more ambiguous
    conflicting_signals: int  # Number of conflicting indicators
    rule_coverage: float  # 0-1, how well rules cover this case


def generate_complex_scenarios(
    count: int, seed: int = 42
) -> list[tuple[AuditResult, ComplianceDecision, ScenarioComplexity]]:
    """
    Generate complex, ambiguous compliance scenarios.

    These scenarios have conflicting signals that make simple rule-based
    decisions difficult, testing quantum superposition's advantage.

    Phase 8.0 Expansion: Now generates up to 100 scenarios with enhanced patterns:
    1. High compliance + high risk (conflicting) - 15%
    2. Low compliance + high business impact (tradeoff) - 15%
    3. Medium everything (ambiguous) - 15%
    4. Marginal boundaries (edge cases) - 15%
    5. Ambiguous PII exposure cases - 15%
    6. Multi-violation interactions - 15%
    7. Compliance vs security conflicts - 10%
    8. Temporal complexity (evolving violations) - 10%

    Args:
        count: Number of scenarios to generate (recommended: 100 for Phase 8.0)
        seed: Random seed for reproducibility

    Returns:
        List of (audit, ground_truth, complexity) tuples
    """
    # Copilot: Using random.Random() instance for reproducible test data generation.
    # This is NOT for security/cryptographic purposes - Bandit B311 is a false positive here.
    # These are experiment scenarios for testing compliance decision algorithms.
    _rng = random.Random(seed)  # nosec B311
    scenarios = []

    # Pattern 1: High compliance + high risk (15%)
    for i in range(int(count * 0.15)):
        score = _rng.uniform(0.75, 0.95)  # High compliance
        audit = AuditResult(
            audit_id=f"COMPLEX-A-{i}",
            score=score,
            risk_level="high",  # But high risk!
            remediation_cost=_rng.uniform(5000, 15000),  # Expensive
            business_impact=_rng.uniform(0.6, 0.9),  # Good impact
            violations=[f"HighRiskViolation-{j}" for j in range(2)],
        )
        # Ground truth: CONDITIONAL due to risk despite good score
        ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        complexity = ScenarioComplexity(
            ambiguity_score=0.8,
            conflicting_signals=2,  # Score vs risk
            rule_coverage=0.4,
        )
        scenarios.append((audit, ground_truth, complexity))

    # Pattern 2: Low compliance + high impact (15%)
    for i in range(int(count * 0.15)):
        score = _rng.uniform(0.40, 0.60)  # Low-medium compliance
        audit = AuditResult(
            audit_id=f"COMPLEX-B-{i}",
            score=score,
            risk_level=_rng.choice(["low", "medium"]),
            remediation_cost=_rng.uniform(500, 2000),  # Cheap to fix
            business_impact=_rng.uniform(0.85, 0.98),  # Very high impact!
            violations=[f"MinorViolation-{j}" for j in range(_rng.randint(2, 4))],
        )
        # Ground truth: CONDITIONAL or MONITOR depending on fix cost
        ground_truth = (
            ComplianceDecision.CONDITIONAL_APPROVAL
            if audit.remediation_cost < 1500
            else ComplianceDecision.APPROVE_WITH_MONITORING
        )
        complexity = ScenarioComplexity(
            ambiguity_score=0.75,
            conflicting_signals=2,  # Compliance vs impact
            rule_coverage=0.5,
        )
        scenarios.append((audit, ground_truth, complexity))

    # Pattern 3: Everything medium (15%)
    for i in range(int(count * 0.15)):
        score = _rng.uniform(0.55, 0.75)  # Medium
        audit = AuditResult(
            audit_id=f"COMPLEX-C-{i}",
            score=score,
            risk_level="medium",
            remediation_cost=_rng.uniform(2000, 5000),
            business_impact=_rng.uniform(0.50, 0.70),
            violations=[f"MediumViolation-{j}" for j in range(_rng.randint(2, 5))],
        )
        # Ground truth: Very ambiguous, use weighted decision
        if score > 0.65 and audit.business_impact > 0.6:
            ground_truth = ComplianceDecision.APPROVE_WITH_MONITORING
        elif audit.remediation_cost < 3000:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        else:
            ground_truth = ComplianceDecision.REJECT
        complexity = ScenarioComplexity(
            ambiguity_score=0.9,  # Very ambiguous
            conflicting_signals=0,  # No clear conflicts
            rule_coverage=0.3,  # Rules don't cover well
        )
        scenarios.append((audit, ground_truth, complexity))

    # Pattern 4: Boundary cases (15%)
    for i in range(int(count * 0.15)):
        # Right on decision boundaries
        score_boundary = _rng.choice([0.50, 0.70, 0.90])  # Key thresholds
        score = score_boundary + _rng.uniform(-0.02, 0.02)
        audit = AuditResult(
            audit_id=f"COMPLEX-D-{i}",
            score=score,
            risk_level=_rng.choice(["low", "medium", "high"]),
            remediation_cost=2000 + _rng.uniform(-100, 100),  # Near threshold
            business_impact=_rng.uniform(0.45, 0.55),  # Near midpoint
            violations=[f"BoundaryViolation-{j}" for j in range(_rng.randint(1, 6))],
        )
        # Apply boundary logic
        if score >= 0.88:
            ground_truth = (
                ComplianceDecision.APPROVE
                if audit.risk_level == "low"
                else ComplianceDecision.APPROVE_WITH_MONITORING
            )
        elif score >= 0.68:
            ground_truth = ComplianceDecision.APPROVE_WITH_MONITORING
        elif audit.remediation_cost < 2100:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        else:
            ground_truth = ComplianceDecision.REJECT
        complexity = ScenarioComplexity(
            ambiguity_score=0.85, conflicting_signals=1, rule_coverage=0.6
        )
        scenarios.append((audit, ground_truth, complexity))

    # Pattern 5: Ambiguous PII exposure cases (15%)
    for i in range(int(count * 0.15)):
        score = _rng.uniform(0.60, 0.80)  # Medium-high
        # Ambiguous: might contain PII but unclear
        pii_indicators = _rng.randint(1, 3)
        audit = AuditResult(
            audit_id=f"COMPLEX-E-{i}",
            score=score,
            risk_level=_rng.choice(["medium", "high"]),
            remediation_cost=_rng.uniform(3000, 8000),
            business_impact=_rng.uniform(0.55, 0.85),
            violations=[f"PotentialPII-{j}" for j in range(pii_indicators)],
            pii_indicators=pii_indicators,  # Phase 1: Explicit PII indicator count
        )
        # Ground truth: depends on PII likelihood and remediation cost
        if pii_indicators >= 3 or audit.risk_level == "high":
            ground_truth = ComplianceDecision.REJECT
        elif audit.remediation_cost < 5000:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        else:
            ground_truth = ComplianceDecision.APPROVE_WITH_MONITORING
        complexity = ScenarioComplexity(
            ambiguity_score=0.85,
            conflicting_signals=2,  # PII vs business value
            rule_coverage=0.35,
        )
        scenarios.append((audit, ground_truth, complexity))

    # Pattern 6: Multi-violation interaction scenarios (15%)
    for i in range(int(count * 0.15)):
        score = _rng.uniform(0.45, 0.75)
        # Phase 1 SOLUTION: Changed from 3-7 to 5-8 for better differentiation from other patterns
        violation_count = _rng.randint(5, 9)  # Multiple violations (5-8)
        audit = AuditResult(
            audit_id=f"COMPLEX-F-{i}",
            score=score,
            risk_level=_rng.choice(["low", "medium", "high"]),
            remediation_cost=_rng.uniform(1000, 10000),
            business_impact=_rng.uniform(0.40, 0.90),
            violations=[f"Violation-Type{j % 4}-{j}" for j in range(violation_count)],
            violation_count=violation_count,  # Phase 1: Explicit violation count
        )
        # Ground truth: complex interaction of multiple factors
        severity_score = (
            (1.0 - score) * violation_count * (1.0 if audit.risk_level == "high" else 0.5)
        )
        if severity_score > 4.0:
            ground_truth = ComplianceDecision.REJECT
        elif severity_score > 2.5:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        elif audit.business_impact > 0.7:
            ground_truth = ComplianceDecision.APPROVE_WITH_MONITORING
        else:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        complexity = ScenarioComplexity(
            ambiguity_score=0.88,
            conflicting_signals=3,  # Multiple interacting factors
            rule_coverage=0.25,
        )
        scenarios.append((audit, ground_truth, complexity))

    # Pattern 7: Compliance vs security conflict edge cases (10%)
    for i in range(int(count * 0.10)):
        score = _rng.uniform(0.80, 0.95)  # High compliance
        audit = AuditResult(
            audit_id=f"COMPLEX-G-{i}",
            score=score,
            risk_level="high",  # But high security risk!
            remediation_cost=_rng.uniform(10000, 20000),  # Very expensive
            business_impact=_rng.uniform(0.70, 0.95),  # High business value
            violations=["SecurityVulnerability", "HighRiskExposure"],
        )
        # Ground truth: security trumps compliance in most cases
        if audit.remediation_cost < 15000:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        else:
            ground_truth = ComplianceDecision.APPROVE_WITH_MONITORING
        complexity = ScenarioComplexity(
            ambiguity_score=0.92,
            conflicting_signals=3,  # Compliance vs security vs cost vs impact
            rule_coverage=0.20,
        )
        scenarios.append((audit, ground_truth, complexity))

    # Pattern 8: Temporal complexity (evolving violations over time) (10%)
    for i in range(int(count * 0.10)):
        base_score = _rng.uniform(0.50, 0.85)
        # Violations that change severity over time (factor 0.5-1.5)
        # Business Logic: Models real-world compliance score evolution
        #   - Deterioration (0.5-1.0): Security patches expire, policies change, drift occurs
        #   - Improvement (1.0-1.5): Remediation efforts, new controls, compliance catch-up
        # Symmetric range around 1.0 allows equal probability of improvement/deterioration
        temporal_factor = _rng.uniform(0.5, 1.5)
        # Cap adjusted score at 1.0 to ensure valid range (0.0-1.0)
        adjusted_score = min(1.0, base_score * temporal_factor)

        audit = AuditResult(
            audit_id=f"COMPLEX-H-{i}",
            score=adjusted_score,  # Score affected by time, capped at 1.0
            risk_level=_rng.choice(["low", "medium", "high"]),
            remediation_cost=_rng.uniform(2000, 12000),
            business_impact=_rng.uniform(0.50, 0.85),
            violations=[f"EvolvingViolation-{j}" for j in range(_rng.randint(1, 4))],
        )
        # Ground truth: use adjusted score for consistency
        if adjusted_score >= 0.85:
            ground_truth = ComplianceDecision.APPROVE_WITH_MONITORING
        elif adjusted_score >= 0.65 or audit.remediation_cost < 6000:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        else:
            ground_truth = ComplianceDecision.REJECT
        complexity = ScenarioComplexity(
            ambiguity_score=0.87,
            conflicting_signals=2,  # Current state vs future evolution
            rule_coverage=0.30,
        )
        scenarios.append((audit, ground_truth, complexity))

    # Fill remaining to exact count (if needed due to rounding)
    while len(scenarios) < count:
        # Add boundary cases
        i = len(scenarios)
        score_boundary = _rng.choice([0.50, 0.70, 0.90])
        score = score_boundary + _rng.uniform(-0.02, 0.02)
        audit = AuditResult(
            audit_id=f"COMPLEX-FILL-{i}",
            score=score,
            risk_level=_rng.choice(["low", "medium", "high"]),
            remediation_cost=2000 + _rng.uniform(-100, 100),
            business_impact=_rng.uniform(0.45, 0.55),
            violations=[f"FillViolation-{j}" for j in range(_rng.randint(1, 3))],
        )
        if score >= 0.88:
            ground_truth = (
                ComplianceDecision.APPROVE
                if audit.risk_level == "low"
                else ComplianceDecision.APPROVE_WITH_MONITORING
            )
        elif score >= 0.68:
            ground_truth = ComplianceDecision.APPROVE_WITH_MONITORING
        elif audit.remediation_cost < 2100:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        else:
            ground_truth = ComplianceDecision.REJECT
        complexity = ScenarioComplexity(
            ambiguity_score=0.85, conflicting_signals=1, rule_coverage=0.6
        )
        scenarios.append((audit, ground_truth, complexity))

    return scenarios


def get_scenario_statistics(
    scenarios: list[tuple[AuditResult, ComplianceDecision, ScenarioComplexity]],
) -> dict:
    """
    Compute statistics about generated scenarios.

    Args:
        scenarios: List of (audit, decision, complexity) tuples

    Returns:
        Dict with statistics
    """
    if not scenarios:
        return {}

    complexities = [c for _, _, c in scenarios]
    decisions = [d for _, d, _ in scenarios]

    return {
        "count": len(scenarios),
        "avg_ambiguity": sum(c.ambiguity_score for c in complexities) / len(complexities),
        "avg_conflicting_signals": sum(c.conflicting_signals for c in complexities)
        / len(complexities),
        "avg_rule_coverage": sum(c.rule_coverage for c in complexities) / len(complexities),
        "decision_distribution": {
            decision.value: sum(1 for d in decisions if d == decision)
            for decision in ComplianceDecision
        },
    }
