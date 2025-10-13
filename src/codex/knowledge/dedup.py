from __future__ import annotations

import re
from collections.abc import Iterable

_WORD = re.compile(r"[A-Za-z0-9_]+")


def _tokens(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def simhash(text: str, bits: int = 64) -> int:
    """Compute a lightweight SimHash fingerprint for ``text``."""

    weights = [0] * bits
    for token in _tokens(text):
        value = hash(token)
        for idx in range(bits):
            if (value >> idx) & 1:
                weights[idx] += 1
            else:
                weights[idx] -= 1
    fingerprint = 0
    for idx, weight in enumerate(weights):
        if weight >= 0:
            fingerprint |= 1 << idx
    return fingerprint


def hamming(a: int, b: int) -> int:
    """Return the Hamming distance between two SimHash fingerprints."""

    return (a ^ b).bit_count()


def dedup_records(texts: Iterable[str], *, threshold: int = 3) -> list[int]:
    """Return indices of records to keep after removing near-duplicates.

    Entries whose SimHash differs by ``threshold`` bits or fewer from an
    earlier record are treated as duplicates and filtered out.
    """

    keep_indices: list[int] = []
    fingerprints: list[int] = []
    for idx, text in enumerate(texts):
        fp = simhash(text)
        if all(hamming(fp, existing) > threshold for existing in fingerprints):
            keep_indices.append(idx)
            fingerprints.append(fp)
    return keep_indices


__all__ = ["dedup_records", "hamming", "simhash"]
