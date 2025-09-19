import importlib
import sys

import pytest

pytest.importorskip("numpy")
pytest.importorskip("accelerate")


def test_accelerate_shim_prints_path(capsys, monkeypatch):
    # Force a fresh import so the shim installs
    monkeypatch.delitem(sys.modules, "training.engine_hf_trainer", raising=False)
    eng = importlib.import_module("training.engine_hf_trainer")
    import accelerate
    from accelerate import Accelerator  # noqa: F401

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


def test_accelerate_shim_handles_new_kwargs_on_legacy(capsys, monkeypatch):
    import accelerate

    accelerate = importlib.reload(accelerate)

    # Simulate legacy accelerate by removing DataLoaderConfiguration and patching __init__
    monkeypatch.delattr(accelerate.utils, "DataLoaderConfiguration", raising=False)

    def legacy_init(self, *args, **kwargs):
        self.kwargs = kwargs

    monkeypatch.setattr(accelerate.Accelerator, "__init__", legacy_init, raising=True)
    monkeypatch.delitem(sys.modules, "training.engine_hf_trainer", raising=False)
    eng = importlib.import_module("training.engine_hf_trainer")

    class DummyDLC:
        dispatch_batches = True
        split_batches = False
        even_batches = True

    acc = eng._make_accelerator(project_dir="/tmp/logs", dataloader_config=DummyDLC())
    out = capsys.readouterr().out
    assert "mapped project_dir -> logging_dir" in out
    assert "translated dataloader_config -> legacy kwargs" in out
    assert "v<0.30: using legacy kwargs path" in out
    assert acc.kwargs["logging_dir"] == "/tmp/logs"
    assert acc.kwargs["dispatch_batches"] is True
    assert acc.kwargs["split_batches"] is False
    assert acc.kwargs["even_batches"] is True
    assert "project_dir" not in acc.kwargs
    assert "dataloader_config" not in acc.kwargs
