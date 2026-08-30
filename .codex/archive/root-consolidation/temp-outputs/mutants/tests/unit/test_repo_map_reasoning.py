"""Unit tests for the Click-based `codex repo-map --reasoning` flag."""

import pytest
from click.testing import CliRunner

try:
    import codex_ml.cli.codex_cli as codex_cli
except ImportError as e:  # pragma: no cover - optional surface
    pytest.skip(f"CLI module not available: {e}", allow_module_level=True)

runner = CliRunner()


def test_repo_map_reasoning_flag_is_propagated(monkeypatch):
    """`--reasoning` flag should result in reasoning=True being forwarded."""

    calls = {}

    def fake_render_repo_map(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return "rendered"

    monkeypatch.setattr(
        "codex_ml.cli.repo_map.render_repo_map",
        fake_render_repo_map,
        raising=True,
    )

    result = runner.invoke(codex_cli.codex, ["repo-map", "--reasoning"])
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert result.output.strip() == "rendered", "Result must not be empty"
    assert calls.get("kwargs", {}).get("reasoning") is True


def test_repo_map_without_reasoning_flag(monkeypatch):
    """Omitting `--reasoning` should call render_repo_map with reasoning=False."""

    calls = {}

    def fake_render_repo_map(*args, **kwargs):
        calls["kwargs"] = kwargs
        return "rendered"

    monkeypatch.setattr(
        "codex_ml.cli.repo_map.render_repo_map",
        fake_render_repo_map,
        raising=True,
    )

    result = runner.invoke(codex_cli.codex, ["repo-map"])
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert result.output.strip() == "rendered", "Result must not be empty"
    assert calls.get("kwargs", {}).get("reasoning", False) is False


def test_repo_map_reasoning_legacy_fallback(monkeypatch):
    """TypeError from render_repo_map(reasoning=...) should trigger fallback call."""

    calls: list[tuple[tuple, dict]] = []

    def fake_render_repo_map(*args, **kwargs):
        calls.append((args, kwargs))
        # First invocation with reasoning should raise TypeError to trigger fallback.
        if len(calls) == 1 and kwargs:
            raise TypeError("unexpected keyword 'reasoning'")
        return "fallback-render"

    monkeypatch.setattr(
        "codex_ml.cli.repo_map.render_repo_map",
        fake_render_repo_map,
        raising=True,
    )

    result = runner.invoke(codex_cli.codex, ["repo-map", "--reasoning"])
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert "fallback-render" in result.output, "Result must not be empty"
    assert calls[0][1].get("reasoning") is True, "Condition must be true"
    assert calls[1][1] == {}, "Condition must be true"
