"""Phase E coverage expansion for src/training/trainer.py — torch-free paths."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


# ---------------------------------------------------------------------------
# Import guard helpers
# ---------------------------------------------------------------------------

def _import_trainer():
    import importlib
    # Use src.training.trainer to avoid the root-level training/ shadow package
    for mod_name in ("src.training.trainer", "training.trainer"):
        try:
            return importlib.import_module(mod_name)
        except (ImportError, ModuleNotFoundError):
            continue
    pytest.skip("training.trainer not importable")


# ---------------------------------------------------------------------------
# CheckpointConfig tests (no torch required)
# ---------------------------------------------------------------------------

class TestCheckpointConfig:
    def setup_method(self):
        self.mod = _import_trainer()
        self.CC = self.mod.CheckpointConfig

    def test_basic_construction(self, tmp_path):
        cfg = self.CC(directory=str(tmp_path))
        assert cfg.directory == str(tmp_path)
        assert cfg.best_k == 1
        assert cfg.monitor == "val_loss"
        assert cfg.mode == "min"
        assert cfg.save_optimizer is True

    def test_mode_max(self, tmp_path):
        cfg = self.CC(directory=str(tmp_path), mode="max")
        assert cfg.mode == "max"

    def test_mode_case_insensitive(self, tmp_path):
        cfg = self.CC(directory=str(tmp_path), mode="MIN")
        assert cfg.mode == "min"

    def test_invalid_mode_raises(self, tmp_path):
        with pytest.raises(ValueError, match="mode must be"):
            self.CC(directory=str(tmp_path), mode="invalid")

    def test_best_k_below_one_raises(self, tmp_path):
        with pytest.raises(ValueError, match="best_k must be >= 1"):
            self.CC(directory=str(tmp_path), best_k=0)

    def test_keep_best_k_overrides_best_k(self, tmp_path):
        cfg = self.CC(directory=str(tmp_path), keep_best_k=3)
        assert cfg.best_k == 3

    def test_conflicting_best_k_and_keep_best_k_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Conflicting best_k"):
            self.CC(directory=str(tmp_path), best_k=2, keep_best_k=5)

    def test_maximize_metric_sets_mode_max(self, tmp_path):
        cfg = self.CC(directory=str(tmp_path), maximize_metric=True)
        assert cfg.mode == "max"

    def test_maximize_metric_false_sets_mode_min(self, tmp_path):
        cfg = self.CC(directory=str(tmp_path), maximize_metric=False)
        assert cfg.mode == "min"

    def test_conflicting_mode_and_maximize_metric_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Conflicting mode"):
            self.CC(directory=str(tmp_path), mode="min", maximize_metric=True)

    def test_path_for_epoch(self, tmp_path):
        cfg = self.CC(directory=str(tmp_path))
        p = cfg.path_for_epoch(3)
        assert p == Path(str(tmp_path)) / "epoch_3.pt"

    def test_save_optimizer_false(self, tmp_path):
        cfg = self.CC(directory=str(tmp_path), save_optimizer=False)
        assert cfg.save_optimizer is False


# ---------------------------------------------------------------------------
# TrainerConfig tests (no torch required)
# ---------------------------------------------------------------------------

class TestTrainerConfig:
    def setup_method(self):
        self.mod = _import_trainer()
        self.TC = self.mod.TrainerConfig

    def test_default_construction(self):
        cfg = self.TC()
        assert cfg.epochs == 1
        assert cfg.gradient_accumulation_steps == 1
        assert cfg.mixed_precision is False
        assert cfg.max_grad_norm is None
        assert cfg.log_every_n_steps == 0
        assert cfg.checkpoint is None
        assert cfg.seed is None
        assert cfg.metrics_ndjson_path is None

    def test_custom_values(self):
        cfg = self.TC(
            epochs=5,
            gradient_accumulation_steps=4,
            mixed_precision=True,
            max_grad_norm=1.0,
        )
        assert cfg.epochs == 5
        assert cfg.gradient_accumulation_steps == 4
        assert cfg.mixed_precision is True
        assert cfg.max_grad_norm == 1.0


# ---------------------------------------------------------------------------
# TrainingState tests (no torch required)
# ---------------------------------------------------------------------------

class TestTrainingState:
    def setup_method(self):
        self.mod = _import_trainer()
        self.TS = self.mod.TrainingState

    def test_default_construction(self):
        state = self.TS()
        assert state.epoch == 0
        assert state.global_step == 0
        assert state.best_metric is None

    def test_custom_state(self):
        state = self.TS(epoch=3, global_step=100, best_metric=0.5)
        assert state.epoch == 3
        assert state.global_step == 100
        assert state.best_metric == 0.5


# ---------------------------------------------------------------------------
# _load_checkpoint_payload tests (no real torch)
# ---------------------------------------------------------------------------

class TestLoadCheckpointPayload:
    def setup_method(self):
        self.mod = _import_trainer()

    def test_raises_when_no_torch_load_fn(self, tmp_path):
        """Should raise RuntimeError when _TORCH_LOAD_FN is None."""
        fn = self.mod._load_checkpoint_payload
        if self.mod._TORCH_LOAD_FN is not None:
            pytest.skip("Real torch available; stub path not exercised")
        with pytest.raises(RuntimeError, match="torch is required"):
            fn(tmp_path / "ckpt.pt", map_location=None)

    def test_with_mocked_torch_load(self, tmp_path):
        """Exercises the load path with a mocked torch.load function."""
        fn = self.mod._load_checkpoint_payload
        fake_payload = {"epoch": 1, "loss": 0.3}
        with (
            patch.object(self.mod, "_TORCH_LOAD_FN", return_value=fake_payload),
            patch.object(self.mod, "_TORCH_SUPPORTS_WEIGHTS_ONLY", False),
        ):
            result = fn(tmp_path / "ckpt.pt", map_location="cpu")
        assert result == fake_payload

    def test_returns_empty_dict_for_non_mapping(self, tmp_path):
        """Non-Mapping payloads from torch.load return {}."""
        fn = self.mod._load_checkpoint_payload
        with (
            patch.object(self.mod, "_TORCH_LOAD_FN", return_value=[1, 2, 3]),
            patch.object(self.mod, "_TORCH_SUPPORTS_WEIGHTS_ONLY", False),
        ):
            result = fn(tmp_path / "ckpt.pt", map_location=None)
        assert result == {}

    def test_weights_only_kwarg_forwarded(self, tmp_path):
        """weights_only=False forwarded when _TORCH_SUPPORTS_WEIGHTS_ONLY is True."""
        fn = self.mod._load_checkpoint_payload
        called_kwargs: dict = {}

        def fake_load(path, **kwargs):
            called_kwargs.update(kwargs)
            return {"ok": True}

        with (
            patch.object(self.mod, "_TORCH_LOAD_FN", fake_load),
            patch.object(self.mod, "_TORCH_SUPPORTS_WEIGHTS_ONLY", True),
        ):
            fn(tmp_path / "ckpt.pt", map_location="cpu")
        assert called_kwargs.get("weights_only") is False


# ---------------------------------------------------------------------------
# Trainer instantiation guard (CODEX_ALLOW_TORCH_STUB)
# ---------------------------------------------------------------------------

class TestTrainerInstantiationGuard:
    def setup_method(self):
        self.mod = _import_trainer()

    def test_raises_without_real_torch_and_env_unset(self):
        if self.mod._HAS_REAL_TORCH:
            pytest.skip("Real torch present; stub guard not active")
        dummy = MagicMock()
        with pytest.raises(RuntimeError, match="Trainer requires a real torch"):
            self.mod.Trainer(dummy, dummy, dummy)

    def test_stub_mode_env_skip_init(self, monkeypatch):
        """CODEX_ALLOW_TORCH_STUB=1 must bypass the real-torch guard."""
        if self.mod._HAS_REAL_TORCH:
            pytest.skip("Real torch present; not testing stub mode")
        monkeypatch.setenv("CODEX_ALLOW_TORCH_STUB", "1")
        # Re-import to pick up patched env
        import importlib
        fresh = importlib.reload(self.mod)
        dummy = MagicMock()
        # Should NOT raise the "requires real torch" error; may raise other errors
        try:
            fresh.Trainer(dummy, dummy, dummy)
        except RuntimeError as exc:
            # Only allow errors unrelated to the torch guard
            assert "requires a real torch" not in str(exc), (
                "Trainer should not raise torch-guard error with CODEX_ALLOW_TORCH_STUB=1"
            )
        except Exception as _err:
            pass  # Other errors from incomplete mock setup are acceptable


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
            assert trainer._should_replace(0.3) is True

    def test_should_replace_min_higher_value(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "min")
            assert trainer._should_replace(0.8) is False

    def test_should_replace_max_higher_value(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "max")
            assert trainer._should_replace(0.9) is True

    def test_should_replace_none_best_metric(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "min")
            trainer.state.best_metric = None
            assert trainer._should_replace(0.5) is True

    def test_should_replace_no_checkpoint_config(self, tmp_path):
        if not self.mod._HAS_REAL_TORCH:
            trainer = self._make_trainer_with_checkpoint(tmp_path, "min")
            trainer.config.checkpoint = None
            assert trainer._should_replace(0.1) is False


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
        assert inputs["input_ids"] is input_ids
        assert labels_out is labels
        assert input_ids.last_device == "cpu"
        assert labels.last_device == "cpu"

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
        assert trainer.simple.optimizer.zero_grad.call_count == 2

    def test_monitor_value_and_latest_checkpoint_path(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        trainer.config.checkpoint.monitor = "score"
        assert trainer._monitor_value({"val_loss": 1.0, "score": 0.3}) == 0.3

        ckpt_old = tmp_path / "epoch1-metric0.90.pt"
        ckpt_new = tmp_path / "epoch2-metric0.80.pt"
        ckpt_old.write_text("old", encoding="utf-8")
        ckpt_new.write_text("new", encoding="utf-8")
        assert trainer._latest_checkpoint_path(tmp_path) == ckpt_new

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
        assert trainer.state.best_metric == 0.4
        assert len(trainer._checkpoints) == 2

        trainer._prune_checkpoints()
        assert len(trainer._checkpoints) == 1
        assert (tmp_path / "epoch_2.pt").exists()
        assert not (tmp_path / "epoch_1.pt").exists()

    def test_find_latest_checkpoint_prefers_latest_pointer(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        (tmp_path / "epoch_2.pt").write_text("ckpt", encoding="utf-8")
        (tmp_path / "latest.json").write_text(
            '{"path": "epoch_2.pt", "epoch": 2, "global_step": 5, "monitor": 0.2}',
            encoding="utf-8",
        )
        latest = trainer._find_latest_checkpoint(tmp_path)
        assert latest is not None
        assert latest[0].name == "epoch_2.pt"
        assert latest[1]["epoch"] == 2

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
        assert trainer.state.epoch == 4
        assert trainer.state.global_step == 17
        assert trainer.state.best_metric == pytest.approx(0.12)

    def test_resume_from_latest_checkpoint_handles_failure(self, tmp_path):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        with patch.object(trainer, "_latest_checkpoint_path", return_value=tmp_path / "missing.pt"):
            with patch.object(self.mod, "load_checkpoint", side_effect=RuntimeError("bad")):
                trainer._resume_from_latest_checkpoint(trainer.config.checkpoint)
        assert trainer.state.epoch == 0

    def test_save_checkpoint_guard_and_init_stub_checkpoint_guard(self, tmp_path, monkeypatch):
        trainer = self._build_partial_trainer(tmp_path, checkpoint=True)
        trainer._save_checkpoint(epoch=1, metrics={"val_metric": 0.9})
        assert not (tmp_path / "epoch_1.pt").exists()

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
        assert result == {"ok": True}
        assert calls["count"] == 2
