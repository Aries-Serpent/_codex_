from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Union

from .utils import _detect_encoding


def load_csv(
    path: Union[str, Path], *, encoding: str = "utf-8", **kwargs
) -> List[list[str]]:
    """Load CSV rows from ``path`` into a list.

    Parameters
    ----------
    path:
        Filesystem path to a CSV file.
    encoding:
        Text encoding used to decode bytes. Pass ``"auto"`` to attempt
        autodetection; defaults to ``"utf-8"``.
    **kwargs:
        Additional arguments forwarded to :func:`csv.reader`.
    """
    p = Path(path)
    if encoding == "auto":
        encoding = _detect_encoding(p)
    with p.open("r", encoding=encoding, newline="") as fh:
        reader = csv.reader(fh, **kwargs)
        return list(reader)
