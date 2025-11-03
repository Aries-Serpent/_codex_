#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List

RE_THEME = re.compile(r'href=["\'][^"\']*theme\.css["\']', re.IGNORECASE)
RE_PRINT = re.compile(r'href=["\'][^"\']*print\.css["\']', re.IGNORECASE)


def lint_file(p: Path) -> List[str]:
    text = p.read_text(encoding="utf-8", errors="ignore")
    errs: List[str] = []
    if not RE_THEME.search(text):
        errs.append("missing.theme.css")
    if not RE_PRINT.search(text):
        errs.append("missing.print.css")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lint HTML templates for required CSS includes (theme.css, print.css)")
    ap.add_argument("--dir", default="docs/templates/status", help="Directory to scan for .html files")
    args = ap.parse_args(argv)

    root = Path(args.dir)
    files = list(root.glob("*.html"))
    had_err = False
    for f in files:
        errs = lint_file(f)
        if errs:
            print(f"[FAIL] {f}: {', '.join(errs)}")
            had_err = True
        else:
            print(f"[OK] {f}")
    if not files:
        print("[WARN] No .html templates found")
    return 1 if had_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
