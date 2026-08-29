"""
Test Codexml Cli

Test module for codexml cli.
"""

import sys

import pytest

pytest.importorskip("hydra")
pytest.importorskip("datasets")

from codex_ml.cli.main import cli


def test_codexml_cli_help():
    assert cli(["--help"]) == 0, "Condition must be true"


def test_codexml_cli_skips_eval(monkeypatch):
    _cli_main = sys.modules.get("codex_ml.cli.main")
    if _cli_main is None:
        pytest.skip("codex_ml.cli.main not loaded")

    # This test exercises the Hydra-backed CLI path.  When typer is installed,
    # `cli` is a Typer wrapper that does not accept bare Hydra overrides as
    # arguments, so the test cannot run in that environment.
    if hasattr(_cli_main, "_typer_cli_wrapper"):
        pytest.skip("test requires Hydra CLI path; typer CLI is active")

    try:
        from hydra.core.global_hydra import GlobalHydra  # hydra-core 1.2+
    except ImportError:
        from hydra._internal.hydra import GlobalHydra  # type: ignore[no-redef]  # older

    called = {"eval": False}

    def fake_eval(*args, **kwargs):
        called["eval"] = True

    monkeypatch.setattr("codex_ml.cli.main.run_training", lambda cfg, output_dir=None: None)
    monkeypatch.setattr("codex_ml.cli.main.evaluate_datasets", fake_eval)

    # Explicitly disable evaluation via config; CLI should exit cleanly and not call evaluate
    with pytest.raises(SystemExit) as excinfo:
        cli(["pipeline.steps=[evaluate]", "eval=null", "hydra.run.dir=."])
    assert excinfo.value.code == 0, "Value must be initialized"
    assert called["eval"] is False, "Condition must be true"

    GlobalHydra.instance().clear()

    with pytest.raises(SystemExit):
        cli(["eval=null"])
    assert called["eval"] is False, "Condition must be true"

    GlobalHydra.instance().clear()

    # With default config (no eval=null), the CLI should attempt evaluation
    with pytest.raises(SystemExit) as excinfo:
        cli(["hydra.run.dir=."])
    assert excinfo.value.code == 0, "Value must be initialized"
    assert called["eval"] is True, "Condition must be true"


def test_run_training_invokes_functional_entry(monkeypatch):
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
    assert "--val-texts" in captured["argv"], "Condition must be true"
    assert "training.epochs=2" in captured["argv"], "Condition must be true"
    assert "training.lr=1e-05" in captured["argv"], "Condition must be true"
    assert "training.lora.r=4" in captured["argv"], "Condition must be true"
    assert "training.lora.alpha=16" in captured["argv"], "Condition must be true"
    assert "training.lora.dropout=0.2" in captured["argv"], "Condition must be true"
