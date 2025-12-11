# Physics-Inspired AI Agent Orchestration

This document describes the physics-inspired orchestration system with mental mapping for AI agent decision-making in the Codex repository.

## Overview

The orchestration system combines:
1. **Physics-Inspired Decision Making** - Uses physics equations to weigh options
2. **Mental Mapping** - Stores reasoning chains for iterative review
3. **Self-Appraisal** - Learns from outcomes to improve future decisions

## Core Philosophy

**"Take time to think and weigh/assess the situation then action"**

The orchestrator follows a deliberate process:
- **ASSESS** → Gather information about current state
- **DELIBERATE** → Calculate physics properties for each option
- **OPTIMIZE** → Find the best path using optimization equations
- **ACT** → Execute with full commitment
- **REFLECT** → Review and learn from outcomes

## Physics-Inspired Equations

### 1. Total Energy Calculation

```python
E_total = E_potential + E_kinetic - E_momentum + E_friction

Where:
- E_potential: Effort required to complete action (0-100)
- E_kinetic: Current progress velocity (0-100)
- E_momentum: Alignment with current trajectory (0-10, reduces energy)
- E_friction: Resistance and obstacles (0-10, increases energy)
```

### 2. Optimization Score

```python
Score = (Impact × Confidence × Momentum) / (Energy × (1 + Risk) × (1 + Friction))

Where:
- Impact: Expected positive outcome (0-1)
- Confidence: Certainty of success (0-1)
- Momentum: Current trajectory alignment (0-10)
- Energy: Total energy required
- Risk: Potential negative outcomes (0-1)
- Friction: Obstacles and resistance (0-10)
```

Higher score = better path forward

### 3. Force Vector Decomposition

Complex decisions are decomposed into force vectors:

```python
F_x = Magnitude × cos(Direction) × Priority
F_y = Magnitude × sin(Direction) × Priority

Net_Force = √(ΣF_x² + ΣF_y²)
Direction = atan2(ΣF_y, ΣF_x)
```

### 4. Potential Fields

```python
Attractive_Potential = Resources × Time_Available × 10.0
Repulsive_Potential = (1 - Velocity) × 5.0
Net_Potential = Attractive - Repulsive
```

## Mental Mapping Model

### Node Types

```python
class NodeType:
    PROBLEM      # Problem to solve
    HYPOTHESIS   # Potential solution
    EVIDENCE     # Supporting data
    DECISION     # Made decision
    ACTION       # Executed action
    OUTCOME      # Result of action
    REFLECTION   # Self-appraisal
    LEARNING     # Lesson learned
```

### Reasoning Chain

Each node stores its complete reasoning chain:

```python
ReasoningStep:
    - thought: What was I thinking?
    - reasoning_type: deductive/inductive/abductive/analogical
    - confidence: How sure was I? (0-1)
    - alternatives_considered: What else did I think about?
    - evidence_used: What data informed this?
```

### Self-Appraisal Algorithm

After each decision outcome:

```python
if actual_success:
    quality = 0.5 + (expected_confidence * 0.5)  # 0.5 to 1.0
else:
    quality = 0.5 - (expected_confidence * 0.5)  # 0.0 to 0.5

quality *= actual_impact  # Weight by actual impact

# Generate lessons
if success and high_confidence:
    lesson = "High confidence validated - good judgment"
elif success and low_confidence:
    lesson = "Succeeded despite doubt - build confidence"
elif failure and high_confidence:
    lesson = "Overconfident - improve assessment"
elif failure and low_confidence:
    lesson = "Appropriately cautious - correct to be uncertain"
```

## Usage Examples

### Example 1: Code Review Decision

```python
from agents.physics_orchestrator import PhysicsInspiredOrchestrator, DecisionState, ActionPath
from agents.mental_mapping import MentalMappingModel

# Initialize
orchestrator = PhysicsInspiredOrchestrator()
mental_map = MentalMappingModel(agent_id="code_reviewer")

# Define current state
state = DecisionState(
    current_position="code_changes_made",
    goal_position="pr_approved_and_merged",
    available_resources=0.8,
    time_available=0.6,
    current_velocity=0.7
)

# Think through the problem
problem_node, reasoning = mental_map.think_through_problem(
    problem="PR has 4 code review comments to address",
    context={'pr_number': 2459}
)

# Define possible paths
paths = [
    ActionPath(
        action_type=ActionType.REFACTOR,
        description="Fix all review comments",
        potential_energy=30.0,
        kinetic_energy=20.0,
        friction=2.0,
        momentum=7.0,
        confidence=0.85,
        risk=0.2,
        impact=0.9,
        urgency=0.7
    ),
    ActionPath(
        action_type=ActionType.DOCUMENT,
        description="Add explanatory comments",
        potential_energy=15.0,
        kinetic_energy=10.0,
        friction=1.0,
        momentum=8.0,
        confidence=0.95,
        risk=0.1,
        impact=0.6,
        urgency=0.5
    )
]

# Orchestrate decision
result = orchestrator.orchestrate(state, paths)

# Record decision in mental map
decision_node = mental_map.make_decision(
    decision_content=result['action_taken'],
    problem_node_id=problem_node.node_id,
    confidence=result.get('confidence', 0.5),
    alternatives_considered=[p.description for p in paths],
    reasoning="Physics-based optimization selected best path"
)

# Later: record outcome
outcome_node = mental_map.record_outcome(
    decision_node_id=decision_node.node_id,
    outcome_content="All comments addressed, PR approved",
    success=True,
    actual_impact=0.9
)

# Iterative review
mental_map.iterative_review(review_threshold=0.6)

# Save for future reference
mental_map.save_mental_map(Path('decision_history/pr_2459.json'))
```

