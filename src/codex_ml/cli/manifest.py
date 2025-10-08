from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from typing import Optional

from ..checkpointing.schema_v2 import to_canonical_bytes, sha256_hexdigest

HELP = """\
Usage:
  python -m codex_ml.cli.manifest hash --path PATH [--update-readme README.md]
"""

BADGE_START = "<!-- codex:manifest:start -->"
BADGE_END = "<!-- codex:manifest:end -->"


def _usage() -> int:
    sys.stdout.write(HELP)
    return 0


def _badge(digest: str) -> str:
    # static Shields badge (no runtime fetch)
    # https://shields.io/docs/static-badges
    label = "manifest"
    msg = f"sha256:{digest[:8]}"
    color = "blue"
    return f"![manifest](https://img.shields.io/badge/{label}-{msg}-{color})"


def cmd_hash(path: Path, update_readme: Optional[Path]) -> int:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    digest = sha256_hexdigest(to_canonical_bytes(data))
    sys.stdout.write(digest + "\n")
    if update_readme:
        readme = Path(update_readme).read_text(encoding="utf-8")
        block = f"{BADGE_START}\n{_badge(digest)}\n{BADGE_END}"
        if BADGE_START in readme and BADGE_END in readme:
            pattern = re.compile(
                re.escape(BADGE_START) + r".*?" + re.escape(BADGE_END),
                flags=re.DOTALL,
            )
            new = pattern.sub(block, readme)
        else:
            new = readme + "\n\n" + block + "\n"
        Path(update_readme).write_text(new, encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] != "hash":
        return _usage()
    # naive argv parse to avoid external deps
    path = None
    update = None
    i = 1
    while i < len(argv):
        if argv[i] in ("--path", "-p") and i + 1 < len(argv):
            path = Path(argv[i + 1])
            i += 2
        elif argv[i] == "--update-readme" and i + 1 < len(argv):
            update = Path(argv[i + 1])
            i += 2
        else:
            return _usage()
    if not path:
        return _usage()
    return cmd_hash(path, update)


if __name__ == "__main__":
    raise SystemExit(main())
