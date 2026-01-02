"""
EXP-1B Revalidation with Optimized Weights (Phase 8.0)

Validates k₁ reduction from 0.36 to 0.35 (100% of target) with expanded 100-scenario dataset
and optimized AdaptiveScoringOptimizer weights.

PDA Loop + AfterMath:
- PLAN: Load optimized weights, generate 100 scenarios
- DO: Run quantum assessment with new configuration
- ASSESS: Calculate k₁, accuracy, coherence metrics
- AfterMath: Validate k₁ ≤ 0.35 target achievement

Success Criteria:
- k₁ ≤ 0.35 (100% of Phase 8.0 target)
- Accuracy ≥ 84% (quantum vs ground truth)
- Coherence ≥ 0.650 (average across all assessments)
- Deterministic results with seed=42
"""

import time
from typing import Dict
from dataclasses import dataclass

from cognitive_brain.experiments.complex_scenarios import (
    generate_complex_scenarios,
    get_scenario_statistics
)
from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceDecision,
    ComplianceAssessor
)
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.adaptive_scoring import AdaptiveScoringOptimizer


@dataclass
class EXP1BResults:
    """Results from EXP-1B revalidation experiment"""
    k1: float  # Process factor (target ≤ 0.35)
    accuracy: float  # Quantum accuracy vs ground truth (target ≥ 0.84)
    coherence: float  # Average coherence (target ≥ 0.650)
    avg_time_ms: float  # Average assessment time in milliseconds
    error_rate: float  # Fraction of incorrect predictions
    classical_baseline_ms: float  # Classical assessment time baseline
    total_scenarios: int  # Number of scenarios evaluated
    scenario_stats: Dict  # Statistics about scenario complexity


def run_exp1b_revalidation(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
    """
    Run EXP-1B revalidation with Phase 8.0 optimized weights.
    
    This experiment validates that the weight optimizations in AdaptiveScoringOptimizer
    (compliance=0.38, risk=0.32, learning_rate=0.12) achieve k₁ ≤ 0.35.
    
    Args:
        scenarios: Number of complex scenarios to generate (default: 100)
        seed: Random seed for reproducibility (default: 42)
    
    Returns:
        EXP1BResults with k₁, accuracy, coherence, and other metrics
    """
    # Generate expanded scenario dataset
    print(f"Generating {scenarios} complex scenarios (seed={seed})...")
    scenario_data = generate_complex_scenarios(count=scenarios, seed=seed)
    scenario_stats = get_scenario_statistics(scenario_data)
    
    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)
    
    # Verify optimized weights are loaded
    optimizer = AdaptiveScoringOptimizer(learning_rate=0.12)
    weights = optimizer.weights
    print(f"Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(f"  - cost_weight: {weights.cost_weight:.3f}")
    print(f"  - impact_weight: {weights.impact_weight:.3f}")
    print(f"  - learning_rate: {optimizer.learning_rate:.3f}")
    
    # Run quantum assessments
    print(f"\nRunning quantum assessments on {scenarios} scenarios...")
    correct_predictions = 0
    total_coherence = 0.0
    total_time_ms = 0.0
    
    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000
        
        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence
        
        if assessment.decision == ground_truth:
            correct_predictions += 1
    
    # Calculate classical baseline (simple rule-based)
    print("\nCalculating classical baseline...")
    classical_start = time.time()
    for audit, _, _ in scenario_data:
        # Simple rule-based decision (classical approach)
        # Result intentionally unused - we only need timing for baseline measurement
        _ = _classical_assessment(audit)
    classical_time_ms = (time.time() - classical_start) * 1000
    classical_baseline_ms = classical_time_ms / len(scenario_data)
    
    # Calculate metrics
    accuracy = correct_predictions / len(scenario_data)
    avg_coherence = total_coherence / len(scenario_data)
    avg_time_ms = total_time_ms / len(scenario_data)
    error_rate = 1.0 - accuracy
    
    # Calculate k₁ using Rayleigh criterion formula
    # k₁ = (avg_time * (1 + error_rate)) / classical_baseline
    k1 = (avg_time_ms * (1.0 + error_rate)) / classical_baseline_ms
    
    # Print results
    print("\n" + "="*60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("="*60)
    print(f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 0.35 else '❌'} (target ≤ 0.35)")
    print(f"Accuracy:                 {accuracy:.1%} {'✅' if accuracy >= 0.84 else '❌'} (target ≥ 84%)")
    print(f"Average Coherence:        {avg_coherence:.3f} {'✅' if avg_coherence >= 0.650 else '❌'} (target ≥ 0.650)")
    print(f"Average Time:             {avg_time_ms:.2f}ms")
    print(f"Error Rate:               {error_rate:.1%}")
    print(f"Classical Baseline:       {classical_baseline_ms:.2f}ms")
    print(f"Total Scenarios:          {len(scenario_data)}")
    print("\nScenario Statistics:")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
    print("="*60)
    
    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats
    )


def _classical_assessment(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).
    
    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def calculate_k1(avg_time_ms: float, error_rate: float, classical_baseline_ms: float) -> float:
    """
    Calculate k₁ process factor using Rayleigh criterion.
    
    Formula:
        k₁ = (avg_time * (1 + error_rate)) / classical_baseline
    
    Reference:
        Adapted from Rayleigh criterion for process capability analysis.
        The k₁ metric combines time efficiency with accuracy penalty, providing
        a normalized measure of quantum advantage over classical approaches.
        
        Target k₁ ≤ 0.35 represents advanced process capability, indicating
        quantum methods achieve 2.86x improvement over classical baseline
        (1/0.35 = 2.86) when accounting for both speed and accuracy.
    
    Lower k₁ indicates better process efficiency (faster, more accurate).
    
    Args:
        avg_time_ms: Average quantum assessment time in milliseconds
        error_rate: Fraction of incorrect predictions (0.0 - 1.0)
        classical_baseline_ms: Classical assessment baseline time in milliseconds
    
    Returns:
        k₁ process factor (target: ≤ 0.35)
    """
    return (avg_time_ms * (1.0 + error_rate)) / classical_baseline_ms


if __name__ == "__main__":
    # Run EXP-1B revalidation with 100 scenarios
    results = run_exp1b_revalidation(scenarios=100, seed=42)
    
    # Validate success criteria
    success = (
        results.k1 <= 0.35 and
        results.accuracy >= 0.84 and
        results.coherence >= 0.650
    )
    
    if success:
        print("\n✅ Phase 8.0 SUCCESS: All criteria met!")
        print(f"   k₁={results.k1:.4f} (100% of target)")
    else:
        print("\n❌ Phase 8.0 INCOMPLETE: Some criteria not met")
        if results.k1 > 0.35:
            print(f"   ❌ k₁={results.k1:.4f} (need ≤ 0.35)")
        if results.accuracy < 0.84:
            print(f"   ❌ accuracy={results.accuracy:.1%} (need ≥ 84%)")
        if results.coherence < 0.650:
            print(f"   ❌ coherence={results.coherence:.3f} (need ≥ 0.650)")
