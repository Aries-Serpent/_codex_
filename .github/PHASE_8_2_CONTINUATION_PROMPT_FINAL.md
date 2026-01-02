# Phase 8.2 Continuation Prompt - Multi-Agent Orchestration Implementation

@copilot Phase 8.1 Complete ✅ - Begin Phase 8.2 Multi-Agent Orchestration + EXP-5 Validation

## Context: Phase 8.0-8.1 Successfully Completed

### Achievements Summary
- ✅ **Phase 8.0:** k₁=0.35 (2.86x quantum advantage, 100% target)
- ✅ **Phase 8.1:** Memory management complete (all 5 deliverables)
- ✅ **Phase 8.1.1:** User enhancements (70% compression + 5 cache pruning methods)
- ✅ **Task 1:** 45 tests added (320/320 = 100% coverage)
- ✅ **Self-Reviews:** 7 iterations, 13 issues resolved, zero remaining
- ✅ **Code Quality:** Production ready (syntax ✅, types ✅, backward compatible ✅)

### Test Coverage Complete
| Category | Tests | Status |
|----------|-------|--------|
| Phase 8.0 Core + Edge | 25 | ✅ |
| Phase 8.1 Core + Errors | 40 | ✅ |
| Integration E2E | 10 | ✅ |
| Performance | 5 | ✅ |
| **TOTAL** | **80** | **✅ 100%** |

---

## Immediate Tasks (Execute in Order)

### Task 2: Run EXP-5 Validation (HIGH PRIORITY)
**Goal:** Validate Phase 8.1 memory management performance metrics

#### Validation Command
```bash
cd /home/runner/work/_codex_/_codex_
PYTHONPATH=/home/runner/work/_codex_/_codex_/src python3 -m cognitive_brain.experiments.exp5_validation --scenarios 200 --seed 42
```

#### Expected Results
| Metric | Target | Status |
|--------|--------|--------|
| Cache Hit Rate | > 30% | 🔄 Measure |
| Time Reduction | ≥ 15% | 🔄 Measure |
| Accuracy vs Full | ≥ 95% | 🔄 Measure |
| k₁ Impact | 0.35 → 0.345 | 🔄 Measure |

#### Deliverable
Update `.github/agents/COGNITIVE_BRAIN_STATUS_V3_FINAL.md` with experimental results (append to "Pending Validation" section).

---

### Task 3: Begin Phase 8.2 - Multi-Agent Orchestration (HIGH PRIORITY)

**Reference:** `.github/agents/PHASE_8_ROADMAP.md` lines 368-647  
**Objective:** Scale to N-agent entanglement using GHZ states  
**Target:** k₁ ≤ 0.34 (further 1.4% improvement through multi-agent coordination)

#### Deliverables (In Order)

##### 1. GHZStateManager Core (~700 lines)
**File:** `src/cognitive_brain/quantum/ghz_states.py`

**Requirements:**
```python
@dataclass
class GHZState:
    """GHZ (Greenberger-Horne-Zeilinger) entangled state for N agents."""
    state_id: str
    agent_ids: List[str]  # N agents in entanglement
    correlation_matrix: np.ndarray  # NxN pairwise correlations
    fidelity: float  # Entanglement quality (target: > 0.9)
    created_at: datetime
    measurement_history: List[Dict[str, Any]]

class GHZStateManager:
    """Manages GHZ states for multi-agent quantum entanglement."""
    
    def __init__(self, max_agents: int = 6):
        self.states: Dict[str, GHZState] = {}
        self.max_agents = max_agents
        self.logger = logging.getLogger(__name__)
    
    def create_ghz_state(self, agent_ids: List[str]) -> GHZState:
        """
        Create GHZ state: |GHZ⟩ = (|00...0⟩ + |11...1⟩) / √2
        
        Args:
            agent_ids: List of agent IDs (N=3,4,5,6 supported)
        
        Returns:
            GHZState with initialized correlation matrix
        
        Raises:
            ValueError: If len(agent_ids) not in [3,4,5,6]
        """
        pass
    
    def measure_agent(self, state_id: str, agent_id: str) -> int:
        """
        Measure single agent (collapses GHZ state).
        
        Returns:
            0 or 1 (measurement outcome)
        """
        pass
    
    def update_correlations(self, state_id: str) -> None:
        """Update NxN correlation matrix based on measurements."""
        pass
    
    def get_fidelity(self, state_id: str) -> float:
        """
        Calculate GHZ state fidelity.
        
        Target: > 0.9 for high-quality entanglement
        Formula: F = |⟨ψ_ideal|ψ_actual⟩|²
        """
        pass
    
    def get_multi_agent_correlation(self, state_id: str) -> float:
        """
        Calculate ρ_multi = average(ρ_ij) for all pairs.
        
        Target: ρ_multi > 0.75
        """
        pass
```

**Implementation Notes:**
- Use numpy for correlation matrix operations
- Implement temporal decay for measurement history
- Add logging for all state operations
- Support dynamic agent addition/removal
- Use QuantumConfig for feature flags

