import json

import torch

from codex_ml.utils.checkpointing import save_ckpt, verify_ckpt_integrity


def test_checksum_roundtrip(tmp_path):
    ckpt = tmp_path / "m.pt"
    save_ckpt({"w": torch.tensor([1.0])}, str(ckpt))
    verify_ckpt_integrity(str(ckpt))
    meta = json.loads((tmp_path / "checksums.json").read_text())
    assert meta["file"] == "m.pt" and len(meta["sha256"]) == 64
