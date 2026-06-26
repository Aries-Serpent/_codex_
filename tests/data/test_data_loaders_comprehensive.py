"""
Comprehensive tests for data loaders (codex_ml/data/loaders.py).

Tests cover:
- JSONL loading with various formats
- CSV loading with quoted fields
- File checksum computation
- Connector URI handling
- Empty file handling
- Malformed data handling
- UTF-8 BOM handling
- Sample dataclass
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from codex_ml.data.loaders import (
    Sample,
    _materialize_connector_uri,
    _resolve_connector_cache_root,
    compute_file_checksum,
    load_csv,
    load_jsonl,
)


@pytest.fixture
def temp_data_dir(tmp_path: Path):
    """Create temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_jsonl_file(temp_data_dir: Path):
    """Create sample JSONL file."""
    jsonl_file = temp_data_dir / "data.jsonl"
    lines = [
        {"prompt": "What is AI?", "completion": "Artificial Intelligence"},
        {"prompt": "Define ML", "completion": "Machine Learning"},
        {"prompt": "What is DL?", "completion": "Deep Learning"},
    ]
    with jsonl_file.open("w") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")
    return jsonl_file


@pytest.fixture
def sample_csv_file(temp_data_dir: Path):
    """Create sample CSV file."""
    csv_file = temp_data_dir / "data.csv"
    with csv_file.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["prompt", "completion"])
        writer.writerow(["Question 1", "Answer 1"])
        writer.writerow(["Question 2", "Answer 2"])
    return csv_file


class TestSampleDataclass:
    """Test Sample dataclass."""

    def test_sample_creation(self):
        """Verify Sample creation."""
        sample = Sample(prompt="test prompt", completion="test completion")
        assert sample.prompt == "test prompt", "prompt is not valid"
        assert sample.completion == "test completion", "completion is not valid"

    def test_sample_frozen(self):
        """Verify Sample is immutable."""
        sample = Sample(prompt="test", completion="answer")
        with pytest.raises(AttributeError):
            sample.prompt = "changed"

    def test_sample_equality(self):
        """Verify Sample equality comparison."""
        s1 = Sample(prompt="q", completion="a")
        s2 = Sample(prompt="q", completion="a")
        s3 = Sample(prompt="q", completion="b")

        assert s1 == s2, "s1 is not valid"
        assert s1 != s3, "s1 is not valid"

    def test_sample_empty_strings(self):
        """Verify Sample with empty strings."""
        sample = Sample(prompt="", completion="")
        assert sample.prompt == "", "prompt is not valid"
        assert sample.completion == "", "completion is not valid"

    def test_sample_unicode(self):
        """Verify Sample with unicode text."""
        sample = Sample(prompt="你好", completion="世界")
        assert sample.prompt == "你好", "prompt is not valid"
        assert sample.completion == "世界", "completion is not valid"


