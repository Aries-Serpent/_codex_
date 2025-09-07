import pytest

pytest.importorskip("hydra")

from codex_ml.cli.main import cli  # noqa: E402


def test_codexml_cli_help():
    with pytest.raises(SystemExit):
        cli(["--help"])


def test_codexml_cli_skips_eval(monkeypatch):
    from hydra._internal.hydra import GlobalHydra

    called = {"eval": False}

    # Patch the evaluation entrypoint used by the CLI
    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    # Explicitly disable evaluation via config; CLI should exit cleanly and not call evaluate
    with pytest.raises(SystemExit) as excinfo:
        cli(["pipeline.steps=[evaluate]", "eval=null", "hydra.run.dir=."])
    assert excinfo.value.code == 0
    assert called is False

    def fake_eval(*args, **kwargs):
        called["eval"] = True

    monkeypatch.setattr("codex_ml.cli.main.run_training", lambda cfg: None)
    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    with pytest.raises(SystemExit):
        cli(["eval=null"])

    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    # With default config (no eval=null), the CLI should attempt evaluation
    with pytest.raises(SystemExit) as excinfo:
        cli(["hydra.run.dir=."])
    assert excinfo.value.code == 0
    assert called is True
