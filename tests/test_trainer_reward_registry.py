from __future__ import annotations

import pytest

from codex_ml.plugins.registries import reward_models, trainers


def test_offline_functional_trainer_callable():
    pytest.importorskip("numpy")
    pytest.importorskip("torch")
    trainer = trainers.resolve_and_instantiate("offline:functional")
    assert callable(trainer)


def test_offline_heuristic_reward_model_scores():
    reward_model = reward_models.resolve_and_instantiate("offline:heuristic")
    score = reward_model.evaluate("Explain steps", "Please explain the steps with an example")
    assert isinstance(score, float)
    summary = reward_model.learn(
        [
            {"prompt": "Prompt", "completion": "Give an example", "label": 1.0},
        ]
    )
    assert summary["samples"] == 1


def test_plugins_cli_lists_trainer_and_reward_entries():
    pytest.importorskip("typer")
    from typer.testing import CliRunner

    from codex_ml.cli import plugins_cli

    runner = CliRunner()
    trainers_result = runner.invoke(plugins_cli.app, ["list", "trainers"])
    assert trainers_result.exit_code == 0
    assert "offline:functional" in trainers_result.stdout

    reward_result = runner.invoke(plugins_cli.app, ["list", "reward_models"])
    assert reward_result.exit_code == 0
    assert "offline:heuristic" in reward_result.stdout
