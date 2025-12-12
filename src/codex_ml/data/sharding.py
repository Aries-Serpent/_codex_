# BEGIN: CODEX_DATA_SHARD
from __future__ import annotations


def shard_range(rank: int, world: int, n: int) -> tuple[int, int]:
    if rank < 0 or rank >= world or n < 0:
        raise ValueError("shard_range expects 0 <= rank < world and non-negative n")
    base, rem = divmod(n, world)
    start = rank * base + min(rank, rem)
    end = start + base + (1 if rank < rem else 0)
    return start, end


# END: CODEX_DATA_SHARD