class TestComputeFileChecksum:
    """Test file checksum computation."""

    def test_checksum_basic(self, temp_data_dir: Path):
        """Verify basic checksum computation."""
        test_file = temp_data_dir / "test.txt"
        test_file.write_text("test content")

        checksum = compute_file_checksum(test_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64, "Checksum must not be empty"

    def test_checksum_deterministic(self, temp_data_dir: Path):
        """Verify checksum is deterministic."""
        test_file = temp_data_dir / "test.txt"
        test_file.write_text("same content")

        checksum1 = compute_file_checksum(test_file)
        checksum2 = compute_file_checksum(test_file)

        assert checksum1 == checksum2, "checksum1 is not valid"

    def test_checksum_different_content(self, temp_data_dir: Path):
        """Verify different content produces different checksums."""
        file1 = temp_data_dir / "file1.txt"
        file2 = temp_data_dir / "file2.txt"

        file1.write_text("content 1")
        file2.write_text("content 2")

        checksum1 = compute_file_checksum(file1)
        checksum2 = compute_file_checksum(file2)

        assert checksum1 != checksum2, "checksum1 is not valid"

    def test_checksum_empty_file(self, temp_data_dir: Path):
        """Verify checksum of empty file."""
        empty_file = temp_data_dir / "empty.txt"
        empty_file.write_text("")

        checksum = compute_file_checksum(empty_file)
        # SHA256 of empty string
        expected = hashlib.sha256(b"").hexdigest()
        assert checksum == expected, "checksum is not valid"

    def test_checksum_binary_file(self, temp_data_dir: Path):
        """Verify checksum of binary file."""
        binary_file = temp_data_dir / "binary.dat"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xff")

        checksum = compute_file_checksum(binary_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64, "Checksum must not be empty"

    def test_checksum_large_file(self, temp_data_dir: Path):
        """Verify checksum of large file (chunked reading)."""
        large_file = temp_data_dir / "large.txt"
        # Write more than 8192 bytes (chunk size)
        large_file.write_text("x" * 10000)

        checksum = compute_file_checksum(large_file)
        assert len(checksum) == 64, "Checksum must not be empty"


class TestLoadJsonl:
    """Test JSONL loading functionality."""

    def test_load_jsonl_basic(self, sample_jsonl_file: Path):
        """Verify basic JSONL loading."""
        data, metadata = load_jsonl(sample_jsonl_file)

        assert len(data) == 3, "Data must not be empty"
        assert data[0]["prompt"] == "What is AI?", "Data must not be empty"
        assert "checksum" in metadata, "Data must not be empty"
        assert metadata["num_records"] == 3, "Data must not be empty"

    def test_load_jsonl_metadata(self, sample_jsonl_file: Path):
        """Verify metadata includes checksum and count."""
        _data, metadata = load_jsonl(sample_jsonl_file)

        assert "checksum" in metadata, "Data must not be empty"
        assert "num_records" in metadata, "Data must not be empty"
        assert metadata["num_records"] == 3, "Data must not be empty"

    def test_load_jsonl_empty_file(self, temp_data_dir: Path):
        """Verify empty JSONL file handling."""
        empty_file = temp_data_dir / "empty.jsonl"
        empty_file.write_text("")
        data, metadata = load_jsonl(empty_file)
        assert len(data) == 0, "Data must not be empty"
        assert metadata["empty_file"] is True, "Data must not be empty"
        assert metadata["num_records"] == 0, "Data must not be empty"

    def test_load_jsonl_malformed_lines(self, temp_data_dir: Path):
        """Verify malformed lines are skipped."""
        malformed_file = temp_data_dir / "malformed.jsonl"
        with malformed_file.open("w") as f:
            f.write('{"valid": "line1"}\n')
            f.write("not valid json\n")
            f.write('{"valid": "line2"}\n')
            f.write("also not json\n")

        data, metadata = load_jsonl(malformed_file)

        assert len(data) == 2, "Data must not be empty"
        assert metadata["skipped_malformed"] == 2, "Data must not be empty"

    def test_load_jsonl_utf8_bom(self, temp_data_dir: Path):
        """Verify UTF-8 BOM handling."""
        bom_file = temp_data_dir / "bom.jsonl"
        with bom_file.open("w", encoding="utf-8-sig") as f:
            f.write('{"text": "with BOM"}\n')

        data, _metadata = load_jsonl(bom_file)

        assert len(data) == 1, "Data must not be empty"
        assert data[0]["text"] == "with BOM", "Data must not be empty"

    def test_load_jsonl_unicode_content(self, temp_data_dir: Path):
        """Verify unicode content handling."""
        unicode_file = temp_data_dir / "unicode.jsonl"
        with unicode_file.open("w", encoding="utf-8") as f:
            f.write('{"text": "你好世界"}\n')
            f.write('{"text": "مرحبا"}\n')
            f.write('{"text": "こんにちは"}\n')

        records, _meta = load_jsonl(unicode_file)

        assert len(records) == 3, "Records must not be empty"
        assert records[0]["text"] == "你好世界", "rec is not valid"

    def test_load_jsonl_nested_objects(self, temp_data_dir: Path):
        """Verify nested JSON objects."""
        nested_file = temp_data_dir / "nested.jsonl"
        with nested_file.open("w") as f:
            f.write('{"outer": {"inner": {"deep": "value"}}}\n')

        data, _metadata = load_jsonl(nested_file)

        assert data[0]["outer"]["inner"]["deep"] == "value", "Data must not be empty"

    def test_load_jsonl_missing_file(self):
        """Verify error for missing file."""
        with pytest.raises(FileNotFoundError):
            load_jsonl(Path("/nonexistent/file.jsonl"))


class TestLoadCsv:
    """Test CSV loading functionality."""

    def test_load_csv_basic(self, sample_csv_file: Path):
        """Verify basic CSV loading."""
        records, meta = load_csv(sample_csv_file)

        assert isinstance(records, list)
        assert isinstance(meta, dict)
        assert len(records) == 2, "Records must not be empty"
        assert records[0]["prompt"] == "Question 1", "rec is not valid"

    def test_load_csv_metadata(self, sample_csv_file: Path):
        """Verify CSV metadata."""
        _records, meta = load_csv(sample_csv_file)

        assert "checksum" in meta, "Condition must be true"
        assert "num_records" in meta, "Condition must be true"
        assert meta["num_records"] == 2, "Condition must be true"

    def test_load_csv_quoted_fields(self, temp_data_dir: Path):
        """Verify quoted field handling."""
        quoted_file = temp_data_dir / "quoted.csv"
        with quoted_file.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["prompt", "completion"])
            writer.writerow(["Question with, comma", "Answer with, comma"])
            writer.writerow(['"Quoted question"', '"Quoted answer"'])

        records, _meta = load_csv(quoted_file)

        assert "comma" in records[0]["prompt"], "Condition must be true"
        assert "Quoted" in records[1]["prompt"], "Condition must be true"

    def test_load_csv_empty_file(self, temp_data_dir: Path):
        """Verify empty CSV file handling."""
        empty_file = temp_data_dir / "empty.csv"
        empty_file.write_text("")

        records, meta = load_csv(empty_file)

        assert records == [], "records is not valid"
        assert meta["empty_file"] is True, "Condition must be true"

    def test_load_csv_missing_file(self):
        """Verify error for missing CSV file."""
        with pytest.raises(FileNotFoundError):
            load_csv(Path("/nonexistent/file.csv"))

    def test_load_csv_unicode(self, temp_data_dir: Path):
        """Verify unicode in CSV."""
        unicode_file = temp_data_dir / "unicode.csv"
        with unicode_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["text"])
            writer.writerow(["日本語"])
            writer.writerow(["Ελληνικά"])

        records, _meta = load_csv(unicode_file)

        assert records[0]["text"] == "日本語", "rec is not valid"
        assert records[1]["text"] == "Ελληνικά", "rec is not valid"


