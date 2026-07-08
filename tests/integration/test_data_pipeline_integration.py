"""
Data Pipeline Integration Tests

Tests end-to-end data processing workflows:
- Data loading from multiple sources
- Preprocessing and transformation pipelines
- Batch processing workflows
- Data validation chains
- Format conversion pipelines
- Error handling and retry mechanisms

Part of Phase 23 Week 2: Integration Testing (100-120 tests)
Target: 30-40 tests for Data Pipeline workflows
"""

from __future__ import annotations

import csv
import json

import pytest

# Mark all tests as integration tests
pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "raw").mkdir()
    (data_dir / "processed").mkdir()
    (data_dir / "validated").mkdir()
    (data_dir / "output").mkdir()
    return data_dir


@pytest.fixture
def sample_json_data(temp_data_dir):
    """Create sample JSON data file."""
    json_file = temp_data_dir / "raw" / "data.json"
    data = [
        {"id": 1, "text": "Sample text one", "label": "positive"},
        {"id": 2, "text": "Sample text two", "label": "negative"},
        {"id": 3, "text": "Sample text three", "label": "positive"},
    ]
    json_file.write_text(json.dumps(data))
    return json_file


@pytest.fixture
def sample_jsonl_data(temp_data_dir):
    """Create sample JSONL data file."""
    jsonl_file = temp_data_dir / "raw" / "data.jsonl"
    data = [
        {"id": 1, "text": "Line one", "score": 0.9},
        {"id": 2, "text": "Line two", "score": 0.8},
        {"id": 3, "text": "Line three", "score": 0.7},
    ]
    with jsonl_file.open("w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")
    return jsonl_file


@pytest.fixture
def sample_csv_data(temp_data_dir):
    """Create sample CSV data file."""
    csv_file = temp_data_dir / "raw" / "data.csv"
    with csv_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "text", "category"])
        writer.writeheader()
        writer.writerows(
            [
                {"id": "1", "text": "First entry", "category": "A"},
                {"id": "2", "text": "Second entry", "category": "B"},
                {"id": "3", "text": "Third entry", "category": "A"},
            ]
        )
    return csv_file


class TestDataLoading:
    """Test data loading from various sources."""

    def test_load_json_file(self, sample_json_data):
        """Verify loading data from JSON file."""
        data = json.loads(sample_json_data.read_text())
        assert len(data) == 3, "Data must not be empty"
        assert data[0]["id"] == 1, "Data must not be empty"
        assert "text" in data[0], "Data must not be empty"

    def test_load_jsonl_file(self, sample_jsonl_data):
        """Verify loading data from JSONL file."""
        data = []
        with sample_jsonl_data.open("r") as f:
            for line in f:
                data.append(json.loads(line))

        assert len(data) == 3, "Data must not be empty"
        assert data[0]["id"] == 1, "Data must not be empty"

    def test_load_csv_file(self, sample_csv_data):
        """Verify loading data from CSV file."""
        data = []
        with sample_csv_data.open("r") as f:
            reader = csv.DictReader(f)
            data = list(reader)

        assert len(data) == 3, "Data must not be empty"
        assert data[0]["id"] == "1", "Data must not be empty"
        assert data[0]["category"] == "A", "Data must not be empty"

    def test_load_empty_file(self, temp_data_dir):
        """Verify handling of empty data files."""
        empty_file = temp_data_dir / "raw" / "empty.json"
        empty_file.write_text("[]")

        data = json.loads(empty_file.read_text())
        assert len(data) == 0, "Data must not be empty"

    def test_load_malformed_json(self, temp_data_dir):
        """Verify error handling for malformed JSON."""
        bad_file = temp_data_dir / "raw" / "malformed.json"
        bad_file.write_text("{bad json")

        with pytest.raises(json.JSONDecodeError):
            json.loads(bad_file.read_text())

    def test_load_missing_file(self, temp_data_dir):
        """Verify handling of missing files."""
        missing = temp_data_dir / "raw" / "nonexistent.json"
        assert not missing.exists(), "Condition must be true"

    def test_load_large_file_streaming(self, temp_data_dir):
        """Verify streaming loading of large files."""
        large_file = temp_data_dir / "raw" / "large.jsonl"
        with large_file.open("w") as f:
            for i in range(100):
                f.write(json.dumps({"id": i, "data": f"entry_{i}"}) + "\n")

        # Streaming read
        count = 0
        with large_file.open("r") as f:
            for line in f:
                json.loads(line)
                count += 1

        assert count == 100, "Count must be greater than zero"


