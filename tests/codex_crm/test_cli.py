"""Comprehensive tests for codex_crm.cli module."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestBuildParser:
    """Tests for build_parser function."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_has_subcommands(self):
        """Test that parser has expected subcommands."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        # Check subparsers exist by trying to parse known commands
        with pytest.raises(SystemExit):
            parser.parse_args([])  # No command should fail

    def test_apply_zd_subcommand(self):
        """Test apply-zd subcommand parsing."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["apply-zd"])
        assert args.command == "apply-zd", "command is not valid"
        assert args.out == ".codex/crm/zendesk", "out is not valid"

    def test_apply_zd_custom_output(self):
        """Test apply-zd with custom output."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["apply-zd", "--out", "/custom/path"])
        assert args.out == "/custom/path", "out is not valid"

    def test_apply_d365_subcommand(self):
        """Test apply-d365 subcommand parsing."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["apply-d365"])
        assert args.command == "apply-d365", "command is not valid"
        assert args.out == ".codex/crm/d365", "out is not valid"

    def test_import_pa_zip_subcommand(self):
        """Test import-pa-zip subcommand parsing."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["import-pa-zip", "--in", "input.zip", "--out", "output/"])
        assert args.command == "import-pa-zip", "command is not valid"
        assert args.source == "input.zip", "source is not valid"
        assert args.out == "output/", "out is not valid"

    def test_import_zaf_zip_subcommand(self):
        """Test import-zaf-zip subcommand parsing."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["import-zaf-zip", "--in", "app.zip", "--out", "scaffold/"])
        assert args.command == "import-zaf-zip", "command is not valid"
        assert args.source == "app.zip", "source is not valid"
        assert args.out == "scaffold/", "out is not valid"

    def test_gen_diagram_subcommand(self):
        """Test gen-diagram subcommand parsing."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(
            [
                "gen-diagram",
                "--flow",
                "test_flow",
                "--steps",
                "step1;step2;step3",
                "--out",
                "diagram.mmd",
            ]
        )
        assert args.command == "gen-diagram", "command is not valid"
        assert args.flow == "test_flow", "flow is not valid"
        assert args.steps == "step1;step2;step3", "steps is not valid"
        assert args.out == "diagram.mmd", "out is not valid"

    def test_evidence_pack_subcommand(self):
        """Test evidence-pack subcommand parsing."""
        from codex_crm.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["evidence-pack", "--out", "evidence/"])
        assert args.command == "evidence-pack", "command is not valid"
        assert args.out == "evidence/", "out is not valid"


class TestMainFunction:
    """Tests for main function."""

    @patch("codex_crm.cli.emit_zendesk_config")
    def test_main_apply_zd(self, mock_emit):
        """Test main with apply-zd command."""
        from codex_crm.cli import main

        result = main(["apply-zd", "--out", os.path.join(tempfile.gettempdir(), "zd")])
        assert result == 0, "Result must not be empty"
        mock_emit.assert_called_once_with(os.path.join(tempfile.gettempdir(), "zd"))

    @patch("codex_crm.cli.emit_d365_config")
    def test_main_apply_d365(self, mock_emit):
        """Test main with apply-d365 command."""
        from codex_crm.cli import main

        result = main(["apply-d365", "--out", os.path.join(tempfile.gettempdir(), "d365")])
        assert result == 0, "Result must not be empty"
        mock_emit.assert_called_once_with(os.path.join(tempfile.gettempdir(), "d365"))

    @patch("codex_crm.cli.write_evidence")
    def test_main_evidence_pack(self, mock_write):
        """Test main with evidence-pack command."""
        from codex_crm.cli import main

        result = main(["evidence-pack", "--out", os.path.join(tempfile.gettempdir(), "evidence")])
        assert result == 0, "Result must not be empty"
        mock_write.assert_called_once_with(os.path.join(tempfile.gettempdir(), "evidence"))

    @patch("codex_crm.cli.flow_to_mermaid")
    def test_main_gen_diagram(self, mock_flow, tmp_path):
        """Test main with gen-diagram command."""
        from codex_crm.cli import main

        mock_flow.return_value = "graph TD\n  A --> B"
        output_file = tmp_path / "test.mmd"

        result = main(
            ["gen-diagram", "--flow", "test", "--steps", "A;B", "--out", str(output_file)]
        )
        assert result == 0, "Result must not be empty"
        mock_flow.assert_called_once_with("test", ["A", "B"])

    def test_main_gen_diagram_steps_parsing(self, tmp_path):
        """Test that steps are parsed correctly."""
        from codex_crm.cli import main

        output_file = tmp_path / "test.mmd"

        with patch("codex_crm.cli.flow_to_mermaid") as mock_flow:
            mock_flow.return_value = "graph TD"
            main(
                [
                    "gen-diagram",
                    "--flow",
                    "flow",
                    "--steps",
                    "  step1 ; step2 ; ; step3  ",
                    "--out",
                    str(output_file),
                ]
            )
            # Should strip whitespace and filter empty
            mock_flow.assert_called_once_with("flow", ["step1", "step2", "step3"])


class TestConstants:
    """Tests for module constants."""

    def test_default_output_root(self):
        """Test default output root constant."""
        from codex_crm.cli import DEFAULT_OUTPUT_ROOT

        assert Path(".codex") / "crm" == DEFAULT_OUTPUT_ROOT, "Condition must be true"

    def test_default_zendesk_output(self):
        """Test default Zendesk output constant."""
        from codex_crm.cli import DEFAULT_ZENDESK_OUTPUT

        assert Path(".codex") / "crm" / "zendesk" == DEFAULT_ZENDESK_OUTPUT, "Condition must be true"

    def test_default_d365_output(self):
        """Test default D365 output constant."""
        from codex_crm.cli import DEFAULT_D365_OUTPUT

        assert Path(".codex") / "crm" / "d365" == DEFAULT_D365_OUTPUT, "Condition must be true"
