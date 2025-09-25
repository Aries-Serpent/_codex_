#!/usr/bin/env python3
"""Validate Markdown fenced code blocks (CommonMark-aligned), offline.

Compat note:
  - Provides the legacy API used by tests:
      * validate_file(path, strict_inner, *, warn_inner=False) -> list[FenceError]
      * validate_paths(paths, strict_inner, *, warn_inner=False) -> list[FenceError]
      * run_validation(paths, warn_inner, strict_inner) -> list[dict]
      * main()

Design notes:
  - Enforces explicit language info string on openers (CommonMark “info string”).
  - Closing fence must not specify a language.
  - Detects “inner backtick/tilde runs” colliding with opener length:
      * warning in --warn-inner, error in --strict-inner.
  - Max indent of 3 spaces for fences, mirroring CommonMark allowances.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Sequence, Tuple

# Curated default scan targets used when CLI paths are omitted by callers
DEFAULT_TARGETS = (
    Path("AUDIT_PROMPT.md"),
    Path("reports"),
    Path("CHANGELOG.md"),
    Path("OPEN_QUESTIONS.md"),
    Path("Codex_Questions.md"),
)
IGNORE_ROOTS = {".codex", ".git", ".mypy_cache", ".pytest_cache"}

Level = Literal["info", "warning", "error"]


@dataclass(slots=True)
class Finding:
    path: str
    line: int
    col: int
    level: Level
    msg: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "col": self.col,
            "level": self.level,
            "msg": self.msg,
        }


@dataclass(slots=True)
class FenceError:
    path: Path
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        help="Markdown files or directories to scan. Defaults to curated targets when omitted.",
    )
    parser.add_argument(
        "--warn-inner",
        action="store_true",
        help="Warn when an inner fence equals or exceeds the opener length.",
    )
    parser.add_argument(
        "--strict-inner",
        action="store_true",
        help="Fail when nested fences appear inside an existing fenced block.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format for findings.",
    )
    return parser.parse_args(argv)


@dataclass(slots=True)
class FenceContext:
    kind: str  # '`' or '~'
    run: int  # opener length
    line: int  # 1-based
    language: str  # info string, may be empty


def collect_files(paths: Sequence[str] | None) -> List[Path]:
    """Return a de-duplicated list of .md/.mdx files from explicit paths or curated defaults."""

    candidates: List[Path] = []
    targets = [Path(p) for p in paths] if paths else [p for p in DEFAULT_TARGETS if p.exists()]
    for target in targets:
        if target.is_dir():
            for extension in (".md", ".mdx"):
                for cand in sorted(target.rglob(f"*{extension}")):
                    if any(part in IGNORE_ROOTS for part in cand.parts):
                        continue
                    candidates.append(cand)
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


def _is_fence(line: str) -> Tuple[bool, str, int, int, str]:
    """Detect a fence. Return (is_fence, kind, run_len, indent, trailing_text)."""

    stripped = line.lstrip(" ")
    indent = len(line) - len(stripped)
    if indent > 3:
        return (False, "", 0, 0, "")
    for ch in ("`", "~"):
        marker = ch * 3
        if stripped.startswith(marker):
            run = len(stripped) - len(stripped.lstrip(ch))
            trailing = stripped[run:]
            return (True, ch, run, indent, trailing)
    return (False, "", 0, 0, "")


def _longest_run(line: str, ch: str) -> int:
    best = cur = 0
    for value in line:
        if value == ch:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 0
    return best


def _scan_file(path: Path, strict_inner: bool, warn_inner: bool) -> List[Finding]:
    findings: List[Finding] = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        findings.append(Finding(str(path), 0, 1, "error", f"failed to read file: {exc}"))
        return findings

    stack: List[FenceContext] = []
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        is_fence, kind, run_length, indent, trailing = _is_fence(raw_line)
        trailing_stripped = trailing.strip()
        if is_fence:
            # Closing?
            if stack and kind == stack[-1].kind and run_length >= stack[-1].run:
                if trailing_stripped:
                    findings.append(
                        Finding(
                            str(path),
                            line_number,
                            indent + run_length + 1,
                            "error",
                            "closing fence must not include a language tag",
                        )
                    )
                stack.pop()
                continue
            # Nested opener/inner fence while an outer fence is active.
            if stack and (strict_inner or warn_inner):
                collision_level: Level = "error" if strict_inner else "warning"
                findings.append(
                    Finding(
                        str(path),
                        line_number,
                        indent + 1,
                        collision_level,
                        "nested code fence detected inside another fence",
                    )
                )
                continue
            # Opening
            if run_length < 3:
                findings.append(
                    Finding(
                        str(path),
                        line_number,
                        indent + 1,
                        "error",
                        "opening fence must be >= 3 characters",
                    )
                )
                continue
            language = trailing_stripped
            if not language:
                findings.append(
                    Finding(
                        str(path),
                        line_number,
                        indent + run_length + 1,
                        "error",
                        "code fence is missing an explicit language tag",
                    )
                )
            stack.append(
                FenceContext(kind=kind, run=run_length, line=line_number, language=language)
            )
            continue

        # Inner-run detection against the active opener
        if not stack:
            continue
        ch = stack[-1].kind
        run_inner = _longest_run(raw_line, ch)
        if run_inner >= stack[-1].run:
            level: Level = "error" if strict_inner else "warning" if warn_inner else "info"
            if level != "info":
                collision_index = raw_line.find(ch * run_inner)
                findings.append(
                    Finding(
                        str(path),
                        line_number,
                        collision_index + 1 if collision_index >= 0 else 1,
                        level,
                        "nested code fence detected inside another fence",
                    )
                )

    if stack:
        for frame in stack:
            language = frame.language or "<unknown>"
            findings.append(
                Finding(
                    str(path),
                    frame.line,
                    1,
                    "error",
                    f"code fence for language '{language}' not closed",
                )
            )
    return findings


# ---- Back-compat helpers used by tests and tools ---------------------------------------------
def validate_file(path: Path, strict_inner: bool, *, warn_inner: bool = False) -> List[FenceError]:
    findings = _scan_file(path, strict_inner=strict_inner, warn_inner=warn_inner)
    return [FenceError(Path(f.path), f.line, f.msg) for f in findings if f.level == "error"]


def validate_paths(
    paths: Sequence[str] | None, strict_inner: bool, *, warn_inner: bool = False
) -> List[FenceError]:
    errors: List[FenceError] = []
    for candidate in collect_files(paths):
        errors.extend(validate_file(candidate, strict_inner, warn_inner=warn_inner))
    return errors


def run_validation(
    paths: Iterable[str] | None, warn_inner: bool, strict_inner: bool
) -> List[Dict[str, object]]:
    provided = list(paths or [])
    candidates = collect_files(provided)
    all_findings: List[Dict[str, object]] = []
    for candidate in candidates:
        scan_results = _scan_file(candidate, strict_inner=strict_inner, warn_inner=warn_inner)
        all_findings.extend(result.as_dict() for result in scan_results)
    return all_findings


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    results = run_validation(args.paths, warn_inner=args.warn_inner, strict_inner=args.strict_inner)
    failed = any(entry["level"] == "error" for entry in results)
    if args.format == "json":
        print(json.dumps({"results": results}, indent=2))
    else:
        for entry in results:
            print(
                f"{entry['path']}:{entry['line']}:{entry['col']}: "
                f"{str(entry['level']).upper()}: {entry['msg']}"
            )
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
