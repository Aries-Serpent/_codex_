# BEGIN: CODEX_CHECKSUMS
from __future__ import annotations

import hashlib
import os
from pathlib import Path


def sha256_dir(path: Path) -> str:
    h = hashlib.sha256()
    for root, _, files in os.walk(path):
        for fn in sorted(files):
            fp = Path(root) / fn
            h.update(fp.name.encode())
            h.update(fp.read_bytes())
    return h.hexdigest()


def write_checksum(path: Path):
    (path / "checksum.sha256").write_text(sha256_dir(path))


# END: CODEX_CHECKSUMS
