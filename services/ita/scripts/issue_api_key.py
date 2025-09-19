"""CLI helper to issue an API key for the Internal Tools API."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.security import ApiKeyStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Issue a short-lived API key for the ITA.")
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Optional custom location for the hashed key store (defaults to $ITA_API_KEYS_PATH or runtime/api_keys.json)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    store = ApiKeyStore(path=args.path)
    key = store.issue_key()
    print(key)
    return 0


if __name__ == "__main__":
    sys.exit(main())
