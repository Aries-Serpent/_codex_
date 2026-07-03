import pytest

pytest.importorskip("mlflow")
"""
Test Training Continual Strategy

Test module for training continual strategy.
"""

from __future__ import annotations

from pathlib import Path

from codex_ml.training.strategies import ContinualReplayStrategy, TrainingResult
from codex_ml.training.unified_training import UnifiedTrainingConfig


class _StubStrategy:
    backend_name = "stub"

    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []
        self.configs = []

    def run(self, config, callbacks, resume_from=None):
        self.calls.append((config.output_dir, config.epochs))
        self.configs.append(config)
        return TrainingResult(
            status="ok",
            backend=self.backend_name,
            final_epoch=config.epochs,
            output_dir=config.output_dir,
            extra={"resume_from": resume_from},
        )


def test_continual_replay_invokes_base(tmp_path: Path) -> None:
    cfg = UnifiedTrainingConfig(output_dir=str(tmp_path))
    cfg.extra = {
        "continual": {
            "phases": [
                {"name": "phase-a", "epochs": 1, "train_texts": ["a"]},
                {
                    "name": "phase-b",
                    "epochs": 2,
                    "train_texts": ["b"],
                    "overrides": {"functional": {"grad_accum": 2}},
                },
            ]
        }
    }
    base = _StubStrategy()
    strategy = ContinualReplayStrategy(base_strategy=base)
    result = strategy.run(cfg, callbacks=[], resume_from=None)

    assert len(base.calls) == 2, "Collection must not be empty"
    assert base.calls[0][0].endswith("phase-a"), "Condition must be true"
    assert base.calls[1][1] == 2, "Condition must be true"
    assert result.status == "ok", "Result must not be empty"
    assert result.extra["phases"][0]["name"] == "phase-a", "Result must not be empty"
    assert result.final_epoch == 3, "Result must not be empty"


def test_continual_replay_requires_schedule(tmp_path: Path) -> None:
    cfg = UnifiedTrainingConfig(output_dir=str(tmp_path))
    cfg.extra = {}
    strategy = ContinualReplayStrategy(base_strategy=_StubStrategy())
    try:
        strategy.run(cfg, callbacks=[], resume_from=None)
    except ValueError as exc:
        message = str(exc)
        assert "continual" in message, "Condition must be true"
        assert "schedule" in message, "Condition must be true"
    else:  # pragma: no cover
        raise AssertionError("Expected ValueError for missing continual schedule")


def test_continual_dataset_materializes_texts(tmp_path: Path) -> None:
    warmup_path = tmp_path / "warmup.jsonl"
    warmup_path.write_text('{"text": "alpha"}\n{"text": "beta"}\n', encoding="utf-8")
    eval_path = tmp_path / "eval.jsonl"
    eval_path.write_text('{"text": "gamma"}\n', encoding="utf-8")

    cfg = UnifiedTrainingConfig(output_dir=str(tmp_path))
    cfg.seed = 7
    cfg.extra = {
        "continual": {
            "phases": [
                {
                    "name": "warmup",
                    "epochs": 1,
                    "dataset": {
                        "role": "train",
                        "path": str(warmup_path),
                        "format": "jsonl",
                        "val_fraction": 0.5,
                    },
                },
                {
                    "name": "evaluation",
                    "epochs": 1,
                    "dataset": {
                        "role": "eval",
                        "path": str(eval_path),
                        "format": "jsonl",
                    },
                },
            ]
        }
    }

    base = _StubStrategy()
    strategy = ContinualReplayStrategy(base_strategy=base)
    strategy.run(cfg, callbacks=[], resume_from=None)

    warmup_functional = base.configs[0].extra.get("functional", {})
    assert len(warmup_functional.get("train_texts", [])) == 1
    assert len(warmup_functional.get("val_texts", [])) == 1

    eval_functional = base.configs[1].extra.get("functional", {})
    assert eval_functional.get("val_texts") == ["gamma"], "Condition must be true"
    assert not eval_functional.get("train_texts"), "Condition must be true"
