"""Comprehensive tests for data handling capability.

Tests cover:
- Schema validation
- Streaming and shuffling determinism
- Data leakage detection
- Imbalance checks
- Dataset versioning
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Schema Validation Tests ---


class DataSchema:
    """Data schema definition."""

    def __init__(self, name: str):
        self.name = name
        self.fields: dict[str, dict[str, Any]] = {}
        self.required: set[str] = set()

    def add_field(
        self, name: str, dtype: str, required: bool = False, nullable: bool = True
    ) -> None:
        """Add field to schema."""
        self.fields[name] = {"dtype": dtype, "nullable": nullable}
        if required:
            self.required.add(name)

    def validate(self, record: dict[str, Any]) -> list[str]:
        """Validate record against schema."""
        errors = []
        for field in self.required:
            if field not in record:
                errors.append(f"Missing required field: {field}")
        for field, value in record.items():
            if field in self.fields:
                spec = self.fields[field]
                if value is None and not spec["nullable"]:
                    errors.append(f"Field {field} cannot be null")
        return errors


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_create_schema(self):
        """Create data schema."""
        schema = DataSchema("user")
        schema.add_field("id", "int", required=True)
        schema.add_field("name", "str", required=True)
        schema.add_field("email", "str", required=False)
        assert len(schema.fields) == 3, "Collection must not be empty"

    def test_validate_valid_record(self):
        """Valid record passes validation."""
        schema = DataSchema("user")
        schema.add_field("id", "int", required=True)
        schema.add_field("name", "str", required=True)
        errors = schema.validate({"id": 1, "name": "Test"})
        assert len(errors) == 0, "Errors must not be empty"

    def test_validate_missing_required(self):
        """Missing required field fails."""
        schema = DataSchema("user")
        schema.add_field("id", "int", required=True)
        errors = schema.validate({})
        assert "Missing required field: id" in errors, "Error should be raised or set"

    def test_validate_null_not_allowed(self):
        """Null in non-nullable field fails."""
        schema = DataSchema("user")
        schema.add_field("id", "int", required=True, nullable=False)
        errors = schema.validate({"id": None})
        assert any("cannot be null" in e for e in errors), "Error should be raised or set"


# --- Streaming Determinism Tests ---


class DeterministicShuffle:
    """Deterministic shuffling for reproducibility."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def shuffle(self, data: list) -> list:
        """Shuffle data deterministically."""
        import random

        rng = random.Random(self.seed)
        result = data.copy()
        rng.shuffle(result)
        return result

    def get_indices(self, length: int) -> list[int]:
        """Get shuffled indices."""
        return self.shuffle(list(range(length)))


class TestDeterministicShuffle:
    """Tests for deterministic shuffling."""

    def test_reproducible_shuffle(self):
        """Same seed produces same shuffle."""
        data = list(range(100))
        s1 = DeterministicShuffle(seed=42)
        s2 = DeterministicShuffle(seed=42)
        assert s1.shuffle(data) == s2.shuffle(data), "Data must not be empty"

    def test_different_seeds(self):
        """Different seeds produce different shuffles."""
        data = list(range(100))
        s1 = DeterministicShuffle(seed=42)
        s2 = DeterministicShuffle(seed=123)
        assert s1.shuffle(data) != s2.shuffle(data), "Data must not be empty"

    @given(st.integers(min_value=0, max_value=1000000))
    @settings(max_examples=20)
    def test_shuffle_reproducible_property(self, seed: int):
        """Property: shuffle is reproducible for any seed."""
        data = list(range(50))
        s1 = DeterministicShuffle(seed=seed)
        s2 = DeterministicShuffle(seed=seed)
        assert s1.shuffle(data) == s2.shuffle(data), "Data must not be empty"


# --- Data Leakage Detection Tests ---


class LeakageDetector:
    """Detect data leakage between splits."""

    def __init__(self):
        self.id_field = "id"

    def detect_overlap(
        self, train: list[dict], val: list[dict], test: list[dict]
    ) -> dict[str, Any]:
        """Detect ID overlap between splits."""
        train_ids = {r[self.id_field] for r in train if self.id_field in r}
        val_ids = {r[self.id_field] for r in val if self.id_field in r}
        test_ids = {r[self.id_field] for r in test if self.id_field in r}

        return {
            "train_val_overlap": train_ids & val_ids,
            "train_test_overlap": train_ids & test_ids,
            "val_test_overlap": val_ids & test_ids,
            "has_leakage": bool(train_ids & val_ids) or bool(train_ids & test_ids),
        }

    def detect_feature_leakage(self, features: list[str], target: str) -> list[str]:
        """Detect features that might leak target information."""
        suspicious = []
        target_parts = target.lower().split("_")
        for f in features:
            f_lower = f.lower()
            if target.lower() in f_lower or any(
                part in f_lower for part in target_parts if len(part) > 3
            ):
                suspicious.append(f)
        return suspicious


