from __future__ import annotations

import pytest
from click.testing import CliRunner


def test_repo_map_lists_visible_entries() -> None:
    codex_cli = pytest.importorskip("codex_ml.cli.codex_cli")

    runner = CliRunner()
    result = runner.invoke(codex_cli.codex, ["repo-map"], catch_exceptions=False)

    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    assert any(line.startswith("[dir] src/") for line in lines)
    assert any(line.endswith("pyproject.toml") for line in lines)
