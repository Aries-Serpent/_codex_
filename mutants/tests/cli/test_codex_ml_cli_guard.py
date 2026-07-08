"""Ensure the Codex ML CLI degrades gracefully when torch is unavailable."""

from __future__ import annotations

import importlib
from pathlib import Path

from click.testing import CliRunner


def test_train_model_reports_missing_torch(monkeypatch) -> None:
    module = importlib.import_module("codex_ml.cli.__init__")
    monkeypatch.setattr(module, "_HAS_TORCH", False, raising=False)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(module.cli, ["train-model"])

        assert result.exit_code == 1, "Result must not be empty"
        assert "pip install codex_ml[torch]" in result.output, "Result must not be empty"

        error_log = Path(".codex/errors.ndjson")
        assert error_log.exists(), "Error should be raised or set"
        contents = error_log.read_text(encoding="utf-8").strip().splitlines()
        assert contents, "expected CLI guard to log an error entry"
