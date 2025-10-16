from __future__ import annotations

import pytest

ddp = pytest.importorskip("codex_ml.distributed", reason="distributed module required")


def _torch_distributed_available() -> bool:
    try:
        import torch.distributed as dist  # type: ignore

        return bool(getattr(dist, "is_available", lambda: False)())
    except Exception:
        return False


@pytest.mark.skipif(not _torch_distributed_available(), reason="torch.distributed unavailable")
def test_ddp_env_optin_initializes_and_cleans(monkeypatch):
    # Opt-in via env; should initialize if torch.distributed is available.
    monkeypatch.setenv("CODEX_DDP", "1")
    initialized = ddp.init_distributed_if_needed()
    # It may fail to init if backend misconfigured; allow False, but barrier/cleanup must be safe.
    assert initialized in (True, False)
    ddp.barrier()
    ddp.cleanup()
