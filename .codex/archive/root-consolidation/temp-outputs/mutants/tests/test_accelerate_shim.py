"""
Test Accelerate Shim

Test module for accelerate shim.
"""

import importlib
import sys
import tempfile

import pytest

pytest.importorskip("numpy")
pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("datasets")
pytest.importorskip("accelerate")
pytest.importorskip("yaml")


def test_accelerate_shim_prints_path(capsys, monkeypatch):
    # Force a fresh import so the shim installs
    monkeypatch.delitem(sys.modules, "training.engine_hf_trainer", raising=False)
    eng = importlib.import_module("training.engine_hf_trainer")
    import accelerate

    has_dlc = hasattr(getattr(accelerate, "utils", object()), "DataLoaderConfiguration")

    # Construct via our helper (same class as what Trainer will see)
    _ = eng._make_accelerator(
        dispatch_batches=True,
        split_batches=True,
        even_batches=True,
        logging_dir=os.path.join(tempfile.gettempdir(), "logs"),
    )
    out = capsys.readouterr().out

    if has_dlc:
        assert "v>=0.30: using DataLoaderConfiguration path" in out, "Value must be greater than zero"
        assert "mapped logging_dir -> project_dir" in out, "Condition must be true"
    else:
        assert "v<0.30: using legacy kwargs path" in out, "Condition must be true"


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

    acc = eng._make_accelerator(project_dir=os.path.join(tempfile.gettempdir(), "logs"), dataloader_config=DummyDLC())
    out = capsys.readouterr().out
    assert "mapped project_dir -> logging_dir" in out, "Condition must be true"
    assert "translated dataloader_config -> legacy kwargs" in out, "Data must not be empty"
    assert "v<0.30: using legacy kwargs path" in out, "Condition must be true"
    assert acc.kwargs["logging_dir"] == os.path.join(tempfile.gettempdir(), "logs"), "Condition must be true"
    assert acc.kwargs["dispatch_batches"] is True, "Condition must be true"
    assert acc.kwargs["split_batches"] is False, "Condition must be true"
    assert acc.kwargs["even_batches"] is True, "Condition must be true"
    assert "project_dir" not in acc.kwargs, "Condition must be true"
    assert "dataloader_config" not in acc.kwargs, "Data must not be empty"
