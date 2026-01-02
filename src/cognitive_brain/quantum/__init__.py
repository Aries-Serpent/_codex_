"""
Quantum Module - Quantum-Inspired Agent Enhancements

This module provides quantum-inspired features for enhanced agent intelligence:
- Superposition: Parallel decision path exploration
- Entanglement: Correlated agent state management
- Uncertainty: Adaptive test coverage optimization
- Wave Collapse: Accelerated pattern learning

All features are gated by environment variable flags for gradual rollout.
"""

from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.base import QuantumFeature, QuantumState
from cognitive_brain.quantum.coherence_monitor import (
    CoherenceMonitor,
    Alert,
    AlertLevel,
    AlertThreshold
)

__version__ = "0.1.0"
__all__ = [
    "QuantumConfig",
    "QuantumFeature",
    "QuantumState",
    "CoherenceMonitor",
    "Alert",
    "AlertLevel",
    "AlertThreshold",
]
