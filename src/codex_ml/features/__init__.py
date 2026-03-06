"""Feature store implementation for centralized feature management."""

__all__ = [
    "Feature",
    "FeatureGroup",
    "FeatureStore",
    "FeatureMetadata",
    "FeatureHealthMonitor",
    "FeatureHealthStatus",
    # SAR-G02: Feast-compatible PoC
    "Entity",
    "FeatureView",
    "FeastCompatibleStore",
    "FeatureServiceResult",
]

from .feast_compat import Entity, FeastCompatibleStore, FeatureServiceResult, FeatureView
from .feature_store import Feature, FeatureGroup, FeatureMetadata, FeatureStore
from .monitoring import FeatureHealthMonitor, FeatureHealthStatus

__version__ = "1.1.0"  # 1.1.0 — SAR-G02 Feast-compat PoC added
