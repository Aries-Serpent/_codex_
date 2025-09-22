import pytest

try:
    from typer.testing import CliRunner
except ModuleNotFoundError:  # pragma: no cover - optional dependency guard
    CliRunner = None  # type: ignore[assignment]

try:
    from codex_ml.cli.plugins_cli import app as plugins_app
except ModuleNotFoundError:  # pragma: no cover - optional dependency guard
    plugins_app = None  # type: ignore[assignment]

from codex_ml.plugins import registries


@pytest.fixture(autouse=True)
def _clear_dataset_env(monkeypatch):
    for key in ("CODEX_ML_TINY_CORPUS_PATH", "CODEX_ML_OFFLINE_DATASETS_DIR"):
        monkeypatch.delenv(key, raising=False)


def test_offline_dataset_loads_fixture(monkeypatch, tmp_path):
    dataset_file = tmp_path / "tiny_corpus.txt"
    dataset_file.write_text("one\ntwo\n", encoding="utf-8")
    monkeypatch.setenv("CODEX_ML_TINY_CORPUS_PATH", str(dataset_file))

    records = registries.datasets.resolve_and_instantiate("offline:tiny-corpus", shuffle=False)

    assert records == ["one", "two"]


def test_offline_dataset_missing_raises(tmp_path):
    bogus = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError) as excinfo:
        registries.datasets.resolve_and_instantiate("offline:tiny-corpus", path=str(bogus))

    assert "offline:tiny-corpus" in str(excinfo.value)


@pytest.mark.skipif(
    CliRunner is None or plugins_app is None,
    reason="plugin CLI unavailable",
)
def test_plugin_cli_lists_datasets():
    runner = CliRunner()
    result = runner.invoke(plugins_app, ["list", "datasets"])
    assert result.exit_code == 0
    entries = result.stdout.strip().splitlines()
    assert "offline:tiny-corpus" in entries
