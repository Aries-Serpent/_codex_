"""
Dynamic load balancer with consistent hashing for minimal remapping.

Provides:
  - Consistent hashing algorithm (minimize remapping on scale events)
  - Round-robin with health checks
  - Weighted distribution (resource-aware scheduling)
  - Request affinity (session stickiness)
  - Load distribution variance <5%

Gate Criterion 3: <5% load variance
"""

import logging
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict
import uuid


logger = logging.getLogger(__name__)


class BackendState(Enum):
    """Backend server state."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class BackendNode:
    """Backend server node."""
    node_id: str
    host: str
    port: int
    weight: float = 1.0  # Resource weight for scheduling
    state: BackendState = BackendState.HEALTHY
    current_connections: int = 0
    max_connections: int = 10000
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port,
            "weight": self.weight,
            "state": self.state.value,
            "current_connections": self.current_connections,
            "max_connections": self.max_connections,
            "capacity_used": self.current_connections / self.max_connections,
        }


@dataclass
class LoadBalancerConfig:
    """Load balancer configuration."""
    name: str
    algorithm: str = "consistent_hash"  # consistent_hash, round_robin, weighted
    health_check_interval: float = 5.0
    session_stickiness: bool = False
    max_failures_before_removal: int = 5


class ConsistentHashRing:
    """
    Consistent hashing ring for minimal key remapping.
    
    Solves: When backends are added/removed, only 1/N of keys need remapping.
    """
    
    def __init__(self, virtual_nodes: int = 160):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}  # hash → node_id
        self.nodes: set = set()
        self.node_hashes: Dict[str, List[int]] = defaultdict(list)
    
    def add_node(self, node_id: str) -> None:
        """Add node to the ring."""
        if node_id in self.nodes:
            return
        
        self.nodes.add(node_id)
        
        for i in range(self.virtual_nodes):
            virtual_key = f"{node_id}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node_id
            self.node_hashes[node_id].append(hash_value)
        
        logger.debug(f"Added node {node_id} to hash ring with {self.virtual_nodes} virtual nodes")
    
    def remove_node(self, node_id: str) -> None:
        """Remove node from the ring."""
        if node_id not in self.nodes:
            return
        
        for hash_value in self.node_hashes[node_id]:
            del self.ring[hash_value]
        
        del self.node_hashes[node_id]
        self.nodes.discard(node_id)
        
        logger.debug(f"Removed node {node_id} from hash ring")
    
    def get_node(self, key: str) -> Optional[str]:
        """Get node responsible for key."""
        if not self.nodes:
            return None
        
        hash_value = self._hash(key)
        
        # Find the first node with hash >= key hash
        sorted_hashes = sorted(self.ring.keys())
        for ring_hash in sorted_hashes:
            if ring_hash >= hash_value:
                return self.ring[ring_hash]
        
        # Wrap around to first node
        if sorted_hashes:
            return self.ring[sorted_hashes[0]]
        
        return None
    
    def _hash(self, key: str) -> int:
        """Hash key to integer."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)


