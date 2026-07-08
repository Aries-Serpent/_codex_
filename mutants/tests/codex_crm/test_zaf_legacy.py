"""Comprehensive tests for codex_crm.zaf_legacy.reader module."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest


class TestZendeskAppPackageError:
    """Tests for ZendeskAppPackageError exception."""

    def test_exception_exists(self):
        """Test ZendeskAppPackageError exists."""
        from codex_crm.zaf_legacy.reader import ZendeskAppPackageError

        with pytest.raises(ZendeskAppPackageError):
            raise ZendeskAppPackageError("Test error")


class TestTextExtensions:
    """Tests for _TEXT_EXTENSIONS constant."""

    def test_text_extensions_frozenset(self):
        """Test _TEXT_EXTENSIONS is a frozenset."""
        from codex_crm.zaf_legacy.reader import _TEXT_EXTENSIONS

        assert isinstance(_TEXT_EXTENSIONS, frozenset)
        assert ".js" in _TEXT_EXTENSIONS, "Condition must be true"
        assert ".json" in _TEXT_EXTENSIONS, "Condition must be true"
        assert ".html" in _TEXT_EXTENSIONS, "Condition must be true"


class TestReadZaf:
    """Tests for read_zaf function."""

    def test_read_zaf_basic(self, tmp_path):
        """Test reading a basic ZAF package."""
        from codex_crm.zaf_legacy.reader import read_zaf

        zip_path = tmp_path / "app.zip"
        manifest = {"name": "TestApp", "version": "1.0.0"}

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("src/app.js", "console.log('hello');")

        result = read_zaf(zip_path)

        assert "archive_path" in result, "Result must not be empty"
        assert "manifest" in result, "Result must not be empty"
        assert "files" in result, "Result must not be empty"
        assert result["manifest"]["name"] == "TestApp", "Result must not be empty"
        assert "src/app.js" in result["files"], "Result must not be empty"

    def test_read_zaf_no_manifest(self, tmp_path):
        """Test reading ZAF package without manifest."""
        from codex_crm.zaf_legacy.reader import read_zaf

        zip_path = tmp_path / "no_manifest.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("src/app.js", "code")

        result = read_zaf(zip_path)
        assert result["manifest"] == {}, "Result must not be empty"


class TestScaffoldTemplate:
    """Tests for scaffold_template function."""

    def test_scaffold_template_creates_directory(self, tmp_path):
        """Test that scaffold creates output directory."""
        from codex_crm.zaf_legacy.reader import scaffold_template

        zip_path = tmp_path / "app.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps({"name": "App"}))

        package = {"archive_path": zip_path, "manifest": {"name": "App"}, "files": {}}
        out_dir = tmp_path / "scaffold" / "nested"
        scaffold_template(package, out_dir)

        assert out_dir.exists(), "Condition must be true"

    def test_scaffold_template_creates_manifest(self, tmp_path):
        """Test that scaffold creates manifest.json."""
        from codex_crm.zaf_legacy.reader import scaffold_template

        package = {"manifest": {"name": "TestApp"}, "files": {}}
        out_dir = tmp_path / "scaffold"
        scaffold_template(package, out_dir)

        manifest_file = out_dir / "manifest.json"
        assert manifest_file.exists(), "Condition must be true"

        manifest = json.loads(manifest_file.read_text())
        assert manifest["name"] == "TestApp", "Condition must be true"

    def test_scaffold_template_creates_readme(self, tmp_path):
        """Test that scaffold creates README.md."""
        from codex_crm.zaf_legacy.reader import scaffold_template

        package = {"manifest": {}, "files": {}}
        out_dir = tmp_path / "scaffold"
        scaffold_template(package, out_dir)

        readme_file = out_dir / "README.md"
        assert readme_file.exists(), "Condition must be true"
        assert "Zendesk App" in readme_file.read_text(), "Condition must be true"

    def test_scaffold_template_adds_api_base_parameter(self, tmp_path):
        """Test that scaffold adds API_BASE parameter if missing."""
        from codex_crm.zaf_legacy.reader import scaffold_template

        package = {"manifest": {"parameters": []}, "files": {}}
        out_dir = tmp_path / "scaffold"
        scaffold_template(package, out_dir)

        manifest_file = out_dir / "manifest.json"
        manifest = json.loads(manifest_file.read_text())

        api_base = next(p for p in manifest["parameters"] if p["name"] == "API_BASE")
        assert api_base["type"] == "text", "Condition must be true"


class TestNormaliseManifest:
    """Tests for _normalise_manifest helper."""

    def test_normalise_adds_api_base(self):
        """Test that API_BASE parameter is added."""
        from codex_crm.zaf_legacy.reader import _normalise_manifest

        manifest = {"name": "App", "parameters": []}
        result = _normalise_manifest(manifest)

        assert any(p["name"] == "API_BASE" for p in result["parameters"]), "Result must not be empty"

    def test_normalise_preserves_existing_api_base(self):
        """Test that existing API_BASE is preserved."""
        from codex_crm.zaf_legacy.reader import _normalise_manifest

        manifest = {"name": "App", "parameters": [{"name": "API_BASE", "default": "custom"}]}
        result = _normalise_manifest(manifest)

        api_bases = [p for p in result["parameters"] if p["name"] == "API_BASE"]
        assert len(api_bases) == 1, "Api_bases must not be empty"
        assert api_bases[0]["default"] == "custom", "Condition must be true"


class TestNormaliseEntryPath:
    """Tests for _normalise_entry_path helper."""

    def test_normalise_basic_path(self):
        """Test normalising a basic path."""

        from codex_crm.zaf_legacy.reader import _normalise_entry_path

        entry = zipfile.ZipInfo("src/app.js")
        result = _normalise_entry_path(entry)

        assert result == Path("src/app.js"), "Result must not be empty"

    def test_normalise_empty_path(self):
        """Test normalising empty path returns None."""

        from codex_crm.zaf_legacy.reader import _normalise_entry_path

        entry = zipfile.ZipInfo("")
        result = _normalise_entry_path(entry)

        assert result is None, "Result must not be empty"

    def test_normalise_dot_path(self):
        """Test normalising dot-only path returns None."""

        from codex_crm.zaf_legacy.reader import _normalise_entry_path

        entry = zipfile.ZipInfo("./")
        result = _normalise_entry_path(entry)

        assert result is None, "Result must not be empty"

    def test_normalise_rejects_path_traversal(self):
        """Test that path traversal is rejected."""
        from codex_crm.zaf_legacy.reader import _normalise_entry_path

        entry = zipfile.ZipInfo("../../../etc/passwd")

        with pytest.raises(ValueError, match="escapes"):
            _normalise_entry_path(entry)


class TestIsProbablyText:
    """Tests for _is_probably_text helper."""

    def test_is_text_js(self):
        """Test .js is text."""
        from codex_crm.zaf_legacy.reader import _is_probably_text

        assert _is_probably_text("app.js") is True, "Condition must be true"

    def test_is_text_json(self):
        """Test .json is text."""
        from codex_crm.zaf_legacy.reader import _is_probably_text

        assert _is_probably_text("config.json") is True, "Condition must be true"

    def test_is_text_html(self):
        """Test .html is text."""
        from codex_crm.zaf_legacy.reader import _is_probably_text

        assert _is_probably_text("index.html") is True, "Condition must be true"

    def test_is_not_text_png(self):
        """Test .png is not text."""
        from codex_crm.zaf_legacy.reader import _is_probably_text

        assert _is_probably_text("image.png") is False, "Condition must be true"

    def test_is_not_text_binary(self):
        """Test .bin is not text."""
        from codex_crm.zaf_legacy.reader import _is_probably_text

        assert _is_probably_text("data.bin") is False, "Data must not be empty"
