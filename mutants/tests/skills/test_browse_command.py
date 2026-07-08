"""Tests for the codex-skill browse command."""

from __future__ import annotations

import pytest

pytest.importorskip("typer", reason="typer required for browse command tests")

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from codex.skills.cli import app

runner = CliRunner()


class TestBrowseCommand:
    """Tests for codex-skill browse."""

    def test_browse_no_dist_no_skills(self):
        """With an empty registry, browse exits gracefully."""
        reg = MagicMock()
        reg.list.return_value = []
        with patch("codex.skills.cli._ensure_registry", return_value=reg):
            result = runner.invoke(app, ["browse"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "No skills found" in result.output, "Result must not be empty"

    def test_browse_lists_skills(self):
        """Browse shows skills table with index numbers."""
        skill = MagicMock()
        skill.skill_id = "doc.retriever.core"
        skill.version = "1.0.0"
        skill.manifest.capability_tags = ["docs"]
        skill.manifest.policy.risk_tier = "low"
        skill.manifest.doc.aais_score = 0.88
        skill.manifest.name = "Doc Retriever"

        reg = MagicMock()
        reg.list.return_value = [skill]
        reg.__len__ = MagicMock(return_value=1)

        with (
            patch("codex.skills.cli._ensure_registry", return_value=reg),
            patch("codex.skills.cli._prompt_selection", return_value=None),
        ):
            result = runner.invoke(app, ["browse", "--no-install"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "doc.retriever.core" in result.output, "Result must not be empty"
        assert "1" in result.output, "Result must not be empty"

    def test_browse_dist_no_archives(self, tmp_path):
        """Browse with --dist and empty dir exits gracefully."""
        result = runner.invoke(app, ["browse", "--dist", str(tmp_path)])
        assert result.exit_code == 0, "Result must not be empty"
        assert "No .7z or .zip archives found" in result.output, "Result must not be empty"

    def test_browse_dist_lists_archives(self, tmp_path):
        """Browse with --dist shows archive list."""
        arc = tmp_path / "doc-retriever-core-1.0.0.7z"
        arc.write_bytes(b"fake archive content")

        with patch("codex.skills.cli._prompt_selection", return_value=None):
            result = runner.invoke(app, ["browse", "--dist", str(tmp_path), "--no-install"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "doc-retriever-core-1.0.0.7z" in result.output, "Result must not be empty"

    def test_browse_dist_missing_dir(self):
        """Browse with non-existent --dist exits with code 1."""
        result = runner.invoke(app, ["browse", "--dist", "/nonexistent/path/xyz"])
        assert result.exit_code == 1, "Result must not be empty"

    def test_browse_dist_installs_selected(self, tmp_path):
        """Browse with --dist installs selected archive."""
        arc = tmp_path / "doc-retriever-core-1.0.0.7z"
        arc.write_bytes(b"fake")

        install_dest = tmp_path / "installed" / "doc-retriever-core"
        install_dest.mkdir(parents=True)

        reg = MagicMock()
        reg.__len__ = MagicMock(return_value=1)

        with (
            patch("codex.skills.cli._prompt_selection", return_value=1),
            patch("codex.skills.cli.install_skill", return_value=install_dest) as mock_install,
            patch("codex.skills.cli._ensure_registry", return_value=reg),
        ):
            result = runner.invoke(app, ["browse", "--dist", str(tmp_path)])

        assert result.exit_code == 0, "Result must not be empty"
        mock_install.assert_called_once_with(arc)
        assert "Installed to" in result.output, "Result must not be empty"
