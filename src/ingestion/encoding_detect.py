from __future__ import annotations
from pathlib import Path
from typing import Optional, Union

try:
    from charset_normalizer import from_bytes as _cn_from_bytes  # preferred
except Exception:  # pragma: no cover
    _cn_from_bytes = None

try:
    import chardet as _chardet  # fallback
except Exception:  # pragma: no cover
    _chardet = None


def autodetect_encoding(path: Union[str, Path], default: str = "utf-8", sample_size: int = 131072) -> str:
    """Return best-effort text encoding for a file at *path*.

    Resolution order (deterministic): charset-normalizer → chardet → default.
    This function never raises; it returns *default* if detection fails.
    """
    p = Path(path)
    try:
        data = p.read_bytes()[: max(1024, int(sample_size))]
    except Exception:
        return default

    # 1) charset-normalizer (preferred)
    if _cn_from_bytes is not None:
        try:
            result = _cn_from_bytes(data)
            best = result.best() if result is not None else None
            enc: Optional[str] = getattr(best, "encoding", None)
            if enc:
                return enc
        except Exception:
            pass

    # 2) chardet (fallback)
    if _chardet is not None:
        try:
            res = _chardet.detect(data) or {}
            enc = res.get("encoding")
            if enc:
                return enc
        except Exception:
            pass

    # 3) default
    return default
