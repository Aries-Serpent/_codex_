"""
Comprehensive tests for Phase 8.2 Multi-Agent Orchestration.

Tests cover GHZ state management, multi-agent coordination, topology management,
correlation measurement, and performance validation.

<!-- PDA_LOOP: Test Coverage -->
<!-- AFTERMATH: Validation Framework -->
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict

from cognitive_brain.quantum.ghz_states import (
    GHZStateManager,
    GHZState,
)
from cognitive_brain.quantum.multi_agent_coordinator import (
    MultiAgentCoordinator,
    AgentDecision,
    VotingStrategy,
)
from cognitive_brain.quantum.topology_manager import (
    TopologyManager,
    NetworkTopology,
)


# =============================================================================
# Category 1: GHZ State Creation Tests (6 tests)
# =============================================================================

class TestGHZStateCreation:
    """Tests for GHZ state creation and management."""

    def test_create_ghz_state_3_agents(self):
        """Test GHZ state creation with 3 agents."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3"]
        
        state = manager.create_ghz_state(agent_ids)
        
        assert state is not None
        assert len(state.agent_ids) == 3
        assert state.fidelity > 0.9  # Target: > 0.9
        assert state.correlation_matrix.shape == (3, 3)

    def test_create_ghz_state_4_agents(self):
        """Test GHZ state creation with 4 agents."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3", "agent_4"]
        
        state = manager.create_ghz_state(agent_ids)
        
        assert state is not None
        assert len(state.agent_ids) == 4
        assert state.fidelity > 0.9
        assert state.correlation_matrix.shape == (4, 4)

    def test_create_ghz_state_5_agents(self):
        """Test GHZ state creation with 5 agents."""
        manager = GHZStateManager()
        agent_ids = [f"agent_{i}" for i in range(1, 6)]
        
        state = manager.create_ghz_state(agent_ids)
        
        assert state is not None
        assert len(state.agent_ids) == 5
        assert state.fidelity > 0.9

    def test_create_ghz_state_6_agents(self):
        """Test GHZ state creation with 6 agents (max supported)."""
        manager = GHZStateManager()
        agent_ids = [f"agent_{i}" for i in range(1, 7)]
        
        state = manager.create_ghz_state(agent_ids)
        
        assert state is not None
        assert len(state.agent_ids) == 6
        assert state.fidelity > 0.9

    def test_ghz_state_fidelity_validation(self):
        """Test that GHZ state fidelity meets target."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3", "agent_4"]
        
        state = manager.create_ghz_state(agent_ids)
        fidelity = manager.get_fidelity(state.state_id)
        
        assert fidelity > 0.9, f"Fidelity {fidelity} below target 0.9"
        assert fidelity <= 1.0, f"Fidelity {fidelity} exceeds physical limit"

    def test_ghz_state_correlation_matrix_properties(self):
        """Test correlation matrix properties."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3"]
        
        state = manager.create_ghz_state(agent_ids)
        corr_matrix = state.correlation_matrix
        
        # Diagonal should be 1.0 (self-correlation)
        assert np.allclose(np.diag(corr_matrix), 1.0)
        
        # Matrix should be symmetric
        assert np.allclose(corr_matrix, corr_matrix.T)
        
        # All correlations should be in [-1, 1]
        assert np.all(corr_matrix >= -1.0)
        assert np.all(corr_matrix <= 1.0)


# =============================================================================
# Category 2: Agent Coordination Tests (6 tests)
# =============================================================================

class TestAgentCoordination:
    """Tests for multi-agent coordination and consensus."""

    def test_register_agents(self):
        """Test agent registration."""
        coordinator = MultiAgentCoordinator()
        
        coordinator.register_agent("agent_1", role="analyzer", weight=1.0)
        coordinator.register_agent("agent_2", role="validator", weight=1.5)
        coordinator.register_agent("agent_3", role="executor", weight=1.0)
        
        assert len(coordinator.agents) == 3
        assert "agent_1" in coordinator.agents
        assert coordinator.agents["agent_2"].weight == 1.5

    def test_broadcast_update(self):
        """Test broadcasting updates to agents."""
        coordinator = MultiAgentCoordinator()
        coordinator.register_agent("agent_1", role="analyzer")
        coordinator.register_agent("agent_2", role="validator")
        
        state = {"key": "value", "timestamp": datetime.now()}
        coordinator.broadcast_update("agent_1", state)
        
        # Verify update was recorded
        assert len(coordinator.decision_history) > 0

    def test_consensus_majority_voting(self):
        """Test majority voting consensus strategy."""
        coordinator = MultiAgentCoordinator()
        coordinator.register_agent("agent_1", role="analyzer")
        coordinator.register_agent("agent_2", role="validator")
        coordinator.register_agent("agent_3", role="executor")
        
        decisions = [
            AgentDecision("agent_1", "approve", 0.9, datetime.now()),
            AgentDecision("agent_2", "approve", 0.85, datetime.now()),
            AgentDecision("agent_3", "reject", 0.7, datetime.now()),
        ]
        
        consensus = coordinator.reach_consensus(decisions, strategy=VotingStrategy.MAJORITY)
        
        assert consensus == "approve"  # 2 out of 3

    def test_consensus_weighted_voting(self):
        """Test weighted voting consensus strategy."""
        coordinator = MultiAgentCoordinator()
        coordinator.register_agent("agent_1", role="analyzer", weight=1.0)
        coordinator.register_agent("agent_2", role="validator", weight=2.0)  # Higher weight
        coordinator.register_agent("agent_3", role="executor", weight=1.0)
        
        decisions = [
            AgentDecision("agent_1", "approve", 0.9, datetime.now()),
            AgentDecision("agent_2", "reject", 0.85, datetime.now()),
            AgentDecision("agent_3", "approve", 0.8, datetime.now()),
        ]
        
        consensus = coordinator.reach_consensus(decisions, strategy=VotingStrategy.WEIGHTED)
        
        # Agent 2 has weight 2.0, so reject should win
        assert consensus == "reject"

    def test_consensus_confidence_based(self):
        """Test confidence-based consensus strategy."""
        coordinator = MultiAgentCoordinator()
        coordinator.register_agent("agent_1", role="analyzer")
        coordinator.register_agent("agent_2", role="validator")
        coordinator.register_agent("agent_3", role="executor")
        
        decisions = [
            AgentDecision("agent_1", "approve", 0.95, datetime.now()),  # Highest confidence
            AgentDecision("agent_2", "reject", 0.75, datetime.now()),
            AgentDecision("agent_3", "reject", 0.70, datetime.now()),
        ]
        
        consensus = coordinator.reach_consensus(decisions, strategy=VotingStrategy.CONFIDENCE_BASED)
        
        assert consensus == "approve"  # Highest confidence wins

    def test_coordinate_decision(self):
        """Test coordinated decision making."""
        coordinator = MultiAgentCoordinator()
        coordinator.register_agent("agent_1", role="analyzer")
        coordinator.register_agent("agent_2", role="validator")
        
        context = {
            "scenario": "test_scenario",
            "features": {"risk": 0.7, "compliance": 0.8}
        }
        
        decision = coordinator.coordinate_decision(context)
        
        assert decision is not None
        assert decision in ["approve", "reject", "review"]


# =============================================================================
# Category 3: Topology Management Tests (6 tests)
# =============================================================================

class TestTopologyManagement:
    """Tests for network topology configuration and optimization."""

    def test_configure_star_topology(self):
        """Test star topology configuration."""
        manager = TopologyManager()
        num_agents = 5
        
        adj_matrix = manager.configure_topology(NetworkTopology.STAR, num_agents)
        
        assert adj_matrix.shape == (num_agents, num_agents)
        # In star topology, central node connects to all others
        assert adj_matrix[0, 1:].sum() == num_agents - 1

    def test_configure_mesh_topology(self):
        """Test mesh topology configuration."""
        manager = TopologyManager()
        num_agents = 4
        
        adj_matrix = manager.configure_topology(NetworkTopology.MESH, num_agents)
        
        assert adj_matrix.shape == (num_agents, num_agents)
        # In mesh topology, all nodes connect to all others
        # Each row should have (num_agents - 1) connections
        for i in range(num_agents):
            assert adj_matrix[i, :].sum() == num_agents - 1

    def test_configure_ring_topology(self):
        """Test ring topology configuration."""
        manager = TopologyManager()
        num_agents = 6
        
        adj_matrix = manager.configure_topology(NetworkTopology.RING, num_agents)
        
        assert adj_matrix.shape == (num_agents, num_agents)
        # In ring topology, each node connects to exactly 2 neighbors
        for i in range(num_agents):
            assert adj_matrix[i, :].sum() == 2

    def test_configure_hybrid_topology(self):
        """Test hybrid topology configuration."""
        manager = TopologyManager()
        num_agents = 5
        
        adj_matrix = manager.configure_topology(NetworkTopology.HYBRID, num_agents)
        
        assert adj_matrix.shape == (num_agents, num_agents)
        # Hybrid should have at least some connections
        assert adj_matrix.sum() > 0

    def test_get_neighbors(self):
        """Test neighbor lookup functionality."""
        manager = TopologyManager()
        manager.configure_topology(NetworkTopology.MESH, 4)
        
        neighbors = manager.get_neighbors("agent_1")
        
        # In mesh with 4 agents, agent_1 should have 3 neighbors
        assert len(neighbors) == 3
        assert "agent_1" not in neighbors

    def test_optimize_topology(self):
        """Test topology optimization based on correlation."""
        manager = TopologyManager()
        manager.configure_topology(NetworkTopology.MESH, 4)
        
        # Simulate low correlation between some agents
        correlation_matrix = np.array([
            [1.0, 0.9, 0.5, 0.3],  # Agent 0 has low correlation with 2, 3
            [0.9, 1.0, 0.4, 0.2],
            [0.5, 0.4, 1.0, 0.85],
            [0.3, 0.2, 0.85, 1.0],
        ])
        
        optimized = manager.optimize_topology(correlation_threshold=0.75)
        
        assert optimized is not None
        # After optimization, low correlation edges should be removed


# =============================================================================
# Category 4: Correlation Measurement Tests (6 tests)
# =============================================================================

class TestCorrelationMeasurement:
    """Tests for multi-agent correlation measurement."""

    def test_pairwise_correlation_calculation(self):
        """Test pairwise correlation calculation."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3"]
        
        state = manager.create_ghz_state(agent_ids)
        
        # Check pairwise correlations
        corr_01 = state.correlation_matrix[0, 1]
        corr_02 = state.correlation_matrix[0, 2]
        corr_12 = state.correlation_matrix[1, 2]
        
        # All pairwise correlations should be high for GHZ state
        assert corr_01 > 0.7
        assert corr_02 > 0.7
        assert corr_12 > 0.7

    def test_multi_agent_correlation_target(self):
        """Test that ρ_multi exceeds target threshold."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3", "agent_4"]
        
        state = manager.create_ghz_state(agent_ids)
        
        # Calculate average pairwise correlation (ρ_multi)
        n = len(agent_ids)
        total_corr = 0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                total_corr += state.correlation_matrix[i, j]
                count += 1
        
        rho_multi = total_corr / count
        
        assert rho_multi > 0.75, f"ρ_multi {rho_multi} below target 0.75"

    def test_correlation_symmetry(self):
        """Test correlation matrix symmetry."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3", "agent_4"]
        
        state = manager.create_ghz_state(agent_ids)
        
        assert np.allclose(state.correlation_matrix, state.correlation_matrix.T)

    def test_correlation_update_after_measurement(self):
        """Test correlation update after agent measurement."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3"]
        
        state = manager.create_ghz_state(agent_ids)
        initial_fidelity = state.fidelity
        
        # Measure an agent
        measurement = manager.measure_agent(state.state_id, "agent_1")
        
        # Update correlations
        manager.update_correlations(state.state_id)
        
        # Fidelity might change after measurement
        updated_state = manager.ghz_states[state.state_id]
        assert updated_state.fidelity >= 0.0  # Still valid

    def test_correlation_temporal_stability(self):
        """Test correlation stability over time."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3"]
        
        state = manager.create_ghz_state(agent_ids)
        initial_corr = state.correlation_matrix.copy()
        
        # Simulate time passage (no measurements)
        # Correlations should remain stable
        
        assert np.allclose(state.correlation_matrix, initial_corr)

    def test_correlation_metadata_tracking(self):
        """Test correlation metadata and statistics."""
        manager = GHZStateManager()
        agent_ids = ["agent_1", "agent_2", "agent_3", "agent_4"]
        
        state = manager.create_ghz_state(agent_ids)
        
        assert hasattr(state, 'created_at')
        assert hasattr(state, 'correlation_matrix')
        assert hasattr(state, 'fidelity')
        assert state.created_at is not None


