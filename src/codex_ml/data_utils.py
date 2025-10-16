"""Dataset utilities for splitting and streaming text corpora.

This module provides helper functions to split an iterable of strings into
train and validation subsets deterministically and to stream text from a
file in chunks. These utilities decouple data handling from the training
engine and ease reproducible experiments.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import random
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from codex_ml.safety import SafetyConfig, sanitize_prompt
from codex_ml.utils.optional import optional_import

torch, _HAS_TORCH = optional_import("torch")


def split_dataset(
    texts: Iterable[str] | str | Path,
    train_ratio: float = 0.9,
    seed: int = 0,
    cache_path: str | Path | None = None,
    checksum_path: str | Path | None = None,
    *,
    filter_enabled: bool = True,
) -> tuple[list[str], list[str]]:
    """Split texts into train and validation lists deterministically.

    Parameters
    ----------
    texts : Iterable[str] | str | Path
        An iterable of strings, or a path to a dataset file supported by
        codex_ml.data.loader.load_dataset.
    train_ratio : float, default=0.9
        Fraction of items placed in the training set.
    seed : int, default=0
        Random seed for deterministic shuffling.
    cache_path : str | Path | None, default=None
        When provided, cache the computed split to this path and reuse it
        on subsequent calls when inputs match.
    checksum_path : str | Path | None, default=None
        When provided, write the dataset checksum to this path for
        reproducibility tracking.
    filter_enabled : bool, default=True
        If True, apply the safety filter prior to splitting.

    Returns
    -------
    (list[str], list[str])
        Train and validation lists.
    """
    from codex_ml.data.loader import apply_safety_filter, load_dataset

    # Load items
    items = load_dataset(Path(texts)) if isinstance(texts, str | Path) else list(texts)

    # Apply safety filter with sanitization mapping
    items = apply_safety_filter(
        items, filter_enabled, lambda t: sanitize_prompt(t, SafetyConfig()).get("text", t)
    )

    # Stable checksum over individual items to detect any content change
    def _checksum(seq: Iterable[str]) -> str:
        h = hashlib.sha256()
        for item in seq:
            h.update(item.encode("utf-8"))
        return h.hexdigest()

    checksum = _checksum(items)
    if checksum_path is not None:
        with contextlib.suppress(Exception):
            Path(checksum_path).write_text(checksum, encoding="utf-8")

    # Try cache (support legacy keys for backward compatibility)
    if cache_path is not None:
        p = Path(cache_path)
        if p.exists():
            with contextlib.suppress(Exception):
                data = json.loads(p.read_text(encoding="utf-8"))
                cached_sig = data.get("checksum") or data.get("sha256") or data.get("data_hash")
                if cached_sig == checksum:
                    return list(data["train"]), list(data["val"])

    # Deterministic shuffle and split
    rng = random.Random(seed)  # noqa: S311 - deterministic shuffle for experiments
    items_shuffled = list(items)
    rng.shuffle(items_shuffled)
    split_idx = int(len(items_shuffled) * float(train_ratio))
    train, val = items_shuffled[:split_idx], items_shuffled[split_idx:]

    # Persist cache
    if cache_path is not None:
        with contextlib.suppress(Exception):
            Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
            Path(cache_path).write_text(
                json.dumps({"train": train, "val": val, "checksum": checksum}, ensure_ascii=False),
                encoding="utf-8",
            )

    return train, val


def stream_texts(
    path: str | Path, chunk_size: int = 4096, encoding: str = "utf-8"
) -> Iterator[str]:
    """Stream text from path in chunks of size chunk_size.

    Parameters
    ----------
    path : str | Path
        Path to a text file.
    chunk_size : int, default=4096
        Number of characters per yielded chunk.
    encoding : str, default="utf-8"
        Text encoding used for reading.

    Yields
    ------
    str
        Chunks of the file as strings.
    """
    p = Path(path)
    with p.open("r", encoding=encoding) as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def _to_token_ids(payload: Any) -> list[int]:
    if isinstance(payload, dict) and "input_ids" in payload:
        return [int(x) for x in payload["input_ids"]]
    if isinstance(payload, list | tuple):
        return [int(x) for x in payload]
    if hasattr(payload, "tolist"):
        return [int(x) for x in payload.tolist()]
    raise TypeError("Tokenizer output must be a sequence of ids or contain 'input_ids'.")


def cache_tokenized(
    dataset: Iterable[str],
    tokenizer: Any,
    cache_path: str | Path,
) -> list[list[int]]:
    """Tokenize ``dataset`` and persist the encoded samples to ``cache_path``.

    The function writes a ``manifest.json`` containing SHA256 hashes for each
    encoded sample. Individual token lists are saved as ``*.pt`` files when
    PyTorch is available; otherwise JSON lines are used as a portable fallback.
    """

    path = Path(cache_path)
    path.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    tokenised: list[list[int]] = []

    for index, text in enumerate(dataset):
        if hasattr(tokenizer, "encode"):
            encoded = tokenizer.encode(text)
        elif callable(tokenizer):
            encoded = tokenizer(text)
        else:  # pragma: no cover - defensive
            raise TypeError("tokenizer must be callable or expose an 'encode' method")

        ids = _to_token_ids(encoded)
        tokenised.append(ids)
        sample_name = f"{index}.pt" if _HAS_TORCH else f"{index}.json"
        sample_path = path / sample_name

        if _HAS_TORCH and torch is not None and hasattr(torch, "save"):
            torch.save(ids, sample_path)  # type: ignore[operator]
        else:
            sample_path.write_text(json.dumps(ids), encoding="utf-8")

        manifest.append(
            {
                "index": index,
                "sha256": hashlib.sha256(json.dumps(ids).encode("utf-8")).hexdigest(),
                "path": sample_name,
            }
        )

    (path / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return tokenised
