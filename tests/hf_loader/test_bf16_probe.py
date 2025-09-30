import importlib
import pytest


@pytest.mark.skipif(pytest.importorskip("torch", reason="torch not installed") is None, reason="torch missing")
def test_bf16_capability_probe():
    import torch  # type: ignore

    if not hasattr(torch, "bfloat16") or getattr(torch, "bfloat16") is None:
        pytest.skip("bf16 not supported by this torch build")

    # train_loop dtype resolver should map 'bf16' to torch.bfloat16
    tl = importlib.import_module("src.codex_ml.train_loop")
    resolve_dtype = getattr(tl, "_resolve_dtype")
    assert resolve_dtype("bf16") == torch.bfloat16

    # hf_loader AMP dtype mapper should map 'bf16' to torch.bfloat16
    hf = importlib.import_module("src.codex_ml.hf_loader")
    map_amp = getattr(hf, "_map_amp_dtype")
    assert map_amp("bf16") == torch.bfloat16