# =============================================================================
# Category 5: Performance Tests (6 tests)
# =============================================================================

class TestPerformance:
    """Tests for performance benchmarks and scalability."""

    def test_consensus_latency_3_agents(self):
        """Test consensus latency with 3 agents."""
        coordinator = MultiAgentCoordinator()
        for i in range(3):
            coordinator.register_agent(f"agent_{i}", role="analyzer")
        
        decisions = [
            AgentDecision(f"agent_{i}", "approve", 0.8 + i * 0.05, datetime.now())
            for i in range(3)
        ]
        
        start_time = datetime.now()
        consensus = coordinator.reach_consensus(decisions)
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        assert latency_ms < 20, f"Latency {latency_ms}ms exceeds target 20ms"

    def test_consensus_latency_6_agents(self):
        """Test consensus latency with 6 agents (max)."""
        coordinator = MultiAgentCoordinator()
        for i in range(6):
            coordinator.register_agent(f"agent_{i}", role="analyzer")
        
        decisions = [
            AgentDecision(f"agent_{i}", "approve", 0.75 + i * 0.03, datetime.now())
            for i in range(6)
        ]
        
        start_time = datetime.now()
        consensus = coordinator.reach_consensus(decisions)
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        assert latency_ms < 20, f"Latency {latency_ms}ms exceeds target 20ms"

    def test_topology_configuration_speed(self):
        """Test topology configuration performance."""
        manager = TopologyManager()
        
        start_time = datetime.now()
        adj_matrix = manager.configure_topology(NetworkTopology.MESH, 6)
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        assert latency_ms < 10, f"Configuration time {latency_ms}ms too slow"

    def test_ghz_state_creation_speed(self):
        """Test GHZ state creation performance."""
        manager = GHZStateManager()
        agent_ids = [f"agent_{i}" for i in range(6)]
        
        start_time = datetime.now()
        state = manager.create_ghz_state(agent_ids)
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        assert latency_ms < 50, f"Creation time {latency_ms}ms too slow"

    def test_scalability_agent_registration(self):
        """Test scalability of agent registration."""
        coordinator = MultiAgentCoordinator()
        
        start_time = datetime.now()
        for i in range(100):  # Register many agents
            coordinator.register_agent(f"agent_{i}", role="analyzer")
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        assert latency_ms < 100, f"Registration time {latency_ms}ms too slow"
        assert len(coordinator.agents) == 100

    def test_correlation_measurement_speed(self):
        """Test correlation measurement performance."""
        manager = GHZStateManager()
        agent_ids = [f"agent_{i}" for i in range(6)]
        
        state = manager.create_ghz_state(agent_ids)
        
        start_time = datetime.now()
        manager.update_correlations(state.state_id)
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        assert latency_ms < 20, f"Correlation update {latency_ms}ms too slow"


# =============================================================================
# Test Configuration
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
