from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_EXT_TO_MIME = {
    ".py": "text/x-python",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".json": "application/json",
    ".csv": "text/csv",
    ".yml": "text/yaml",
    ".yaml": "text/yaml",
    ".sql": "application/sql",
    ".js": "application/javascript",
    ".ts": "application/typescript",
    ".sh": "text/x-shellscript",
}

_EXT_TO_LANG = {
    ".py": "python",
    ".md": "markdown",
    ".txt": "text",
    ".json": "json",
    ".csv": "csv",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".sql": "sql",
    ".js": "javascript",
    ".ts": "typescript",
    ".sh": "shell",
}


@dataclass
class FileMeta:
    path: str
    size_bytes: int
    mtime_epoch: float
    mime: str
    lang: str
    sloc: int


def _sloc_of_bytes(b: bytes) -> int:
    """Very small SLoC heuristic for textual files."""
    try:
        text = b.decode("utf-8", "ignore")
    except Exception:
        return 0
    sloc = 0
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        sloc += 1
    return sloc


def detect_mime_lang(p: Path) -> tuple[str, str]:
    ext = p.suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream"), _EXT_TO_LANG.get(ext, "binary")


def stat_file(p: Path) -> FileMeta:
    st = p.stat()
    mime, lang = detect_mime_lang(p)
    try:
        b = p.read_bytes()
    except Exception:
        b = b""
    return FileMeta(
        path=p.as_posix(),
        size_bytes=st.st_size,
        mtime_epoch=st.st_mtime,
        mime=mime,
        lang=lang,
        sloc=_sloc_of_bytes(b),
    )
