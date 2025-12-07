"""Feature store implementation for centralized feature management."""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "Feature",
    "FeatureGroup",
    "FeatureStore",
    "FeatureMetadata",
]


@dataclass
class FeatureMetadata:
    """Metadata for a feature.

    Attributes:
        name: Feature name
        version: Feature version
        dtype: Data type
        description: Human-readable description
        created_at: Creation timestamp
        updated_at: Last update timestamp
        tags: Additional metadata tags
    """

    name: str
    version: str
    dtype: str
    description: str
    created_at: str
    updated_at: str
    tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Feature:
    """Feature definition.

    Attributes:
        name: Feature name
        transform_fn: Transformation function
        dependencies: List of dependent features
        metadata: Feature metadata
    """

    name: str
    transform_fn: Callable
    dependencies: List[str] = field(default_factory=list)
    metadata: Optional[FeatureMetadata] = None

    def compute(self, inputs: Dict[str, Any]) -> Any:
        """Compute feature value from inputs.

        Args:
            inputs: Input data dictionary

        Returns:
            Computed feature value
        """
        return self.transform_fn(inputs)


@dataclass
class FeatureGroup:
    """Group of related features.

    Attributes:
        name: Group name
        features: List of features in group
        version: Group version
        description: Group description
    """

    name: str
    features: List[Feature]
    version: str
    description: str = ""

    def get_feature(self, name: str) -> Optional[Feature]:
        """Get feature by name.

        Args:
            name: Feature name

        Returns:
            Feature if found, None otherwise
        """
        for feature in self.features:
            if feature.name == name:
                return feature
        return None


class FeatureStore:
    """Centralized feature store.

    Manages feature definitions, versioning, and materialization.
    """

    def __init__(self, store_path: Path | str):
        """Initialize feature store.

        Args:
            store_path: Path to feature store directory
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

        self.feature_groups: Dict[str, FeatureGroup] = {}
        self.feature_cache: Dict[str, Any] = {}

        self._load_registry()

    def _load_registry(self):
        """Load feature registry from disk."""
        registry_path = self.store_path / "registry.json"
        if registry_path.exists():
            with open(registry_path) as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} feature groups from registry")

    def _save_registry(self):
        """Save feature registry to disk."""
        registry_path = self.store_path / "registry.json"
        data = {
            name: {
                "version": group.version,
                "description": group.description,
                "features": [f.name for f in group.features],
            }
            for name, group in self.feature_groups.items()
        }
        with open(registry_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data)} feature groups to registry")

    def register_feature_group(self, group: FeatureGroup):
        """Register a feature group.

        Args:
            group: Feature group to register
        """
        self.feature_groups[group.name] = group
        self._save_registry()
        logger.info(f"Registered feature group: {group.name} v{group.version}")

    def get_feature_group(self, name: str, version: Optional[str] = None) -> Optional[FeatureGroup]:
        """Get feature group by name and version.

        Args:
            name: Group name
            version: Group version (latest if None)

        Returns:
            Feature group if found
        """
        group = self.feature_groups.get(name)
        if group and (version is None or group.version == version):
            return group
        return None

    def materialize_features(
        self,
        feature_names: List[str],
        inputs: Dict[str, Any],
        cache: bool = True,
    ) -> Dict[str, Any]:
        """Materialize features from inputs.

        Args:
            feature_names: List of feature names to compute
            inputs: Input data
            cache: Whether to cache results

        Returns:
            Dictionary of computed features
        """
        results = {}

        for name in feature_names:
            # Check cache
            cache_key = self._compute_cache_key(name, inputs)
            if cache and cache_key in self.feature_cache:
                results[name] = self.feature_cache[cache_key]
                continue

            # Find and compute feature
            feature = self._find_feature(name)
            if feature:
                value = feature.compute(inputs)
                results[name] = value

                if cache:
                    self.feature_cache[cache_key] = value
            else:
                logger.warning(f"Feature not found: {name}")

        return results

    def _find_feature(self, name: str) -> Optional[Feature]:
        """Find feature by name across all groups.

        Args:
            name: Feature name

        Returns:
            Feature if found
        """
        for group in self.feature_groups.values():
            feature = group.get_feature(name)
            if feature:
                return feature
        return None

    def _compute_cache_key(self, feature_name: str, inputs: Dict[str, Any]) -> str:
        """Compute cache key for feature.

        Args:
            feature_name: Feature name
            inputs: Input data

        Returns:
            Cache key string
        """
        # Create deterministic hash of inputs
        input_str = json.dumps(inputs, sort_keys=True)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]
        return f"{feature_name}:{input_hash}"

    def get_feature_metadata(self, name: str) -> Optional[FeatureMetadata]:
        """Get metadata for a feature.

        Args:
            name: Feature name

        Returns:
            Feature metadata if found
        """
        feature = self._find_feature(name)
        return feature.metadata if feature else None

    def list_features(self) -> List[str]:
        """List all registered features.

        Returns:
            List of feature names
        """
        features = []
        for group in self.feature_groups.values():
            features.extend([f.name for f in group.features])
        return features

    def clear_cache(self):
        """Clear feature cache."""
        self.feature_cache.clear()
        logger.info("Feature cache cleared")
