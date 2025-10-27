from __future__ import annotations

from pathlib import Path

from codex_ml.training.strategies import ContinualReplayStrategy, TrainingResult
from codex_ml.training.unified_training import UnifiedTrainingConfig


class _StubStrategy:
    backend_name = "stub"

    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def run(self, config, callbacks, resume_from=None):
        self.calls.append((config.output_dir, config.epochs))
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

    assert len(base.calls) == 2
    assert base.calls[0][0].endswith("phase-a")
    assert base.calls[1][1] == 2
    assert result.status == "ok"
    assert result.extra["phases"][0]["name"] == "phase-a"
    assert result.final_epoch == 3


def test_continual_replay_requires_schedule(tmp_path: Path) -> None:
    cfg = UnifiedTrainingConfig(output_dir=str(tmp_path))
    cfg.extra = {}
    strategy = ContinualReplayStrategy(base_strategy=_StubStrategy())
    try:
        strategy.run(cfg, callbacks=[], resume_from=None)
    except ValueError as exc:
        assert "continual schedule" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ValueError for missing continual schedule")
