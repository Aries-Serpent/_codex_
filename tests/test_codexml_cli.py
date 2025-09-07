import pytest

pytest.importorskip("hydra")

from codex_ml.cli.main import cli  # noqa: E402


def test_codexml_cli_help():
    with pytest.raises(SystemExit):
        cli(["--help"])


def test_codexml_cli_skips_evaluation_when_eval_missing(monkeypatch):
    called = False

    def fake_eval(*args, **kwargs):  # pragma: no cover - stub
        nonlocal called
        called = True

    # Patch the evaluation entrypoint used by the CLI
    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    # Explicitly disable evaluation via config; CLI should exit cleanly and not call evaluate
    with pytest.raises(SystemExit) as excinfo:
        cli(["pipeline.steps=[evaluate]", "eval=null", "hydra.run.dir=."])
    assert excinfo.value.code == 0
    assert called is False


def test_codexml_cli_runs_evaluation_by_default(monkeypatch):
    called = False

    def fake_eval(*args, **kwargs):  # pragma: no cover - stub
        nonlocal called
        called = True

    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    # With default config (no eval=null), the CLI should attempt evaluation
    with pytest.raises(SystemExit) as excinfo:
        cli(["hydra.run.dir=."])
    assert excinfo.value.code == 0
    assert called is True
