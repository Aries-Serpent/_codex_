#!/usr/bin/env python3
"""Move functional_training.py into codex package and rewrite imports."""
import pathlib
import re
import shutil
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def move_module() -> bool:
    src = REPO_ROOT / "functional_training.py"
    dest = REPO_ROOT / "src" / "codex" / "training.py"
    if not src.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    return True


def rewrite_imports() -> None:
    targets = []
    for base in ("src", "tests"):
        path = REPO_ROOT / base
        if path.exists():
            targets.extend(path.rglob("*.py"))
    for file in targets:
        text = file.read_text(encoding="utf-8")
        new_text = re.sub(r"\bfunctional_training\b", "codex.training", text)
        if new_text != text:
            file.write_text(new_text, encoding="utf-8")


def main() -> None:
    if move_module():
        rewrite_imports()
    else:
        print("functional_training.py not found; nothing to do", file=sys.stderr)


if __name__ == "__main__":
    main()
