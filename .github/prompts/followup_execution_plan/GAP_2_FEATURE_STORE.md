# Gap 2: Feature Store Implementation

**Priority:** Low  
**Category:** Training & Model Management + Monitoring & Feedback  
**Azure MLOps Capabilities:** Rows 27, 63  
**Current State:** 🟡 Partial (88% complete)

---

## Gap Description

### Current Implementation
- ✅ Tokenization pipeline exists (`src/codex_ml/tokenization/`)
- ✅ Data preprocessing pipelines
- ✅ Dataset manifests with SHA256 validation
- ✅ Data drift detection
- ❌ No dedicated feature store
- ❌ No feature versioning system
- ❌ No feature freshness monitoring
- ❌ No feature reuse across models

### Azure MLOps Requirement (Level 4)
> **Row 27:** "Managed feature store is adopted"  
> **Row 63:** "Feature materialization health and freshness are monitored"  
> Expectation: Centralized feature store with versioning, monitoring, and reuse capabilities.

---

## Objective

Implement a feature store system to enable:
1. Centralized feature definition and storage
2. Feature versioning and lineage tracking
3. Feature freshness and health monitoring
4. Feature reuse across multiple models
5. Point-in-time correct feature retrieval

---

## Implementation Tasks

### Task 1: Feature Store Core Module
**File:** `src/codex_ml/features/feature_store.py`

```python
"""Feature store implementation for centralized feature management."""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        return {
            "name": self.name,
            "version": self.version,
            "dtype": self.dtype,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
        }


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
    transform_fn: callable
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
```

### Task 2: Feature Monitoring
**File:** `src/codex_ml/features/monitoring.py`

```python
"""Feature store monitoring and health checks."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

__all__ = ["FeatureHealthMonitor", "FeatureHealthStatus"]


@dataclass
class FeatureHealthStatus:
    """Health status for a feature.
    
    Attributes:
        feature_name: Feature name
        is_healthy: Whether feature is healthy
        last_updated: Last update timestamp
        freshness_minutes: Minutes since last update
        error_count: Number of errors in monitoring window
        warnings: List of warning messages
    """
    feature_name: str
    is_healthy: bool
    last_updated: str
    freshness_minutes: float
    error_count: int = 0
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class FeatureHealthMonitor:
    """Monitor feature health and freshness."""
    
    def __init__(self, freshness_threshold_minutes: int = 60):
        """Initialize feature health monitor.
        
        Args:
            freshness_threshold_minutes: Max minutes before feature is stale
        """
        self.freshness_threshold = timedelta(minutes=freshness_threshold_minutes)
        self.feature_updates: Dict[str, datetime] = {}
        self.error_counts: Dict[str, int] = {}
    
    def record_feature_update(self, feature_name: str):
        """Record feature update timestamp.
        
        Args:
            feature_name: Feature name
        """
        self.feature_updates[feature_name] = datetime.now()
        logger.debug(f"Recorded update for feature: {feature_name}")
    
    def record_feature_error(self, feature_name: str):
        """Record feature error.
        
        Args:
            feature_name: Feature name
        """
        self.error_counts[feature_name] = self.error_counts.get(feature_name, 0) + 1
        logger.warning(f"Recorded error for feature: {feature_name}")
    
    def check_feature_health(self, feature_name: str) -> FeatureHealthStatus:
        """Check health of a feature.
        
        Args:
            feature_name: Feature name
            
        Returns:
            Feature health status
        """
        now = datetime.now()
        last_updated = self.feature_updates.get(feature_name)
        
        if not last_updated:
            return FeatureHealthStatus(
                feature_name=feature_name,
                is_healthy=False,
                last_updated="never",
                freshness_minutes=float('inf'),
                error_count=0,
                warnings=["Feature has never been updated"],
            )
        
        age = now - last_updated
        freshness_minutes = age.total_seconds() / 60
        error_count = self.error_counts.get(feature_name, 0)
        
        warnings = []
        is_healthy = True
        
        if age > self.freshness_threshold:
            warnings.append(f"Feature is stale (>{self.freshness_threshold.total_seconds()/60:.0f} min)")
            is_healthy = False
        
        if error_count > 0:
            warnings.append(f"{error_count} errors in monitoring window")
            if error_count > 5:
                is_healthy = False
        
        return FeatureHealthStatus(
            feature_name=feature_name,
            is_healthy=is_healthy,
            last_updated=last_updated.isoformat(),
            freshness_minutes=freshness_minutes,
            error_count=error_count,
            warnings=warnings,
        )
    
    def check_all_features(self, feature_names: List[str]) -> Dict[str, FeatureHealthStatus]:
        """Check health of all features.
        
        Args:
            feature_names: List of feature names to check
            
        Returns:
            Dictionary mapping feature names to health status
        """
        return {
            name: self.check_feature_health(name)
            for name in feature_names
        }
    
    def reset_error_counts(self):
        """Reset error counts for all features."""
        self.error_counts.clear()
        logger.info("Reset error counts for all features")
```

