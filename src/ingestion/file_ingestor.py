from __future__ import annotations

from pathlib import Path
from typing import Union

from .utils import _detect_encoding


def read_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Return the contents of ``path`` decoded as text.

    Parameters
    ----------
    path:
        Filesystem path to a text file.
    encoding:
        Text encoding used to decode bytes. Pass ``"auto"`` to attempt
        autodetection; defaults to ``"utf-8"``.
    """
    p = Path(path)
    if encoding == "auto":
        encoding = _detect_encoding(p)
    return p.read_text(encoding=encoding)
