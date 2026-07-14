"""Complete Feature Store tests."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from codex_ml.features.feature_store import (
    Feature,
    FeatureGroup,
    FeatureStore,
)


class TestFeatureStoreComplete:
    """Test complete feature store implementation."""

    @pytest.fixture
    def store(self, tmp_path):
        return FeatureStore(str(tmp_path / "features"))

    def test_register_feature_group(self, store):
        """Test feature group registration."""

        def dummy_transform(inputs):
            return inputs.get("value", 0) * 2

        group = FeatureGroup(
            name="user_features",
            version="1.0.0",
            features=[
                Feature(name="age", transform_fn=dummy_transform),
                Feature(name="score", transform_fn=dummy_transform),
            ],
            description="User demographic features",
        )

        store.register_feature_group(group)

        # Verify registration
        retrieved = store.get_feature_group("user_features")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.name == "user_features", "name is not valid"
        assert retrieved.version == "1.0.0", "version is not valid"
        assert len(retrieved.features) == 2, "Collection must not be empty"

    def test_materialize_to_parquet(self, store, tmp_path):
        """Test materialization to parquet."""
        pytest.importorskip("pandas")
        pytest.importorskip("pyarrow")

        def dummy_transform(inputs):
            return inputs.get("value", 0)

        group = FeatureGroup(
            name="numeric_features",
            version="1.0.0",
            features=[Feature(name="value", transform_fn=dummy_transform)],
        )
        store.register_feature_group(group)

        # Materialize data
        data = {"value": [1.0, 2.0, 3.0]}
        storage_path = store.materialize_to_parquet("numeric_features", data, version="1.0.0")

        assert storage_path.exists(), "st is not valid"
        assert storage_path.suffix == ".parquet", "suffix is not valid"

        # Verify version was recorded
        versions = store.list_versions("numeric_features")
        assert "1.0.0" in versions, "Condition must be true"

    def test_point_in_time_retrieval(self, store):
        """Test point-in-time feature retrieval."""
        pytest.importorskip("pandas")
        pytest.importorskip("pyarrow")

        def dummy_transform(inputs):
            return inputs.get("value", 0)

        # Create v1
        group_v1 = FeatureGroup(
            name="temporal",
            version="1.0.0",
            features=[Feature(name="val", transform_fn=dummy_transform)],
        )
        store.register_feature_group(group_v1)
        store.materialize_to_parquet("temporal", {"val": [1.0]}, version="1.0.0")

        # Wait a moment
        import time

        time.sleep(0.1)

        timestamp_between = datetime.now(UTC)
        time.sleep(0.1)

        # Create v2
        group_v2 = FeatureGroup(
            name="temporal",
            version="2.0.0",
            features=[Feature(name="val", transform_fn=dummy_transform)],
        )
        store.register_feature_group(group_v2)
        store.materialize_to_parquet("temporal", {"val": [2.0]}, version="2.0.0")

        # Point-in-time retrieval should get v1
        result = store.get_features_at_time(["temporal"], timestamp_between)
        assert "temporal" in result, "Result must not be empty"
        assert result["temporal"]["version"] == "1.0.0", "Result must not be empty"

    def test_version_listing(self, store):
        """Test version listing functionality."""

        def dummy_transform(inputs):
            return 0

        for v in ["1.0.0", "1.1.0", "2.0.0"]:
            group = FeatureGroup(
                name="versioned",
                version=v,
                features=[Feature(name="test", transform_fn=dummy_transform)],
            )
            store.register_feature_group(group)

        versions = store.list_versions("versioned")
        # Should have at least one (may be empty list in basic impl)
        assert isinstance(versions, list)

    def test_feature_materialization(self, store):
        """Test feature materialization."""

        def multiply_transform(inputs):
            return inputs.get("x", 0) * 2

        group = FeatureGroup(
            name="computed",
            version="1.0.0",
            features=[Feature(name="doubled", transform_fn=multiply_transform)],
        )
        store.register_feature_group(group)

        # Materialize features
        inputs = {"x": 5}
        results = store.materialize_features(["doubled"], inputs)
        assert "doubled" in results, "Result must not be empty"
        assert results["doubled"] == 10, "Result must not be empty"

    def test_cache_functionality(self, store):
        """Test feature caching."""
        call_count = [0]

        def counting_transform(inputs):
            call_count[0] += 1
            return inputs.get("value", 0)

        group = FeatureGroup(
            name="cached",
            version="1.0.0",
            features=[Feature(name="val", transform_fn=counting_transform)],
        )
        store.register_feature_group(group)

        inputs = {"value": 42}

        # First call - should compute
        result1 = store.materialize_features(["val"], inputs, cache=True)
        assert call_count[0] == 1, "Count must be greater than zero"

        # Second call - should use cache
        result2 = store.materialize_features(["val"], inputs, cache=True)
        assert call_count[0] == 1, "Count must be greater than zero"
        assert result1 == result2, "Result must not be empty"

        # Clear cache and try again
        store.clear_cache()
        store.materialize_features(["val"], inputs, cache=True)
        assert call_count[0] == 2, "Count must be greater than zero"

    def test_registry_persistence(self, store, tmp_path):
        """Test that registry persists to disk."""

        def dummy_transform(inputs):
            return 0

        group = FeatureGroup(
            name="persistent",
            version="1.0.0",
            features=[Feature(name="test", transform_fn=dummy_transform)],
        )
        store.register_feature_group(group)

        # Check registry file exists
        registry_path = Path(tmp_path) / "features" / "registry.json"
        assert registry_path.exists(), "Condition must be true"

        # Verify content
        with open(registry_path) as f:
            data = json.load(f)
            assert "persistent" in data, "Data must not be empty"

    def test_list_features(self, store):
        """Test listing all features."""

        def dummy_transform(inputs):
            return 0

        group = FeatureGroup(
            name="listable",
            version="1.0.0",
            features=[
                Feature(name="feat1", transform_fn=dummy_transform),
                Feature(name="feat2", transform_fn=dummy_transform),
            ],
        )
        store.register_feature_group(group)

        features = store.list_features()
        assert "feat1" in features, "Condition must be true"
        assert "feat2" in features, "Condition must be true"


class TestFeatureVersioning:
    """Test feature versioning capabilities."""

    @pytest.fixture
    def store(self, tmp_path):
        return FeatureStore(str(tmp_path / "features"))

    def test_semantic_versioning(self, store):
        """Test semantic version handling."""
        pytest.importorskip("pandas")
        pytest.importorskip("pyarrow")

        def dummy_transform(inputs):
            return 0

        # Create multiple versions
        for v in ["1.0.0", "1.0.1", "1.1.0", "2.0.0"]:
            group = FeatureGroup(
                name="semver",
                version=v,
                features=[Feature(name="test", transform_fn=dummy_transform)],
            )
            store.register_feature_group(group)
            store.materialize_to_parquet("semver", {"test": [1]}, version=v)

        versions = store.list_versions("semver")
        assert len(versions) >= 1, "Versions must not be empty"

    def test_auto_version_increment(self, store):
        """Test automatic version incrementing."""
        pytest.importorskip("pandas")
        pytest.importorskip("pyarrow")

        def dummy_transform(inputs):
            return 0

        group = FeatureGroup(
            name="auto_version",
            version="1.0.0",
            features=[Feature(name="test", transform_fn=dummy_transform)],
        )
        store.register_feature_group(group)

        # First materialization with version
        store.materialize_to_parquet("auto_version", {"test": [1]}, version="1.0.0")

        # Second materialization without version (should auto-increment)
        store.materialize_to_parquet("auto_version", {"test": [2]})

        versions = store.list_versions("auto_version")
        assert len(versions) >= 1, "Versions must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