### Task 3: Feature Store CLI
**File:** `src/codex_ml/cli/features.py`

```python
"""CLI for feature store management."""
import json
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from codex_ml.features.feature_store import FeatureStore
from codex_ml.features.monitoring import FeatureHealthMonitor

app = typer.Typer(help="Feature store management commands")
console = Console()


@app.command()
def list_features(
    store_path: Path = typer.Option(".codex/feature_store", help="Feature store path"),
):
    """List all registered features."""
    store = FeatureStore(store_path)
    features = store.list_features()
    
    console.print(f"\n[bold]Registered Features ({len(features)}):[/bold]")
    for name in sorted(features):
        console.print(f"  • {name}")


@app.command()
def check_health(
    store_path: Path = typer.Option(".codex/feature_store", help="Feature store path"),
    freshness_threshold: int = typer.Option(60, help="Freshness threshold (minutes)"),
):
    """Check health of all features."""
    store = FeatureStore(store_path)
    monitor = FeatureHealthMonitor(freshness_threshold_minutes=freshness_threshold)
    
    features = store.list_features()
    health_status = monitor.check_all_features(features)
    
    table = Table(title="Feature Health Status")
    table.add_column("Feature", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Freshness", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Warnings")
    
    for name, status in health_status.items():
        status_emoji = "✅" if status.is_healthy else "❌"
        freshness = f"{status.freshness_minutes:.1f}m" if status.freshness_minutes != float('inf') else "∞"
        warnings_str = "; ".join(status.warnings) if status.warnings else ""
        
        table.add_row(
            name,
            status_emoji,
            freshness,
            str(status.error_count),
            warnings_str,
        )
    
    console.print(table)


@app.command()
def export_metadata(
    store_path: Path = typer.Option(".codex/feature_store", help="Feature store path"),
    output: Path = typer.Option("features_metadata.json", help="Output file"),
):
    """Export feature metadata to JSON."""
    store = FeatureStore(store_path)
    
    metadata = {}
    for name in store.list_features():
        meta = store.get_feature_metadata(name)
        if meta:
            metadata[name] = meta.to_dict()
    
    with open(output, "w") as f:
        json.dump(metadata, f, indent=2)
    
    console.print(f"✅ Exported metadata for {len(metadata)} features to {output}")


if __name__ == "__main__":
    app()
```

### Task 4: Example Feature Definitions
**File:** `examples/features/text_features.py`

```python
"""Example feature definitions for text processing."""
from codex_ml.features.feature_store import Feature, FeatureGroup, FeatureMetadata
from datetime import datetime


def create_text_features() -> FeatureGroup:
    """Create text processing feature group."""
    
    # Define features
    token_count = Feature(
        name="token_count",
        transform_fn=lambda inputs: len(inputs["text"].split()),
        metadata=FeatureMetadata(
            name="token_count",
            version="1.0.0",
            dtype="int",
            description="Number of tokens in text",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags={"category": "text_stats"},
        ),
    )
    
    char_count = Feature(
        name="char_count",
        transform_fn=lambda inputs: len(inputs["text"]),
        metadata=FeatureMetadata(
            name="char_count",
            version="1.0.0",
            dtype="int",
            description="Number of characters in text",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags={"category": "text_stats"},
        ),
    )
    
    avg_word_length = Feature(
        name="avg_word_length",
        transform_fn=lambda inputs: sum(len(w) for w in inputs["text"].split()) / max(len(inputs["text"].split()), 1),
        dependencies=["token_count"],
        metadata=FeatureMetadata(
            name="avg_word_length",
            version="1.0.0",
            dtype="float",
            description="Average word length",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags={"category": "text_stats"},
        ),
    )
    
    return FeatureGroup(
        name="text_features",
        features=[token_count, char_count, avg_word_length],
        version="1.0.0",
        description="Basic text processing features",
    )
```

