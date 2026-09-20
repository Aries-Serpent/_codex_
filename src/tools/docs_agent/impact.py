from __future__ import annotations

import argparse
import json
from pathlib import Path

from .query import query_impact
from .utils import parse_common_args


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Impact analysis for changed files")
    )
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--target-file", action="append", default=[])
    args = parser.parse_args()
    files = args.file + args.target_file
    result = query_impact(Path(args.repo_root), files)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
