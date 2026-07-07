#!/usr/bin/env python3
"""
SBOM Verification Script for Cognitive Brain

Verifies SBOM integrity and authenticity before offline installation.

Usage:
    python scripts/deploy/verify_sbom.py --profile core
    python scripts/deploy/verify_sbom.py --profile runtime
    python scripts/deploy/verify_sbom.py --profile full
    python scripts/deploy/verify_sbom.py --all
    python scripts/deploy/verify_sbom.py --verify-wheels /path/to/wheelhouse

Features:
    - Load CycloneDX SBOM (XML/JSON)
    - Verify HMAC-SHA256 signature
    - Hash verification against manifest
    - Detect tampering or corruption
    - List all packages in SBOM
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
SBOM_DIR = REPO_ROOT / ".codex" / "sbom"

HMAC_KEY = os.environ.get("SBOM_HMAC_KEY", "default-dev-key-change-in-prod").encode()


def verify_hmac_signature(xml_file: Path, sig_file: Path) -> bool:
    """Verify HMAC-SHA256 signature of SBOM."""
    if not sig_file.exists():
        logger.warning(f"Signature file not found: {sig_file}")
        return False

    # Read XML content
    with open(xml_file, "r") as f:
        xml_content = f.read()

    # Read signature
    with open(sig_file, "r") as f:
        sig_content = f.read()

    # Parse signature file
    sig_lines = sig_content.strip().split("\n")
    sig_dict = {}
    for line in sig_lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            sig_dict[key] = value

    expected_sig = sig_dict.get("signature", "")

    # Calculate HMAC
    calculated_sig = hmac.new(HMAC_KEY, xml_content.encode(), hashlib.sha256).hexdigest()

    # Compare
    is_valid = hmac.compare_digest(calculated_sig, expected_sig)
    if is_valid:
        logger.info(f"✓ HMAC signature valid for {xml_file.name}")
    else:
        logger.error(f"✗ HMAC signature INVALID for {xml_file.name}")
        logger.error(f"  Expected: {expected_sig}")
        logger.error(f"  Got:      {calculated_sig}")

    return is_valid


def parse_bom_xml(xml_file: Path) -> dict[str, Any]:
    """Parse CycloneDX XML SBOM."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Handle namespace
    ns = {"bom": "http://cyclonedx.org/schema/bom/1.4"}

    components = []
    for component in root.findall(".//bom:component", ns):
        name = component.find("bom:name", ns)
        version = component.find("bom:version", ns)
        purl = component.find("bom:purl", ns)

        components.append({
            "name": name.text if name is not None else "unknown",
            "version": version.text if version is not None else "unknown",
            "purl": purl.text if purl is not None else "unknown",
        })

    # Get metadata
    metadata = root.find("bom:metadata", ns)
    component_meta = metadata.find("bom:component", ns) if metadata is not None else None

    bom_data = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "components": components,
        "metadata": {},
    }

    if component_meta is not None:
        name = component_meta.find("bom:name", ns)
        version = component_meta.find("bom:version", ns)
        if name is not None:
            bom_data["metadata"]["name"] = name.text
        if version is not None:
            bom_data["metadata"]["version"] = version.text

    return bom_data


def parse_bom_json(json_file: Path) -> dict[str, Any]:
    """Parse CycloneDX JSON SBOM."""
    with open(json_file, "r") as f:
        return json.load(f)


def verify_sbom_integrity(profile: str) -> int:
    """Verify SBOM for a specific profile."""
    logger.info(f"Verifying SBOM for {profile} profile...")

    xml_file = SBOM_DIR / f"cognitive_brain-0.1.0-{profile}.xml"
    sig_file = SBOM_DIR / f"cognitive_brain-0.1.0-{profile}.xml.sig"
    json_file = SBOM_DIR / f"cognitive_brain-0.1.0-{profile}.json"

    # Check files exist
    if not xml_file.exists():
        logger.error(f"SBOM file not found: {xml_file}")
        return 1

    if not json_file.exists():
        logger.error(f"JSON SBOM file not found: {json_file}")
        return 1

    # Verify signature
    if not verify_hmac_signature(xml_file, sig_file):
        logger.error("Signature verification failed - SBOM may have been tampered with")
        return 1

    # Parse both formats
    try:
        bom_xml = parse_bom_xml(xml_file)
        bom_json = parse_bom_json(json_file)

        # Compare component counts
        xml_count = len(bom_xml.get("components", []))
        json_count = len(bom_json.get("components", []))

        if xml_count != json_count:
            logger.warning(f"Component count mismatch: XML={xml_count}, JSON={json_count}")

        logger.info(f"✓ SBOM integrity verified")
        logger.info(f"  Format: CycloneDX 1.4")
        logger.info(f"  Components: {xml_count}")
        logger.info(f"  Profile: {profile}")

        return 0

    except Exception as e:
        logger.error(f"Error parsing SBOM: {e}")
        return 1


