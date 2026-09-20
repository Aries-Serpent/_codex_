from __future__ import annotations

import argparse
import json
from pathlib import Path

from .copilot_tools import TOOLS


def main() -> int:
    parser = argparse.ArgumentParser(description="Docs agent MCP-compatible tool server")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--tool", help="Tool name to call")
    parser.add_argument("--input-json", default="{}", help="JSON input payload")
    parser.add_argument("--list-tools", action="store_true")
    args = parser.parse_args()

    if args.list_tools:
        print(json.dumps({"tools": sorted(TOOLS.keys())}, sort_keys=True))
        return 0

    if not args.tool:
        print(json.dumps({"tools": sorted(TOOLS.keys()), "mode": "tool-bridge"}, sort_keys=True))
        return 0

    if args.tool not in TOOLS:
        print(json.dumps({"error": f"unknown tool {args.tool}"}, sort_keys=True))
        return 2

    payload = json.loads(args.input_json)
    fn = TOOLS[args.tool]
    result = fn(Path(args.repo_root), **payload)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
