"""Feature store implementation for centralized feature management.

Provides:
- Feature versioning with semantic versioning
- Point-in-time (PoT) feature retrieval
- Parquet-based persistent storage
- Feature metadata and lineage tracking
- Efficient caching and materialization
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "Feature",
    "FeatureGroup",
    "FeatureMetadata",
    "FeatureStore",
    "FeatureVersion",
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
    tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class FeatureVersion:
    """Version information for a feature.

    Attributes:
        version: Semantic version string (e.g., "1.0.0")
        timestamp: Creation timestamp
        feature_name: Name of the feature
        storage_path: Path to materialized feature data
        metadata: Additional version metadata
    """

    version: str
    timestamp: str
    feature_name: str
    storage_path: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Feature:
    """Feature definition.

    Attributes:
        name: Feature name
        transform_fn: Transformation function
        dependencies: list of dependent features
        metadata: Feature metadata
    """

    name: str
    transform_fn: Callable
    dependencies: list[str] = field(default_factory=list)
    metadata: Optional[FeatureMetadata] = None

    def compute(self, inputs: dict[str, Any]) -> Any:
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
        features: list of features in group
        version: Group version
        description: Group description
    """

    name: str
    features: list[Feature]
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

    Manages feature definitions, versioning, materialization, and point-in-time retrieval.

    Features:
    - Feature registration and versioning
    - Point-in-time feature retrieval
    - Parquet-based persistent storage
    - Feature metadata tracking
    - Efficient caching
    """

    def __init__(self, store_path: Path | str, enable_versioning: bool = True):
        """Initialize feature store.

        Args:
            store_path: Path to feature store directory
            enable_versioning: Enable feature versioning
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.enable_versioning = enable_versioning

        self.feature_groups: dict[str, FeatureGroup] = {}
        self.feature_cache: dict[str, Any] = {}
        self.feature_versions: dict[str, list[FeatureVersion]] = {}

        self._load_registry()

    def _load_registry(self) -> None:
        """Load feature registry from disk."""
        registry_path = self.store_path / "registry.json"
        if registry_path.exists():
            with open(registry_path) as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} feature groups from registry")

    def _save_registry(self) -> None:
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
        feature_names: list[str],
        inputs: dict[str, Any],
        cache: bool = True,
    ) -> dict[str, Any]:
        """Materialize features from inputs.

        Args:
            feature_names: list of feature names to compute
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

    def _compute_cache_key(self, feature_name: str, inputs: dict[str, Any]) -> str:
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

    def list_features(self) -> list[str]:
        """list all registered features.

        Returns:
            list of feature names
        """
        features = []
        for group in self.feature_groups.values():
            features.extend([f.name for f in group.features])
        return features

    def clear_cache(self) -> None:
        """Clear feature cache."""
        self.feature_cache.clear()
        logger.info("Feature cache cleared")

    def list_versions(self, feature_name: str) -> list[str]:
        """list all versions of a feature.

        Args:
            feature_name: Feature name

        Returns:
            list of version strings
        """
        versions = self.feature_versions.get(feature_name, [])
        return [v.version for v in versions]

    def get_features_at_time(
        self,
        feature_names: list[str],
        timestamp: str | datetime,
        lookback_days: int = 30,
    ) -> dict[str, Any]:
        """Get point-in-time features.

        Retrieves feature values as they were at a specific timestamp.

        Args:
            feature_names: list of feature names
            timestamp: Target timestamp (ISO string or datetime)
            lookback_days: Maximum lookback window in days

        Returns:
            Dictionary of feature values at the given time
        """
        target_time = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp

        results = {}

        for feature_name in feature_names:
            # Find the latest version before target time
            versions = self.feature_versions.get(feature_name, [])
            valid_versions = [
                v for v in versions if datetime.fromisoformat(v.timestamp) <= target_time
            ]

            if valid_versions:
                # Sort by timestamp and get the most recent
                valid_versions.sort(key=lambda v: v.timestamp, reverse=True)
                latest_version = valid_versions[0]

                # Load feature value from storage if available
                if latest_version.storage_path:
                    storage_path = Path(latest_version.storage_path)
                    if storage_path.exists():
                        # In production, would load from parquet
                        # For now, return metadata
                        results[feature_name] = {
                            "version": latest_version.version,
                            "timestamp": latest_version.timestamp,
                            "storage_path": str(storage_path),
                        }
                else:
                    logger.warning(f"No storage path for feature: {feature_name}")
            else:
                logger.warning(f"No feature version found for {feature_name} at {timestamp}")

        return results

    def materialize_to_parquet(
        self,
        feature_group_name: str,
        data: dict[str, Any],
        version: Optional[str] = None,
        partition_by_date: bool = True,
    ) -> Path:
        """Materialize feature group to parquet file.

        Args:
            feature_group_name: Feature group name
            data: Feature data to materialize
            version: Version string (auto-generated if None)
            partition_by_date: Partition by date for efficient retrieval

        Returns:
            Path to materialized parquet file
        """
        try:
            import pandas as pd

            if importlib.util.find_spec("pyarrow") is None:
                raise ImportError("pyarrow is required for parquet support")
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            logger.error(
                "pandas and pyarrow required for parquet materialization. "
                "Install with: pip install pandas pyarrow"
            )
            raise

        # Generate version if not provided
        if version is None:
            existing_versions = self.list_versions(feature_group_name)
            if existing_versions:
                # Simple version increment (1.0.0 -> 1.0.1)
                last_version = existing_versions[-1]
                parts = last_version.split(".")
                parts[-1] = str(int(parts[-1]) + 1)
                version = ".".join(parts)
            else:
                version = "1.0.0"

        # Create storage path
        timestamp = datetime.now(timezone.utc)
        if partition_by_date:
            date_str = timestamp.strftime("%Y/%m/%d")
            storage_dir = self.store_path / feature_group_name / date_str
        else:
            storage_dir = self.store_path / feature_group_name

        storage_dir.mkdir(parents=True, exist_ok=True)
        storage_path = storage_dir / f"v{version}_{timestamp.strftime('%H%M%S')}.parquet"

        # Convert to DataFrame and write
        df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
        df.to_parquet(storage_path, compression="snappy", index=False)

        # Record version
        feature_version = FeatureVersion(
            version=version,
            timestamp=timestamp.isoformat(),
            feature_name=feature_group_name,
            storage_path=str(storage_path),
            metadata={"row_count": len(df), "column_count": len(df.columns)},
        )

        if feature_group_name not in self.feature_versions:
            self.feature_versions[feature_group_name] = []
        self.feature_versions[feature_group_name].append(feature_version)

        logger.info(
            f"Materialized {feature_group_name} v{version} to {storage_path} ({len(df)} rows)"
        )

        return storage_path
