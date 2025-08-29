import pytest

from codex_ml.utils import checkpointing as ckpt


class DummyModel:
    def state_dict(self):  # pragma: no cover - trivial
        return {"w": 1}

    def load_state_dict(self, sd):  # pragma: no cover - trivial
        return sd


def dummy_model():
    return DummyModel()


def test_save_and_resume_with_pickle(tmp_path, monkeypatch):
    monkeypatch.setattr(ckpt, "TORCH_AVAILABLE", False)
    m = dummy_model()
    mgr = ckpt.CheckpointManager(tmp_path)
    mgr.save(1, model=m)
    out = mgr.resume_from(tmp_path / "epoch-1")
    assert out["meta"]["epoch"] == 1


def test_resume_missing_path_raises(tmp_path):
    mgr = ckpt.CheckpointManager(tmp_path)
    with pytest.raises(FileNotFoundError):
        mgr.resume_from(tmp_path / "missing")
