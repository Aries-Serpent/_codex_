"""
Tests for codex.release.manifest module.

This module contains tests for release manifest handling.
"""

import pytest
import json
import tempfile
from pathlib import Path


class TestComponent:
    """Tests for Component dataclass."""

    def test_basic_creation(self):
        """Test Component basic creation."""
        from codex.release.manifest import Component
        
        component = Component(
            tombstone="tombstone_1",
            dest_path="path/to/dest"
        )
        
        assert component.tombstone == "tombstone_1"
        assert component.dest_path == "path/to/dest"
        assert component.mode == "0644"
        assert component.type == "file"
        assert component.template_vars is None

    def test_custom_values(self):
        """Test Component with custom values."""
        from codex.release.manifest import Component
        
        component = Component(
            tombstone="ts",
            dest_path="dest",
            mode="0755",
            type="file",
            template_vars={"key": "value"}
        )
        
        assert component.mode == "0755"
        assert component.template_vars == {"key": "value"}


class TestSymlink:
    """Tests for Symlink dataclass."""

    def test_basic_creation(self):
        """Test Symlink basic creation."""
        from codex.release.manifest import Symlink
        
        symlink = Symlink(
            link_path="path/to/link",
            target="path/to/target"
        )
        
        assert symlink.link_path == "path/to/link"
        assert symlink.target == "path/to/target"


class TestManifest:
    """Tests for Manifest dataclass."""

    def test_basic_creation(self):
        """Test Manifest basic creation."""
        from codex.release.manifest import Manifest, Component, Symlink
        
        manifest = Manifest(
            release_id="release_1",
            version="1.0.0",
            created_at="2024-01-01T00:00:00Z",
            actor="user@example.com",
            target={"platform": "linux"},
            components=[Component("ts", "dest")],
            symlinks=[],
            post_unpack_commands=[],
            checks={}
        )
        
        assert manifest.release_id == "release_1"
        assert manifest.version == "1.0.0"
        assert len(manifest.components) == 1


class TestRequire:
    """Tests for _require helper."""

    def test_require_true(self):
        """Test _require with true condition."""
        from codex.release.manifest import _require
        
        # Should not raise
        _require(True, "This should not raise")

    def test_require_false(self):
        """Test _require with false condition."""
        from codex.release.manifest import _require
        
        with pytest.raises(ValueError, match="Test error"):
            _require(False, "Test error")


class TestIsRelSafe:
    """Tests for _is_rel_safe helper."""

    def test_relative_path(self):
        """Test relative path is safe."""
        from codex.release.manifest import _is_rel_safe
        
        assert _is_rel_safe("path/to/file") is True
        assert _is_rel_safe("file.txt") is True

    def test_absolute_path(self):
        """Test absolute path is not safe."""
        from codex.release.manifest import _is_rel_safe
        
        assert _is_rel_safe("/path/to/file") is False

    def test_path_traversal(self):
        """Test path traversal is not safe."""
        from codex.release.manifest import _is_rel_safe
        
        assert _is_rel_safe("../parent") is False
        assert _is_rel_safe("path/../other") is False


class TestLoadManifest:
    """Tests for load_manifest function."""

    def test_valid_manifest(self, tmp_path):
        """Test loading a valid manifest."""
        from codex.release.manifest import load_manifest
        
        manifest_data = {
            "release_id": "test_release_1",
            "version": "1.0.0",
            "created_at": "2024-01-01T00:00:00Z",
            "actor": "user@example.com",
            "target": {"platform": "linux"},
            "components": [
                {"tombstone": "ts1", "dest_path": "dest/path"}
            ],
            "symlinks": [],
            "post_unpack_commands": [],
            "checks": {}
        }
        
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest_data))
        
        result = load_manifest(manifest_file)
        
        assert result.release_id == "test_release_1"
        assert result.version == "1.0.0"

    def test_missing_release_id(self, tmp_path):
        """Test manifest without release_id."""
        from codex.release.manifest import load_manifest
        
        manifest_data = {
            "version": "1.0.0",
            "created_at": "2024-01-01T00:00:00Z",
            "actor": "user@example.com",
            "components": [{"tombstone": "ts1", "dest_path": "dest"}]
        }
        
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest_data))
        
        with pytest.raises(ValueError, match="release_id"):
            load_manifest(manifest_file)

    def test_missing_version(self, tmp_path):
        """Test manifest without version."""
        from codex.release.manifest import load_manifest
        
        manifest_data = {
            "release_id": "test_release_1",
            "created_at": "2024-01-01T00:00:00Z",
            "actor": "user@example.com",
            "components": [{"tombstone": "ts1", "dest_path": "dest"}]
        }
        
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest_data))
        
        with pytest.raises(ValueError, match="version"):
            load_manifest(manifest_file)

    def test_empty_components(self, tmp_path):
        """Test manifest with empty components."""
        from codex.release.manifest import load_manifest
        
        manifest_data = {
            "release_id": "test_release_1",
            "version": "1.0.0",
            "created_at": "2024-01-01T00:00:00Z",
            "actor": "user@example.com",
            "components": []
        }
        
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest_data))
        
        with pytest.raises(ValueError, match="components"):
            load_manifest(manifest_file)
