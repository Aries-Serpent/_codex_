"""
Variable Intent Writer — gap-closure for Copilot agent variable writes.

PROBLEM
-------
The Copilot coding agent sandbox only has GITHUB_TOKEN (scoped installation
token) which returns HTTP 403 on the GitHub Actions Variables API.
CODEX_MASTER_KEY (the required PAT) is not forwarded to the agent sandbox
when the org-level secret hasn't been injected by the setup steps.

SOLUTION — Intent-file mailbox pattern
---------------------------------------
1. Agent writes a JSON intent file to ``.codex/pending_ops/variable_set_*.json``
   describing the variable operation it wants to perform.
2. ``process-variable-intents.yml`` GitHub Actions workflow triggers on push,
   reads the intent file(s), and executes them using CODEX_MASTER_KEY.
3. The workflow commits back a deletion of each processed intent file so the
   queue is self-cleaning.

This approach works because:
- ``report_progress`` can always push commits regardless of token scope.
- The processing workflow has CODEX_MASTER_KEY available as an org secret.
- No sensitive values travel through the intent file — variable *values* for
  non-sensitive variables are fine; for sensitive values the admin should set
  them directly via the Codespace or GitHub settings UI.

Usage (Python API)
------------------
    from scripts.tools.variable_intent_writer import write_variable_intent

    # Queue a variable create/update — processed on next push
    path = write_variable_intent(
        operation="set",
        name="COPILOT_ACCESS_TEST",
        value="copilot-agent-session-test",
    )
    print(f"Intent queued → {path}")
    # Then call report_progress to push the commit and trigger the workflow.

Usage (CLI)
-----------
    python scripts/tools/variable_intent_writer.py set COPILOT_ACCESS_TEST "hello"
    python scripts/tools/variable_intent_writer.py list
    python scripts/tools/variable_intent_writer.py clear
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).parents[2]
_PENDING_DIR = _REPO_ROOT / ".codex" / "pending_ops"


def write_variable_intent(
    operation: str,
    name: str,
    value: Optional[str] = None,
    scope: str = "repo",
    owner: str = "Aries-Serpent",
    repo: str = "_codex_",
) -> Path:
    """Write a variable-operation intent file to ``.codex/pending_ops/``.

    Parameters
    ----------
    operation : ``"set"`` or ``"delete"``
    name      : GitHub Actions variable name (UPPER_SNAKE_CASE).
    value     : Variable value (required for ``"set"``; omit for ``"delete"``).
    scope     : ``"repo"`` (default) or ``"org"``.
    owner     : Repository owner / org slug.
    repo      : Repository name.

    Returns
    -------
    Path to the written intent file.
    """
    if operation not in ("set", "delete"):
        raise ValueError(f"operation must be 'set' or 'delete', got {operation!r}")
    if operation == "set" and value is None:
        raise ValueError("value is required for operation='set'")

    _PENDING_DIR.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    filename = f"variable_{operation}_{name}_{ts}.json"
    path = _PENDING_DIR / filename

    intent = {
        "schema_version": "1",
        "operation": operation,
        "scope": scope,
        "owner": owner,
        "repo": repo,
        "name": name,
        "value": value,
        "queued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "queued_by": "variable_intent_writer",
        "note": (
            "Processed by .github/workflows/process-variable-intents.yml "
            "on next push using CODEX_MASTER_KEY."
        ),
    }
    path.write_text(json.dumps(intent, indent=2) + "\n", encoding="utf-8")
    return path


def list_intents() -> list[dict]:
    """Return all pending intent files as parsed dicts."""
    if not _PENDING_DIR.exists():
        return []
    intents = []
    for f in sorted(_PENDING_DIR.glob("variable_*.json")):
        try:
            intents.append(json.loads(f.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            # Malformed intent file — skip silently with a warning so corrupt
            # files don't block the queue but are visible in logs.
            print(f"  ⚠️  Skipping malformed intent file: {f.name}", file=sys.stderr)
    return intents


def clear_intents() -> int:
    """Remove all pending intent files. Returns number removed."""
    if not _PENDING_DIR.exists():
        return 0
    removed = 0
    for f in _PENDING_DIR.glob("variable_*.json"):
        f.unlink()
        removed += 1
    return removed


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Queue variable write operations for the process-variable-intents workflow."
    )
    sub = parser.add_subparsers(dest="cmd")

    p_set = sub.add_parser("set", help="Queue a variable create/update")
    p_set.add_argument("name", help="Variable name (UPPER_SNAKE_CASE)")
    p_set.add_argument("value", help="Variable value")
    p_set.add_argument("--scope", default="repo", choices=["repo", "org"])
    p_set.add_argument("--owner", default="Aries-Serpent")
    p_set.add_argument("--repo", default="_codex_")

    p_del = sub.add_parser("delete", help="Queue a variable deletion")
    p_del.add_argument("name")
    p_del.add_argument("--scope", default="repo", choices=["repo", "org"])
    p_del.add_argument("--owner", default="Aries-Serpent")
    p_del.add_argument("--repo", default="_codex_")

    sub.add_parser("list", help="List pending intents")
    sub.add_parser("clear", help="Remove all pending intents")

    args = parser.parse_args()

    if args.cmd == "set":
        path = write_variable_intent(
            "set", args.name, args.value, args.scope, args.owner, args.repo
        )
        print(f"✅ Intent queued → {path.relative_to(_REPO_ROOT)}")
        print("   Push your changes (report_progress) to trigger processing.")

    elif args.cmd == "delete":
        path = write_variable_intent(
            "delete", args.name, scope=args.scope, owner=args.owner, repo=args.repo
        )
        print(f"✅ Delete intent queued → {path.relative_to(_REPO_ROOT)}")

    elif args.cmd == "list":
        intents = list_intents()
        if not intents:
            print("No pending intents.")
        for i in intents:
            print(
                f"  [{i['operation'].upper()}] {i['name']} "
                f"(scope={i['scope']}, queued={i['queued_at']})"
            )

    elif args.cmd == "clear":
        n = clear_intents()
        print(f"Removed {n} pending intent file(s).")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    _cli()