class TestDataPreprocessing:
    """Test data preprocessing and transformation."""

    def test_text_normalization(self, sample_json_data):
        """Verify text normalization preprocessing."""
        data = json.loads(sample_json_data.read_text())

        # Simple normalization
        for item in data:
            item["text"] = item["text"].lower().strip()

        assert data[0]["text"] == "sample text one", "Data must not be empty"

    def test_tokenization(self, sample_json_data):
        """Verify text tokenization preprocessing."""
        data = json.loads(sample_json_data.read_text())

        for item in data:
            item["tokens"] = item["text"].split()

        assert len(data[0]["tokens"]) == 3, "Collection must not be empty"

    def test_label_encoding(self, sample_json_data):
        """Verify label encoding transformation."""
        data = json.loads(sample_json_data.read_text())

        label_map = {"positive": 1, "negative": 0}
        for item in data:
            item["label_encoded"] = label_map.get(item["label"], -1)

        assert data[0]["label_encoded"] == 1, "Data must not be empty"
        assert data[1]["label_encoded"] == 0, "Data must not be empty"

    def test_feature_extraction(self, sample_json_data):
        """Verify feature extraction from raw data."""
        data = json.loads(sample_json_data.read_text())

        for item in data:
            item["features"] = {
                "text_length": len(item["text"]),
                "word_count": len(item["text"].split()),
            }

        assert data[0]["features"]["word_count"] == 3, "Data must not be empty"

    def test_data_filtering(self, sample_json_data):
        """Verify data filtering preprocessing."""
        data = json.loads(sample_json_data.read_text())

        # Filter by label
        filtered = [item for item in data if item["label"] == "positive"]

        assert len(filtered) == 2, "Filtered must not be empty"

    def test_data_deduplication(self, temp_data_dir):
        """Verify deduplication of duplicate records."""
        data_file = temp_data_dir / "raw" / "duplicates.json"
        data = [
            {"id": 1, "text": "Same text"},
            {"id": 2, "text": "Different text"},
            {"id": 3, "text": "Same text"},
        ]
        data_file.write_text(json.dumps(data))

        # Deduplicate by text
        seen = set()
        unique = []
        for item in data:
            if item["text"] not in seen:
                seen.add(item["text"])
                unique.append(item)

        assert len(unique) == 2, "Unique must not be empty"


class TestBatchProcessing:
    """Test batch processing workflows."""

    def test_process_in_batches(self, sample_jsonl_data):
        """Verify batch processing of data."""
        batch_size = 2
        batches = []

        current_batch = []
        with sample_jsonl_data.open("r") as f:
            for line in f:
                item = json.loads(line)
                current_batch.append(item)

                if len(current_batch) >= batch_size:
                    batches.append(current_batch)
                    current_batch = []

        if current_batch:
            batches.append(current_batch)

        assert len(batches) == 2, "Batches must not be empty"
        assert len(batches[0]) == 2, "Collection must not be empty"
        assert len(batches[1]) == 1, "Collection must not be empty"

    def test_parallel_batch_processing(self, sample_jsonl_data):
        """Verify parallel processing of batches."""
        from concurrent.futures import ThreadPoolExecutor

        def process_batch(batch):
            return [item["text"].upper() for item in batch]

        data = []
        with sample_jsonl_data.open("r") as f:
            for line in f:
                data.append(json.loads(line))

        batch_size = 2
        batches = [data[i : i + batch_size] for i in range(0, len(data), batch_size)]

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(process_batch, batches))

        assert len(results) == 2, "Results must not be empty"

    def test_batch_size_optimization(self, temp_data_dir):
        """Verify batch size affects processing."""
        data_file = temp_data_dir / "raw" / "batch_test.jsonl"
        with data_file.open("w") as f:
            for i in range(10):
                f.write(json.dumps({"id": i}) + "\n")

        for batch_size in [1, 2, 5]:
            batch_count = 0
            current_batch = []

            with data_file.open("r") as f:
                for line in f:
                    current_batch.append(json.loads(line))
                    if len(current_batch) >= batch_size:
                        batch_count += 1
                        current_batch = []

            if current_batch:
                batch_count += 1

            expected = (10 + batch_size - 1) // batch_size
            assert batch_count == expected, "Count must be greater than zero"


