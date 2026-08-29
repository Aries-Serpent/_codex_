"""Comprehensive tests for codex_crm.cdm.loader module."""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest


class TestFieldDef:
    """Tests for FieldDef dataclass."""

    def test_field_def_creation(self):
        """Test FieldDef instantiation."""
        from codex_crm.cdm.loader import FieldDef

        field = FieldDef(
            name="Test Field",
            key="test_field",
            ftype="text",
            required=True,
            choices=["a", "b", "c"],
            default="a",
        )
        assert field.name == "Test Field", "name is not valid"
        assert field.key == "test_field", "key is not valid"
        assert field.ftype == "text", "ftype is not valid"
        assert field.required is True, "required is not valid"
        assert field.choices == ["a", "b", "c"]
        assert field.default == "a", "default is not valid"

    def test_field_def_optional_default(self):
        """Test FieldDef with no default."""
        from codex_crm.cdm.loader import FieldDef

        field = FieldDef(name="Field", key="field", ftype="integer", required=False, choices=[])
        assert field.default is None, "default is not valid"

    def test_field_def_slots(self):
        """Test that FieldDef uses slots."""
        from codex_crm.cdm.loader import FieldDef

        field = FieldDef(name="F", key="f", ftype="t", required=False, choices=[])
        # Slots-based classes don't have __dict__
        assert not hasattr(field, "__dict__") or len(field.__dict__) == 0


class TestIterCsv:
    """Tests for _iter_csv helper."""

    def test_iter_csv_basic(self):
        """Test CSV iteration with mock resource."""
        from codex_crm.cdm.loader import _iter_csv

        csv_content = "name,key,type\nField1,field1,text\nField2,field2,integer"
        mock_resource = MagicMock()
        mock_resource.open.return_value.__enter__ = MagicMock(return_value=io.StringIO(csv_content))
        mock_resource.open.return_value.__exit__ = MagicMock(return_value=False)

        rows = list(_iter_csv(mock_resource))
        assert len(rows) == 2, "Rows must not be empty"
        assert rows[0]["name"] == "Field1", "Condition must be true"
        assert rows[1]["type"] == "integer", "Condition must be true"


class TestIterCsvDirectory:
    """Tests for _iter_csv_directory helper."""

    @patch("codex_crm.cdm.loader.resources.files")
    def test_iter_csv_directory_not_found(self, mock_files):
        """Test error when directory not found."""
        from codex_crm.cdm.loader import _iter_csv_directory

        mock_data_root = MagicMock()
        mock_data_root.is_dir.return_value = False
        mock_files.return_value.__truediv__.return_value.__truediv__.return_value = mock_data_root

        with pytest.raises(FileNotFoundError):
            list(_iter_csv_directory("nonexistent"))


class TestLoadCdm:
    """Tests for load_cdm function."""

    @patch("codex_crm.cdm.loader._iter_csv_directory")
    @patch("codex_crm.cdm.loader._iter_csv")
    def test_load_cdm_basic(self, mock_iter_csv, mock_iter_dir):
        """Test basic CDM loading."""
        from codex_crm.cdm.loader import load_cdm

        # Setup mock CSV file
        mock_csv_file = MagicMock()
        mock_csv_file.name = "assignment.csv"
        mock_iter_dir.return_value = [mock_csv_file]

        # Setup CSV rows
        mock_iter_csv.return_value = [
            {
                "name": "Field1",
                "key": "field1",
                "type": "text",
                "required": "true",
                "choices": "a|b|c",
                "default": "a",
            }
        ]

        cdm = load_cdm()
        assert "assignment" in cdm, "Condition must be true"
        assert len(cdm["assignment"]) == 1, "Collection must not be empty"
        field = cdm["assignment"][0]
        assert field.name == "Field1", "name is not valid"
        assert field.required is True, "required is not valid"
        assert field.choices == ["a", "b", "c"]

    @patch("codex_crm.cdm.loader._iter_csv_directory")
    @patch("codex_crm.cdm.loader._iter_csv")
    def test_load_cdm_required_false(self, mock_iter_csv, mock_iter_dir):
        """Test CDM loading with required=false."""
        from codex_crm.cdm.loader import load_cdm

        mock_csv_file = MagicMock()
        mock_csv_file.name = "entity.csv"
        mock_iter_dir.return_value = [mock_csv_file]

        mock_iter_csv.return_value = [
            {
                "name": "OptionalField",
                "key": "opt",
                "type": "text",
                "required": "false",
                "choices": "",
                "default": "",
            }
        ]

        cdm = load_cdm()
        assert cdm["entity"][0].required is False, "required is not valid"
        assert cdm["entity"][0].choices == [], "choices is not valid"
        assert cdm["entity"][0].default is None, "default is not valid"


class TestLoadMapping:
    """Tests for load_mapping function."""

    @patch("codex_crm.cdm.loader._iter_csv_directory")
    @patch("codex_crm.cdm.loader._iter_csv")
    def test_load_mapping_basic(self, mock_iter_csv, mock_iter_dir):
        """Test basic mapping loading."""
        from codex_crm.cdm.loader import load_mapping

        mock_csv_file = MagicMock()
        mock_csv_file.name = "zendesk.csv"
        mock_iter_dir.return_value = [mock_csv_file]

        mock_iter_csv.return_value = [
            {"cdm_key": "field1", "platform_key": "zd_field1"},
            {"cdm_key": "field2", "platform_key": "zd_field2"},
        ]

        mappings = load_mapping()
        assert "zendesk" in mappings, "Condition must be true"
        assert mappings["zendesk"]["field1"] == "zd_field1", "Condition must be true"
        assert mappings["zendesk"]["field2"] == "zd_field2", "Condition must be true"


class TestLoadJson:
    """Tests for load_json function."""

    def test_load_json_valid(self, tmp_path):
        """Test loading valid JSON file."""
        from codex_crm.cdm.loader import load_json

        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}', encoding="utf-8")

        data = load_json(json_file)
        assert data == {"key": "value"}, "Data must not be empty"

    def test_load_json_complex(self, tmp_path):
        """Test loading complex JSON file."""
        from codex_crm.cdm.loader import load_json

        json_file = tmp_path / "complex.json"
        json_file.write_text('{"items": [1, 2, 3], "nested": {"a": "b"}}', encoding="utf-8")

        data = load_json(json_file)
        assert data["items"] == [1, 2, 3]
        assert data["nested"]["a"] == "b", "Data must not be empty"
