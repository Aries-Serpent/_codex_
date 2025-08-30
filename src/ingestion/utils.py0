from __future__ import annotations

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, TypeVar, Union

import numpy as np

T = TypeVar("T")


def seeded_shuffle(data: Sequence[T], seed: int) -> List[T]:
    """Return a deterministically shuffled copy of ``data`` using *seed*.

    NumPy's ``Generator`` is used to ensure reproducible permutations across
    platforms, matching scikit-learn's ``random_state`` semantics.
    """

    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(data))
    return [data[i] for i in idx]


def read_text(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Read a text file with optional encoding auto-detection.

    When ``encoding="auto"`` the function attempts to detect the encoding using
    ``charset_normalizer``. Detection is best-effort and falls back to UTF-8 when
    the library is unavailable or no best guess is produced.
    """

    p = Path(path)
    enc = encoding
    if encoding == "auto":
        try:
            from charset_normalizer import from_path

            best = from_path(p).best()
            enc = best.encoding if best and best.encoding else "utf-8"
        except Exception:
            enc = "utf-8"
    return p.read_text(encoding=enc)


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Backward compatible alias for :func:`read_text`."""

    return read_text(path, encoding=encoding)
