"""
Manifest Module

This module provides functionality for manifest.

Usage:
    from data.manifest import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Dataset manifest helpers used by the modular training stack."""


import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast

from codex_ml.utils.atomic_io import safe_write_text
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


def x__sha256_file__mutmut_orig(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_1(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = None
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_2(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open(None) as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_3(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("XXrbXX") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_4(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("RB") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_5(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(None, b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_6(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), None):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_7(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_8(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), ):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_9(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: None, b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_10(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(None), b""):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_11(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b"XXXX"):
            digest.update(chunk)
    return digest.hexdigest()


def x__sha256_file__mutmut_12(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(None)
    return digest.hexdigest()

x__sha256_file__mutmut_mutants : ClassVar[MutantDict] = {
'x__sha256_file__mutmut_1': x__sha256_file__mutmut_1, 
    'x__sha256_file__mutmut_2': x__sha256_file__mutmut_2, 
    'x__sha256_file__mutmut_3': x__sha256_file__mutmut_3, 
    'x__sha256_file__mutmut_4': x__sha256_file__mutmut_4, 
    'x__sha256_file__mutmut_5': x__sha256_file__mutmut_5, 
    'x__sha256_file__mutmut_6': x__sha256_file__mutmut_6, 
    'x__sha256_file__mutmut_7': x__sha256_file__mutmut_7, 
    'x__sha256_file__mutmut_8': x__sha256_file__mutmut_8, 
    'x__sha256_file__mutmut_9': x__sha256_file__mutmut_9, 
    'x__sha256_file__mutmut_10': x__sha256_file__mutmut_10, 
    'x__sha256_file__mutmut_11': x__sha256_file__mutmut_11, 
    'x__sha256_file__mutmut_12': x__sha256_file__mutmut_12
}

def _sha256_file(*args, **kwargs):
    result = _mutmut_trampoline(x__sha256_file__mutmut_orig, x__sha256_file__mutmut_mutants, args, kwargs)
    return result 

_sha256_file.__signature__ = _mutmut_signature(x__sha256_file__mutmut_orig)
x__sha256_file__mutmut_orig.__name__ = 'x__sha256_file'


def x__default_created_at__mutmut_orig() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_1() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = None
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_2() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get(None)
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_3() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("XXSOURCE_DATE_EPOCHXX")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_4() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("source_date_epoch")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_5() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(None)
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_6() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(None))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_7() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(None)
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_8() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(None, exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_9() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=None)
    return int(time.time())


def x__default_created_at__mutmut_10() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(exc_info=True)
    return int(time.time())


def x__default_created_at__mutmut_11() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", )
    return int(time.time())


def x__default_created_at__mutmut_12() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=False)
    return int(time.time())


def x__default_created_at__mutmut_13() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError as e:
            logger.debug(f"ValueError: {e}")
            logger.warning(f"ValueError: {e}", exc_info=True)
    return int(None)

x__default_created_at__mutmut_mutants : ClassVar[MutantDict] = {
'x__default_created_at__mutmut_1': x__default_created_at__mutmut_1, 
    'x__default_created_at__mutmut_2': x__default_created_at__mutmut_2, 
    'x__default_created_at__mutmut_3': x__default_created_at__mutmut_3, 
    'x__default_created_at__mutmut_4': x__default_created_at__mutmut_4, 
    'x__default_created_at__mutmut_5': x__default_created_at__mutmut_5, 
    'x__default_created_at__mutmut_6': x__default_created_at__mutmut_6, 
    'x__default_created_at__mutmut_7': x__default_created_at__mutmut_7, 
    'x__default_created_at__mutmut_8': x__default_created_at__mutmut_8, 
    'x__default_created_at__mutmut_9': x__default_created_at__mutmut_9, 
    'x__default_created_at__mutmut_10': x__default_created_at__mutmut_10, 
    'x__default_created_at__mutmut_11': x__default_created_at__mutmut_11, 
    'x__default_created_at__mutmut_12': x__default_created_at__mutmut_12, 
    'x__default_created_at__mutmut_13': x__default_created_at__mutmut_13
}

def _default_created_at(*args, **kwargs):
    result = _mutmut_trampoline(x__default_created_at__mutmut_orig, x__default_created_at__mutmut_mutants, args, kwargs)
    return result 

_default_created_at.__signature__ = _mutmut_signature(x__default_created_at__mutmut_orig)
x__default_created_at__mutmut_orig.__name__ = 'x__default_created_at'


@dataclass(slots=True)
class Shard:
    path: str
    size: int
    sha256: str


@dataclass(slots=True)
class DatasetManifest:
    schema_version: str = "1.0"
    created_at: int = field(default_factory=_default_created_at)
    dataset_id: str | None = None
    shards: list[Shard] = field(default_factory=list)

    @staticmethod
    def build(root: str | Path, shard_paths: list[str]) -> DatasetManifest:
        """Construct a manifest for ``shard_paths`` relative to ``root``."""

        base = Path(root)
        entries: list[Shard] = []
        for relative in shard_paths:
            file_path = base / relative
            stat = file_path.stat()
            entries.append(
                Shard(
                    path=relative,
                    size=stat.st_size,
                    sha256=_sha256_file(file_path),
                )
            )
        return DatasetManifest(shards=entries)

    def to_json(self) -> str:
        """Serialise the manifest to a formatted JSON string."""

        return json.dumps(
            {
                "schema_version": self.schema_version,
                "created_at": self.created_at,
                "dataset_id": self.dataset_id,
                "shards": [asdict(shard) for shard in self.shards],
            },
            indent=2,
            sort_keys=True,
        )

    def write(self, path: str | Path) -> Path:
        """Persist the manifest to ``path`` atomically."""

        result = cast(Path, safe_write_text(path, self.to_json()))
        return result

    @staticmethod
    def load(path: str | Path) -> DatasetManifest:
        """Load a manifest from disk without mutating the file."""

        data: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        shards = [Shard(**entry) for entry in data.get("shards", [])]
        return DatasetManifest(
            schema_version=data.get("schema_version", "1.0"),
            created_at=int(data.get("created_at", 0)),
            dataset_id=data.get("dataset_id"),
            shards=shards,
        )

    def verify(self, root: str | Path) -> None:
        """Ensure every shard exists beneath ``root`` with matching checksums."""

        base = Path(root)
        for shard in self.shards:
            target = base / shard.path
            if not target.exists():
                raise ValueError(f"Missing shard: {shard.path}")
            actual = _sha256_file(target)
            if actual != shard.sha256:
                raise ValueError(
                    f"Checksum mismatch for {shard.path}: " f"expected {shard.sha256}, got {actual}"
                )


__all__ = ["DatasetManifest", "Shard"]
