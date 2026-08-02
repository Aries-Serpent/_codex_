#!/usr/bin/env python3
"""Check the canonical token contract in session-critical documentation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_MARKER = "## 📦 Tokenized Variable Contract"
CANONICAL = {
    "TVAR_COPILOT_AGENT_AUTH_ENABLED",
    "TVAR_COPILOT_AGENT_MAX_AUTONOMY",
    "TVAR_COGNITIVE_BRAIN_SESSION_NUM",
    "TVAR_CODEX_CI_FAILURE_RATE",
    "TVAR_CODEX_CI_LAST_GREEN_SHA",
    "TVAR_CODEX_SWEEP_SKIP_MAIN",
    "TVAR_CODEX_MAX_HEALER_RUNS",
    "TVAR_CODEX_HEALER_SKIP_SKIPCI",
    "TSEC_CODEX_MASTER_KEY",
    "TSEC_CODEX_BACKUP_KEY",
    "TENV_PYTHON_VERSION",
    "TENV_NODE_VERSION",
    # Legacy aliases retained while reporting documents converge on the
    # canonical names above.
    "TVAR_COPILOT_AGENT_MAX_AUTONOMY_LEVEL",
    "TVAR_COGNITIVE_BRAIN_SESSION_NUMBER",
    "TVAR_CODEX_MAX_HEALER_RUNS_PER_HOUR",
    "TVAR_AGENT_HANDOFF_TIMEOUT_SECONDS",
    "TVAR_AUTONOMOUS_ACTIONS_ENABLED",
    "TVAR_CODEX_CACHE_VERSION",
    "TVAR_CODEX_CI_FAILURE_THRESHOLD",
    "TVAR_CODEX_COVERAGE_THRESHOLD",
    "TVAR_COGNITIVE_BRAIN_ALLOWED_ACTORS",
    "TVAR_COGNITIVE_BRAIN_INJECTION_ENABLED",
    "TVAR_COPILOT_AGENT_STATE",
    "TVAR_EMBEDDING_INDEX_AUTO_REBUILD",
    "TENV_DRY_RUN",
    "TENV_PR_NUMBER",
    "TENV_REF",
    "TENV_SHA",
    "TSEC_CODECOV_TOKEN",
    "TSEC_GITHUB_TOKEN",
}
DEFAULT_DOCS = (
    ".codex/plans/LEAN_WORKFLOW_OS_PLANSET.md",
    "docs/reporting/copilot_agent_session_standard_operation.md",
    "docs/reporting/workflow_portfolio_7d_analysis.md",
)


def _annotation(message: str) -> None:
    print(f"::warning::{message}")


def check(paths: list[Path]) -> dict[str, object]:
    violations: list[dict[str, object]] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            violations.append({"path": str(path), "kind": "read_error", "message": str(exc)})
            continue
        found = set(re.findall(r"`((?:TVAR|TSEC|TENV)_[A-Z0-9_]+)`", text))
        if CONTRACT_MARKER not in text:
            violations.append(
                {"path": str(path), "kind": "missing_contract", "message": "missing token contract block"}
            )
        unknown = sorted(found - CANONICAL)
        if unknown:
            violations.append(
                {"path": str(path), "kind": "unknown_tokens", "message": ", ".join(unknown)}
            )
    return {
        "checked": [str(p) for p in paths],
        "violations": violations,
        "status": "warning" if violations else "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Documentation paths relative to repository root")
    parser.add_argument("--json", dest="json_path", help="Write a JSON report")
    args = parser.parse_args()
    paths = [REPO_ROOT / p for p in (args.paths or DEFAULT_DOCS)]
    report = check(paths)
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    violations = cast(list[dict[str, str]], report["violations"])
    for item in violations:
        _annotation(f"{item['path']}: {item['message']}")
    print(f"Token contract check: {len(paths)} document(s), {len(report['violations'])} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
