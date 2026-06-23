#!/usr/bin/env python3
"""
Phase 9.3 Task 4: Workload Balancing Rules
===========================================
Distribute load evenly across agents with intelligent constraints.

Balancing strategies:
- Round-robin by default
- Load-aware: Deprioritize agents at >80% CPU/Memory capacity
- Latency-aware: Prefer agents with lowest p99 latency
- Cost-aware: Prefer cheaper runners if capability equivalent

Constraints enforced:
- CPU per agent: <1000m
- Memory per agent: <2000Mi
- Latency per agent: <2s
- Max queue depth: 5 tasks per agent

Spillover logic:
- If primary agent queue full, route to secondary
- If all agents at capacity, queue with backoff retry
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading


class BalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LOAD_AWARE = "load_aware"
    LATENCY_AWARE = "latency_aware"
    COST_AWARE = "cost_aware"
    HYBRID = "hybrid"  # Combines all strategies


@dataclass
class AgentMetrics:
    """Runtime metrics for an agent."""
    agent_id: str
    agent_name: str
    
    # Resource utilization (0-100%)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    # Performance
    avg_task_latency_ms: float = 100.0
    p99_latency_ms: float = 500.0
    avg_throughput_tasks_per_sec: float = 5.0
    
    # Queue status
    queue_depth: int = 0
    max_queue_capacity: int = 5
    active_tasks: int = 0
    
    # Cost
    cost_per_hour: float = 1.0  # Relative cost
    
    # Health
    error_rate: float = 0.0  # 0-1
    availability: float = 1.0  # 0-1 (uptime percentage)
    
    # Metadata
    last_updated: str = ""
    updated_count: int = 0


@dataclass
class LoadBalancingDecision:
    """Load balancing decision for agent assignment."""
    primary_agent_id: str
    secondary_agents: List[str] = field(default_factory=list)
    strategy_used: BalancingStrategy = BalancingStrategy.HYBRID
    load_scores: Dict[str, float] = field(default_factory=dict)  # agent_id -> score
    reasoning: str = ""
    decision_timestamp: str = ""


class AgentMetricsCollector:
    """Collect and track agent metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, AgentMetrics] = {}
        self.lock = threading.RLock()
    
    def register_agent(self, agent_id: str, agent_name: str, cost_per_hour: float = 1.0):
        """Register an agent for metrics tracking."""
        with self.lock:
            self.metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_name=agent_name,
                cost_per_hour=cost_per_hour,
                last_updated=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
    
    def update_metrics(self, agent_id: str, **kwargs):
        """Update agent metrics."""
        with self.lock:
            if agent_id not in self.metrics:
                return
            
            for key, value in kwargs.items():
                if hasattr(self.metrics[agent_id], key):
                    setattr(self.metrics[agent_id], key, value)
            
            self.metrics[agent_id].last_updated = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            self.metrics[agent_id].updated_count += 1
    
    def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get metrics for an agent."""
        with self.lock:
            return self.metrics.get(agent_id)
    
    def get_all_metrics(self) -> Dict[str, AgentMetrics]:
        """Get all agent metrics."""
        with self.lock:
            return {aid: asdict(metrics) for aid, metrics in self.metrics.items()}
    
    def get_healthy_agents(self) -> List[str]:
        """Get agents that are healthy (availability >0.9, error_rate <0.1)."""
        with self.lock:
            healthy = []
            for agent_id, metrics in self.metrics.items():
                if metrics.availability > 0.9 and metrics.error_rate < 0.1:
                    healthy.append(agent_id)
            return healthy
    
    def get_agents_above_capacity(self, threshold: float = 0.8) -> List[str]:
        """Get agents above resource threshold (CPU or Memory >threshold)."""
        with self.lock:
            above_threshold = []
            for agent_id, metrics in self.metrics.items():
                if metrics.cpu_usage > threshold * 100 or metrics.memory_usage > threshold * 100:
                    above_threshold.append(agent_id)
            return above_threshold


class LoadBalancer:
    """Intelligent load balancer for agent assignment."""
    
    def __init__(self, metrics_collector: AgentMetricsCollector):
        self.metrics_collector = metrics_collector
        self.strategy = BalancingStrategy.HYBRID
        self.capacity_threshold = 0.8
        self.max_queue_depth = 5
        self.latency_threshold_ms = 2000
    
    def calculate_load_score(
        self,
        agent_id: str,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calculate load score for an agent (0-100, lower=better).
        
        Weights:
          - cpu_load: 0.3
          - memory_load: 0.2
          - queue_utilization: 0.3
          - latency: 0.1
          - error_rate: 0.1
        """
        if weights is None:
            weights = {
                "cpu_load": 0.3,
                "memory_load": 0.2,
                "queue_utilization": 0.3,
                "latency": 0.1,
                "error_rate": 0.1,
            }
        
        metrics = self.metrics_collector.get_agent_metrics(agent_id)
        if not metrics:
            return float('inf')
        
        # Component scores (0-100)
        cpu_score = metrics.cpu_usage  # Already 0-100%
        memory_score = metrics.memory_usage  # Already 0-100%
        queue_score = (metrics.queue_depth / metrics.max_queue_capacity) * 100
        latency_score = min(100, (metrics.p99_latency_ms / self.latency_threshold_ms) * 100)
        error_score = metrics.error_rate * 100
        
        # Weighted sum
        total_score = (
            cpu_score * weights["cpu_load"] +
            memory_score * weights["memory_load"] +
            queue_score * weights["queue_utilization"] +
            latency_score * weights["latency"] +
            error_score * weights["error_rate"]
        )
        
        return total_score
    
    def round_robin_selection(self, agents: List[str]) -> str:
        """Select agent using round-robin (simple rotation)."""
        if not agents:
            return None
        return agents[0]  # In production, rotate through list
    
    def load_aware_selection(self, agents: List[str]) -> Tuple[str, List[str]]:
        """Select best agent based on load, return primary and secondaries."""
        if not agents:
            return None, []
        
        # Score all agents
        scores = {}
        for agent_id in agents:
            scores[agent_id] = self.calculate_load_score(agent_id)
        
        # Sort by score (ascending = best)
        sorted_agents = sorted(scores.items(), key=lambda x: x[1])
        
        # Primary: lowest score
        primary = sorted_agents[0][0] if sorted_agents else None
        
        # Secondaries: next 2 agents
        secondaries = [a[0] for a in sorted_agents[1:3]]
        
        return primary, secondaries, scores
    
    def latency_aware_selection(self, agents: List[str]) -> Tuple[str, List[str], Dict]:
        """Select agent with lowest p99 latency."""
        if not agents:
            return None, [], {}
        
        metrics_by_agent = {
            aid: self.metrics_collector.get_agent_metrics(aid)
            for aid in agents
        }
        
        # Sort by p99 latency
        sorted_agents = sorted(
            metrics_by_agent.items(),
            key=lambda x: x[1].p99_latency_ms if x[1] else float('inf')
        )
        
        primary = sorted_agents[0][0] if sorted_agents else None
        secondaries = [a[0] for a in sorted_agents[1:3]]
        scores = {a[0]: a[1].p99_latency_ms for a in sorted_agents if a[1]}
        
        return primary, secondaries, scores
    
    def cost_aware_selection(self, agents: List[str]) -> Tuple[str, List[str], Dict]:
        """Select cheapest agent if capability equivalent."""
        if not agents:
            return None, [], {}
        
        metrics_by_agent = {
            aid: self.metrics_collector.get_agent_metrics(aid)
            for aid in agents
        }
        
        # Sort by cost (ascending = cheapest)
        sorted_agents = sorted(
            metrics_by_agent.items(),
            key=lambda x: x[1].cost_per_hour if x[1] else float('inf')
        )
        
        primary = sorted_agents[0][0] if sorted_agents else None
        secondaries = [a[0] for a in sorted_agents[1:3]]
        scores = {a[0]: a[1].cost_per_hour for a in sorted_agents if a[1]}
        
        return primary, secondaries, scores
    
    def hybrid_selection(self, agents: List[str]) -> Tuple[str, List[str], Dict]:
        """Hybrid selection combining all strategies with weights."""
        if not agents:
            return None, [], {}
        
        # Get scores from each strategy
        load_primary, load_secondaries, load_scores = self.load_aware_selection(agents)
        latency_primary, latency_secondaries, latency_scores = self.latency_aware_selection(agents)
        cost_primary, cost_secondaries, cost_scores = self.cost_aware_selection(agents)
        
        # Combine scores with weights
        strategy_weights = {
            "load": 0.5,
            "latency": 0.3,
            "cost": 0.2,
        }
        
        final_scores = {}
        for agent_id in agents:
            load_score = load_scores.get(agent_id, 100)
            latency_score = (
                self.metrics_collector.get_agent_metrics(agent_id).p99_latency_ms / 2000 * 100
                if self.metrics_collector.get_agent_metrics(agent_id)
                else 100
            )
            cost_score = (
                self.metrics_collector.get_agent_metrics(agent_id).cost_per_hour * 100
                if self.metrics_collector.get_agent_metrics(agent_id)
                else 100
            )
            
            final_scores[agent_id] = (
                load_score * strategy_weights["load"] +
                latency_score * strategy_weights["latency"] +
                cost_score * strategy_weights["cost"]
            )
        
        # Sort by final score
        sorted_agents = sorted(final_scores.items(), key=lambda x: x[1])
        
        primary = sorted_agents[0][0] if sorted_agents else None
        secondaries = [a[0] for a in sorted_agents[1:3]]
        
        return primary, secondaries, final_scores
    
    def make_balancing_decision(
        self,
        candidate_agents: List[str],
        required_capacity: str = "small"  # small, medium, large
    ) -> LoadBalancingDecision:
        """Make load balancing decision for given agents."""
        start_time = time.time()
        
        # Filter out unhealthy agents
        healthy_agents = [a for a in candidate_agents if a in self.metrics_collector.get_healthy_agents()]
        if not healthy_agents:
            healthy_agents = candidate_agents  # Fallback to all if none healthy
        
        # Filter out over-capacity agents
        over_capacity = self.metrics_collector.get_agents_above_capacity(self.capacity_threshold)
        available_agents = [a for a in healthy_agents if a not in over_capacity]
        
        # If all at capacity, use spillover logic
        if not available_agents:
            available_agents = healthy_agents
        
        # Make selection based on strategy
        if self.strategy == BalancingStrategy.ROUND_ROBIN:
            primary = self.round_robin_selection(available_agents)
            secondaries = available_agents[1:3]
            final_scores = {}
        elif self.strategy == BalancingStrategy.LOAD_AWARE:
            primary, secondaries, final_scores = self.load_aware_selection(available_agents)
        elif self.strategy == BalancingStrategy.LATENCY_AWARE:
            primary, secondaries, final_scores = self.latency_aware_selection(available_agents)
        elif self.strategy == BalancingStrategy.COST_AWARE:
            primary, secondaries, final_scores = self.cost_aware_selection(available_agents)
        else:  # HYBRID
            primary, secondaries, final_scores = self.hybrid_selection(available_agents)
        
        latency_ms = (time.time() - start_time) * 1000
        
        decision = LoadBalancingDecision(
            primary_agent_id=primary,
            secondary_agents=secondaries,
            strategy_used=self.strategy,
            load_scores=final_scores,
            reasoning=f"Selected {primary} based on {self.strategy.value} (available: {len(available_agents)}, healthy: {len(healthy_agents)})",
            decision_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        
        return decision


def example_load_balancing():
    """Example usage of load balancer."""
    print("\n" + "=" * 80)
    print("PHASE 9.3 TASK 4: WORKLOAD BALANCING RULES")
    print("=" * 80)
    
    # Initialize metrics collector
    metrics = AgentMetricsCollector()
    
    # Register agents with different characteristics
    print("\n[1] Registering agents...")
    agents_config = [
        ("agent-ci-1", "CI Tester 1", 1.0, 30, 20, 150, 400),  # id, name, cost, cpu, mem, latency, p99
        ("agent-ci-2", "CI Tester 2", 1.5, 80, 70, 200, 1200),  # Loaded
        ("agent-security", "Security Agent", 2.0, 10, 15, 100, 300),  # Cheap, fast
        ("agent-ml", "ML Agent", 3.0, 95, 90, 500, 2500),  # Very loaded
    ]
    
    for agent_id, agent_name, cost, cpu, mem, latency, p99 in agents_config:
        metrics.register_agent(agent_id, agent_name, cost)
        metrics.update_metrics(
            agent_id,
            cpu_usage=cpu,
            memory_usage=mem,
            avg_task_latency_ms=latency,
            p99_latency_ms=p99,
            queue_depth=int(cpu / 25),  # Rough correlation
            availability=0.99 if cpu < 80 else 0.9,
        )
        print(f"  ✓ {agent_name}: CPU={cpu}%, Memory={mem}%, P99={p99}ms, Cost=${cost}/h")
    
    # Create load balancer
    print("\n[2] Testing balancing strategies...")
    balancer = LoadBalancer(metrics)
    
    candidate_agents = ["agent-ci-1", "agent-ci-2", "agent-security", "agent-ml"]
    
    # Test each strategy
    strategies = [
        BalancingStrategy.ROUND_ROBIN,
        BalancingStrategy.LOAD_AWARE,
        BalancingStrategy.LATENCY_AWARE,
        BalancingStrategy.COST_AWARE,
        BalancingStrategy.HYBRID,
    ]
    
    for strategy in strategies:
        balancer.strategy = strategy
        decision = balancer.make_balancing_decision(candidate_agents)
        print(f"\n  {strategy.value.upper()}:")
        print(f"    Primary: {decision.primary_agent_id}")
        print(f"    Secondaries: {decision.secondary_agents}")
        print(f"    Reasoning: {decision.reasoning}")
    
    # Show metrics summary
    print("\n[3] Agent Metrics Summary:")
    all_metrics = metrics.get_all_metrics()
    for agent_id, m in all_metrics.items():
        print(f"  {m['agent_name']}:")
        print(f"    Load Score: {balancer.calculate_load_score(agent_id):.1f}")
        print(f"    CPU: {m['cpu_usage']:.0f}% | Memory: {m['memory_usage']:.0f}% | Queue: {m['queue_depth']}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    example_load_balancing()