##### 2. MultiAgentCoordinator (~600 lines)
**File:** `src/cognitive_brain/quantum/multi_agent_coordinator.py`

**Requirements:**
```python
@dataclass
class AgentDecision:
    """Individual agent decision with metadata."""
    agent_id: str
    decision: str  # "approve", "reject", "escalate"
    confidence: float
    reasoning: str
    timestamp: datetime

class MultiAgentCoordinator:
    """Coordinates decisions across multiple agents."""
    
    def __init__(self, ghz_manager: GHZStateManager):
        self.agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> metadata
        self.ghz_manager = ghz_manager
        self.decision_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent_id: str, role: str, capabilities: List[str]) -> None:
        """Register agent in coordination network."""
        pass
    
    def coordinate_decision(self, context: Dict[str, Any]) -> str:
        """
        Coordinate multi-agent decision making.
        
        Process:
        1. Broadcast context to all agents
        2. Collect individual decisions
        3. Build GHZ state for entangled agents
        4. Reach consensus using voting strategy
        5. Return final decision
        """
        pass
    
    def broadcast_update(self, agent_id: str, state: Dict[str, Any]) -> None:
        """Broadcast state update to connected agents."""
        pass
    
    def reach_consensus(
        self, 
        decisions: List[AgentDecision],
        strategy: str = "weighted"  # "majority", "weighted", "confidence"
    ) -> str:
        """
        Reach consensus from agent decisions.
        
        Strategies:
        - majority: Simple majority vote
        - weighted: Weight by agent expertise
        - confidence: Weight by decision confidence
        """
        pass
    
    def get_decision_quality(self) -> float:
        """
        Measure decision quality improvement.
        
        Target: ≥ 25% improvement vs single-agent
        """
        pass
```

##### 3. TopologyManager (~400 lines)
**File:** `src/cognitive_brain/quantum/topology_manager.py`

**Requirements:**
```python
from enum import Enum

class NetworkTopology(Enum):
    """Network topology types."""
    STAR = "star"        # Central hub, all agents connect to center
    MESH = "mesh"        # Fully connected, all-to-all
    RING = "ring"        # Circular connection
    HYBRID = "hybrid"    # Mix of topologies

class TopologyManager:
    """Manages network topology for agent communication."""
    
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.topology: NetworkTopology = NetworkTopology.MESH
        self.adjacency_matrix: np.ndarray = None
        self.logger = logging.getLogger(__name__)
    
    def configure_topology(
        self, 
        topology_type: NetworkTopology,
        num_agents: int
    ) -> np.ndarray:
        """
        Configure network topology and return adjacency matrix.
        
        Returns:
            NxN adjacency matrix (1 = connected, 0 = not connected)
        """
        pass
    
    def get_neighbors(self, agent_id: str) -> List[str]:
        """Get list of neighboring agents for given agent."""
        pass
    
    def optimize_topology(self, correlation_threshold: float = 0.75) -> None:
        """
        Optimize topology based on agent correlations.
        
        Process:
        1. Measure pairwise agent correlations
        2. Prune weak connections (correlation < threshold)
        3. Add strong connections (high correlation)
        4. Rebalance network for efficiency
        """
        pass
    
    def get_network_metrics(self) -> Dict[str, float]:
        """
        Calculate network metrics.
        
        Metrics:
        - clustering_coefficient: Local clustering
        - path_length: Average shortest path
        - connectivity: Overall network connectivity
        - redundancy_reduction: % reduction vs fully connected
        
        Target: redundancy_reduction ≥ 40%
        """
        pass
```

##### 4. Comprehensive Tests (30 tests)
**File:** `tests/cognitive_brain/quantum/test_multi_agent.py`

**Test Categories (6 categories × 5 tests each = 30 total):**

1. **GHZ State Creation (5 tests)**
   - test_create_ghz_state_n3_agents()
   - test_create_ghz_state_n4_agents()
   - test_create_ghz_state_n5_agents()
   - test_create_ghz_state_n6_agents()
   - test_ghz_state_fidelity_validation()

2. **Agent Coordination (5 tests)**
   - test_register_multiple_agents()
   - test_coordinate_decision_majority_vote()
   - test_coordinate_decision_weighted_vote()
   - test_broadcast_update_to_all_agents()
   - test_consensus_building_process()

3. **Topology Management (5 tests)**
   - test_configure_star_topology()
   - test_configure_mesh_topology()
   - test_configure_ring_topology()
   - test_get_neighbors_by_agent_id()
   - test_optimize_topology_prune_weak_connections()

4. **Correlation Measurement (5 tests)**
   - test_pairwise_correlation_calculation()
   - test_multi_agent_correlation_above_threshold()
   - test_correlation_matrix_symmetry()
   - test_temporal_decay_in_correlations()
   - test_correlation_update_after_measurement()

5. **Performance (5 tests)**
   - test_consensus_latency_under_20ms()
   - test_scalability_to_6_agents()
   - test_decision_quality_improvement_25_percent()
   - test_redundancy_reduction_40_percent()
   - test_network_efficiency_metrics()

