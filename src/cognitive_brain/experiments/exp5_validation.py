"""
EXP-5 Validation: Quantum Memory Management Performance

Validates Phase 8.1 memory management implementation against targets:
- Cache hit rate > 30%
- Time reduction ≥ 15%
- Accuracy vs full assessment ≥ 95%
- k₁ improvement: 0.35 → 0.345 (1.4% reduction)

PDA Loop + AfterMath:
- PLAN: Define experiment with memory vs non-memory baselines
- DO: Run 200 assessments with memory enabled
- ASSESS: Calculate cache hit rate, time savings, accuracy
- AfterMath: Validate k₁ reduction, document improvements

Hypothesis:
Memory-guided decisions reduce computation time by 15% while maintaining
95%+ accuracy relative to full quantum assessment.
"""

import time
import numpy as np
import logging
from typing import Dict
from dataclasses import dataclass

from cognitive_brain.experiments.complex_scenarios import (
    generate_complex_scenarios,
    get_scenario_statistics
)
from cognitive_brain.integrations.memory_integration import (
    MemoryAugmentedComplianceAssessor
)
from cognitive_brain.integrations.compliance_integration import (
    QuantumComplianceAssessor
)
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor


# Configure logging
logger = logging.getLogger(__name__)


# Constants from previous phases
CLASSICAL_BASELINE_MS = 28.5  # Classical assessment baseline from EXP-1B (Phase 8.0)
PHASE_8_0_ERROR_RATE = 0.136  # Phase 8.0 error rate (1 - 0.864 accuracy)
DEFAULT_SCENARIOS = 200  # Default number of scenarios for validation
DEFAULT_SEED = 42  # Default random seed for reproducibility


@dataclass
class EXP5Results:
    """Results from EXP-5 validation experiment"""
    k1_with_memory: float
    k1_without_memory: float
    k1_improvement_pct: float
    cache_hit_rate: float
    time_reduction_pct: float
    accuracy_vs_full: float
    avg_time_with_memory_ms: float
    avg_time_without_memory_ms: float
    total_scenarios: int
    memory_stats: Dict


