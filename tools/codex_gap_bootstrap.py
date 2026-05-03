#!/usr/bin/env python
"""codex_gap_bootstrap.py

Helper utility to bootstrap work for a specific gap from codex_gap_registry.yaml.

Given a gap id, this script can:
- Locate the gap entry in codex_gap_registry.yaml.
- Create a docs stub under docs/gaps/<gap_id>.md if it does not exist.
- Print suggestions for where to place code and tests based on the capability.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


def load_registry(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with `pip install pyyaml`.")
    if not path.exists():
        raise FileNotFoundError(f"Registry not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or "gaps" not in data:
        raise ValueError(f"Unexpected registry structure in {path}")
    return data


def find_gap(registry: dict[str, Any], gap_id: str) -> Optional[dict[str, Any]]:
    for item in registry.get("gaps", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("id")) == gap_id:
            return item
    return None


def ensure_docs_stub(repo_root: Path, gap_id: str, gap: dict[str, Any]) -> Path:
    docs_root = repo_root / "docs" / "gaps"
    docs_root.mkdir(parents=True, exist_ok=True)
    doc_path = docs_root / f"{gap_id}.md"
    if doc_path.exists():
        return doc_path
    capability = gap.get("capability", "general")
    description = gap.get("description", "")
    status = gap.get("status", "")
    doc_path.write_text(
        (
            f"# Gap: {gap_id}\n\n"
            f"- Capability: `{capability}`\n"
            f"- Status: `{status}`\n\n"
            "## Description\n\n"
            f"{description}\n\n"
            "## Notes\n\n"
            "- TODO: Fill in design notes, constraints, and acceptance criteria.\n"
            "- TODO: Link to relevant modules, tests, and audit sections.\n"
        ),
        encoding="utf-8",
    )
    return doc_path


def suggest_paths_for_gap(gap: dict[str, Any]) -> dict[str, str]:
    capability = str(gap.get("capability", "general")).lower()
    suggestions: dict[str, str] = {}
    if "token" in capability:
        suggestions["code"] = "src/codex_ml/tokenization/"
        suggestions["tests"] = "tests/codex_ml/test_tokenization_*.py"
    elif "train" in capability:
        suggestions["code"] = "src/codex_ml/training/"
        suggestions["tests"] = "tests/codex_ml/test_training_*.py"
    elif "deploy" in capability:
        suggestions["code"] = "src/codex_ml/deploy/"
        suggestions["tests"] = "tests/codex_ml/test_deploy_*.py"
    else:
        suggestions["code"] = "src/codex_ml/"
        suggestions["tests"] = "tests/codex_ml/"
    return suggestions


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bootstrap work for a gap id.")
    p.add_argument("gap_id", help="Gap id as recorded in codex_gap_registry.yaml.")
    p.add_argument(
        "--registry",
        type=str,
        default="codex_gap_registry.yaml",
        help="Path to codex_gap_registry.yaml (default: codex_gap_registry.yaml).",
    )
    p.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    registry_path = repo_root / args.registry
    registry = load_registry(registry_path)
    gap = find_gap(registry, args.gap_id)
    if gap is None:
        raise SystemExit(f"Gap id not found in registry: {args.gap_id}")
    doc_path = ensure_docs_stub(repo_root, args.gap_id, gap)
    suggestions = suggest_paths_for_gap(gap)
    print(f"Created/updated docs stub at: {doc_path}")
    print("Suggested locations:")
    for kind, path in suggestions.items():
        print(f"- {kind}: {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
