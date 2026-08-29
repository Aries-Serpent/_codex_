"""Minimal ingestion facade aligned with the public configs.

This module offers a lightweight ingest API that mirrors the defaults
shipped in ``configs/training/data/base.yaml``.  The goal is to provide a tiny
but well-structured entrypoint that unit tests (and the quickstart
documentation) can rely on without needing the heavyweight historical
pipelines.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import csv  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
from collections.abc import Iterable, Iterator, Mapping, MutableMapping  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import (  # noqa: E402
    Any,
    Optional,
)

from codex_ml.utils.yaml_support import MissingPyYAMLError, safe_load  # noqa: E402

__all__ = ["ingest", "ingest_sample", "load_dataset"]


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------


@dataclass
class _DataConfig:
    sample_mode: bool = True
    sample_size: int = 16
    dataset_name: str = "local_sample"
    dataset_path: Path = Path("data/sample/")
    shuffle: bool = True
    preprocess_lowercase: bool = True
    preprocess_max_length: Optional[int] = 512
    seed: int = 42


def _repo_root() -> Path:
    """Return the repository root (``src`` parent)."""

    return Path(__file__).resolve().parents[2]


def _default_config() -> _DataConfig:
    return _DataConfig()


def _load_yaml_config(config_path: Path) -> Mapping[str, Any]:
    with config_path.open("r", encoding="utf-8") as fh:
        loaded = safe_load(fh) or {}
    if not isinstance(loaded, Mapping):
        raise TypeError(f"Expected mapping at {config_path}, got {type(loaded).__name__}")
    return loaded


def _extract_config(mapping: Mapping[str, Any]) -> _DataConfig:
    data_block = mapping.get("data", {})
    if not isinstance(data_block, Mapping):
        data_block = {}

    dataset_block = data_block.get("dataset", {})
    if not isinstance(dataset_block, Mapping):
        dataset_block = {}

    preprocess_block = data_block.get("preprocess", {})
    if not isinstance(preprocess_block, Mapping):
        preprocess_block = {}

    sample_mode = bool(data_block.get("sample_mode", True))
    sample_size = int(data_block.get("sample_size", 16) or 0)
    dataset_name = str(dataset_block.get("name", "local_sample"))
    dataset_path = Path(str(dataset_block.get("path", "data/sample/")))
    shuffle = bool(dataset_block.get("shuffle", True))
    preprocess_lowercase = bool(preprocess_block.get("lowercase", True))
    max_length_raw = preprocess_block.get("max_length", 512)
    preprocess_max_length = None if max_length_raw in (None, "") else int(max_length_raw)

    return _DataConfig(
        sample_mode=sample_mode,
        sample_size=sample_size,
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        shuffle=shuffle,
        preprocess_lowercase=preprocess_lowercase,
        preprocess_max_length=preprocess_max_length,
    )


def _load_config(config_path: str | Path | None) -> _DataConfig:
    """Load the ingestion configuration, falling back to built-in defaults."""

    base = _repo_root() / "configs" / "data" / "base.yaml"
    target = Path(config_path) if config_path is not None else base
    try:
        mapping = _load_yaml_config(target)
    except FileNotFoundError as e:
        type(e).__name__
        logger.debug("FileNotFoundError: <ERROR_TYPE>")
        logger.warning("FileNotFoundError: <ERROR_TYPE>", exc_info=True)
        # Fallback to baked defaults when config is missing.
        return _default_config()
    except MissingPyYAMLError as e:
        type(e).__name__
        logger.debug("MissingPyYAMLError: <ERROR_TYPE>")
        logger.warning("MissingPyYAMLError: <ERROR_TYPE>", exc_info=True)
        return _default_config()
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return _default_config()

    cfg = _extract_config(mapping)

    dataset_path = cfg.dataset_path
    if not dataset_path.is_absolute():
        cfg.dataset_path = (_repo_root() / dataset_path).resolve()
    else:
        cfg.dataset_path = dataset_path
    return cfg


# ---------------------------------------------------------------------------
# Dataset parsing utilities
# ---------------------------------------------------------------------------

_TEXT_EXTENSIONS = {".txt", ".md"}
_JSONL_EXTENSIONS = {".jsonl"}
_JSON_EXTENSIONS = {".json"}
_CSV_EXTENSIONS = {".csv", ".tsv"}


def _iter_dataset_files(path: Path) -> Iterator[Path]:
    resolved = (path if path.is_absolute() else (_repo_root() / path)).resolve()
    if resolved.is_file():
        yield resolved
        return
    if resolved.is_dir():
        for candidate in sorted(resolved.glob("**/*")):
            if candidate.is_file():
                yield candidate


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [dict(row) for row in reader]


def _normalize_json_item(item: Any) -> dict[str, Any]:
    if isinstance(item, Mapping):
        return dict(item)
    return {"text": item}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                rows.append({"text": line})
                continue
            rows.append(_normalize_json_item(item))
    return rows


def _read_json(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except json.JSONDecodeError:
        logger.debug("Exception caught, returning", exc_info=True)
        return [{"text": path.read_text(encoding="utf-8")}]

    if isinstance(payload, list):
        return [_normalize_json_item(item) for item in payload]
    if isinstance(payload, tuple):
        return [_normalize_json_item(item) for item in payload]
    return [_normalize_json_item(payload)]


def _read_text(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    return [{"text": line.strip()} for line in text.splitlines() if line.strip()]


def _load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for file_path in _iter_dataset_files(path):
        suffix = file_path.suffix.lower()
        if suffix in _CSV_EXTENSIONS:
            records.extend(_read_csv(file_path))
        elif suffix in _JSONL_EXTENSIONS:
            records.extend(_read_jsonl(file_path))
        elif suffix in _JSON_EXTENSIONS:
            records.extend(_read_json(file_path))
        elif suffix in _TEXT_EXTENSIONS:
            records.extend(_read_text(file_path))
    return records


def _transform_value(value: Any, *, lowercase: bool, max_length: Optional[int]) -> Any:
    if isinstance(value, str):
        text = value.lower() if lowercase else value
        if max_length is not None and max_length >= 0:
            return text[:max_length]
        return text
    if isinstance(value, list):
        return [
            _transform_value(item, lowercase=lowercase, max_length=max_length) for item in value
        ]
    if isinstance(value, tuple):
        return tuple(
            _transform_value(item, lowercase=lowercase, max_length=max_length) for item in value
        )
    if isinstance(value, MutableMapping):
        return {
            key: _transform_value(sub, lowercase=lowercase, max_length=max_length)
            for key, sub in value.items()
        }
    return value


def _apply_preprocess(records: Iterable[dict[str, Any]], cfg: _DataConfig) -> list[dict[str, Any]]:
    processed: list[dict[str, Any]] = []
    for record in records:
        processed.append(
            {
                key: _transform_value(
                    value,
                    lowercase=cfg.preprocess_lowercase,
                    max_length=cfg.preprocess_max_length,
                )
                for key, value in record.items()
            }
        )
    return processed


def _limit_records(records: list[dict[str, Any]], cfg: _DataConfig) -> list[dict[str, Any]]:
    if not records:
        return []
    items = list(records)
    if cfg.shuffle:
        rng = random.Random(cfg.seed)  # nosec B311 — non-cryptographic ML sampling/shuffling
        rng.shuffle(items)
    if cfg.sample_mode:
        limit = max(0, cfg.sample_size)
        if limit:
            return items[:limit]
    return items


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def ingest(
    *,
    path: str | Path | None = None,
    sample_mode: Optional[bool] = None,
    sample_size: Optional[int] = None,
    seed: Optional[int] = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Load a small dataset according to the data defaults.

    Parameters are intentionally aligned with the defaults exposed in
    ``configs/training/data/base.yaml``.  They are optional so the smoke tests can
    invoke the function with minimal arguments.
    """

    cfg = _load_config(config_path)

    if path is not None:
        cfg.dataset_path = Path(path)
    if sample_mode is not None:
        cfg.sample_mode = bool(sample_mode)
    if sample_size is not None:
        cfg.sample_size = int(sample_size)
    if seed is not None:
        cfg.seed = int(seed)

    records = _load_records(cfg.dataset_path)
    records = _apply_preprocess(records, cfg)
    limited = _limit_records(records, cfg)

    metadata = {
        "dataset": cfg.dataset_name,
        "path": str(cfg.dataset_path),
        "sample_mode": cfg.sample_mode,
        "sample_size": cfg.sample_size,
        "total_records": len(records),
        "returned_records": len(limited),
    }
    return {"records": limited, "metadata": metadata}


def load_dataset(**kwargs: Any) -> dict[str, Any]:
    """Alias for :func:`ingest` to match historical naming."""

    return ingest(**kwargs)


def ingest_sample(sample_size: int = 8) -> dict[str, Any]:
    """Convenience helper returning a small sample regardless of config."""

    return ingest(sample_mode=True, sample_size=sample_size)