### Example 2: Architecture Decision

```python
# Complex architectural decision with multiple forces
from agents.physics_orchestrator import ForceVector

# Define force vectors influencing decision
forces = [
    ForceVector(
        name="Performance Requirements",
        magnitude=0.9,
        direction=0.0,  # 0 radians (right)
        priority=1.0
    ),
    ForceVector(
        name="Development Time",
        magnitude=0.7,
        direction=math.pi,  # π radians (left)
        priority=0.8
    ),
    ForceVector(
        name="Maintainability",
        magnitude=0.8,
        direction=math.pi/2,  # π/2 radians (up)
        priority=0.9
    ),
    ForceVector(
        name="Team Expertise",
        magnitude=0.6,
        direction=3*math.pi/2,  # 3π/2 radians (down)
        priority=0.7
    )
]

# Calculate net force
net_x = sum(f.get_components()[0] for f in forces)
net_y = sum(f.get_components()[1] for f in forces)
net_magnitude = math.sqrt(net_x**2 + net_y**2)
net_direction = math.atan2(net_y, net_x)

print(f"Net force magnitude: {net_magnitude:.2f}")
print(f"Net direction: {math.degrees(net_direction):.1f}°")

# Use net force to inform decision weights
```

## Integration with Existing Systems

### With Audit Pipeline

```python
# Before running audit, assess and deliberate
state = DecisionState(
    current_position="code_complete",
    goal_position="audit_passed",
    available_resources=0.9,
    time_available=0.8,
    current_velocity=0.6
)

paths = [
    ActionPath(
        action_type=ActionType.AUDIT,
        description="Run full audit with trend storage",
        potential_energy=40.0,
        confidence=0.9,
        impact=0.95,
        urgency=0.8
    )
]

result = orchestrator.orchestrate(state, paths)

if result['action_taken'] == 'audit':
    # Execute audit
    subprocess.run(['python', '-m', 'scripts.space_traversal.audit_runner', 'run'])
```

### With Pre-Release Deployment

```python
# Deployment decision with high stakes
state = DecisionState(
    current_position="pre_release_ready",
    goal_position="deployed_to_production",
    available_resources=0.95,
    time_available=1.0,
    current_velocity=0.8
)

# High energy, high impact decision
deploy_path = ActionPath(
    action_type=ActionType.DEPLOY,
    description="Create pre-release and deploy",
    potential_energy=80.0,  # High effort
    kinetic_energy=50.0,
    friction=4.0,  # Some obstacles
    momentum=6.0,  # Good alignment
    confidence=0.85,
    risk=0.4,  # Moderate risk
    impact=0.95,  # High impact
    urgency=0.9  # Time-sensitive
)

# Deliberate carefully before deployment
result = orchestrator.orchestrate(state, [deploy_path, wait_path])
```

## Metrics and Tracking

### Decision Quality Metrics

```python
mental_map.appraisal_metrics = {
    'total_decisions': 15,
    'correct_decisions': 13,
    'accuracy_rate': 0.867,
    'average_confidence': 0.78,
    'average_quality': 0.82,
    'review_rate': 0.40  # 40% of nodes reviewed
}
```

### Learning Curve Visualization

```python
# Track decision quality over time
history = mental_map.learning_history

qualities = [entry['quality_score'] for entry in history]
timestamps = [entry['timestamp'] for entry in history]

# Quality improving over time?
import matplotlib.pyplot as plt
plt.plot(range(len(qualities)), qualities)
plt.xlabel('Decision Number')
plt.ylabel('Quality Score')
plt.title('Decision Quality Over Time')
plt.savefig('learning_curve.png')
```

## Configuration

### Orchestrator Config

```json
{
  "deliberation_time": 5.0,
  "confidence_threshold": 0.6,
  "energy_budget": 100.0,
  "risk_tolerance": 0.5,
  "momentum_weight": 0.3,
  "friction_weight": 0.2
}
```

### Mental Map Config

```json
{
  "agent_id": "codex_agent_001",
  "auto_review": true,
  "review_threshold": 0.6,
  "save_interval": 10,
  "max_history_size": 1000
}
```

## Best Practices

### 1. Always Think Before Acting

