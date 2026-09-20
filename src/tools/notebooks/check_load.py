#!/usr/bin/env python3
"""Dry-load notebooks to ensure they parse with nbformat."""

from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "artifacts" / "notebook_checks"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SKIP_PARTS = {
    ".git",
    ".nox",
    ".tox",
    "__pycache__",
    "artifacts",
    "build",
    "dist",
    "logs",
    "mlruns",
    "nox_sessions",
    "site-packages",
}


def _should_skip(path: pathlib.Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def main() -> None:
    try:
        import nbformat  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        (OUTPUT_DIR / "nb_load_check.json").write_text(
            json.dumps({"status": "nbformat-missing", "error": str(exc)}, indent=2),
            encoding="utf-8",
        )
        print("[nb] nbformat missing; recorded status")
        return

    results: dict[str, dict[str, str]] = {}
    for notebook in ROOT.rglob("*.ipynb"):
        if _should_skip(notebook):
            continue
        try:
            nbformat.read(str(notebook), as_version=4)
        except Exception as exc:  # pragma: no cover - best-effort log
            results[str(notebook)] = {"load": "error", "msg": str(exc)}
        else:
            results[str(notebook)] = {"load": "ok"}
    (OUTPUT_DIR / "nb_load_check.json").write_text(
        json.dumps(results, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print("[nb] DONE")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