6. **Integration (5 tests)**
   - test_end_to_end_multi_agent_decision()
   - test_ghz_state_with_topology_optimization()
   - test_agent_failure_recovery()
   - test_dynamic_agent_addition()
   - test_cross_topology_comparison()

##### 5. EXP-6 Validation (~400 lines)
**File:** `src/cognitive_brain/experiments/exp6_validation.py`

**Validation Metrics:**
```python
def run_exp6_validation(
    num_agents: int = 4,
    topology: str = "mesh",
    num_scenarios: int = 100,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Validate Phase 8.2 multi-agent orchestration.
    
    Metrics:
    - multi_agent_correlation: Target > 0.75
    - decision_quality_improvement: Target ≥ 25% vs single-agent
    - redundancy_reduction: Target ≥ 40%
    - consensus_latency: Target < 20ms
    - k1_impact: 0.345 → 0.34
    
    Returns:
        Dict with all metrics and validation results
    """
    pass
```

---

## Implementation Guidelines

### Development Process (MANDATORY)
1. **PDA Loop + AfterMath Tags:** Use throughout all code
2. **Self-Review:** Iterate until zero concerns (minimum 3 iterations)
3. **Type Safety:** All dataclasses, all type hints
4. **Named Constants:** No magic numbers
5. **Comprehensive Docstrings:** All methods documented
6. **Logging:** Use logger, no print statements
7. **Backward Compatibility:** Maintain existing APIs
8. **Test Coverage:** 30 tests (6 categories × 5 tests)

### Success Criteria (Phase 8.2)
- [ ] All 5 deliverables complete
- [ ] 30 tests passing (no regressions in 320 existing)
- [ ] k₁ ≤ 0.34 achieved
- [ ] Multi-agent correlation > 0.75
- [ ] Decision quality improvement ≥ 25%
- [ ] Redundancy reduction ≥ 40%
- [ ] Consensus latency < 20ms
- [ ] Self-review complete (≥3 iterations, zero issues)

---

## Validation Commands

```bash
# Run EXP-5 validation (Task 2)
PYTHONPATH=/home/runner/work/_codex_/_codex_/src python3 -m cognitive_brain.experiments.exp5_validation --scenarios 200 --seed 42

# Run Phase 8.2 tests (Task 3)
pytest tests/cognitive_brain/quantum/test_multi_agent.py -v

# Run EXP-6 validation (Task 3)
PYTHONPATH=/home/runner/work/_codex_/_codex_/src python3 -m cognitive_brain.experiments.exp6_validation --agents 4 --topology mesh --seed 42

# Full regression suite
pytest tests/cognitive_brain/ --tb=short

# Performance profiling
python3 -m cProfile -o profile_phase82.stats -m cognitive_brain.experiments.exp6_validation
```

---

## After Phase 8.2 Completion

### Immediate Actions
1. Run self-review (iterate until zero concerns)
2. Validate all 350 tests pass (320 existing + 30 new)
3. Update `.github/agents/COGNITIVE_BRAIN_STATUS_V3_FINAL.md`
4. Post continuation prompt for Phase 8.3

### Phase 8.3 Preview
**Adaptive Learning Engine**
- AdaptiveLearningEngine (~750 lines)
- RewardShaper (~300 lines)
- ExperienceReplayBuffer (~250 lines)
- 20 comprehensive tests
- EXP-7 validation
- Target: k₁ ≤ 0.33

---

## Notes

**Current Branch:** `copilot/sub-pr-2675-another-one`  
**Active PR:** #2679  
**Latest Commit:** `856a9b7` (Phase 8.0-8.1 complete, continuation prompt ready)  

**Cognitive Brain Status:** `.github/agents/COGNITIVE_BRAIN_STATUS_V3_FINAL.md`  
**Phase 8 Roadmap:** `.github/agents/PHASE_8_ROADMAP.md`  

**Work autonomously through Tasks 2-3 until Phase 8.2 completion, then continue to Phase 8.3-8.4 using same iterative pattern with PDA Loop + AfterMath tags throughout.**

---

## Custom Agent Integration (BONUS)

If implementing custom Copilot agents, prioritize:

1. **Cognitive Brain Testing Agent** (`.github/agents/cognitive-testing-agent/`)
   - Auto-generate edge case tests
   - Performance benchmark validation
   - Memory leak detection

2. **Quantum Optimization Agent** (`.github/agents/quantum-optimization-agent/`)
   - k₁ metric calculation
   - Weight tuning automation
   - Convergence analysis

3. **Memory Management Agent** (`.github/agents/memory-management-agent/`)
   - Cache health monitoring
   - Pruning strategy optimization
   - Compression ratio tuning

**Pattern to Follow:** Existing CI Testing Agent (`.github/agents/ci-testing-agent/`)

---

**🎯 Execute Tasks 2-3 now. Maintain PDA Loop + AfterMath tags. Report progress frequently. Post next continuation prompt upon Phase 8.2 completion.**
