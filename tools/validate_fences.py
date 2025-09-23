#!/usr/bin/env python3
"""Validate markdown code fences for offline audit outputs."""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

FENCE_PREFIX = "```"

DEFAULT_TARGETS = (
    Path("AUDIT_PROMPT.md"),
    Path("reports"),
    Path("CHANGELOG.md"),
    Path("OPEN_QUESTIONS.md"),
    Path("Codex_Questions.md"),
)


@dataclass
class FenceError:
    path: Path
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def collect_files(paths: Sequence[str]) -> List[Path]:
    candidates: List[Path] = []
    targets = [Path(p) for p in paths] if paths else [p for p in DEFAULT_TARGETS if p.exists()]
    ignore_roots = {".codex", ".git", ".mypy_cache", ".pytest_cache"}
    for target in targets:
        if target.is_dir():
            for extension in (".md", ".mdx"):
                for candidate in sorted(target.rglob(f"*{extension}")):
                    if any(part in ignore_roots for part in candidate.parts):
                        continue
                    candidates.append(candidate)
        elif target.suffix.lower() in {".md", ".mdx"}:
            candidates.append(target)
    unique: List[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def validate_file(path: Path, strict_inner: bool) -> List[FenceError]:
    errors: List[FenceError] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(FenceError(path, 0, f"failed to read file: {exc}"))
        return errors

    in_block = False
    block_start = 0
    current_language = ""
    opening_fence_length = 0

    for idx, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()

        if stripped.startswith(FENCE_PREFIX):
            backtick_count = len(stripped) - len(stripped.lstrip("`"))
            if backtick_count < 3:
                continue
            trailing = stripped[backtick_count:].strip()

            if not in_block:
                if not trailing:
                    errors.append(
                        FenceError(
                            path,
                            idx,
                            "code fence is missing an explicit language tag",
                        )
                    )
                current_language = trailing
                in_block = True
                block_start = idx
                opening_fence_length = backtick_count
            else:
                if backtick_count < opening_fence_length:
                    if strict_inner:
                        errors.append(
                            FenceError(
                                path,
                                idx,
                                "nested code fence detected inside another fence",
                            )
                        )
                    continue
                if trailing:
                    errors.append(
                        FenceError(
                            path,
                            idx,
                            "closing fence must not include a language tag",
                        )
                    )
                in_block = False
                current_language = ""
                opening_fence_length = 0
            continue

        if in_block and strict_inner and FENCE_PREFIX in stripped:
            errors.append(
                FenceError(
                    path,
                    idx,
                    "nested code fence detected inside another fence",
                )
            )

    if in_block:
        errors.append(
            FenceError(
                path,
                block_start,
                f"code fence for language '{current_language}' not closed",
            )
        )

    return errors


def validate_paths(paths: Sequence[str], strict_inner: bool) -> List[FenceError]:
    errors: List[FenceError] = []
    for file_path in collect_files(paths):
        errors.extend(validate_file(file_path, strict_inner))
    return errors


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        help="Markdown files or directories to scan. Defaults to the current directory if omitted.",
    )
    parser.add_argument(
        "--strict-inner",
        action="store_true",
        help="Fail when nested fences appear inside an existing fenced block.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    errors = validate_paths(args.paths, args.strict_inner)
    if errors:
        for error in errors:
            print(error.format(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
