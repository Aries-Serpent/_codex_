"""Diff hygiene analysis used by the ITA."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Sequence

from .models import RepoHygieneIssue, RepoHygieneRequest

_SECRET_PATTERNS = [
    re.compile(r"AWS_(ACCESS|SECRET)_KEY", re.IGNORECASE),
    re.compile(r"-----BEGIN (RSA|DSA|EC) PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9]{20,}"),
]

_LICENSE_HEADER_PATTERN = re.compile(r"Copyright \(c\)\s+20\d{2}")


@dataclass(frozen=True)
class HygieneCheckResult:
    check: str
    issues: Sequence[RepoHygieneIssue]


def _check_format(lines: List[str]) -> Sequence[RepoHygieneIssue]:
    issues: List[RepoHygieneIssue] = []
    for line_no, line in enumerate(lines, start=1):
        if line.rstrip("\n").endswith(" "):
            issues.append(
                RepoHygieneIssue(
                    type="format",
                    path="*",
                    message=f"Trailing whitespace detected on line {line_no}",
                    severity="warn",
                )
            )
    return issues


def _check_lint(lines: List[str]) -> Sequence[RepoHygieneIssue]:
    issues: List[RepoHygieneIssue] = []
    for line_no, line in enumerate(lines, start=1):
        if "print(" in line and "TODO" in line:
            issues.append(
                RepoHygieneIssue(
                    type="lint",
                    path="*",
                    message=f"Debug print with TODO found on line {line_no}",
                    severity="warn",
                )
            )
    return issues


def _check_secrets(lines: List[str]) -> Sequence[RepoHygieneIssue]:
    issues: List[RepoHygieneIssue] = []
    for line_no, line in enumerate(lines, start=1):
        for pattern in _SECRET_PATTERNS:
            if pattern.search(line):
                issues.append(
                    RepoHygieneIssue(
                        type="secrets",
                        path="*",
                        message=f"Potential secret detected on line {line_no}",
                        severity="error",
                    )
                )
                break
    return issues


def _check_license(lines: List[str]) -> Sequence[RepoHygieneIssue]:
    issues: List[RepoHygieneIssue] = []
    if any(line.startswith("+++") for line in lines):
        added_files = [line for line in lines if line.startswith("+++ ")]
        for entry in added_files:
            if not _LICENSE_HEADER_PATTERN.search("".join(lines)):
                issues.append(
                    RepoHygieneIssue(
                        type="license",
                        path=entry.replace("+++ b/", ""),
                        message="New file missing copyright header placeholder",
                        severity="info",
                    )
                )
    return issues


_AVAILABLE_CHECKS = {
    "format": _check_format,
    "lint": _check_lint,
    "secrets": _check_secrets,
    "license": _check_license,
}


def run_hygiene_checks(request: RepoHygieneRequest) -> List[RepoHygieneIssue]:
    requested = request.checks or list(_AVAILABLE_CHECKS.keys())
    unknown = sorted(set(requested) - set(_AVAILABLE_CHECKS.keys()))
    if unknown:
        raise ValueError(f"Unsupported hygiene checks requested: {', '.join(unknown)}")

    lines = request.diff.splitlines()
    issues: List[RepoHygieneIssue] = []
    for check in requested:
        issues.extend(_AVAILABLE_CHECKS[check](lines))
    return issues


__all__ = ["run_hygiene_checks"]