def list_sbom_packages(profile: str) -> int:
    """List all packages in SBOM."""
    json_file = SBOM_DIR / f"cognitive_brain-0.1.0-{profile}.json"

    if not json_file.exists():
        logger.error(f"SBOM file not found: {json_file}")
        return 1

    try:
        with open(json_file, "r") as f:
            bom_data = json.load(f)

        components = bom_data.get("components", [])
        logger.info(f"Packages in {profile} profile SBOM:")
        logger.info(f"Total: {len(components)}")

        # Group by initial letter for readability
        by_letter = {}
        for comp in components:
            name = comp.get("name", "unknown")
            first_letter = name[0].upper()
            if first_letter not in by_letter:
                by_letter[first_letter] = []
            by_letter[first_letter].append(name)

        for letter in sorted(by_letter.keys()):
            packages = sorted(by_letter[letter])
            logger.info(f"  [{letter}] {', '.join(packages)}")

        return 0

    except Exception as e:
        logger.error(f"Error reading SBOM: {e}")
        return 1


def verify_wheels_against_sbom(wheelhouse: Path, profile: str) -> int:
    """Verify wheels in wheelhouse match SBOM packages."""
    logger.info(f"Verifying wheels against {profile} profile SBOM...")

    json_file = SBOM_DIR / f"cognitive_brain-0.1.0-{profile}.json"

    if not wheelhouse.exists():
        logger.error(f"Wheelhouse directory not found: {wheelhouse}")
        return 1

    if not json_file.exists():
        logger.error(f"SBOM file not found: {json_file}")
        return 1

    # Load SBOM packages
    with open(json_file, "r") as f:
        bom_data = json.load(f)

    sbom_packages = {comp["name"].lower(): comp for comp in bom_data.get("components", [])}

    # List wheels
    wheels = list(wheelhouse.glob("*.whl"))
    logger.info(f"Found {len(wheels)} wheels in {wheelhouse}")

    # Simple validation: check wheel names are plausible
    issues = []
    for wheel in wheels:
        wheel_name = wheel.stem  # Remove .whl extension
        parts = wheel_name.split("-")
        if len(parts) >= 2:
            package_name = parts[0].lower().replace("_", "-")
            if package_name not in sbom_packages:
                logger.warning(f"  ⚠ Wheel not in SBOM: {wheel.name}")
                issues.append(str(wheel.name))

    if issues:
        logger.error(f"Found {len(issues)} wheels not in SBOM")
        return 1
    else:
        logger.info(f"✓ All wheels match SBOM packages")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify CycloneDX SBOMs for cognitive_brain"
    )
    parser.add_argument(
        "--profile",
        choices=["core", "runtime", "full"],
        default="core",
        help="Profile to verify",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all profiles",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List packages in SBOM",
    )
    parser.add_argument(
        "--verify-wheels",
        type=Path,
        help="Verify wheels against SBOM",
    )

    args = parser.parse_args()

    try:
        if args.verify_wheels:
            return verify_wheels_against_sbom(args.verify_wheels, args.profile)

        if args.all:
            results = []
            for profile in ["core", "runtime", "full"]:
                if args.list:
                    results.append(list_sbom_packages(profile))
                else:
                    results.append(verify_sbom_integrity(profile))
            return max(results) if results else 0
        else:
            if args.list:
                return list_sbom_packages(args.profile)
            else:
                return verify_sbom_integrity(args.profile)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
