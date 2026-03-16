"""
Test Codexml Cli

Test module for codexml cli.
"""

import pytest

pytest.importorskip("hydra")
pytest.importorskip("datasets")

from codex_ml.cli.main import cli  # noqa: E402


def test_codexml_cli_help():
    with pytest.raises(SystemExit):
        cli(["--help"])


def test_codexml_cli_skips_eval(monkeypatch):
    from hydra._internal.hydra import GlobalHydra

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


def test_run_training_invokes_functional_entry(monkeypatch):
    import sys
    cli_main = sys.modules.get("codex_ml.cli.main")
    if cli_main is None:
        pytest.skip("codex_ml.cli.main not loaded")
    from omegaconf import OmegaConf

    # The functional training path only exists in the non-typer branch.
    # When typer is available, run_training is a no-op stub that doesn't
    # call _functional_training_main, so this test is not applicable.
    if not hasattr(cli_main, "_functional_training_main"):
        pytest.skip("functional training path only available when typer is absent")

    captured: dict[str, list[str]] = {}

    def fake_main(argv: list[str] | None) -> int:
        captured["argv"] = argv or []
        return 0

    # Monkeypatch the cached module-level variable that _load_functional_training_main uses
    # First, ensure the global is initialized so monkeypatch can set it
    cli_main._functional_training_main = fake_main
    monkeypatch.setattr(cli_main, "_functional_training_main", fake_main)

    cfg = OmegaConf.create(
        {
            "output_dir": "my_runs",
            "epochs": 2,
            "texts": ["hi"],
            "val_texts": ["bye"],
            "lr": 1e-5,
            "lora": {"r": 4, "alpha": 16, "dropout": 0.2},
        }
    )
    cli_main.run_training(cfg, output_dir="ignored_root")

    assert captured["argv"][:4] == ["--output-dir", "my_runs", "--texts", "hi"]
    assert "--val-texts" in captured["argv"]
    assert "training.epochs=2" in captured["argv"]
    assert "training.lr=1e-05" in captured["argv"]
    assert "training.lora.r=4" in captured["argv"]
    assert "training.lora.alpha=16" in captured["argv"]
    assert "training.lora.dropout=0.2" in captured["argv"]
