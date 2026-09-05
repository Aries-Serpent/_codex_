"""Streaming-friendly dataset loader with caching and deterministic helpers."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import csv  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import (  # noqa: E402
    Any,
    Optional,
    TypeVar,
)

from codex_ml.config import DataConfig  # noqa: E402
from codex_ml.utils.provenance import export_environment  # noqa: E402
from codex_ml.utils.seeding import set_reproducible  # noqa: E402

T = TypeVar("T")

__all__ = [
    "CacheManifest",
    "DataPreparationError",
    "apply_safety_filter",
    "load_dataset",
    "load_texts",
    "prepare_data_from_config",
    "seeded_shuffle",
    "stream_texts",
    "take_n",
]


class DataPreparationError(RuntimeError):
    """Raised when dataset preparation fails."""


@dataclass
class CacheManifest:
    """Metadata describing the cached representation of a dataset."""

    version: str = "1"
    source: str = ""
    checksum: str = ""
    encoding: str = "utf-8"
    newline: str = "unix"
    num_records: int = 0
    shard_index: int = 0
    shard_total: int = 1
    created_at: float = field(default_factory=time.time)
    params: dict[str, Any] = field(default_factory=dict)
    splits: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "source": self.source,
            "checksum": self.checksum,
            "encoding": self.encoding,
            "newline": self.newline,
            "num_records": self.num_records,
            "shard": {"index": self.shard_index, "total": self.shard_total},
            "created_at": self.created_at,
            "params": dict(self.params),
            "splits": {k: dict(v) for k, v in self.splits.items()},
        }

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> Optional[CacheManifest]:
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (
            IOError,
            OSError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
            ModuleNotFoundError,
            ImportError,
        ):
            logger.warning("Exception occurred", exc_info=True)
            return None
        return cls(
            version=str(data.get("version", "1")),
            source=str(data.get("source", "")),
            checksum=str(data.get("checksum", "")),
            encoding=str(data.get("encoding", "utf-8")),
            newline=str(data.get("newline", "unix")),
            num_records=int(data.get("num_records", 0)),
            shard_index=int(data.get("shard", {}).get("index", 0)),
            shard_total=int(data.get("shard", {}).get("total", 1)),
            created_at=float(data.get("created_at", time.time())),
            params=dict(data.get("params", {})),
            splits={k: dict(v) for k, v in data.get("splits", {}).items()},
        )


def normalize_newlines(text: str, mode: str) -> str:
    """Normalise newline characters according to ``mode``."""

    if mode not in {"unix", "windows", "preserve"}:
        raise ValueError(f"Unsupported newline mode: {mode}")
    normalised = text.replace("\r\n", "\n").replace("\r", "\n")
    if mode == "windows":
        return normalised.replace("\n", "\r\n")
    if mode == "preserve":
        return text
    return normalised


def _decode_bytes(
    raw: bytes,
    *,
    encoding: str,
    fallback_encoding: Optional[str],
    validate_utf8: bool,
) -> str:
    try:
        return raw.decode(encoding)
    except UnicodeDecodeError as e:
        type(e).__name__
        logger.debug("UnicodeDecodeError: <ERROR_TYPE>")
        logger.warning("UnicodeDecodeError: <ERROR_TYPE>", exc_info=True)
        if validate_utf8:
            raise
        if fallback_encoding:
            return raw.decode(fallback_encoding, errors="replace")
        return raw.decode(encoding, errors="replace")


def stream_texts(
    source: str | Path | Iterable[str],
    *,
    encoding: str = "utf-8",
    fallback_encoding: Optional[str] = None,
    newline: str = "unix",
    shard_index: int = 0,
    shard_total: int = 1,
    validate_utf8: bool = True,
    skip_empty: bool = True,
) -> Iterator[str]:
    """Yield text records from ``source`` one by one."""

    if shard_total <= 0:
        raise ValueError("shard_total must be positive")
    if shard_index < 0 or shard_index >= shard_total:
        raise ValueError("shard_index must be within [0, shard_total)")

    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.is_dir():
            for child in sorted(path.iterdir()):
                if child.is_file():
                    yield from stream_texts(
                        child,
                        encoding=encoding,
                        fallback_encoding=fallback_encoding,
                        newline=newline,
                        shard_index=shard_index,
                        shard_total=shard_total,
                        validate_utf8=validate_utf8,
                        skip_empty=skip_empty,
                    )
            return
        with path.open("rb") as fh:
            for idx, raw_line in enumerate(fh):
                if shard_total > 1 and idx % shard_total != shard_index:
                    continue
                line = _decode_bytes(
                    raw_line,
                    encoding=encoding,
                    fallback_encoding=fallback_encoding,
                    validate_utf8=validate_utf8,
                )
                line = normalize_newlines(line, newline)
                line = line.strip("\n")
                if skip_empty and not line.strip():
                    continue
                yield line
    else:
        for idx, item in enumerate(source):
            if shard_total > 1 and idx % shard_total != shard_index:
                continue
            text = normalize_newlines(str(item), newline)
            text = text.strip("\n")
            if skip_empty and not text.strip():
                continue
            yield text


def take_n(iterable: Iterable[T], n: int, *, strict: bool = False) -> list[T]:
    """Take ``n`` items from ``iterable`` deterministically."""

    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return []
    result: list[T] = []
    for item in iterable:
        result.append(item)
        if len(result) >= n:
            break
    if strict and len(result) < n:
        raise ValueError(f"Iterable contained only {len(result)} items; expected {n}")
    return result


def seeded_shuffle(items: Sequence[T], seed: int) -> list[T]:
    """Return a deterministically shuffled copy of ``items`` using ``seed``."""

    from random import Random

    result = list(items)
    Random(seed).shuffle(result)  # nosec B311 — non-cryptographic ML sampling/shuffling
    return result


def _compute_checksum(texts: Iterable[str]) -> str:
    h = hashlib.sha256()
    for text in texts:
        h.update(text.encode("utf-8"))
    return h.hexdigest()


def _cache_key(path: Path, **params: Any) -> str:
    h = hashlib.sha256()
    h.update(str(path.resolve()).encode("utf-8"))
    for key in sorted(params):
        h.update(f"{key}={params[key]}".encode())
    try:
        stat = path.stat()
        h.update(str(stat.st_mtime_ns).encode("utf-8"))
    except FileNotFoundError as e:
        type(e).__name__
        logger.debug("FileNotFoundError: <ERROR_TYPE>")
        logger.warning("FileNotFoundError: <ERROR_TYPE>", exc_info=True)
    return h.hexdigest()


_TEXT_FIELD_CANDIDATES = ("text", "content", "value")


def _detect_dataset_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    return "text"


def _extract_text_from_mapping(mapping: dict[str, Any]) -> str:
    for key in _TEXT_FIELD_CANDIDATES:
        if key in mapping and mapping[key] is not None:
            return str(mapping[key])
    if len(mapping) == 1:
        value = next(iter(mapping.values()))
        return "" if value is None else str(value)
    raise ValueError("Could not determine text field in mapping record")


def _coerce_jsonl_records(lines: Iterable[str]) -> list[str]:
    texts: list[str] = []
    for idx, line in enumerate(lines, start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {idx}: {exc}") from exc
        if isinstance(record, str):
            texts.append(record)
        elif isinstance(record, Mapping):
            texts.append(_extract_text_from_mapping(dict(record)))
        else:
            raise ValueError(
                f"Unsupported JSONL payload type on line {idx}: {type(record).__name__}"
            )
    return texts


def _coerce_csv_records(lines: Iterable[str], *, skip_empty: bool) -> list[str]:
    # ``csv`` expects newline-terminated rows; rehydrate in-memory buffer.
    buffer = io.StringIO()
    for line in lines:
        buffer.write(line)
        buffer.write("\n")
    buffer.seek(0)

    reader = csv.DictReader(buffer)
    fieldnames = reader.fieldnames or []
    if not fieldnames:
        return []
    text_field = None
    lowered = {name.lower(): name for name in fieldnames}
    for candidate in _TEXT_FIELD_CANDIDATES:
        if candidate in lowered:
            text_field = lowered[candidate]
            break
    if text_field is None:
        text_field = fieldnames[0]

    texts: list[str] = []
    for row in reader:
        if not row:
            continue
        value = row.get(text_field)
        if value is None:
            # fallback to first non-empty column
            value = next((row[name] for name in fieldnames if row.get(name)), "")
        if skip_empty and (value is None or not str(value).strip()):
            continue
        texts.append(str(value))
    return texts


def _normalise_loaded_texts(
    path: Path, lines: list[str], *, skip_empty: bool, fmt: str | None = None
) -> list[str]:
    fmt = fmt or _detect_dataset_format(path)
    if fmt == "jsonl":
        return _coerce_jsonl_records(lines)
    if fmt == "csv":
        return _coerce_csv_records(lines, skip_empty=skip_empty)
    return lines


def load_texts(path: Path, encoding: str = "utf-8") -> list[str]:
    """Load text records from ``path`` eager into memory."""

    return list(stream_texts(path, encoding=encoding))


def load_dataset(
    path: Path,
    cache_dir: Optional[Path] = None,
    *,
    encoding: str = "utf-8",
    newline: str = "unix",
    validate_utf8: bool = True,
    fallback_encoding: Optional[str] = None,
    manifest_path: Optional[Path] = None,
    shard_index: int = 0,
    shard_total: int = 1,
    max_items: Optional[int] = None,
    skip_empty: bool = True,
) -> list[str]:
    """Load dataset from ``path`` with optional caching and manifest tracking."""
    # Convert string path to Path object if needed
    if not isinstance(path, Path):
        path = Path(path)

    if cache_dir is None:
        cache_dir = path.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    params = {
        "encoding": encoding,
        "newline": newline,
        "validate_utf8": validate_utf8,
        "fallback": fallback_encoding or "",
        "shard_index": shard_index,
        "shard_total": shard_total,
        "max_items": max_items if max_items is not None else "",
        "skip_empty": skip_empty,
    }
    key = _cache_key(path, **params)
    cache_file = cache_dir / f"{key}.pkl"
    manifest_file = manifest_path or (cache_dir / f"{key}.manifest.json")

    if cache_file.exists():
        try:
            # Use safe pickle loading to prevent code execution vulnerabilities
            from codex_ml.utils.safe_pickle import safe_pickle_load

            data = safe_pickle_load(str(cache_file), use_restricted_unpickler=True)
            if isinstance(data, list):
                return data
        except (IOError, OSError, ModuleNotFoundError, ImportError):
            logger.warning("Exception occurred", exc_info=True)
            try:
                cache_file.unlink()
            except FileNotFoundError as e:
                type(e).__name__
                logger.debug("FileNotFoundError: <ERROR_TYPE>")
                logger.warning("FileNotFoundError: <ERROR_TYPE>", exc_info=True)

    fmt = _detect_dataset_format(path)

    iterator = stream_texts(
        path,
        encoding=encoding,
        fallback_encoding=fallback_encoding,
        newline=newline,
        shard_index=shard_index,
        shard_total=shard_total,
        validate_utf8=validate_utf8,
        skip_empty=skip_empty,
    )

    if fmt == "csv":
        raw_lines = list(iterator)
    elif max_items is not None:
        raw_lines = take_n(iterator, max_items)
    else:
        raw_lines = list(iterator)

    texts = _normalise_loaded_texts(path, raw_lines, skip_empty=skip_empty, fmt=fmt)
    if max_items is not None:
        texts = texts[:max_items]

    from codex_ml.utils.safe_pickle import safe_pickle_dump

    safe_pickle_dump(texts, str(cache_file))
    manifest = CacheManifest(
        source=str(path),
        checksum=_compute_checksum(texts),
        encoding=encoding,
        newline=newline,
        num_records=len(texts),
        shard_index=shard_index,
        shard_total=shard_total,
        params=params,
    )
    manifest.write(Path(manifest_file))
    return texts


def apply_safety_filter(
    texts: Sequence[str],
    filter_enabled: bool = True,
    safety_fn: Optional[Callable[[str], str]] = None,
) -> list[str]:
    """Optionally apply ``safety_fn`` to each text when ``filter_enabled``."""

    if not filter_enabled or safety_fn is None:
        return list(texts)
    return [safety_fn(t) for t in texts]


def prepare_data_from_config(data_cfg: DataConfig) -> dict[str, Any]:
    """Prepare datasets according to ``data_cfg`` and write cache artefacts."""

    source_path = Path(data_cfg.source_path)
    if not source_path.exists():
        raise DataPreparationError(f"data.source_path does not exist: {source_path}")

    seed_value = int(data_cfg.shuffle_seed or 0)
    set_reproducible(seed_value)

    base_iter = stream_texts(
        source_path,
        encoding=data_cfg.encoding,
        fallback_encoding=data_cfg.fallback_encoding,
        newline=data_cfg.newline_normalization,
        shard_index=data_cfg.shard.index,
        shard_total=data_cfg.shard.total,
        validate_utf8=data_cfg.validate_utf8,
        skip_empty=data_cfg.skip_empty,
    )
    texts = list(base_iter) if data_cfg.max_items is None else take_n(base_iter, data_cfg.max_items)

    from codex_ml.data_utils import split_dataset  # local import to avoid cycle

    ratios = {k: float(v) for k, v in data_cfg.split_ratios.items()}
    train_ratio = ratios.get("train", 0.9)
    seed = seed_value
    train_texts, remainder = split_dataset(
        texts=texts,
        train_ratio=train_ratio,
        seed=seed,
        cache_path=None,
        checksum_path=None,
        filter_enabled=data_cfg.safety_filter,
    )

    remainder = list(remainder)
    other_ratios = [(name, ratio) for name, ratio in ratios.items() if name != "train"]
    total_remaining_ratio = sum(r for _, r in other_ratios)
    remainder_shuffled = seeded_shuffle(remainder, seed + 1)

    split_map: dict[str, list[str]] = {"train": train_texts}
    offset = 0
    remaining = len(remainder_shuffled)
    for idx, (name, ratio) in enumerate(other_ratios):
        if ratio <= 0 or remaining == 0:
            split_map[name] = []
            continue
        if idx == len(other_ratios) - 1 or total_remaining_ratio <= 0:
            split_map[name] = remainder_shuffled[offset:]
            offset = remaining
            continue
        share = ratio / total_remaining_ratio if total_remaining_ratio else 0.0
        count = int(round(remaining * share))
        count = max(0, min(count, remaining - offset))
        split_map[name] = remainder_shuffled[offset : offset + count]
        offset += count
        total_remaining_ratio -= ratio
    if offset < remaining:
        last_key = other_ratios[-1][0] if other_ratios else "train"
        split_map.setdefault(last_key, []).extend(remainder_shuffled[offset:])

    cache_dir = Path(data_cfg.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    export_environment(
        cache_dir / "provenance",
        seed=seed_value,
        command="prepare-data",
        extras={"source": str(source_path.resolve())},
    )

    manifest_path = (
        Path(data_cfg.manifest_path)
        if data_cfg.manifest_path
        else cache_dir / data_cfg.cache_manifest_name
    )

    split_metadata: dict[str, dict[str, Any]] = {}
    for name, values in split_map.items():
        target = cache_dir / f"{name}.txt"
        target.write_text("\n".join(values) + ("\n" if values else ""), encoding=data_cfg.encoding)
        split_metadata[name] = {
            "path": str(target),
            "count": len(values),
            "checksum": _compute_checksum(values),
        }

    manifest = CacheManifest(
        source=str(source_path.resolve()),
        checksum=_compute_checksum(train_texts + remainder_shuffled),
        encoding=data_cfg.encoding,
        newline=data_cfg.newline_normalization,
        num_records=len(train_texts) + len(remainder_shuffled),
        shard_index=data_cfg.shard.index,
        shard_total=data_cfg.shard.total,
        params={
            "split_ratios": ratios,
            "safety_filter": data_cfg.safety_filter,
            "shuffle_seed": data_cfg.shuffle_seed,
        },
        splits=split_metadata,
    )
    manifest.write(manifest_path)

    return {
        "source_path": str(source_path),
        "cache_dir": str(cache_dir),
        "manifest": str(manifest_path),
        "splits": split_metadata,
    }
