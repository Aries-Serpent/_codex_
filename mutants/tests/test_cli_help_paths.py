"""Smoke tests to guarantee CLI help paths stay accessible."""

from __future__ import annotations

import sys

import pytest

from tests.utils.cli_runner import run_module


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Typer help formatting differs on Windows"
)
def test_codex_ml_cli_help_succeeds():
    """`python -m codex_ml.cli.main --help` should print guidance and exit cleanly."""

    result = run_module("codex_ml.cli.main", "--help")
    assert result.returncode == 0
    stderr = result.stderr.strip()
    # When hydra-core is unavailable we surface guidance via stderr.
    if "hydra-core" in stderr:
        assert "codex-ml-cli requires hydra-core" in stderr
    else:
        # Hydra available: Typer/argparse prints usage to stdout.
        assert "Usage" in result.stdout or "usage" in result.stdout


def test_tokenization_cli_help_lists_commands():
    """`python -m tokenization.cli --help` should list available commands."""

    result = run_module("tokenization.cli", "--help")
    assert result.returncode == 0
    output = result.stdout + result.stderr
    try:  # Typer is optional; importing may fail if the extra isn't installed.
        import typer  # type: ignore
    except Exception:
        typer_available = False
    else:
        typer_available = hasattr(typer, "Typer")
    # Typer prints "Usage" header; fallback shim echoes commands.
    if typer_available:
        assert "Usage" in output or "usage" in output
    else:
        assert "tokenizer utilities" in output.lower()
    for command in ("inspect", "encode", "export"):
        assert command in output
