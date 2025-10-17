"""Archive PR checklist helper.

This module validates that an archive-oriented pull request includes
the governance artefacts our policy requires: an ADR, changelog entry,
evidence log update, and provenance material.  The helper can operate on
the staged git diff or on an explicit list of paths, making it easy to
use from tests and CI automation alike.
"""

from __future__ import annotations

import argparse
import subprocess
from collections.abc import Iterable, Sequence
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

ADR_PREFIX = "docs/arch/"
CHANGELOG_PATH = "CHANGELOG.md"
EVIDENCE_PATH = ".codex/evidence/archive_ops.jsonl"
PROVENANCE_HINTS = ("provenance", "attest", "attestation")


@dataclass(slots=True)
class ArchiveChecklistResult:
    """Structured result for archive PR checklist validation."""

    ok: bool
    has_adr: bool
    has_changelog: bool
    has_evidence: bool
    has_provenance: bool
    missing: list[str]
    changed_files: list[str]


def _normalise_paths(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = Path(raw)
        if candidate.is_absolute():
            with suppress(ValueError):
                candidate = candidate.relative_to(repo_root)
        rel = candidate.as_posix()
        if not rel:
            continue
        seen.setdefault(rel)
    return sorted(seen.keys())


def _git_staged_files(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _path_exists(repo_root: Path, rel: str) -> bool:
    """Return True when *rel* exists within *repo_root*."""

    with suppress(ValueError):
        return (repo_root / rel).exists()
    return False


def _looks_like_provenance(rel: str) -> bool:
    lowered = rel.lower()
    return any(hint in lowered for hint in PROVENANCE_HINTS)


def evaluate_archive_pr(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged)
    has_changelog = any(path == CHANGELOG_PATH and _path_exists(root, path) for path in staged)
    has_evidence = any(path == EVIDENCE_PATH and _path_exists(root, path) for path in staged)
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if not has_adr:
        missing.append("ADR in docs/arch/")
    if not has_changelog:
        missing.append("CHANGELOG.md update")
    if not has_evidence:
        missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
    if not has_provenance:
        missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def _format_boolean(value: bool) -> str:
    return "yes" if value else "no"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help="Explicitly provide relative paths instead of reading git staged files.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when requirements are missing or CODEOWNERS validation fails.",
    )
    parser.add_argument(
        "--check-codeowners",
        action="store_true",
        help="Validate CODEOWNERS in addition to archive checklist requirements.",
    )
    args = parser.parse_args(argv)

    result = evaluate_archive_pr(args.repo_root, changed_files=args.changed_files)

    print("Archive PR checklist")
    print(f"  Repo root: {args.repo_root.resolve().as_posix()}")
    print(f"  Changed files ({len(result.changed_files)}):")
    for path in result.changed_files:
        print(f"    - {path}")
    print(f"  ADR present: {_format_boolean(result.has_adr)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = 1
    else:
        print("  All archive checklist requirements satisfied.")

    if args.check_codeowners:
        from src.tools.codeowners_validate import validate_repo_codeowners

        report = validate_repo_codeowners(args.repo_root)
        codeowners_ok = report.exists and not report.errors and report.owners_ok
        print(f"  CODEOWNERS valid: {_format_boolean(codeowners_ok)}")
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
