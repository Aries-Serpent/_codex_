#!/usr/bin/env python
"""Validate fenced code blocks across Markdown/patch files in the repo.

This refresh aligns the validator with the Markdown fence rules emphasized in
our contributor docs:

* Openers and closers must use the same fence character (backtick or tilde) and
  the closer length must be greater than or equal to the opener.
* Backtick info strings must not contain backticks (per CommonMark/GFM).
* Inner lines that could terminate the outer fence are flagged, optionally as
  warnings when ``--warn-inner`` is supplied.

The module continues to expose the legacy ``validate_file`` helper so existing
callers (tests, CLIs, and docs) remain compatible.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MD_EXTS = {".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".patch", ".diff"}
SKIP_DIRS = {".git", ".codex", "temp", "artifacts", "reports", "site"}
SKIP_FILES = {
    os.path.join("samples", "broken_fence.sample.md"),
    os.path.join("docs", "FollowUp_Implementation_Plan.md"),
    os.path.join("docs", "reproducibility.md"),
    os.path.join("docs", "reference", "audit_prompt.md"),
    os.path.join("docs", "rubrics", "codex_eval_rubric_v3.md"),
    os.path.join("patches", "analysis.patch"),
    os.path.join("tests", "data", "validate_fences_sample.md"),
    os.path.join("tests", "samples", "bad_fences.md"),
    os.path.join("_codex", "status", "_codex_status_update-2025-09-21.md"),
}

OPEN_RE = re.compile(r"^(?P<seq>`{3,}|~{3,})(?P<info>[^\n]*)$")
CLOSE_RE = re.compile(r"^(?P<seq>`{3,}|~{3,})(?P<trail>[ \t]*)$")


@dataclass
class FenceError:
    """Represents a fence validation problem compatible with legacy callers."""

    path: str
    line: int
    message: str
    severity: str = "error"

    def __str__(self) -> str:  # pragma: no cover - best-effort repr
        return f"{self.path}:{self.line}: {self.message}"


@dataclass
class FenceState:
    """Track information about the currently open fence block."""

    char: str
    length: int
    opener_line: int
    opener_text: str
    info: str
    indent: int
    max_inner: int = 0
    max_inner_line: int | None = None


def _prepare_line(line: str) -> tuple[int, str]:
    """Return ``(indent, trimmed)`` handling unified diff prefixes when present."""

    raw = line.rstrip("\n")
    idx = 0
    length = len(raw)
    while idx < length and raw[idx] == " ":
        idx += 1
    indent = idx
    trimmed = raw[idx:]

    if trimmed.startswith(("+", "-")):
        idx += 1
        trimmed = raw[idx:]
        while trimmed.startswith(" "):
            idx += 1
            trimmed = raw[idx:]
        indent = idx

    return indent, trimmed


def _max_run(text: str, char: str) -> int:
    """Return the maximum contiguous run of ``char`` within ``text``."""

    best = 0
    current = 0
    for ch in text:
        if ch == char:
            current += 1
            if current > best:
                best = current
        else:
            current = 0
    return best


def iter_files(root: str | Path) -> Iterable[str]:
    """Yield Markdown/diff files beneath ``root`` respecting skip lists."""

    root_path = Path(root)
    for dirpath, _, filenames in os.walk(root_path):
        parts = Path(dirpath).parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        for filename in filenames:
            ext = Path(filename).suffix.lower()
            if ext in MD_EXTS:
                full_path = os.path.join(dirpath, filename)
                rel = os.path.relpath(full_path, root_path)
                if rel in SKIP_FILES:
                    continue
                yield full_path


def _scan_file(
    path: str,
    *,
    strict_inner: bool,
    warn_inner: bool,
    check_language: bool,
) -> tuple[list[FenceError], list[FenceError]]:
    """Return ``(errors, warnings)`` discovered while scanning ``path``."""

    errors: list[FenceError] = []
    warnings: list[FenceError] = []

    try:
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:  # pragma: no cover - surfaced as runtime failure
        errors.append(FenceError(path=path, line=0, message=f"Read error: {exc}"))
        return errors, warnings

    inner_mode = "ignore"
    if warn_inner:
        inner_mode = "warn"
    elif strict_inner:
        inner_mode = "error"

    state: FenceState | None = None

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        indent, trimmed = _prepare_line(raw_line)

        if state is None:
            if indent <= 3:
                open_match = OPEN_RE.match(trimmed)
                if open_match:
                    seq = open_match.group("seq")
                    info = (open_match.group("info") or "").rstrip()
                    char = seq[0]
                    state = FenceState(
                        char=char,
                        length=len(seq),
                        opener_line=lineno,
                        opener_text=trimmed,
                        info=info,
                        indent=indent,
                    )
                    if check_language and not info.strip():
                        errors.append(
                            FenceError(
                                path=path,
                                line=lineno,
                                message="Missing language tag for fenced block",
                            )
                        )
                    if char == "`" and "`" in info:
                        errors.append(
                            FenceError(
                                path=path,
                                line=lineno,
                                message="Backticks in info string (backtick fence)",
                            )
                        )
                    continue
            continue

        # Inside a fenced block
        if indent <= 3:
            close_match = CLOSE_RE.match(trimmed)
            if close_match:
                seq = close_match.group("seq")
                char = seq[0]
                if char != state.char:
                    errors.append(
                        FenceError(
                            path=path,
                            line=lineno,
                            message="mixed fence types within one block",
                        )
                    )
                    state = None
                    continue

                close_len = len(seq)
                if close_len < state.length:
                    errors.append(
                        FenceError(
                            path=path,
                            line=lineno,
                            message=(
                                f"Closing fence shorter than opener (open={state.length}, "
                                f"close={close_len})"
                            ),
                        )
                    )
                    continue

                if inner_mode != "ignore" and state.max_inner >= state.length:
                    msg = (
                        f"nested code fence detected (outer={state.length}, "
                        f"inner={state.max_inner})"
                    )
                    issue = FenceError(
                        path=path,
                        line=state.max_inner_line or lineno,
                        message=msg,
                        severity="warning" if inner_mode == "warn" else "error",
                    )
                    if inner_mode == "warn":
                        warnings.append(issue)
                    else:
                        errors.append(issue)

                state = None
                continue

            if trimmed.startswith(("`", "~")) and trimmed[0] != state.char:
                errors.append(
                    FenceError(
                        path=path,
                        line=lineno,
                        message="mixed fence types within one block",
                    )
                )
                state = None
                continue

        if inner_mode != "ignore":
            run = _max_run(trimmed, state.char)
            if run >= state.length:
                if run > state.max_inner:
                    state.max_inner = run
                    state.max_inner_line = lineno
                elif state.max_inner_line is None:
                    state.max_inner_line = lineno

    if state is not None:
        errors.append(
            FenceError(
                path=path,
                line=state.opener_line,
                message="EOF while inside a fenced block",
            )
        )

    return errors, warnings


def validate_file(
    path: str | Path,
    strict_inner: bool | None = None,
    warn_inner: bool | None = None,
    check_language: bool = True,
):
    """Validate fenced blocks in ``path`` with backwards-compatible semantics."""

    str_path = str(path)
    if strict_inner is None and warn_inner is None:
        errors, _warnings = _scan_file(
            str_path,
            strict_inner=False,
            warn_inner=False,
            check_language=check_language,
        )
        ok = not errors
        problems = [str(err) for err in errors]
        return ok, problems

    warn_flag = bool(warn_inner)
    strict_flag = bool(strict_inner) or warn_flag
    errors, warnings = _scan_file(
        str_path,
        strict_inner=strict_flag,
        warn_inner=warn_flag,
        check_language=check_language,
    )
    if warn_flag:
        return errors
    return errors


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Markdown fence usage")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--strict-inner",
        action="store_true",
        help="Treat inner/nested fences as errors",
    )
    mode.add_argument(
        "--warn-inner",
        action="store_true",
        help="Emit warnings (but not errors) for inner fences",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Specific files or directories to validate (defaults to the repo)",
    )
    return parser.parse_args(argv)


def _gather_targets(paths: Sequence[str]) -> list[str]:
    if not paths:
        return list(iter_files(REPO_ROOT))

    targets: list[str] = []
    for entry in paths:
        expanded = Path(entry).expanduser()
        if not expanded.is_absolute():
            expanded = (Path.cwd() / expanded).resolve()
        if expanded.is_dir():
            targets.extend(iter_files(expanded))
            continue
        targets.append(str(expanded))
    return targets


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)

    targets = _gather_targets(args.paths)
    if not targets:
        print("[fence-check] No matching files")
        return 0

    warn_flag = args.warn_inner
    strict_flag = args.strict_inner or not args.warn_inner
    check_inner = strict_flag or warn_flag

    exit_code = 0
    had_output = False

    for target in targets:
        errors, warnings = _scan_file(
            target,
            strict_inner=check_inner,
            warn_inner=warn_flag,
            check_language=True,
        )
        for err in errors:
            had_output = True
            exit_code = 1
            print(f"[fence-check] {err.path}:{err.line}: ERROR — {err.message}")
        for warn in warnings:
            had_output = True
            print(f"[fence-check] {warn.path}:{warn.line}: WARN — {warn.message}")

    if not had_output:
        print("[fence-check] OK")
    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main(sys.argv[1:]))
