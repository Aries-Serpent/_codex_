"""Minimal torch.distributed.fsdp stub."""

from __future__ import annotations

from enum import Enum
from typing import Any


class BackwardPrefetch(Enum):
    BACKWARD_PRE = "BACKWARD_PRE"
    BACKWARD_POST = "BACKWARD_POST"


class CPUOffload:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


class FullStateDictConfig:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


class MixedPrecision:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


class ShardedStateDictConfig:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


class ShardingStrategy(Enum):
    FULL_SHARD = "FULL_SHARD"
    SHARD_GRAD_OP = "SHARD_GRAD_OP"
    NO_SHARD = "NO_SHARD"
    HYBRID_SHARD = "HYBRID_SHARD"


class StateDictType(Enum):
    FULL_STATE_DICT = "FULL_STATE_DICT"
    SHARDED_STATE_DICT = "SHARDED_STATE_DICT"


class FullyShardedDataParallel:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


__all__ = [
    "BackwardPrefetch",
    "CPUOffload",
    "FullStateDictConfig",
    "MixedPrecision",
    "ShardedStateDictConfig",
    "ShardingStrategy",
    "StateDictType",
    "FullyShardedDataParallel",
]
