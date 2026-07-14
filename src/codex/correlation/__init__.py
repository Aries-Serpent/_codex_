"""
Anomaly Correlation Engine - Phase 4E Planset 011

Cross-system anomaly correlation with probabilistic causal inference,
root cause detection, and intelligent alert aggregation.

Modules:
  - anomaly_correlator: Multi-type anomaly correlation (temporal, spatial, magnitude)
  - root_cause_engine: Backward-chaining root cause inference with causal graphs
  - fp_suppressor: Machine learning-based false positive suppression
  - causal_graph: Probabilistic directed acyclic graph (DAG) of system dependencies
"""

from .anomaly_correlator import (
    AnomalyCollector,
    TemporalCorrelator,
    SpatialCorrelator,
    MagnitudeCorrelator,
    AlertAggregator,
    CorrelatedAnomaly,
)
from .root_cause_engine import (
    BackwardChainer,
    RootCauseInference,
    CausalGraph,
    CausalLink,
)
from .fp_suppressor import (
    FalsePositiveClassifier,
    HistoricalTracker,
    SuppressionPolicy,
)

__all__ = [
    "AnomalyCollector",
    "TemporalCorrelator",
    "SpatialCorrelator",
    "MagnitudeCorrelator",
    "AlertAggregator",
    "CorrelatedAnomaly",
    "BackwardChainer",
    "RootCauseInference",
    "CausalGraph",
    "CausalLink",
    "FalsePositiveClassifier",
    "HistoricalTracker",
    "SuppressionPolicy",
]
