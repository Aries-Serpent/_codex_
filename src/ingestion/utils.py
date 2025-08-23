from __future__ import annotations

from pathlib import Path
from typing import Union

from .encoding_detect import autodetect_encoding


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Read a text file and return its content as a string.

    Parameters
    ----------
    path:
        Filesystem path to the text file.
    encoding:
        Text encoding used to decode bytes. Pass ``"auto"`` to attempt
        autodetection; defaults to ``"utf-8"``.
    """
    p = Path(path)
    if encoding == "auto":
        encoding = autodetect_encoding(p)
    return p.read_text(encoding=encoding)