class TestLeakageDetection:
    """Tests for leakage detection."""

    def test_no_leakage(self):
        """No leakage between splits."""
        detector = LeakageDetector()
        train = [{"id": 1}, {"id": 2}]
        val = [{"id": 3}]
        test = [{"id": 4}]
        result = detector.detect_overlap(train, val, test)
        assert not result["has_leakage"], "Result must not be empty"

    def test_detect_train_val_leakage(self):
        """Detect train-val overlap."""
        detector = LeakageDetector()
        train = [{"id": 1}, {"id": 2}]
        val = [{"id": 2}, {"id": 3}]  # ID 2 is in both
        test = [{"id": 4}]
        result = detector.detect_overlap(train, val, test)
        assert result["has_leakage"], "Result must not be empty"
        assert 2 in result["train_val_overlap"], "Result must not be empty"

    def test_detect_feature_leakage(self):
        """Detect suspicious features."""
        detector = LeakageDetector()
        features = ["age", "income", "target_encoded", "label_mean"]
        suspicious = detector.detect_feature_leakage(features, "target")
        assert "target_encoded" in suspicious, "Condition must be true"


# --- Imbalance Detection Tests ---


class ImbalanceChecker:
    """Check for class imbalance."""

    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold

    def compute_distribution(self, labels: list) -> dict[Any, float]:
        """Compute label distribution."""
        counts = Counter(labels)
        total = len(labels)
        return {k: v / total for k, v in counts.items()}

    def is_imbalanced(self, labels: list) -> bool:
        """Check if data is imbalanced."""
        dist = self.compute_distribution(labels)
        if not dist:
            return False
        min_ratio = min(dist.values())
        return min_ratio < self.threshold

    def get_imbalance_ratio(self, labels: list) -> float:
        """Get imbalance ratio (minority/majority)."""
        dist = self.compute_distribution(labels)
        if not dist:
            return 1.0
        return min(dist.values()) / max(dist.values())


class TestImbalanceDetection:
    """Tests for imbalance detection."""

    def test_balanced_data(self):
        """Balanced data is not imbalanced."""
        checker = ImbalanceChecker(threshold=0.1)
        labels = [0] * 50 + [1] * 50
        assert not checker.is_imbalanced(labels), "Condition must be true"

    def test_imbalanced_data(self):
        """Imbalanced data is detected."""
        checker = ImbalanceChecker(threshold=0.1)
        labels = [0] * 95 + [1] * 5
        assert checker.is_imbalanced(labels), "Condition must be true"

    def test_imbalance_ratio(self):
        """Compute imbalance ratio."""
        checker = ImbalanceChecker()
        labels = [0] * 80 + [1] * 20
        ratio = checker.get_imbalance_ratio(labels)
        assert 0.24 < ratio < 0.26, "24 is not valid"


# --- Dataset Versioning Tests ---


class DatasetVersion:
    """Dataset version information."""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.checksum: str = ""
        self.row_count: int = 0
        self.columns: list[str] = []

    def compute_checksum(self, data: list[dict]) -> str:
        """Compute dataset checksum."""
        canonical = json.dumps(data, sort_keys=True)
        self.checksum = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        return self.checksum

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "checksum": self.checksum,
            "row_count": self.row_count,
            "columns": self.columns,
        }


class DatasetRegistry:
    """Registry for dataset versions."""

    def __init__(self):
        self.datasets: dict[str, DatasetVersion] = {}

    def register(self, version: DatasetVersion) -> None:
        """Register dataset version."""
        key = f"{version.name}:{version.version}"
        self.datasets[key] = version

    def get(self, name: str, version: str) -> DatasetVersion | None:
        """Get dataset version."""
        return self.datasets.get(f"{name}:{version}")

    def list_versions(self, name: str) -> list[str]:
        """List all versions of a dataset."""
        return [v.version for k, v in self.datasets.items() if v.name == name]


