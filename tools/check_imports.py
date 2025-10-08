#!/usr/bin/env python3
from __future__ import annotations
import importlib
import pkgutil
import sys
import json


def iter_modules(pkg_name: str):
    pkg = importlib.import_module(pkg_name)
    if not hasattr(pkg, "__path__"):
        yield pkg_name
        return
    for m in pkgutil.walk_packages(pkg.__path__, prefix=pkg_name + "."):
        yield m.name


def main(argv=None) -> int:
    target = "codex_ml"
    ok = True
    for name in iter_modules(target):
        try:
            importlib.import_module(name)
            rec = {"module": name, "ok": True}
        except Exception as e:
            ok = False
            rec = {"module": name, "ok": False, "error": f"{type(e).__name__}: {e}"}
        sys.stdout.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
