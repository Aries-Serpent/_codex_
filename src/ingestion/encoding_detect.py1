from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

try:
    import chardet as _chardet  # preferred
except Exception:  # pragma: no cover
    _chardet = None

try:
    from charset_normalizer import from_bytes as _cn_from_bytes  # fallback
except Exception:  # pragma: no cover
    _cn_from_bytes = None


def autodetect_encoding(
    path: Union[str, Path], default: str = "utf-8", sample_size: int = 131072
) -> str:
    """Return best-effort text encoding for a file at *path*.
    Resolution order (deterministic): BOM → chardet → charset-normalizer →
    heuristic trial → default.  This function never raises; it returns
    *default* if detection fails.
    """
    p = Path(path)
    try:
        data = p.read_bytes()[: max(1024, int(sample_size))]
    except Exception:
        return default

    # 0) byte-order marks for UTF variants
    if data.startswith(b"\xff\xfe\x00\x00") or data.startswith(b"\x00\x00\xfe\xff"):
        return "utf-32"
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return "utf-16"
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8"

    safe = {
        "utf-8",
        "utf-16",
        "utf-32",
        "cp1252",
        "windows-1252",
        "iso-8859-1",
    }

    def _norm(e: Optional[str]) -> Optional[str]:
        return e.lower().replace("_", "-") if e else None

    # 1) chardet (preferred)
    if _chardet is not None:
        try:
            res = _chardet.detect(data) or {}
            enc = _norm(res.get("encoding"))
        except Exception:
            enc = None
        if enc in safe:
            return "cp1252" if enc == "windows-1252" else enc

    # 2) charset-normalizer (fallback)
    if _cn_from_bytes is not None:
        try:
            result = _cn_from_bytes(data)
            best = result.best() if result is not None else None
            enc = _norm(getattr(best, "encoding", None))
        except Exception:
            enc = None
        if enc in safe:
            return "cp1252" if enc == "windows-1252" else enc

    # 3) simple heuristics
    for enc in ("utf-8", "cp1252", "iso-8859-1"):
        try:
            data.decode(enc)
            decoded = True
        except (UnicodeDecodeError, LookupError):
            decoded = False
        if decoded:
            return enc

    # 4) default
    return default
