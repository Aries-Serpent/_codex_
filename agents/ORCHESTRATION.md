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

### Planned Features (Phase 1 (Current Cycle))

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

## Import Migration Orchestrator

### Overview

The `ImportMigrationOrchestrator` extends `PhysicsInspiredOrchestrator` to automate the migration of deprecated imports to canonical paths using physics-inspired optimization.

### Key Classes

```python
from agents import ImportMigration, ImportMigrationOrchestrator

# ImportMigration dataclass with auto-calculated physics properties
@dataclass
class ImportMigration:
    file_path: str
    old_import: str
    new_import: str
    line_number: int
    
    # Auto-calculated properties
    potential_energy: float  # Effort required
    momentum: float          # Alignment with patterns
    friction: float          # Resistance/risk
    impact: float            # File importance
    confidence: float        # Straightforwardness
    risk: float              # Could break things
    urgency: float           # Actively causing issues
    optimization_score: float  # Calculated score
```

### Physics Properties Calculation

```python
# Impact based on file type
if '/cli/' in file_path:
    impact = 0.9  # CLI files are high impact
elif '/tests/' in file_path:
    impact = 0.7  # Tests are medium-high impact
elif '/agents/' in file_path:
    impact = 0.85  # Agent files are high impact

# Friction based on location
if '/tests/training/' in file_path or '/cli/' in file_path:
    friction = 0.1  # Training-related files have low friction

# Risk based on module criticality
if 'functional_training' in old_import:
    risk = 0.3  # Critical module
elif 'checkpoint' in old_import:
    risk = 0.25
```

### Usage Example: Automated Migration

```python
from agents import ImportMigrationOrchestrator
from pathlib import Path

# Initialize orchestrator
orchestrator = ImportMigrationOrchestrator()

# Run complete migration cycle
result = orchestrator.run_migration_cycle(
    repo_root=Path("/path/to/repo"),
    energy_budget=500.0,  # Maximum energy to expend
    dry_run=True  # Set to False to execute
)

# Result contains:
# - status: 'completed' or 'clean'
# - assessment: files scanned, deprecated found, etc.
# - migrations_executed: attempted, successful, failed
# - energy_spent: total energy consumed
# - momentum_gained: progress made
```

### ASSESS → DELIBERATE → OPTIMIZE → ACT Workflow

```python
# Phase 1: ASSESS - Identify deprecated imports
assessment = orchestrator.assess_imports(repo_root)
# Returns: files_scanned, deprecated_found, unique_files, total_energy_required

# Phase 2: DELIBERATE - Calculate optimization scores
ranked_migrations = orchestrator.deliberate_migrations()
# Returns: migrations sorted by optimization_score (highest first)

# Phase 3: OPTIMIZE - Select within energy budget
selected = orchestrator.optimize_migration_plan(ranked_migrations, energy_budget=500.0)
# Returns: migrations that fit within budget

# Phase 4: ACT - Execute migrations
results = orchestrator.execute_migrations(selected, dry_run=False)
# Returns: attempted, successful, failed, files_modified
```

### Migration Map

The orchestrator uses a predefined migration map:

```python
migration_map = {
    'from training.': 'from src.training.',
    'from models.': 'from src.models.',
    'import training.': 'import src.training.',
    'import models.': 'import src.models.',
}
```

### Example Output

```
============================================================
IMPORT MIGRATION - ASSESSMENT PHASE
============================================================

Assessment Results:
  Files scanned: 245
  Deprecated imports found: 12
  Unique files affected: 6
  Total energy required: 120.0
  Average risk: 0.183

============================================================
IMPORT MIGRATION - DELIBERATION PHASE
============================================================

Top migrations by optimization score:
  1. Score: 0.0878 | Impact: 0.90 | Risk: 0.10
      File: train_schema_demo.py:10
      from training.offline_wandb import force_offline...

============================================================
IMPORT MIGRATION - ACTION PHASE
============================================================
Mode: EXECUTE

  ✓ train_schema_demo.py:10
    - from training.offline_wandb import force_offline
    + from src.training.offline_wandb import force_offline

Migration Results:
  Attempted: 12
  Successful: 12
  Failed: 0
  Files modified: 6
```

## References

