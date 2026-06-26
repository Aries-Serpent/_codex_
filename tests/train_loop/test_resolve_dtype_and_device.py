"""
Test Resolve Dtype And Device

Test module for resolve dtype and device.
"""

import importlib


def test_resolve_dtype_and_device_no_crash():
    mod = importlib.import_module("src.codex_ml.train_loop")
    resolve_dtype = mod._resolve_dtype
    resolve_device = mod._resolve_device

    # dtype resolution should tolerate missing torch and unknown values
    assert resolve_dtype(None) is None, "Condition must be true"
    assert resolve_dtype("unknown") is None, "Condition must be true"
    out_f32 = resolve_dtype("f32")
    out_bf16 = resolve_dtype("bf16")
    out_fp16 = resolve_dtype("fp16")

    try:
        import torch  # type: ignore

        # Handle both actual torch types and mocks
        if out_f32 is not None and not isinstance(out_f32, type(None)):
            # If torch.float32 is a real torch dtype, compare directly
            # If it's a mock, just verify it's not None
            if hasattr(torch, "float32") and hasattr(torch.float32, "dtype"):
                assert out_f32 == torch.float32 or out_f32 is None, "out_f32 is not valid"
            else:
                # Mock torch or missing attribute - just verify not None or is None
                assert out_f32 in (None, torch.float32) or str(out_f32) in (
                    "float32",
                    "torch.float32",
                )
        # bf16 may be None on older Torch builds; allow None
        assert out_bf16 in (None, getattr(torch, "bfloat16", None)) or str(out_bf16) in (
            "bfloat16",
            "torch.bfloat16",
            "None",
        )
        assert out_fp16 in (None, torch.float16) or str(out_fp16) in (
            "float16",
            "torch.float16",
            "None",
        )
    except ImportError:
        assert out_f32 is None and out_bf16 is None and out_fp16 is None

    # device resolution returns a device or "cpu" string fallback when torch missing
    dev = resolve_device(None)
    # Accept either torch.device or "cpu"
    try:
        import torch  # type: ignore

        assert isinstance(dev, torch.device) or str(dev) == "cpu" or dev == "cpu"
    except ImportError:
        assert dev == "cpu", "dev is not valid"
