"""Dataset utilities with deterministic splits and local caching."""

from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DataConfig:
    dataset_path: str | Path
    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1
    seed: int = 42
    cache_dir: str | Path = "artifacts/cache"
    loader_version: str = "1.0"


@dataclass
class DatasetSplits:
    train: list[Any]
    val: list[Any]
    test: list[Any]
    cache_path: Path | None = None
    from_cache: bool = False


def _normalise_ratios(cfg: DataConfig) -> tuple[float, float, float]:
    total = cfg.train_ratio + cfg.val_ratio + cfg.test_ratio
    if total <= 0:
        raise ValueError("Split ratios must sum to a positive value")
    return cfg.train_ratio / total, cfg.val_ratio / total, cfg.test_ratio / total


def _load_raw_dataset(path: Path) -> list[Any]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    with path.open("r", encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle if line.strip()]


def _hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _cache_key(
    cfg: DataConfig,
    dataset_path: Path,
    *,
    checksum_fn: Callable[[Path], str] = _hash_file,
) -> str:
    h = hashlib.sha256()
    h.update(str(dataset_path.resolve()).encode("utf-8"))
    h.update(checksum_fn(dataset_path).encode("utf-8"))
    h.update(str(cfg.loader_version).encode("utf-8"))
    h.update(str(cfg.seed).encode("utf-8"))
    h.update(str(cfg.train_ratio).encode("utf-8"))
    h.update(str(cfg.val_ratio).encode("utf-8"))
    h.update(str(cfg.test_ratio).encode("utf-8"))
    return h.hexdigest()


def _write_cache(path: Path, splits: DatasetSplits) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"train": splits.train, "val": splits.val, "test": splits.test}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_cache(path: Path) -> DatasetSplits:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return DatasetSplits(
        train=list(payload.get("train", [])),
        val=list(payload.get("val", [])),
        test=list(payload.get("test", [])),
        cache_path=path,
        from_cache=True,
    )


def load_dataset(cfg: DataConfig) -> DatasetSplits:
    dataset_path = Path(cfg.dataset_path)
    ratios = _normalise_ratios(cfg)
    cache_root = Path(cfg.cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_dir = cache_root / dataset_path.stem
    if not dataset_path.exists():
        cached = sorted(cache_dir.glob("splits-*.json"))
        if cached:
            return _read_cache(cached[-1])
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    raw_data = _load_raw_dataset(dataset_path)
    key = _cache_key(cfg, dataset_path)
    cache_path = cache_dir / f"splits-{key}.json"

    if cache_path.exists():
        return _read_cache(cache_path)

    rng = random.Random(cfg.seed)  # nosec B311 - deterministic dataset split shuffling
    shuffled = list(raw_data)
    rng.shuffle(shuffled)

    total = len(shuffled)
    train_end = int(total * ratios[0])
    val_end = train_end + int(total * ratios[1])

    train_split = shuffled[:train_end]
    val_split = shuffled[train_end:val_end]
    test_split = shuffled[val_end:]

    splits = DatasetSplits(
        train=train_split,
        val=val_split,
        test=test_split,
        cache_path=cache_path,
        from_cache=False,
    )
    _write_cache(cache_path, splits)
    return splits
