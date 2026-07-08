"""Gap-fill tests for CRM evidence bundle functionality.

Tests for src/codex_crm/evidence/emit.py to improve CRM module coverage.
"""

import hashlib
import json
import platform
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from src.codex_crm.evidence.emit import (
    sha256_file,
    write_evidence,
)


class TestSHA256FileHashing:
    """Test SHA256 file hashing functionality."""

    def test_sha256_file_basic(self):
        """Test basic SHA256 file hashing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)

        try:
            result = sha256_file(temp_path)
            assert isinstance(result, str)
            assert len(result) == 64, "Result must not be empty"
            assert result.isalnum(), "Result must not be empty"
        finally:
            temp_path.unlink()

    def test_sha256_file_consistent(self):
        """Test that SHA256 hashing is consistent."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)

        try:
            result1 = sha256_file(temp_path)
            result2 = sha256_file(temp_path)
            assert result1 == result2, "Result must not be empty"
        finally:
            temp_path.unlink()

    def test_sha256_file_different_content(self):
        """Test that different content produces different hashes."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1:
            f1.write("content1")
            temp_path1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f2:
            f2.write("content2")
            temp_path2 = Path(f2.name)

        try:
            result1 = sha256_file(temp_path1)
            result2 = sha256_file(temp_path2)
            assert result1 != result2, "Result must not be empty"
        finally:
            temp_path1.unlink()
            temp_path2.unlink()

    def test_sha256_file_large_file(self):
        """Test SHA256 hashing with larger file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            # Write > 8192 bytes to test chunked reading
            f.write("x" * 10000)
            temp_path = Path(f.name)

        try:
            result = sha256_file(temp_path)
            assert isinstance(result, str)
            assert len(result) == 64, "Result must not be empty"
        finally:
            temp_path.unlink()

    def test_sha256_file_empty_file(self):
        """Test SHA256 hashing of empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = sha256_file(temp_path)
            # Empty file hash
            expected = hashlib.sha256(b"").hexdigest()
            assert result == expected, "Result must not be empty"
        finally:
            temp_path.unlink()

    def test_sha256_file_binary_content(self):
        """Test SHA256 hashing with binary content."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(b"\x00\x01\x02\x03\x04")
            temp_path = Path(f.name)

        try:
            result = sha256_file(temp_path)
            assert isinstance(result, str)
            assert len(result) == 64, "Result must not be empty"
        finally:
            temp_path.unlink()


class TestWriteEvidenceBasic:
    """Test basic evidence bundle writing."""

    def test_write_evidence_creates_directory(self):
        """Test that write_evidence creates output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)
            assert output_path.exists(), "Condition must be true"

    def test_write_evidence_creates_seeds_file(self):
        """Test that write_evidence creates seeds.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            seeds_file = output_path / "seeds.json"
            assert seeds_file.exists(), "Condition must be true"

            content = json.loads(seeds_file.read_text())
            assert "rng" in content, "Content must not be empty"
            assert content["rng"] == 1337, "Content must not be empty"

    def test_write_evidence_creates_env_file(self):
        """Test that write_evidence creates env.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            env_file = output_path / "env.json"
            assert env_file.exists(), "Condition must be true"

            content = json.loads(env_file.read_text())
            assert "platform" in content, "Content must not be empty"
            assert "python" in content, "Content must not be empty"
            assert "timestamp" in content, "Content must not be empty"

    def test_write_evidence_creates_checksums_file(self):
        """Test that write_evidence creates checksums.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            checksums_file = output_path / "checksums.json"
            assert checksums_file.exists(), "Condition must be true"

            content = json.loads(checksums_file.read_text())
            assert isinstance(content, dict)

    def test_write_evidence_creates_run_manifest(self):
        """Test that write_evidence creates run_manifest.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            manifest_file = output_path / "run_manifest.json"
            assert manifest_file.exists(), "Condition must be true"

            content = json.loads(manifest_file.read_text())
            assert "timestamp" in content, "Content must not be empty"
            assert "artifacts" in content, "Content must not be empty"
            assert isinstance(content["artifacts"], list)

    def test_write_evidence_creates_manifest_file(self):
        """Test that write_evidence creates manifest.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            manifest_file = output_path / "manifest.json"
            assert manifest_file.exists(), "Condition must be true"

            content = json.loads(manifest_file.read_text())
            assert "message" in content, "Content must not be empty"


class TestWriteEvidenceWithSeeds:
    """Test evidence writing with custom seeds."""

    def test_write_evidence_with_custom_seeds(self):
        """Test write_evidence with custom seed values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            custom_seeds = {"rng": 9999, "other": 42}
            write_evidence(output_path, seeds=custom_seeds)

            seeds_file = output_path / "seeds.json"
            content = json.loads(seeds_file.read_text())
            assert content["rng"] == 9999, "Content must not be empty"
            assert content["other"] == 42, "Content must not be empty"

    def test_write_evidence_with_none_seeds(self):
        """Test write_evidence with None seeds defaults to {rng: 1337}."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path, seeds=None)

            seeds_file = output_path / "seeds.json"
            content = json.loads(seeds_file.read_text())
            assert content["rng"] == 1337, "Content must not be empty"


