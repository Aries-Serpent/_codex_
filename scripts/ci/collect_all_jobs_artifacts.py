#!/usr/bin/env python3
"""
Collect all jobs and artifacts for PR #3248 failing workflow runs.
This script uses the run IDs from failing_checks.md and calls GitHub MCP tools.
"""


# Extract all run IDs from failing_checks.md
run_ids = [
    22027661337, 22027661294, 22027661310, 22026389814, 22026313981,
    22026314012, 22026313973, 22026314005, 22026314000, 22026313988,
    22024110777, 22024110778, 22024110753, 22024110754, 22024110767,
    22024110781, 22023621614, 22023621613, 22023621610, 22023621608,
    22023621587, 22023621573, 22023512543, 22023461298, 22023381775,
    22023381762, 22023381763, 22023381774, 22022552790, 22022207105,
    22022207108, 22022207107, 22021853627, 22021853613, 22021853619,
    22018172941, 22018172903, 22018172928, 22009637111, 22009637115,
    22007189326, 22007189304, 22004882338, 21997453266
]


if __name__ == "__main__":
    print(f"Total run IDs to process: {len(run_ids)}")
    print(f"Run IDs: {run_ids[:5]}... (showing first 5)")
    print("\nTo collect jobs and artifacts, use:")
    print("github-mcp-server-actions_list(method='list_workflow_jobs', owner='Aries-Serpent', repo='_codex_', resource_id=RUN_ID)")
    print("github-mcp-server-actions_list(method='list_workflow_run_artifacts', owner='Aries-Serpent', repo='_codex_', resource_id=RUN_ID)")
