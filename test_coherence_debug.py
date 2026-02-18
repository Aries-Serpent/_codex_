"""
Minimal test to debug coherence calculation issue
"""

from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceAssessor,
)
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig

# Create test configuration
config = QuantumConfig.from_env()
config.quantum_mode = True
config.superposition = True

# Initialize components
repository = QuantumMetricRepository(db_path=":memory:")
monitor = CoherenceMonitor(config, repository)
assessor = ComplianceAssessor(config, monitor, repository, enable_superposition=True)

# Create a simple audit
audit = AuditResult(
    audit_id="test-001",
    score=0.85,
    risk_level="low",
    remediation_cost=500.0,
    business_impact=0.7
)

print("Running compliance assessment...")
assessment = assessor.assess_compliance(audit)

print(f"\nResults:")
print(f"  Decision: {assessment.decision}")
print(f"  Confidence: {assessment.confidence:.3f}")
print(f"  Coherence: {assessment.coherence:.3f}")
print(f"  Used Superposition: {assessment.used_superposition}")
print(f"  Evaluation Time: {assessment.evaluation_time_ms:.2f}ms")

if assessment.coherence == 0.0:
    print("\n🚨 BUG CONFIRMED: Coherence is zero!")
    print("\nDebugging superposition engine...")
    
    # Test the engine directly
    from cognitive_brain.quantum.superposition import Decision, SuperpositionEngine
    
    engine = SuperpositionEngine(config, monitor)
    
    # Create test decisions
    decisions = [
        Decision(id="D1", name="Test1", evaluation_fn=lambda: 0.9),
        Decision(id="D2", name="Test2", evaluation_fn=lambda: 0.7),
        Decision(id="D3", name="Test3", evaluation_fn=lambda: 0.5),
    ]
    
    state = engine.create_superposition(decisions)
    print(f"\n  State created - coherence: {state.coherence}")
    
    probabilities = engine.evaluate_parallel(state)
    print(f"  After evaluation - coherence: {state.coherence}")
    print(f"  Probabilities: {probabilities}")
    
    coherence = engine.get_coherence(state)
    print(f"  get_coherence() returns: {coherence}")
    
else:
    print(f"\n✅ Coherence is working: {assessment.coherence:.3f}")
