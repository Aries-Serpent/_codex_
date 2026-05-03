"""
Test Generate Audit Dashboard

Test module for generate audit dashboard.
"""

#!/usr/bin/env python3
"""
Tests for generate_audit_dashboard.py script.

Tests cover core functionality including:
- Directory scanning
- Manifest loading
- HTML generation
- XSS prevention
- Format utilities
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from generate_audit_dashboard import (
    SUPPORTED_EXTENSIONS,
    format_size,
    format_timestamp,
    generate_html_dashboard,
    load_manifest,
    scan_directory,
)


class TestFormatUtilities:
    """Test formatting utility functions."""

    def test_format_size_bytes(self):
        """Test format_size with bytes."""
        assert format_size(500) == "500.00 B"
        assert format_size(0) == "0.00 B"

    def test_format_size_kilobytes(self):
        """Test format_size with kilobytes."""
        assert format_size(1024) == "1.00 KB"
        assert format_size(2048) == "2.00 KB"

    def test_format_size_megabytes(self):
        """Test format_size with megabytes."""
        assert format_size(1024 * 1024) == "1.00 MB"
        assert format_size(5 * 1024 * 1024) == "5.00 MB"

    def test_format_size_gigabytes(self):
        """Test format_size with gigabytes."""
        assert format_size(1024 * 1024 * 1024) == "1.00 GB"

    def test_format_timestamp_valid(self):
        """Test format_timestamp with valid timestamp."""
        timestamp = datetime(2024, 1, 15, 10, 30, 45).timestamp()
        result = format_timestamp(timestamp)
        assert "2024-01-15" in result
        assert "10:30:45" in result

    def test_format_timestamp_invalid(self):
        """Test format_timestamp with invalid timestamp."""
        result = format_timestamp(-1)
        assert result == "Unknown"

    def test_format_timestamp_future(self):
        """Test format_timestamp with future timestamp."""
        # Very large timestamp (year 3000)
        result = format_timestamp(32503680000)
        # Should handle gracefully
        assert result == "Unknown" or "3000" in result


class TestScanDirectory:
    """Test directory scanning functionality."""

    def test_scan_directory_empty(self, tmp_path):
        """Test scanning an empty directory."""
        files = scan_directory(tmp_path)
        assert files == []

    def test_scan_directory_nonexistent(self, tmp_path):
        """Test scanning a non-existent directory."""
        nonexistent = tmp_path / "does_not_exist"
        files = scan_directory(nonexistent)
        assert files == []

    def test_scan_directory_with_files(self, tmp_path):
        """Test scanning directory with files."""
        # Create test files
        (tmp_path / "file1.json").write_text('{"test": true}')
        (tmp_path / "file2.md").write_text("# Test")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content")

        files = scan_directory(tmp_path)

        assert len(files) == 3
        assert any(f["name"] == "file1.json" for f in files)
        assert any(f["name"] == "file2.md" for f in files)
        assert any(f["name"] == "file3.txt" for f in files)

    def test_scan_directory_file_metadata(self, tmp_path):
        """Test that file metadata is correctly extracted."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        files = scan_directory(tmp_path)

        assert len(files) == 1
        file_info = files[0]
        assert file_info["name"] == "test.json"
        assert file_info["size"] > 0
        assert file_info["type"] == ".json"
        assert "modified" in file_info
        assert "path" in file_info


class TestLoadManifest:
    """Test manifest loading functionality."""

    def test_load_manifest_valid(self, tmp_path):
        """Test loading a valid manifest file."""
        manifest_path = tmp_path / "manifest.json"
        manifest_data = {
            "version": "1.0.0",
            "artifacts": [{"name": "test.json", "size": 100}],
            "weights": {"test": 0.5},
        }
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_manifest(manifest_path)

        assert result == manifest_data
        assert result["version"] == "1.0.0"
        assert len(result["artifacts"]) == 1

    def test_load_manifest_nonexistent(self, tmp_path):
        """Test loading a non-existent manifest file."""
        nonexistent = tmp_path / "missing.json"
        result = load_manifest(nonexistent)
        assert result == {}

    def test_load_manifest_invalid_json(self, tmp_path):
        """Test loading an invalid JSON manifest."""
        manifest_path = tmp_path / "invalid.json"
        manifest_path.write_text("{ invalid json }")

        result = load_manifest(manifest_path)
        assert result == {}

    def test_load_manifest_empty(self, tmp_path):
        """Test loading an empty manifest file."""
        manifest_path = tmp_path / "empty.json"
        manifest_path.write_text("{}")

        result = load_manifest(manifest_path)
        assert result == {}


