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
from dataclasses import dataclass
from typing import Dict

from cognitive_brain.experiments.complex_scenarios import (
    generate_complex_scenarios,
    get_scenario_statistics,
)
from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceAssessor,
    ComplianceDecision,
)
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.adaptive_scoring import AdaptiveScoringOptimizer
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig


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
    config.quantum_mode = True  # Enable quantum features
    config.superposition = True  # Required for complex scenario handling

    # Initialize required dependencies for quantum compliance assessor
    repository = QuantumMetricRepository(db_path=":memory:")  # In-memory DB for experiments
    monitor = CoherenceMonitor(config, repository)
    assessor = ComplianceAssessor(config, monitor, repository)

    # Verify optimized weights are loaded
    optimizer = AdaptiveScoringOptimizer(learning_rate=0.12)
    weights = optimizer.weights
    print("Loaded optimized weights:")
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
    
    # Sprint 3: Diagnostic logging for failure analysis
    mismatches = []
    pattern_failures = {}  # Track failures by scenario pattern

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess_compliance(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision == ground_truth:
            correct_predictions += 1
        else:
            # Sprint 3: Log mismatch for analysis
            pattern = audit.audit_id.split('-')[1] if '-' in audit.audit_id else 'UNKNOWN'
            mismatch = {
                'audit_id': audit.audit_id,
                'pattern': pattern,
                'expected': ground_truth.value,
                'predicted': assessment.decision.value,
                'score': audit.score,
                'risk': audit.risk_level,
                'cost': audit.remediation_cost,
                'impact': audit.business_impact,
                'coherence': assessment.coherence,
                'confidence': assessment.confidence,
                'complexity': complexity.ambiguity_score
            }
            mismatches.append(mismatch)
            
            # Track by pattern
            if pattern not in pattern_failures:
                pattern_failures[pattern] = []
            pattern_failures[pattern].append(mismatch)
    
    # Sprint 1 Optimization: Flush any batched metrics
    # CoherenceMonitor may have batched metrics for performance
    if hasattr(monitor, 'flush_batch'):
        monitor.flush_batch()
        print("  - Flushed batched metrics to database")

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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 0.35 else '❌'} (target ≤ 0.35)"
    )
    print(
        f"Accuracy:                 {accuracy:.1%} {'✅' if accuracy >= 0.84 else '❌'} (target ≥ 84%)"
    )
    print(
        f"Average Coherence:        {avg_coherence:.3f} {'✅' if avg_coherence >= 0.650 else '❌'} (target ≥ 0.650)"
    )
    print(f"Average Time:             {avg_time_ms:.2f}ms")
    print(f"Error Rate:               {error_rate:.1%}")
    print(f"Classical Baseline:       {classical_baseline_ms:.2f}ms")
    print(f"Total Scenarios:          {len(scenario_data)}")
    print("\nScenario Statistics:")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
    print("=" * 60)
    
    # Sprint 3: Print diagnostic information
    if mismatches:
        print(f"\n📊 Sprint 3 Diagnostic Analysis")
        print("=" * 60)
        print(f"Total Mismatches: {len(mismatches)} / {len(scenario_data)}")
        print(f"\nFailures by Pattern:")
        for pattern in sorted(pattern_failures.keys()):
            failures = pattern_failures[pattern]
            print(f"  Pattern {pattern}: {len(failures)} failures")
            
            # Show common characteristics
            avg_score = sum(m['score'] for m in failures) / len(failures)
            avg_cost = sum(m['cost'] for m in failures) / len(failures)
            avg_coherence = sum(m['coherence'] for m in failures) / len(failures)
            
            print(f"    Avg Score: {avg_score:.2f}, Avg Cost: {avg_cost:.0f}, Avg Coherence: {avg_coherence:.3f}")
            
            # Show a few examples
            for i, m in enumerate(failures[:3]):
                print(f"    Example {i+1}: {m['audit_id']}")
                print(f"      Expected: {m['expected']}, Got: {m['predicted']}")
                print(f"      Score: {m['score']:.2f}, Risk: {m['risk']}, Cost: {m['cost']:.0f}")
        print("=" * 60)
    

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
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


def calculate_k1(
    avg_time_ms: float, error_rate: float, classical_baseline_ms: float
) -> float:
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
        results.k1 <= 0.35 and results.accuracy >= 0.84 and results.coherence >= 0.650
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
