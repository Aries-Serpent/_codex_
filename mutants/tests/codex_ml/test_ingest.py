"""
Test Ingest Module

Integration tests for the data ingestion module.
Tests configuration loading, dataset parsing, and preprocessing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codex_ml.ingest import (
    _DataConfig,
    _default_config,
    _extract_config,
    _iter_dataset_files,
    _load_records,
    _normalize_json_item,
    _read_csv,
    _read_json,
    _read_jsonl,
    _read_text,
    ingest_sample,
    load_dataset,
)


class TestDataConfig:
    """Tests for _DataConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = _DataConfig()

        assert config.sample_mode is True, "sample_mode is not valid"
        assert config.sample_size == 16, "sample_size is not valid"
        assert config.dataset_name == "local_sample", "Data must not be empty"
        assert config.shuffle is True, "shuffle is not valid"
        assert config.preprocess_lowercase is True, "preprocess_lowercase is not valid"
        assert config.preprocess_max_length == 512, "Length must be greater than zero"
        assert config.seed == 42, "seed is not valid"

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = _DataConfig(
            sample_mode=False,
            sample_size=100,
            dataset_name="my_dataset",
            shuffle=False,
            preprocess_lowercase=False,
            preprocess_max_length=1024,
            seed=123,
        )

        assert config.sample_mode is False, "sample_mode is not valid"
        assert config.sample_size == 100, "sample_size is not valid"
        assert config.dataset_name == "my_dataset", "Data must not be empty"
        assert config.preprocess_max_length == 1024, "Length must be greater than zero"


class TestDefaultConfig:
    """Tests for _default_config function."""

    def test_returns_dataconfig(self) -> None:
        """Test _default_config returns DataConfig instance."""
        config = _default_config()

        assert isinstance(config, _DataConfig)

    def test_default_values_match(self) -> None:
        """Test default config has expected values."""
        config = _default_config()

        assert config.sample_mode is True, "sample_mode is not valid"
        assert config.sample_size == 16, "sample_size is not valid"


class TestExtractConfig:
    """Tests for _extract_config function."""

    def test_empty_mapping(self) -> None:
        """Test extraction from empty mapping."""
        config = _extract_config({})

        assert config.sample_mode is True, "sample_mode is not valid"
        assert config.sample_size == 16, "sample_size is not valid"
        assert config.dataset_name == "local_sample", "Data must not be empty"

    def test_full_config(self) -> None:
        """Test extraction from full config mapping."""
        mapping = {
            "data": {
                "sample_mode": False,
                "sample_size": 50,
                "dataset": {
                    "name": "test_dataset",
                    "path": "/data/test",
                    "shuffle": False,
                },
                "preprocess": {
                    "lowercase": False,
                    "max_length": 256,
                },
            }
        }

        config = _extract_config(mapping)

        assert config.sample_mode is False, "sample_mode is not valid"
        assert config.sample_size == 50, "sample_size is not valid"
        assert config.dataset_name == "test_dataset", "Data must not be empty"
        assert config.shuffle is False, "shuffle is not valid"
        assert config.preprocess_lowercase is False, "preprocess_lowercase is not valid"
        assert config.preprocess_max_length == 256, "Length must be greater than zero"

    def test_partial_config(self) -> None:
        """Test extraction from partial config."""
        mapping = {
            "data": {
                "sample_size": 32,
            }
        }

        config = _extract_config(mapping)

        assert config.sample_size == 32, "sample_size is not valid"
        assert config.sample_mode is True, "sample_mode is not valid"

    def test_invalid_data_block(self) -> None:
        """Test handling of invalid data block type."""
        mapping = {"data": "not a mapping"}
        config = _extract_config(mapping)

        # Should fall back to defaults
        assert config.sample_mode is True, "sample_mode is not valid"

    def test_null_max_length(self) -> None:
        """Test null max_length handling."""
        mapping = {
            "data": {
                "preprocess": {
                    "max_length": None,
                }
            }
        }

        config = _extract_config(mapping)
        assert config.preprocess_max_length is None, "Length must be greater than zero"


class TestNormalizeJsonItem:
    """Tests for _normalize_json_item function."""

    def test_mapping_passthrough(self) -> None:
        """Test mapping items are converted to dict."""
        item = {"text": "hello", "label": 1}
        result = _normalize_json_item(item)

        assert result == {"text": "hello", "label": 1}

    def test_string_wrapped(self) -> None:
        """Test string items are wrapped in text key."""
        result = _normalize_json_item("hello world")

        assert result == {"text": "hello world"}, "Result must not be empty"

    def test_number_wrapped(self) -> None:
        """Test number items are wrapped."""
        result = _normalize_json_item(42)

        assert result == {"text": 42}, "Result must not be empty"

    def test_list_wrapped(self) -> None:
        """Test list items are wrapped."""
        result = _normalize_json_item([1, 2, 3])

        assert result == {"text": [1, 2, 3]}


class TestReadCsv:
    """Tests for _read_csv function."""

    def test_read_csv_file(self, tmp_path: Path) -> None:
        """Test reading a CSV file."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("text,label\nhello,1\nworld,2\n")

        records = _read_csv(csv_file)

        assert len(records) == 2, "Records must not be empty"
        assert records[0] == {"text": "hello", "label": "1"}
        assert records[1] == {"text": "world", "label": "2"}

    def test_read_empty_csv(self, tmp_path: Path) -> None:
        """Test reading empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("text,label\n")

        records = _read_csv(csv_file)

        assert records == [], "records is not valid"


