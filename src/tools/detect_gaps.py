"""Lightweight gap detection utility for Codex tasks.

This script scans the repository for common configuration and packaging gaps
that routinely break CI jobs. It intentionally uses only the standard library
so it can run in constrained environments.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Gap:
    """Represents a single actionable gap in the repository."""

    id: str
    severity: str
    description: str
    remediation: str


DEFAULT_GAPS: Sequence[Gap] = (
    Gap(
        id="codex_plans_package",
        severity="high",
        description="Missing codex_plans package directory",
        remediation="Ensure src/codex_plans exists with an __init__.py file.",
    ),
    Gap(
        id="bandit_config",
        severity="medium",
        description="Bandit configuration should exist at bandit.yaml",
        remediation="Create bandit.yaml with repository-specific skips and excludes.",
    ),
    Gap(
        id="docker_base",
        severity="medium",
        description="Dockerfiles should avoid deprecated Debian buster images",
        remediation="Replace debian:buster bases with debian:bullseye-slim or newer.",
    ),
)


def discover_gaps(repo_root: Path) -> list[Gap]:
    """Return gaps that are currently present in the repository."""

    results: list[Gap] = []

    codex_plans = repo_root / "src" / "codex_plans" / "__init__.py"
    if not codex_plans.exists():
        results.append(DEFAULT_GAPS[0])

    bandit_config = repo_root / "bandit.yaml"
    if not bandit_config.exists():
        results.append(DEFAULT_GAPS[1])

    dockerfiles = list(repo_root.glob("**/Dockerfile*"))
    for dockerfile in dockerfiles:
        try:
            content = dockerfile.read_text(encoding="utf-8")
        except OSError:
            continue
        if "debian:buster" in content:
            results.append(DEFAULT_GAPS[2])
            break

    return results


def format_gaps(gaps: Iterable[Gap], output_format: str) -> str:
    if output_format == "json":
        return json.dumps([asdict(gap) for gap in gaps], indent=2)

    lines = ["Detected gaps:"]
    for gap in gaps:
        lines.append(f"- [{gap.severity}] {gap.id}: {gap.description}")
        lines.append(f"  Remediation: {gap.remediation}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect repository gaps")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root directory",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args()

    gaps = discover_gaps(args.repo_root)
    output = format_gaps(gaps, args.format)
    print(output)


if __name__ == "__main__":
    main()
