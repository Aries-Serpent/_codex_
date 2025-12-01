#!/usr/bin/env python
"""Capture a lightweight environment snapshot for _codex_.

This tool focuses on:
- Python version and executable.
- Platform information.
- Key env vars (filtered to CODEX_*, CUDA_*, and a small allowlist).
- Installed package hints for core dependencies (yaml, pytest, numpy, torch).

Outputs:
- codex_env_snapshot.json
- codex_env_snapshot.md

The JSON is machine-readable for automation; the Markdown is human-friendly.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _collect_env_vars() -> Dict[str, str]:
    allow_prefixes = ("CODEX_", "CUDA_", "PYTORCH_", "HF_", "TRANSFORMERS_")
    allow_exact = {"PYTHONHASHSEED"}
    result: Dict[str, str] = {}
    for k, v in os.environ.items():
        if k in allow_exact or any(k.startswith(p) for p in allow_prefixes):
            result[k] = v
    return result


def _check_import(name: str) -> Dict[str, Any]:
    info = {"available": False, "version": None}
    if name in sys.modules:
        mod = sys.modules[name]
    else:
        spec = __import__(name)
        mod = spec
    info["available"] = True
    info["version"] = getattr(mod, "__version__", None)
    return info


def _build_snapshot() -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {
        "python": {
            "version": sys.version,
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "env": _collect_env_vars(),
        "deps": {},
    }

    for dep in ("yaml", "pytest", "numpy", "torch"):
        try:
            snapshot["deps"][dep] = _check_import(dep)
        except Exception:
            snapshot["deps"][dep] = {"available": False, "version": None}
    return snapshot


def _write_json(path: Path, snapshot: Dict[str, Any]) -> None:
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, snapshot: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# _codex_ Environment Snapshot\n")
    py = snapshot["python"]
    plat = snapshot["platform"]
    lines.append("## Python\n")
    lines.append(f"- Version: `{py['version']}`")
    lines.append(f"- Executable: `{py['executable']}`\n")

    lines.append("## Platform\n")
    lines.append(f"- System: `{plat['system']}`")
    lines.append(f"- Release: `{plat['release']}`")
    lines.append(f"- Machine: `{plat['machine']}`\n")

    lines.append("## Dependencies\n")
    for name, info in snapshot.get("deps", {}).items():
        status = "available" if info.get("available") else "missing"
        ver = info.get("version") or "unknown"
        lines.append(f"- `{name}`: {status}, version={ver}")
    lines.append("")

    env = snapshot.get("env", {})
    if env:
        lines.append("## Selected Environment Variables\n")
        for k in sorted(env.keys()):
            lines.append(f"- `{k}` = `{env[k]}`")
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Capture _codex_ environment snapshot.")
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_env_snapshot.json",
        help="Path to JSON output (default: codex_env_snapshot.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_env_snapshot.md",
        help="Path to Markdown output (default: codex_env_snapshot.md).",
    )
    args = parser.parse_args(argv)

    snapshot = _build_snapshot()
    json_path = Path(args.json_out).expanduser().resolve()
    md_path = Path(args.md_out).expanduser().resolve()
    _write_json(json_path, snapshot)
    _write_markdown(md_path, snapshot)
    print(f"Wrote environment snapshot JSON to {json_path}")
    print(f"Wrote environment snapshot Markdown to {md_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
