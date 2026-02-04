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
from cognitive_brain.quantum.adaptive_scoring import AdaptiveScoringOptimizer
from cognitive_brain.quantum.config import QuantumConfig
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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


def x_run_exp1b_revalidation__mutmut_orig(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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


def x_run_exp1b_revalidation__mutmut_1(scenarios: int = 101, seed: int = 42) -> EXP1BResults:
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


def x_run_exp1b_revalidation__mutmut_2(scenarios: int = 100, seed: int = 43) -> EXP1BResults:
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


def x_run_exp1b_revalidation__mutmut_3(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
    scenario_data = generate_complex_scenarios(count=scenarios, seed=seed)
    scenario_stats = get_scenario_statistics(scenario_data)

    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_4(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    scenario_data = None
    scenario_stats = get_scenario_statistics(scenario_data)

    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_5(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    scenario_data = generate_complex_scenarios(count=None, seed=seed)
    scenario_stats = get_scenario_statistics(scenario_data)

    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_6(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    scenario_data = generate_complex_scenarios(count=scenarios, seed=None)
    scenario_stats = get_scenario_statistics(scenario_data)

    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_7(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    scenario_data = generate_complex_scenarios(seed=seed)
    scenario_stats = get_scenario_statistics(scenario_data)

    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_8(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    scenario_data = generate_complex_scenarios(count=scenarios, )
    scenario_stats = get_scenario_statistics(scenario_data)

    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_9(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    scenario_stats = None

    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_10(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    scenario_stats = get_scenario_statistics(None)

    # Initialize quantum assessor with Phase 8.0 optimized configuration
    config = QuantumConfig.from_env()
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_11(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    config = None
    config.superposition_enabled = True  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_12(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    config.superposition_enabled = None  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_13(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    config.superposition_enabled = False  # Required for complex scenario handling
    assessor = ComplianceAssessor(config)

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


def x_run_exp1b_revalidation__mutmut_14(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    assessor = None

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


def x_run_exp1b_revalidation__mutmut_15(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    assessor = ComplianceAssessor(None)

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


def x_run_exp1b_revalidation__mutmut_16(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    optimizer = None
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


def x_run_exp1b_revalidation__mutmut_17(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    optimizer = AdaptiveScoringOptimizer(learning_rate=None)
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


def x_run_exp1b_revalidation__mutmut_18(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    optimizer = AdaptiveScoringOptimizer(learning_rate=1.12)
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


def x_run_exp1b_revalidation__mutmut_19(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    weights = None
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


def x_run_exp1b_revalidation__mutmut_20(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
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


def x_run_exp1b_revalidation__mutmut_21(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("XXLoaded optimized weights:XX")
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


def x_run_exp1b_revalidation__mutmut_22(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("loaded optimized weights:")
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


def x_run_exp1b_revalidation__mutmut_23(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("LOADED OPTIMIZED WEIGHTS:")
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


def x_run_exp1b_revalidation__mutmut_24(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(None)
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


def x_run_exp1b_revalidation__mutmut_25(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(None)
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


def x_run_exp1b_revalidation__mutmut_26(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(None)
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


def x_run_exp1b_revalidation__mutmut_27(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(f"  - cost_weight: {weights.cost_weight:.3f}")
    print(None)
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


def x_run_exp1b_revalidation__mutmut_28(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(f"  - cost_weight: {weights.cost_weight:.3f}")
    print(f"  - impact_weight: {weights.impact_weight:.3f}")
    print(None)

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


def x_run_exp1b_revalidation__mutmut_29(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(f"  - cost_weight: {weights.cost_weight:.3f}")
    print(f"  - impact_weight: {weights.impact_weight:.3f}")
    print(f"  - learning_rate: {optimizer.learning_rate:.3f}")

    # Run quantum assessments
    print(None)
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


def x_run_exp1b_revalidation__mutmut_30(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(f"  - cost_weight: {weights.cost_weight:.3f}")
    print(f"  - impact_weight: {weights.impact_weight:.3f}")
    print(f"  - learning_rate: {optimizer.learning_rate:.3f}")

    # Run quantum assessments
    print(f"\nRunning quantum assessments on {scenarios} scenarios...")
    correct_predictions = None
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


def x_run_exp1b_revalidation__mutmut_31(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(f"  - cost_weight: {weights.cost_weight:.3f}")
    print(f"  - impact_weight: {weights.impact_weight:.3f}")
    print(f"  - learning_rate: {optimizer.learning_rate:.3f}")

    # Run quantum assessments
    print(f"\nRunning quantum assessments on {scenarios} scenarios...")
    correct_predictions = 1
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


def x_run_exp1b_revalidation__mutmut_32(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(f"  - cost_weight: {weights.cost_weight:.3f}")
    print(f"  - impact_weight: {weights.impact_weight:.3f}")
    print(f"  - learning_rate: {optimizer.learning_rate:.3f}")

    # Run quantum assessments
    print(f"\nRunning quantum assessments on {scenarios} scenarios...")
    correct_predictions = 0
    total_coherence = None
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


def x_run_exp1b_revalidation__mutmut_33(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("Loaded optimized weights:")
    print(f"  - compliance_score_weight: {weights.compliance_score_weight:.3f}")
    print(f"  - risk_weight: {weights.risk_weight:.3f}")
    print(f"  - cost_weight: {weights.cost_weight:.3f}")
    print(f"  - impact_weight: {weights.impact_weight:.3f}")
    print(f"  - learning_rate: {optimizer.learning_rate:.3f}")

    # Run quantum assessments
    print(f"\nRunning quantum assessments on {scenarios} scenarios...")
    correct_predictions = 0
    total_coherence = 1.0
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


def x_run_exp1b_revalidation__mutmut_34(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    total_time_ms = None

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


def x_run_exp1b_revalidation__mutmut_35(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    total_time_ms = 1.0

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


def x_run_exp1b_revalidation__mutmut_36(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = None
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


def x_run_exp1b_revalidation__mutmut_37(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = None
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


def x_run_exp1b_revalidation__mutmut_38(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(None)
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


def x_run_exp1b_revalidation__mutmut_39(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = None

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


def x_run_exp1b_revalidation__mutmut_40(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) / 1000

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


def x_run_exp1b_revalidation__mutmut_41(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() + start_time) * 1000

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


def x_run_exp1b_revalidation__mutmut_42(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1001

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


def x_run_exp1b_revalidation__mutmut_43(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms = elapsed_ms
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


def x_run_exp1b_revalidation__mutmut_44(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms -= elapsed_ms
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


def x_run_exp1b_revalidation__mutmut_45(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence = assessment.coherence

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


def x_run_exp1b_revalidation__mutmut_46(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence -= assessment.coherence

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


def x_run_exp1b_revalidation__mutmut_47(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision != ground_truth:
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


def x_run_exp1b_revalidation__mutmut_48(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision == ground_truth:
            correct_predictions = 1

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


def x_run_exp1b_revalidation__mutmut_49(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision == ground_truth:
            correct_predictions -= 1

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


def x_run_exp1b_revalidation__mutmut_50(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision == ground_truth:
            correct_predictions += 2

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


def x_run_exp1b_revalidation__mutmut_51(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision == ground_truth:
            correct_predictions += 1

    # Calculate classical baseline (simple rule-based)
    print(None)
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


def x_run_exp1b_revalidation__mutmut_52(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision == ground_truth:
            correct_predictions += 1

    # Calculate classical baseline (simple rule-based)
    print("XX\nCalculating classical baseline...XX")
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


def x_run_exp1b_revalidation__mutmut_53(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision == ground_truth:
            correct_predictions += 1

    # Calculate classical baseline (simple rule-based)
    print("\ncalculating classical baseline...")
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


def x_run_exp1b_revalidation__mutmut_54(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    for audit, ground_truth, complexity in scenario_data:
        start_time = time.time()
        assessment = assessor.assess(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        total_time_ms += elapsed_ms
        total_coherence += assessment.coherence

        if assessment.decision == ground_truth:
            correct_predictions += 1

    # Calculate classical baseline (simple rule-based)
    print("\nCALCULATING CLASSICAL BASELINE...")
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


def x_run_exp1b_revalidation__mutmut_55(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    classical_start = None
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


def x_run_exp1b_revalidation__mutmut_56(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
        _ = None
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


def x_run_exp1b_revalidation__mutmut_57(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
        _ = _classical_assessment(None)
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


def x_run_exp1b_revalidation__mutmut_58(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    classical_time_ms = None
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


def x_run_exp1b_revalidation__mutmut_59(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    classical_time_ms = (time.time() - classical_start) / 1000
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


def x_run_exp1b_revalidation__mutmut_60(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    classical_time_ms = (time.time() + classical_start) * 1000
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


def x_run_exp1b_revalidation__mutmut_61(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    classical_time_ms = (time.time() - classical_start) * 1001
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


def x_run_exp1b_revalidation__mutmut_62(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    classical_baseline_ms = None

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


def x_run_exp1b_revalidation__mutmut_63(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    classical_baseline_ms = classical_time_ms * len(scenario_data)

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


def x_run_exp1b_revalidation__mutmut_64(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    accuracy = None
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


def x_run_exp1b_revalidation__mutmut_65(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    accuracy = correct_predictions * len(scenario_data)
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


def x_run_exp1b_revalidation__mutmut_66(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    avg_coherence = None
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


def x_run_exp1b_revalidation__mutmut_67(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    avg_coherence = total_coherence * len(scenario_data)
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


def x_run_exp1b_revalidation__mutmut_68(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    avg_time_ms = None
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


def x_run_exp1b_revalidation__mutmut_69(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    avg_time_ms = total_time_ms * len(scenario_data)
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


def x_run_exp1b_revalidation__mutmut_70(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    error_rate = None

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


def x_run_exp1b_revalidation__mutmut_71(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    error_rate = 1.0 + accuracy

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


def x_run_exp1b_revalidation__mutmut_72(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    error_rate = 2.0 - accuracy

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


def x_run_exp1b_revalidation__mutmut_73(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    k1 = None

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


def x_run_exp1b_revalidation__mutmut_74(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    k1 = (avg_time_ms * (1.0 + error_rate)) * classical_baseline_ms

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


def x_run_exp1b_revalidation__mutmut_75(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    k1 = (avg_time_ms / (1.0 + error_rate)) / classical_baseline_ms

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


def x_run_exp1b_revalidation__mutmut_76(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    k1 = (avg_time_ms * (1.0 - error_rate)) / classical_baseline_ms

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


def x_run_exp1b_revalidation__mutmut_77(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    k1 = (avg_time_ms * (2.0 + error_rate)) / classical_baseline_ms

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


def x_run_exp1b_revalidation__mutmut_78(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
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


def x_run_exp1b_revalidation__mutmut_79(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" - "=" * 60)
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


def x_run_exp1b_revalidation__mutmut_80(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("XX\nXX" + "=" * 60)
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


def x_run_exp1b_revalidation__mutmut_81(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" / 60)
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


def x_run_exp1b_revalidation__mutmut_82(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "XX=XX" * 60)
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


def x_run_exp1b_revalidation__mutmut_83(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 61)
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


def x_run_exp1b_revalidation__mutmut_84(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print(None)
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


def x_run_exp1b_revalidation__mutmut_85(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("XXEXP-1B Revalidation Results (Phase 8.0)XX")
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


def x_run_exp1b_revalidation__mutmut_86(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("exp-1b revalidation results (phase 8.0)")
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


def x_run_exp1b_revalidation__mutmut_87(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B REVALIDATION RESULTS (PHASE 8.0)")
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


def x_run_exp1b_revalidation__mutmut_88(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print(None)
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


def x_run_exp1b_revalidation__mutmut_89(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" / 60)
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


def x_run_exp1b_revalidation__mutmut_90(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("XX=XX" * 60)
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


def x_run_exp1b_revalidation__mutmut_91(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 61)
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


def x_run_exp1b_revalidation__mutmut_92(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        None
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


def x_run_exp1b_revalidation__mutmut_93(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'XX✅XX' if k1 <= 0.35 else '❌'} (target ≤ 0.35)"
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


def x_run_exp1b_revalidation__mutmut_94(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 < 0.35 else '❌'} (target ≤ 0.35)"
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


def x_run_exp1b_revalidation__mutmut_95(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 1.35 else '❌'} (target ≤ 0.35)"
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


def x_run_exp1b_revalidation__mutmut_96(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 0.35 else 'XX❌XX'} (target ≤ 0.35)"
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


def x_run_exp1b_revalidation__mutmut_97(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 0.35 else '❌'} (target ≤ 0.35)"
    )
    print(
        None
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


def x_run_exp1b_revalidation__mutmut_98(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 0.35 else '❌'} (target ≤ 0.35)"
    )
    print(
        f"Accuracy:                 {accuracy:.1%} {'XX✅XX' if accuracy >= 0.84 else '❌'} (target ≥ 84%)"
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


def x_run_exp1b_revalidation__mutmut_99(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 0.35 else '❌'} (target ≤ 0.35)"
    )
    print(
        f"Accuracy:                 {accuracy:.1%} {'✅' if accuracy > 0.84 else '❌'} (target ≥ 84%)"
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


def x_run_exp1b_revalidation__mutmut_100(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 0.35 else '❌'} (target ≤ 0.35)"
    )
    print(
        f"Accuracy:                 {accuracy:.1%} {'✅' if accuracy >= 1.8399999999999999 else '❌'} (target ≥ 84%)"
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


def x_run_exp1b_revalidation__mutmut_101(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\n" + "=" * 60)
    print("EXP-1B Revalidation Results (Phase 8.0)")
    print("=" * 60)
    print(
        f"k₁ Process Factor:        {k1:.4f} {'✅' if k1 <= 0.35 else '❌'} (target ≤ 0.35)"
    )
    print(
        f"Accuracy:                 {accuracy:.1%} {'✅' if accuracy >= 0.84 else 'XX❌XX'} (target ≥ 84%)"
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


def x_run_exp1b_revalidation__mutmut_102(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
        None
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


def x_run_exp1b_revalidation__mutmut_103(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
        f"Average Coherence:        {avg_coherence:.3f} {'XX✅XX' if avg_coherence >= 0.650 else '❌'} (target ≥ 0.650)"
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


def x_run_exp1b_revalidation__mutmut_104(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
        f"Average Coherence:        {avg_coherence:.3f} {'✅' if avg_coherence > 0.650 else '❌'} (target ≥ 0.650)"
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


def x_run_exp1b_revalidation__mutmut_105(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
        f"Average Coherence:        {avg_coherence:.3f} {'✅' if avg_coherence >= 1.65 else '❌'} (target ≥ 0.650)"
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


def x_run_exp1b_revalidation__mutmut_106(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
        f"Average Coherence:        {avg_coherence:.3f} {'✅' if avg_coherence >= 0.650 else 'XX❌XX'} (target ≥ 0.650)"
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


def x_run_exp1b_revalidation__mutmut_107(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
    print(f"Error Rate:               {error_rate:.1%}")
    print(f"Classical Baseline:       {classical_baseline_ms:.2f}ms")
    print(f"Total Scenarios:          {len(scenario_data)}")
    print("\nScenario Statistics:")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_108(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
    print(f"Classical Baseline:       {classical_baseline_ms:.2f}ms")
    print(f"Total Scenarios:          {len(scenario_data)}")
    print("\nScenario Statistics:")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_109(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
    print(f"Total Scenarios:          {len(scenario_data)}")
    print("\nScenario Statistics:")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_110(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
    print("\nScenario Statistics:")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_111(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_112(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("XX\nScenario Statistics:XX")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_113(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\nscenario statistics:")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_114(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("\nSCENARIO STATISTICS:")
    print(f"  - Avg Ambiguity:        {scenario_stats['avg_ambiguity']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_115(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_116(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(f"  - Avg Ambiguity:        {scenario_stats['XXavg_ambiguityXX']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_117(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(f"  - Avg Ambiguity:        {scenario_stats['AVG_AMBIGUITY']:.3f}")
    print(f"  - Avg Conflicts:        {scenario_stats['avg_conflicting_signals']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_118(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_119(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(f"  - Avg Conflicts:        {scenario_stats['XXavg_conflicting_signalsXX']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_120(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(f"  - Avg Conflicts:        {scenario_stats['AVG_CONFLICTING_SIGNALS']:.2f}")
    print(f"  - Avg Rule Coverage:    {scenario_stats['avg_rule_coverage']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_121(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)
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


def x_run_exp1b_revalidation__mutmut_122(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(f"  - Avg Rule Coverage:    {scenario_stats['XXavg_rule_coverageXX']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_123(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(f"  - Avg Rule Coverage:    {scenario_stats['AVG_RULE_COVERAGE']:.3f}")
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


def x_run_exp1b_revalidation__mutmut_124(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print(None)

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


def x_run_exp1b_revalidation__mutmut_125(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("=" / 60)

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


def x_run_exp1b_revalidation__mutmut_126(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("XX=XX" * 60)

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


def x_run_exp1b_revalidation__mutmut_127(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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
    print("=" * 61)

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


def x_run_exp1b_revalidation__mutmut_128(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=None,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_129(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=None,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_130(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=None,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_131(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=None,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_132(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=None,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_133(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=None,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_134(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=None,
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_135(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=None,
    )


def x_run_exp1b_revalidation__mutmut_136(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_137(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_138(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_139(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_140(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_141(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        total_scenarios=len(scenario_data),
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_142(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        scenario_stats=scenario_stats,
    )


def x_run_exp1b_revalidation__mutmut_143(scenarios: int = 100, seed: int = 42) -> EXP1BResults:
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

    return EXP1BResults(
        k1=k1,
        accuracy=accuracy,
        coherence=avg_coherence,
        avg_time_ms=avg_time_ms,
        error_rate=error_rate,
        classical_baseline_ms=classical_baseline_ms,
        total_scenarios=len(scenario_data),
        )

x_run_exp1b_revalidation__mutmut_mutants : ClassVar[MutantDict] = {
'x_run_exp1b_revalidation__mutmut_1': x_run_exp1b_revalidation__mutmut_1, 
    'x_run_exp1b_revalidation__mutmut_2': x_run_exp1b_revalidation__mutmut_2, 
    'x_run_exp1b_revalidation__mutmut_3': x_run_exp1b_revalidation__mutmut_3, 
    'x_run_exp1b_revalidation__mutmut_4': x_run_exp1b_revalidation__mutmut_4, 
    'x_run_exp1b_revalidation__mutmut_5': x_run_exp1b_revalidation__mutmut_5, 
    'x_run_exp1b_revalidation__mutmut_6': x_run_exp1b_revalidation__mutmut_6, 
    'x_run_exp1b_revalidation__mutmut_7': x_run_exp1b_revalidation__mutmut_7, 
    'x_run_exp1b_revalidation__mutmut_8': x_run_exp1b_revalidation__mutmut_8, 
    'x_run_exp1b_revalidation__mutmut_9': x_run_exp1b_revalidation__mutmut_9, 
    'x_run_exp1b_revalidation__mutmut_10': x_run_exp1b_revalidation__mutmut_10, 
    'x_run_exp1b_revalidation__mutmut_11': x_run_exp1b_revalidation__mutmut_11, 
    'x_run_exp1b_revalidation__mutmut_12': x_run_exp1b_revalidation__mutmut_12, 
    'x_run_exp1b_revalidation__mutmut_13': x_run_exp1b_revalidation__mutmut_13, 
    'x_run_exp1b_revalidation__mutmut_14': x_run_exp1b_revalidation__mutmut_14, 
    'x_run_exp1b_revalidation__mutmut_15': x_run_exp1b_revalidation__mutmut_15, 
    'x_run_exp1b_revalidation__mutmut_16': x_run_exp1b_revalidation__mutmut_16, 
    'x_run_exp1b_revalidation__mutmut_17': x_run_exp1b_revalidation__mutmut_17, 
    'x_run_exp1b_revalidation__mutmut_18': x_run_exp1b_revalidation__mutmut_18, 
    'x_run_exp1b_revalidation__mutmut_19': x_run_exp1b_revalidation__mutmut_19, 
    'x_run_exp1b_revalidation__mutmut_20': x_run_exp1b_revalidation__mutmut_20, 
    'x_run_exp1b_revalidation__mutmut_21': x_run_exp1b_revalidation__mutmut_21, 
    'x_run_exp1b_revalidation__mutmut_22': x_run_exp1b_revalidation__mutmut_22, 
    'x_run_exp1b_revalidation__mutmut_23': x_run_exp1b_revalidation__mutmut_23, 
    'x_run_exp1b_revalidation__mutmut_24': x_run_exp1b_revalidation__mutmut_24, 
    'x_run_exp1b_revalidation__mutmut_25': x_run_exp1b_revalidation__mutmut_25, 
    'x_run_exp1b_revalidation__mutmut_26': x_run_exp1b_revalidation__mutmut_26, 
    'x_run_exp1b_revalidation__mutmut_27': x_run_exp1b_revalidation__mutmut_27, 
    'x_run_exp1b_revalidation__mutmut_28': x_run_exp1b_revalidation__mutmut_28, 
    'x_run_exp1b_revalidation__mutmut_29': x_run_exp1b_revalidation__mutmut_29, 
    'x_run_exp1b_revalidation__mutmut_30': x_run_exp1b_revalidation__mutmut_30, 
    'x_run_exp1b_revalidation__mutmut_31': x_run_exp1b_revalidation__mutmut_31, 
    'x_run_exp1b_revalidation__mutmut_32': x_run_exp1b_revalidation__mutmut_32, 
    'x_run_exp1b_revalidation__mutmut_33': x_run_exp1b_revalidation__mutmut_33, 
    'x_run_exp1b_revalidation__mutmut_34': x_run_exp1b_revalidation__mutmut_34, 
    'x_run_exp1b_revalidation__mutmut_35': x_run_exp1b_revalidation__mutmut_35, 
    'x_run_exp1b_revalidation__mutmut_36': x_run_exp1b_revalidation__mutmut_36, 
    'x_run_exp1b_revalidation__mutmut_37': x_run_exp1b_revalidation__mutmut_37, 
    'x_run_exp1b_revalidation__mutmut_38': x_run_exp1b_revalidation__mutmut_38, 
    'x_run_exp1b_revalidation__mutmut_39': x_run_exp1b_revalidation__mutmut_39, 
    'x_run_exp1b_revalidation__mutmut_40': x_run_exp1b_revalidation__mutmut_40, 
    'x_run_exp1b_revalidation__mutmut_41': x_run_exp1b_revalidation__mutmut_41, 
    'x_run_exp1b_revalidation__mutmut_42': x_run_exp1b_revalidation__mutmut_42, 
    'x_run_exp1b_revalidation__mutmut_43': x_run_exp1b_revalidation__mutmut_43, 
    'x_run_exp1b_revalidation__mutmut_44': x_run_exp1b_revalidation__mutmut_44, 
    'x_run_exp1b_revalidation__mutmut_45': x_run_exp1b_revalidation__mutmut_45, 
    'x_run_exp1b_revalidation__mutmut_46': x_run_exp1b_revalidation__mutmut_46, 
    'x_run_exp1b_revalidation__mutmut_47': x_run_exp1b_revalidation__mutmut_47, 
    'x_run_exp1b_revalidation__mutmut_48': x_run_exp1b_revalidation__mutmut_48, 
    'x_run_exp1b_revalidation__mutmut_49': x_run_exp1b_revalidation__mutmut_49, 
    'x_run_exp1b_revalidation__mutmut_50': x_run_exp1b_revalidation__mutmut_50, 
    'x_run_exp1b_revalidation__mutmut_51': x_run_exp1b_revalidation__mutmut_51, 
    'x_run_exp1b_revalidation__mutmut_52': x_run_exp1b_revalidation__mutmut_52, 
    'x_run_exp1b_revalidation__mutmut_53': x_run_exp1b_revalidation__mutmut_53, 
    'x_run_exp1b_revalidation__mutmut_54': x_run_exp1b_revalidation__mutmut_54, 
    'x_run_exp1b_revalidation__mutmut_55': x_run_exp1b_revalidation__mutmut_55, 
    'x_run_exp1b_revalidation__mutmut_56': x_run_exp1b_revalidation__mutmut_56, 
    'x_run_exp1b_revalidation__mutmut_57': x_run_exp1b_revalidation__mutmut_57, 
    'x_run_exp1b_revalidation__mutmut_58': x_run_exp1b_revalidation__mutmut_58, 
    'x_run_exp1b_revalidation__mutmut_59': x_run_exp1b_revalidation__mutmut_59, 
    'x_run_exp1b_revalidation__mutmut_60': x_run_exp1b_revalidation__mutmut_60, 
    'x_run_exp1b_revalidation__mutmut_61': x_run_exp1b_revalidation__mutmut_61, 
    'x_run_exp1b_revalidation__mutmut_62': x_run_exp1b_revalidation__mutmut_62, 
    'x_run_exp1b_revalidation__mutmut_63': x_run_exp1b_revalidation__mutmut_63, 
    'x_run_exp1b_revalidation__mutmut_64': x_run_exp1b_revalidation__mutmut_64, 
    'x_run_exp1b_revalidation__mutmut_65': x_run_exp1b_revalidation__mutmut_65, 
    'x_run_exp1b_revalidation__mutmut_66': x_run_exp1b_revalidation__mutmut_66, 
    'x_run_exp1b_revalidation__mutmut_67': x_run_exp1b_revalidation__mutmut_67, 
    'x_run_exp1b_revalidation__mutmut_68': x_run_exp1b_revalidation__mutmut_68, 
    'x_run_exp1b_revalidation__mutmut_69': x_run_exp1b_revalidation__mutmut_69, 
    'x_run_exp1b_revalidation__mutmut_70': x_run_exp1b_revalidation__mutmut_70, 
    'x_run_exp1b_revalidation__mutmut_71': x_run_exp1b_revalidation__mutmut_71, 
    'x_run_exp1b_revalidation__mutmut_72': x_run_exp1b_revalidation__mutmut_72, 
    'x_run_exp1b_revalidation__mutmut_73': x_run_exp1b_revalidation__mutmut_73, 
    'x_run_exp1b_revalidation__mutmut_74': x_run_exp1b_revalidation__mutmut_74, 
    'x_run_exp1b_revalidation__mutmut_75': x_run_exp1b_revalidation__mutmut_75, 
    'x_run_exp1b_revalidation__mutmut_76': x_run_exp1b_revalidation__mutmut_76, 
    'x_run_exp1b_revalidation__mutmut_77': x_run_exp1b_revalidation__mutmut_77, 
    'x_run_exp1b_revalidation__mutmut_78': x_run_exp1b_revalidation__mutmut_78, 
    'x_run_exp1b_revalidation__mutmut_79': x_run_exp1b_revalidation__mutmut_79, 
    'x_run_exp1b_revalidation__mutmut_80': x_run_exp1b_revalidation__mutmut_80, 
    'x_run_exp1b_revalidation__mutmut_81': x_run_exp1b_revalidation__mutmut_81, 
    'x_run_exp1b_revalidation__mutmut_82': x_run_exp1b_revalidation__mutmut_82, 
    'x_run_exp1b_revalidation__mutmut_83': x_run_exp1b_revalidation__mutmut_83, 
    'x_run_exp1b_revalidation__mutmut_84': x_run_exp1b_revalidation__mutmut_84, 
    'x_run_exp1b_revalidation__mutmut_85': x_run_exp1b_revalidation__mutmut_85, 
    'x_run_exp1b_revalidation__mutmut_86': x_run_exp1b_revalidation__mutmut_86, 
    'x_run_exp1b_revalidation__mutmut_87': x_run_exp1b_revalidation__mutmut_87, 
    'x_run_exp1b_revalidation__mutmut_88': x_run_exp1b_revalidation__mutmut_88, 
    'x_run_exp1b_revalidation__mutmut_89': x_run_exp1b_revalidation__mutmut_89, 
    'x_run_exp1b_revalidation__mutmut_90': x_run_exp1b_revalidation__mutmut_90, 
    'x_run_exp1b_revalidation__mutmut_91': x_run_exp1b_revalidation__mutmut_91, 
    'x_run_exp1b_revalidation__mutmut_92': x_run_exp1b_revalidation__mutmut_92, 
    'x_run_exp1b_revalidation__mutmut_93': x_run_exp1b_revalidation__mutmut_93, 
    'x_run_exp1b_revalidation__mutmut_94': x_run_exp1b_revalidation__mutmut_94, 
    'x_run_exp1b_revalidation__mutmut_95': x_run_exp1b_revalidation__mutmut_95, 
    'x_run_exp1b_revalidation__mutmut_96': x_run_exp1b_revalidation__mutmut_96, 
    'x_run_exp1b_revalidation__mutmut_97': x_run_exp1b_revalidation__mutmut_97, 
    'x_run_exp1b_revalidation__mutmut_98': x_run_exp1b_revalidation__mutmut_98, 
    'x_run_exp1b_revalidation__mutmut_99': x_run_exp1b_revalidation__mutmut_99, 
    'x_run_exp1b_revalidation__mutmut_100': x_run_exp1b_revalidation__mutmut_100, 
    'x_run_exp1b_revalidation__mutmut_101': x_run_exp1b_revalidation__mutmut_101, 
    'x_run_exp1b_revalidation__mutmut_102': x_run_exp1b_revalidation__mutmut_102, 
    'x_run_exp1b_revalidation__mutmut_103': x_run_exp1b_revalidation__mutmut_103, 
    'x_run_exp1b_revalidation__mutmut_104': x_run_exp1b_revalidation__mutmut_104, 
    'x_run_exp1b_revalidation__mutmut_105': x_run_exp1b_revalidation__mutmut_105, 
    'x_run_exp1b_revalidation__mutmut_106': x_run_exp1b_revalidation__mutmut_106, 
    'x_run_exp1b_revalidation__mutmut_107': x_run_exp1b_revalidation__mutmut_107, 
    'x_run_exp1b_revalidation__mutmut_108': x_run_exp1b_revalidation__mutmut_108, 
    'x_run_exp1b_revalidation__mutmut_109': x_run_exp1b_revalidation__mutmut_109, 
    'x_run_exp1b_revalidation__mutmut_110': x_run_exp1b_revalidation__mutmut_110, 
    'x_run_exp1b_revalidation__mutmut_111': x_run_exp1b_revalidation__mutmut_111, 
    'x_run_exp1b_revalidation__mutmut_112': x_run_exp1b_revalidation__mutmut_112, 
    'x_run_exp1b_revalidation__mutmut_113': x_run_exp1b_revalidation__mutmut_113, 
    'x_run_exp1b_revalidation__mutmut_114': x_run_exp1b_revalidation__mutmut_114, 
    'x_run_exp1b_revalidation__mutmut_115': x_run_exp1b_revalidation__mutmut_115, 
    'x_run_exp1b_revalidation__mutmut_116': x_run_exp1b_revalidation__mutmut_116, 
    'x_run_exp1b_revalidation__mutmut_117': x_run_exp1b_revalidation__mutmut_117, 
    'x_run_exp1b_revalidation__mutmut_118': x_run_exp1b_revalidation__mutmut_118, 
    'x_run_exp1b_revalidation__mutmut_119': x_run_exp1b_revalidation__mutmut_119, 
    'x_run_exp1b_revalidation__mutmut_120': x_run_exp1b_revalidation__mutmut_120, 
    'x_run_exp1b_revalidation__mutmut_121': x_run_exp1b_revalidation__mutmut_121, 
    'x_run_exp1b_revalidation__mutmut_122': x_run_exp1b_revalidation__mutmut_122, 
    'x_run_exp1b_revalidation__mutmut_123': x_run_exp1b_revalidation__mutmut_123, 
    'x_run_exp1b_revalidation__mutmut_124': x_run_exp1b_revalidation__mutmut_124, 
    'x_run_exp1b_revalidation__mutmut_125': x_run_exp1b_revalidation__mutmut_125, 
    'x_run_exp1b_revalidation__mutmut_126': x_run_exp1b_revalidation__mutmut_126, 
    'x_run_exp1b_revalidation__mutmut_127': x_run_exp1b_revalidation__mutmut_127, 
    'x_run_exp1b_revalidation__mutmut_128': x_run_exp1b_revalidation__mutmut_128, 
    'x_run_exp1b_revalidation__mutmut_129': x_run_exp1b_revalidation__mutmut_129, 
    'x_run_exp1b_revalidation__mutmut_130': x_run_exp1b_revalidation__mutmut_130, 
    'x_run_exp1b_revalidation__mutmut_131': x_run_exp1b_revalidation__mutmut_131, 
    'x_run_exp1b_revalidation__mutmut_132': x_run_exp1b_revalidation__mutmut_132, 
    'x_run_exp1b_revalidation__mutmut_133': x_run_exp1b_revalidation__mutmut_133, 
    'x_run_exp1b_revalidation__mutmut_134': x_run_exp1b_revalidation__mutmut_134, 
    'x_run_exp1b_revalidation__mutmut_135': x_run_exp1b_revalidation__mutmut_135, 
    'x_run_exp1b_revalidation__mutmut_136': x_run_exp1b_revalidation__mutmut_136, 
    'x_run_exp1b_revalidation__mutmut_137': x_run_exp1b_revalidation__mutmut_137, 
    'x_run_exp1b_revalidation__mutmut_138': x_run_exp1b_revalidation__mutmut_138, 
    'x_run_exp1b_revalidation__mutmut_139': x_run_exp1b_revalidation__mutmut_139, 
    'x_run_exp1b_revalidation__mutmut_140': x_run_exp1b_revalidation__mutmut_140, 
    'x_run_exp1b_revalidation__mutmut_141': x_run_exp1b_revalidation__mutmut_141, 
    'x_run_exp1b_revalidation__mutmut_142': x_run_exp1b_revalidation__mutmut_142, 
    'x_run_exp1b_revalidation__mutmut_143': x_run_exp1b_revalidation__mutmut_143
}

def run_exp1b_revalidation(*args, **kwargs):
    result = _mutmut_trampoline(x_run_exp1b_revalidation__mutmut_orig, x_run_exp1b_revalidation__mutmut_mutants, args, kwargs)
    return result 

run_exp1b_revalidation.__signature__ = _mutmut_signature(x_run_exp1b_revalidation__mutmut_orig)
x_run_exp1b_revalidation__mutmut_orig.__name__ = 'x_run_exp1b_revalidation'


def x__classical_assessment__mutmut_orig(audit: AuditResult) -> ComplianceDecision:
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


def x__classical_assessment__mutmut_1(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 or audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_2(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score > 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_3(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 1.9 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_4(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level != "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_5(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "XXlowXX":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_6(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "LOW":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_7(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score > 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_8(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 1.7:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_9(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 or audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_10(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score > 0.50 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_11(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 1.5 and audit.remediation_cost < 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_12(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost <= 5000:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT


def x__classical_assessment__mutmut_13(audit: AuditResult) -> ComplianceDecision:
    """
    Simple rule-based classical assessment (baseline).

    Uses straightforward thresholds without quantum superposition or adaptive scoring.
    """
    # Simple rule-based logic
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE
    elif audit.score >= 0.70:
        return ComplianceDecision.APPROVE_WITH_MONITORING
    elif audit.score >= 0.50 and audit.remediation_cost < 5001:
        return ComplianceDecision.CONDITIONAL_APPROVAL
    else:
        return ComplianceDecision.REJECT

x__classical_assessment__mutmut_mutants : ClassVar[MutantDict] = {
'x__classical_assessment__mutmut_1': x__classical_assessment__mutmut_1, 
    'x__classical_assessment__mutmut_2': x__classical_assessment__mutmut_2, 
    'x__classical_assessment__mutmut_3': x__classical_assessment__mutmut_3, 
    'x__classical_assessment__mutmut_4': x__classical_assessment__mutmut_4, 
    'x__classical_assessment__mutmut_5': x__classical_assessment__mutmut_5, 
    'x__classical_assessment__mutmut_6': x__classical_assessment__mutmut_6, 
    'x__classical_assessment__mutmut_7': x__classical_assessment__mutmut_7, 
    'x__classical_assessment__mutmut_8': x__classical_assessment__mutmut_8, 
    'x__classical_assessment__mutmut_9': x__classical_assessment__mutmut_9, 
    'x__classical_assessment__mutmut_10': x__classical_assessment__mutmut_10, 
    'x__classical_assessment__mutmut_11': x__classical_assessment__mutmut_11, 
    'x__classical_assessment__mutmut_12': x__classical_assessment__mutmut_12, 
    'x__classical_assessment__mutmut_13': x__classical_assessment__mutmut_13
}

def _classical_assessment(*args, **kwargs):
    result = _mutmut_trampoline(x__classical_assessment__mutmut_orig, x__classical_assessment__mutmut_mutants, args, kwargs)
    return result 

_classical_assessment.__signature__ = _mutmut_signature(x__classical_assessment__mutmut_orig)
x__classical_assessment__mutmut_orig.__name__ = 'x__classical_assessment'


def x_calculate_k1__mutmut_orig(
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


def x_calculate_k1__mutmut_1(
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
    return (avg_time_ms * (1.0 + error_rate)) * classical_baseline_ms


def x_calculate_k1__mutmut_2(
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
    return (avg_time_ms / (1.0 + error_rate)) / classical_baseline_ms


def x_calculate_k1__mutmut_3(
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
    return (avg_time_ms * (1.0 - error_rate)) / classical_baseline_ms


def x_calculate_k1__mutmut_4(
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
    return (avg_time_ms * (2.0 + error_rate)) / classical_baseline_ms

x_calculate_k1__mutmut_mutants : ClassVar[MutantDict] = {
'x_calculate_k1__mutmut_1': x_calculate_k1__mutmut_1, 
    'x_calculate_k1__mutmut_2': x_calculate_k1__mutmut_2, 
    'x_calculate_k1__mutmut_3': x_calculate_k1__mutmut_3, 
    'x_calculate_k1__mutmut_4': x_calculate_k1__mutmut_4
}

def calculate_k1(*args, **kwargs):
    result = _mutmut_trampoline(x_calculate_k1__mutmut_orig, x_calculate_k1__mutmut_mutants, args, kwargs)
    return result 

calculate_k1.__signature__ = _mutmut_signature(x_calculate_k1__mutmut_orig)
x_calculate_k1__mutmut_orig.__name__ = 'x_calculate_k1'


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
