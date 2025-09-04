#!/usr/bin/env python3
from __future__ import annotations

import re
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools" / "select_precommit.py"
PATTERNS = [re.compile(r"(^|\s)(?:\./)?tools/select_precommit\.py(\s|$)")]


def _is_directly_invoked() -> bool:
    for p in ROOT.rglob("*"):
        if p.is_dir() or ".git" in p.parts:
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        if any(rx.search(text) for rx in PATTERNS):
            # Ignore lines explicitly using "python tools/select_precommit.py"
            if "python tools/select_precommit.py" in text:
                continue
            return True
    return False


def main() -> int:
    if not TARGET.exists():
        return 0
    lines = TARGET.read_text(encoding="utf-8").splitlines(True)
    has_shebang = lines and lines[0].startswith("#!")
    direct = _is_directly_invoked()
    if direct:
        # Ensure shebang and +x.
        if not has_shebang:
            lines.insert(0, "#!/usr/bin/env python3\n")
            TARGET.write_text("".join(lines), encoding="utf-8")
        st = TARGET.stat()
        TARGET.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print("[guard] kept shebang and set +x on tools/select_precommit.py")
    else:
        # Drop shebang if present.
        if has_shebang:
            TARGET.write_text("".join(lines[1:]), encoding="utf-8")
            st = TARGET.stat()
            TARGET.chmod(st.st_mode & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
            print("[guard] dropped shebang (invoked via 'python ...')")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
