#!/usr/bin/env python3
"""
Repo audit scanner for Codex Environment. Run locally in your Codex environment.

Usage:
  python3 scripts/repo_audit.py --format markdown --output audit.md

Outputs:
  - machine-readable JSON summary (audit.json)
  - human-readable markdown (audit.md)
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List

ROOT = Path(".").resolve()
STUB_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"NotImplementedError",
    r"\bpass\s*#\s*TODO\b",
    r"\bXXX\b",
]

SEARCH_PATTERNS = [
    ("requirements", ["requirements.txt", "pyproject.toml", "Pipfile", "environment.yml"]),
    ("docker", ["Dockerfile"]),
    ("notebooks", ["*.ipynb"]),
    ("tests", ["tests/**", "test_*.py"]),
    ("tokenizer", ["*tokenizer*.py", "tokenization/**", "src/tokenizer/**"]),
    ("model", ["model/**", "src/model/**", "*model*.py"]),
    ("train", ["train*.py", "src/training/**"]),
    ("ci", [".github/**", "noxfile.py", "tox.ini"]),
    ("checkpoints", ["checkpoint*.py", "src/utils/checkpoint.py"]),
    (
        "logging",
        ["wandb", "mlflow", "tensorboard", "logging_factory", "src/utils/logging_factory.py"],
    ),
]


def find_files(root: Path) -> Iterator[Path]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            yield Path(dirpath) / name


def search_for_patterns() -> Dict[str, List[str]]:
    found: Dict[str, List[str]] = {}
    files = list(find_files(ROOT))
    for key, patterns in SEARCH_PATTERNS:
        matches: List[str] = []
        for pattern in patterns:
            for file_path in files:
                rel = str(file_path.relative_to(ROOT))
                if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(str(file_path), pattern):
                    matches.append(rel)
        found[key] = sorted(set(matches))
    return found


def find_stubs() -> List[Dict[str, object]]:
    stubs: List[Dict[str, object]] = []
    for file_path in find_files(ROOT):
        if file_path.suffix not in {".py", ".md", ".txt", ".ipynb"}:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in STUB_PATTERNS:
            for match in re.finditer(pattern, text):
                stubs.append(
                    {
                        "file": str(file_path.relative_to(ROOT)),
                        "match": pattern,
                        "line": text[: match.start()].count("\n") + 1,
                        "context": text[max(0, match.start() - 80) : match.end() + 80][:200],
                    }
                )
    return stubs


def detect_tokenizers() -> Dict[str, Iterable[str]]:
    files = list(find_files(ROOT))
    tokenizer_modules: List[str] = []
    for file_path in files:
        if file_path.suffix != ".py":
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if (
            "from tokenizers" in text
            or "import tokenizers" in text
            or ("Tokenizer" in text and "transformers" in text)
        ):
            tokenizer_modules.append(str(file_path.relative_to(ROOT)))
    vocab_files = [
        str(p.relative_to(ROOT))
        for p in files
        if p.name in {"vocab.json", "merges.txt", "tokenizer.json", "tokenizer.model"}
    ]
    return {"tokenizer_modules": tokenizer_modules, "vocab_files": vocab_files}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", default="audit.md")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    all_stubs = find_stubs()
    stub_sample = all_stubs[:1000]
    report: Dict[str, Any]
    report = {
        "root": str(ROOT),
        "files_count": sum(1 for _ in find_files(ROOT)),
        "search_hits": search_for_patterns(),
        "stubs": stub_sample,
        "stubs_total": len(all_stubs),
        "stubs_truncated": max(0, len(all_stubs) - len(stub_sample)),
        "tokenizer_info": detect_tokenizers(),
    }

    with open("audit.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    if args.format == "json":
        print(json.dumps(report, indent=2))
        return

    lines: List[str] = []
    lines.append("# Repo Audit Summary")
    lines.append("")
    lines.append(f"- Root: {report['root']}")
    lines.append(f"- Files scanned: {report['files_count']}")
    lines.append("## Search hits")
    for key, matches in report["search_hits"].items():
        lines.append(f"- **{key}**: {len(matches)} matches")
        for match in matches[:20]:
            lines.append(f"  - {match}")
    lines.append("")
    lines.append("## Tokenizer heuristics")
    for key, matches in report["tokenizer_info"].items():
        lines.append(f"- **{key}**: {list(matches)}")
    lines.append("")
    lines.append("## Stubs found")
    for stub in report["stubs"][:200]:
        lines.append(f"- {stub['file']}:{stub['line']} -> {stub['match']}")
    if report["stubs_truncated"]:
        lines.append(f"- ... truncated {report['stubs_truncated']} additional stub entries")

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"Wrote {args.output} and audit.json")


if __name__ == "__main__":
    main()
