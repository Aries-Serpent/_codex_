#!/usr/bin/env python3
"""
Generate Wheel Manifest

Purpose:
    Generates wheel_manifest

Usage:
    python scripts/ci/generate_wheel_manifest.py [options]
    
    Examples:
    $ python scripts/ci/generate_wheel_manifest.py --help

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


"""
Generate a reproducible wheel manifest with cryptographic hashes.

This script creates a baseline artifact lock file that includes:
- Wheel filenames
- SHA256 hashes
- Platform information
- Python version

Usage:
    python scripts/ci/generate_wheel_manifest.py --wheelhouse /path/to/wheels --output manifest.json
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def compute_sha256(filepath: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_manifest(wheelhouse_dir: Path, platform: str, python_version: str) -> dict:
    """Generate wheel manifest with hashes."""
    wheels = []

    if not wheelhouse_dir.exists():
        print(f"Warning: Wheelhouse directory {wheelhouse_dir} does not exist", file=sys.stderr)
        return {"platform": platform, "python_version": python_version, "wheels": [], "count": 0}

    for wheel_file in sorted(wheelhouse_dir.glob("*.whl")):
        wheel_info = {
            "name": wheel_file.name,
            "sha256": compute_sha256(wheel_file),
            "size": wheel_file.stat().st_size,
        }
        wheels.append(wheel_info)

    manifest = {
        "platform": platform,
        "python_version": python_version,
        "wheels": wheels,
        "count": len(wheels),
    }

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate wheel manifest with hashes")
    parser.add_argument(
        "--wheelhouse", type=Path, required=True, help="Path to wheelhouse directory"
    )
    parser.add_argument("--output", type=Path, required=True, help="Output manifest file path")
    parser.add_argument(
        "--platform", default="linux/amd64", help="Platform identifier (default: linux/amd64)"
    )
    parser.add_argument("--python-version", default="3.11", help="Python version (default: 3.11)")

    args = parser.parse_args()

    manifest = generate_manifest(args.wheelhouse, args.platform, args.python_version)

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Write manifest
    with open(args.output, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    print(f"Generated manifest: {args.output}")
    print(f"  Platform: {manifest['platform']}")
    print(f"  Python: {manifest['python_version']}")
    print(f"  Wheels: {manifest['count']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
