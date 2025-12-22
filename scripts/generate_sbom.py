#!/usr/bin/env python3
"""Generate Software Bill of Materials (SBOM) for the project.

This script generates a CycloneDX-format SBOM containing all project dependencies
for supply chain security and vulnerability tracking.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

__all__ = ["generate_sbom", "main"]


def get_installed_packages() -> List[Dict[str, str]]:
    """Get list of installed packages using pip freeze.

    Returns:
        List of dicts with package name and version
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True
        )

        packages = []
        for line in result.stdout.strip().split("\n"):
            if line and "==" in line:
                name, version = line.split("==", 1)
                packages.append({"name": name, "version": version})

        return packages
    except subprocess.CalledProcessError as e:
        print(f"Error getting installed packages: {e}", file=sys.stderr)
        return []


def generate_sbom_cyclonedx(output_path: Path, packages: List[Dict[str, str]]) -> None:
    """Generate SBOM in CycloneDX JSON format.

    Args:
        output_path: Path where SBOM will be saved
        packages: List of package dicts with name and version
    """
    # Try using cyclonedx-bom if available
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "cyclonedx_py",
                "--format",
                "json",
                "--output",
                str(output_path),
            ],
            check=True,
            capture_output=True,
        )
        print(f"✓ SBOM generated using cyclonedx-bom: {output_path}")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("cyclonedx-bom not available, generating manual SBOM")

    # Fallback: manual SBOM generation
    sbom: Dict[str, Any] = {
        "$schema": "http://cyclonedx.org/schema/bom-1.4.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": f"urn:uuid:codex-{output_path.stem}",
        "version": 1,
        "metadata": {
            "timestamp": None,  # Would use datetime.utcnow().isoformat() + "Z"
            "tools": [
                {"vendor": "Aries-Serpent", "name": "codex-sbom-generator", "version": "1.0.0"}
            ],
            "component": {
                "type": "application",
                "name": "codex",
                "version": "0.1.0",
                "description": "Codex ML training framework",
            },
        },
        "components": [],
    }

    # Add components (packages)
    for pkg in packages:
        component = {
            "type": "library",
            "name": pkg["name"],
            "version": pkg["version"],
            "purl": f"pkg:pypi/{pkg['name']}@{pkg['version']}",
        }
        sbom["components"].append(component)

    # Write SBOM
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sbom, f, indent=2, sort_keys=True)

    print(f"✓ SBOM generated manually: {output_path}")
    print(f"  Components: {len(packages)}")


def generate_sbom(output_path: str | Path = "sbom.json") -> Path:
    """Generate SBOM for the project.

    Args:
        output_path: Path where SBOM will be saved (default: sbom.json)

    Returns:
        Path to generated SBOM file
    """
    output_path = Path(output_path)

    print("Generating Software Bill of Materials (SBOM)...")

    # Get installed packages
    packages = get_installed_packages()
    print(f"Found {len(packages)} installed packages")

    # Generate SBOM
    generate_sbom_cyclonedx(output_path, packages)

    return output_path


def main(argv: List[str] | None = None) -> int:
    """Main entry point for SBOM generation.

    Args:
        argv: Command line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 for success)
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Software Bill of Materials (SBOM)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate SBOM in current directory
  python generate_sbom.py
  
  # Generate SBOM in dist directory
  python generate_sbom.py --output dist/sbom.json
  
  # Install cyclonedx-bom for better SBOM generation
  pip install cyclonedx-bom
""",
    )

    parser.add_argument(
        "--output", "-o", default="sbom.json", help="Output path for SBOM file (default: sbom.json)"
    )

    args = parser.parse_args(argv)

    try:
        sbom_path = generate_sbom(args.output)
        print(f"\n✅ SBOM generation complete: {sbom_path}")
        return 0
    except Exception as e:
        logger.debug(f"Exception: {e}")
        print(f"\n❌ SBOM generation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
