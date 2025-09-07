import pytest

pytest.importorskip("hydra")

from codex_ml.cli.main import cli  # noqa: E402


def test_codexml_cli_help():
    with pytest.raises(SystemExit):
        cli(["--help"])


def test_codexml_cli_skips_eval_when_missing(monkeypatch):
    called = False

    def fake_eval(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    with pytest.raises(SystemExit) as exc:
        cli(["pipeline.steps=[evaluate]", "eval=null"])

    assert exc.value.code == 0
    assert not called
