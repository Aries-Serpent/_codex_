from __future__ import annotations

from codex_ml.distributed import (
    barrier,
    cleanup,
    get_rank,
    get_world_size,
    init_distributed_if_needed,
    is_distributed_available,
)


def test_minimal_distributed_noop_paths(monkeypatch):
    monkeypatch.delenv("CODEX_DDP", raising=False)
    _ = is_distributed_available()
    assert init_distributed_if_needed() is False
    assert get_rank() == 0
    assert get_world_size() == 1
    barrier()
    cleanup()
