"""Smoke test for codex.cli_release Typer app."""

from __future__ import annotations

import pytest

# Skip if typer is not properly installed
try:
    import typer

    if not hasattr(typer, "Typer"):
        pytest.skip("typer package not properly installed", allow_module_level=True)
    from typer.testing import CliRunner

    from codex import cli_release

    TYPER_AVAILABLE = True
except (ImportError, AttributeError):
    TYPER_AVAILABLE = False
    pytest.skip("typer package not available", allow_module_level=True)


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="typer not available")
def test_cli_release_help():
    runner = CliRunner()
    result = runner.invoke(cli_release.app, ["--help"])
    assert result.exit_code == 0, "Result must not be empty"
    assert result.output, "Result must not be empty"
