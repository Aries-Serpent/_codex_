#!/usr/bin/env python
"""Validate `_codex_` configuration files under `conf/`.

This tool:

- Recursively scans a config directory (default: `conf/`).
- For each `*.yaml` file:
  - Parses YAML.
  - Attempts to construct `CodexConfig` via `codex_ml.config.schema.from_dict`.
- Emits:
  - A JSON summary (`codex_config_validation_report.json`).
  - A Markdown summary (`codex_config_validation_report.md`).
- Returns a non-zero exit code if any file fails validation.

The intent is to run this as a **local gate** before invoking more
expensive workflows.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from codex_ml.config import schema as cfg_schema


@dataclass
class FileResult:
    path: str
    ok: bool
    error: Optional[str]


def _iter_yaml_files(root: Path) -> List[Path]:
    if not root.exists():
        return []
    files: List[Path] = []
    for p in root.rglob("*.yaml"):
        if p.is_file():
            files.append(p)
    return sorted(files)


def _validate_file(path: Path) -> FileResult:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return FileResult(path=str(path), ok=False, error=f"YAML parse error: {e}")

    try:
        cfg_schema.from_dict(raw)
    except cfg_schema.ConfigValidationError as e:
        return FileResult(path=str(path), ok=False, error=f"Config validation error: {e}")
    except Exception as e:  # pragma: no cover
        return FileResult(path=str(path), ok=False, error=f"Unexpected error: {e}")

    return FileResult(path=str(path), ok=True, error=None)


def _write_json(path: Path, results: List[FileResult]) -> None:
    data = {
        "total_files": len(results),
        "num_ok": sum(1 for r in results if r.ok),
        "num_failed": sum(1 for r in results if not r.ok),
        "files": [asdict(r) for r in results],
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(path: Path, results: List[FileResult]) -> None:
    total = len(results)
    num_ok = sum(1 for r in results if r.ok)
    num_failed = sum(1 for r in results if not r.ok)

    lines: List[str] = []
    lines.append("# _codex_ Config Validation Report\n")
    lines.append(f"- Total files: **{total}**")
    lines.append(f"- OK : **{num_ok}**")
    lines.append(f"- Failed : **{num_failed}**\n")

    if not results:
        lines.append("No YAML configuration files were found.\n")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    lines.append("## File Results\n")
    lines.append("| File | Status | Error |")
    lines.append("| ---- | ------ | ----- |")

    for r in results:
        status = "OK" if r.ok else "FAILED"
        err = r.error or ""
        lines.append(f"| `{r.path}` | {status} | {err} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate `_codex_` YAML configs against the config schema."
    )
    parser.add_argument(
        "--conf-dir",
        type=str,
        default="conf",
        help="Config directory to scan (default: conf).",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="codex_config_validation_report.json",
        help="JSON report path (default: codex_config_validation_report.json).",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="codex_config_validation_report.md",
        help="Markdown report path (default: codex_config_validation_report.md).",
    )
    args = parser.parse_args(argv)

    conf_root = Path(args.conf_dir).expanduser().resolve()
    yaml_files = _iter_yaml_files(conf_root)
    results = [_validate_file(p) for p in yaml_files]

    base_dir = conf_root.parent if Path(args.conf_dir).is_dir() else Path.cwd()
    json_out_raw = Path(args.json_out).expanduser()
    md_out_raw = Path(args.md_out).expanduser()

    json_out = json_out_raw if json_out_raw.is_absolute() else base_dir / json_out_raw
    md_out = md_out_raw if md_out_raw.is_absolute() else base_dir / md_out_raw
    _write_json(json_out, results)
    _write_markdown(md_out, results)

    num_failed = sum(1 for r in results if not r.ok)
    if num_failed > 0:
        print(f"{num_failed} config files failed validation.")
        return 1

    print(f"Validated {len(results)} config files successfully.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
