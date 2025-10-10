from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Callable


def _fsync_dir(path: Path) -> None:
    """Best-effort directory fsync to persist rename on POSIX."""
    try:
        fd = os.open(str(path), os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except Exception:
        # Not all platforms/filesystems support this; ignore.
        pass


def safe_write_bytes(target: str | Path, producer: Callable[[], bytes]) -> Path:
    """
    Atomically write bytes to `target` using a temp file + fsync + os.replace.
    The producer is called once to generate the content bytes.
    """
    target_p = Path(target)
    target_p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target_p.parent, delete=False) as tf:
        tmp_path = Path(tf.name)
        data = producer()
        tf.write(data)
        tf.flush()
        os.fsync(tf.fileno())
    os.replace(tmp_path, target_p)  # atomic on same filesystem
    _fsync_dir(target_p.parent)
    return target_p


def safe_write_text(target: str | Path, text: str, encoding: str = "utf-8") -> Path:
    return safe_write_bytes(target, lambda: text.encode(encoding))