### Task 5: Integration Tests
**File:** `tests/test_feature_store.py`

```python
"""Tests for feature store."""
import pytest
from pathlib import Path
from codex_ml.features.feature_store import Feature, FeatureGroup, FeatureStore
from codex_ml.features.monitoring import FeatureHealthMonitor


def test_feature_store_basic(tmp_path):
    """Test basic feature store operations."""
    store = FeatureStore(tmp_path / "store")
    
    # Create feature group
    feature = Feature(
        name="test_feature",
        transform_fn=lambda x: x["value"] * 2,
    )
    group = FeatureGroup(
        name="test_group",
        features=[feature],
        version="1.0.0",
    )
    
    # Register
    store.register_feature_group(group)
    
    # Retrieve
    retrieved = store.get_feature_group("test_group")
    assert retrieved is not None
    assert retrieved.version == "1.0.0"


def test_feature_materialization(tmp_path):
    """Test feature materialization."""
    store = FeatureStore(tmp_path / "store")
    
    feature = Feature(
        name="double",
        transform_fn=lambda x: x["value"] * 2,
    )
    group = FeatureGroup(
        name="math",
        features=[feature],
        version="1.0.0",
    )
    store.register_feature_group(group)
    
    # Materialize
    results = store.materialize_features(
        ["double"],
        {"value": 5},
    )
    
    assert results["double"] == 10


def test_feature_health_monitoring():
    """Test feature health monitoring."""
    monitor = FeatureHealthMonitor(freshness_threshold_minutes=1)
    
    # Record update
    monitor.record_feature_update("test_feature")
    
    # Check health
    status = monitor.check_feature_health("test_feature")
    assert status.is_healthy
    assert status.freshness_minutes < 1


def test_feature_cache(tmp_path):
    """Test feature caching."""
    store = FeatureStore(tmp_path / "store")
    
    call_count = {"count": 0}
    
    def expensive_fn(x):
        call_count["count"] += 1
        return x["value"] ** 2
    
    feature = Feature(name="expensive", transform_fn=expensive_fn)
    group = FeatureGroup(name="test", features=[feature], version="1.0.0")
    store.register_feature_group(group)
    
    # First call - should compute
    result1 = store.materialize_features(["expensive"], {"value": 3}, cache=True)
    assert result1["expensive"] == 9
    assert call_count["count"] == 1
    
    # Second call - should use cache
    result2 = store.materialize_features(["expensive"], {"value": 3}, cache=True)
    assert result2["expensive"] == 9
    assert call_count["count"] == 1  # Not incremented
```

---

## Documentation Updates

### New Files to Create
1. `docs/features/feature_store_guide.md` - Feature store usage guide
2. `docs/features/feature_monitoring.md` - Monitoring and health checks
3. `examples/features/` - Example feature definitions

### Updates Required
1. `README.md` - Add feature store section
2. `AGENTS.md` - Document feature store usage
3. `docs/API_REFERENCE.md` - Add feature store API documentation

---

## Success Criteria

✅ **Complete when:**
1. Feature store core implementation complete
2. Feature health monitoring functional
3. CLI commands working
4. Integration tests passing (>80% coverage)
5. Example feature definitions created
6. Documentation complete
7. Azure MLOps capability rows 27, 63 marked as ✅ Met

**Expected Capability Improvement:**
- Training & Model Management: 88% → 100% (+12%)
- Monitoring & Feedback: 92% → 100% (+8%)
- Overall Azure MLOps Score: 94% → 97% (+3%)

---

## References

- Current tokenization pipeline: `src/codex_ml/tokenization/`
- Dataset manifests: `src/codex_ml/utils/repro.py`
- Data drift detection: `src/codex_ml/monitoring/drift_detection.py`
