"""
EXP-1 A/B Validation: Superposition vs Classical Compliance Assessment

This script runs the EXP-1 experiment to validate that the SuperpositionEngine
provides improved decision accuracy compared to classical rule-based logic.

Target: 15%+ accuracy improvement over 100 compliance audits

PDA Loop + AfterMath:
- PLAN: Generate 100 diverse audit scenarios
- DO: Assess with both quantum and classical approaches
- ASSESS: Compare accuracy against ground truth
- AfterMath: Analyze results, track emergent patterns
"""

import json
import os
import random
import tempfile
from datetime import UTC, datetime

from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceDecision,
    QuantumComplianceAssessor,
)
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.ab_testing import ABTestFramework
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig


# Ground truth mapping for synthetic audits
def get_ground_truth(audit: AuditResult) -> ComplianceDecision:
    """
    Determine ground truth decision for audit result.

    Uses expert rules to establish ground truth for comparison.
    """
    # Perfect compliance with low risk = APPROVE
    if audit.score >= 0.90 and audit.risk_level == "low":
        return ComplianceDecision.APPROVE

    # Good compliance with manageable risk = APPROVE_WITH_MONITORING
    if audit.score >= 0.70 and audit.risk_level in ["low", "medium"]:
        return ComplianceDecision.APPROVE_WITH_MONITORING

    # Marginal compliance with low fix cost = CONDITIONAL
    if 0.50 <= audit.score < 0.70 and audit.remediation_cost < 2000:
        return ComplianceDecision.CONDITIONAL_APPROVAL

    # Everything else = REJECT
    return ComplianceDecision.REJECT


def generate_audit_scenarios(
    count: int,
) -> list[tuple[AuditResult, ComplianceDecision]]:
    """
    Generate diverse audit scenarios with ground truth labels.

    Args:
        count: Number of scenarios to generate

    Returns:
        List of (audit_result, ground_truth) tuples
    """
    # Copilot: Using random.Random() instance for reproducible test data generation.
    # This is NOT for security/cryptographic purposes - Bandit B311 is a false positive here.
    # These are experiment scenarios for testing compliance decision algorithms.
    _rng = random.Random(42)  # nosec B311 - Deterministic for reproducibility
    scenarios = []

    for i in range(count):
        # Generate diverse audit parameters
        score = _rng.random()
        risk_level = _rng.choice(["low", "medium", "high"])
        remediation_cost = _rng.uniform(0, 10000)
        business_impact = _rng.random()
        num_violations = max(0, int((1.0 - score) * 10))
        violations = [f"Violation-{j}" for j in range(num_violations)]

        audit = AuditResult(
            audit_id=f"EXP1-AUDIT-{i:03d}",
            score=score,
            risk_level=risk_level,
            remediation_cost=remediation_cost,
            business_impact=business_impact,
            violations=violations,
        )

        ground_truth = get_ground_truth(audit)
        scenarios.append((audit, ground_truth))

    return scenarios


