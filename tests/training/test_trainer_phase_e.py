import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def _import_trainer():
    return importlib.import_module("training.trainer")


# ---------------------------------------------------------------------------
# Trainer._should_replace logic
# ---------------------------------------------------------------------------


class TestShouldReplace:
    """Test the _should_replace method indirectly via patching."""

    def setup_method(self):
        self.mod = _import_trainer()

    def _make_trainer_with_checkpoint(self, tmp_path, mode: str):
        """Build a partial Trainer state via direct attribute manipulation."""
        cfg = self.mod.TrainerConfig(epochs=1)
        cc = self.mod.CheckpointConfig(directory=str(tmp_path), mode=mode)
        cfg.checkpoint = cc
        state = self.mod.TrainingState(best_metric=0.5)

        # Build a minimal stand-in without full __init__
        trainer = object.__new__(self.mod.Trainer)
        trainer.config = cfg
        trainer.state = state
        return trainer

    def test_should_replace_min_lower_value(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "min")
            assert trainer._should_replace(0.3) is True, "Condition must be true"

    def test_should_replace_min_higher_value(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "min")
            assert trainer._should_replace(0.8) is False, "Condition must be true"

    def test_should_replace_max_higher_value(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "max")
            assert trainer._should_replace(0.9) is True, "Condition must be true"

    def test_should_replace_none_best_metric(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "min")
            trainer.state.best_metric = None
            assert trainer._should_replace(0.5) is True, "Condition must be true"

    def test_should_replace_no_checkpoint_config(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "min")
            trainer.config.checkpoint = None
            assert trainer._should_replace(0.1) is False, "Condition must be true"


class _TensorStub:
    """Tiny tensor-like test helper for torch-free Trainer branch testing."""

    def __init__(self, value=None):
        self.value = value
        self.last_device = None

    def to(self, device):
        self.last_device = device
        return self

    def detach(self):
        return self

    def cpu(self):
        return self

    def item(self):
        return float(self.value if self.value is not None else 0.0)


