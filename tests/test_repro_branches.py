from __future__ import annotations

import torch

from codex_ml.utils.repro import set_reproducible


def test_set_reproducible_handles_failures(monkeypatch):
    def boom(*_, **__):
        raise RuntimeError("boom")

    monkeypatch.setattr(torch, "use_deterministic_algorithms", boom)

    class CudnnStub:
        def __setattr__(self, name, value):
            raise RuntimeError("boom")

    monkeypatch.setattr(torch, "backends", type("B", (), {"cudnn": CudnnStub()})())

    # Should swallow the internal errors and still set up determinism guards
    set_reproducible(123)