class TestDatasetVersioning:
    """Tests for dataset versioning."""

    def test_create_version(self):
        """Create dataset version."""
        version = DatasetVersion("train", "1.0.0")
        assert version.name == "train", "name is not valid"

    def test_compute_checksum(self):
        """Compute dataset checksum."""
        version = DatasetVersion("test", "1.0.0")
        data = [{"a": 1}, {"a": 2}]
        checksum = version.compute_checksum(data)
        assert len(checksum) == 16, "Checksum must not be empty"

    def test_checksum_deterministic(self):
        """Checksum is deterministic."""
        data = [{"x": 1}, {"x": 2}]
        v1 = DatasetVersion("test", "1.0.0")
        v2 = DatasetVersion("test", "1.0.0")
        assert v1.compute_checksum(data) == v2.compute_checksum(data), "Data must not be empty"

    def test_registry(self):
        """Register and retrieve datasets."""
        registry = DatasetRegistry()
        v1 = DatasetVersion("train", "1.0.0")
        v2 = DatasetVersion("train", "1.1.0")
        registry.register(v1)
        registry.register(v2)
        versions = registry.list_versions("train")
        assert len(versions) == 2, "Versions must not be empty"


# --- Data Loader Tests ---


class DataLoader:
    """Data loader with batching."""

    def __init__(self, data: list, batch_size: int = 32, shuffle: bool = False, seed: int = 42):
        self.data = data
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.seed = seed

    def __len__(self) -> int:
        return (len(self.data) + self.batch_size - 1) // self.batch_size

    def get_batches(self) -> list[list]:
        """Get all batches."""
        data = self.data
        if self.shuffle:
            shuffler = DeterministicShuffle(self.seed)
            data = shuffler.shuffle(data)
        batches = []
        for i in range(0, len(data), self.batch_size):
            batches.append(data[i : i + self.batch_size])
        return batches


class TestDataLoader:
    """Tests for data loader."""

    def test_batch_count(self):
        """Correct number of batches."""
        data = list(range(100))
        loader = DataLoader(data, batch_size=32)
        assert len(loader) == 4, "Loader must not be empty"

    def test_batches_content(self):
        """Batches contain all data."""
        data = list(range(100))
        loader = DataLoader(data, batch_size=32)
        batches = loader.get_batches()
        all_items = [item for batch in batches for item in batch]
        assert sorted(all_items) == sorted(data), "Data must not be empty"

    def test_shuffle_deterministic(self):
        """Shuffled batches are deterministic."""
        data = list(range(100))
        loader1 = DataLoader(data, batch_size=32, shuffle=True, seed=42)
        loader2 = DataLoader(data, batch_size=32, shuffle=True, seed=42)
        assert loader1.get_batches() == loader2.get_batches(), "Condition must be true"


# --- Data Split Tests ---


class DataSplitter:
    """Split data into train/val/test."""

    def __init__(self, train_ratio: float = 0.8, val_ratio: float = 0.1, seed: int = 42):
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = 1.0 - train_ratio - val_ratio
        self.seed = seed

    def split(self, data: list) -> tuple[list, list, list]:
        """Split data into train/val/test."""
        shuffler = DeterministicShuffle(self.seed)
        shuffled = shuffler.shuffle(data)
        n = len(shuffled)
        train_end = int(n * self.train_ratio)
        val_end = train_end + int(n * self.val_ratio)
        return shuffled[:train_end], shuffled[train_end:val_end], shuffled[val_end:]


class TestDataSplitter:
    """Tests for data splitting."""

    def test_split_ratios(self):
        """Split respects ratios approximately."""
        data = list(range(1000))
        splitter = DataSplitter(train_ratio=0.8, val_ratio=0.1)
        train, val, test = splitter.split(data)
        assert 750 < len(train) < 850, "Train must not be empty"
        assert 50 < len(val) < 150, "Val must not be empty"
        assert 50 < len(test) < 150, "Test must not be empty"

    def test_split_no_overlap(self):
        """Splits have no overlap."""
        data = list(range(100))
        splitter = DataSplitter()
        train, val, test = splitter.split(data)
        all_items = train + val + test
        assert len(all_items) == len(set(all_items)), "All_items must not be empty"

    def test_split_deterministic(self):
        """Split is deterministic."""
        data = list(range(100))
        s1 = DataSplitter(seed=42)
        s2 = DataSplitter(seed=42)
        assert s1.split(data) == s2.split(data), "Data must not be empty"
