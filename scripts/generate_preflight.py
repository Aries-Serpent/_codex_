#!/usr/bin/env python3
"""
Generate Preflight

Purpose:
    Generates preflight

Usage:
    python scripts/generate_preflight.py [options]
    
    Examples:
    $ python scripts/generate_preflight.py --help

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


"""
Pre-flight checklist generator for Codex operations.

Purpose: Automate pre-flight planning to address CODEX-005.
Usage: python scripts/generate_preflight.py --task "Apply security patch" --files "src/auth.py tests/test_auth.py"
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def get_git_context() -> dict[str, str]:
    """Retrieve current git context."""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()

        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()

        return {"branch": branch, "commit": commit}
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Warning: Could not get git context: {exc}")
        return {"branch": "unknown", "commit": "unknown"}


def identify_tools(files: list[str]) -> list[str]:
    """Identify tools needed based on file types."""
    tools: set[str] = set()

    for file_path in files:
        if file_path.endswith(".py"):
            tools.update({"python", "pytest", "mypy", "black"})
        elif file_path.endswith(".sh"):
            tools.update({"bash", "shellcheck"})
        elif file_path.endswith(".patch"):
            tools.update({"git", "apply_patch"})
        elif file_path.endswith(".json"):
            tools.add("jq")

    return sorted(tools)


def generate_checklist(task: str, files: list[str], pr_number: Optional[str] = None) -> str:
    """Generate a pre-flight checklist."""
    git_context = get_git_context()
    tools = identify_tools(files)
    now = datetime.now(timezone.utc)

    file_lines = "\n".join(f"  - [ ] {path}" for path in files)

    checklist = f"""
## Operation: {task}

**Date (UTC)**: {now.strftime('%Y-%m-%d %H:%M:%S')}
**Operator**: [YOUR NAME]
**Branch**: {git_context['branch'] or 'unknown'}
**Commit**: {git_context['commit'] or 'unknown'}
**PR Number**: {pr_number or 'N/A'}

### Phase 1: Context Collection
- [ ] Read ALL source files
{file_lines}
- [ ] Identified file locations and line numbers
- [ ] Documented current state (size, key functions, interdependencies)
- [ ] Checked for existing tests, examples, templates
- [ ] Gathered git context (done: branch={git_context['branch']}, commit={git_context['commit']})

### Phase 2: Tool Inventory
- [ ] Listed all operations: Create, Read, Update, Delete, Validate
- [ ] Mapped each operation to tool
  - Identified tools needed: {', '.join(tools) if tools else 'TBD'}
- [ ] Pre-validated tool availability: [VERIFY EACH TOOL]
- [ ] Checked for tool conflicts

### Phase 3: Strategy Definition
- [ ] Defined success criteria
- [ ] Outlined step-by-step execution plan
- [ ] Identified rollback points
- [ ] Documented assumptions

### Phase 4: Risk Assessment
| Risk | Probability | Mitigation |
|------|-------------|-----------|
| [Risk 1] | Low/Med/High | [Mitigation strategy] |

### Phase 5: Execution Lock
- [ ] Checklist committed
- [ ] Plan is locked
- [ ] All commands verified
- [ ] Deviations documented

### Phase 6: Validation Plan
- [ ] Pre-execution validation
- [ ] Post-execution validation
- [ ] Rollback procedure
- [ ] Success confirmation

### Execution Summary

**Status**: [ ] Ready / [ ] Blocked
**Estimated Duration**: [TIME ESTIMATE]
"""

    return checklist.strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate pre-flight checklist for Codex operations"
    )
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Files affected by this operation",
    )
    parser.add_argument("--pr", help="Pull request number")
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    checklist = generate_checklist(args.task, args.files, args.pr)

    if args.output:
        Path(args.output).write_text(checklist)
        print(f"✅ Checklist written to: {args.output}")
    else:
        print(checklist)


if __name__ == "__main__":
    main()
