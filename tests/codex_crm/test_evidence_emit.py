"""Comprehensive tests for codex_crm.evidence.emit module."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestSha256File:
    """Tests for sha256_file function."""

    def test_sha256_file_basic(self, tmp_path):
        """Test SHA256 hash computation for a file."""
        from codex_crm.evidence.emit import sha256_file

        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!", encoding="utf-8")

        digest = sha256_file(test_file)
        assert isinstance(digest, str)
        assert len(digest) == 64  # SHA256 hex digest is 64 chars

    def test_sha256_file_empty(self, tmp_path):
        """Test SHA256 hash for empty file."""
        from codex_crm.evidence.emit import sha256_file

        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        digest = sha256_file(test_file)
        # SHA256 of empty string is well-known
        assert digest == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_sha256_file_binary(self, tmp_path):
        """Test SHA256 hash for binary file."""
        from codex_crm.evidence.emit import sha256_file

        test_file = tmp_path / "binary.bin"
        test_file.write_bytes(b"\x00\x01\x02\x03")

        digest = sha256_file(test_file)
        assert isinstance(digest, str)
        assert len(digest) == 64

    def test_sha256_file_consistent(self, tmp_path):
        """Test that SHA256 hash is consistent."""
        from codex_crm.evidence.emit import sha256_file

        test_file = tmp_path / "consistent.txt"
        test_file.write_text("Same content", encoding="utf-8")

        digest1 = sha256_file(test_file)
        digest2 = sha256_file(test_file)
        assert digest1 == digest2


class TestWriteEvidence:
    """Tests for write_evidence function."""

    def test_write_evidence_creates_directory(self, tmp_path):
        """Test that write_evidence creates output directory."""
        from codex_crm.evidence.emit import write_evidence

        out_dir = tmp_path / "evidence" / "nested"
        write_evidence(out_dir)

        assert out_dir.exists()
        assert out_dir.is_dir()

    def test_write_evidence_creates_seeds_file(self, tmp_path):
        """Test that write_evidence creates seeds.json."""
        from codex_crm.evidence.emit import write_evidence

        out_dir = tmp_path / "evidence"
        write_evidence(out_dir)

        seeds_file = out_dir / "seeds.json"
        assert seeds_file.exists()
        
        seeds = json.loads(seeds_file.read_text())
        assert "rng" in seeds
        assert seeds["rng"] == 1337

    def test_write_evidence_custom_seeds(self, tmp_path):
        """Test write_evidence with custom seeds."""
        from codex_crm.evidence.emit import write_evidence

        out_dir = tmp_path / "evidence"
        custom_seeds = {"custom_seed": 42, "another": 99}
        write_evidence(out_dir, seeds=custom_seeds)

        seeds_file = out_dir / "seeds.json"
        seeds = json.loads(seeds_file.read_text())
        assert seeds["custom_seed"] == 42
        assert seeds["another"] == 99

    def test_write_evidence_creates_env_file(self, tmp_path):
        """Test that write_evidence creates env.json."""
        from codex_crm.evidence.emit import write_evidence

        out_dir = tmp_path / "evidence"
        write_evidence(out_dir)

        env_file = out_dir / "env.json"
        assert env_file.exists()
        
        env = json.loads(env_file.read_text())
        assert "platform" in env
        assert "python" in env
        assert "timestamp" in env
        assert isinstance(env["timestamp"], float)

    def test_write_evidence_creates_checksums_file(self, tmp_path):
        """Test that write_evidence creates checksums.json."""
        from codex_crm.evidence.emit import write_evidence

        out_dir = tmp_path / "evidence"
        write_evidence(out_dir)

        checksums_file = out_dir / "checksums.json"
        assert checksums_file.exists()
        
        checksums = json.loads(checksums_file.read_text())
        assert isinstance(checksums, dict)

    def test_write_evidence_creates_manifest_file(self, tmp_path):
        """Test that write_evidence creates run_manifest.json."""
        from codex_crm.evidence.emit import write_evidence

        out_dir = tmp_path / "evidence"
        write_evidence(out_dir)

        manifest_file = out_dir / "run_manifest.json"
        assert manifest_file.exists()
        
        manifest = json.loads(manifest_file.read_text())
        assert "timestamp" in manifest
        assert "artifacts" in manifest
        assert isinstance(manifest["artifacts"], list)

    def test_write_evidence_json_sorted(self, tmp_path):
        """Test that JSON files have sorted keys."""
        from codex_crm.evidence.emit import write_evidence

        out_dir = tmp_path / "evidence"
        write_evidence(out_dir, seeds={"z": 1, "a": 2, "m": 3})

        seeds_file = out_dir / "seeds.json"
        content = seeds_file.read_text()
        # Keys should be sorted: a, m, z
        assert content.index('"a"') < content.index('"m"') < content.index('"z"')


class TestConfigDirs:
    """Tests for CONFIG_DIRS constant."""

    def test_config_dirs_exists(self):
        """Test that CONFIG_DIRS constant exists."""
        from codex_crm.evidence.emit import CONFIG_DIRS

        assert isinstance(CONFIG_DIRS, tuple)
        assert len(CONFIG_DIRS) == 3

    def test_config_dirs_paths(self):
        """Test CONFIG_DIRS contains expected paths."""
        from codex_crm.evidence.emit import CONFIG_DIRS

        paths = [str(p) for p in CONFIG_DIRS]
        assert "configs/deployment/zd" in paths
        assert "configs/deployment/d365" in paths
        assert "configs/deployment/powerautomate/templates" in paths