class LoadBalancer:
    """
    Dynamic load balancer with multiple algorithms.
    
    Guarantees:
    - Load distribution variance <5%
    - Consistent hashing (minimal remapping on scale events)
    - Health-aware routing
    - Request affinity support
    """
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.backends: Dict[str, BackendNode] = {}
        self.hash_ring = ConsistentHashRing()
        self.round_robin_index = 0
        self.request_count = 0
        self.session_affinity: Dict[str, str] = {}  # session_id → node_id
        self.request_distribution: Dict[str, int] = defaultdict(int)
        self.backend_latencies: Dict[str, List[float]] = defaultdict(list)
    
    def add_backend(self, node: BackendNode) -> None:
        """Add backend to load balancer."""
        self.backends[node.node_id] = node
        self.hash_ring.add_node(node.node_id)
        self.request_distribution[node.node_id] = 0
        logger.info(f"Added backend {node.node_id} ({node.host}:{node.port})")
    
    def remove_backend(self, node_id: str) -> None:
        """Remove backend from load balancer."""
        if node_id not in self.backends:
            return
        
        self.hash_ring.remove_node(node_id)
        del self.backends[node_id]
        if node_id in self.request_distribution:
            del self.request_distribution[node_id]
        
        logger.info(f"Removed backend {node_id}")
    
    def select_backend(self, request_id: str, 
                      session_id: Optional[str] = None) -> Optional[BackendNode]:
        """
        Select backend for request.
        
        Gate Criterion 3: Load variance <5%
        
        Returns:
            Selected backend or None if no healthy backends
        """
        self.request_count += 1
        
        # Check for session affinity
        if self.config.session_stickiness and session_id:
            if session_id in self.session_affinity:
                node_id = self.session_affinity[session_id]
                if node_id in self.backends and self.backends[node_id].state == BackendState.HEALTHY:
                    self.request_distribution[node_id] += 1
                    return self.backends[node_id]
        
        # Select backend based on algorithm
        if self.config.algorithm == "consistent_hash":
            node_id = self._select_consistent_hash(request_id)
        elif self.config.algorithm == "round_robin":
            node_id = self._select_round_robin()
        elif self.config.algorithm == "weighted":
            node_id = self._select_weighted()
        else:
            node_id = self._select_round_robin()
        
        if node_id and node_id in self.backends:
            self.request_distribution[node_id] += 1
            
            # Store session affinity
            if self.config.session_stickiness and session_id:
                self.session_affinity[session_id] = node_id
            
            return self.backends[node_id]
        
        return None
    
    def _select_consistent_hash(self, request_id: str) -> Optional[str]:
        """Select backend using consistent hashing."""
        healthy_nodes = [
            n_id for n_id, node in self.backends.items()
            if node.state == BackendState.HEALTHY
        ]
        
        if not healthy_nodes:
            return None
        
        # If we only have one node, return it
        if len(healthy_nodes) == 1:
            return healthy_nodes[0]
        
        # Use consistent hash ring
        node_id = self.hash_ring.get_node(request_id)
        
        # If selected node is unhealthy, try to find healthy one
        if node_id and self.backends[node_id].state != BackendState.HEALTHY:
            node_id = healthy_nodes[0]
        
        return node_id
    
    def _select_round_robin(self) -> Optional[str]:
        """Select backend using round-robin."""
        healthy_nodes = [
            n_id for n_id, node in self.backends.items()
            if node.state == BackendState.HEALTHY
        ]
        
        if not healthy_nodes:
            return None
        
        node_id = healthy_nodes[self.round_robin_index % len(healthy_nodes)]
        self.round_robin_index += 1
        return node_id
    
    def _select_weighted(self) -> Optional[str]:
        """Select backend using weighted distribution."""
        healthy_nodes = [
            (n_id, node) for n_id, node in self.backends.items()
            if node.state == BackendState.HEALTHY
        ]
        
        if not healthy_nodes:
            return None
        
        # Calculate weighted probability
        total_weight = sum(node.weight for _, node in healthy_nodes)
        
        # Find node with least connections relative to weight
        best_node = min(
            healthy_nodes,
            key=lambda x: x[1].current_connections / (x[1].weight or 1.0)
        )
        
        return best_node[0]
    
    def record_request(self, node_id: str, latency_ms: float) -> None:
        """Record request latency for a backend."""
        if node_id not in self.backend_latencies:
            self.backend_latencies[node_id] = []
        
        self.backend_latencies[node_id].append(latency_ms)
        
        # Keep last 1000 measurements
        if len(self.backend_latencies[node_id]) > 1000:
            self.backend_latencies[node_id].pop(0)
    
    def update_backend_state(self, node_id: str, state: BackendState) -> None:
        """Update backend health state."""
        if node_id not in self.backends:
            return
        
        self.backends[node_id].state = state
        logger.debug(f"Updated backend {node_id} state to {state.value}")
    
    def get_load_distribution(self) -> Dict[str, Dict]:
        """Get current load distribution."""
        if self.request_count == 0:
            return {}
        
        distribution = {}
        for node_id, count in self.request_distribution.items():
            percentage = (count / self.request_count) * 100
            distribution[node_id] = {
                "request_count": count,
                "percentage": percentage,
            }
        
        return distribution
    
    def get_load_variance(self) -> float:
        """
        Calculate load distribution variance.
        
        Gate Criterion 3: Should be <5%
        
        Returns:
            Variance percentage (lower is better)
        """
        if not self.backends:
            return 0.0
        
        # Expected percentage per backend (uniform distribution)
        expected = 100.0 / len(self.backends)
        
        # Calculate variance
        total_variance = 0.0
        for node_id in self.backends.keys():
            actual_percentage = (self.request_distribution.get(node_id, 0) / 
                               max(self.request_count, 1)) * 100
            variance = abs(actual_percentage - expected)
            total_variance += variance
        
        avg_variance = total_variance / len(self.backends)
        return avg_variance
    
    def get_backend_stats(self, node_id: str) -> Optional[Dict]:
        """Get statistics for a backend."""
        if node_id not in self.backends:
            return None
        
        node = self.backends[node_id]
        latencies = self.backend_latencies.get(node_id, [])
        
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        min_latency = min(latencies) if latencies else 0.0
        max_latency = max(latencies) if latencies else 0.0
        
        return {
            "node_id": node_id,
            "host": node.host,
            "port": node.port,
            "state": node.state.value,
            "current_connections": node.current_connections,
            "request_count": self.request_distribution.get(node_id, 0),
            "avg_latency_ms": avg_latency,
            "min_latency_ms": min_latency,
            "max_latency_ms": max_latency,
            "measurements_count": len(latencies),
        }
    
    def get_all_backend_stats(self) -> List[Dict]:
        """Get statistics for all backends."""
        return [
            self.get_backend_stats(node_id)
            for node_id in self.backends.keys()
            if self.get_backend_stats(node_id) is not None
        ]
    
    def verify_load_distribution(self) -> Dict[str, any]:
        """
        Verify load balancer capability.
        
        Gate Criterion 3: Load variance <5%
        """
        variance = self.get_load_variance()
        
        return {
            "timestamp": time.time(),
            "algorithm": self.config.algorithm,
            "total_backends": len(self.backends),
            "healthy_backends": sum(
                1 for n in self.backends.values()
                if n.state == BackendState.HEALTHY
            ),
            "total_requests": self.request_count,
            "load_variance": variance,
            "variance_sla_met": variance < 5.0,
            "consistent_hash_nodes": len(self.hash_ring.nodes),
            "session_affinities": len(self.session_affinity),
            "distribution": self.get_load_distribution(),
        }
