from __future__ import annotations

import argparse

MODULES = {
    "inventory": "tools.docs_agent.inventory",
    "changed_candidates": "tools.docs_agent.changed_candidates",
    "coverage": "tools.docs_agent.coverage",
    "convert": "tools.docs_agent.convert",
    "validate": "tools.docs_agent.validate",
    "build_index": "tools.docs_agent.build_index",
    "query": "tools.docs_agent.query",
    "task_brief": "tools.docs_agent.task_brief",
    "impact": "tools.docs_agent.impact",
    "no_unmanaged_candidates": "tools.docs_agent.no_unmanaged_candidates",
    "mcp_server": "tools.docs_agent.mcp_server",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="docs_agent command dispatcher")
    parser.add_argument("command", choices=sorted(MODULES))
    parser.add_argument("args", nargs=argparse.REMAINDER)
    ns = parser.parse_args()

    import runpy
    import sys

    sys.argv = [ns.command] + ns.args
    runpy.run_module(MODULES[ns.command], run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
