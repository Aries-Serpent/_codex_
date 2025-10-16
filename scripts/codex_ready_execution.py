"""Codex-ready sequential executor for remediation tasks.

This script automates the high-level workflow described in the
codex-ready task sequence: parse documentation, scan the repository for
capability gaps, log proposed adaptations, and emit structured error
records when something fails. It is intentionally offline-friendly.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "codex_ready"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

README_PLACEHOLDER_PATTERN = re.compile(r"\]\(#\)")
DEFAULT_PATTERNS = (
    r"NotImplementedError",
    r"TODO",
    r"pass\s+#\s*TODO",
)


@dataclass
class SearchResult:
    path: Path
    line_no: int
    line: str


def log_error(step: str, description: str, error: Exception) -> None:
    """Append a formatted error capture block to error_log.md."""

    timestamp = datetime.now(timezone.utc).isoformat()
    block = (
        f"> Question from ChatGPT @codex {timestamp}:\n"
        f"> While performing {step}, encountered the following error: {error!r} "
        f"Context: {description}. What are the possible causes, and how can this be "
        f"resolved while preserving intended functionality?\n"
    )
    target = REPO_ROOT / "error_log.md"
    with target.open("a", encoding="utf-8") as handle:
        handle.write(block)
        if not block.endswith("\n"):
            handle.write("\n")


def parse_readme(update: bool = False) -> dict:
    """Inspect README for placeholder references and optionally emit a sanitized copy."""

    readme_path = REPO_ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    matches = [m.group(0) for m in README_PLACEHOLDER_PATTERN.finditer(text)]

    sanitized_path: Path | None = None
    if update and matches:
        sanitized_text = README_PLACEHOLDER_PATTERN.sub("(TBD)", text)
        sanitized_path = ARTIFACT_DIR / "README.sanitized.md"
        sanitized_path.write_text(sanitized_text, encoding="utf-8")

    return {
        "readme": str(readme_path.relative_to(REPO_ROOT)),
        "placeholders_found": matches,
        "sanitized_copy": str(sanitized_path.relative_to(REPO_ROOT)) if sanitized_path else None,
    }


def scan_repository(patterns: Sequence[str]) -> list[SearchResult]:
    """Search tracked files for the supplied regex patterns."""

    results: list[SearchResult] = []
    for path in REPO_ROOT.rglob("*.py"):
        if ".venv" in path.parts or "venv" in path.parts:
            continue
        try:
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for pattern in patterns:
                    if re.search(pattern, line):
                        results.append(SearchResult(path=path.relative_to(REPO_ROOT), line_no=line_no, line=line.strip()))
                        break
        except UnicodeDecodeError:
            continue
    return results


def record_change_log(entries: Iterable[dict]) -> Path:
    """Append entries to the codex-ready change log JSONL file."""

    target = ARTIFACT_DIR / "change_log.jsonl"
    with target.open("a", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return target


def finalize(summary: dict) -> Path:
    """Persist a final summary artifact for downstream tooling."""

    target = ARTIFACT_DIR / "summary.json"
    target.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex-ready sequential executor")
    parser.add_argument(
        "--patterns",
        nargs="*",
        default=list(DEFAULT_PATTERNS),
        help="Additional regex patterns to search for across the repository.",
    )
    parser.add_argument(
        "--update-readme",
        action="store_true",
        help="Emit a sanitized README snapshot with placeholder references replaced.",
    )
    parser.add_argument(
        "--change-description",
        default="Codex-ready remediation planning",
        help="Description recorded in the change log entries.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argparser()
    args = parser.parse_args(argv)

    try:
        readme_info = parse_readme(update=args.update_readme)
    except Exception as exc:  # pragma: no cover - defensive guard
        log_error("STEP_1:README_PARSE", "Failed to parse README for placeholders", exc)
        raise

    try:
        search_hits = scan_repository(args.patterns)
    except Exception as exc:  # pragma: no cover - defensive guard
        log_error("STEP_2:SCAN_REPOSITORY", "Pattern scan failed", exc)
        raise

    change_entries: List[dict] = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": args.change_description,
            "readme_placeholders": readme_info.get("placeholders_found", []),
            "sanitized_readme": readme_info.get("sanitized_copy"),
            "matches_found": len(search_hits),
        }
    ]
    record_change_log(change_entries)

    summary = {
        "readme": readme_info,
        "search_results": [
            {
                "path": str(result.path),
                "line_no": result.line_no,
                "line": result.line,
            }
            for result in search_hits[:50]
        ],
        "change_log": str((ARTIFACT_DIR / "change_log.jsonl").relative_to(REPO_ROOT)),
    }
    finalize(summary)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
