"""
Sbom Cyclonedx

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/sbom_cyclonedx.py [options]

    Examples:
    $ python scripts/sbom_cyclonedx.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import argparse
import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from packaging.version import parse as parse_version

ARTIFACT_ROOT = Path("artifacts")
SBOM_DIR = ARTIFACT_ROOT / "sbom"
DEFAULT_OUTPUT = SBOM_DIR / "cyclonedx.json"
DEFAULT_PACKAGE_LIST = SBOM_DIR / "packages.txt"
LOCK_CANDIDATES = ("requirements/lock.txt", "uv.lock")


@dataclass
class PackageRecord:
    """Canonical representation of a locked dependency."""

    name: str
    version: str
    sources: set[str] = field(default_factory=set)

    def as_component(self) -> dict[str, object]:
        purl = f"pkg:pypi/{self.name.lower()}@{self.version}"
        properties: list[dict[str, str]] = []
        if self.sources:
            properties.append(
                {
                    "name": "codex:lock-source",
                    "value": ",".join(sorted(self.sources)),
                }
            )
        component: dict[str, object] = {
            "type": "library",
            "name": self.name,
            "version": self.version,
            "bom-ref": purl,
            "purl": purl,
            "scope": "required",
        }
        if properties:
            component["properties"] = properties
        return component


def _iter_lock_paths(explicit: Sequence[str] | None) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for raw in explicit or ():
        candidate = Path(raw).resolve()
        if candidate.exists() and candidate not in seen:
            paths.append(candidate)
            seen.add(candidate)
    if not paths:
        for name in LOCK_CANDIDATES:
            candidate = Path(name)
            if candidate.exists() and candidate.resolve() not in seen:
                paths.append(candidate.resolve())
                seen.add(candidate.resolve())
    return paths


def _parse_requirements_lock(path: Path) -> Iterable[PackageRecord]:
    records: list[PackageRecord] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return records
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            continue
        name_part, version = line.split("==", 1)
        name = name_part.split("[", 1)[0].strip()
        version = version.strip()
        if not name or not version:
            continue
        records.append(PackageRecord(name=name, version=version, sources={path.name}))
    return records


def _parse_uv_lock(path: Path) -> Iterable[PackageRecord]:
    records: list[PackageRecord] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return records

    current_name: str | None = None
    current_version: str | None = None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[[") and line.endswith("]]"):
            if current_name and current_version:
                records.append(
                    PackageRecord(
                        name=current_name,
                        version=current_version,
                        sources={path.name},
                    )
                )
            current_name = None
            current_version = None
            continue
        if line.startswith("name ="):
            current_name = line.split("=", 1)[1].split("#", 1)[0].strip().strip('"')
        elif line.startswith("version ="):
            current_version = line.split("=", 1)[1].split("#", 1)[0].strip().strip('"')
    if current_name and current_version:
        records.append(
            PackageRecord(name=current_name, version=current_version, sources={path.name})
        )
    return records


def _collect_packages(paths: Iterable[Path]) -> list[PackageRecord]:
    catalog: dict[str, PackageRecord] = {}
    for path in paths:
        if path.name.endswith(".lock") and path.name != "uv.lock":
            candidates = _parse_requirements_lock(path)
        elif path.name == "uv.lock":
            candidates = _parse_uv_lock(path)
        else:
            candidates = _parse_requirements_lock(path)
        for record in candidates:
            key = record.name.lower()
            existing = catalog.get(key)
            if existing is None:
                catalog[key] = record
                continue
            if parse_version(record.version) > parse_version(existing.version):
                record.sources.update(existing.sources)
                catalog[key] = record
            else:
                existing.sources.update(record.sources)
    return [catalog[key] for key in sorted(catalog)]


def _build_bom(
    records: Sequence[PackageRecord], project_name: str, project_version: str | None
) -> dict[str, object]:
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    metadata: dict[str, object] = {
        "timestamp": timestamp,
        "tools": [
            {
                "vendor": "codex",
                "name": "sbom_cyclonedx.py",
                "version": "offline",
            }
        ],
    }
    component: dict[str, object] = {"type": "application", "name": project_name}
    if project_version:
        component["version"] = project_version
    metadata["component"] = component
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": metadata,
        "components": [record.as_component() for record in records],
    }


def _write_packages_txt(records: Sequence[PackageRecord], output: Path) -> None:
    lines = [
        f"{record.name}=={record.version}  # {', '.join(sorted(record.sources))}".rstrip()
        for record in records
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate an offline CycloneDX SBOM from repository lock files.",
    )
    parser.add_argument(
        "--lock",
        action="append",
        dest="locks",
        help="Optional explicit lock files (can be supplied multiple times).",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to the CycloneDX JSON output (default: artifacts/sbom/cyclonedx.json).",
    )
    parser.add_argument(
        "--packages-output",
        default=str(DEFAULT_PACKAGE_LIST),
        help="Write a plaintext package list for auditors (default: artifacts/sbom/packages.txt).",
    )
    parser.add_argument(
        "--project-name",
        default=Path.cwd().name,
        help="Name recorded as the application component in the SBOM metadata.",
    )
    parser.add_argument(
        "--project-version",
        default=None,
        help="Optional version string recorded in SBOM metadata.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    lock_paths = _iter_lock_paths(args.locks)
    if not lock_paths:
        print(
            "No lock files discovered; provide --lock or create requirements/lock.txt/uv.lock",
            file=sys.stderr,
        )
        return 2

    records = _collect_packages(lock_paths)
    if not records:
        print("Lock files did not yield any packages", file=sys.stderr)
        return 3

    SBOM_DIR.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()
    package_list_path = Path(args.packages_output)
    if not package_list_path.is_absolute():
        package_list_path = (Path.cwd() / package_list_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    package_list_path.parent.mkdir(parents=True, exist_ok=True)

    bom = _build_bom(records, project_name=args.project_name, project_version=args.project_version)
    output_path.write_text(json.dumps(bom, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_packages_txt(records, package_list_path)

    print(f"SBOM written to {output_path}")
    print(f"Package inventory written to {package_list_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
