"""Comprehensive tests for codex_crm.pa_legacy.reader module."""

from __future__ import annotations

import json
import zipfile

import pytest


class TestPowerAutomateExceptions:
    """Tests for Power Automate exceptions."""

    def test_parse_error_exists(self):
        """Test PowerAutomateParseError exists."""
        from codex_crm.pa_legacy.reader import PowerAutomateParseError

        with pytest.raises(PowerAutomateParseError):
            raise PowerAutomateParseError("Test error")

    def test_package_error_exists(self):
        """Test PowerAutomatePackageError exists as alias."""
        from codex_crm.pa_legacy.reader import (
            PowerAutomatePackageError,
            PowerAutomateParseError,
        )

        # Package error should be a subclass of ParseError
        assert issubclass(PowerAutomatePackageError, PowerAutomateParseError)


class TestReadPaLegacy:
    """Tests for read_pa_legacy function."""

    def test_read_pa_legacy_basic(self, tmp_path):
        """Test reading a basic PA package."""
        from codex_crm.pa_legacy.reader import read_pa_legacy

        # Create a test ZIP
        zip_path = tmp_path / "test.zip"
        manifest = {"name": "TestFlow", "version": "1.0"}
        flow_def = {"definition": {"steps": []}}

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("flows/flow1.json", json.dumps(flow_def))

        result = read_pa_legacy(zip_path)

        assert "manifest" in result, "Result must not be empty"
        assert result["manifest"]["name"] == "TestFlow", "Result must not be empty"
        assert "flows" in result, "Result must not be empty"
        assert "flow1" in result["flows"], "Result must not be empty"

    def test_read_pa_legacy_multiple_flows(self, tmp_path):
        """Test reading PA package with multiple flows."""
        from codex_crm.pa_legacy.reader import read_pa_legacy

        zip_path = tmp_path / "multi.zip"
        manifest = {"name": "MultiFlow"}

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("manifest.json", json.dumps(manifest))
            zf.writestr("flows/flow1.json", json.dumps({"id": "1"}))
            zf.writestr("flows/flow2.json", json.dumps({"id": "2"}))
            zf.writestr("flows/nested/flow3.json", json.dumps({"id": "3"}))

        result = read_pa_legacy(zip_path)

        assert len(result["flows"]) >= 2, "Collection must not be empty"

    def test_read_pa_legacy_invalid_zip(self, tmp_path):
        """Test reading invalid ZIP raises error."""
        from codex_crm.pa_legacy.reader import PowerAutomateParseError, read_pa_legacy

        invalid_file = tmp_path / "invalid.zip"
        invalid_file.write_text("not a zip")

        with pytest.raises(PowerAutomateParseError):
            read_pa_legacy(invalid_file)

    def test_read_pa_legacy_missing_manifest(self, tmp_path):
        """Test reading ZIP without manifest raises error."""
        from codex_crm.pa_legacy.reader import PowerAutomateParseError, read_pa_legacy

        zip_path = tmp_path / "no_manifest.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("flows/flow1.json", json.dumps({}))

        with pytest.raises(PowerAutomateParseError):
            read_pa_legacy(zip_path)


class TestToTemplate:
    """Tests for to_template function."""

    def test_to_template_basic(self):
        """Test basic template conversion."""
        from codex_crm.pa_legacy.reader import to_template

        package = {
            "manifest": {"name": "Test"},
            "flows": {"flow1": {"definition": {"resources": {"connection1": {"type": "sql"}}}}},
        }

        template = to_template(package)

        assert "connections" in template, "Condition must be true"
        assert "flows" in template, "Condition must be true"
        assert "variables" in template, "Condition must be true"
        assert len(template["connections"]) == 1, "Collection must not be empty"
        assert template["connections"][0]["name"] == "connection1", "Condition must be true"
        assert template["connections"][0]["type"] == "sql", "Condition must be true"
        assert "${CONN_CONNECTION1}" in template["connections"][0]["placeholder"], "Condition must be true"

    def test_to_template_empty_flows(self):
        """Test template conversion with empty flows."""
        from codex_crm.pa_legacy.reader import to_template

        package = {"flows": {}}
        template = to_template(package)

        assert template["connections"] == [], "Condition must be true"
        assert template["flows"] == {}, "Condition must be true"
        assert template["variables"] == [], "Condition must be true"

    def test_to_template_no_resources(self):
        """Test template conversion with flow missing resources."""
        from codex_crm.pa_legacy.reader import to_template

        package = {"flows": {"flow1": {"definition": {}}}}

        template = to_template(package)
        assert template["connections"] == [], "Condition must be true"

    def test_to_template_missing_type(self):
        """Test template conversion with missing type defaults to unknown."""
        from codex_crm.pa_legacy.reader import to_template

        package = {"flows": {"flow1": {"definition": {"resources": {"conn": {}}}}}}

        template = to_template(package)
        assert template["connections"][0]["type"] == "unknown", "Condition must be true"
