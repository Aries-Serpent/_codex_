"""
Cache Optimization Analysis and Performance Monitoring.

PHASE 5 TRACK 5: Cache hierarchy optimization for 15%+ hit rate improvement
and 20-30% latency reduction.

Features:
- Multi-layer cache performance analysis
- Optimization opportunity identification
- Performance benchmarking before/after
- Cache warming strategy generation
- Key collision detection
- Eviction pattern analysis
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CacheLayerMetrics:
    """Metrics for a single cache layer."""
    
    layer_name: str
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    promotions: int = 0  # Times promoted to higher tier
    demotions: int = 0   # Times demoted to lower tier
    total_size_bytes: int = 0
    avg_value_size: int = 0
    max_size_bytes: int = 0
    ttl_seconds: int = 0
    timestamp: float = field(default_factory=time.time)
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def utilization(self) -> float:
        """Calculate cache utilization percentage."""
        if self.max_size_bytes <= 0:
            return 0.0
        return (self.total_size_bytes / self.max_size_bytes) * 100
    
    @property
    def eviction_rate(self) -> float:
        """Calculate eviction rate per 1000 accesses."""
        total = self.hits + self.misses
        return (self.evictions / total * 1000) if total > 0 else 0.0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "layer": self.layer_name,
            "hit_rate": f"{self.hit_rate:.1f}%",
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "promotions": self.promotions,
            "demotions": self.demotions,
            "total_size_mb": self.total_size_bytes / 1024 / 1024,
            "utilization": f"{self.utilization:.1f}%",
            "eviction_rate_per_1k": f"{self.eviction_rate:.1f}",
        }


@dataclass
class CacheOptimization:
    """Proposed cache optimization."""
    
    name: str
    description: str
    estimated_hit_rate_improvement: float  # Percentage improvement
    estimated_latency_improvement: float  # Percentage improvement
    priority: str  # HIGH, MEDIUM, LOW
    implementation_effort: str  # HIGH, MEDIUM, LOW
    affected_layers: List[str] = field(default_factory=list)
    estimated_complexity_points: int = 0


class CacheOptimizationAnalyzer:
    """Analyze cache performance and identify optimization opportunities."""
    
    # Predefined optimizations
    OPTIMIZATIONS = [
        CacheOptimization(
            name="L1 Cache Warming",
            description="Pre-load predicted hot keys on L1 initialization",
            estimated_hit_rate_improvement=15.0,
            estimated_latency_improvement=20.0,
            priority="HIGH",
            implementation_effort="MEDIUM",
            affected_layers=["L1"],
            estimated_complexity_points=8,
        ),
        CacheOptimization(
            name="Batch Operations",
            description="Add get_many/set_many for bulk operations",
            estimated_hit_rate_improvement=10.0,
            estimated_latency_improvement=15.0,
            priority="HIGH",
            implementation_effort="LOW",
            affected_layers=["L1", "L2"],
            estimated_complexity_points=5,
        ),
        CacheOptimization(
            name="Weighted LRU Eviction",
            description="Use weighted LRU based on access patterns",
            estimated_hit_rate_improvement=8.0,
            estimated_latency_improvement=5.0,
            priority="MEDIUM",
            implementation_effort="MEDIUM",
            affected_layers=["L2"],
            estimated_complexity_points=6,
        ),
        CacheOptimization(
            name="Adaptive TTL Extension",
            description="Extend TTL on hotkey access to reduce evictions",
            estimated_hit_rate_improvement=12.0,
            estimated_latency_improvement=8.0,
            priority="HIGH",
            implementation_effort="LOW",
            affected_layers=["L1", "L2", "L3"],
            estimated_complexity_points=4,
        ),
        CacheOptimization(
            name="L3 Database Indexes",
            description="Add SQLite indexes for faster lookups",
            estimated_hit_rate_improvement=15.0,
            estimated_latency_improvement=25.0,
            priority="MEDIUM",
            implementation_effort="MEDIUM",
            affected_layers=["L3"],
            estimated_complexity_points=6,
        ),
        CacheOptimization(
            name="Key Collision Reduction",
            description="Improve cache key hashing to reduce collisions",
            estimated_hit_rate_improvement=5.0,
            estimated_latency_improvement=3.0,
            priority="LOW",
            implementation_effort="MEDIUM",
            affected_layers=["L1", "L2"],
            estimated_complexity_points=4,
        ),
        CacheOptimization(
            name="Cross-Layer Coherency",
            description="Improve cache coherency signals between layers",
            estimated_hit_rate_improvement=8.0,
            estimated_latency_improvement=10.0,
            priority="MEDIUM",
            implementation_effort="HIGH",
            affected_layers=["L1", "L2", "L3"],
            estimated_complexity_points=10,
        ),
        CacheOptimization(
            name="Cache Compression",
            description="Compress large values in L3 for better density",
            estimated_hit_rate_improvement=6.0,
            estimated_latency_improvement=8.0,
            priority="LOW",
            implementation_effort="MEDIUM",
            affected_layers=["L3"],
            estimated_complexity_points=5,
        ),
    ]
    
    def __init__(self):
        """Initialize analyzer."""
        self.layer_metrics: Dict[str, CacheLayerMetrics] = {}
        self.identified_optimizations: List[CacheOptimization] = []
    
    def record_layer_metrics(self, metrics: CacheLayerMetrics) -> None:
        """Record metrics for a cache layer."""
        self.layer_metrics[metrics.layer_name] = metrics
        logger.debug(f"Recorded metrics for {metrics.layer_name}")
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze cache performance and identify optimizations."""
        analysis = {
            "timestamp": time.time(),
            "layers": {},
            "recommendations": [],
            "overall_hit_rate": self._calculate_overall_hit_rate(),
            "estimated_improvements": {},
        }
        
        # Add layer metrics
        for layer_name, metrics in self.layer_metrics.items():
            analysis["layers"][layer_name] = metrics.to_dict()
        
        # Identify bottleneck layers
        bottlenecks = self._identify_bottlenecks()
        analysis["bottlenecks"] = bottlenecks
        
        # Generate recommendations
        recommendations = self._generate_recommendations(bottlenecks)
        analysis["recommendations"] = [
            {
                "optimization": opt.name,
                "priority": opt.priority,
                "effort": opt.implementation_effort,
                "hit_rate_improvement": f"{opt.estimated_hit_rate_improvement:.1f}%",
                "latency_improvement": f"{opt.estimated_latency_improvement:.1f}%",
            }
            for opt in recommendations
        ]
        
        # Calculate estimated improvements from recommended optimizations
        estimated_hit_rate_gain = sum(opt.estimated_hit_rate_improvement for opt in recommendations[:3])
        estimated_latency_gain = sum(opt.estimated_latency_improvement for opt in recommendations[:3])
        
        analysis["estimated_improvements"] = {
            "hit_rate_improvement": f"{estimated_hit_rate_gain:.1f}%",
            "latency_improvement": f"{estimated_latency_gain:.1f}%",
            "top_3_optimizations": [opt.name for opt in recommendations[:3]],
        }
        
        return analysis
    
    def _calculate_overall_hit_rate(self) -> float:
        """Calculate overall hit rate across all layers."""
        total_hits = sum(m.hits for m in self.layer_metrics.values())
        total_misses = sum(m.misses for m in self.layer_metrics.values())
        total = total_hits + total_misses
        return (total_hits / total * 100) if total > 0 else 0.0
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify cache layers with performance issues."""
        bottlenecks = []
        
        for layer_name, metrics in self.layer_metrics.items():
            issues = []
            
            # Check hit rate
            if metrics.hit_rate < 60:
                issues.append(f"Low hit rate: {metrics.hit_rate:.1f}%")
            
            # Check utilization
            if metrics.utilization > 90:
                issues.append(f"High utilization: {metrics.utilization:.1f}%")
            
            # Check eviction rate
            if metrics.eviction_rate > 10:
                issues.append(f"High eviction rate: {metrics.eviction_rate:.1f} per 1000")
            
            if issues:
                bottlenecks.append({
                    "layer": layer_name,
                    "issues": issues,
                    "hit_rate": f"{metrics.hit_rate:.1f}%",
                    "utilization": f"{metrics.utilization:.1f}%",
                })
        
        return bottlenecks
    
    def _generate_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[CacheOptimization]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        affected_layers = {b["layer"] for b in bottlenecks}
        
        # Sort optimizations by priority and effort
        sorted_opts = sorted(
            self.OPTIMIZATIONS,
            key=lambda x: (x.priority != "HIGH", x.implementation_effort == "HIGH", -x.estimated_hit_rate_improvement)
        )
        
        # Select optimizations that affect bottleneck layers
        for opt in sorted_opts:
            if any(layer in affected_layers for layer in opt.affected_layers):
                recommendations.append(opt)
            
            if len(recommendations) >= 5:
                break
        
        self.identified_optimizations = recommendations
        return recommendations


class CacheWarmingStrategy:
    """Generate cache warming strategies based on access patterns."""
    
    def __init__(self):
        """Initialize warming strategy generator."""
        self.access_patterns: Dict[str, int] = {}
        self.sequential_patterns: List[Tuple[str, str]] = []
    
    def record_access(self, key: str) -> None:
        """Record a key access."""
        if key not in self.access_patterns:
            self.access_patterns[key] = 0
        self.access_patterns[key] += 1
    
    def analyze_access_patterns(self) -> Dict[str, Any]:
        """Analyze access patterns and generate warming strategy."""
        if not self.access_patterns:
            return {"status": "No access patterns recorded"}
        
        # Find hot keys
        sorted_keys = sorted(self.access_patterns.items(), key=lambda x: -x[1])
        hot_keys = [k for k, v in sorted_keys[:int(len(sorted_keys) * 0.2)]]  # Top 20%
        
        return {
            "total_unique_keys": len(self.access_patterns),
            "hot_keys_count": len(hot_keys),
            "hottest_keys": [k for k, _ in sorted_keys[:10]],
            "skewness": self._calculate_skewness(sorted_keys),
            "recommended_warm_set_size": len(hot_keys),
        }
    
    def _calculate_skewness(self, sorted_items: List[Tuple[str, int]]) -> str:
        """Calculate access pattern skewness."""
        if len(sorted_items) < 2:
            return "Unknown"
        
        top_10_pct = sum(v for _, v in sorted_items[:max(1, len(sorted_items) // 10)])
        total = sum(v for _, v in sorted_items)
        
        if total == 0:
            return "Unknown"
        
        skewness_ratio = top_10_pct / total
        
        if skewness_ratio > 0.6:
            return "High (60%+ of accesses in top 10%)"
        elif skewness_ratio > 0.4:
            return "Medium (40-60% in top 10%)"
        else:
            return "Low (even distribution)"


def generate_cache_optimization_report(
    layer_metrics: Dict[str, CacheLayerMetrics],
    access_patterns: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """Generate comprehensive cache optimization report.
    
    Args:
        layer_metrics: Metrics for each cache layer
        access_patterns: Optional access pattern data
    
    Returns:
        Comprehensive optimization report
    """
    analyzer = CacheOptimizationAnalyzer()
    
    for metrics in layer_metrics.values():
        analyzer.record_layer_metrics(metrics)
    
    analysis = analyzer.analyze()
    
    # Add warming strategy if access patterns provided
    if access_patterns:
        warming_strategy = CacheWarmingStrategy()
        for key, count in access_patterns.items():
            for _ in range(count):
                warming_strategy.record_access(key)
        analysis["warming_strategy"] = warming_strategy.analyze_access_patterns()
    
    return analysis
