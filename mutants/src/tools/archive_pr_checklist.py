"""Archive PR checklist helper.

This module validates that an archive-oriented pull request includes the
governance artefacts our policy requires: an ADR, changelog entry, evidence log
update, and provenance material.  The helper can operate on the staged git diff
or on an explicit list of paths, making it easy to use from tests and CI
automation alike.

Recognised provenance artefacts
-------------------------------
Paths that contain any of the following substrings are treated as provenance
evidence when the referenced files exist relative to the repository root:

* ``provenance`` – legacy directory layout.
* ``attest`` or ``attestation`` – generic attestations.
* ``intoto`` or ``in-toto`` – in-toto statements and bundles (e.g.
  ``artifacts/intoto/archive.intoto.jsonl``).
* ``slsa`` – SLSA provenance materials such as ``artifacts/slsa/provenance.json``.

The detection is case-insensitive and applies to full paths so future patterns
in these ecosystems continue to satisfy the provenance requirement without
changing the helper.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import argparse
import subprocess
from collections.abc import Iterable, Sequence
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

ADR_PREFIX = "docs/arch/"
CHANGELOG_PATH = "docs/CHANGELOG.md"
EVIDENCE_PATH = ".codex/evidence/archive_ops.jsonl"
PROVENANCE_HINTS: tuple[str, ...] = (
    "provenance",
    "attest",
    "attestation",
    "intoto",
    "in-toto",
    "slsa",
)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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


def x__normalise_paths__mutmut_orig(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
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


def x__normalise_paths__mutmut_1(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = None
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


def x__normalise_paths__mutmut_2(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = None
        if candidate.is_absolute():
            with suppress(ValueError):
                candidate = candidate.relative_to(repo_root)
        rel = candidate.as_posix()
        if not rel:
            continue
        seen.setdefault(rel)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_3(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = Path(None)
        if candidate.is_absolute():
            with suppress(ValueError):
                candidate = candidate.relative_to(repo_root)
        rel = candidate.as_posix()
        if not rel:
            continue
        seen.setdefault(rel)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_4(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = Path(raw)
        if candidate.is_absolute():
            with suppress(None):
                candidate = candidate.relative_to(repo_root)
        rel = candidate.as_posix()
        if not rel:
            continue
        seen.setdefault(rel)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_5(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = Path(raw)
        if candidate.is_absolute():
            with suppress(ValueError):
                candidate = None
        rel = candidate.as_posix()
        if not rel:
            continue
        seen.setdefault(rel)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_6(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = Path(raw)
        if candidate.is_absolute():
            with suppress(ValueError):
                candidate = candidate.relative_to(None)
        rel = candidate.as_posix()
        if not rel:
            continue
        seen.setdefault(rel)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_7(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = Path(raw)
        if candidate.is_absolute():
            with suppress(ValueError):
                candidate = candidate.relative_to(repo_root)
        rel = None
        if not rel:
            continue
        seen.setdefault(rel)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_8(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = Path(raw)
        if candidate.is_absolute():
            with suppress(ValueError):
                candidate = candidate.relative_to(repo_root)
        rel = candidate.as_posix()
        if rel:
            continue
        seen.setdefault(rel)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_9(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
    """Return sorted, deduplicated paths relative to *repo_root* as POSIX strings."""

    seen: dict[str, None] = {}
    for raw in files:
        candidate = Path(raw)
        if candidate.is_absolute():
            with suppress(ValueError):
                candidate = candidate.relative_to(repo_root)
        rel = candidate.as_posix()
        if not rel:
            break
        seen.setdefault(rel)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_10(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
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
        seen.setdefault(None)
    return sorted(seen.keys())


def x__normalise_paths__mutmut_11(repo_root: Path, files: Iterable[str | Path]) -> list[str]:
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
    return sorted(None)

x__normalise_paths__mutmut_mutants : ClassVar[MutantDict] = {
'x__normalise_paths__mutmut_1': x__normalise_paths__mutmut_1, 
    'x__normalise_paths__mutmut_2': x__normalise_paths__mutmut_2, 
    'x__normalise_paths__mutmut_3': x__normalise_paths__mutmut_3, 
    'x__normalise_paths__mutmut_4': x__normalise_paths__mutmut_4, 
    'x__normalise_paths__mutmut_5': x__normalise_paths__mutmut_5, 
    'x__normalise_paths__mutmut_6': x__normalise_paths__mutmut_6, 
    'x__normalise_paths__mutmut_7': x__normalise_paths__mutmut_7, 
    'x__normalise_paths__mutmut_8': x__normalise_paths__mutmut_8, 
    'x__normalise_paths__mutmut_9': x__normalise_paths__mutmut_9, 
    'x__normalise_paths__mutmut_10': x__normalise_paths__mutmut_10, 
    'x__normalise_paths__mutmut_11': x__normalise_paths__mutmut_11
}

def _normalise_paths(*args, **kwargs):
    result = _mutmut_trampoline(x__normalise_paths__mutmut_orig, x__normalise_paths__mutmut_mutants, args, kwargs)
    return result 

_normalise_paths.__signature__ = _mutmut_signature(x__normalise_paths__mutmut_orig)
x__normalise_paths__mutmut_orig.__name__ = 'x__normalise_paths'


def x__git_staged_files__mutmut_orig(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_1(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = None
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_2(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            None,
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_3(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=None,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_4(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=None,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_5(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=None,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_6(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=None,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_7(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_8(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_9(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_10(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_11(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_12(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["XXgitXX", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_13(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["GIT", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_14(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "XXdiffXX", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_15(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "DIFF", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_16(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "XX--stagedXX", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_17(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--STAGED", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_18(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "XX--name-onlyXX"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_19(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--NAME-ONLY"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_20(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=False,
            check=False,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_21(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=True,
            text=True,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_22(repo_root: Path) -> list[str]:
    """Return staged file paths using ``git diff --staged``.

    Returns an empty list when git is unavailable or the command fails.
    """

    try:
        proc = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=False,
        )
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_23(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(None)
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_24(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(None, exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_25(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=None)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_26(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(exc_info=True)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_27(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", )
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_28(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=False)
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_29(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode == 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def x__git_staged_files__mutmut_30(repo_root: Path) -> list[str]:
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
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return []
    if proc.returncode != 1:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]

x__git_staged_files__mutmut_mutants : ClassVar[MutantDict] = {
'x__git_staged_files__mutmut_1': x__git_staged_files__mutmut_1, 
    'x__git_staged_files__mutmut_2': x__git_staged_files__mutmut_2, 
    'x__git_staged_files__mutmut_3': x__git_staged_files__mutmut_3, 
    'x__git_staged_files__mutmut_4': x__git_staged_files__mutmut_4, 
    'x__git_staged_files__mutmut_5': x__git_staged_files__mutmut_5, 
    'x__git_staged_files__mutmut_6': x__git_staged_files__mutmut_6, 
    'x__git_staged_files__mutmut_7': x__git_staged_files__mutmut_7, 
    'x__git_staged_files__mutmut_8': x__git_staged_files__mutmut_8, 
    'x__git_staged_files__mutmut_9': x__git_staged_files__mutmut_9, 
    'x__git_staged_files__mutmut_10': x__git_staged_files__mutmut_10, 
    'x__git_staged_files__mutmut_11': x__git_staged_files__mutmut_11, 
    'x__git_staged_files__mutmut_12': x__git_staged_files__mutmut_12, 
    'x__git_staged_files__mutmut_13': x__git_staged_files__mutmut_13, 
    'x__git_staged_files__mutmut_14': x__git_staged_files__mutmut_14, 
    'x__git_staged_files__mutmut_15': x__git_staged_files__mutmut_15, 
    'x__git_staged_files__mutmut_16': x__git_staged_files__mutmut_16, 
    'x__git_staged_files__mutmut_17': x__git_staged_files__mutmut_17, 
    'x__git_staged_files__mutmut_18': x__git_staged_files__mutmut_18, 
    'x__git_staged_files__mutmut_19': x__git_staged_files__mutmut_19, 
    'x__git_staged_files__mutmut_20': x__git_staged_files__mutmut_20, 
    'x__git_staged_files__mutmut_21': x__git_staged_files__mutmut_21, 
    'x__git_staged_files__mutmut_22': x__git_staged_files__mutmut_22, 
    'x__git_staged_files__mutmut_23': x__git_staged_files__mutmut_23, 
    'x__git_staged_files__mutmut_24': x__git_staged_files__mutmut_24, 
    'x__git_staged_files__mutmut_25': x__git_staged_files__mutmut_25, 
    'x__git_staged_files__mutmut_26': x__git_staged_files__mutmut_26, 
    'x__git_staged_files__mutmut_27': x__git_staged_files__mutmut_27, 
    'x__git_staged_files__mutmut_28': x__git_staged_files__mutmut_28, 
    'x__git_staged_files__mutmut_29': x__git_staged_files__mutmut_29, 
    'x__git_staged_files__mutmut_30': x__git_staged_files__mutmut_30
}

def _git_staged_files(*args, **kwargs):
    result = _mutmut_trampoline(x__git_staged_files__mutmut_orig, x__git_staged_files__mutmut_mutants, args, kwargs)
    return result 

_git_staged_files.__signature__ = _mutmut_signature(x__git_staged_files__mutmut_orig)
x__git_staged_files__mutmut_orig.__name__ = 'x__git_staged_files'


def x__path_exists__mutmut_orig(repo_root: Path, rel: str) -> bool:
    """Return True when *rel* exists within *repo_root*."""

    with suppress(ValueError):
        return (repo_root / rel).exists()
    return False


def x__path_exists__mutmut_1(repo_root: Path, rel: str) -> bool:
    """Return True when *rel* exists within *repo_root*."""

    with suppress(None):
        return (repo_root / rel).exists()
    return False


def x__path_exists__mutmut_2(repo_root: Path, rel: str) -> bool:
    """Return True when *rel* exists within *repo_root*."""

    with suppress(ValueError):
        return (repo_root * rel).exists()
    return False


def x__path_exists__mutmut_3(repo_root: Path, rel: str) -> bool:
    """Return True when *rel* exists within *repo_root*."""

    with suppress(ValueError):
        return (repo_root / rel).exists()
    return True

x__path_exists__mutmut_mutants : ClassVar[MutantDict] = {
'x__path_exists__mutmut_1': x__path_exists__mutmut_1, 
    'x__path_exists__mutmut_2': x__path_exists__mutmut_2, 
    'x__path_exists__mutmut_3': x__path_exists__mutmut_3
}

def _path_exists(*args, **kwargs):
    result = _mutmut_trampoline(x__path_exists__mutmut_orig, x__path_exists__mutmut_mutants, args, kwargs)
    return result 

_path_exists.__signature__ = _mutmut_signature(x__path_exists__mutmut_orig)
x__path_exists__mutmut_orig.__name__ = 'x__path_exists'


def x__looks_like_provenance__mutmut_orig(rel: str) -> bool:
    lowered = rel.lower()
    return any(hint in lowered for hint in PROVENANCE_HINTS)


def x__looks_like_provenance__mutmut_1(rel: str) -> bool:
    lowered = None
    return any(hint in lowered for hint in PROVENANCE_HINTS)


def x__looks_like_provenance__mutmut_2(rel: str) -> bool:
    lowered = rel.upper()
    return any(hint in lowered for hint in PROVENANCE_HINTS)


def x__looks_like_provenance__mutmut_3(rel: str) -> bool:
    lowered = rel.lower()
    return any(None)


def x__looks_like_provenance__mutmut_4(rel: str) -> bool:
    lowered = rel.lower()
    return any(hint not in lowered for hint in PROVENANCE_HINTS)

x__looks_like_provenance__mutmut_mutants : ClassVar[MutantDict] = {
'x__looks_like_provenance__mutmut_1': x__looks_like_provenance__mutmut_1, 
    'x__looks_like_provenance__mutmut_2': x__looks_like_provenance__mutmut_2, 
    'x__looks_like_provenance__mutmut_3': x__looks_like_provenance__mutmut_3, 
    'x__looks_like_provenance__mutmut_4': x__looks_like_provenance__mutmut_4
}

def _looks_like_provenance(*args, **kwargs):
    result = _mutmut_trampoline(x__looks_like_provenance__mutmut_orig, x__looks_like_provenance__mutmut_mutants, args, kwargs)
    return result 

_looks_like_provenance.__signature__ = _mutmut_signature(x__looks_like_provenance__mutmut_orig)
x__looks_like_provenance__mutmut_orig.__name__ = 'x__looks_like_provenance'


def x_evaluate_archive_pr__mutmut_orig(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_1(
    repo_root: str | Path = "XX.XX",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_2(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = None
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_3(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(None).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_4(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = None

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_5(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(None, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_6(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, None)

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_7(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_8(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, )

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_9(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files and _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_10(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(None))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_11(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = None
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_12(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        None
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_13(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) or _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_14(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(None) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_15(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(None, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_16(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, None) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_17(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_18(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, ) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_19(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = None
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_20(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        None
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_21(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH or _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_22(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path != CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_23(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(None, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_24(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, None) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_25(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_26(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, ) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_27(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = None
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_28(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        None
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_29(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH or _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_30(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path != EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_31(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(None, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_32(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, None) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_33(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_34(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, ) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_35(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = None

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_36(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        None
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_37(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) or _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_38(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(None) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_39(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(None, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_40(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, None) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_41(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_42(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, ) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_43(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = None
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_44(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_45(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append(None)
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_46(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("XXADR in docs/arch/XX")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_47(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("adr in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_48(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR IN DOCS/ARCH/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_49(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if has_changelog:
            missing.append("docs/CHANGELOG.md update")
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


def x_evaluate_archive_pr__mutmut_50(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append(None)
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


def x_evaluate_archive_pr__mutmut_51(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("XXdocs/CHANGELOG.md updateXX")
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


def x_evaluate_archive_pr__mutmut_52(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/changelog.md update")
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


def x_evaluate_archive_pr__mutmut_53(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("DOCS/CHANGELOG.MD UPDATE")
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


def x_evaluate_archive_pr__mutmut_54(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if has_evidence:
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


def x_evaluate_archive_pr__mutmut_55(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append(None)
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


def x_evaluate_archive_pr__mutmut_56(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("XXEvidence log delta (.codex/evidence/archive_ops.jsonl)XX")
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


def x_evaluate_archive_pr__mutmut_57(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("evidence log delta (.codex/evidence/archive_ops.jsonl)")
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


def x_evaluate_archive_pr__mutmut_58(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("EVIDENCE LOG DELTA (.CODEX/EVIDENCE/ARCHIVE_OPS.JSONL)")
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


def x_evaluate_archive_pr__mutmut_59(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if has_provenance:
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


def x_evaluate_archive_pr__mutmut_60(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append(None)

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_61(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("XXProvenance artifactXX")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_62(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_63(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("PROVENANCE ARTIFACT")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_64(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=None,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_65(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=None,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_66(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=None,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_67(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=None,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_68(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=None,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_69(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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
        missing=None,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_70(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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
        changed_files=None,
    )


def x_evaluate_archive_pr__mutmut_71(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_72(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_73(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_74(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_75(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=not missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        missing=missing,
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_76(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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
        changed_files=staged,
    )


def x_evaluate_archive_pr__mutmut_77(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
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
        )


def x_evaluate_archive_pr__mutmut_78(
    repo_root: str | Path = ".",
    *,
    changed_files: Sequence[str | Path] | None = None,
) -> ArchiveChecklistResult:
    """Evaluate whether the staged archive change-set meets policy gates."""

    root = Path(repo_root).resolve()
    staged = _normalise_paths(root, changed_files or _git_staged_files(root))

    has_adr = any(
        path.startswith(ADR_PREFIX) and _path_exists(root, path) for path in staged
    )
    has_changelog = any(
        path == CHANGELOG_PATH and _path_exists(root, path) for path in staged
    )
    has_evidence = any(
        path == EVIDENCE_PATH and _path_exists(root, path) for path in staged
    )
    has_provenance = any(
        _looks_like_provenance(path) and _path_exists(root, path) for path in staged
    )

    missing: list[str] = []
    if staged:
        if not has_adr:
            missing.append("ADR in docs/arch/")
        if not has_changelog:
            missing.append("docs/CHANGELOG.md update")
        if not has_evidence:
            missing.append("Evidence log delta (.codex/evidence/archive_ops.jsonl)")
        if not has_provenance:
            missing.append("Provenance artifact")

    return ArchiveChecklistResult(
        ok=missing,
        has_adr=has_adr,
        has_changelog=has_changelog,
        has_evidence=has_evidence,
        has_provenance=has_provenance,
        missing=missing,
        changed_files=staged,
    )

x_evaluate_archive_pr__mutmut_mutants : ClassVar[MutantDict] = {
'x_evaluate_archive_pr__mutmut_1': x_evaluate_archive_pr__mutmut_1, 
    'x_evaluate_archive_pr__mutmut_2': x_evaluate_archive_pr__mutmut_2, 
    'x_evaluate_archive_pr__mutmut_3': x_evaluate_archive_pr__mutmut_3, 
    'x_evaluate_archive_pr__mutmut_4': x_evaluate_archive_pr__mutmut_4, 
    'x_evaluate_archive_pr__mutmut_5': x_evaluate_archive_pr__mutmut_5, 
    'x_evaluate_archive_pr__mutmut_6': x_evaluate_archive_pr__mutmut_6, 
    'x_evaluate_archive_pr__mutmut_7': x_evaluate_archive_pr__mutmut_7, 
    'x_evaluate_archive_pr__mutmut_8': x_evaluate_archive_pr__mutmut_8, 
    'x_evaluate_archive_pr__mutmut_9': x_evaluate_archive_pr__mutmut_9, 
    'x_evaluate_archive_pr__mutmut_10': x_evaluate_archive_pr__mutmut_10, 
    'x_evaluate_archive_pr__mutmut_11': x_evaluate_archive_pr__mutmut_11, 
    'x_evaluate_archive_pr__mutmut_12': x_evaluate_archive_pr__mutmut_12, 
    'x_evaluate_archive_pr__mutmut_13': x_evaluate_archive_pr__mutmut_13, 
    'x_evaluate_archive_pr__mutmut_14': x_evaluate_archive_pr__mutmut_14, 
    'x_evaluate_archive_pr__mutmut_15': x_evaluate_archive_pr__mutmut_15, 
    'x_evaluate_archive_pr__mutmut_16': x_evaluate_archive_pr__mutmut_16, 
    'x_evaluate_archive_pr__mutmut_17': x_evaluate_archive_pr__mutmut_17, 
    'x_evaluate_archive_pr__mutmut_18': x_evaluate_archive_pr__mutmut_18, 
    'x_evaluate_archive_pr__mutmut_19': x_evaluate_archive_pr__mutmut_19, 
    'x_evaluate_archive_pr__mutmut_20': x_evaluate_archive_pr__mutmut_20, 
    'x_evaluate_archive_pr__mutmut_21': x_evaluate_archive_pr__mutmut_21, 
    'x_evaluate_archive_pr__mutmut_22': x_evaluate_archive_pr__mutmut_22, 
    'x_evaluate_archive_pr__mutmut_23': x_evaluate_archive_pr__mutmut_23, 
    'x_evaluate_archive_pr__mutmut_24': x_evaluate_archive_pr__mutmut_24, 
    'x_evaluate_archive_pr__mutmut_25': x_evaluate_archive_pr__mutmut_25, 
    'x_evaluate_archive_pr__mutmut_26': x_evaluate_archive_pr__mutmut_26, 
    'x_evaluate_archive_pr__mutmut_27': x_evaluate_archive_pr__mutmut_27, 
    'x_evaluate_archive_pr__mutmut_28': x_evaluate_archive_pr__mutmut_28, 
    'x_evaluate_archive_pr__mutmut_29': x_evaluate_archive_pr__mutmut_29, 
    'x_evaluate_archive_pr__mutmut_30': x_evaluate_archive_pr__mutmut_30, 
    'x_evaluate_archive_pr__mutmut_31': x_evaluate_archive_pr__mutmut_31, 
    'x_evaluate_archive_pr__mutmut_32': x_evaluate_archive_pr__mutmut_32, 
    'x_evaluate_archive_pr__mutmut_33': x_evaluate_archive_pr__mutmut_33, 
    'x_evaluate_archive_pr__mutmut_34': x_evaluate_archive_pr__mutmut_34, 
    'x_evaluate_archive_pr__mutmut_35': x_evaluate_archive_pr__mutmut_35, 
    'x_evaluate_archive_pr__mutmut_36': x_evaluate_archive_pr__mutmut_36, 
    'x_evaluate_archive_pr__mutmut_37': x_evaluate_archive_pr__mutmut_37, 
    'x_evaluate_archive_pr__mutmut_38': x_evaluate_archive_pr__mutmut_38, 
    'x_evaluate_archive_pr__mutmut_39': x_evaluate_archive_pr__mutmut_39, 
    'x_evaluate_archive_pr__mutmut_40': x_evaluate_archive_pr__mutmut_40, 
    'x_evaluate_archive_pr__mutmut_41': x_evaluate_archive_pr__mutmut_41, 
    'x_evaluate_archive_pr__mutmut_42': x_evaluate_archive_pr__mutmut_42, 
    'x_evaluate_archive_pr__mutmut_43': x_evaluate_archive_pr__mutmut_43, 
    'x_evaluate_archive_pr__mutmut_44': x_evaluate_archive_pr__mutmut_44, 
    'x_evaluate_archive_pr__mutmut_45': x_evaluate_archive_pr__mutmut_45, 
    'x_evaluate_archive_pr__mutmut_46': x_evaluate_archive_pr__mutmut_46, 
    'x_evaluate_archive_pr__mutmut_47': x_evaluate_archive_pr__mutmut_47, 
    'x_evaluate_archive_pr__mutmut_48': x_evaluate_archive_pr__mutmut_48, 
    'x_evaluate_archive_pr__mutmut_49': x_evaluate_archive_pr__mutmut_49, 
    'x_evaluate_archive_pr__mutmut_50': x_evaluate_archive_pr__mutmut_50, 
    'x_evaluate_archive_pr__mutmut_51': x_evaluate_archive_pr__mutmut_51, 
    'x_evaluate_archive_pr__mutmut_52': x_evaluate_archive_pr__mutmut_52, 
    'x_evaluate_archive_pr__mutmut_53': x_evaluate_archive_pr__mutmut_53, 
    'x_evaluate_archive_pr__mutmut_54': x_evaluate_archive_pr__mutmut_54, 
    'x_evaluate_archive_pr__mutmut_55': x_evaluate_archive_pr__mutmut_55, 
    'x_evaluate_archive_pr__mutmut_56': x_evaluate_archive_pr__mutmut_56, 
    'x_evaluate_archive_pr__mutmut_57': x_evaluate_archive_pr__mutmut_57, 
    'x_evaluate_archive_pr__mutmut_58': x_evaluate_archive_pr__mutmut_58, 
    'x_evaluate_archive_pr__mutmut_59': x_evaluate_archive_pr__mutmut_59, 
    'x_evaluate_archive_pr__mutmut_60': x_evaluate_archive_pr__mutmut_60, 
    'x_evaluate_archive_pr__mutmut_61': x_evaluate_archive_pr__mutmut_61, 
    'x_evaluate_archive_pr__mutmut_62': x_evaluate_archive_pr__mutmut_62, 
    'x_evaluate_archive_pr__mutmut_63': x_evaluate_archive_pr__mutmut_63, 
    'x_evaluate_archive_pr__mutmut_64': x_evaluate_archive_pr__mutmut_64, 
    'x_evaluate_archive_pr__mutmut_65': x_evaluate_archive_pr__mutmut_65, 
    'x_evaluate_archive_pr__mutmut_66': x_evaluate_archive_pr__mutmut_66, 
    'x_evaluate_archive_pr__mutmut_67': x_evaluate_archive_pr__mutmut_67, 
    'x_evaluate_archive_pr__mutmut_68': x_evaluate_archive_pr__mutmut_68, 
    'x_evaluate_archive_pr__mutmut_69': x_evaluate_archive_pr__mutmut_69, 
    'x_evaluate_archive_pr__mutmut_70': x_evaluate_archive_pr__mutmut_70, 
    'x_evaluate_archive_pr__mutmut_71': x_evaluate_archive_pr__mutmut_71, 
    'x_evaluate_archive_pr__mutmut_72': x_evaluate_archive_pr__mutmut_72, 
    'x_evaluate_archive_pr__mutmut_73': x_evaluate_archive_pr__mutmut_73, 
    'x_evaluate_archive_pr__mutmut_74': x_evaluate_archive_pr__mutmut_74, 
    'x_evaluate_archive_pr__mutmut_75': x_evaluate_archive_pr__mutmut_75, 
    'x_evaluate_archive_pr__mutmut_76': x_evaluate_archive_pr__mutmut_76, 
    'x_evaluate_archive_pr__mutmut_77': x_evaluate_archive_pr__mutmut_77, 
    'x_evaluate_archive_pr__mutmut_78': x_evaluate_archive_pr__mutmut_78
}

def evaluate_archive_pr(*args, **kwargs):
    result = _mutmut_trampoline(x_evaluate_archive_pr__mutmut_orig, x_evaluate_archive_pr__mutmut_mutants, args, kwargs)
    return result 

evaluate_archive_pr.__signature__ = _mutmut_signature(x_evaluate_archive_pr__mutmut_orig)
x_evaluate_archive_pr__mutmut_orig.__name__ = 'x_evaluate_archive_pr'


def x__format_boolean__mutmut_orig(value: bool) -> str:
    return "yes" if value else "no"


def x__format_boolean__mutmut_1(value: bool) -> str:
    return "XXyesXX" if value else "no"


def x__format_boolean__mutmut_2(value: bool) -> str:
    return "YES" if value else "no"


def x__format_boolean__mutmut_3(value: bool) -> str:
    return "yes" if value else "XXnoXX"


def x__format_boolean__mutmut_4(value: bool) -> str:
    return "yes" if value else "NO"

x__format_boolean__mutmut_mutants : ClassVar[MutantDict] = {
'x__format_boolean__mutmut_1': x__format_boolean__mutmut_1, 
    'x__format_boolean__mutmut_2': x__format_boolean__mutmut_2, 
    'x__format_boolean__mutmut_3': x__format_boolean__mutmut_3, 
    'x__format_boolean__mutmut_4': x__format_boolean__mutmut_4
}

def _format_boolean(*args, **kwargs):
    result = _mutmut_trampoline(x__format_boolean__mutmut_orig, x__format_boolean__mutmut_mutants, args, kwargs)
    return result 

_format_boolean.__signature__ = _mutmut_signature(x__format_boolean__mutmut_orig)
x__format_boolean__mutmut_orig.__name__ = 'x__format_boolean'


def x_main__mutmut_orig(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_1(argv: Sequence[str] | None = None) -> int:
    parser = None
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_2(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=None)
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_3(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="XXArchive PR checklist gateXX")
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_4(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="archive pr checklist gate")
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_5(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ARCHIVE PR CHECKLIST GATE")
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_6(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument(None, type=Path, default=Path("."))
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_7(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=None, default=Path("."))
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_8(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=None)
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_9(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument(type=Path, default=Path("."))
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_10(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", default=Path("."))
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_11(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, )
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_12(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("XX--repo-rootXX", type=Path, default=Path("."))
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_13(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--REPO-ROOT", type=Path, default=Path("."))
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_14(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path(None))
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_15(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("XX.XX"))
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_16(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_17(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action=None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_18(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest=None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_19(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help=None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_20(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_21(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_22(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_23(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_24(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "XX--changed-fileXX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_25(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--CHANGED-FILE",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_26(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="XXappendXX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_27(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="APPEND",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_28(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="XXchanged_filesXX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_29(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="CHANGED_FILES",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_30(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help="XXExplicitly provide relative paths instead of reading git staged files.XX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_31(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help="explicitly provide relative paths instead of reading git staged files.",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_32(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help="EXPLICITLY PROVIDE RELATIVE PATHS INSTEAD OF READING GIT STAGED FILES.",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_33(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help="Explicitly provide relative paths instead of reading git staged files.",
    )
    parser.add_argument(
        None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_34(argv: Sequence[str] | None = None) -> int:
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
        action=None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_35(argv: Sequence[str] | None = None) -> int:
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
        help=None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_36(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help="Explicitly provide relative paths instead of reading git staged files.",
    )
    parser.add_argument(
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_37(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_38(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_39(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help="Explicitly provide relative paths instead of reading git staged files.",
    )
    parser.add_argument(
        "XX--strictXX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_40(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive PR checklist gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--changed-file",
        action="append",
        dest="changed_files",
        help="Explicitly provide relative paths instead of reading git staged files.",
    )
    parser.add_argument(
        "--STRICT",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_41(argv: Sequence[str] | None = None) -> int:
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
        action="XXstore_trueXX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_42(argv: Sequence[str] | None = None) -> int:
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
        action="STORE_TRUE",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_43(argv: Sequence[str] | None = None) -> int:
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
        help="XXExit non-zero when requirements are missing or CODEOWNERS validation fails.XX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_44(argv: Sequence[str] | None = None) -> int:
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
        help="exit non-zero when requirements are missing or codeowners validation fails.",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_45(argv: Sequence[str] | None = None) -> int:
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
        help="EXIT NON-ZERO WHEN REQUIREMENTS ARE MISSING OR CODEOWNERS VALIDATION FAILS.",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_46(argv: Sequence[str] | None = None) -> int:
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
        None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_47(argv: Sequence[str] | None = None) -> int:
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
        action=None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_48(argv: Sequence[str] | None = None) -> int:
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
        help=None,
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_49(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_50(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_51(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_52(argv: Sequence[str] | None = None) -> int:
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
        "XX--check-codeownersXX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_53(argv: Sequence[str] | None = None) -> int:
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
        "--CHECK-CODEOWNERS",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_54(argv: Sequence[str] | None = None) -> int:
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
        action="XXstore_trueXX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_55(argv: Sequence[str] | None = None) -> int:
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
        action="STORE_TRUE",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_56(argv: Sequence[str] | None = None) -> int:
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
        help="XXValidate CODEOWNERS in addition to archive checklist requirements.XX",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_57(argv: Sequence[str] | None = None) -> int:
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
        help="validate codeowners in addition to archive checklist requirements.",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_58(argv: Sequence[str] | None = None) -> int:
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
        help="VALIDATE CODEOWNERS IN ADDITION TO ARCHIVE CHECKLIST REQUIREMENTS.",
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_59(argv: Sequence[str] | None = None) -> int:
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
    args = None

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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_60(argv: Sequence[str] | None = None) -> int:
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
    args = parser.parse_args(None)

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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_61(argv: Sequence[str] | None = None) -> int:
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

    result = None

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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_62(argv: Sequence[str] | None = None) -> int:
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

    result = evaluate_archive_pr(None, changed_files=args.changed_files)

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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_63(argv: Sequence[str] | None = None) -> int:
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

    result = evaluate_archive_pr(args.repo_root, changed_files=None)

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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_64(argv: Sequence[str] | None = None) -> int:
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

    result = evaluate_archive_pr(changed_files=args.changed_files)

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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_65(argv: Sequence[str] | None = None) -> int:
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

    result = evaluate_archive_pr(args.repo_root, )

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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_66(argv: Sequence[str] | None = None) -> int:
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

    print(None)
    print(f"  Repo root: {args.repo_root.resolve().as_posix()}")
    print(f"  Changed files ({len(result.changed_files)}):")
    for path in result.changed_files:
        print(f"    - {path}")
    print(f"  ADR present: {_format_boolean(result.has_adr)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_67(argv: Sequence[str] | None = None) -> int:
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

    print("XXArchive PR checklistXX")
    print(f"  Repo root: {args.repo_root.resolve().as_posix()}")
    print(f"  Changed files ({len(result.changed_files)}):")
    for path in result.changed_files:
        print(f"    - {path}")
    print(f"  ADR present: {_format_boolean(result.has_adr)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_68(argv: Sequence[str] | None = None) -> int:
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

    print("archive pr checklist")
    print(f"  Repo root: {args.repo_root.resolve().as_posix()}")
    print(f"  Changed files ({len(result.changed_files)}):")
    for path in result.changed_files:
        print(f"    - {path}")
    print(f"  ADR present: {_format_boolean(result.has_adr)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_69(argv: Sequence[str] | None = None) -> int:
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

    print("ARCHIVE PR CHECKLIST")
    print(f"  Repo root: {args.repo_root.resolve().as_posix()}")
    print(f"  Changed files ({len(result.changed_files)}):")
    for path in result.changed_files:
        print(f"    - {path}")
    print(f"  ADR present: {_format_boolean(result.has_adr)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_70(argv: Sequence[str] | None = None) -> int:
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
    print(None)
    print(f"  Changed files ({len(result.changed_files)}):")
    for path in result.changed_files:
        print(f"    - {path}")
    print(f"  ADR present: {_format_boolean(result.has_adr)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_71(argv: Sequence[str] | None = None) -> int:
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
    print(None)
    for path in result.changed_files:
        print(f"    - {path}")
    print(f"  ADR present: {_format_boolean(result.has_adr)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_72(argv: Sequence[str] | None = None) -> int:
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
        print(None)
    print(f"  ADR present: {_format_boolean(result.has_adr)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_73(argv: Sequence[str] | None = None) -> int:
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
    print(None)
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_74(argv: Sequence[str] | None = None) -> int:
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
    print(f"  ADR present: {_format_boolean(None)}")
    print(f"  CHANGELOG updated: {_format_boolean(result.has_changelog)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_75(argv: Sequence[str] | None = None) -> int:
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
    print(None)
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_76(argv: Sequence[str] | None = None) -> int:
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
    print(f"  CHANGELOG updated: {_format_boolean(None)}")
    print(f"  Evidence log updated: {_format_boolean(result.has_evidence)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_77(argv: Sequence[str] | None = None) -> int:
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
    print(None)
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_78(argv: Sequence[str] | None = None) -> int:
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
    print(f"  Evidence log updated: {_format_boolean(None)}")
    print(f"  Provenance artifact present: {_format_boolean(result.has_provenance)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_79(argv: Sequence[str] | None = None) -> int:
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
    print(None)

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_80(argv: Sequence[str] | None = None) -> int:
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
    print(f"  Provenance artifact present: {_format_boolean(None)}")

    exit_code = 0
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_81(argv: Sequence[str] | None = None) -> int:
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

    exit_code = None
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_82(argv: Sequence[str] | None = None) -> int:
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

    exit_code = 1
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_83(argv: Sequence[str] | None = None) -> int:
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
    if result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_84(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print(None)
    elif result.missing:
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


def x_main__mutmut_85(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("XX  Warning: no changed files detected; treating checklist as a no-op.XX")
    elif result.missing:
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


def x_main__mutmut_86(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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


def x_main__mutmut_87(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  WARNING: NO CHANGED FILES DETECTED; TREATING CHECKLIST AS A NO-OP.")
    elif result.missing:
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


def x_main__mutmut_88(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print(None)
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


def x_main__mutmut_89(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("XX  Missing requirements:XX")
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


def x_main__mutmut_90(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  missing requirements:")
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


def x_main__mutmut_91(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  MISSING REQUIREMENTS:")
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


def x_main__mutmut_92(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(None)
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


def x_main__mutmut_93(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = None
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


def x_main__mutmut_94(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = 2
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


def x_main__mutmut_95(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = 1
    else:
        print(None)

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


def x_main__mutmut_96(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = 1
    else:
        print("XX  All archive checklist requirements satisfied.XX")

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


def x_main__mutmut_97(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = 1
    else:
        print("  all archive checklist requirements satisfied.")

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


def x_main__mutmut_98(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = 1
    else:
        print("  ALL ARCHIVE CHECKLIST REQUIREMENTS SATISFIED.")

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


def x_main__mutmut_99(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = 1
    else:
        print("  All archive checklist requirements satisfied.")

    if args.check_codeowners:
        from src.tools.codeowners_validate import validate_repo_codeowners

        report = None
        codeowners_ok = report.exists and not report.errors and report.owners_ok
        print(f"  CODEOWNERS valid: {_format_boolean(codeowners_ok)}")
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_100(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
        print("  Missing requirements:")
        for item in result.missing:
            print(f"    - {item}")
        if args.strict:
            exit_code = 1
    else:
        print("  All archive checklist requirements satisfied.")

    if args.check_codeowners:
        from src.tools.codeowners_validate import validate_repo_codeowners

        report = validate_repo_codeowners(None)
        codeowners_ok = report.exists and not report.errors and report.owners_ok
        print(f"  CODEOWNERS valid: {_format_boolean(codeowners_ok)}")
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_101(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
        codeowners_ok = None
        print(f"  CODEOWNERS valid: {_format_boolean(codeowners_ok)}")
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_102(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
        codeowners_ok = report.exists and not report.errors or report.owners_ok
        print(f"  CODEOWNERS valid: {_format_boolean(codeowners_ok)}")
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_103(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
        codeowners_ok = report.exists or not report.errors and report.owners_ok
        print(f"  CODEOWNERS valid: {_format_boolean(codeowners_ok)}")
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_104(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
        codeowners_ok = report.exists and report.errors and report.owners_ok
        print(f"  CODEOWNERS valid: {_format_boolean(codeowners_ok)}")
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_105(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
        print(None)
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_106(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
        print(f"  CODEOWNERS valid: {_format_boolean(None)}")
        if not codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_107(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
        if codeowners_ok:
            if report.errors:
                for err in report.errors:
                    print(f"    error: {err}")
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_108(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
                    print(None)
            if args.strict:
                exit_code = 1

    return exit_code


def x_main__mutmut_109(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
                exit_code = None

    return exit_code


def x_main__mutmut_110(argv: Sequence[str] | None = None) -> int:
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
    if not result.changed_files:
        print("  Warning: no changed files detected; treating checklist as a no-op.")
    elif result.missing:
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
                exit_code = 2

    return exit_code

x_main__mutmut_mutants : ClassVar[MutantDict] = {
'x_main__mutmut_1': x_main__mutmut_1, 
    'x_main__mutmut_2': x_main__mutmut_2, 
    'x_main__mutmut_3': x_main__mutmut_3, 
    'x_main__mutmut_4': x_main__mutmut_4, 
    'x_main__mutmut_5': x_main__mutmut_5, 
    'x_main__mutmut_6': x_main__mutmut_6, 
    'x_main__mutmut_7': x_main__mutmut_7, 
    'x_main__mutmut_8': x_main__mutmut_8, 
    'x_main__mutmut_9': x_main__mutmut_9, 
    'x_main__mutmut_10': x_main__mutmut_10, 
    'x_main__mutmut_11': x_main__mutmut_11, 
    'x_main__mutmut_12': x_main__mutmut_12, 
    'x_main__mutmut_13': x_main__mutmut_13, 
    'x_main__mutmut_14': x_main__mutmut_14, 
    'x_main__mutmut_15': x_main__mutmut_15, 
    'x_main__mutmut_16': x_main__mutmut_16, 
    'x_main__mutmut_17': x_main__mutmut_17, 
    'x_main__mutmut_18': x_main__mutmut_18, 
    'x_main__mutmut_19': x_main__mutmut_19, 
    'x_main__mutmut_20': x_main__mutmut_20, 
    'x_main__mutmut_21': x_main__mutmut_21, 
    'x_main__mutmut_22': x_main__mutmut_22, 
    'x_main__mutmut_23': x_main__mutmut_23, 
    'x_main__mutmut_24': x_main__mutmut_24, 
    'x_main__mutmut_25': x_main__mutmut_25, 
    'x_main__mutmut_26': x_main__mutmut_26, 
    'x_main__mutmut_27': x_main__mutmut_27, 
    'x_main__mutmut_28': x_main__mutmut_28, 
    'x_main__mutmut_29': x_main__mutmut_29, 
    'x_main__mutmut_30': x_main__mutmut_30, 
    'x_main__mutmut_31': x_main__mutmut_31, 
    'x_main__mutmut_32': x_main__mutmut_32, 
    'x_main__mutmut_33': x_main__mutmut_33, 
    'x_main__mutmut_34': x_main__mutmut_34, 
    'x_main__mutmut_35': x_main__mutmut_35, 
    'x_main__mutmut_36': x_main__mutmut_36, 
    'x_main__mutmut_37': x_main__mutmut_37, 
    'x_main__mutmut_38': x_main__mutmut_38, 
    'x_main__mutmut_39': x_main__mutmut_39, 
    'x_main__mutmut_40': x_main__mutmut_40, 
    'x_main__mutmut_41': x_main__mutmut_41, 
    'x_main__mutmut_42': x_main__mutmut_42, 
    'x_main__mutmut_43': x_main__mutmut_43, 
    'x_main__mutmut_44': x_main__mutmut_44, 
    'x_main__mutmut_45': x_main__mutmut_45, 
    'x_main__mutmut_46': x_main__mutmut_46, 
    'x_main__mutmut_47': x_main__mutmut_47, 
    'x_main__mutmut_48': x_main__mutmut_48, 
    'x_main__mutmut_49': x_main__mutmut_49, 
    'x_main__mutmut_50': x_main__mutmut_50, 
    'x_main__mutmut_51': x_main__mutmut_51, 
    'x_main__mutmut_52': x_main__mutmut_52, 
    'x_main__mutmut_53': x_main__mutmut_53, 
    'x_main__mutmut_54': x_main__mutmut_54, 
    'x_main__mutmut_55': x_main__mutmut_55, 
    'x_main__mutmut_56': x_main__mutmut_56, 
    'x_main__mutmut_57': x_main__mutmut_57, 
    'x_main__mutmut_58': x_main__mutmut_58, 
    'x_main__mutmut_59': x_main__mutmut_59, 
    'x_main__mutmut_60': x_main__mutmut_60, 
    'x_main__mutmut_61': x_main__mutmut_61, 
    'x_main__mutmut_62': x_main__mutmut_62, 
    'x_main__mutmut_63': x_main__mutmut_63, 
    'x_main__mutmut_64': x_main__mutmut_64, 
    'x_main__mutmut_65': x_main__mutmut_65, 
    'x_main__mutmut_66': x_main__mutmut_66, 
    'x_main__mutmut_67': x_main__mutmut_67, 
    'x_main__mutmut_68': x_main__mutmut_68, 
    'x_main__mutmut_69': x_main__mutmut_69, 
    'x_main__mutmut_70': x_main__mutmut_70, 
    'x_main__mutmut_71': x_main__mutmut_71, 
    'x_main__mutmut_72': x_main__mutmut_72, 
    'x_main__mutmut_73': x_main__mutmut_73, 
    'x_main__mutmut_74': x_main__mutmut_74, 
    'x_main__mutmut_75': x_main__mutmut_75, 
    'x_main__mutmut_76': x_main__mutmut_76, 
    'x_main__mutmut_77': x_main__mutmut_77, 
    'x_main__mutmut_78': x_main__mutmut_78, 
    'x_main__mutmut_79': x_main__mutmut_79, 
    'x_main__mutmut_80': x_main__mutmut_80, 
    'x_main__mutmut_81': x_main__mutmut_81, 
    'x_main__mutmut_82': x_main__mutmut_82, 
    'x_main__mutmut_83': x_main__mutmut_83, 
    'x_main__mutmut_84': x_main__mutmut_84, 
    'x_main__mutmut_85': x_main__mutmut_85, 
    'x_main__mutmut_86': x_main__mutmut_86, 
    'x_main__mutmut_87': x_main__mutmut_87, 
    'x_main__mutmut_88': x_main__mutmut_88, 
    'x_main__mutmut_89': x_main__mutmut_89, 
    'x_main__mutmut_90': x_main__mutmut_90, 
    'x_main__mutmut_91': x_main__mutmut_91, 
    'x_main__mutmut_92': x_main__mutmut_92, 
    'x_main__mutmut_93': x_main__mutmut_93, 
    'x_main__mutmut_94': x_main__mutmut_94, 
    'x_main__mutmut_95': x_main__mutmut_95, 
    'x_main__mutmut_96': x_main__mutmut_96, 
    'x_main__mutmut_97': x_main__mutmut_97, 
    'x_main__mutmut_98': x_main__mutmut_98, 
    'x_main__mutmut_99': x_main__mutmut_99, 
    'x_main__mutmut_100': x_main__mutmut_100, 
    'x_main__mutmut_101': x_main__mutmut_101, 
    'x_main__mutmut_102': x_main__mutmut_102, 
    'x_main__mutmut_103': x_main__mutmut_103, 
    'x_main__mutmut_104': x_main__mutmut_104, 
    'x_main__mutmut_105': x_main__mutmut_105, 
    'x_main__mutmut_106': x_main__mutmut_106, 
    'x_main__mutmut_107': x_main__mutmut_107, 
    'x_main__mutmut_108': x_main__mutmut_108, 
    'x_main__mutmut_109': x_main__mutmut_109, 
    'x_main__mutmut_110': x_main__mutmut_110
}

def main(*args, **kwargs):
    result = _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs)
    return result 

main.__signature__ = _mutmut_signature(x_main__mutmut_orig)
x_main__mutmut_orig.__name__ = 'x_main'


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