def run_exp5_validation(scenarios: int = 200, seed: int = 42) -> EXP5Results:
    """
    Run EXP-5 validation for memory management performance.
    
    Compares memory-augmented assessor against baseline (no memory) to measure:
    1. Cache hit rate (target: > 30%)
    2. Time reduction (target: ≥ 15%)
    3. Accuracy (target: ≥ 95% agreement with full assessment)
    4. k₁ impact (target: 0.35 → 0.345)
    
    Args:
        scenarios: Number of scenarios to test (default: 200)
        seed: Random seed for reproducibility (default: 42)
    
    Returns:
        EXP5Results with all validation metrics
    """
    print(f"="*70)
    print("EXP-5: Quantum Memory Management Validation")
    print(f"="*70)
    print(f"Scenarios: {scenarios} | Seed: {seed}")
    print()
    
    # Generate test scenarios
    print("Generating complex scenarios...")
    scenario_data = generate_complex_scenarios(count=scenarios, seed=seed)
    scenario_stats = get_scenario_statistics(scenario_data)
    print(f"✓ Generated {len(scenario_data)} scenarios")
    print(f"  Avg ambiguity: {scenario_stats['avg_ambiguity']:.3f}")
    print()
    
    # Initialize components
    config = QuantumConfig()
    config.quantum_mode = True
    config.superposition = True
    
    # Mock repository
    class MockRepo:
        def store_quantum_metric(self, *args, **kwargs):
            pass
    
    repository = MockRepo()
    monitor = CoherenceMonitor(config, repository)
    
    # Create assessors
    print("Initializing assessors...")
    memory_assessor = MemoryAugmentedComplianceAssessor(
        config=config,
        monitor=monitor,
        repository=repository,
        enable_memory=True
    )
    
    baseline_assessor = QuantumComplianceAssessor(
        config=config,
        monitor=monitor,
        repository=repository
    )
    print("✓ Assessors initialized")
    print()
    
    # Run memory-augmented assessments
    print("Running memory-augmented assessments...")
    memory_times = []
    memory_decisions = []
    
    for i, (audit, ground_truth, complexity) in enumerate(scenario_data):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(scenario_data)}")
        
        start_time = time.time()
        assessment = memory_assessor.assess_with_memory(audit)
        elapsed_ms = (time.time() - start_time) * 1000
        
        memory_times.append(elapsed_ms)
        memory_decisions.append(assessment.decision)
    
    print(f"✓ Completed {len(scenario_data)} memory-augmented assessments")
    print()
    
    # Run baseline assessments (no memory)
    print("Running baseline assessments (no memory)...")
    baseline_times = []
    baseline_decisions = []
    
    for i, (audit, ground_truth, complexity) in enumerate(scenario_data):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(scenario_data)}")
        
        start_time = time.time()
        assessment = baseline_assessor.assess_compliance(audit)
        elapsed_ms = (time.time() - start_time) * 1000
        
        baseline_times.append(elapsed_ms)
        baseline_decisions.append(assessment.decision)
    
    print(f"✓ Completed {len(scenario_data)} baseline assessments")
    print()
    
    # Calculate metrics
    print("Calculating metrics...")
    
    # Time metrics
    avg_time_memory = np.mean(memory_times)
    avg_time_baseline = np.mean(baseline_times)
    time_reduction_pct = (avg_time_baseline - avg_time_memory) / avg_time_baseline
    
    # Accuracy (memory vs baseline)
    # Note: This measures consistency between memory and baseline decisions,
    # not absolute accuracy against ground truth. Both could be wrong together.
    # For true accuracy, compare against ground_truth from scenarios.
    agreements = sum(1 for m, b in zip(memory_decisions, baseline_decisions) if m == b)
    accuracy = agreements / len(memory_decisions)
    
    # For k₁ calculation, we need error rate against ground truth
    # Calculate actual errors against ground truth
    memory_errors = sum(
        1 for (_, ground_truth, _), decision in zip(scenario_data, memory_decisions)
        if decision != ground_truth
    )
    actual_error_rate = memory_errors / len(scenario_data)
    
    # Cache hit rate
    memory_stats = memory_assessor.get_statistics()
    cache_hit_rate = memory_stats['cache_hit_rate']
    
    # k₁ calculation (using Phase 8.0 formula)
    # k₁ = (avg_time * (1 + error_rate)) / classical_baseline
    # Constants defined at module level
    
    k1_memory = (avg_time_memory * (1.0 + actual_error_rate)) / CLASSICAL_BASELINE_MS
    k1_baseline = (avg_time_baseline * (1.0 + PHASE_8_0_ERROR_RATE)) / CLASSICAL_BASELINE_MS
    k1_improvement_pct = ((k1_baseline - k1_memory) / k1_baseline) * 100
    
    print("✓ Metrics calculated")
    print()
    
    # Print results
    print("="*70)
    print("EXP-5 Results: Quantum Memory Management")
    print("="*70)
    print()
    print("Time Performance:")
    print(f"  Avg time (with memory):    {avg_time_memory:.2f}ms")
    print(f"  Avg time (baseline):       {avg_time_baseline:.2f}ms")
    print(f"  Time reduction:            {time_reduction_pct:.1%} {'✅' if time_reduction_pct >= 0.15 else '❌'} (target ≥ 15%)")
    print()
    print("Memory Performance:")
    print(f"  Cache hit rate:            {cache_hit_rate:.1%} {'✅' if cache_hit_rate >= 0.30 else '❌'} (target > 30%)")
    print(f"  Cache hits:                {memory_stats['cache_hits']}")
    print(f"  Cache misses:              {memory_stats['cache_misses']}")
    print()
    print("Accuracy:")
    print(f"  Memory vs Baseline:        {accuracy:.1%} {'✅' if accuracy >= 0.95 else '❌'} (target ≥ 95%)")
    print(f"  Agreements:                {agreements}/{len(memory_decisions)}")
    print()
    print("k₁ Optimization:")
    print(f"  k₁ (with memory):          {k1_memory:.4f} {'✅' if k1_memory <= 0.345 else '❌'} (target ≤ 0.345)")
    print(f"  k₁ (baseline):             {k1_baseline:.4f}")
    print(f"  k₁ improvement:            {k1_improvement_pct:.2f}%")
    print()
    print("Memory System Stats:")
    print(f"  STM size:                  {memory_stats['stm_size']}/{memory_stats['stm_capacity']}")
    print(f"  LTM size:                  {memory_stats['ltm_size']}/{memory_stats['ltm_capacity']}")
    print(f"  Patterns stored:           {memory_stats['total_stored']}")
    print(f"  Patterns consolidated:     {memory_stats['total_consolidated']}")
    print(f"  Consolidation rate:        {memory_stats['consolidation_rate']:.1%}")
    print()
    print("="*70)
    
    # Validate success criteria
    success = (
        k1_memory <= 0.345 and
        cache_hit_rate >= 0.30 and
        time_reduction_pct >= 0.15 and
        accuracy >= 0.95
    )
    
    if success:
        print("✅ Phase 8.1 SUCCESS: All criteria met!")
        print(f"   k₁={k1_memory:.4f} (target ≤ 0.345)")
        print(f"   Cache hit rate={cache_hit_rate:.1%} (target > 30%)")
        print(f"   Time reduction={time_reduction_pct:.1%} (target ≥ 15%)")
        print(f"   Accuracy={accuracy:.1%} (target ≥ 95%)")
    else:
        print("⚠️  Phase 8.1 INCOMPLETE: Some criteria not met")
        if k1_memory > 0.345:
            print(f"   ❌ k₁={k1_memory:.4f} (need ≤ 0.345)")
        if cache_hit_rate < 0.30:
            print(f"   ❌ cache_hit_rate={cache_hit_rate:.1%} (need > 30%)")
        if time_reduction_pct < 0.15:
            print(f"   ❌ time_reduction={time_reduction_pct:.1%} (need ≥ 15%)")
        if accuracy < 0.95:
            print(f"   ❌ accuracy={accuracy:.1%} (need ≥ 95%)")
    
    print("="*70)
    
    return EXP5Results(
        k1_with_memory=k1_memory,
        k1_without_memory=k1_baseline,
        k1_improvement_pct=k1_improvement_pct,
        cache_hit_rate=cache_hit_rate,
        time_reduction_pct=time_reduction_pct,
        accuracy_vs_full=accuracy,
        avg_time_with_memory_ms=avg_time_memory,
        avg_time_without_memory_ms=avg_time_baseline,
        total_scenarios=len(scenario_data),
        memory_stats=memory_stats
    )


if __name__ == "__main__":
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run EXP-5 validation experiment")
    parser.add_argument(
        "--scenarios",
        type=int,
        default=DEFAULT_SCENARIOS,
        help=f"Number of scenarios to generate (default: {DEFAULT_SCENARIOS})"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed for reproducibility (default: {DEFAULT_SEED})"
    )
    args = parser.parse_args()
    
    # Run EXP-5 validation with configurable parameters
    results = run_exp5_validation(scenarios=args.scenarios, seed=args.seed)
    
    # Summary
    print()
    print("EXP-5 Complete. Key findings:")
    print(f"- k₁ improved from {results.k1_without_memory:.4f} to {results.k1_with_memory:.4f}")
    print(f"- Cache hit rate: {results.cache_hit_rate:.1%}")
    print(f"- Time savings: {results.time_reduction_pct:.1%}")
    print(f"- Accuracy maintained: {results.accuracy_vs_full:.1%}")
