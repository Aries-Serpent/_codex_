#!/usr/bin/env python3
"""
Prepare Repo Status Prompt

Purpose:
    Main execution script

Usage:
    python scripts/prepare_repo_status_prompt.py [options]
    
    Examples:
    $ python scripts/prepare_repo_status_prompt.py --help

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

from pathlib import Path

from codex_audit.prompting import prepare_repo_status_prompt
from codex_audit.policy import write_policy_mapping
from codex_audit.gates import run_gates


def main() -> int:
    repo_root = Path.cwd()
    policy_path = repo_root / "artifacts" / "ra_policy_map.json"
    gate_path = repo_root / "artifacts" / "gate_results.json"
    scorecard_path = repo_root / "artifacts" / "repo_audit_scorecard.md"
    output_prompt = repo_root / "artifacts" / "repo_status_update_prompt.txt"

    policy_map = write_policy_mapping(policy_path)
    run_gates(repo_root=repo_root, output_path=gate_path)
    prepare_repo_status_prompt(
        gate_results_path=gate_path,
        policy_map_path=policy_path,
        scorecard_path=scorecard_path,
        output_path=output_prompt,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