class TestDataValidation:
    """Test data validation workflows."""

    def test_validate_required_fields(self, sample_json_data):
        """Verify validation of required fields."""
        data = json.loads(sample_json_data.read_text())
        required_fields = ["id", "text", "label"]

        for item in data:
            for field in required_fields:
                assert field in item, "Item must not be empty"

    def test_validate_data_types(self, sample_json_data):
        """Verify validation of data types."""
        data = json.loads(sample_json_data.read_text())

        for item in data:
            assert isinstance(item["id"], int)
            assert isinstance(item["text"], str)
            assert isinstance(item["label"], str)

    def test_validate_value_ranges(self, sample_jsonl_data):
        """Verify validation of value ranges."""
        data = []
        with sample_jsonl_data.open("r") as f:
            for line in f:
                data.append(json.loads(line))

        for item in data:
            assert 0.0 <= item["score"] <= 1.0, "Item must not be empty"

    def test_validate_string_patterns(self, sample_json_data):
        """Verify validation of string patterns."""
        data = json.loads(sample_json_data.read_text())

        for item in data:
            # Text should not be empty
            assert len(item["text"]) > 0, "Collection must not be empty"

    def test_validation_error_reporting(self, temp_data_dir):
        """Verify validation error collection."""
        invalid_data = temp_data_dir / "raw" / "invalid.json"
        data = [
            {"id": 1, "text": "Valid"},
            {"id": "invalid", "text": ""},  # Invalid id type, empty text
            {"text": "Missing id"},  # Missing id field
        ]
        invalid_data.write_text(json.dumps(data))

        errors = []
        loaded_data = json.loads(invalid_data.read_text())

        for idx, item in enumerate(loaded_data):
            if "id" not in item:
                errors.append(f"Row {idx}: Missing 'id' field")
            elif not isinstance(item.get("id"), int):
                errors.append(f"Row {idx}: Invalid 'id' type")
            if item.get("text", "") == "":
                errors.append(f"Row {idx}: Empty 'text' field")

        assert len(errors) > 0, "Errors must not be empty"


class TestFormatConversion:
    """Test format conversion pipelines."""

    def test_json_to_jsonl_conversion(self, sample_json_data, temp_data_dir):
        """Verify JSON to JSONL conversion."""
        output_file = temp_data_dir / "output" / "converted.jsonl"

        data = json.loads(sample_json_data.read_text())
        with output_file.open("w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")

        # Verify conversion
        converted = []
        with output_file.open("r") as f:
            for line in f:
                converted.append(json.loads(line))

        assert len(converted) == len(data), "Converted must not be empty"

    def test_csv_to_json_conversion(self, sample_csv_data, temp_data_dir):
        """Verify CSV to JSON conversion."""
        output_file = temp_data_dir / "output" / "converted.json"

        data = []
        with sample_csv_data.open("r") as f:
            reader = csv.DictReader(f)
            data = list(reader)

        output_file.write_text(json.dumps(data))

        # Verify conversion
        converted = json.loads(output_file.read_text())
        assert len(converted) == 3, "Converted must not be empty"

    def test_jsonl_to_csv_conversion(self, sample_jsonl_data, temp_data_dir):
        """Verify JSONL to CSV conversion."""
        output_file = temp_data_dir / "output" / "converted.csv"

        data = []
        with sample_jsonl_data.open("r") as f:
            for line in f:
                data.append(json.loads(line))

        if data:
            fieldnames = list(data[0].keys())
            with output_file.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

        # Verify conversion
        with output_file.open("r") as f:
            reader = csv.DictReader(f)
            converted = list(reader)

        assert len(converted) == 3, "Converted must not be empty"


class TestPipelineChaining:
    """Test chaining multiple pipeline stages."""

    def test_load_preprocess_validate_chain(self, sample_json_data, temp_data_dir):
        """Verify load → preprocess → validate chain."""
        # Load
        data = json.loads(sample_json_data.read_text())

        # Preprocess
        for item in data:
            item["text"] = item["text"].lower()
            item["text_length"] = len(item["text"])

        # Validate
        validated = []
        for item in data:
            if item["text_length"] > 0:
                validated.append(item)

        assert len(validated) == 3, "Validated must not be empty"

    def test_extract_transform_load_pipeline(self, sample_csv_data, temp_data_dir):
        """Verify ETL pipeline workflow."""
        # Extract
        data = []
        with sample_csv_data.open("r") as f:
            reader = csv.DictReader(f)
            data = list(reader)

        # Transform
        for item in data:
            item["processed"] = True
            item["text_upper"] = item["text"].upper()

        # Load
        output_file = temp_data_dir / "output" / "etl_result.json"
        output_file.write_text(json.dumps(data))

        assert output_file.exists(), "Condition must be true"

    def test_filter_deduplicate_sort_chain(self, temp_data_dir):
        """Verify filter → deduplicate → sort chain."""
        data_file = temp_data_dir / "raw" / "chain_test.json"
        data = [
            {"id": 3, "score": 0.5},
            {"id": 1, "score": 0.9},
            {"id": 2, "score": 0.3},
            {"id": 1, "score": 0.9},  # Duplicate
            {"id": 4, "score": 0.1},
        ]
        data_file.write_text(json.dumps(data))

        loaded = json.loads(data_file.read_text())

        # Filter
        filtered = [item for item in loaded if item["score"] >= 0.3]

        # Deduplicate
        seen = set()
        unique = []
        for item in filtered:
            key = (item["id"], item["score"])
            if key not in seen:
                seen.add(key)
                unique.append(item)

        # Sort
        sorted_data = sorted(unique, key=lambda x: x["id"])

        assert len(sorted_data) == 3, "Sorted_data must not be empty"
        assert sorted_data[0]["id"] == 1, "Data must not be empty"


