"""Comprehensive tests for codex_crm.d365_admin.generate module."""

from __future__ import annotations

import csv
from unittest.mock import patch


class TestEmitD365Config:
    """Tests for emit_d365_config function."""

    @patch("codex_crm.d365_admin.generate.load_cdm")
    def test_emit_d365_config_creates_directory(self, mock_cdm, tmp_path):
        """Test that output directory is created."""
        from codex_crm.cdm.loader import FieldDef
        from codex_crm.d365_admin.generate import emit_d365_config

        mock_cdm.return_value = {
            "assignment": [
                FieldDef(name="Field1", key="field1", ftype="text", required=True, choices=[])
            ]
        }

        out_dir = tmp_path / "d365" / "config"
        emit_d365_config(str(out_dir))

        assert out_dir.exists(), "Condition must be true"
        assert out_dir.is_dir(), "Condition must be true"

    @patch("codex_crm.d365_admin.generate.load_cdm")
    def test_emit_d365_config_creates_tables(self, mock_cdm, tmp_path):
        """Test that tables.csv is created."""
        from codex_crm.d365_admin.generate import emit_d365_config

        mock_cdm.return_value = {"assignment": []}

        out_dir = tmp_path / "d365"
        emit_d365_config(str(out_dir))

        tables_file = out_dir / "tables.csv"
        assert tables_file.exists(), "Condition must be true"

        with open(tables_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1, "Rows must not be empty"
        assert rows[0]["table"] == "cdx_assignment", "Condition must be true"
        assert rows[0]["display_name"] == "Assignment", "Condition must be true"

    @patch("codex_crm.d365_admin.generate.load_cdm")
    def test_emit_d365_config_creates_columns(self, mock_cdm, tmp_path):
        """Test that columns.csv is created."""
        from codex_crm.cdm.loader import FieldDef
        from codex_crm.d365_admin.generate import emit_d365_config

        mock_cdm.return_value = {
            "assignment": [
                FieldDef(
                    name="Status",
                    key="codex_status",
                    ftype="choice",
                    required=True,
                    choices=["open", "closed"],
                ),
                FieldDef(
                    name="Priority",
                    key="codex_priority",
                    ftype="integer",
                    required=False,
                    choices=[],
                ),
            ]
        }

        out_dir = tmp_path / "d365"
        emit_d365_config(str(out_dir))

        columns_file = out_dir / "columns.csv"
        assert columns_file.exists(), "Condition must be true"

        with open(columns_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2, "Rows must not be empty"
        assert rows[0]["logical_name"] == "cdx_status", "Condition must be true"
        assert rows[0]["display_name"] == "Status", "Condition must be true"
        assert rows[0]["required"] == "Yes", "Condition must be true"
        assert rows[0]["optionset"] == "open;closed", "Condition must be true"

        assert rows[1]["logical_name"] == "cdx_priority", "Condition must be true"
        assert rows[1]["type"] == "Integer", "Condition must be true"
        assert rows[1]["required"] == "No", "Condition must be true"

    @patch("codex_crm.d365_admin.generate.load_cdm")
    def test_emit_d365_config_creates_slas(self, mock_cdm, tmp_path):
        """Test that slas.csv is created."""
        from codex_crm.d365_admin.generate import emit_d365_config

        mock_cdm.return_value = {"assignment": []}

        out_dir = tmp_path / "d365"
        emit_d365_config(str(out_dir))

        slas_file = out_dir / "slas.csv"
        assert slas_file.exists(), "Condition must be true"

        with open(slas_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1, "Rows must not be empty"
        assert rows[0]["name"] == "cdx_assignment_standard", "Condition must be true"


class TestD365Key:
    """Tests for _d365_key helper."""

    def test_d365_key_replaces_codex_prefix(self):
        """Test that codex_ prefix is replaced with cdx_."""
        from codex_crm.d365_admin.generate import _d365_key

        assert _d365_key("codex_status") == "cdx_status", "Condition must be true"
        assert _d365_key("codex_priority") == "cdx_priority", "Condition must be true"

    def test_d365_key_no_prefix(self):
        """Test key without codex_ prefix."""
        from codex_crm.d365_admin.generate import _d365_key

        assert _d365_key("custom_field") == "custom_field", "Condition must be true"


class TestMapType:
    """Tests for _map_type helper."""

    def test_map_type_integer(self):
        """Test integer type mapping."""
        from codex_crm.d365_admin.generate import _map_type

        assert _map_type("integer") == "Integer", "Condition must be true"

    def test_map_type_choice(self):
        """Test choice type mapping."""
        from codex_crm.d365_admin.generate import _map_type

        assert _map_type("choice") == "Choice", "Condition must be true"

    def test_map_type_lookup(self):
        """Test lookup type mapping."""
        from codex_crm.d365_admin.generate import _map_type

        assert _map_type("lookup") == "Lookup", "Condition must be true"

    def test_map_type_unknown(self):
        """Test unknown type defaults to Text."""
        from codex_crm.d365_admin.generate import _map_type

        assert _map_type("text") == "Text", "Condition must be true"
        assert _map_type("unknown") == "Text", "Condition must be true"
        assert _map_type("custom") == "Text", "Condition must be true"
