import importlib


def test_resolve_dtype_and_device_no_crash():
    mod = importlib.import_module("src.codex_ml.train_loop")
    resolve_dtype = getattr(mod, "_resolve_dtype")
    resolve_device = getattr(mod, "_resolve_device")

    # dtype resolution should tolerate missing torch and unknown values
    assert resolve_dtype(None) is None
    assert resolve_dtype("unknown") is None
    out_f32 = resolve_dtype("f32")
    out_bf16 = resolve_dtype("bf16")
    out_fp16 = resolve_dtype("fp16")

    try:
        import torch  # type: ignore

        assert out_f32 in (None, torch.float32)
        # bf16 may be None on older Torch builds; allow None
        assert out_bf16 in (None, getattr(torch, "bfloat16", None))
        assert out_fp16 in (None, torch.float16)
    except Exception:
        assert out_f32 is None and out_bf16 is None and out_fp16 is None

    # device resolution returns a device or "cpu" string fallback when torch missing
    dev = resolve_device(None)
    # Accept either torch.device or "cpu"
    try:
        import torch  # type: ignore

        assert isinstance(dev, torch.device) or str(dev) == "cpu"
    except Exception:
        assert dev == "cpu"

