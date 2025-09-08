#!/usr/bin/env python3
"""
Export environment and provenance information to stdout or a file.

This utility collects a lightweight, privacy-preserving summary of the current
runtime for reproducibility, including Python/platform versions, optional torch
and numpy versions, and the current Git commit hash if available.

Usage:
  python scripts/export_env_info.py --output .codex/env.json
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Try to use the repository's provenance utility when available
try:
    from codex_ml.utils.provenance import (
        environment_summary as _prov_environment_summary,  # type: ignore
    )
except Exception:
    _prov_environment_summary = None  # type: ignore[assignment]


def _git_commit_fallback() -> Optional[str]:
    try:
        # Walk up to find a git root
        p = Path(__file__).resolve()
        for parent in [p] + list(p.parents):
            if (parent / ".git").exists():
                return subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=parent, text=True
                ).strip()
        # fallback to CWD
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def _minimal_env_summary() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "python": sys.version,
        "platform": platform.platform(),
    }
    try:
        import torch  # type: ignore

        info["torch"] = getattr(torch, "__version__", None)
        info["cuda"] = (
            torch.version.cuda if hasattr(torch, "version") and torch.cuda.is_available() else None  # type: ignore[attr-defined]
        )
    except Exception:
        pass
    try:
        import numpy as np  # type: ignore

        info["numpy"] = getattr(np, "__version__", None)
    except Exception:
        pass
    gc = _git_commit_fallback()
    if gc:
        info["git_commit"] = gc
    return info


def collect_env() -> Dict[str, Any]:
    # Prefer rich environment summary from provenance utils
    try:
        if callable(_prov_environment_summary):  # type: ignore[truthy-bool]
            env = _prov_environment_summary()  # type: ignore[misc]
            if isinstance(env, dict):
                env.setdefault("git_commit", env.get("git_commit") or _git_commit_fallback())
                return env
    except Exception:
        pass
    return _minimal_env_summary()


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Export environment/provenance info")
    ap.add_argument("--output", "-o", type=str, default="", help="Output JSON file path")
    args = ap.parse_args(argv)

    env = collect_env()

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(env, indent=2, sort_keys=True), encoding="utf-8")
    else:
        print(json.dumps(env, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
