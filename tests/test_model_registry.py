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
def _clear_model_env(monkeypatch):
    for key in (
        "CODEX_ML_GPT2_PATH",
        "CODEX_ML_TINYLLAMA_PATH",
        "CODEX_ML_OFFLINE_MODELS_DIR",
    ):
        monkeypatch.delenv(key, raising=False)


def test_gpt2_offline_uses_local_path(monkeypatch, tmp_path):
    sentinel = object()

    def fake_instantiate_model(alias, cfg=None):  # type: ignore[unused-argument]
        return sentinel

    monkeypatch.setattr(registries, "_instantiate_model", fake_instantiate_model)
    weights_dir = tmp_path / "gpt2"
    weights_dir.mkdir()
    monkeypatch.setenv("CODEX_ML_GPT2_PATH", str(weights_dir))

    result = registries.models.resolve_and_instantiate("gpt2-offline")

    assert result is sentinel


def test_gpt2_offline_missing_artifacts(monkeypatch):
    monkeypatch.delenv("CODEX_ML_GPT2_PATH", raising=False)
    monkeypatch.delenv("CODEX_ML_OFFLINE_MODELS_DIR", raising=False)

    with pytest.raises(FileNotFoundError) as excinfo:
        registries.models.resolve_and_instantiate("gpt2-offline")

    assert "gpt2-offline" in str(excinfo.value)


@pytest.mark.skipif(
    CliRunner is None or plugins_app is None,
    reason="plugin CLI unavailable",
)
def test_plugin_cli_lists_model_entries():
    runner = CliRunner()
    result = runner.invoke(plugins_app, ["list", "models"])
    assert result.exit_code == 0
    output = result.stdout.strip().splitlines()
    assert "gpt2-offline" in output
    assert "tinyllama-offline" in output
