from pathlib import Path
from types import SimpleNamespace

from training.checkpoint_manager import CheckpointManager


class DummyModel:
    def save_pretrained(self, path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "model.bin").write_text("x", encoding="utf-8")


def test_checkpoint_callback(tmp_path):
    mgr = CheckpointManager(tmp_path, save_steps=1)
    cb = mgr.callback()
    state = SimpleNamespace(global_step=1)
    cb.on_step_end(None, state, None, model=DummyModel())
    assert (tmp_path / "step-1" / "model.bin").exists()
