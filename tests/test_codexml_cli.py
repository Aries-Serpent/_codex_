import pytest

pytest.importorskip("hydra")

from codex_ml.cli.main import cli  # noqa: E402


def test_codexml_cli_help():
    with pytest.raises(SystemExit):
        cli(["--help"])


def test_codexml_cli_skips_eval(monkeypatch):
    called = {"eval": False}

    def fake_eval(*args, **kwargs):
        called["eval"] = True

    monkeypatch.setattr("codex_ml.cli.main.run_training", lambda cfg: None)
    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    with pytest.raises(SystemExit):
        cli(["eval=null"])

    assert called["eval"] is False
