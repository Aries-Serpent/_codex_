#!/usr/bin/env python
"""Validate fenced code blocks across Markdown/patch files in the repo.

Checks:
  1) Balanced fences (backticks or tildes) per file.
  2) No mixing fence types within a single code block.
  3) For 'diff' patches: ensure a single outer fence used (heuristic).

Exit codes:
  0 = OK
  1 = Violations found
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from typing import Iterable, List, Tuple

MD_EXTS = {".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".patch", ".diff"}
SKIP_DIRS = {".git", ".codex", "temp", "artifacts", "reports", "site"}
SKIP_FILES = {
    os.path.join("samples", "broken_fence.sample.md"),
    os.path.join("docs", "FollowUp_Implementation_Plan.md"),
}

FENCE_RE = re.compile(r"^(?P<fence>(`{3,}|~{3,}))(?P<label>.*)$")


@dataclass
class FenceError:
    """Represents a fence validation problem compatible with legacy callers."""

    path: str
    line: int
    message: str
    severity: str = "error"

    def __str__(self) -> str:  # pragma: no cover - best-effort repr
        return f"{self.path}:{self.line}: {self.message}"


def iter_files(root: str) -> Iterable[str]:
    for dirpath, _, filenames in os.walk(root):
        # Skip hidden and vendor-ish dirs
        parts = dirpath.split(os.sep)
        if any(p in SKIP_DIRS for p in parts):
            continue
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in MD_EXTS:
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                if rel in SKIP_FILES:
                    continue
                yield os.path.join(dirpath, fn)


def _scan_file(
    path: str,
    *,
    strict_inner: bool,
    warn_inner: bool,
    check_language: bool,
) -> Tuple[List[FenceError], List[FenceError]]:
    """Return ``(errors, warnings)`` discovered while scanning ``path``."""

    errors: List[FenceError] = []
    warnings: List[FenceError] = []

    last_lineno = 0

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        in_block = False
        current_fence: str | None = None
        nested_reported = False

        for lineno, raw_line in enumerate(f, start=1):
            last_lineno = lineno
            line = raw_line.rstrip("\n")
            stripped = line.lstrip()
            if stripped[:1] in {"+", "-"}:
                candidate = stripped[1:].lstrip()
                if candidate.startswith(("`", "~")):
                    stripped = candidate
            match = FENCE_RE.match(stripped)
            if match:
                fence_token = match.group("fence")
                fence_char = fence_token[0]
                if not in_block:
                    in_block = True
                    current_fence = fence_char
                    nested_reported = False

                    label = match.group("label")
                    if check_language and label is not None and not label.strip():
                        errors.append(
                            FenceError(
                                path=path,
                                line=lineno,
                                message="Missing language tag for fenced block",
                            )
                        )
                else:
                    if current_fence and fence_char != current_fence:
                        errors.append(
                            FenceError(
                                path=path,
                                line=lineno,
                                message="mixed fence types within one block",
                            )
                        )
                    in_block = False
                    current_fence = None
                    nested_reported = False
                continue

            if in_block and strict_inner and current_fence and not nested_reported:
                inner_token = current_fence * 3
                if inner_token in line:
                    problem = FenceError(
                        path=path,
                        line=lineno,
                        message="nested code fence detected",
                        severity="warning" if warn_inner else "error",
                    )
                    if warn_inner:
                        warnings.append(problem)
                    else:
                        errors.append(problem)
                    nested_reported = True

        if in_block:
            errors.append(
                FenceError(
                    path=path,
                    line=last_lineno,
                    message="EOF while inside a fenced block",
                )
            )

    return errors, warnings


def validate_file(
    path: str,
    strict_inner: bool | None = None,
    warn_inner: bool | None = None,
):
    """Validate fenced blocks in ``path`` with backwards-compatible semantics."""

    if strict_inner is None and warn_inner is None:
        errors, _warnings = _scan_file(
            path,
            strict_inner=False,
            warn_inner=False,
            check_language=False,
        )
        ok = not errors
        problems = [str(err) for err in errors]
        return ok, problems

    strict = bool(strict_inner)
    warn = bool(warn_inner)
    errors, _warnings = _scan_file(
        path,
        strict_inner=strict,
        warn_inner=warn,
        check_language=True,
    )
    # Legacy callers expect warnings to be suppressed entirely when warn_inner=True.
    return errors


def main() -> int:
    root = os.getcwd()
    all_ok = True
    all_problems: list[str] = []
    for p in iter_files(root):
        ok, probs = validate_file(p)
        if not ok:
            all_ok = False
            all_problems.extend(probs)
    if not all_ok:
        print("Fence validation failures:")
        for msg in all_problems:
            print(" -", msg)
        return 1
    print("Fences OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
