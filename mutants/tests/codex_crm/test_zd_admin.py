"""Comprehensive tests for codex_crm.zd_admin.generate module."""

from __future__ import annotations

import json
from unittest.mock import patch


class TestEmitZendeskConfig:
    """Tests for emit_zendesk_config function."""

    @patch("codex_crm.zd_admin.generate.load_cdm")
    @patch("codex_crm.zd_admin.generate.load_mapping")
    def test_emit_zendesk_config_creates_directory(self, mock_mapping, mock_cdm, tmp_path):
        """Test that output directory is created."""
        from codex_crm.cdm.loader import FieldDef
        from codex_crm.zd_admin.generate import emit_zendesk_config

        mock_cdm.return_value = {
            "assignment": [
                FieldDef(name="Field1", key="field1", ftype="text", required=True, choices=[])
            ]
        }
        mock_mapping.return_value = {}

        out_dir = tmp_path / "zendesk" / "config"
        emit_zendesk_config(str(out_dir))

        assert out_dir.exists(), "Condition must be true"
        assert out_dir.is_dir(), "Condition must be true"

    @patch("codex_crm.zd_admin.generate.load_cdm")
    @patch("codex_crm.zd_admin.generate.load_mapping")
    def test_emit_zendesk_config_creates_forms(self, mock_mapping, mock_cdm, tmp_path):
        """Test that forms.json is created."""
        from codex_crm.cdm.loader import FieldDef
        from codex_crm.zd_admin.generate import emit_zendesk_config

        mock_cdm.return_value = {
            "assignment": [
                FieldDef(
                    name="Status",
                    key="status",
                    ftype="choice",
                    required=True,
                    choices=["open", "closed"],
                )
            ]
        }
        mock_mapping.return_value = {}

        out_dir = tmp_path / "zendesk"
        emit_zendesk_config(str(out_dir))

        forms_file = out_dir / "forms.json"
        assert forms_file.exists(), "f is not valid"

        forms = json.loads(forms_file.read_text())
        assert isinstance(forms, list)
        assert len(forms) == 1, "Forms must not be empty"
        assert forms[0]["title"] == "Assignment", "f is not valid"
        assert "fields" in forms[0], "Condition must be true"

    @patch("codex_crm.zd_admin.generate.load_cdm")
    @patch("codex_crm.zd_admin.generate.load_mapping")
    def test_emit_zendesk_config_creates_triggers(self, mock_mapping, mock_cdm, tmp_path):
        """Test that triggers.json is created."""
        from codex_crm.zd_admin.generate import emit_zendesk_config

        mock_cdm.return_value = {"assignment": []}
        mock_mapping.return_value = {}

        out_dir = tmp_path / "zendesk"
        emit_zendesk_config(str(out_dir))

        triggers_file = out_dir / "triggers.json"
        assert triggers_file.exists(), "Condition must be true"

        triggers = json.loads(triggers_file.read_text())
        assert isinstance(triggers, list)
        assert len(triggers) == 1, "Triggers must not be empty"
        assert triggers[0]["title"] == "codex_assignment_auto_route", "Condition must be true"

    @patch("codex_crm.zd_admin.generate.load_cdm")
    @patch("codex_crm.zd_admin.generate.load_mapping")
    def test_emit_zendesk_config_creates_sla(self, mock_mapping, mock_cdm, tmp_path):
        """Test that sla.json is created."""
        from codex_crm.zd_admin.generate import emit_zendesk_config

        mock_cdm.return_value = {"assignment": []}
        mock_mapping.return_value = {}

        out_dir = tmp_path / "zendesk"
        emit_zendesk_config(str(out_dir))

        sla_file = out_dir / "sla.json"
        assert sla_file.exists(), "Condition must be true"

        sla = json.loads(sla_file.read_text())
        assert isinstance(sla, list)
        assert sla[0]["title"] == "codex_assignment_standard", "Condition must be true"
        assert "policy" in sla[0], "Condition must be true"

    @patch("codex_crm.zd_admin.generate.load_cdm")
    @patch("codex_crm.zd_admin.generate.load_mapping")
    def test_emit_zendesk_config_creates_mappings(self, mock_mapping, mock_cdm, tmp_path):
        """Test that mappings.json is created."""
        from codex_crm.zd_admin.generate import emit_zendesk_config

        mock_cdm.return_value = {"assignment": []}
        mock_mapping.return_value = {"scope1": {"key1": "value1"}}

        out_dir = tmp_path / "zendesk"
        emit_zendesk_config(str(out_dir))

        mappings_file = out_dir / "mappings.json"
        assert mappings_file.exists(), "Condition must be true"

        mappings = json.loads(mappings_file.read_text())
        assert mappings == {"scope1": {"key1": "value1"}}, "Value must be initialized"


class TestAssignmentForm:
    """Tests for _assignment_form helper."""

    def test_assignment_form_basic(self):
        """Test assignment form generation."""
        from codex_crm.cdm.loader import FieldDef
        from codex_crm.zd_admin.generate import _assignment_form

        fields = [
            FieldDef(name="Field1", key="f1", ftype="text", required=True, choices=[]),
            FieldDef(name="Field2", key="f2", ftype="choice", required=False, choices=["a", "b"]),
        ]
        form = _assignment_form(fields)

        assert form["title"] == "Assignment", "f is not valid"
        assert len(form["fields"]) == 2, "Collection must not be empty"
        assert form["fields"][0]["id"] == "f1", "f is not valid"
        assert form["fields"][0]["type"] == "text", "f is not valid"
        assert form["fields"][0]["required"] is True, "f is not valid"
        assert form["fields"][1]["required"] is False, "f is not valid"


class TestDumpJson:
    """Tests for _dump_json helper."""

    def test_dump_json_sorted_keys(self):
        """Test that JSON output has sorted keys."""
        from codex_crm.zd_admin.generate import _dump_json

        result = _dump_json({"z": 1, "a": 2, "m": 3})
        assert result.index('"a"') < result.index('"m"') < result.index('"z"'), "Result must not be empty"

    def test_dump_json_indented(self):
        """Test that JSON output is indented."""
        from codex_crm.zd_admin.generate import _dump_json

        result = _dump_json({"key": "value"})
        assert "\n" in result, "Result must not be empty"
