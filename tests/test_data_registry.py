from __future__ import annotations

import pytest

from codex_ml.data.registry import get_dataset
from codex_ml.plugins.registries import datasets as plugin_datasets


def test_offline_tiny_corpus_loads_from_path(tmp_path):
    data_file = tmp_path / "tiny.txt"
    data_file.write_text("alpha\nbeta\n", encoding="utf-8")

    records = get_dataset("offline:tiny-corpus", path=str(data_file), shuffle=False)
    assert records == ["alpha", "beta"]


def test_offline_tiny_corpus_missing(tmp_path, monkeypatch):
    missing = tmp_path / "missing.txt"
    monkeypatch.delenv("CODEX_ML_TINY_CORPUS_PATH", raising=False)
    monkeypatch.setenv("CODEX_ML_OFFLINE_DATASETS_DIR", str(tmp_path / "other"))

    with pytest.raises(FileNotFoundError):
        get_dataset("offline:tiny-corpus", path=str(missing))


def test_plugin_catalogue_offline_tiny_corpus(tmp_path):
    data_file = tmp_path / "tiny.txt"
    data_file.write_text("alpha\nbeta\n", encoding="utf-8")

    records = plugin_datasets.resolve_and_instantiate(
        "offline:tiny-corpus",
        path=str(data_file),
        shuffle=False,
    )
    assert records == ["alpha", "beta"]


def test_plugin_catalogue_offline_tiny_corpus_missing(tmp_path, monkeypatch):
    missing = tmp_path / "missing.txt"
    monkeypatch.delenv("CODEX_ML_TINY_CORPUS_PATH", raising=False)
    monkeypatch.setenv("CODEX_ML_OFFLINE_DATASETS_DIR", str(tmp_path / "other"))

    with pytest.raises(FileNotFoundError):
        plugin_datasets.resolve_and_instantiate(
            "offline:tiny-corpus",
            path=str(missing),
        )


def test_plugins_cli_lists_offline_datasets():
    pytest.importorskip("typer")
    from typer.testing import CliRunner

    from codex_ml.cli import plugins_cli

    runner = CliRunner()
    result = runner.invoke(plugins_cli.app, ["list", "datasets"])
    assert result.exit_code == 0
    output = result.stdout.splitlines()
    assert any("offline:tiny-corpus" in line for line in output)
