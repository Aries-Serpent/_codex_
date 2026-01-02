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
from typing import List, Tuple
from dataclasses import dataclass

from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceDecision
)


@dataclass
class ScenarioComplexity:
    """Metrics describing scenario complexity"""
    ambiguity_score: float  # 0-1, higher = more ambiguous
    conflicting_signals: int  # Number of conflicting indicators
    rule_coverage: float  # 0-1, how well rules cover this case
    

def generate_complex_scenarios(count: int, seed: int = 42) -> List[Tuple[AuditResult, ComplianceDecision, ScenarioComplexity]]:
    """
    Generate complex, ambiguous compliance scenarios.
    
    These scenarios have conflicting signals that make simple rule-based
    decisions difficult, testing quantum superposition's advantage.
    
    Complexity Patterns:
    1. High compliance + high risk (conflicting)
    2. Low compliance + high business impact (tradeoff)
    3. Medium everything (ambiguous)
    4. Marginal boundaries (edge cases)
    5. Multi-factor conflicts (complex tradeoffs)
    
    Args:
        count: Number of scenarios to generate
        seed: Random seed for reproducibility
    
    Returns:
        List of (audit, ground_truth, complexity) tuples
    """
    random.seed(seed)
    scenarios = []
    
    # Pattern 1: High compliance + high risk (25%)
    for i in range(count // 4):
        score = random.uniform(0.75, 0.95)  # High compliance
        audit = AuditResult(
            audit_id=f"COMPLEX-A-{i}",
            score=score,
            risk_level="high",  # But high risk!
            remediation_cost=random.uniform(5000, 15000),  # Expensive
            business_impact=random.uniform(0.6, 0.9),  # Good impact
            violations=[f"HighRiskViolation-{j}" for j in range(2)]
        )
        # Ground truth: CONDITIONAL due to risk despite good score
        ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        complexity = ScenarioComplexity(
            ambiguity_score=0.8,
            conflicting_signals=2,  # Score vs risk
            rule_coverage=0.4
        )
        scenarios.append((audit, ground_truth, complexity))
    
    # Pattern 2: Low compliance + high impact (25%)
    for i in range(count // 4):
        score = random.uniform(0.40, 0.60)  # Low-medium compliance
        audit = AuditResult(
            audit_id=f"COMPLEX-B-{i}",
            score=score,
            risk_level=random.choice(["low", "medium"]),
            remediation_cost=random.uniform(500, 2000),  # Cheap to fix
            business_impact=random.uniform(0.85, 0.98),  # Very high impact!
            violations=[f"MinorViolation-{j}" for j in range(random.randint(2, 4))]
        )
        # Ground truth: CONDITIONAL or MONITOR depending on fix cost
        ground_truth = (ComplianceDecision.CONDITIONAL_APPROVAL if audit.remediation_cost < 1500 
                       else ComplianceDecision.APPROVE_WITH_MONITORING)
        complexity = ScenarioComplexity(
            ambiguity_score=0.75,
            conflicting_signals=2,  # Compliance vs impact
            rule_coverage=0.5
        )
        scenarios.append((audit, ground_truth, complexity))
    
    # Pattern 3: Everything medium (25%)
    for i in range(count // 4):
        score = random.uniform(0.55, 0.75)  # Medium
        audit = AuditResult(
            audit_id=f"COMPLEX-C-{i}",
            score=score,
            risk_level="medium",
            remediation_cost=random.uniform(2000, 5000),
            business_impact=random.uniform(0.50, 0.70),
            violations=[f"MediumViolation-{j}" for j in range(random.randint(2, 5))]
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
            rule_coverage=0.3  # Rules don't cover well
        )
        scenarios.append((audit, ground_truth, complexity))
    
    # Pattern 4: Boundary cases (remaining)
    remaining = count - len(scenarios)
    for i in range(remaining):
        # Right on decision boundaries
        score_boundary = random.choice([0.50, 0.70, 0.90])  # Key thresholds
        score = score_boundary + random.uniform(-0.02, 0.02)
        audit = AuditResult(
            audit_id=f"COMPLEX-D-{i}",
            score=score,
            risk_level=random.choice(["low", "medium", "high"]),
            remediation_cost=2000 + random.uniform(-100, 100),  # Near threshold
            business_impact=random.uniform(0.45, 0.55),  # Near midpoint
            violations=[f"BoundaryViolation-{j}" for j in range(random.randint(1, 6))]
        )
        # Apply boundary logic
        if score >= 0.88:
            ground_truth = (ComplianceDecision.APPROVE if audit.risk_level == "low"
                          else ComplianceDecision.APPROVE_WITH_MONITORING)
        elif score >= 0.68:
            ground_truth = ComplianceDecision.APPROVE_WITH_MONITORING
        elif audit.remediation_cost < 2100:
            ground_truth = ComplianceDecision.CONDITIONAL_APPROVAL
        else:
            ground_truth = ComplianceDecision.REJECT
        complexity = ScenarioComplexity(
            ambiguity_score=0.85,
            conflicting_signals=1,
            rule_coverage=0.6
        )
        scenarios.append((audit, ground_truth, complexity))
    
    return scenarios


def get_scenario_statistics(scenarios: List[Tuple[AuditResult, ComplianceDecision, ScenarioComplexity]]) -> dict:
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
        'count': len(scenarios),
        'avg_ambiguity': sum(c.ambiguity_score for c in complexities) / len(complexities),
        'avg_conflicting_signals': sum(c.conflicting_signals for c in complexities) / len(complexities),
        'avg_rule_coverage': sum(c.rule_coverage for c in complexities) / len(complexities),
        'decision_distribution': {
            decision.value: sum(1 for d in decisions if d == decision)
            for decision in ComplianceDecision
        }
    }
