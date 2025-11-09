#!/usr/bin/env python3
"""CLI to validate dataset manifest files."""

from __future__ import annotations

import argparse
from pathlib import Path

from codex_ml.data.validator import DatasetValidator


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate dataset manifests")
    parser.add_argument("manifest", type=Path, help="Path to manifest JSON file")
    parser.add_argument(
        "--check-splits",
        action="store_true",
        help="Verify referenced split/checksum files exist",
    )
    args = parser.parse_args()

    manifest_valid = DatasetValidator.validate_manifest(args.manifest)
    if args.check_splits:
        manifest_valid = manifest_valid and DatasetValidator.validate_splits(args.manifest)
    return 0 if manifest_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
