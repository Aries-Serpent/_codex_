#!/usr/bin/env python3
"""
Thin wrapper to run or emulate the repository's ``validate-fences`` pre-commit hook.

When ``pre-commit`` is available this script delegates to
``pre-commit run validate-fences --files ...`` to ensure the exact hook logic is
applied.  If ``pre-commit`` is unavailable (e.g., in minimal CI containers) the
script falls back to a lightweight, inline validator that checks for:

* Missing language tags on fenced code block openers.
* Nested triple-backtick runs inside an existing fence when ``--strict-inner``
  is used.
* Unclosed fences at end-of-file.

The fallback validator retains compatibility with the legacy helper functions
(``validate_file``/``validate_paths``/``run_validation``) exercised by existing
unit tests.

Usage::

    python3 tools/validate_fences.py --strict-inner docs/guides/mlflow_offline.md
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

DEFAULT_TARGETS: tuple[Path, ...] = (
    Path("AUDIT_PROMPT.md"),
    Path("reports"),
    Path("CHANGELOG.md"),
    Path("OPEN_QUESTIONS.md"),
    Path("Codex_Questions.md"),
)
IGNORE_ROOTS = {".codex", ".git", ".mypy_cache", ".pytest_cache", "site"}
FENCE_BACKTICK = "```"
FENCE_TILDE = "~~~"


@dataclass(slots=True)
class FenceError:
    path: Path
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def _iter_lines(path: Path) -> Iterable[tuple[int, str]]:
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            yield index, line


def validate_file(path: Path, strict_inner: bool, *, warn_inner: bool = False) -> List[FenceError]:
    errors: List[FenceError] = []
    inside_fence = False
    fence_marker = ""
    fence_start_line = 0

    for line_no, line in _iter_lines(path):
        stripped = line.lstrip()
        if stripped.startswith(FENCE_BACKTICK) or stripped.startswith(FENCE_TILDE):
            if not inside_fence:
                inside_fence = True
                fence_marker = (
                    FENCE_BACKTICK if stripped.startswith(FENCE_BACKTICK) else FENCE_TILDE
                )
                fence_start_line = line_no
                language = stripped[len(fence_marker) :].strip()
                if not language:
                    errors.append(
                        FenceError(
                            path=path,
                            line=line_no,
                            message="Code fence is missing a language tag (e.g. ```python).",
                        )
                    )
            else:
                inside_fence = False
                fence_marker = ""
            continue

        if inside_fence and strict_inner and fence_marker in line:
            # ``warn_inner`` mirrors the legacy API. The caller decides how to surface warnings.
            if warn_inner:
                continue
            errors.append(
                FenceError(
                    path=path,
                    line=line_no,
                    message="Detected nested code fence inside a fenced block.",
                )
            )

    if inside_fence:
        errors.append(
            FenceError(
                path=path,
                line=fence_start_line,
                message="Code fence opened but not closed before end of file.",
            )
        )

    return errors


def _collect_targets(paths: Sequence[str] | None) -> List[Path]:
    candidates: List[Path] = []
    inputs = [Path(p) for p in paths] if paths else [p for p in DEFAULT_TARGETS if p.exists()]
    for target in inputs:
        if target.is_dir():
            for extension in (".md", ".mdx"):
                for found in sorted(target.rglob(f"*{extension}")):
                    if (
                        any(part in IGNORE_ROOTS for part in found.parts)
                        or found.suffix == ".ipynb"
                    ):
                        continue
                    candidates.append(found)
        elif target.suffix.lower() in {".md", ".mdx"}:
            candidates.append(target)
    unique: List[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(candidate)
    return unique


def validate_paths(
    paths: Sequence[str] | None, strict_inner: bool, *, warn_inner: bool = False
) -> List[FenceError]:
    errors: List[FenceError] = []
    for path in _collect_targets(paths):
        errors.extend(validate_file(path, strict_inner, warn_inner=warn_inner))
    return errors


def run_validation(
    paths: Iterable[str] | None, warn_inner: bool, strict_inner: bool
) -> List[dict[str, object]]:
    findings: List[dict[str, object]] = []
    for error in validate_paths(
        list(paths) if paths is not None else None, strict_inner, warn_inner=warn_inner
    ):
        findings.append(
            {
                "path": str(error.path),
                "line": error.line,
                "message": error.message,
                "level": "error",
            }
        )
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Markdown files or directories to validate.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--strict-inner", action="store_true", help="Fail on nested fences inside a block."
    )
    mode.add_argument(
        "--warn-inner", action="store_true", help="Warn (but do not fail) on nested fences."
    )
    parser.add_argument(
        "--no-pre-commit",
        action="store_true",
        help="Skip delegating to pre-commit even if available.",
    )
    args = parser.parse_args(argv)

    if not args.warn_inner and not args.strict_inner:
        args.strict_inner = True  # Default to strict mode for CLI parity with legacy script.

    use_pre_commit = (
        not args.no_pre_commit
        and not args.warn_inner
        and shutil.which("pre-commit") is not None
        and os.environ.get("PRE_COMMIT") != "1"
    )
    files = [str(path) for path in _collect_targets(args.paths)]

    if use_pre_commit:
        cmd = ["pre-commit", "run", "validate-fences", "--files", *files]
        return subprocess.call(cmd)

    exit_code = 0
    for error in validate_paths(
        args.paths, strict_inner=args.strict_inner, warn_inner=args.warn_inner
    ):
        level = "warning" if args.warn_inner else "error"
        stream = sys.stderr if not args.warn_inner else sys.stdout
        print(f"[{level}] {error.format()}", file=stream)
        if not args.warn_inner:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
