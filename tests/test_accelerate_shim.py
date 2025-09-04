def test_accelerate_shim_prints_path(capsys, monkeypatch):
    # Force a fresh import so the shim installs
    import sys

    monkeypatch.delitem(sys.modules, "training.engine_hf_trainer", raising=False)
    import accelerate

    import training.engine_hf_trainer as eng

    has_dlc = hasattr(getattr(accelerate, "utils", object()), "DataLoaderConfiguration")

    # Construct via our helper (same class as what Trainer will see)
    _ = eng._make_accelerator(
        dispatch_batches=True,
        split_batches=True,
        even_batches=True,
        logging_dir="/tmp/logs",
    )
    out = capsys.readouterr().out

    if has_dlc:
        assert "v>=0.30: using DataLoaderConfiguration path" in out
        assert "mapped logging_dir -> project_dir" in out
    else:
        assert "v<0.30: using legacy kwargs path" in out
