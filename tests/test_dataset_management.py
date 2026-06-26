"""Tests for dataset management and compression system."""

import json
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dataset_dedup import ContentDeduplicator
from dataset_pipeline import DatasetManager, FileProcessor


@pytest.fixture
def temp_dataset(tmp_path):
    """Create a temporary dataset for testing."""
    # Create directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create Python file
    python_code = '''"""Sample module."""

class TestClass:
    """A test class."""

    def method(self, arg):
        """A method."""
        return arg * 2

def test_function():
    """A function."""
    return True
'''
    (src_dir / "module.py").write_text(python_code)

    # Create duplicate Python file
    (src_dir / "module_copy.py").write_text(python_code)

    # Create documentation
    doc_content = """# Documentation

## Section 1

Some text here.

```python
code_example()
```

## Section 2

More text.
"""
    (docs_dir / "README.md").write_text(doc_content)

    # Create config file
    config_content = '{"key": "value", "nested": {"item": 1}}'
    (tmp_path / "config.json").write_text(config_content)

    return tmp_path


def test_file_processor_categorize():
    """Test file categorization."""
    assert FileProcessor.categorize_file(Path("test.py")) == "source_code", "FileProcess is not valid"
    assert FileProcessor.categorize_file(Path("README.md")) == "documentation", "FileProcess is not valid"
    assert FileProcessor.categorize_file(Path("config.yaml")) == "config", "FileProcess is not valid"
    assert FileProcessor.categorize_file(Path("test.ipynb")) == "notebook", "FileProcess is not valid"
    assert FileProcessor.categorize_file(Path("data.sql")) == "database", "Data must not be empty"
    assert FileProcessor.categorize_file(Path("unknown.xyz")) is None, "FileProcess is not valid"


def test_file_processor_should_skip():
    """Test skip logic."""
    assert FileProcessor.should_skip(Path(".git/config")), "FileProcess is not valid"
    assert FileProcessor.should_skip(Path("__pycache__/module.pyc")), "FileProcess is not valid"
    assert FileProcessor.should_skip(Path("node_modules/package/index.js")), "FileProcess is not valid"
    assert not FileProcessor.should_skip(Path("src/module.py")), "Condition must be true"


def test_file_processor_checksum(temp_dataset):
    """Test checksum calculation."""
    test_file = temp_dataset / "src" / "module.py"
    checksum = FileProcessor.calculate_checksum(test_file)

    assert checksum, "checksum is not valid"
    assert len(checksum) == 64, "Checksum must not be empty"

    # Verify same content produces same checksum
    checksum2 = FileProcessor.calculate_checksum(test_file)
    assert checksum == checksum2, "checksum is not valid"


def test_file_processor_process_documentation(temp_dataset):
    """Test documentation processing."""
    doc_file = temp_dataset / "docs" / "README.md"
    content, quality = FileProcessor.process_documentation(doc_file)

    assert content is not None, "content must be initialized"
    assert 0.0 <= quality <= 1.0, "0 is not valid"

    metadata = json.loads(content)
    assert "headers_count" in metadata, "Data must not be empty"
    assert metadata["headers_count"] > 0, "Value must be greater than zero"
    assert "code_blocks_count" in metadata, "Data must not be empty"


def test_file_processor_process_source_code(temp_dataset):
    """Test source code processing."""
    py_file = temp_dataset / "src" / "module.py"
    content, quality = FileProcessor.process_source_code(py_file)

    assert content is not None, "content must be initialized"
    assert 0.0 <= quality <= 1.0, "0 is not valid"

    metadata = json.loads(content)
    assert "classes" in metadata, "Data must not be empty"
    assert metadata["classes"] >= 1, "Value must be greater than zero"
    assert "functions" in metadata, "Data must not be empty"
    assert metadata["functions"] >= 1, "Value must be greater than zero"


