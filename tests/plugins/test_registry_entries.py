from __future__ import annotations

from pathlib import Path

import pytest

from codex_ml.plugins import registries


def test_offline_tokenizer_instantiates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEX_ML_TINY_TOKENIZER_PATH", raising=False)
    tokenizer = registries.tokenizers.resolve_and_instantiate("offline:tiny-vocab")
    assert tokenizer.encode("hello offline world") == [2, 3, 4]
    assert tokenizer.decode([2, 3, 4]) == "hello offline world"


def test_offline_tokenizer_missing_asset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CODEX_ML_TINY_TOKENIZER_PATH", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError) as excinfo:
        registries.tokenizers.resolve_and_instantiate("offline:tiny-vocab")
    message = str(excinfo.value)
    assert "CODEX_ML_TINY_TOKENIZER_PATH" in message


def test_offline_model_instantiates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEX_ML_TINY_SEQUENCE_PATH", raising=False)
    model = registries.models.resolve_and_instantiate("offline:tiny-sequence")
    assert model.generate("hello there") == "offline world"
    assert model.generate("something else") == "tiny offline model"


def test_offline_model_missing_asset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CODEX_ML_TINY_SEQUENCE_PATH", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError) as excinfo:
        registries.models.resolve_and_instantiate("offline:tiny-sequence")
    assert "CODEX_ML_TINY_SEQUENCE_PATH" in str(excinfo.value)


def test_offline_dataset_instantiates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEX_ML_TINY_CORPUS_PATH", raising=False)
    dataset = registries.datasets.resolve_and_instantiate("offline:tiny-corpus")
    assert isinstance(dataset, list)
    assert dataset


def test_offline_dataset_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError) as excinfo:
        registries.datasets.resolve_and_instantiate(
            "offline:tiny-corpus", path=tmp_path / "missing.txt"
        )
    assert "offline:tiny-corpus" in str(excinfo.value)


def test_offline_metric_instantiates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEX_ML_WEIGHTED_ACCURACY_PATH", raising=False)
    metric = registries.metrics.resolve_and_instantiate("offline:weighted-accuracy")
    score = metric(["a", "b", "c"], ["a", "x", "c"])
    assert 0.0 <= score <= 1.0


def test_offline_metric_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError) as excinfo:
        registries.metrics.resolve_and_instantiate(
            "offline:weighted-accuracy", weights_path=tmp_path / "missing.json"
        )
    assert "offline:weighted-accuracy" in str(excinfo.value)


def test_offline_trainer_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("numpy")
    monkeypatch.delenv("CODEX_ML_FUNCTIONAL_TRAINER_CONFIG", raising=False)
    trainer = registries.trainers.resolve_and_instantiate("offline:functional")
    defaults = getattr(trainer, "__codex_defaults__", {})
    assert defaults["learning_rate"] == pytest.approx(0.001)
    assert defaults["max_steps"] == 3


def test_offline_trainer_missing_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pytest.importorskip("numpy")
    monkeypatch.setenv("CODEX_ML_FUNCTIONAL_TRAINER_CONFIG", str(tmp_path / "missing.json"))
    with pytest.raises(FileNotFoundError) as excinfo:
        registries.trainers.resolve_and_instantiate("offline:functional")
    assert "offline:functional" in str(excinfo.value)


def test_offline_reward_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEX_ML_LENGTH_REWARD_PATH", raising=False)
    reward_model = registries.reward_models.resolve_and_instantiate("offline:length")
    assert reward_model.evaluate("prompt", "abcd") == pytest.approx(2.0)


def test_offline_reward_model_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError) as excinfo:
        registries.reward_models.resolve_and_instantiate(
            "offline:length", config_path=tmp_path / "missing.json"
        )
    assert "offline:length" in str(excinfo.value)


def test_offline_rl_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEX_ML_SCRIPTED_AGENT_PATH", raising=False)
    agent = registries.rl_agents.resolve_and_instantiate("offline:scripted")
    actions = [agent.act(None) for _ in range(5)]
    assert actions[:4] == [1, 0, 1, 1]
    assert actions[4] == 1  # loops back to the start


def test_offline_rl_agent_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError) as excinfo:
        registries.rl_agents.resolve_and_instantiate(
            "offline:scripted", policy_path=tmp_path / "missing.json"
        )
    assert "offline:scripted" in str(excinfo.value)
