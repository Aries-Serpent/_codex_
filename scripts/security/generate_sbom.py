#!/usr/bin/env python
"""
Generate Sbom

Purpose:
    Generates sbom

Usage:
    python scripts/security/generate_sbom.py [options]

    Examples:
    $ python scripts/security/generate_sbom.py --help

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
from pathlib import Path

# Offline CycloneDX-like minimal SBOM generator using stdlib only.


def list_distributions():
    try:
        from importlib.metadata import distributions  # py3.8+

        for dist in distributions():
            yield dist
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        # Fallback: pip freeze

        # Not reliable; advise using importlib.metadata
        pass


def sbom() -> dict:
    comps = []
    try:
        from importlib.metadata import distributions

        for d in distributions():
            name = d.metadata.get("Name") or d.metadata.get("Summary") or str(d)
            version = d.version
            comps.append(
                {
                    "type": "library",
                    "name": name,
                    "version": version,
                    "purl": f"pkg:pypi/{name}@{version}".lower(),
                }
            )
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        pass
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": "urn:uuid:offline-local",
        "version": 1,
        "components": sorted(comps, key=lambda c: (c["name"] or "").lower()),
        "metadata": {"tools": [{"vendor": "codex", "name": "sbom-generator", "version": "1.0.0"}]},
    }


def main():
    ap = argparse.ArgumentParser(description="Offline SBOM generator (CycloneDX-like, minimal)")
    ap.add_argument("--out", default="artifacts/security/sbom.json", help="Output path")
    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = sbom()
    out.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    print(f"SBOM written: {out}")


if __name__ == "__main__":
    main()