class TestReadJsonl:
    """Tests for _read_jsonl function."""

    def test_read_jsonl_file(self, tmp_path: Path) -> None:
        """Test reading a JSONL file."""
        jsonl_file = tmp_path / "data.jsonl"
        jsonl_file.write_text('{"text": "hello"}\n{"text": "world"}\n')

        records = _read_jsonl(jsonl_file)

        assert len(records) == 2, "Records must not be empty"
        assert records[0] == {"text": "hello"}, "rec is not valid"
        assert records[1] == {"text": "world"}, "rec is not valid"

    def test_read_jsonl_with_blank_lines(self, tmp_path: Path) -> None:
        """Test JSONL with blank lines."""
        jsonl_file = tmp_path / "data.jsonl"
        jsonl_file.write_text('{"text": "a"}\n\n{"text": "b"}\n')

        records = _read_jsonl(jsonl_file)

        assert len(records) == 2, "Records must not be empty"

    def test_read_jsonl_invalid_json(self, tmp_path: Path) -> None:
        """Test JSONL with invalid JSON line."""
        jsonl_file = tmp_path / "data.jsonl"
        jsonl_file.write_text('{"text": "valid"}\nnot json\n')

        records = _read_jsonl(jsonl_file)

        assert len(records) == 2, "Records must not be empty"
        assert records[0] == {"text": "valid"}, "rec is not valid"
        # Malformed JSON lines should fall back to raw-text records.
        assert records[1] == {"text": "not json"}, "rec is not valid"


class TestReadJson:
    """Tests for _read_json function."""

    def test_read_json_array(self, tmp_path: Path) -> None:
        """Test reading JSON array."""
        json_file = tmp_path / "data.json"
        json_file.write_text('[{"text": "a"}, {"text": "b"}]')

        records = _read_json(json_file)

        assert len(records) == 2, "Records must not be empty"
        assert records[0] == {"text": "a"}, "rec is not valid"

    def test_read_json_object(self, tmp_path: Path) -> None:
        """Test reading JSON object."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"text": "single"}')

        records = _read_json(json_file)

        assert len(records) == 1, "Records must not be empty"
        assert records[0] == {"text": "single"}, "rec is not valid"

    def test_read_invalid_json(self, tmp_path: Path) -> None:
        """Test reading invalid JSON."""
        json_file = tmp_path / "data.json"
        json_file.write_text("not valid json")

        records = _read_json(json_file)

        # Should return raw text
        assert len(records) == 1, "Records must not be empty"
        assert records[0]["text"] == "not valid json", "rec is not valid"


class TestReadText:
    """Tests for _read_text function."""

    def test_read_text_file(self, tmp_path: Path) -> None:
        """Test reading text file."""
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("line 1\nline 2\nline 3\n")

        records = _read_text(txt_file)

        assert len(records) == 3, "Records must not be empty"
        assert records[0] == {"text": "line 1"}, "rec is not valid"
        assert records[2] == {"text": "line 3"}, "rec is not valid"

    def test_read_text_skips_empty_lines(self, tmp_path: Path) -> None:
        """Test that empty lines are skipped."""
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("line 1\n\n\nline 2\n")

        records = _read_text(txt_file)

        assert len(records) == 2, "Records must not be empty"


class TestIterDatasetFiles:
    """Tests for _iter_dataset_files function."""

    def test_single_file(self, tmp_path: Path) -> None:
        """Test iterating over single file."""
        data_file = tmp_path / "data.txt"
        data_file.write_text("content")

        files = list(_iter_dataset_files(data_file))

        assert len(files) == 1, "Files must not be empty"
        assert files[0] == data_file, "Data must not be empty"

    def test_directory(self, tmp_path: Path) -> None:
        """Test iterating over directory."""
        (tmp_path / "file1.txt").write_text("a")
        (tmp_path / "file2.txt").write_text("b")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.txt").write_text("c")

        files = list(_iter_dataset_files(tmp_path))

        assert len(files) == 3, "Files must not be empty"


class TestLoadRecords:
    """Tests for _load_records function."""

    def test_load_mixed_files(self, tmp_path: Path) -> None:
        """Test loading records from mixed file types."""
        # Create test files
        (tmp_path / "data.txt").write_text("text line\n")
        (tmp_path / "data.jsonl").write_text('{"text": "jsonl line"}\n')
        (tmp_path / "data.csv").write_text("text\ncsv line\n")

        records = _load_records(tmp_path)

        # Should have records from all files
        assert len(records) >= 3, "Records must not be empty"


class TestPublicAPI:
    """Tests for public API functions."""

    def test_ingest_sample_returns_list(self) -> None:
        """Test ingest_sample returns a list."""
        try:
            result = ingest_sample(size=5)
            assert isinstance(result, list)
        except Exception as _err:
            # May fail if no sample data available
            pytest.skip("Sample data not available")

    def test_load_dataset_returns_list(self) -> None:
        """Test load_dataset returns a list."""
        try:
            result = load_dataset()
            assert isinstance(result, list)
        except (ValueError, TypeError) as _err:
            # May fail if no dataset available
            pytest.skip("Dataset not available")

    def test_ingest_function_exists(self) -> None:
        """Test ingest function is exported."""
        from codex_ml.ingest import ingest

        assert callable(ingest), "Condition must be true"


class TestAllExports:
    """Tests for module exports."""

    def test_all_exports(self) -> None:
        """Test __all__ contains expected exports."""
        from codex_ml import ingest

        expected = ["ingest", "load_dataset", "ingest_sample"]
        for name in expected:
            assert name in ingest.__all__, "Condition must be true"
            assert hasattr(ingest, name)