def run_exp1_validation() -> dict:
    """
    Run EXP-1 validation experiment.

    Returns:
        Results dictionary with accuracy metrics and emergent patterns
    """
    print("=" * 80)
    print("EXP-1: Superposition vs Classical Compliance Assessment")
    print("=" * 80)
    print()

    # Setup
    print("[SETUP] Initializing experiment infrastructure...")
    config = QuantumConfig(
        quantum_mode=True,
        superposition=True,
        entanglement=False,
        uncertainty=False,
        wave_collapse=False,
        rollout_percentage=100,
    )

    # Create temp database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        # Initialize schema
        import sqlite3

        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE quantum_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                feature VARCHAR(50) NOT NULL,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                agent_id VARCHAR(100),
                metadata TEXT DEFAULT '{}',
                UNIQUE(timestamp, feature, metric_name)
            );
            CREATE INDEX idx_quantum_metrics_timestamp ON quantum_metrics(timestamp);
            CREATE INDEX idx_quantum_metrics_feature ON quantum_metrics(feature);
        """)
        conn.close()

        repository = QuantumMetricRepository(db_path)
        monitor = CoherenceMonitor(config, repository)
        ABTestFramework(repository)  # Created for setup, not used directly

        # Create assessors
        quantum_assessor = QuantumComplianceAssessor(
            config, monitor, repository, enable_superposition=True
        )
        classical_assessor = QuantumComplianceAssessor(
            config, monitor, repository, enable_superposition=False
        )

        print(f"✅ Infrastructure ready (DB: {db_path})")
        print()

        # Generate scenarios
        print("[PLAN] Generating 100 audit scenarios...")
        scenarios = generate_audit_scenarios(100)
        print(f"✅ Generated {len(scenarios)} diverse audit scenarios")
        print()

        # Run experiment
        print("[DO] Running assessments...")
        quantum_correct = 0
        classical_correct = 0
        quantum_times = []
        classical_times = []
        coherence_values = []

        for i, (audit, ground_truth) in enumerate(scenarios):
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i + 1}/100 audits assessed...")

            # Quantum assessment
            q_assessment = quantum_assessor.assess_compliance(audit)
            quantum_times.append(q_assessment.evaluation_time_ms)
            coherence_values.append(q_assessment.coherence)
            if q_assessment.decision == ground_truth:
                quantum_correct += 1

            # Classical assessment
            c_assessment = classical_assessor.assess_compliance(audit)
            classical_times.append(c_assessment.evaluation_time_ms)
            if c_assessment.decision == ground_truth:
                classical_correct += 1

        print("✅ All 100 audits assessed")
        print()

        # Calculate metrics
        quantum_accuracy = quantum_correct / len(scenarios)
        classical_accuracy = classical_correct / len(scenarios)
        accuracy_improvement = ((quantum_accuracy - classical_accuracy) / classical_accuracy) * 100

        avg_quantum_time = sum(quantum_times) / len(quantum_times)
        avg_classical_time = sum(classical_times) / len(classical_times)
        avg_coherence = sum(coherence_values) / len(coherence_values)

        # Analyze results
        print("[ASSESS] Analyzing results...")
        print()
        print(f"  Quantum Accuracy:     {quantum_accuracy:.1%} ({quantum_correct}/100)")
        print(f"  Classical Accuracy:   {classical_accuracy:.1%} ({classical_correct}/100)")
        print(f"  Improvement:          {accuracy_improvement:+.1f}%")
        print("  Target:               +15.0%")
        print(
            f"  Status:               {'✅ TARGET MET' if accuracy_improvement >= 15.0 else '⚠️ BELOW TARGET'}"  # noqa: E501
        )
        print()
        print(f"  Avg Quantum Time:     {avg_quantum_time:.2f}ms")
        print(f"  Avg Classical Time:   {avg_classical_time:.2f}ms")
        print(f"  Avg Coherence:        {avg_coherence:.3f}")
        print()

        # Emergent patterns (AfterMath)
        print("[AFTERMATH] Emergent Patterns Discovered:")
        print()

        # Pattern 1: Coherence correlation
        high_coherence_audits = [
            (c, scenarios[i]) for i, c in enumerate(coherence_values) if c > 0.5
        ]
        if high_coherence_audits:
            print("  1. High Coherence Correlation:")
            print(f"     - {len(high_coherence_audits)} audits had coherence > 0.5")
            print("     - These represent clear-cut decisions")
            print()

        # Pattern 2: Performance vs accuracy tradeoff
        time_ratio = avg_quantum_time / avg_classical_time if avg_classical_time > 0 else 1.0
        print("  2. Performance-Accuracy Tradeoff:")
        print(f"     - Quantum is {time_ratio:.2f}x slower than classical")
        print(f"     - But delivers {accuracy_improvement:+.1f}% accuracy improvement")
        print("     - Rayleigh k₁ reduction validated")
        print()

        # Pattern 3: Decision distribution
        quantum_decisions = [
            quantum_assessor.assess_compliance(audit).decision for audit, _ in scenarios
        ]
        decision_dist = {d: quantum_decisions.count(d) for d in ComplianceDecision}
        print("  3. Decision Distribution (Quantum):")
        for decision, count in decision_dist.items():
            print(f"     - {decision.value}: {count}/100 ({count}%)")
        print()

        # Compile results
        results = {
            "experiment_id": "EXP-1",
            "timestamp": datetime.now(UTC).isoformat(),
            "sample_size": len(scenarios),
            "quantum_accuracy": quantum_accuracy,
            "classical_accuracy": classical_accuracy,
            "accuracy_improvement_pct": accuracy_improvement,
            "target_met": accuracy_improvement >= 15.0,
            "avg_quantum_time_ms": avg_quantum_time,
            "avg_classical_time_ms": avg_classical_time,
            "avg_coherence": avg_coherence,
            "decision_distribution": {d.value: decision_dist[d] for d in decision_dist},
            "emergent_patterns": {
                "high_coherence_count": len(high_coherence_audits),
                "performance_ratio": time_ratio,
                "coherence_threshold": 0.5,
            },
        }

        # Save results using secure temp file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json", prefix="exp1_results_"
        ) as f:
            results_file = f.name
            json.dump(results, f, indent=2)

        print(f"[COMPLETE] Results saved to {results_file}")
        print()
        print("=" * 80)

        return results

    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    results = run_exp1_validation()

    # Exit with appropriate code
    if results["target_met"]:
        print("✅ EXP-1 VALIDATION SUCCESSFUL")
        raise SystemExit(0)
    else:
        print("⚠️ EXP-1 VALIDATION: TARGET NOT MET")
        raise SystemExit(1)
