from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover - fallback for older versions
    import tomli as tomllib  # type: ignore


PINNED_RE = re.compile(r"^[^=<>!~]+==[^,]+$")


def check(path: Path) -> int:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    deps = data.get("project", {}).get("dependencies", [])
    bad = [d for d in deps if not PINNED_RE.match(d)]
    if bad:
        print("Unpinned dependencies:", ", ".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("pyproject.toml")
    sys.exit(check(target))