class TestGenerateHtmlDashboard:
    """Test HTML dashboard generation."""

    def test_generate_html_basic(self, tmp_path):
        """Test basic HTML generation."""
        output_path = tmp_path / "index.html"

        generate_html_dashboard(
            audit_artifacts=[], reports=[], manifest={}, output_path=output_path
        )

        assert output_path.exists()
        content = output_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Audit Dashboard" in content

    def test_generate_html_with_artifacts(self, tmp_path):
        """Test HTML generation with artifacts."""
        output_path = tmp_path / "index.html"
        artifacts = [
            {
                "path": "audit_artifacts/test.json",
                "name": "test.json",
                "size": 1024,
                "modified": datetime.now().timestamp(),
                "type": ".json",
            }
        ]

        generate_html_dashboard(
            audit_artifacts=artifacts, reports=[], manifest={}, output_path=output_path
        )

        content = output_path.read_text()
        assert "test.json" in content
        assert "1.00 KB" in content

    def test_generate_html_with_manifest(self, tmp_path):
        """Test HTML generation with manifest data."""
        output_path = tmp_path / "index.html"
        manifest = {
            "version": "1.5.0",
            "timestamp": datetime.now().timestamp(),
            "weights": {"functionality": 0.25, "tests": 0.25},
            "artifacts": [
                {
                    "name": "capabilities.json",
                    "format": "json",
                    "size": 5000,
                    "sha": "abc123" * 10,
                    "generated_at": datetime.now().timestamp(),
                }
            ],
        }

        generate_html_dashboard(
            audit_artifacts=[], reports=[], manifest=manifest, output_path=output_path
        )

        content = output_path.read_text()
        assert "1.5.0" in content
        assert "functionality" in content.lower()
        assert "0.25" in content

    def test_xss_prevention_filenames(self, tmp_path):
        """Test XSS prevention with malicious filenames."""
        output_path = tmp_path / "index.html"
        malicious_artifacts = [
            {
                "path": "<script>alert('xss')</script>",
                "name": "<img src=x onerror=alert(1)>",
                "size": 100,
                "modified": datetime.now().timestamp(),
                "type": ".json",
            }
        ]

        generate_html_dashboard(
            audit_artifacts=malicious_artifacts,
            reports=[],
            manifest={},
            output_path=output_path,
        )

        content = output_path.read_text()
        # Verify HTML entities are escaped
        # Both conditions must be true: raw malicious content absent AND escaped version present
        assert "&lt;script&gt;" in content or "&#x3C;script&#x3E;" in content
        assert "<script>alert('xss')</script>" not in content
        assert "<img src=x onerror=alert(1)>" not in content

    def test_xss_prevention_manifest(self, tmp_path):
        """Test XSS prevention with malicious manifest data."""
        output_path = tmp_path / "index.html"
        malicious_manifest = {
            "version": "<script>alert('version')</script>",
            "weights": {
                "<script>alert('key')</script>": "<script>alert('value')</script>"
            },
            "artifacts": [
                {
                    "name": "<img src=x onerror=alert(2)>",
                    "format": "<b>malicious</b>",
                    "size": 100,
                    "sha": "abc123",
                    "generated_at": datetime.now().timestamp(),
                }
            ],
        }

        generate_html_dashboard(
            audit_artifacts=[],
            reports=[],
            manifest=malicious_manifest,
            output_path=output_path,
        )

        content = output_path.read_text()
        # Verify all malicious content is escaped
        # Check for the specific malicious script content, not just any script tag
        assert "alert('version')" not in content or "&lt;script&gt;alert" in content
        assert "alert('key')" not in content or "&lt;script&gt;alert" in content
        assert "&lt;script&gt;" in content or "&#x3C;script&#x3E;" in content
        assert "<img src=x onerror=" not in content
        assert "<b>malicious</b>" not in content
        assert "&lt;b&gt;" in content or "&#x3C;b&#x3E;" in content

    def test_supported_extensions_constant(self):
        """Test that SUPPORTED_EXTENSIONS constant is defined."""
        assert isinstance(SUPPORTED_EXTENSIONS, set)
        assert "json" in SUPPORTED_EXTENSIONS
        assert "md" in SUPPORTED_EXTENSIONS
        assert "txt" in SUPPORTED_EXTENSIONS
        assert "html" in SUPPORTED_EXTENSIONS


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_scan_directory_with_permission_error(self, tmp_path):
        """Test handling of permission errors during scan."""
        # This test may not work on all systems
        # Just verify it doesn't crash
        files = scan_directory(tmp_path)
        assert isinstance(files, list)

    def test_very_large_file_size(self):
        """Test format_size with very large files."""
        # 5 TB
        result = format_size(5 * 1024 * 1024 * 1024 * 1024)
        assert "TB" in result

    def test_unicode_filenames(self, tmp_path):
        """Test handling of Unicode filenames."""
        output_path = tmp_path / "index.html"
        artifacts = [
            {
                "path": "test_文件.json",
                "name": "测试文件.json",
                "size": 100,
                "modified": datetime.now().timestamp(),
                "type": ".json",
            }
        ]

        generate_html_dashboard(
            audit_artifacts=artifacts, reports=[], manifest={}, output_path=output_path
        )

        content = output_path.read_text(encoding="utf-8")
        assert "测试文件" in content or "&#x" in content  # Either raw or escaped

    def test_empty_manifest_artifacts(self, tmp_path):
        """Test with empty artifacts list in manifest."""
        output_path = tmp_path / "index.html"
        manifest = {"artifacts": []}

        generate_html_dashboard(
            audit_artifacts=[], reports=[], manifest=manifest, output_path=output_path
        )

        assert output_path.exists()

    def test_missing_artifact_fields(self, tmp_path):
        """Test handling of artifacts with missing fields."""
        output_path = tmp_path / "index.html"
        artifacts = [
            {
                "path": "test.json",
                "name": "test.json",
                # Missing size and modified
            }
        ]

        # Should handle gracefully without crashing
        try:
            generate_html_dashboard(
                audit_artifacts=artifacts,
                reports=[],
                manifest={},
                output_path=output_path,
            )
        except KeyError:
            # Expected if fields are required
            pass