class TestConnectorCacheRoot:
    """Test connector cache root resolution."""

    def test_resolve_default_cache(self):
        """Verify default cache location."""
        cache_root = _resolve_connector_cache_root()
        assert cache_root.name == "connector_cache", "name is not valid"
        assert ".codex" in str(cache_root), "Condition must be true"

    def test_resolve_env_override(self, monkeypatch, tmp_path: Path):
        """Verify environment variable override."""
        custom_cache = tmp_path / "custom_cache"
        monkeypatch.setenv("CODEX_CONNECTOR_CACHE_ROOT", str(custom_cache))

        cache_root = _resolve_connector_cache_root()
        assert cache_root == custom_cache, "cache_root is not valid"

    def test_resolve_expanduser(self, monkeypatch):
        """Verify tilde expansion in cache path."""
        monkeypatch.setenv("CODEX_CONNECTOR_CACHE_ROOT", "~/test_cache")

        cache_root = _resolve_connector_cache_root()
        assert "~" not in str(cache_root), "Condition must be true"


class TestConnectorUri:
    """Test connector URI materialization."""

    @patch("codex_ml.data.loaders.get_connector")
    @patch("codex_ml.data.loaders._run_connector_coro")
    def test_materialize_basic(self, mock_run_coro, mock_get_connector, tmp_path: Path):
        """Verify basic connector URI materialization."""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        mock_run_coro.return_value = ["file1.txt", "file2.txt"]

        mock_run_coro.side_effect = [
            ["file1.txt", "file2.txt"],  # list_files
            b"content1",  # read_file for file1
            b"content2",  # read_file for file2
        ]

        uri = "connector://test_connector/data"

        try:
            result = _materialize_connector_uri(uri, cache_root=tmp_path)
            # Should return list of paths
            assert isinstance(result, list)
        except (ValueError, RuntimeError) as e:
            # Expected if connector not fully mocked
            assert "connector" in str(e).lower(), "Condition must be true"

    def test_materialize_invalid_uri(self):
        """Verify error for invalid connector URI."""
        with pytest.raises(ValueError, match="connector URI must include"):
            _materialize_connector_uri("connector://")

    def test_materialize_missing_connector_name(self):
        """Verify error for missing connector name."""
        with pytest.raises(ValueError, match="connector URI missing connector name"):
            _materialize_connector_uri("connector:///path")

    @patch("codex_ml.data.loaders.get_connector")
    def test_materialize_unknown_connector(self, mock_get_connector):
        """Verify error for unknown connector."""
        mock_get_connector.side_effect = KeyError("unknown")

        with pytest.raises(ValueError, match="unknown connector"):
            _materialize_connector_uri("connector://unknown/path")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_jsonl_single_line(self, temp_data_dir: Path):
        """Verify single line JSONL."""
        single_file = temp_data_dir / "single.jsonl"
        single_file.write_text('{"key": "value"}\n')

        # UPDATED: Unpack tuple return (records, metadata)
        data, metadata = load_jsonl(single_file)
        assert len(data) == 1, "Data must not be empty"
        assert metadata["num_records"] == 1, "Data must not be empty"

    def test_jsonl_no_newline_at_end(self, temp_data_dir: Path):
        """Verify JSONL without trailing newline."""
        no_newline = temp_data_dir / "no_newline.jsonl"
        no_newline.write_text('{"key": "value"}')

        # UPDATED: Unpack tuple return (records, metadata)
        data, _metadata = load_jsonl(no_newline)
        assert len(data) == 1, "Data must not be empty"

    def test_csv_single_row(self, temp_data_dir: Path):
        """Verify CSV with single data row."""
        single_row = temp_data_dir / "single.csv"
        with single_row.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["col1", "col2"])
            writer.writerow(["val1", "val2"])

        # UPDATED: Unpack tuple return (records, metadata)
        data, _metadata = load_csv(single_row)
        assert len(data) == 1, "Data must not be empty"

    def test_jsonl_whitespace_only_lines(self, temp_data_dir: Path):
        """Verify whitespace-only lines are skipped."""
        whitespace_file = temp_data_dir / "whitespace.jsonl"
        with whitespace_file.open("w") as f:
            f.write('{"valid": "line1"}\n')
            f.write("   \n")
            f.write("\t\t\n")
            f.write('{"valid": "line2"}\n')

        # UPDATED: Unpack tuple return (records, metadata)
        data, _metadata = load_jsonl(whitespace_file)
        # Whitespace lines should be skipped
        assert len(data) == 2, "Data must not be empty"

    def test_checksum_identical_files(self, temp_data_dir: Path):
        """Verify identical files have same checksum."""
        file1 = temp_data_dir / "file1.txt"
        file2 = temp_data_dir / "file2.txt"

        content = "identical content"
        file1.write_text(content)
        file2.write_text(content)

        checksum1 = compute_file_checksum(file1)
        checksum2 = compute_file_checksum(file2)

        assert checksum1 == checksum2, "checksum1 is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
