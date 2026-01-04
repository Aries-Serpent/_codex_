"""
Latency Monitor for Performance Agent
Tracks request latencies and detects anomalies
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import statistics

RANDOM_SEED = 47  # Performance Monitor Agent seed

@dataclass
class LatencyMetric:
    """Single latency measurement"""
    timestamp: datetime
    endpoint: str
    latency_ms: float
    status_code: int
    metadata: Dict[str, Any]

class LatencyMonitor:
    """Monitor request latencies and detect performance issues"""
    
    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.measurements: List[LatencyMetric] = []
        self.thresholds = {
            "p50": 50.0,   # 50ms
            "p95": 100.0,  # 100ms
            "p99": 200.0   # 200ms
        }
        self.initialized = True
    
    def record_latency(
        self,
        endpoint: str,
        latency_ms: float,
        status_code: int = 200,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a latency measurement"""
        metric = LatencyMetric(
            timestamp=datetime.now(),
            endpoint=endpoint,
            latency_ms=latency_ms,
            status_code=status_code,
            metadata=metadata or {}
        )
        self.measurements.append(metric)
    
    def get_percentiles(self, endpoint: Optional[str] = None) -> Dict[str, float]:
        """Calculate latency percentiles"""
        measurements = self.measurements
        if endpoint:
            measurements = [m for m in measurements if m.endpoint == endpoint]
        
        if not measurements:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        
        latencies = sorted([m.latency_ms for m in measurements])
        n = len(latencies)
        
        return {
            "p50": latencies[int(n * 0.50)] if n > 0 else 0.0,
            "p95": latencies[int(n * 0.95)] if n > 0 else 0.0,
            "p99": latencies[int(n * 0.99)] if n > 0 else 0.0,
        }
    
    def check_thresholds(self, endpoint: Optional[str] = None) -> Dict[str, bool]:
        """Check if latencies exceed thresholds"""
        percentiles = self.get_percentiles(endpoint)
        return {
            "p50_ok": percentiles["p50"] <= self.thresholds["p50"],
            "p95_ok": percentiles["p95"] <= self.thresholds["p95"],
            "p99_ok": percentiles["p99"] <= self.thresholds["p99"],
        }
    
    def detect_anomalies(self, window_size: int = 100) -> List[LatencyMetric]:
        """Detect anomalous latency measurements"""
        if len(self.measurements) < window_size:
            return []
        
        recent = self.measurements[-window_size:]
        latencies = [m.latency_ms for m in recent]
        
        mean = statistics.mean(latencies)
        stdev = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        threshold = mean + (3 * stdev)  # 3 sigma
        
        anomalies = [m for m in recent if m.latency_ms > threshold]
        return anomalies
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get monitoring metrics"""
        percentiles = self.get_percentiles()
        return {
            "seed": self.seed,
            "total_measurements": len(self.measurements),
            "percentiles": percentiles,
            "thresholds_met": self.check_thresholds(),
            "anomaly_count": len(self.detect_anomalies()),
            "initialized": self.initialized
        }


def create_monitor(seed: int = RANDOM_SEED) -> LatencyMonitor:
    """Factory function to create latency monitor"""
    return LatencyMonitor(seed=seed)
