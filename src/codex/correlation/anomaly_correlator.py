"""
Anomaly Correlation Engine - Multi-system anomaly collection and correlation

Implements temporal, spatial, and magnitude correlation across 6+ systems:
- CI/CD System (workflow failures, timeouts)
- RAG Module (retrieval failures, latency spikes)
- Auth System (token failures, rate limiting)
- Performance Monitor (latency anomalies, throughput drops)
- Coverage System (coverage regressions, gate failures)
- Security Scanner (vulnerabilities, policy violations)

Target: >85% correlation accuracy, <500ms latency per anomaly
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================


class AnomalySystem(Enum):
    """Supported anomaly systems"""
    CI_CD = "ci_cd"
    RAG = "rag"
    AUTH = "auth"
    PERFORMANCE = "performance"
    COVERAGE = "coverage"
    SECURITY = "security"


class CorrelationType(Enum):
    """Types of anomaly correlation"""
    TEMPORAL = "temporal"  # Anomalies within time window
    SPATIAL = "spatial"    # Related systems/dependencies
    MAGNITUDE = "magnitude"  # Related metric changes


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Anomaly:
    """Individual anomaly event"""
    system: AnomalySystem
    timestamp: datetime
    metric_name: str
    metric_value: float
    baseline_value: float
    severity: AlertSeverity
    description: str
    tags: Dict[str, str] = field(default_factory=dict)
    
    def zscore(self) -> float:
        """Calculate z-score magnitude"""
        if self.baseline_value == 0:
            return abs(self.metric_value)
        return abs((self.metric_value - self.baseline_value) / max(abs(self.baseline_value), 0.01))


@dataclass
class CorrelatedAnomaly:
    """Group of correlated anomalies with root cause"""
    id: str
    anomalies: List[Anomaly]
    correlation_type: CorrelationType
    correlation_confidence: float  # 0-1
    primary_system: AnomalySystem
    correlated_systems: Set[AnomalySystem] = field(default_factory=set)
    temporal_window_ms: int = 300000  # 5 minutes default
    root_cause_inferred: Optional[str] = None
    root_cause_confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        self.correlated_systems = {a.system for a in self.anomalies}


@dataclass
class AnomalySnapshot:
    """Time-stamped snapshot of anomalies for batching"""
    timestamp: datetime
    anomalies: List[Anomaly]
    system_counts: Dict[AnomalySystem, int] = field(default_factory=dict)
    
    def __post_init__(self):
        for anomaly in self.anomalies:
            self.system_counts[anomaly.system] = self.system_counts.get(anomaly.system, 0) + 1


# ============================================================================
# ANOMALY COLLECTOR
# ============================================================================


class AnomalyCollector:
    """
    Collects anomalies from 6+ systems and maintains in-memory queue.
    
    Target: <100ms per collection cycle for all systems
    """
    
    def __init__(self, max_history: int = 10000):
        """Initialize collector with anomaly queue"""
        self.max_history = max_history
        self.anomalies: List[Anomaly] = []
        self.system_feeds: Dict[AnomalySystem, List[Anomaly]] = defaultdict(list)
        
    def collect_from_system(self, system: AnomalySystem, anomalies: List[Anomaly]) -> None:
        """Receive anomaly batch from system"""
        for anomaly in anomalies:
            anomaly.system = system
            self.anomalies.append(anomaly)
            self.system_feeds[system].append(anomaly)
        
        # Maintain history limit
        if len(self.anomalies) > self.max_history:
            self.anomalies = self.anomalies[-self.max_history:]
    
    def get_recent_anomalies(self, 
                            lookback_ms: int = 300000) -> List[Anomaly]:
        """Get anomalies within lookback window (default 5 minutes)"""
        cutoff = datetime.utcnow() - timedelta(milliseconds=lookback_ms)
        return [a for a in self.anomalies if a.timestamp >= cutoff]
    
    def get_system_anomalies(self, 
                            system: AnomalySystem,
                            lookback_ms: int = 300000) -> List[Anomaly]:
        """Get anomalies for specific system"""
        cutoff = datetime.utcnow() - timedelta(milliseconds=lookback_ms)
        return [a for a in self.system_feeds.get(system, []) 
                if a.timestamp >= cutoff]
    
    def clear_old_anomalies(self, max_age_ms: int = 3600000) -> int:
        """Remove anomalies older than max_age (default 1 hour)"""
        cutoff = datetime.utcnow() - timedelta(milliseconds=max_age_ms)
        before = len(self.anomalies)
        self.anomalies = [a for a in self.anomalies if a.timestamp >= cutoff]
        return before - len(self.anomalies)


# ============================================================================
# TEMPORAL CORRELATOR
# ============================================================================


class TemporalCorrelator:
    """
    Correlates anomalies that occur within time window (default 5 minutes).
    
    Target: >85% accuracy on temporal windows
    """
    
    def __init__(self, window_ms: int = 300000, min_anomalies: int = 2):
        """
        Initialize temporal correlator.
        
        Args:
            window_ms: Time window for correlation (default 5 minutes)
            min_anomalies: Minimum anomalies to form correlation (default 2)
        """
        self.window_ms = window_ms
        self.min_anomalies = min_anomalies
    
    def correlate(self, anomalies: List[Anomaly]) -> List[CorrelatedAnomaly]:
        """Correlate anomalies by temporal proximity"""
        if len(anomalies) < self.min_anomalies:
            return []
        
        # Sort by timestamp
        sorted_anomalies = sorted(anomalies, key=lambda a: a.timestamp)
        correlated_groups: List[CorrelatedAnomaly] = []
        
        i = 0
        while i < len(sorted_anomalies):
            group = [sorted_anomalies[i]]
            anchor_time = sorted_anomalies[i].timestamp
            window_end = anchor_time + timedelta(milliseconds=self.window_ms)
            
            j = i + 1
            while j < len(sorted_anomalies) and sorted_anomalies[j].timestamp <= window_end:
                group.append(sorted_anomalies[j])
                j += 1
            
            # Only create correlation if we have multiple anomalies
            if len(group) >= self.min_anomalies:
                # Calculate temporal confidence based on time distribution
                time_spans = [(group[k].timestamp - group[k-1].timestamp).total_seconds() 
                              for k in range(1, len(group))]
                np.mean(time_spans) if time_spans else 0
                max_spacing = np.max(time_spans) if time_spans else self.window_ms / 1000
                
                # Confidence: anomalies closer together = higher confidence
                temporal_confidence = 1.0 - min(max_spacing / (self.window_ms / 1000), 1.0)
                
                correlated = CorrelatedAnomaly(
                    id=f"temporal_{int(anchor_time.timestamp())}_{len(correlated_groups)}",
                    anomalies=group,
                    correlation_type=CorrelationType.TEMPORAL,
                    correlation_confidence=temporal_confidence,
                    primary_system=group[0].system,
                    temporal_window_ms=self.window_ms
                )
                correlated_groups.append(correlated)
            
            i = j if j > i + 1 else i + 1
        
        return correlated_groups


# ============================================================================
# SPATIAL CORRELATOR
# ============================================================================


class SpatialCorrelator:
    """
    Correlates anomalies across dependent systems.
    
    Maintains dependency graph: CI/CD → Performance → RAG, etc.
    
    Target: >85% accuracy on dependency detection
    """
    
    # System dependency graph (which systems can affect which)
    DEPENDENCIES = {
        AnomalySystem.CI_CD: {AnomalySystem.PERFORMANCE, AnomalySystem.COVERAGE},
        AnomalySystem.RAG: {AnomalySystem.PERFORMANCE},
        AnomalySystem.AUTH: {AnomalySystem.PERFORMANCE},
        AnomalySystem.PERFORMANCE: {AnomalySystem.COVERAGE},
        AnomalySystem.COVERAGE: set(),
        AnomalySystem.SECURITY: {AnomalySystem.CI_CD},
    }
    
    REVERSE_DEPENDENCIES = {
        AnomalySystem.CI_CD: {AnomalySystem.SECURITY},
        AnomalySystem.RAG: set(),
        AnomalySystem.AUTH: set(),
        AnomalySystem.PERFORMANCE: {AnomalySystem.CI_CD, AnomalySystem.RAG, 
                                     AnomalySystem.AUTH},
        AnomalySystem.COVERAGE: {AnomalySystem.CI_CD, AnomalySystem.PERFORMANCE},
        AnomalySystem.SECURITY: set(),
    }
    
    def __init__(self, lookback_ms: int = 600000):  # 10 minutes default
        """Initialize spatial correlator"""
        self.lookback_ms = lookback_ms
    
    def correlate(self, anomalies: List[Anomaly]) -> List[CorrelatedAnomaly]:
        """Correlate anomalies across system dependencies"""
        if len(anomalies) < 2:
            return []
        
        correlated_groups: List[CorrelatedAnomaly] = []
        cutoff = datetime.utcnow() - timedelta(milliseconds=self.lookback_ms)
        recent_anomalies = [a for a in anomalies if a.timestamp >= cutoff]
        
        # Group by system
        by_system: Dict[AnomalySystem, List[Anomaly]] = defaultdict(list)
        for anomaly in recent_anomalies:
            by_system[anomaly.system].append(anomaly)
        
        # Find correlations across dependent systems
        processed_systems: Set[AnomalySystem] = set()
        
        for system in by_system:
            if system in processed_systems:
                continue
            
            group = by_system[system]
            
            # Find anomalies in dependent systems
            dependent_systems = self.DEPENDENCIES.get(system, set())
            upstream_systems = self.REVERSE_DEPENDENCIES.get(system, set())
            
            related_anomalies = list(group)
            related_systems = {system}
            
            for dep_system in dependent_systems:
                if dep_system in by_system:
                    related_anomalies.extend(by_system[dep_system])
                    related_systems.add(dep_system)
                    processed_systems.add(dep_system)
            
            for upstream in upstream_systems:
                if upstream in by_system:
                    related_anomalies.extend(by_system[upstream])
                    related_systems.add(upstream)
                    processed_systems.add(upstream)
            
            if len(related_anomalies) >= 2:
                # Spatial confidence based on how many dependencies are involved
                spatial_confidence = min(len(related_systems) / 3.0, 1.0)
                
                correlated = CorrelatedAnomaly(
                    id=f"spatial_{system.value}_{len(correlated_groups)}",
                    anomalies=related_anomalies,
                    correlation_type=CorrelationType.SPATIAL,
                    correlation_confidence=spatial_confidence,
                    primary_system=system,
                )
                correlated_groups.append(correlated)
            
            processed_systems.add(system)
        
        return correlated_groups


# ============================================================================
# MAGNITUDE CORRELATOR
# ============================================================================


class MagnitudeCorrelator:
    """
    Correlates anomalies based on similar magnitude changes.
    
    Example: Memory spike + CPU spike in same window = likely related
    
    Target: >85% accuracy on magnitude correlation
    """
    
    def __init__(self, zscore_threshold: float = 2.0, min_anomalies: int = 2):
        """
        Initialize magnitude correlator.
        
        Args:
            zscore_threshold: Z-score threshold for anomaly grouping
            min_anomalies: Minimum anomalies to form correlation
        """
        self.zscore_threshold = zscore_threshold
        self.min_anomalies = min_anomalies
    
    def correlate(self, anomalies: List[Anomaly]) -> List[CorrelatedAnomaly]:
        """Correlate anomalies by magnitude similarity"""
        if len(anomalies) < self.min_anomalies:
            return []
        
        # Calculate z-scores
        zscores = [a.zscore() for a in anomalies]
        
        # Group anomalies by z-score similarity
        # Anomalies with similar magnitudes (within threshold) are related
        correlated_groups: List[CorrelatedAnomaly] = []
        processed_indices: Set[int] = set()
        
        for i, anomaly_i in enumerate(anomalies):
            if i in processed_indices:
                continue
            
            group = [anomaly_i]
            zscore_i = zscores[i]
            processed_indices.add(i)
            
            for j in range(i + 1, len(anomalies)):
                if j in processed_indices:
                    continue
                
                zscore_j = zscores[j]
                # Anomalies are related if z-scores are within threshold
                # More lenient threshold (2.0) for grouping
                if abs(zscore_i - zscore_j) < 2.0:
                    group.append(anomalies[j])
                    processed_indices.add(j)
            
            if len(group) >= self.min_anomalies:
                # Magnitude confidence based on how similar z-scores are
                group_zscores = [zscores[anomalies.index(a)] for a in group]
                mean_zscore = np.mean(group_zscores)
                zscore_variance = np.var(group_zscores)
                magnitude_confidence = 1.0 / (1.0 + zscore_variance)
                
                correlated = CorrelatedAnomaly(
                    id=f"magnitude_{mean_zscore:.2f}_{len(correlated_groups)}",
                    anomalies=group,
                    correlation_type=CorrelationType.MAGNITUDE,
                    correlation_confidence=magnitude_confidence,
                    primary_system=group[0].system,
                )
                correlated_groups.append(correlated)
        
        return correlated_groups


# ============================================================================
# ALERT AGGREGATOR
# ============================================================================


class AlertAggregator:
    """
    Aggregates correlated anomalies into consolidated alerts.
    
    Suppresses cascading secondary alerts.
    
    Target: 60%+ alert reduction from cascading alerts
    """
    
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize alert aggregator.
        
        Args:
            confidence_threshold: Minimum confidence to include in aggregation
        """
        self.confidence_threshold = confidence_threshold
    
    def aggregate(self, 
                 correlations: List[CorrelatedAnomaly]) -> Tuple[List[CorrelatedAnomaly], int]:
        """
        Aggregate correlations into consolidated alerts.
        
        Returns:
            (consolidated_alerts, suppressed_count)
        """
        if not correlations:
            return [], 0
        
        # Merge overlapping correlations
        consolidated: List[CorrelatedAnomaly] = []
        used_indices: Set[int] = set()
        
        for i, corr_i in enumerate(correlations):
            if i in used_indices:
                continue
            
            if corr_i.correlation_confidence < self.confidence_threshold:
                used_indices.add(i)
                continue
            
            # Merge with other correlations that have significant overlap
            merged_group = [corr_i]
            merged_anomalies = set(id(a) for a in corr_i.anomalies)
            
            for j in range(i + 1, len(correlations)):
                if j in used_indices:
                    continue
                
                corr_j = correlations[j]
                
                # Check for anomaly overlap
                overlap = set(id(a) for a in corr_j.anomalies) & merged_anomalies
                overlap_ratio = len(overlap) / max(
                    len(merged_anomalies),
                    len(set(id(a) for a in corr_j.anomalies))
                )
                
                if overlap_ratio > 0.3:  # 30% overlap threshold
                    merged_group.append(corr_j)
                    merged_anomalies.update(id(a) for a in corr_j.anomalies)
                    used_indices.add(j)
            
            # Combine into single consolidated alert
            all_anomalies = []
            for corr in merged_group:
                all_anomalies.extend(corr.anomalies)
            
            # Remove duplicates
            unique_anomalies = []
            seen_ids = set()
            for anomaly in all_anomalies:
                aid = (anomaly.system, anomaly.timestamp, anomaly.metric_name)
                if aid not in seen_ids:
                    unique_anomalies.append(anomaly)
                    seen_ids.add(aid)
            
            if unique_anomalies:
                # Combine confidence scores (geometric mean)
                combined_confidence = np.prod([corr.correlation_confidence 
                                              for corr in merged_group]) ** (1.0 / len(merged_group))
                
                consolidated_alert = CorrelatedAnomaly(
                    id=f"aggregated_{i}_{len(consolidated)}",
                    anomalies=unique_anomalies,
                    correlation_type=merged_group[0].correlation_type,
                    correlation_confidence=combined_confidence,
                    primary_system=merged_group[0].primary_system,
                )
                consolidated.append(consolidated_alert)
            
            used_indices.add(i)
        
        # Count suppressed secondary alerts
        suppressed_count = max(0, len(correlations) - len(consolidated))
        
        return consolidated, suppressed_count