class TestWriteEvidenceEnvironment:
    """Test environment information capture."""

    def test_env_contains_platform(self):
        """Test that environment includes platform info."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            env_file = output_path / "env.json"
            content = json.loads(env_file.read_text())
            assert content["platform"] == platform.platform(), "Content must not be empty"

    def test_env_contains_python_version(self):
        """Test that environment includes Python version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            env_file = output_path / "env.json"
            content = json.loads(env_file.read_text())
            assert content["python"] == platform.python_version(), "Content must not be empty"

    def test_env_contains_timestamp(self):
        """Test that environment includes timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            before = time.time()
            write_evidence(output_path)
            after = time.time()

            env_file = output_path / "env.json"
            content = json.loads(env_file.read_text())
            assert before <= content["timestamp"] <= after, "Content must not be empty"


class TestWriteEvidenceChecksums:
    """Test checksum generation."""

    def test_checksums_empty_when_no_config_dirs(self):
        """Test that checksums are empty when config dirs don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"

            # Mock CONFIG_DIRS to be empty
            with patch("src.codex_crm.evidence.emit.CONFIG_DIRS", []):
                write_evidence(output_path)

            checksums_file = output_path / "checksums.json"
            content = json.loads(checksums_file.read_text())
            assert content == {}, "Content must not be empty"

    def test_run_manifest_artifacts_list(self):
        """Test that run manifest contains artifacts as sorted list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            manifest_file = output_path / "run_manifest.json"
            content = json.loads(manifest_file.read_text())

            assert isinstance(content["artifacts"], list)
            # Verify it's sorted
            if len(content["artifacts"]) > 0:
                sorted_list = sorted(content["artifacts"])
                assert content["artifacts"] == sorted_list, "Content must not be empty"


class TestWriteEvidencePathHandling:
    """Test path handling in evidence writing."""

    def test_write_evidence_with_string_path(self):
        """Test write_evidence with string path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_str = str(Path(tmpdir) / "evidence")
            write_evidence(output_str)

            assert Path(output_str).exists(), "Condition must be true"

    def test_write_evidence_with_path_object(self):
        """Test write_evidence with Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            assert output_path.exists(), "Condition must be true"

    def test_write_evidence_nested_directory(self):
        """Test write_evidence creates nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "evidence" / "path"
            write_evidence(output_path)

            assert output_path.exists(), "Condition must be true"

    def test_write_evidence_existing_directory(self):
        """Test write_evidence with existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            output_path.mkdir()

            write_evidence(output_path)
            assert output_path.exists(), "Condition must be true"


class TestWriteEvidenceFileContents:
    """Test the content of written evidence files."""

    def test_all_files_valid_json(self):
        """Test that all generated files contain valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            json_files = [
                output_path / "seeds.json",
                output_path / "env.json",
                output_path / "checksums.json",
                output_path / "run_manifest.json",
                output_path / "manifest.json",
            ]

            for json_file in json_files:
                assert json_file.exists(), "Condition must be true"
                content = json.loads(json_file.read_text())
                assert isinstance(content, dict)

    def test_evidence_files_sorted_keys(self):
        """Test that JSON files have sorted keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            write_evidence(output_path)

            # Check seeds.json has sorted keys
            seeds_file = output_path / "seeds.json"
            text = seeds_file.read_text()
            # Verify it matches JSON with sorted keys
            original = json.loads(text)
            reserialized = json.dumps(original, indent=2, sort_keys=True)
            assert text == reserialized, "text is not valid"


class TestEvidenceIntegration:
    """Integration tests for evidence writing."""

    def test_complete_evidence_bundle(self):
        """Test that complete evidence bundle is written correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "evidence"
            custom_seeds = {"rng": 555}
            write_evidence(output_path, seeds=custom_seeds)

            # Verify all files exist
            assert (output_path / "seeds.json").exists(), "Condition must be true"
            assert (output_path / "env.json").exists(), "Condition must be true"
            assert (output_path / "checksums.json").exists(), "Condition must be true"
            assert (output_path / "run_manifest.json").exists(), "Condition must be true"
            assert (output_path / "manifest.json").exists(), "Condition must be true"

            # Verify seeds content
            seeds = json.loads((output_path / "seeds.json").read_text())
            assert seeds["rng"] == 555, "Condition must be true"

            # Verify env structure
            env = json.loads((output_path / "env.json").read_text())
            assert len(env) >= 3, "Env must not be empty"

    def test_evidence_reproducibility(self):
        """Test that running evidence writing twice produces consistent results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path1 = Path(tmpdir) / "evidence1"
            output_path2 = Path(tmpdir) / "evidence2"

            seeds = {"rng": 777}
            write_evidence(output_path1, seeds=seeds)
            write_evidence(output_path2, seeds=seeds)

            # Compare seeds files
            seeds1 = json.loads((output_path1 / "seeds.json").read_text())
            seeds2 = json.loads((output_path2 / "seeds.json").read_text())
            assert seeds1 == seeds2, "seeds1 is not valid"

            # Compare manifests structure (timestamps will differ)
            manifest1 = json.loads((output_path1 / "run_manifest.json").read_text())
            manifest2 = json.loads((output_path2 / "run_manifest.json").read_text())
            assert manifest1["artifacts"] == manifest2["artifacts"], "Condition must be true"
