"""
Test Repo Map Command

Test module for repo map command.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner


def test_repo_map_lists_visible_entries() -> None:
    codex_cli = pytest.importorskip("codex_ml.cli.codex_cli")

    runner = CliRunner()
    result = runner.invoke(codex_cli.codex, ["repo-map"], catch_exceptions=False)

    assert result.exit_code == 0, "Result must not be empty"
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    assert any(line.startswith("[dir] src/") for line in lines), "Condition must be true"
    assert any(line.endswith("pyproject.toml") for line in lines), "Condition must be true"


def test_repo_map_reasoning_surface_knobs() -> None:
    codex_cli = pytest.importorskip("codex_ml.cli.codex_cli")

    runner = CliRunner()
    result = runner.invoke(
        codex_cli.codex,
        ["repo-map", "--reasoning"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, "Result must not be empty"
    output = result.output
    assert "reasoning_status:" in output, "Condition must be true"
    assert "trace_mode" in output, "Condition must be true"
    assert "curriculum.preset" in output, "Condition must be true"
    assert "rollout_ring" in output, "Condition must be true"
