from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

from .encoding_detect import autodetect_encoding


def load_json(path: Union[str, Path], *, encoding: str = "utf-8") -> Any:
    """Load JSON data from ``path``.

    Parameters
    ----------
    path:
        Filesystem path to a JSON document.
    encoding:
        Text encoding used to decode bytes. Pass ``"auto"`` to attempt
        autodetection; defaults to ``"utf-8"``.
    """
    p = Path(path)
    if encoding == "auto":
        encoding = autodetect_encoding(p)
    with p.open("r", encoding=encoding) as fh:
        return json.load(fh)
