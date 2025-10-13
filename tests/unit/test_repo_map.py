from __future__ import annotations

import sys
import types
from pathlib import Path

from click.testing import CliRunner


def _ensure_config_settings_stub() -> None:
    """Inject minimal stubs so that codex imports succeed without full settings."""
    if "codex_ml.config.settings" in sys.modules:
        return

    module = types.ModuleType("codex_ml.config.settings")

    class _StubAppSettings:  # pragma: no cover
        pass

    class _StubEvalRow:  # pragma: no cover
        @staticmethod
        def model_json_schema() -> dict:
            return {}

    def _eval_row_schema() -> dict:
        return {}

    def _get_settings() -> _StubAppSettings:
        return _StubAppSettings()

    module.AppSettings = _StubAppSettings
    module.EvalRow = _StubEvalRow
    module.eval_row_schema = _eval_row_schema  # type: ignore[attr-defined]
    module.get_settings = _get_settings  # type: ignore[attr-defined]
    sys.modules["codex_ml.config.settings"] = module


def test_repo_map_lists_visible_top_level_entries() -> None:
    """Ensure repo-map CLI lists all visible entries and omits hidden ones."""
    _ensure_config_settings_stub()

    from codex_ml.cli.codex_cli import codex

    runner = CliRunner()
    result = runner.invoke(codex, ["repo-map"])

    assert result.exit_code == 0
    lines = [line for line in result.output.splitlines() if line.strip()]
    assert lines, "expected repo-map to emit at least one entry"

    entries = [line.split()[-1] for line in lines]
    assert all(not entry.startswith(".") for entry in entries)
    assert any(entry.endswith("/") for entry in entries)

    repo_root = Path(__file__).resolve().parents[2]
    for entry in entries:
        name = entry.rstrip("/")
        assert (repo_root / name).exists()