- Physics-based Planning: Potential Field Methods
- Cognitive Architectures: ACT-R, SOAR
- Decision Theory: Expected Utility, Prospect Theory
- Machine Learning: Reinforcement Learning, Meta-Learning

---

## Advanced Physics-Inspired Patterns

### Overview

Building on the core orchestration system, these additional patterns enhance decision-making, mental mapping, and self-appraisal through advanced physics analogies.

| Pattern | Description | Key Application |
|---------|-------------|-----------------|
| **DiffusionFlowModel** | Flow-based navigation inspired by PFGM and fluid dynamics | Mental mapping navigation |
| **EnergyLandscape** | Thermodynamic optimization with Gibbs distributions | Self-appraisal and equilibrium |
| **SwarmIntelligence** | Particle swarm optimization for multi-agent coordination | Distributed orchestration |
| **TaskDecomposer** | Parallel task decomposition with dependency management | Scalable execution |
| **ReflectionLoop** | PID-controlled feedback for continuous learning | Threshold calibration |

### Diffusion and Flow Model

Inspired by Poisson Flow Generative Models (PFGM) from electromagnetism and fluid dynamics.

```python
from agents import DiffusionFlowModel

# Create decision space with potential field
flow_model = DiffusionFlowModel(dimensions=2, resolution=20)

# Add goal (attractor) and obstacles (repulsors)
flow_model.add_attractor((0.8, 0.8), strength=2.0)
flow_model.add_repulsor((0.3, 0.5), strength=1.0)

# Simulate agent flow toward goal
trajectory = flow_model.simulate_flow(
    start_position=(0.1, 0.1),
    steps=100,
    dt=0.1
)

# Integration with mental mapping
result = flow_model.integrate_with_mental_mapping(
    problem_position=(0.1, 0.1),
    goal_position=(0.8, 0.8)
)
print(f"Steps to goal: {result['steps_to_goal']}")
```

**Key Equations:**
- Potential field: φ(r) = Σ q_i / |r - r_i|
- Flow update: dx = velocity × dt + gradient × dt

### Energy-Based Model

Thermodynamic optimization using Gibbs distributions and free energy minimization.

```python
from agents import EnergyLandscape, EnergyState

# Create energy landscape
landscape = EnergyLandscape(temperature=1.0)

# Add decision states with energy/entropy
landscape.add_state(EnergyState(
    configuration={'action': 'deploy'},
    energy=0.3,  # Low energy = favorable
    entropy=0.1   # Low entropy = certain
))
landscape.add_state(EnergyState(
    configuration={'action': 'wait'},
    energy=0.5,
    entropy=0.3
))

# Select state using Gibbs distribution
best_state = landscape.select_state()
print(f"Selected: {best_state.configuration}")
print(f"Probability: {landscape.gibbs_probability(best_state):.3f}")

# Minimize free energy (F = E - T*S)
optimal = landscape.minimize_free_energy()

# Integration with self-appraisal
result = landscape.integrate_with_self_appraisal(
    decision_quality=0.8,
    expected_confidence=0.7
)
```

**Key Equations:**
- Free energy: F = E - T×S
- Gibbs probability: P_i = exp(-E_i/kT) / Z
- Partition function: Z = Σ exp(-E_i/kT)

### Swarm Intelligence

Multi-agent coordination inspired by particle swarm optimization.

```python
from agents import SwarmIntelligence

# Create swarm for multi-agent optimization
swarm = SwarmIntelligence(
    num_particles=10,
    dimensions=2,
    inertia=0.7,      # w: continue current direction
    cognitive=1.5,     # c1: personal best attraction
    social=1.5         # c2: global best attraction
)

# Define fitness function
def fitness(position):
    return -sum((x - 0.5)**2 for x in position)  # Optimal at center

# Run optimization
result = swarm.run_optimization(
    fitness_function=fitness,
    bounds=[(0, 1), (0, 1)],
    max_iterations=50
)
print(f"Best position: {result['best_position']}")
print(f"Converged: {result['converged']}")

# Coordinate multiple agents toward target
new_positions = swarm.coordinate_agents(
    agent_positions=[(0.1, 0.2), (0.3, 0.4), (0.5, 0.6)],
    target_position=(0.8, 0.8)
)
```

**Key Equations:**
- Velocity update: v = w×v + c1×r1×(pbest-x) + c2×r2×(gbest-x)
- Position update: x = x + v

