"""
Throughput Optimizer for Performance Agent
Optimizes system throughput and identifies bottlenecks
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

RANDOM_SEED = 47

@dataclass
class ThroughputSample:
    """Single throughput measurement"""
    timestamp: datetime
    requests_per_second: float
    active_connections: int
    queue_depth: int

class ThroughputOptimizer:
    """Optimize system throughput"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.samples: List[ThroughputSample] = []
        self.target_rps = 1000.0  # Target: >1000 req/s
        self.initialized = True
    
    def record_throughput(
        self,
        rps: float,
        connections: int,
        queue_depth: int
    ) -> None:
        """Record throughput measurement"""
        sample = ThroughputSample(
            timestamp=datetime.now(),
            requests_per_second=rps,
            active_connections=connections,
            queue_depth=queue_depth
        )
        self.samples.append(sample)
    
    def get_average_throughput(self, window_minutes: int = 5) -> float:
        """Calculate average throughput over time window"""
        if not self.samples:
            return 0.0
        
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        recent = [s for s in self.samples if s.timestamp >= cutoff]
        
        if not recent:
            return 0.0
        
        return sum(s.requests_per_second for s in recent) / len(recent)
    
    def identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        if not self.samples:
            return bottlenecks
        
        recent = self.samples[-100:] if len(self.samples) >= 100 else self.samples
        
        # Check average throughput
        avg_rps = sum(s.requests_per_second for s in recent) / len(recent)
        if avg_rps < self.target_rps:
            bottlenecks.append(f"throughput_below_target: {avg_rps:.1f} < {self.target_rps}")
        
        # Check queue depth
        avg_queue = sum(s.queue_depth for s in recent) / len(recent)
        if avg_queue > 100:
            bottlenecks.append(f"high_queue_depth: {avg_queue:.1f}")
        
        # Check connection usage
        avg_conn = sum(s.active_connections for s in recent) / len(recent)
        if avg_conn > 500:
            bottlenecks.append(f"high_connection_count: {avg_conn:.1f}")
        
        return bottlenecks
    
    def suggest_optimizations(self) -> List[str]:
        """Suggest throughput optimizations"""
        suggestions = []
        bottlenecks = self.identify_bottlenecks()
        
        for bottleneck in bottlenecks:
            if "throughput_below_target" in bottleneck:
                suggestions.append("Scale horizontally: add more worker instances")
                suggestions.append("Enable connection pooling")
            elif "high_queue_depth" in bottleneck:
                suggestions.append("Increase worker threads")
                suggestions.append("Implement request prioritization")
            elif "high_connection_count" in bottleneck:
                suggestions.append("Enable connection reuse")
                suggestions.append("Implement connection limits")
        
        return suggestions
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get optimizer metrics"""
        return {
            "seed": self.seed,
            "total_samples": len(self.samples),
            "average_throughput": self.get_average_throughput(),
            "target_rps": self.target_rps,
            "bottlenecks": self.identify_bottlenecks(),
            "optimizations": self.suggest_optimizations(),
            "initialized": self.initialized
        }


def create_optimizer(seed: int = RANDOM_SEED) -> ThroughputOptimizer:
    """Factory function to create throughput optimizer"""
    return ThroughputOptimizer(seed=seed)