```python
# BAD: Immediate action
run_command("dangerous_operation")

# GOOD: Assess, deliberate, then act
state = assess_current_state()
paths = generate_possible_paths()
optimal = orchestrator.optimize_path(paths, state)
if optimal and optimal.confidence > threshold:
    execute(optimal)
```

### 2. Record All Reasoning

```python
# Store WHY you made a decision
decision_node.add_reasoning_step(
    thought="Chose approach A because...",
    reasoning_type="deductive",
    confidence=0.8,
    alternatives=["approach_b", "approach_c"],
    evidence=["benchmark_results", "expert_opinion"]
)
```

### 3. Review and Learn

```python
# After every outcome, reflect
outcome = execute_decision(decision)
mental_map.record_outcome(
    decision_node_id,
    outcome.description,
    success=outcome.success,
    actual_impact=outcome.impact
)

# Periodic review
if iteration % 10 == 0:
    mental_map.iterative_review()
```

### 4. Use Physics Analogies

```python
# Think in terms of:
# - Energy (effort required)
# - Momentum (current trajectory)
# - Friction (obstacles)
# - Potential fields (attractors and repulsors)
# - Force vectors (competing priorities)
```

## Future Enhancements

### Planned Features (Q1 2026)

- **Multi-Agent Coordination**: Orchestrate multiple agents with force vector alignment
- **Predictive Analytics**: Use past mental maps to predict future decision quality
- **Adaptive Thresholds**: Automatically adjust confidence/risk thresholds based on outcomes
- **Visual Mind Maps**: Generate visual graphs of reasoning chains
- **Pattern Recognition**: Identify recurring decision patterns for optimization

### Research Directions

- **Quantum-Inspired Game Theory**: Blue Team vs Red Team scenarios with wavefunctions and entanglement
- **Thermodynamic Optimization**: Use entropy and free energy for decision optimization
- **Relativity Effects**: Time dilation for urgent vs. non-urgent decisions
- **Field Theory**: Model problem spaces as field potentials

## Quantum-Inspired Game Theory Module

### Overview

The `quantum_game_theory.py` module extends physics-inspired orchestration with:

1. **Classical Energy-Based Game Logic** - Statistical physics approach to Nash equilibria
2. **Quantum-Inspired Extension** - Wavefunctions, operators, superposition, entanglement

### Key Concepts

```python
from agents.quantum_game_theory import (
    BlueRedTeamSimulator,
    create_security_game,
    ClassicalGameEngine,
    QuantumInspiredGameEngine,
    TeamType
)

# Classical: Payoffs → Hamiltonian, Strategies → Microstates
# H(i,j) = -P(i,j)  # Energy minimization = payoff maximization

# Quantum: Strategies → Hilbert space, Mixed strategies → Wavefunctions
# |ψ⟩ = Σ ψ_ij |a_i⟩ ⊗ |b_j⟩  # Joint strategy state
```

### Usage Example: Security Game

```python
# Create a Blue (Defense) vs Red (Attack) game
blue_strats, red_strats, payoff_blue, payoff_red = create_security_game()

# Quantum simulator with entanglement and noise
simulator = BlueRedTeamSimulator(
    blue_strats, red_strats, payoff_blue, payoff_red,
    mode='quantum',
    entanglement=0.5,      # Correlated strategies
    noise_level=0.1,       # Decoherence for uncertainty
    risk_aversion=0.3      # Risk-adjusted utilities
)

# Evaluate a hypothesis
result = simulator.evaluate_hypothesis("Defense-heavy strategy is optimal")
print(f"Blue expected payoff: {result['blue_expected_payoff']:.3f}")
print(f"Blue risk-adjusted: {result['blue_risk_adjusted_utility']:.3f}")

# Run multi-round learning simulation
sim_result = simulator.run_simulation(num_rounds=10, learning_rate=0.1)
```

### Key Features

| Feature | Classical | Quantum-Inspired |
|---------|-----------|------------------|
| Strategy Representation | Probability distributions | Wavefunctions |
| Correlation | Independent | Entanglement |
| Equilibrium | Nash (replicator dynamics) | Quantum (unitary learning) |
| Risk Analysis | Expected value only | Variance + risk-adjusted |
| Noise Model | None | Decoherence channels |

### Physics Equations

**Gibbs Distribution** (Classical equilibrium):
```
p(i,j) ∝ exp(-β H(i,j))
β = inverse temperature (higher = more deterministic)
```

**Expected Payoff** (Quantum):
```
E[U] = ⟨ψ|Û|ψ⟩
Var(U) = ⟨ψ|Û²|ψ⟩ - E[U]²
```

**Risk-Adjusted Utility**:
```
J = E[U] - λ·Var(U)
λ = risk aversion parameter
```

## References

- Physics-based Planning: Potential Field Methods
- Cognitive Architectures: ACT-R, SOAR
- Decision Theory: Expected Utility, Prospect Theory
- Machine Learning: Reinforcement Learning, Meta-Learning

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-10  
**Maintained by**: Aries-Serpent/_codex_ team
