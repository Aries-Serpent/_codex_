# BEGIN: CODEX_DATA_SHARD
from __future__ import annotations

def shard_range(rank: int, world: int, n: int) -> tuple[int,int]:
    assert 0 <= rank < world and n >= 0
    base, rem = divmod(n, world)
    start = rank * base + min(rank, rem)
    end = start + base + (1 if rank < rem else 0)
    return start, end
# END: CODEX_DATA_SHARD
