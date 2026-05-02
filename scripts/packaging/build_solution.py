#!/usr/bin/env python3
"""
Build Solution

Purpose:
    Builds solution

Usage:
    python scripts/packaging/build_solution.py [options]

    Examples:
    $ python scripts/packaging/build_solution.py --help

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

import argparse
import hashlib
import json
import logging
import shutil
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO_ROOT / "configs" / "packaging" / "zendesk_quantum_packages.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "build" / "solutions"


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load the packaging manifest YAML."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with manifest_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Invalid manifest: expected dictionary")

    return data


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def copy_includes(
    package_root: Path,
    repo_root: Path,
    includes: list[str],
) -> list[dict[str, str]]:
    """Copy included files/directories to package root.

    Returns:
        List of file manifests with paths and hashes
    """
    file_manifest = []

    def ignore_patterns(directory: str, names: list[str]) -> set[str]:
        """Ignore patterns for shutil.copytree."""
        ignored = set()
        for name in names:
            if name in {"__pycache__", ".pyc", ".pytest_cache", ".git"} or name.endswith((".pyc", ".pyo", ".pyd", ".so", ".dylib")) or name.endswith((".egg-info", ".dist-info")):
                ignored.add(name)
        return ignored

    for entry in includes:
        source = repo_root / entry

        if not source.exists():
            logger.warning(f"Include path not found: {source}")
            continue

        destination = package_root / entry

        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
                ignore=ignore_patterns,
            )
            # Add all files in directory to manifest
            for file_path in destination.rglob("*"):
                if file_path.is_file():
                    file_manifest.append({
                        "path": str(file_path.relative_to(package_root)),
                        "hash": calculate_file_hash(file_path),
                    })
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            file_manifest.append({
                "path": str(destination.relative_to(package_root)),
                "hash": calculate_file_hash(destination),
            })

    return file_manifest


def create_package_metadata(
    package_spec: dict[str, Any],
    file_manifest: list[dict[str, str]],
    version: str,
) -> dict[str, Any]:
    """Create package metadata dictionary."""
    return {
        "package_name": package_spec.get("name", "unknown"),
        "version": version,
        "description": package_spec.get("description", ""),
        "entry_point": package_spec.get("entry_point", ""),
        "target_platform": package_spec.get("target_platform", []),
        "capabilities": package_spec.get("capabilities", []),
        "dependencies": package_spec.get("dependencies", {}),
        "physics_paradigms": package_spec.get("physics_paradigms", []),
        "integration": package_spec.get("integration", {}),
        "created_at": datetime.now().isoformat(),
        "file_manifest": file_manifest,
    }


def write_readme(package_root: Path, metadata: dict[str, Any]) -> None:
    """Write package README."""
    content = [
        f"# {metadata['package_name']}",
        "",
        metadata.get("description", ""),
        "",
        f"**Version:** {metadata['version']}",
        f"**Created:** {metadata['created_at']}",
        "",
    ]

    if metadata.get("entry_point"):
        content.extend([
            "## Entry Point",
            "",
            "```python",
            f"{metadata['entry_point']}",
            "```",
            "",
        ])

    if metadata.get("capabilities"):
        content.extend([
            "## Capabilities",
            "",
        ])
        content.extend([f"- {cap}" for cap in metadata["capabilities"]])
        content.append("")

    if metadata.get("dependencies"):
        content.extend([
            "## Dependencies",
            "",
            "```json",
            json.dumps(metadata["dependencies"], indent=2),
            "```",
            "",
        ])

    if metadata.get("physics_paradigms"):
        content.extend([
            "## Physics Paradigms",
            "",
        ])
        content.extend([f"- {paradigm}" for paradigm in metadata["physics_paradigms"]])
        content.append("")

    readme_path = package_root / "README.md"
    readme_path.write_text("\n".join(content), encoding="utf-8")


def write_manifest(package_root: Path, metadata: dict[str, Any]) -> None:
    """Write package manifest JSON."""
    manifest_path = package_root / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def create_archive(
    package_root: Path,
    output_path: Path,
    archive_format: str = "zip",
) -> Path:
    """Create archive from package directory.

    Args:
        package_root: Directory to archive
        output_path: Output archive path (without extension)
        archive_format: "zip" or "tar.gz"

    Returns:
        Path to created archive
    """
    if archive_format == "zip":
        archive_path = output_path.with_suffix(".zip")
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_root.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_root.parent)
                    zipf.write(file_path, arcname)

    elif archive_format == "tar.gz":
        archive_path = output_path.with_suffix(".tar.gz")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(package_root, arcname=package_root.name)

    else:
        raise ValueError(f"Unsupported archive format: {archive_format}")

    return archive_path


def build_solution_package(
    package_spec: dict[str, Any],
    repo_root: Path,
    output_dir: Path,
    version: str,
    archive_format: str = "zip",
) -> Path:
    """Build a solution package.

    Args:
        package_spec: Package specification from manifest
        repo_root: Repository root directory
        output_dir: Output directory for packages
        version: Version string for the package
        archive_format: Archive format ("zip" or "tar.gz")

    Returns:
        Path to created archive
    """
    package_name = package_spec.get("name", "unknown")
    logger.info(f"Building package: {package_name}")

    # Create staging directory
    staging_dir = output_dir / "staging" / package_name
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True)

    # Create skeleton directories
    skeleton_dirs = package_spec.get("skeleton_dirs", [])
    for skeleton_dir in skeleton_dirs:
        (staging_dir / skeleton_dir).mkdir(parents=True, exist_ok=True)

    # Copy includes
    includes = package_spec.get("includes", [])
    file_manifest = copy_includes(staging_dir, repo_root, includes)

    logger.info(f"Copied {len(file_manifest)} files to package")

    # Create metadata
    metadata = create_package_metadata(package_spec, file_manifest, version)

    # Write README and manifest
    write_readme(staging_dir, metadata)
    write_manifest(staging_dir, metadata)

    # Create archive
    archive_output = output_dir / f"{package_name}-{version}"
    archive_path = create_archive(staging_dir, archive_output, archive_format)

    logger.info(f"Created archive: {archive_path}")

    # Calculate archive hash
    archive_hash = calculate_file_hash(archive_path)
    logger.info(f"Archive SHA256: {archive_hash}")

    # Write hash file
    hash_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    hash_path.write_text(f"{archive_hash}  {archive_path.name}\n")

    return archive_path


def build_all_solutions(
    manifest_path: Path,
    output_dir: Path,
    version: str | None = None,
    archive_format: str = "zip",
) -> list[Path]:
    """Build all solution packages from manifest.

    Args:
        manifest_path: Path to manifest YAML
        output_dir: Output directory
        version: Version override, or None to use manifest version
        archive_format: Archive format

    Returns:
        List of created archive paths
    """
    manifest = load_manifest(manifest_path)

    # Get version
    if version is None:
        version = manifest.get("version", "1.0.0")

    logger.info(f"Building solutions from {manifest_path}")
    logger.info(f"Version: {version}")
    logger.info(f"Output: {output_dir}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build packages
    packages = manifest.get("packages", [])
    archives = []

    for package_spec in packages:
        try:
            archive_path = build_solution_package(
                package_spec=package_spec,
                repo_root=REPO_ROOT,
                output_dir=output_dir,
                version=version,
                archive_format=archive_format,
            )
            archives.append(archive_path)
        except Exception as e:
            logger.error(f"Failed to build package {package_spec.get('name')}: {e}")

    # Create build summary
    summary = {
        "manifest": str(manifest_path),
        "version": version,
        "build_date": datetime.now().isoformat(),
        "packages_built": len(archives),
        "packages": [
            {
                "name": archive.stem,
                "path": str(archive),
                "size_bytes": archive.stat().st_size,
            }
            for archive in archives
        ],
    }

    summary_path = output_dir / f"build_summary_{version}.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Build summary: {summary_path}")

    return archives


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to packaging manifest YAML",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory for solution packages",
    )
    parser.add_argument(
        "--version",
        help="Version override (default: use manifest version)",
    )
    parser.add_argument(
        "--format",
        choices=["zip", "tar.gz"],
        default="zip",
        help="Archive format",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        archives = build_all_solutions(
            manifest_path=args.manifest,
            output_dir=args.output,
            version=args.version,
            archive_format=args.format,
        )

        print(f"\n{'='*60}")
        print("Solution Packaging Complete")
        print(f"{'='*60}")
        print(f"Built {len(archives)} packages:")
        for archive in archives:
            size_mb = archive.stat().st_size / (1024 * 1024)
            print(f"  - {archive.name} ({size_mb:.2f} MB)")
        print(f"{'='*60}\n")

        return 0

    except Exception as e:
        logger.error(f"Build failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