class TestTrainerTorchFreeBranches:
    def setup_method(self):
        self.mod = _import_trainer()

    def _build_partial_trainer(self, tmp_path, *, checkpoint: bool = True):
        trainer = object.__new__(self.mod.Trainer)
        cfg = self.mod.TrainerConfig(epochs=1)
        if checkpoint:
            cfg.checkpoint = self.mod.CheckpointConfig(directory=str(tmp_path), mode="min")
        trainer.config = cfg
        trainer.state = self.mod.TrainingState(epoch=0, global_step=0, best_metric=0.5)
        trainer._checkpoints = []
        trainer._resume_metadata = None
        trainer._logging_session = MagicMock()
        trainer._metrics_path = None

        trainer.simple = MagicMock()
        trainer.simple.device = "cpu"
        trainer.simple.model = MagicMock()
        trainer.simple.optimizer = MagicMock()
        return trainer

    def test_prepare_batch_mapping_and_tuple_variants(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=False)
        input_ids = _TensorStub(1)
        labels = _TensorStub(2)
        inputs, labels_out = trainer._prepare_batch({"input_ids": input_ids, "labels": labels})
        assert inputs["input_ids"] is input_ids, "Condition must be true"
        assert labels_out is labels, "labels_out is not valid"
        assert input_ids.last_device == "cpu", "last_device is not valid"
        assert labels.last_device == "cpu", "last_device is not valid"

        inputs2, labels2 = trainer._prepare_batch((_TensorStub(3), _TensorStub(4)))
        assert isinstance(inputs2, _TensorStub)
        assert isinstance(labels2, _TensorStub)

    def test_prepare_batch_invalid_inputs_raise(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=False)
        with pytest.raises(ValueError, match="must include a 'labels' tensor"):
            trainer._prepare_batch({"input_ids": _TensorStub(1)})
        with pytest.raises(TypeError, match="Unsupported batch type"):
            trainer._prepare_batch(("only_one",))

    def test_zero_grad_typeerror_fallback(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=False)
        trainer.simple.optimizer.zero_grad.side_effect = [TypeError("unsupported"), None]
        trainer._zero_grad()
        assert trainer.simple.optimizer.zero_grad.call_count == 2, "Count must be greater than zero"

    def test_monitor_value_and_latest_checkpoint_path(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        trainer.config.checkpoint.monitor = "score"
        assert trainer._monitor_value({"val_loss": 1.0, "score": 0.3}) == 0.3

        ckpt_old = tmp_path / "epoch1-metric0.90.pt"
        ckpt_new = tmp_path / "epoch2-metric0.80.pt"
        ckpt_old.write_text("old", encoding="utf-8")
        ckpt_new.write_text("new", encoding="utf-8")
        assert trainer._latest_checkpoint_path(tmp_path) == ckpt_new, "Condition must be true"

    def test_checkpoint_discovery_hydration_and_prune(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        trainer.config.checkpoint.best_k = 1

        (tmp_path / "epoch_1.pt").write_text("ckpt-1", encoding="utf-8")
        (tmp_path / "epoch_2.pt").write_text("ckpt-2", encoding="utf-8")
        (tmp_path / "epoch_1.json").write_text(
            '{"epoch": 1, "monitor": 0.9}',
            encoding="utf-8",
        )
        (tmp_path / "epoch_2.json").write_text(
            '{"epoch": 2, "monitor": 0.4}',
            encoding="utf-8",
        )

        trainer._hydrate_existing_checkpoints(tmp_path)
        assert trainer.state.best_metric == 0.4, "best_metric is not valid"
        assert len(trainer._checkpoints) == 2, "Collection must not be empty"

        trainer._prune_checkpoints()
        assert len(trainer._checkpoints) == 1, "Collection must not be empty"
        assert (tmp_path / "epoch_2.pt").exists(), "Condition must be true"
        assert not (tmp_path / "epoch_1.pt").exists(), "Condition must be true"

    def test_find_latest_checkpoint_prefers_latest_pointer(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        (tmp_path / "epoch_2.pt").write_text("ckpt", encoding="utf-8")
        (tmp_path / "latest.json").write_text(
            '{"path": "epoch_2.pt", "epoch": 2, "global_step": 5, "monitor": 0.2}',
            encoding="utf-8",
        )
        latest = trainer._find_latest_checkpoint(tmp_path)
        assert latest is not None, "latest must be initialized"
        assert latest[0].name == "epoch_2.pt", "name is not valid"
        assert latest[1]["epoch"] == 2, "Condition must be true"

    def test_load_checkpoint_applies_model_and_state(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        payload = {
            "model_state": {"weight": 1},
            "optimizer_state": {"lr": 0.001},
            "epoch": "4",
            "global_step": "17",
            "monitor": "0.12",
        }
        with patch.object(self.mod, "_load_checkpoint_payload", return_value=payload):
            trainer._load_checkpoint(tmp_path / "epoch_4.pt", pointer={})
        trainer.simple.model.load_state_dict.assert_called_once_with({"weight": 1})
        trainer.simple.optimizer.load_state_dict.assert_called_once_with({"lr": 0.001})
        assert trainer.state.epoch == 4, "epoch is not valid"
        assert trainer.state.global_step == 17, "global_step is not valid"
        assert trainer.state.best_metric == pytest.approx(0.12), "best_metric is not valid"

    def test_resume_from_latest_checkpoint_handles_failure(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        with patch.object(trainer, "_latest_checkpoint_path", return_value=tmp_path / "missing.pt"):
            with patch.object(self.mod, "load_checkpoint", side_effect=RuntimeError("bad")):
                trainer._resume_from_latest_checkpoint(trainer.config.checkpoint)
        assert trainer.state.epoch == 0, "epoch is not valid"

    def test_save_checkpoint_guard_and_init_stub_checkpoint_guard(self, tmp_path, monkeypatch):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        trainer._save_checkpoint(epoch=1, metrics={"val_metric": 0.9})
        assert not (tmp_path / "epoch_1.pt").exists(), "Condition must be true"

        if self.mod._HAS_REAL_TORCH:
            pytest.skip("Guard branch only relevant without real torch")
        monkeypatch.setenv("CODEX_ALLOW_TORCH_STUB", "1")
        cfg = self.mod.TrainerConfig(
            epochs=1,
            checkpoint=self.mod.CheckpointConfig(directory=str(tmp_path)),
        )
        with pytest.raises(RuntimeError, match="Checkpointing requires a real torch installation"):
            self.mod.Trainer(MagicMock(), MagicMock(), MagicMock(), config=cfg)

    def test_load_checkpoint_payload_typeerror_retry(self, tmp_path):
        fn = self.mod._load_checkpoint_payload
        calls = {"count": 0}

        def flaky_load(_path, **kwargs):
            calls["count"] += 1
            if calls["count"] == 1 and "weights_only" in kwargs:
                raise TypeError("weights_only unexpected")
            return {"ok": True}

        with (
            patch.object(self.mod, "_TORCH_LOAD_FN", flaky_load),
            patch.object(self.mod, "_TORCH_SUPPORTS_WEIGHTS_ONLY", True),
        ):
            result = fn(tmp_path / "ckpt.pt", map_location="cpu")
        assert result == {"ok": True}, "Result must not be empty"
        assert calls["count"] == 2, "Count must be greater than zero"
