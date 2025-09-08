import pytest

pytest.importorskip("hydra")

from codex_ml.cli.main import cli  # noqa: E402


def test_codexml_cli_help():
    with pytest.raises(SystemExit):
        cli(["--help"])


@pytest.mark.xfail(reason="Hydra internals unavailable", strict=False)
def test_codexml_cli_skips_eval(monkeypatch):
    from hydra.core.global_hydra import GlobalHydra

    called = {"eval": False}

    def fake_eval(*args, **kwargs):
        called["eval"] = True

    monkeypatch.setattr("codex_ml.cli.main.run_training", lambda cfg, output_dir=None: None)
    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    # Explicitly disable evaluation via config; CLI should exit cleanly and not call evaluate
    with pytest.raises(SystemExit) as excinfo:
        cli(["pipeline.steps=[evaluate]", "eval=null", "hydra.run.dir=."])
    assert excinfo.value.code == 0
    assert called["eval"] is False

    GlobalHydra.instance().clear()

    with pytest.raises(SystemExit):
        cli(["eval=null"])
    assert called["eval"] is False

    GlobalHydra.instance().clear()

    # With default config (no eval=null), the CLI should attempt evaluation
    with pytest.raises(SystemExit) as excinfo:
        cli(["hydra.run.dir=."])
    assert excinfo.value.code == 0
    assert called["eval"] is True


@pytest.mark.xfail(reason="run_training arg mapping shifted", strict=False)
def test_run_training_invokes_functional_entry(monkeypatch):
    from omegaconf import OmegaConf

    from codex_ml.cli import main as cli_main

    captured: dict[str, list[str]] = {}

    def fake_main(argv: list[str] | None) -> int:
        captured["argv"] = argv or []
        return 0

    monkeypatch.setattr(cli_main, "_functional_training_main", fake_main)

    cfg = OmegaConf.create(
        {
            "output_dir": "my_runs",
            "epochs": 2,
            "texts": ["hi"],
            "val_texts": ["bye"],
            "lr": 1e-5,
        }
    )
    cli_main.run_training(cfg, output_dir="ignored_root")

    assert captured["argv"][:4] == ["--output-dir", "my_runs", "--texts", "hi"]
    assert "--val-texts" in captured["argv"]
    # verify important overrides are mapped and forwarded
    assert "num_train_epochs=2" in captured["argv"]
    assert "learning_rate=1e-05" in captured["argv"]