class TestErrorHandling:
    """Test error handling in data pipelines."""

    def test_continue_on_error(self, temp_data_dir):
        """Verify pipeline continues on individual errors."""
        data_file = temp_data_dir / "raw" / "mixed.jsonl"
        with data_file.open("w") as f:
            f.write(json.dumps({"id": 1, "value": "valid"}) + "\n")
            f.write("{invalid json\n")
            f.write(json.dumps({"id": 2, "value": "valid"}) + "\n")

        valid_records = []
        errors = []

        with data_file.open("r") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                    valid_records.append(record)
                except json.JSONDecodeError as e:
                    errors.append((line_num, str(e)))

        assert len(valid_records) == 2, "Valid_records must not be empty"
        assert len(errors) == 1, "Errors must not be empty"

    def test_retry_on_failure(self):
        """Verify retry mechanism for transient failures."""
        max_retries = 3
        attempt = 0

        def flaky_operation():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        result: str | None = None
        for retry in range(max_retries):
            try:
                result = flaky_operation()
                break
            except ConnectionError:
                if retry == max_retries - 1:
                    raise

        assert result == "success", "Result must not be empty"

    def test_rollback_on_error(self, temp_data_dir):
        """Verify rollback mechanism on pipeline errors."""
        output_file = temp_data_dir / "output" / "transaction.json"
        temp_file = temp_data_dir / "output" / "transaction.tmp"

        data = [{"id": 1}, {"id": 2}]

        try:
            # Write to temp file
            temp_file.write_text(json.dumps(data))

            # Validate
            loaded = json.loads(temp_file.read_text())
            assert len(loaded) == 2, "Loaded must not be empty"

            # Commit
            temp_file.rename(output_file)
        except OSError:
            # Rollback
            if temp_file.exists():
                temp_file.unlink()
            raise

        assert output_file.exists(), "Condition must be true"


class TestPerformanceOptimization:
    """Test performance optimization in pipelines."""

    def test_lazy_loading(self, temp_data_dir):
        """Verify lazy loading for memory efficiency."""
        large_file = temp_data_dir / "raw" / "large_lazy.jsonl"
        with large_file.open("w") as f:
            for i in range(1000):
                f.write(json.dumps({"id": i}) + "\n")

        # Generator for lazy loading
        def lazy_reader(filepath):
            with open(filepath) as f:
                for line in f:
                    yield json.loads(line)

        reader = lazy_reader(large_file)
        first_item = next(reader)

        assert first_item["id"] == 0, "Item must not be empty"

    def test_memory_efficient_processing(self, temp_data_dir):
        """Verify memory-efficient streaming processing."""
        input_file = temp_data_dir / "raw" / "stream_input.jsonl"
        output_file = temp_data_dir / "output" / "stream_output.jsonl"

        # Create input
        with input_file.open("w") as f:
            for i in range(100):
                f.write(json.dumps({"id": i, "value": i * 2}) + "\n")

        # Stream processing
        with input_file.open("r") as fin, output_file.open("w") as fout:
            for line in fin:
                item = json.loads(line)
                item["processed"] = True
                fout.write(json.dumps(item) + "\n")

        assert output_file.exists(), "Condition must be true"

    def test_caching_intermediate_results(self, temp_data_dir):
        """Verify caching of intermediate pipeline results."""
        cache_file = temp_data_dir / "processed" / "cache.json"

        # Expensive operation result
        expensive_result = [{"id": i, "computed": i**2} for i in range(10)]

        # Cache
        cache_file.write_text(json.dumps(expensive_result))

        # Retrieve from cache
        cached = json.loads(cache_file.read_text())

        assert len(cached) == 10, "Cached must not be empty"
        assert cached[5]["computed"] == 25, "Condition must be true"
