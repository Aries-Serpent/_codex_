import json
from pathlib import Path

import pytest

from codex_ml.utils.checkpointing import CheckpointManager


def test_checkpoint_checksum_verify(tmp_path: Path):
    cm = CheckpointManager(tmp_path)
    ckpt = cm.save(1, model=None)
    meta = json.loads((ckpt / "checksums.json").read_text())
    cm.resume_from(ckpt)
    state_file = ckpt / meta["file"]
    state_file.write_bytes(b"corrupt")
    with pytest.raises(RuntimeError):
        cm.resume_from(ckpt)
