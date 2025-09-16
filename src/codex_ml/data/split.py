"""Dataset splitting utilities with manifest and checksum logging.

This module provides a deterministic ``train/val/test`` split helper that also
emits metadata describing the split. The metadata captures the seed used for
shuffling, a hashed dataset identifier, per-split sizes, and checksums that can
be stored alongside other run artefacts for reproducibility audits.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

DEFAULT_MANIFEST_NAME = "split_manifest.json"
DEFAULT_CHECKSUMS_NAME = "split_checksums.json"
MANIFEST_SCHEMA = "https://codexml.ai/schemas/dataset_split_manifest.v1"
MANIFEST_VERSION = "v1"


def _hash_identifier(identifier: str) -> str:
    """Return a SHA256 hash for ``identifier`` as a hexadecimal string."""

    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def _json_ready(value: Any) -> Any:
    """Best-effort conversion to JSON-serialisable primitives."""

    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _split_checksum(dataset_hash: str, split: str, indices: Sequence[int]) -> str:
    """Compute a checksum for ``indices`` scoped to ``dataset_hash``."""

    payload = f"{dataset_hash}:{split}:{','.join(str(i) for i in indices)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SplitMetadata:
    """Metadata describing a split for the JSON manifest."""

    split: str
    indices: List[int]
    checksum: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "split": self.split,
            "indices": list(self.indices),
            "size": len(self.indices),
            "checksum": self.checksum,
        }


def _build_manifest(
    *,
    dataset_name: Optional[str],
    dataset_identifier: str,
    dataset_hash: str,
    seed: int,
    train: SplitMetadata,
    val: SplitMetadata,
    test: SplitMetadata,
    fractions: Mapping[str, float],
) -> Dict[str, Any]:
    """Assemble the manifest payload."""

    manifest = {
        "$schema": MANIFEST_SCHEMA,
        "schema_version": MANIFEST_VERSION,
        "seed": int(seed),
        "dataset": {
            "name": dataset_name,
            "raw_id": dataset_identifier,
            "hashed_id": dataset_hash,
            "size": len(train.indices) + len(val.indices) + len(test.indices),
        },
        "fractions": {k: float(v) for k, v in fractions.items()},
        "splits": {
            "train": train.as_dict(),
            "val": val.as_dict(),
            "test": test.as_dict(),
        },
    }
    return manifest


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True), encoding="utf-8")


def _write_checksums(path: Path, splits: Iterable[SplitMetadata]) -> None:
    data = {meta.split: meta.checksum for meta in splits}
    _write_json(path, data)


def train_val_test_split(
    dataset: Sequence[Any],
    *,
    val_frac: float = 0.1,
    test_frac: float = 0.1,
    seed: int = 0,
    dataset_id: Optional[str] = None,
    manifest_path: Optional[str | Path] = None,
    artifact_dir: Optional[str | Path] = None,
) -> Tuple[List[Any], List[Any], List[Any]]:
    """Split ``dataset`` into train/val/test subsets.

    Parameters
    ----------
    dataset:
        Sequence of items to split.
    val_frac:
        Fraction of examples to allocate to the validation split.
    test_frac:
        Fraction of examples to allocate to the test split.
    seed:
        Random seed used to shuffle prior to splitting.
    dataset_id:
        Optional identifier for the dataset. When omitted the function attempts
        to use ``dataset.name`` if available, otherwise defaults to a generic
        label.
    manifest_path:
        Location for the JSON manifest describing the split. When omitted the
        manifest is written to ``artifact_dir / split_manifest.json`` if an
        artefact directory is provided.
    artifact_dir:
        Directory for auxiliary artefacts such as the checksum file. Defaults to
        ``manifest_path.parent`` when not explicitly provided.

    Returns
    -------
    Tuple[List[Any], List[Any], List[Any]]
        Train, validation and test subsets in that order.
    """

    if not 0.0 <= val_frac < 1.0:
        raise ValueError("val_frac must be in [0, 1)")
    if not 0.0 <= test_frac < 1.0:
        raise ValueError("test_frac must be in [0, 1)")
    if val_frac + test_frac >= 1.0:
        raise ValueError("val_frac + test_frac must be < 1")

    n = len(dataset)
    indices = list(range(n))
    rng = random.Random(int(seed))
    rng.shuffle(indices)

    n_test = int(n * test_frac)
    n_val = int(n * val_frac)
    test_idx = indices[:n_test]
    val_idx = indices[n_test : n_test + n_val]
    train_idx = indices[n_test + n_val :]

    def _subset(idxs: Sequence[int]) -> List[Any]:
        return [dataset[i] for i in idxs]

    dataset_name = getattr(dataset, "name", None)
    raw_identifier = dataset_id or dataset_name or "dataset"
    dataset_hash = _hash_identifier(str(raw_identifier))

    train_split = SplitMetadata(
        "train", list(train_idx), _split_checksum(dataset_hash, "train", train_idx)
    )
    val_split = SplitMetadata("val", list(val_idx), _split_checksum(dataset_hash, "val", val_idx))
    test_split = SplitMetadata(
        "test", list(test_idx), _split_checksum(dataset_hash, "test", test_idx)
    )

    manifest = _build_manifest(
        dataset_name=dataset_name,
        dataset_identifier=str(raw_identifier),
        dataset_hash=dataset_hash,
        seed=int(seed),
        train=train_split,
        val=val_split,
        test=test_split,
        fractions={
            "train": 1.0 - float(val_frac) - float(test_frac),
            "val": float(val_frac),
            "test": float(test_frac),
        },
    )

    art_dir = Path(artifact_dir) if artifact_dir is not None else None
    manifest_target = Path(manifest_path) if manifest_path is not None else None
    if art_dir is None and manifest_target is not None:
        art_dir = manifest_target.parent

    if manifest_target is None and art_dir is not None:
        manifest_target = art_dir / DEFAULT_MANIFEST_NAME

    if manifest_target is not None:
        _write_json(Path(manifest_target), manifest)

    if art_dir is not None:
        checksum_path = art_dir / DEFAULT_CHECKSUMS_NAME
        _write_checksums(checksum_path, [train_split, val_split, test_split])

    return _subset(train_idx), _subset(val_idx), _subset(test_idx)


__all__ = [
    "train_val_test_split",
    "SplitMetadata",
    "DEFAULT_MANIFEST_NAME",
    "DEFAULT_CHECKSUMS_NAME",
]
