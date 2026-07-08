"""
Comprehensive tests for the Codex Ingest module.

Tests cover:
- Snapshot creation from files, directories, and archives
- Manifest parsing and validation
- Content hashing and determinism
- Error handling and safeguards
"""

from pathlib import Path

import pytest


class TestIngestAdapter:
    """Tests for the ingest adapter module."""

    def test_ingest_single_file(self, tmp_path: Path):
        """Test ingesting a single Python file."""
        from codex.ingest.adapter import ingest

        # Create test file
        test_file = tmp_path / "test_script.py"
        test_file.write_text("logger.info('hello')\n", encoding="utf-8")

        # Create artifacts directory
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        # Ingest
        snapshot = ingest(test_file, artifacts_dir=artifacts_dir)

        assert snapshot.snapshot_id is not None, "snapshot_id must be initialized"
        assert snapshot.content_hash is not None, "content_hash must be initialized"
        assert snapshot.snapshot_dir.exists(), "Condition must be true"
        assert (snapshot.snapshot_dir / "source").exists(), "Condition must be true"
        assert (snapshot.snapshot_dir / "snapshot-meta.json").exists(), "Condition must be true"

    def test_ingest_directory(self, tmp_path: Path):
        """Test ingesting a directory of Python files."""
        from codex.ingest.adapter import ingest

        # Create test directory
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("def main(): pass\n", encoding="utf-8")
        (source_dir / "utils.py").write_text("def helper(): pass\n", encoding="utf-8")

        # Create artifacts directory
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        # Ingest
        snapshot = ingest(source_dir, artifacts_dir=artifacts_dir)

        assert snapshot.snapshot_id is not None, "snapshot_id must be initialized"
        assert (snapshot.snapshot_dir / "source" / "main.py").exists(), "Condition must be true"
        assert (snapshot.snapshot_dir / "source" / "utils.py").exists(), "Condition must be true"

    def test_ingest_with_manifest(self, tmp_path: Path):
        """Test ingesting with a manifest file."""
        from codex.ingest.adapter import ingest

        # Create test file
        test_file = tmp_path / "script.py"
        test_file.write_text("logger.info('test')\n", encoding="utf-8")

        # Create manifest
        manifest_file = tmp_path / "manifest.yaml"
        manifest_file.write_text(
            """
version: "1.0"
source:
  type: file
  path: "./script.py"
metadata:
  owner: "@test"
""",
            encoding="utf-8",
        )

        # Create artifacts directory
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        # Ingest
        snapshot = ingest(test_file, manifest_path=manifest_file, artifacts_dir=artifacts_dir)

        assert snapshot.manifest is not None, "manifest must be initialized"
        assert snapshot.manifest.version == "1.0", "version is not valid"
        assert (snapshot.snapshot_dir / "manifest.yaml").exists(), "Condition must be true"

    def test_ingest_custom_snapshot_id(self, tmp_path: Path):
        """Test ingesting with a custom snapshot ID."""
        from codex.ingest.adapter import ingest

        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1\n", encoding="utf-8")

        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        snapshot = ingest(test_file, snapshot_id="custom-id-123", artifacts_dir=artifacts_dir)

        assert snapshot.snapshot_id == "custom-id-123", "snapshot_id is not valid"
        assert (artifacts_dir / "custom-id-123").exists(), "Condition must be true"

    def test_ingest_deterministic_hash(self, tmp_path: Path):
        """Test that content hash is deterministic."""
        from codex.ingest.adapter import ingest

        test_file = tmp_path / "test.py"
        test_file.write_text("content = 'fixed'\n", encoding="utf-8")

        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        snapshot1 = ingest(test_file, snapshot_id="snap1", artifacts_dir=artifacts_dir)
        snapshot2 = ingest(test_file, snapshot_id="snap2", artifacts_dir=artifacts_dir)

        assert snapshot1.content_hash == snapshot2.content_hash, "Content must not be empty"

    def test_ingest_file_not_found(self, tmp_path: Path):
        """Test error handling for non-existent file."""
        from codex.ingest.adapter import ingest

        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            ingest(tmp_path / "nonexistent.py", artifacts_dir=artifacts_dir)

    def test_ingest_creates_artifact_directories(self, tmp_path: Path):
        """Test that ingest creates expected subdirectories."""
        from codex.ingest.adapter import ingest

        test_file = tmp_path / "test.py"
        test_file.write_text("pass\n", encoding="utf-8")

        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        snapshot = ingest(test_file, artifacts_dir=artifacts_dir)

        assert (snapshot.snapshot_dir / "patches").exists(), "Condition must be true"
        assert (snapshot.snapshot_dir / "tests" / "codex_generated").exists(), "Condition must be true"
        assert (snapshot.snapshot_dir / "llm_provenance").exists(), "Condition must be true"

    def test_snapshot_to_dict(self, tmp_path: Path):
        """Test snapshot serialization."""
        from codex.ingest.adapter import ingest

        test_file = tmp_path / "test.py"
        test_file.write_text("pass\n", encoding="utf-8")

        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        snapshot = ingest(test_file, artifacts_dir=artifacts_dir)
        data = snapshot.to_dict()

        assert "snapshot_id" in data, "Data must not be empty"
        assert "content_hash" in data, "Data must not be empty"
        assert "created_at" in data, "Data must not be empty"


