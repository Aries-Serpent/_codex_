#!/usr/bin/env python3
"""Offline helper to collect repository gaps and stage patch files."""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class Context:
    """Directories used by the task sequence script."""

    root: Path
    docs_dir: Path
    logs_dir: Path
    patches_dir: Path
    changelog: Path
    gaps_report: Path
    pruning_log: Path
    error_log: Path


def build_ctx(root: Path) -> Context:
    docs_dir = root / "docs"
    logs_dir = root / "logs"
    patches_dir = root / "patches" / "pending"
    return Context(
        root=root,
        docs_dir=docs_dir,
        logs_dir=logs_dir,
        patches_dir=patches_dir,
        changelog=root / "CHANGELOG.md",
        gaps_report=docs_dir / "gaps_report.md",
        pruning_log=docs_dir / "pruning_log.md",
        error_log=logs_dir / "error_captures.log",
    )


def ts_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def safe_write_text(path: Path, content: str) -> None:
    ensure_dirs(path.parent)
    path.write_text(content, encoding="utf-8")


def collect_repository_overview(root: Path) -> Dict[str, int]:
    counts = {"py": 0, "md": 0, "yaml": 0, "ipynb": 0, "other": 0}
    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        suffix = candidate.suffix.lower()
        if suffix == ".py":
            counts["py"] += 1
        elif suffix == ".md":
            counts["md"] += 1
        elif suffix in {".yml", ".yaml"}:
            counts["yaml"] += 1
        elif suffix == ".ipynb":
            counts["ipynb"] += 1
        else:
            counts["other"] += 1
    return counts


STUB_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bTODO\b"),
    re.compile(r"NotImplementedError"),
    re.compile(r"\bFIXME\b"),
)


def find_stubbed_files(root: Path) -> List[str]:
    findings: List[str] = []
    for file_path in root.rglob("*.py"):
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            continue
        for pattern in STUB_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append(f"- {file_path.relative_to(root)}:{line_no}: {pattern.pattern}\n")
    return findings


def write_gaps_report(ctx: Context, findings: Iterable[str]) -> None:
    header = "# Gap Analysis Report\n\n"
    body = "".join(findings)
    if not body:
        body = "No stubs detected\n"
    safe_write_text(ctx.gaps_report, header + body)


def stage_unified_diff(ctx: Context, target_name: str, diff_text: str) -> Path:
    ensure_dirs(ctx.patches_dir)
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", target_name).strip("_") or "patch"
    output = ctx.patches_dir / f"{ts_iso()}__{safe_name}.patch"
    safe_write_text(output, diff_text.rstrip() + "\n")
    return output


def append_pruning_log(ctx: Context, items: Iterable[Tuple[str, str]]) -> None:
    ensure_dirs(ctx.pruning_log.parent)
    lines: List[str] = []
    if ctx.pruning_log.exists():
        lines.append(ctx.pruning_log.read_text(encoding="utf-8"))
    lines.append(f"## Pruning @ {ts_iso()}\n")
    for module, rationale in items:
        lines.append(f"- {module} — {rationale}\n")
    safe_write_text(ctx.pruning_log, "".join(lines))


def log_error(ctx: Context, step: str, error: Exception) -> None:
    ensure_dirs(ctx.logs_dir)
    block = textwrap.dedent(
        f"""
        Question for ChatGPT-5 {ts_iso()}:
        While performing [{step}], encountered the following error:
        {error!r}
        Context: See codex_task_sequence.py and logs for details.
        What are the possible causes, and how can this be resolved while preserving intended functionality?
        """
    ).lstrip()
    with ctx.error_log.open("a", encoding="utf-8") as handle:
        handle.write(block)


def append_changelog(ctx: Context, bullets: Iterable[str]) -> None:
    ensure_dirs(ctx.changelog.parent)
    if not ctx.changelog.exists():
        safe_write_text(ctx.changelog, "# Changelog\n\n")
    entry_lines = [f"### Unreleased - {datetime.utcnow():%Y-%m-%d}\n"]
    entry_lines.extend(f"- {line}\n" for line in bullets)
    entry_lines.append("\n")
    with ctx.changelog.open("a", encoding="utf-8") as handle:
        handle.writelines(entry_lines)


def run_sequence(ctx: Context, dry_run: bool, diffs: List[Path]) -> int:
    try:
        overview = collect_repository_overview(ctx.root)
        findings = find_stubbed_files(ctx.root)
        write_gaps_report(ctx, findings)

        staged: List[Path] = []
        for diff_path in diffs:
            try:
                diff_text = diff_path.read_text(encoding="utf-8")
            except Exception as exc:  # pragma: no cover - best effort
                log_error(ctx, f"read_diff:{diff_path}", exc)
                continue
            staged.append(stage_unified_diff(ctx, diff_path.name, diff_text))

        append_pruning_log(
            ctx,
            [
                (
                    "interfaces/rl.py",
                    "Deferred RLHF/bandit agent implementation; high complexity.",
                ),
                (
                    "monitoring/prometheus.py",
                    "GPU/NVML telemetry deferred; environment constraints.",
                ),
            ],
        )

        bullets = [
            "Generated docs/gaps_report.md from repository scan.",
            (
                f"Staged {len(staged)} patch file(s) under patches/pending/."
                if staged
                else "No patches staged."
            ),
            "Appended docs/pruning_log.md with deferred items.",
        ]
        append_changelog(ctx, bullets)

        print(
            json.dumps(
                {
                    "overview": overview,
                    "gaps_report": str(ctx.gaps_report),
                    "pruning_log": str(ctx.pruning_log),
                    "error_log": str(ctx.error_log),
                    "patches_dir": str(ctx.patches_dir),
                    "dry_run": dry_run,
                    "staged_patches": [str(path) for path in staged],
                },
                indent=2,
            )
        )
        return 0
    except Exception as exc:  # pragma: no cover - high level guard
        log_error(ctx, "run_sequence", exc)
        print(f"[error] {exc}", file=sys.stderr)
        return 1


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex sequential execution (offline).")
    parser.add_argument("--root", type=str, default=".", help="Repository root.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Stage diffs only; never apply.",
    )
    parser.add_argument(
        "--apply-diff",
        action="append",
        default=[],
        help="Path(s) to unified diff files to stage.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    ctx = build_ctx(Path(args.root).resolve())
    diff_paths = [Path(item).resolve() for item in args.apply_diff]
    return run_sequence(ctx, dry_run=args.dry_run, diffs=diff_paths)


if __name__ == "__main__":
    import sys

    sys.exit(main())
