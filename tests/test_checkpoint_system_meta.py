import json
from codex_ml.utils.checkpointing import CheckpointManager


def test_checkpoint_writes_system_meta(tmp_path):
    mgr = CheckpointManager(tmp_path)
    mgr.save(0)
    path = tmp_path / "epoch-0" / "system.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert isinstance(data, dict)