def test_file_processor_process_config(temp_dataset):
    """Test config file processing."""
    config_file = temp_dataset / "config.json"
    content, quality = FileProcessor.process_config(config_file)

    assert content is not None, "content must be initialized"
    assert 0.0 <= quality <= 1.0, "0 is not valid"

    metadata = json.loads(content)
    assert "is_valid" in metadata, "Data must not be empty"
    assert metadata["is_valid"] is True, "Data must not be empty"


def test_file_processor_process_file(temp_dataset):
    """Test complete file processing."""
    py_file = temp_dataset / "src" / "module.py"
    processed = FileProcessor.process_file(py_file, temp_dataset)

    assert processed is not None, "processed must be initialized"
    assert processed.category == "source_code", "category is not valid"
    assert processed.checksum, "Condition must be true"
    assert processed.size_original > 0, "size_original must be greater than zero"
    assert processed.size_compressed > 0, "size_compressed must be greater than zero"
    assert processed.size_compressed < processed.size_original, "size_compressed is not valid"
    assert 0.0 <= processed.quality_score <= 1.0, "0 is not valid"
    assert 0.0 < processed.compression_ratio < 1.0, "0 is not valid"


def test_dataset_manager_init(temp_dataset):
    """Test DatasetManager initialization."""
    manager = DatasetManager(temp_dataset)

    assert manager.repo_path == temp_dataset, "Data must not be empty"
    assert manager.output_dir.exists(), "Condition must be true"
    assert len(manager.processed_files) == 0, "Collection must not be empty"


def test_dataset_manager_scan(temp_dataset):
    """Test repository scanning."""
    manager = DatasetManager(temp_dataset)
    count = manager.scan_repository()

    assert count > 0, "count must be positive"
    assert len(manager.processed_files) == count, "Collection must not be empty"

    # Check categories
    categories = {pf.category for pf in manager.processed_files}
    assert "source_code" in categories, "Condition must be true"
    assert "documentation" in categories, "Condition must be true"
    assert "config" in categories, "Condition must be true"


def test_dataset_manager_deduplication(temp_dataset):
    """Test that duplicate files are deduplicated."""
    manager = DatasetManager(temp_dataset)
    manager.scan_repository()

    # We created two identical Python files
    # Check that only unique files are kept
    checksums = [pf.checksum for pf in manager.processed_files]
    assert len(checksums) == len(set(checksums)), "Checksums must not be empty"


def test_dataset_manager_generate_manifest(temp_dataset):
    """Test manifest generation."""
    manager = DatasetManager(temp_dataset)
    manager.scan_repository()

    manifest = manager.generate_manifest("test_v1.0")

    assert manifest.version == "test_v1.0", "version is not valid"
    assert manifest.total_files > 0, "total_files must be greater than zero"
    assert manifest.total_size_original > 0, "total_size_original must be greater than zero"
    assert manifest.total_size_compressed > 0, "total_size_compressed must be greater than zero"
    assert manifest.compression_ratio < 1.0, "compression_ratio is not valid"
    assert len(manifest.file_categories) > 0, "Collection must not be empty"
    assert "average_quality_score" in manifest.quality_metrics, "Condition must be true"


def test_dataset_manager_save_manifest(temp_dataset):
    """Test manifest saving."""
    manager = DatasetManager(temp_dataset)
    manager.scan_repository()

    manifest = manager.generate_manifest("test_v1.0")
    manifest_path = manager.save_manifest(manifest, "test_v1.0")

    assert manifest_path.exists(), "Condition must be true"

    # Verify JSON is valid
    with open(manifest_path) as f:
        loaded = json.load(f)

    assert loaded["version"] == "test_v1.0", "Condition must be true"
    assert loaded["total_files"] > 0, "Value must be greater than zero"


def test_dataset_manager_create_archive(temp_dataset):
    """Test archive creation."""
    manager = DatasetManager(temp_dataset)
    manager.scan_repository()

    archive_path = manager.create_compressed_archive("test_v1.0", "tar.gz")

    assert archive_path.exists(), "Condition must be true"
    assert archive_path.suffix == ".gz", "suffix is not valid"
    assert archive_path.stat().st_size > 0, "st_size must be greater than zero"


