"""
A/B Testing Harness for ML Models - Phase 18 Lane B

Manages A/B testing between baseline and quantized models with statistical analysis.
"""

import json
import logging
import random
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """A/B test status enumeration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class TestConfig:
    """A/B test configuration."""
    baseline_version: str
    treatment_version: str
    traffic_split: float = 0.5  # % of traffic to treatment
    minimum_samples: int = 1000  # Minimum samples per variant
    duration_hours: float = 4.0  # Test duration
    confidence_level: float = 0.95  # Statistical confidence
    power: float = 0.80  # Statistical power (1 - beta)
    primary_metric: str = "latency"  # Primary success metric
    metrics_to_track: List[str] = field(default_factory=lambda: [
        "latency", "accuracy", "throughput", "fp_rate"
    ])
    test_name: str = "baseline_vs_quantized"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class MetricPoint:
    """Single metric measurement."""
    timestamp: datetime
    variant: str  # "baseline" or "treatment"
    metric_name: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestMetrics:
    """Aggregated metrics for a test variant."""
    variant_name: str
    sample_count: int
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Latency metrics (ms)
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    latency_mean: float = 0.0
    latency_std: float = 0.0
    
    # Accuracy metrics
    accuracy: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    
    # Throughput metrics
    throughput_qps: float = 0.0
    
    # Derived metrics
    latency_improvement: float = 0.0  # vs baseline
    accuracy_parity: float = 1.0  # ratio to baseline
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "variant_name": self.variant_name,
            "sample_count": self.sample_count,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "latency_p50": self.latency_p50,
            "latency_p95": self.latency_p95,
            "latency_p99": self.latency_p99,
            "latency_mean": self.latency_mean,
            "latency_std": self.latency_std,
            "accuracy": self.accuracy,
            "false_positive_rate": self.false_positive_rate,
            "false_negative_rate": self.false_negative_rate,
            "throughput_qps": self.throughput_qps,
            "latency_improvement": self.latency_improvement,
            "accuracy_parity": self.accuracy_parity,
        }


class ABTestingHarness:
    """Manages A/B testing between two model versions."""
    
    def __init__(self, test_root: Optional[str] = None):
        """Initialize A/B testing harness."""
        self.test_root = Path(test_root or "~/.codex/ab_tests").expanduser()
        self.test_root.mkdir(parents=True, exist_ok=True)
        
        self.config: Optional[TestConfig] = None
        self.test_id: Optional[str] = None
        self.status = TestStatus.INITIALIZING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Metric collection
        self.metrics: List[MetricPoint] = []
        self.baseline_metrics: Optional[TestMetrics] = None
        self.treatment_metrics: Optional[TestMetrics] = None
        self.variant_assignments: Dict[str, str] = {}  # request_id -> variant
        
    def initialize_test(self, config: TestConfig) -> str:
        """Initialize a new A/B test."""
        self.config = config
        self.test_id = f"ab_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.status = TestStatus.RUNNING
        self.start_time = datetime.utcnow()
        
        # Calculate end time
        self.end_time = self.start_time + timedelta(hours=config.duration_hours)
        
        logger.info(
            f"Initialized A/B test {self.test_id}: "
            f"baseline={config.baseline_version}, "
            f"treatment={config.treatment_version}, "
            f"duration={config.duration_hours}h, "
            f"traffic_split={config.traffic_split}"
        )
        
        return self.test_id
    
    def assign_variant(self, request_id: str) -> str:
        """Assign request to a variant based on traffic split."""
        if not self.config:
            raise RuntimeError("Test not initialized")
        
        # Check if already assigned
        if request_id in self.variant_assignments:
            return self.variant_assignments[request_id]
        
        # Assign based on traffic split
        rand = random.random()
        variant = (
            "treatment" if rand < self.config.traffic_split else "baseline"
        )
        
        self.variant_assignments[request_id] = variant
        return variant
    
    def record_metric(
        self,
        request_id: str,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a metric measurement."""
        if not self.config:
            raise RuntimeError("Test not initialized")
        
        variant = self.variant_assignments.get(request_id, "unknown")
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            variant=variant,
            metric_name=metric_name,
            value=value,
            metadata=metadata or {},
        )
        
        self.metrics.append(point)
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze A/B test results."""
        if not self.config:
            raise RuntimeError("Test not initialized")
        
        self.status = TestStatus.ANALYZING
        
        # Group metrics by variant and metric name
        variant_data: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for point in self.metrics:
            variant_data[point.variant][point.metric_name].append(point.value)

        # Calculate metrics for each variant
        baseline_data: Dict[str, List[float]] = variant_data.get("baseline", {})
        treatment_data: Dict[str, List[float]] = variant_data.get("treatment", {})
        
        self.baseline_metrics = self._calculate_metrics(
            "baseline", baseline_data
        )
        self.treatment_metrics = self._calculate_metrics(
            "treatment", treatment_data
        )
        
        # Calculate relative improvements
        if self.baseline_metrics and self.treatment_metrics:
            self.treatment_metrics.latency_improvement = (
                (self.baseline_metrics.latency_mean - self.treatment_metrics.latency_mean)
                / self.baseline_metrics.latency_mean * 100
            ) if self.baseline_metrics.latency_mean > 0 else 0
            
            self.treatment_metrics.accuracy_parity = (
                self.treatment_metrics.accuracy / self.baseline_metrics.accuracy
                if self.baseline_metrics.accuracy > 0 else 1.0
            )
        
        self.status = TestStatus.COMPLETE
        
        return self._generate_report()
    
    def _calculate_metrics(
        self,
        variant_name: str,
        variant_data: Dict[str, List[float]],
    ) -> TestMetrics:
        """Calculate metrics for a variant."""
        now = datetime.utcnow()
        
        metrics = TestMetrics(
            variant_name=variant_name,
            sample_count=len(variant_data.get("latency", [])),
            start_time=self.start_time or now,
            end_time=now,
        )
        
        # Latency percentiles
        if "latency" in variant_data and variant_data["latency"]:
            latencies = np.array(variant_data["latency"])
            metrics.latency_p50 = float(np.percentile(latencies, 50))
            metrics.latency_p95 = float(np.percentile(latencies, 95))
            metrics.latency_p99 = float(np.percentile(latencies, 99))
            metrics.latency_mean = float(np.mean(latencies))
            metrics.latency_std = float(np.std(latencies))
        
        # Accuracy
        if "accuracy" in variant_data and variant_data["accuracy"]:
            metrics.accuracy = float(np.mean(variant_data["accuracy"]))
        
        # False positive rate
        if "fp_rate" in variant_data and variant_data["fp_rate"]:
            metrics.false_positive_rate = float(np.mean(variant_data["fp_rate"]))
        
        # Throughput
        if "throughput" in variant_data and variant_data["throughput"]:
            metrics.throughput_qps = float(np.mean(variant_data["throughput"]))
        
        return metrics
    
    def perform_statistical_test(self) -> Dict[str, Any]:
        """Perform statistical significance test."""
        if not self.baseline_metrics or not self.treatment_metrics:
            return {"error": "Metrics not available"}

        config = self.config
        if config is None:
            return {"error": "Test not initialized"}

        # T-test for latency
        baseline_latencies = [
            p.value for p in self.metrics
            if p.variant == "baseline" and p.metric_name == "latency"
        ]
        treatment_latencies = [
            p.value for p in self.metrics
            if p.variant == "treatment" and p.metric_name == "latency"
        ]

        from scipy import stats

        if baseline_latencies and treatment_latencies:
            t_stat, p_value = stats.ttest_ind(baseline_latencies, treatment_latencies)
            is_significant = p_value < (1 - config.confidence_level)
        else:
            t_stat, p_value, is_significant = 0, 1.0, False

        return {
            "test_type": "t-test",
            "metric": "latency",
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "is_significant": is_significant,
            "confidence_level": config.confidence_level,
            "baseline_mean": self.baseline_metrics.latency_mean,
            "treatment_mean": self.treatment_metrics.latency_mean,
            "improvement_percent": self.treatment_metrics.latency_improvement,
        }

    def _generate_report(self) -> Dict[str, Any]:
        """Generate test report."""
        stats_test = self.perform_statistical_test()
        config = self.config
        if config is None:
            return {"error": "Test not initialized"}

        return {
            "test_id": self.test_id,
            "config": config.to_dict(),
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "baseline_metrics": self.baseline_metrics.to_dict() if self.baseline_metrics else None,
            "treatment_metrics": self.treatment_metrics.to_dict() if self.treatment_metrics else None,
            "statistical_test": stats_test,
            "total_samples": len(self.metrics),
        }
    
    def save_results(self) -> str:
        """Save test results to disk."""
        if not self.test_id:
            raise RuntimeError("Test not initialized")
        
        results = self._generate_report()
        results_file = self.test_root / f"{self.test_id}_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Saved test results to {results_file}")
        return str(results_file)
    
    def is_running(self) -> bool:
        """Check if test is currently running."""
        if not self.end_time:
            return self.status == TestStatus.RUNNING
        return datetime.utcnow() < self.end_time and self.status == TestStatus.RUNNING
    
    def get_elapsed_time(self) -> timedelta:
        """Get elapsed test time."""
        start = self.start_time or datetime.utcnow()
        return datetime.utcnow() - start
    
    def get_progress(self) -> Dict[str, Any]:
        """Get test progress."""
        if not self.config or not self.start_time:
            return {}
        
        elapsed = self.get_elapsed_time()
        total_duration = timedelta(hours=self.config.duration_hours)
        progress_pct = min(100.0, (elapsed.total_seconds() / total_duration.total_seconds()) * 100)
        
        return {
            "test_id": self.test_id,
            "status": self.status.value,
            "elapsed_seconds": elapsed.total_seconds(),
            "total_seconds": total_duration.total_seconds(),
            "progress_percent": progress_pct,
            "total_samples": len(self.metrics),
            "baseline_samples": len([
                p for p in self.metrics if p.variant == "baseline"
            ]),
            "treatment_samples": len([
                p for p in self.metrics if p.variant == "treatment"
            ]),
            "minimum_samples_met": (
                len([p for p in self.metrics if p.variant == "baseline"]) >= self.config.minimum_samples
                and len([p for p in self.metrics if p.variant == "treatment"]) >= self.config.minimum_samples
            ),
        }
