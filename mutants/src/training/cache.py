"""Token cache for persisting tokenized batches to disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

import numpy as np
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class TokenCache:
    """Persist tokenized batches to disk as NPZ shards with a manifest."""

    def xǁTokenCacheǁ__init____mutmut_orig(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_1(self, out_dir: str | Path, rows_per_shard: int = 1025) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_2(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = None
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_3(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(None)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_4(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=None, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_5(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=None)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_6(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_7(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, )
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_8(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=False, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_9(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=False)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_10(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = None
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_11(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(None)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_12(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = None
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_13(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = None
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_14(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 1
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_15(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = None
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_16(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 1
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_17(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = None
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_18(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "XXrows_per_shardXX": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_19(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "ROWS_PER_SHARD": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_20(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "XXshardsXX": [],
        }
        self._write_manifest()

    def xǁTokenCacheǁ__init____mutmut_21(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "SHARDS": [],
        }
        self._write_manifest()
    
    xǁTokenCacheǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenCacheǁ__init____mutmut_1': xǁTokenCacheǁ__init____mutmut_1, 
        'xǁTokenCacheǁ__init____mutmut_2': xǁTokenCacheǁ__init____mutmut_2, 
        'xǁTokenCacheǁ__init____mutmut_3': xǁTokenCacheǁ__init____mutmut_3, 
        'xǁTokenCacheǁ__init____mutmut_4': xǁTokenCacheǁ__init____mutmut_4, 
        'xǁTokenCacheǁ__init____mutmut_5': xǁTokenCacheǁ__init____mutmut_5, 
        'xǁTokenCacheǁ__init____mutmut_6': xǁTokenCacheǁ__init____mutmut_6, 
        'xǁTokenCacheǁ__init____mutmut_7': xǁTokenCacheǁ__init____mutmut_7, 
        'xǁTokenCacheǁ__init____mutmut_8': xǁTokenCacheǁ__init____mutmut_8, 
        'xǁTokenCacheǁ__init____mutmut_9': xǁTokenCacheǁ__init____mutmut_9, 
        'xǁTokenCacheǁ__init____mutmut_10': xǁTokenCacheǁ__init____mutmut_10, 
        'xǁTokenCacheǁ__init____mutmut_11': xǁTokenCacheǁ__init____mutmut_11, 
        'xǁTokenCacheǁ__init____mutmut_12': xǁTokenCacheǁ__init____mutmut_12, 
        'xǁTokenCacheǁ__init____mutmut_13': xǁTokenCacheǁ__init____mutmut_13, 
        'xǁTokenCacheǁ__init____mutmut_14': xǁTokenCacheǁ__init____mutmut_14, 
        'xǁTokenCacheǁ__init____mutmut_15': xǁTokenCacheǁ__init____mutmut_15, 
        'xǁTokenCacheǁ__init____mutmut_16': xǁTokenCacheǁ__init____mutmut_16, 
        'xǁTokenCacheǁ__init____mutmut_17': xǁTokenCacheǁ__init____mutmut_17, 
        'xǁTokenCacheǁ__init____mutmut_18': xǁTokenCacheǁ__init____mutmut_18, 
        'xǁTokenCacheǁ__init____mutmut_19': xǁTokenCacheǁ__init____mutmut_19, 
        'xǁTokenCacheǁ__init____mutmut_20': xǁTokenCacheǁ__init____mutmut_20, 
        'xǁTokenCacheǁ__init____mutmut_21': xǁTokenCacheǁ__init____mutmut_21
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenCacheǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTokenCacheǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTokenCacheǁ__init____mutmut_orig)
    xǁTokenCacheǁ__init____mutmut_orig.__name__ = 'xǁTokenCacheǁ__init__'

    def xǁTokenCacheǁadd_batch__mutmut_orig(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = next(iter(batch.values())).shape[0]
        self._buffer_rows += rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def xǁTokenCacheǁadd_batch__mutmut_1(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(None)
        rows = next(iter(batch.values())).shape[0]
        self._buffer_rows += rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def xǁTokenCacheǁadd_batch__mutmut_2(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = None
        self._buffer_rows += rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def xǁTokenCacheǁadd_batch__mutmut_3(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = next(None).shape[0]
        self._buffer_rows += rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def xǁTokenCacheǁadd_batch__mutmut_4(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = next(iter(None)).shape[0]
        self._buffer_rows += rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def xǁTokenCacheǁadd_batch__mutmut_5(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = next(iter(batch.values())).shape[1]
        self._buffer_rows += rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def xǁTokenCacheǁadd_batch__mutmut_6(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = next(iter(batch.values())).shape[0]
        self._buffer_rows = rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def xǁTokenCacheǁadd_batch__mutmut_7(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = next(iter(batch.values())).shape[0]
        self._buffer_rows -= rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def xǁTokenCacheǁadd_batch__mutmut_8(self, batch: dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = next(iter(batch.values())).shape[0]
        self._buffer_rows += rows
        if self._buffer_rows > self.rows_per_shard:
            self._flush()
    
    xǁTokenCacheǁadd_batch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenCacheǁadd_batch__mutmut_1': xǁTokenCacheǁadd_batch__mutmut_1, 
        'xǁTokenCacheǁadd_batch__mutmut_2': xǁTokenCacheǁadd_batch__mutmut_2, 
        'xǁTokenCacheǁadd_batch__mutmut_3': xǁTokenCacheǁadd_batch__mutmut_3, 
        'xǁTokenCacheǁadd_batch__mutmut_4': xǁTokenCacheǁadd_batch__mutmut_4, 
        'xǁTokenCacheǁadd_batch__mutmut_5': xǁTokenCacheǁadd_batch__mutmut_5, 
        'xǁTokenCacheǁadd_batch__mutmut_6': xǁTokenCacheǁadd_batch__mutmut_6, 
        'xǁTokenCacheǁadd_batch__mutmut_7': xǁTokenCacheǁadd_batch__mutmut_7, 
        'xǁTokenCacheǁadd_batch__mutmut_8': xǁTokenCacheǁadd_batch__mutmut_8
    }
    
    def add_batch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenCacheǁadd_batch__mutmut_orig"), object.__getattribute__(self, "xǁTokenCacheǁadd_batch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_batch.__signature__ = _mutmut_signature(xǁTokenCacheǁadd_batch__mutmut_orig)
    xǁTokenCacheǁadd_batch__mutmut_orig.__name__ = 'xǁTokenCacheǁadd_batch'

    def xǁTokenCacheǁ_flush__mutmut_orig(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_1(self) -> None:
        if self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_2(self) -> None:
        if not self._buffer:
            return
        shard_path = None
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_3(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir * f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_4(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = None
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_5(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[1].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_6(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = None
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_7(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate(None, axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_8(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=None)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_9(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate(axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_10(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], )
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_11(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=1)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_12(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(None, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_13(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(**data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_14(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, )  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_15(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = None
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_16(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(None)
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_17(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(None).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_18(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(None)).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_19(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[1])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_20(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = None
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_21(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"XXpathXX": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_22(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"PATH": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_23(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "XXrowsXX": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_24(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "ROWS": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_25(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(None)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_26(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["XXshardsXX"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_27(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["SHARDS"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_28(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = None
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_29(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 1
        self._shard_idx += 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_30(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx = 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_31(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx -= 1
        self._write_manifest()

    def xǁTokenCacheǁ_flush__mutmut_32(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 2
        self._write_manifest()
    
    xǁTokenCacheǁ_flush__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenCacheǁ_flush__mutmut_1': xǁTokenCacheǁ_flush__mutmut_1, 
        'xǁTokenCacheǁ_flush__mutmut_2': xǁTokenCacheǁ_flush__mutmut_2, 
        'xǁTokenCacheǁ_flush__mutmut_3': xǁTokenCacheǁ_flush__mutmut_3, 
        'xǁTokenCacheǁ_flush__mutmut_4': xǁTokenCacheǁ_flush__mutmut_4, 
        'xǁTokenCacheǁ_flush__mutmut_5': xǁTokenCacheǁ_flush__mutmut_5, 
        'xǁTokenCacheǁ_flush__mutmut_6': xǁTokenCacheǁ_flush__mutmut_6, 
        'xǁTokenCacheǁ_flush__mutmut_7': xǁTokenCacheǁ_flush__mutmut_7, 
        'xǁTokenCacheǁ_flush__mutmut_8': xǁTokenCacheǁ_flush__mutmut_8, 
        'xǁTokenCacheǁ_flush__mutmut_9': xǁTokenCacheǁ_flush__mutmut_9, 
        'xǁTokenCacheǁ_flush__mutmut_10': xǁTokenCacheǁ_flush__mutmut_10, 
        'xǁTokenCacheǁ_flush__mutmut_11': xǁTokenCacheǁ_flush__mutmut_11, 
        'xǁTokenCacheǁ_flush__mutmut_12': xǁTokenCacheǁ_flush__mutmut_12, 
        'xǁTokenCacheǁ_flush__mutmut_13': xǁTokenCacheǁ_flush__mutmut_13, 
        'xǁTokenCacheǁ_flush__mutmut_14': xǁTokenCacheǁ_flush__mutmut_14, 
        'xǁTokenCacheǁ_flush__mutmut_15': xǁTokenCacheǁ_flush__mutmut_15, 
        'xǁTokenCacheǁ_flush__mutmut_16': xǁTokenCacheǁ_flush__mutmut_16, 
        'xǁTokenCacheǁ_flush__mutmut_17': xǁTokenCacheǁ_flush__mutmut_17, 
        'xǁTokenCacheǁ_flush__mutmut_18': xǁTokenCacheǁ_flush__mutmut_18, 
        'xǁTokenCacheǁ_flush__mutmut_19': xǁTokenCacheǁ_flush__mutmut_19, 
        'xǁTokenCacheǁ_flush__mutmut_20': xǁTokenCacheǁ_flush__mutmut_20, 
        'xǁTokenCacheǁ_flush__mutmut_21': xǁTokenCacheǁ_flush__mutmut_21, 
        'xǁTokenCacheǁ_flush__mutmut_22': xǁTokenCacheǁ_flush__mutmut_22, 
        'xǁTokenCacheǁ_flush__mutmut_23': xǁTokenCacheǁ_flush__mutmut_23, 
        'xǁTokenCacheǁ_flush__mutmut_24': xǁTokenCacheǁ_flush__mutmut_24, 
        'xǁTokenCacheǁ_flush__mutmut_25': xǁTokenCacheǁ_flush__mutmut_25, 
        'xǁTokenCacheǁ_flush__mutmut_26': xǁTokenCacheǁ_flush__mutmut_26, 
        'xǁTokenCacheǁ_flush__mutmut_27': xǁTokenCacheǁ_flush__mutmut_27, 
        'xǁTokenCacheǁ_flush__mutmut_28': xǁTokenCacheǁ_flush__mutmut_28, 
        'xǁTokenCacheǁ_flush__mutmut_29': xǁTokenCacheǁ_flush__mutmut_29, 
        'xǁTokenCacheǁ_flush__mutmut_30': xǁTokenCacheǁ_flush__mutmut_30, 
        'xǁTokenCacheǁ_flush__mutmut_31': xǁTokenCacheǁ_flush__mutmut_31, 
        'xǁTokenCacheǁ_flush__mutmut_32': xǁTokenCacheǁ_flush__mutmut_32
    }
    
    def _flush(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenCacheǁ_flush__mutmut_orig"), object.__getattribute__(self, "xǁTokenCacheǁ_flush__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _flush.__signature__ = _mutmut_signature(xǁTokenCacheǁ_flush__mutmut_orig)
    xǁTokenCacheǁ_flush__mutmut_orig.__name__ = 'xǁTokenCacheǁ_flush'

    def finalize(self) -> None:
        """Flush remaining data to disk."""
        self._flush()

    def xǁTokenCacheǁ_write_manifest__mutmut_orig(self) -> None:
        (self.out_dir / "manifest.json").write_text(json.dumps(self.manifest))

    def xǁTokenCacheǁ_write_manifest__mutmut_1(self) -> None:
        (self.out_dir / "manifest.json").write_text(None)

    def xǁTokenCacheǁ_write_manifest__mutmut_2(self) -> None:
        (self.out_dir * "manifest.json").write_text(json.dumps(self.manifest))

    def xǁTokenCacheǁ_write_manifest__mutmut_3(self) -> None:
        (self.out_dir / "XXmanifest.jsonXX").write_text(json.dumps(self.manifest))

    def xǁTokenCacheǁ_write_manifest__mutmut_4(self) -> None:
        (self.out_dir / "MANIFEST.JSON").write_text(json.dumps(self.manifest))

    def xǁTokenCacheǁ_write_manifest__mutmut_5(self) -> None:
        (self.out_dir / "manifest.json").write_text(json.dumps(None))
    
    xǁTokenCacheǁ_write_manifest__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenCacheǁ_write_manifest__mutmut_1': xǁTokenCacheǁ_write_manifest__mutmut_1, 
        'xǁTokenCacheǁ_write_manifest__mutmut_2': xǁTokenCacheǁ_write_manifest__mutmut_2, 
        'xǁTokenCacheǁ_write_manifest__mutmut_3': xǁTokenCacheǁ_write_manifest__mutmut_3, 
        'xǁTokenCacheǁ_write_manifest__mutmut_4': xǁTokenCacheǁ_write_manifest__mutmut_4, 
        'xǁTokenCacheǁ_write_manifest__mutmut_5': xǁTokenCacheǁ_write_manifest__mutmut_5
    }
    
    def _write_manifest(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenCacheǁ_write_manifest__mutmut_orig"), object.__getattribute__(self, "xǁTokenCacheǁ_write_manifest__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _write_manifest.__signature__ = _mutmut_signature(xǁTokenCacheǁ_write_manifest__mutmut_orig)
    xǁTokenCacheǁ_write_manifest__mutmut_orig.__name__ = 'xǁTokenCacheǁ_write_manifest'

    @staticmethod
    def iter_batches(out_dir: str | Path) -> Iterator[dict[str, np.ndarray]]:
        """Yield cached batches from ``out_dir`` using ``numpy.memmap``."""
        out = Path(out_dir)
        manifest = json.loads((out / "manifest.json").read_text())
        for shard in manifest.get("shards", []):
            shard_path = out / shard["path"]
            data = np.load(shard_path, mmap_mode="r")
            batch = {k: data[k] for k in data.files}
            yield batch
            data.close()


__all__ = ["TokenCache"]
