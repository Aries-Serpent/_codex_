#!/usr/bin/env python
"""General maintenance script for executing Codex tasks across multiple capabilities.

This script performs a sequence of generic operations useful across the
Codex-ready tasks, including:

1. Parsing and updating the README.md to fix outdated references.
2. Scanning the repository for TODOs, stubs, and missing implementations.
3. Running quality gates via pre‑commit and nox.
4. Appending a summary entry to the CHANGELOG.md.
5. Capturing and logging errors in the prescribed format.

Note: This script does not execute GitHub Actions or any external CI services.
Run it locally via:

    python scripts/run_codex_tasks.py

"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"
ERROR_LOG = LOGS_DIR / "error_captures.log"


def log_error(step: str, error: Exception) -> None:
    """Log an error capture block for ChatGPT‑5 troubleshooting."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    with ERROR_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            f"Question for ChatGPT-5 {timestamp}:\n"
            f"While performing [{step}], encountered the following error:\n"
            f"{repr(error)}\n"
            f"Context: See run_codex_tasks.py for details.\n"
            "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
        )


def update_readme() -> None:
    """Update outdated references in README.md."""
    readme_path = ROOT / "README.md"
    if not readme_path.exists():
        return
    content = readme_path.read_text(encoding="utf-8")
    # Example replacement: adjust config file names and sections
    updated = re.sub(r"configs/training/base\.yaml", "configs/config.yaml", content)
    if updated != content:
        readme_path.write_text(updated, encoding="utf-8")


def search_for_gaps() -> None:
    """Scan repository files for TODOs, NotImplementedError, and pass statements."""
    patterns = [r"TODO", r"NotImplementedError", r"pass  # TODO"]
    gaps_report = ROOT / "docs" / "gaps_report.md"
    findings = []
    for path in ROOT.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append(f"- {path.relative_to(ROOT)}:{line_no}: {pattern}\n")
    if findings:
        gaps_report.parent.mkdir(parents=True, exist_ok=True)
        gaps_report.write_text("# Gap Analysis Report\n\n" + "".join(findings), encoding="utf-8")


def run_quality_gates() -> None:
    """Run pre-commit hooks and nox sessions."""
    subprocess.run(["pre-commit", "run", "--all-files"], check=True, cwd=str(ROOT))
    noxfile = ROOT / "noxfile.py"
    if noxfile.exists():
        for session in ["lint", "type", "tests", "sast", "coverage"]:
            try:
                subprocess.run(["nox", "-s", session], check=True, cwd=str(ROOT))
            except subprocess.CalledProcessError as exc:
                log_error(f"3.run_quality_gates:{session}", exc)


def append_changelog() -> None:
    """Append maintenance summary to CHANGELOG.md."""
    changelog = ROOT / "CHANGELOG.md"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")
    entry = (
        f"\n### Unreleased - {timestamp}\n"
        "- Updated README references to current configuration structure.\n"
        "- Generated gaps report for TODOs and stubs.\n"
        "- Executed pre-commit and nox quality gate sessions.\n"
    )
    if not changelog.exists():
        changelog.write_text("# Changelog\n\n", encoding="utf-8")
    with changelog.open("a", encoding="utf-8") as fh:
        fh.write(entry)


def main() -> None:
    try:
        update_readme()
    except Exception as e:
        log_error("1.update_readme", e)
    try:
        search_for_gaps()
    except Exception as e:
        log_error("2.search_for_gaps", e)
    try:
        run_quality_gates()
    except Exception as e:
        log_error("3.run_quality_gates", e)
    try:
        append_changelog()
    except Exception as e:
        log_error("4.append_changelog", e)
    print(
        "Codex maintenance tasks complete. See docs/gaps_report.md, logs/error_captures.log, and CHANGELOG.md for details."
    )


if __name__ == "__main__":
    main()
