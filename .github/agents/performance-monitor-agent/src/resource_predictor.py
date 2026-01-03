"""
Resource Predictor for Performance Agent
Predicts resource usage patterns and capacity needs
"""
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import random

RANDOM_SEED = 47

@dataclass
class ResourceUsage:
    """Resource usage snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    disk_io_mbps: float
    network_mbps: float

class ResourcePredictor:
    """Predict resource usage and capacity needs"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.history: List[ResourceUsage] = []
        self.initialized = True
    
    def record_usage(
        self,
        cpu: float,
        memory_mb: float,
        disk_mbps: float,
        network_mbps: float
    ) -> None:
        """Record resource usage snapshot"""
        usage = ResourceUsage(
            timestamp=datetime.now(),
            cpu_percent=cpu,
            memory_mb=memory_mb,
            disk_io_mbps=disk_mbps,
            network_mbps=network_mbps
        )
        self.history.append(usage)
    
    def predict_peak_usage(self, resource: str = "cpu") -> float:
        """Predict peak resource usage based on historical patterns"""
        if not self.history:
            return 0.0
        
        # Simple linear extrapolation from recent trend
        recent = self.history[-100:] if len(self.history) >= 100 else self.history
        
        if resource == "cpu":
            values = [r.cpu_percent for r in recent]
        elif resource == "memory":
            values = [r.memory_mb for r in recent]
        elif resource == "disk":
            values = [r.disk_io_mbps for r in recent]
        elif resource == "network":
            values = [r.network_mbps for r in recent]
        else:
            return 0.0
        
        if len(values) < 2:
            return values[0] if values else 0.0
        
        # Calculate trend
        avg = sum(values) / len(values)
        recent_avg = sum(values[-10:]) / min(10, len(values))
        
        # Predict peak as recent trend + 20% buffer
        predicted = recent_avg * 1.2
        
        return predicted
    
    def check_capacity(self) -> Dict[str, bool]:
        """Check if approaching capacity limits"""
        cpu_limit = 80.0  # 80% CPU
        memory_limit = 8192.0  # 8GB
        
        cpu_peak = self.predict_peak_usage("cpu")
        mem_peak = self.predict_peak_usage("memory")
        
        return {
            "cpu_ok": cpu_peak < cpu_limit,
            "memory_ok": mem_peak < memory_limit,
            "capacity_adequate": cpu_peak < cpu_limit and mem_peak < memory_limit
        }
    
    def recommend_scaling(self) -> List[str]:
        """Recommend scaling actions"""
        recommendations = []
        capacity = self.check_capacity()
        
        if not capacity["cpu_ok"]:
            cpu_peak = self.predict_peak_usage("cpu")
            recommendations.append(f"Scale CPU: predicted peak {cpu_peak:.1f}% > 80%")
        
        if not capacity["memory_ok"]:
            mem_peak = self.predict_peak_usage("memory")
            recommendations.append(f"Scale Memory: predicted peak {mem_peak:.1f}MB > 8GB")
        
        return recommendations
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get predictor metrics"""
        return {
            "seed": self.seed,
            "history_size": len(self.history),
            "predicted_cpu": self.predict_peak_usage("cpu"),
            "predicted_memory": self.predict_peak_usage("memory"),
            "capacity_check": self.check_capacity(),
            "scaling_recommendations": self.recommend_scaling(),
            "initialized": self.initialized
        }


def create_predictor(seed: int = RANDOM_SEED) -> ResourcePredictor:
    """Factory function to create resource predictor"""
    return ResourcePredictor(seed=seed)
