from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List


def _sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    """Compute SHA256 for a file in streaming chunks."""
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def manifest_for_paths(
    paths: Iterable[str | Path],
    destination: str | Path | None = None,
) -> List[Dict[str, object]]:
    """Build (and optionally persist) manifest rows for ``paths``.

    Args:
        paths: Iterable of filesystem paths to hash.
        destination: When provided, write JSON Lines rows to this path. Parent
            directories are created automatically.

    Returns:
        List of manifest row dictionaries containing ``path``, ``sha256`` and
        ``bytes`` entries.
    """

    rows: List[Dict[str, object]] = []
    for raw in paths:
        p = Path(raw)
        rows.append(
            {
                "path": str(p),
                "sha256": _sha256_file(p),
                "bytes": p.stat().st_size,
            }
        )

    if destination is not None:
        out_path = Path(destination)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join(json.dumps(row, sort_keys=True) for row in rows)
        out_path.write_text(content, encoding="utf-8")

    return rows