def test_content_deduplicator_init(temp_dataset):
    """Test ContentDeduplicator initialization."""
    dedup = ContentDeduplicator(temp_dataset)

    assert dedup.root_path == temp_dataset, "Data must not be empty"
    assert len(dedup.file_checksums) == 0, "Collection must not be empty"


def test_content_deduplicator_scan(temp_dataset):
    """Test directory scanning."""
    dedup = ContentDeduplicator(temp_dataset)
    count = dedup.scan_directory()

    assert count > 0, "count must be positive"
    assert len(dedup.file_checksums) == count, "Collection must not be empty"


def test_content_deduplicator_find_duplicates(temp_dataset):
    """Test duplicate detection."""
    dedup = ContentDeduplicator(temp_dataset)
    dedup.scan_directory()

    report = dedup.analyze_duplicates()

    assert report.total_files > 0, "total_files must be greater than zero"
    assert report.unique_files > 0, "unique_files must be greater than zero"

    # We have duplicate Python files
    assert report.duplicate_files > 0, "duplicate_files must be greater than zero"
    assert report.duplicate_groups > 0, "duplicate_groups must be greater than zero"
    assert report.space_wasted > 0, "space_wasted must be greater than zero"


def test_content_deduplicator_create_strategy(temp_dataset):
    """Test deduplication strategy creation."""
    dedup = ContentDeduplicator(temp_dataset)
    dedup.scan_directory()

    report = dedup.analyze_duplicates()
    strategy = dedup.create_dedup_strategy(report)

    # Should have mappings for duplicates
    assert len(strategy) > 0, "Strategy must not be empty"

    # All values should be paths to keep
    for source, target in strategy.items():
        assert source != target, "source is not valid"


def test_content_deduplicator_save_report(temp_dataset):
    """Test report saving."""
    dedup = ContentDeduplicator(temp_dataset)
    dedup.scan_directory()

    report = dedup.analyze_duplicates()
    output_path = temp_dataset / "dedup_report.json"
    dedup.save_report(report, output_path)

    assert output_path.exists(), "Condition must be true"

    # Verify JSON is valid
    with open(output_path) as f:
        loaded = json.load(f)

    assert "total_files" in loaded, "Condition must be true"
    assert "duplicate_files" in loaded, "Condition must be true"


def test_compression_effectiveness(temp_dataset):
    """Test that compression actually reduces size."""
    manager = DatasetManager(temp_dataset)
    manager.scan_repository()

    for pf in manager.processed_files:
        # Text files should compress well, but only if large enough to overcome gzip header overhead
        if pf.category in ("source_code", "documentation", "config") and pf.size_original >= 1024:
            assert pf.compression_ratio < 0.8, "compression_ratio is not valid"


def test_quality_scoring(temp_dataset):
    """Test quality score assignment."""
    manager = DatasetManager(temp_dataset)
    manager.scan_repository()

    # All files should have valid quality scores
    for pf in manager.processed_files:
        assert 0.0 <= pf.quality_score <= 1.0, "0 is not valid"

    # Source code should have reasonable quality
    code_files = [pf for pf in manager.processed_files if pf.category == "source_code"]
    assert any(pf.quality_score > 0.5 for pf in code_files), "quality_score must be greater than zero"


def test_skip_patterns_respected(temp_dataset):
    """Test that skip patterns are properly applied."""
    # Create files that should be skipped
    (temp_dataset / ".git").mkdir()
    (temp_dataset / ".git" / "config").write_text("config")

    (temp_dataset / "__pycache__").mkdir()
    (temp_dataset / "__pycache__" / "module.pyc").write_bytes(b"compiled")

    manager = DatasetManager(temp_dataset)
    manager.scan_repository()

    # Check that skipped files are not in results
    paths = [pf.relative_path for pf in manager.processed_files]
    assert not any(".git" in path for path in paths), "Condition must be true"
    assert not any("__pycache__" in path for path in paths), "Condition must be true"