class TestManifestParser:
    """Tests for manifest parsing."""

    def test_parse_minimal_manifest(self, tmp_path: Path):
        """Test parsing a minimal valid manifest."""
        from codex.ingest.manifest import parse_manifest

        manifest_file = tmp_path / "manifest.yaml"
        manifest_file.write_text(
            """
version: "1.0"
source:
  type: file
  path: "./script.py"
""",
            encoding="utf-8",
        )

        manifest = parse_manifest(manifest_file)

        assert manifest.version == "1.0", "version is not valid"
        assert manifest.source.type == "file", "type is not valid"
        assert manifest.source.path == "./script.py", "path is not valid"

    def test_parse_full_manifest(self, tmp_path: Path):
        """Test parsing a complete manifest with all fields."""
        from codex.ingest.manifest import parse_manifest

        manifest_file = tmp_path / "manifest.yaml"
        manifest_file.write_text(
            """
version: "1.0"
source:
  type: git-url
  path: "https://github.com/example/repo"
  ref: "main"
entry_point: "main:run"
sample_inputs:
  - path: "input1.txt"
    description: "Test input"
golden_outputs:
  - input_ref: "input1.txt"
    expected_output: "output1.txt"
    comparison_mode: fuzzy
constraints:
  max_runtime_seconds: 120
  max_memory_mb: 1024
  allowed_network: true
  forbidden_patterns:
    - "eval("
metadata:
  owner: "@developer"
  privacy: public
  allow_external_llm: true
  tags:
    - "utility"
""",
            encoding="utf-8",
        )

        manifest = parse_manifest(manifest_file)

        assert manifest.source.type == "git-url", "type is not valid"
        assert manifest.source.ref == "main", "ref is not valid"
        assert manifest.entry_point == "main:run", "entry_point is not valid"
        assert len(manifest.sample_inputs) == 1, "Collection must not be empty"
        assert len(manifest.golden_outputs) == 1, "Collection must not be empty"
        assert manifest.constraints.max_runtime_seconds == 120, "max_runtime_seconds is not valid"
        assert manifest.metadata.privacy == "public", "Data must not be empty"

    def test_parse_manifest_missing_version(self, tmp_path: Path):
        """Test error on missing version."""
        from codex.ingest.manifest import parse_manifest

        manifest_file = tmp_path / "manifest.yaml"
        manifest_file.write_text(
            """
source:
  type: file
  path: "./script.py"
""",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="version"):
            parse_manifest(manifest_file)

    def test_parse_manifest_invalid_version_format(self, tmp_path: Path):
        """Test error on invalid version format."""
        from codex.ingest.manifest import parse_manifest

        manifest_file = tmp_path / "manifest.yaml"
        manifest_file.write_text(
            """
version: "invalid"
source:
  type: file
  path: "./script.py"
""",
            encoding="utf-8",
        )

        with pytest.raises(ValueError):
            parse_manifest(manifest_file)

    def test_parse_manifest_constraint_bounds(self, tmp_path: Path):
        """Test constraint bounds validation."""
        from codex.ingest.manifest import parse_manifest

        manifest_file = tmp_path / "manifest.yaml"
        manifest_file.write_text(
            """
version: "1.0"
source:
  type: file
  path: "./script.py"
constraints:
  max_runtime_seconds: 10000
""",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="max_runtime_seconds"):
            parse_manifest(manifest_file)

    def test_manifest_to_dict(self, tmp_path: Path):
        """Test manifest serialization."""
        from codex.ingest.manifest import parse_manifest

        manifest_file = tmp_path / "manifest.yaml"
        manifest_file.write_text(
            """
version: "1.0"
source:
  type: file
  path: "./script.py"
""",
            encoding="utf-8",
        )

        manifest = parse_manifest(manifest_file)
        data = manifest.to_dict()

        assert data["version"] == "1.0", "Data must not be empty"
        assert data["source"]["type"] == "file", "Data must not be empty"


class TestContentHash:
    """Tests for content hashing."""

    def test_hash_single_file(self, tmp_path: Path):
        """Test hashing a single file."""
        from codex.ingest.adapter import _compute_content_hash

        test_file = tmp_path / "test.py"
        test_file.write_text("content\n", encoding="utf-8")

        hash1 = _compute_content_hash(test_file)
        hash2 = _compute_content_hash(test_file)

        assert hash1 == hash2, "hash1 is not valid"
        assert len(hash1) == 64, "Hash1 must not be empty"

    def test_hash_directory_deterministic(self, tmp_path: Path):
        """Test that directory hashing is deterministic."""
        from codex.ingest.adapter import _compute_content_hash

        test_dir = tmp_path / "source"
        test_dir.mkdir()
        (test_dir / "a.py").write_text("a\n", encoding="utf-8")
        (test_dir / "b.py").write_text("b\n", encoding="utf-8")

        hash1 = _compute_content_hash(test_dir)
        hash2 = _compute_content_hash(test_dir)

        assert hash1 == hash2, "hash1 is not valid"

    def test_hash_different_content(self, tmp_path: Path):
        """Test that different content produces different hashes."""
        from codex.ingest.adapter import _compute_content_hash

        file1 = tmp_path / "file1.py"
        file2 = tmp_path / "file2.py"
        file1.write_text("content1\n", encoding="utf-8")
        file2.write_text("content2\n", encoding="utf-8")

        hash1 = _compute_content_hash(file1)
        hash2 = _compute_content_hash(file2)

        assert hash1 != hash2, "hash1 is not valid"
