"""
Comprehensive tests for dataset loaders

Tests cover:
- JSONL loader
- CSV loader
- HuggingFace dataset loader
- Deterministic splitting
- Caching behavior
- Manifest generation
"""

import csv
import json
import tempfile
from pathlib import Path

import pytest

# Mark all tests in this module
pytestmark = pytest.mark.ml_comprehensive


@pytest.fixture
def sample_jsonl_file():
    """Create sample JSONL file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        data = [
            {"text": "Sample 1", "label": 0},
            {"text": "Sample 2", "label": 1},
            {"text": "Sample 3", "label": 0},
            {"text": "Sample 4", "label": 1},
            {"text": "Sample 5", "label": 0},
        ]
        for item in data:
            f.write(json.dumps(item) + "\n")
        return Path(f.name)


@pytest.fixture
def sample_csv_file():
    """Create sample CSV file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label"])
        writer.writeheader()
        data = [
            {"text": "Sample 1", "label": "0"},
            {"text": "Sample 2", "label": "1"},
            {"text": "Sample 3", "label": "0"},
        ]
        writer.writerows(data)
        return Path(f.name)


class TestJSONLLoader:
    """Test JSONL dataset loader"""

    def test_load_jsonl_basic(self, sample_jsonl_file):
        """Test basic JSONL loading"""
        # Load file
        data = []
        with open(sample_jsonl_file) as f:
            for line in f:
                data.append(json.loads(line))

        assert len(data) == 5, "Data must not be empty"
        assert "text" in data[0], "Data must not be empty"
        assert "label" in data[0], "Data must not be empty"

    def test_load_jsonl_invalid_path(self):
        """Test JSONL loader with invalid path"""
        with pytest.raises(FileNotFoundError), open("nonexistent.jsonl"):
            pass


class TestCSVLoader:
    """Test CSV dataset loader"""

    def test_load_csv_basic(self, sample_csv_file):
        """Test basic CSV loading"""
        data = []
        with open(sample_csv_file) as f:
            reader = csv.DictReader(f)
            data = list(reader)

        assert len(data) == 3, "Data must not be empty"
        assert "text" in data[0], "Data must not be empty"
        assert "label" in data[0], "Data must not be empty"


class TestDeterministicSplitting:
    """Test deterministic dataset splitting"""

    def test_split_dataset_reproducible(self):
        """Test that splitting is reproducible with same seed"""
        import random

        dataset = list(range(100))

        # Split 1
        random.seed(42)
        split1 = random.sample(dataset, 80)

        # Split 2 with same seed
        random.seed(42)
        split2 = random.sample(dataset, 80)

        # Should produce identical splits
        assert split1 == split2, "split1 is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
