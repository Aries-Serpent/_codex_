from __future__ import annotations

from pathlib import Path
from typing import Union

from .io_text import _detect_encoding, read_text, seeded_shuffle

__all__ = ["read_text", "seeded_shuffle", "read_text_file", "_detect_encoding"]


def read_text_file(path: Union[str, Path], *, encoding: str = "utf-8") -> str:
    """Backward-compatible alias for :func:`read_text`.

    This wrapper attempts to call the underlying `read_text` with an explicit
    encoding argument for backward compatibility with call sites that pass
    encoding. If the underlying implementation does not accept an `encoding`
    parameter (older variants), the wrapper will fall back to calling it
    without that argument. Any other exceptions are surfaced as RuntimeError
    with contextual information.
    """
    try:
        return read_text(path, encoding=encoding)
    except TypeError:
        # Underlying read_text may not accept an encoding parameter.
        try:
            return read_text(path)
        except Exception as exc:
            raise RuntimeError(f"Failed to read text from {path!s}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to read text from {path!s}") from exc
