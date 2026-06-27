"""Simple dataset scaffolding for _codex_.

This module defines a small, in-memory dataset wrapper that leverages the
existing tokenization and deterministic ordering helpers to provide a
minimal, testable surface for training and evaluation.

It is intentionally small and does not depend on external libraries such
as torch or numpy.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from codex_ml.data import dataloader  # type: ignore[attr-defined]
from codex_ml.tokenization import base as token_base


@dataclass
class Sample:
    text: str
    label: int


@dataclass
class EncodedSample:
    tokens: list[int]
    label: int


class SimpleDataset:
    """Tiny dataset wrapper holding a list of (text, label) samples."""

    def __init__(self, samples: Sequence[Sample], seed: int = 0) -> None:
        self._samples = list(samples)
        self._seed = seed

    def __len__(self) -> int:
        return len(self._samples)

    def encoded(self) -> list[EncodedSample]:
        """Return a deterministically ordered list of encoded samples."""
        indices = list(range(len(self._samples)))
        ordered_indices = dataloader.deterministic_order(indices, seed=self._seed)
        result: list[EncodedSample] = []
        for idx in ordered_indices:
            s = self._samples[idx]
            tokens = token_base.tokenize_example(s.text)
            result.append(EncodedSample(tokens=tokens, label=s.label))
        return result
