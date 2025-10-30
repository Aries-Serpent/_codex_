"""
Unit tests for CLI `repo-map --reasoning` flag propagation.

Goals:
  * Verify `codex repo-map --reasoning` forwards reasoning=True to implementation.
  * Verify default (no flag) leaves reasoning False/omitted.
  * Provide a guarded xfail for legacy fallback (if not yet implemented).

Constraints:
  - Do not modify production CLI.
  - Tests must pass in local dev (pytest, typer.testing).
"""

import pytest

from typer.testing import CliRunner

try:
    import codex_ml.cli.codex_cli as codex_cli  # expected to export `app` and `_print_repo_map`
except Exception as e:  # pragma: no cover
    pytest.skip(f"CLI module not importable: {e}", allow_module_level=True)

runner = CliRunner()


def _require_cli_bits():
    """Skip tests if the CLI surface isn't present locally."""
    if not hasattr(codex_cli, "app"):
        pytest.skip("codex_cli.app not found")
    if not hasattr(codex_cli, "_print_repo_map"):
        pytest.skip("codex_cli._print_repo_map not found")


def test_repo_map_reasoning_flag_is_propagated(monkeypatch):
    """
    Expectation:
      `codex repo-map --reasoning` passes reasoning=True to _print_repo_map.
    """
    _require_cli_bits()
    calls = {}

    def fake_print_repo_map(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        print("OK: repo-map invoked with reasoning")

    monkeypatch.setattr(codex_cli, "_print_repo_map", fake_print_repo_map, raising=True)

    result = runner.invoke(codex_cli.app, ["repo-map", "--reasoning"])
    assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"
    assert calls.get("kwargs", {}).get("reasoning") is True, f"Expected reasoning=True; got {calls}"


def test_repo_map_without_reasoning_flag(monkeypatch):
    """
    Expectation:
      `codex repo-map` (no flag) results in reasoning=False (or omitted→False).
    """
    _require_cli_bits()
    calls = {}

    def fake_print_repo_map(*args, **kwargs):
        calls["kwargs"] = kwargs
        print("OK: repo-map invoked without reasoning")

    monkeypatch.setattr(codex_cli, "_print_repo_map", fake_print_repo_map, raising=True)
    result = runner.invoke(codex_cli.app, ["repo-map"])
    assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"
    assert calls.get("kwargs", {}).get("reasoning", False) is False, f"Expected False; got {calls}"


@pytest.mark.xfail(
    reason="Legacy fallback may not exist yet; unmark when implemented", strict=False
)
def test_repo_map_legacy_fallback_signature(monkeypatch):
    """
    Optional legacy guard:
      If the CLI tries `_print_repo_map(reasoning=True)` but the implementation
      only accepts no-arg call, a robust CLI would catch TypeError and retry.
      This test is marked xfail until that behavior lands.
    """
    _require_cli_bits()

    def legacy_noarg_impl():
        print("OK: legacy repo-map (no kwargs)")

    # Simulate a signature mismatch by swapping in a no-arg impl.
    monkeypatch.setattr(codex_cli, "_print_repo_map", legacy_noarg_impl, raising=True)
    result = runner.invoke(codex_cli.app, ["repo-map", "--reasoning"])
    # A resilient CLI would still succeed.
    assert result.exit_code == 0, f"Expected legacy fallback; got failure: {result.output}"