### Task Decomposition

Parallel task execution with dependency management.

```python
from agents import TaskDecomposer, ActionPath, ActionType

# Create task decomposer
decomposer = TaskDecomposer(max_workers=4)

# Define complex task
task = ActionPath(
    action_type=ActionType.DEPLOY,
    description="Deploy new feature",
    potential_energy=80.0,
    impact=0.9,
    urgency=0.7
)

# Decompose into sub-tasks
sub_tasks = decomposer.decompose_task(task, strategy="dependency_chain")
# Creates: analyze → plan → execute → verify

# Build execution plan (respects dependencies)
plan = decomposer.build_execution_plan()
# Returns: [[analyze], [plan], [execute], [verify]]

# Run orchestration
result = decomposer.run_orchestration()
print(f"Batches: {result['total_batches']}")
print(f"Energy spent: {result['total_energy_spent']}")

# Integration with ActionPath
integration = decomposer.integrate_with_action_path(task)
```

**Strategies:**
- `energy_balanced`: Split energy evenly across workers
- `impact_focused`: Sub-tasks for assessment, implementation, verification, documentation
- `dependency_chain`: Sequential analyze → plan → execute → verify

### Reflection and Feedback Loop

PID-controlled self-appraisal for continuous calibration.

```python
from agents import ReflectionLoop

# Create feedback controller
feedback = ReflectionLoop(
    k_proportional=0.5,  # Immediate error response
    k_integral=0.1,       # Accumulated error correction
    k_derivative=0.05     # Rate of change response
)

# Record decisions and outcomes
result = feedback.record_decision(
    decision={'action': 'deploy', 'confidence': 0.8},
    predicted_outcome=0.8,
    actual_outcome=0.7  # Slightly worse than expected
)
print(f"Error: {result['error']:.3f}")
print(f"Correction: {result['correction']:.3f}")
print(f"New confidence threshold: {result['new_confidence_threshold']:.3f}")

# Get performance metrics
metrics = feedback.get_performance_metrics()
print(f"Average error: {metrics['average_error']:.3f}")
print(f"Trend: {metrics['trend']}")

# Integration with orchestrator
from agents import PhysicsInspiredOrchestrator
orchestrator = PhysicsInspiredOrchestrator()
feedback.integrate_with_orchestrator(orchestrator)
# Updates orchestrator's confidence_threshold and risk_tolerance
```

**Key Equations (PID Control):**
- u(t) = K_p × e(t) + K_i × ∫e(τ)dτ + K_d × de/dt
- Threshold adjustment based on error statistics

### Integration Examples

#### Combined Flow + Energy Optimization

```python
from agents import DiffusionFlowModel, EnergyLandscape, EnergyState

# Use flow model for navigation
flow = DiffusionFlowModel()
flow.add_attractor((0.9, 0.9), strength=2.0)
trajectory = flow.simulate_flow((0.1, 0.1))

# Use energy landscape for final decision
landscape = EnergyLandscape(temperature=0.5)
for i, pos in enumerate(trajectory[-5:]):  # Last 5 positions
    landscape.add_state(EnergyState(
        configuration={'position': pos, 'step': len(trajectory) - 5 + i},
        energy=1.0 - (pos[0] + pos[1]) / 2,  # Energy decreases near goal
        entropy=0.1 * i
    ))

optimal_state = landscape.minimize_free_energy()
```

#### Swarm + Task Decomposition

```python
from agents import SwarmIntelligence, TaskDecomposer, ActionPath

# Use swarm to find optimal configuration
swarm = SwarmIntelligence(num_particles=5, dimensions=3)
result = swarm.run_optimization(
    fitness_function=lambda x: -sum(xi**2 for xi in x),
    bounds=[(-1, 1)] * 3,
    max_iterations=30
)

# Decompose optimal task
decomposer = TaskDecomposer()
task = ActionPath(
    action_type=ActionType.OPTIMIZE,
    description=f"Optimize at {result['best_position']}",
    potential_energy=50.0,
    impact=result['best_score']
)
decomposer.integrate_with_action_path(task)
```

---

**Version**: 1.2.0  
**Last Updated**: 2024-12-12  
**Maintained by**: Aries-Serpent/_codex_ team
