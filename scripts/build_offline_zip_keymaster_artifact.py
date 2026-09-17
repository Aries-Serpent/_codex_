#!/usr/bin/env python3
"""Build a repo-local standalone offline ZIP keymaster artifact.

The repo's monolithic project metadata already contains the entry points for the
keymaster package, but the minimal downloadable artifact is intentionally kept
separate so it can be built and staged locally without dragging in the whole ML
toolchain or publishing to an external index.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING_DIR = ROOT / "staging" / "offline_zip_keymaster"
OUT_DIR = STAGING_DIR / "dist"


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    if not STAGING_DIR.exists():
        raise FileNotFoundError(f"Missing staging project directory: {STAGING_DIR}")

    if shutil.which("python"):
        python_exe = sys.executable
    else:
        python_exe = "python"

    try:
        import build  # noqa: F401
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The offline ZIP keymaster artifact build requires the local 'build' package. "
            "Install it from the local wheelhouse or a trusted offline source before running this script."
        ) from exc

    _run([python_exe, "-m", "build", "--wheel", "--sdist", "--outdir", str(OUT_DIR)], STAGING_DIR)

    print(f"Offline ZIP keymaster artifact staged at: {OUT_DIR}")
    for artifact in sorted(OUT_DIR.iterdir()):
        print(f"  - {artifact.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
