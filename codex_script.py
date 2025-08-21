#!/usr/bin/env python3
"""Codex CLI utility with patch guard and validation.

This script demonstrates how to apply fragile text patches safely and how to
run basic validation commands after execution. The main functionality is a
placeholder for future expansion.
"""

import argparse
import subprocess
from pathlib import Path

SENTINEL = "# [PATCHED_SECTION]"


def apply_patch(path: Path) -> None:
    """Replace ``foo`` with ``bar`` once and mark the file as patched."""

    if not path.exists():
        return
    text = path.read_text()
    if SENTINEL in text:
        return
    patched = text.replace("foo", "bar")
    if patched != text:
        path.write_text(f"{patched}\n{SENTINEL}\n")


def main() -> None:
    """Entry point for the CLI."""

    parser = argparse.ArgumentParser(description="Codex CLI")
    parser.add_argument("path", type=Path, help="File to patch in-place")
    args = parser.parse_args()
    apply_patch(args.path)


if __name__ == "__main__":
    main()

    # Validation block: run tools and write to .codex/results.md (non-blocking)
    try:
        results_dir = Path(".codex")
        results_dir.mkdir(parents=True, exist_ok=True)
        results_path = results_dir / "results.md"
        with open(results_path, "w") as results:
            tools = [
                ("Ruff Lint", ["ruff", "--diff"]),
                ("MyPy Type Check", ["mypy", "."]),
                ("PyTest", ["pytest", "-q", "--maxfail=1"]),
                ("Bandit SAST", ["bandit", "-r", "."]),
                ("Semgrep SAST", ["semgrep", "--config", "p/ci"]),
                ("DetectSecrets", ["detect-secrets", "scan"]),
            ]
            for name, cmd in tools:
                results.write(f"## {name}\n```\n")
                try:
                    proc = subprocess.run(cmd, capture_output=True, text=True)
                    results.write(proc.stdout)
                    results.write(proc.stderr)
                except Exception as e:  # pragma: no cover - non-blocking
                    results.write(f"Error running {name}: {e}\n")
                results.write("```\n\n")
    except Exception:  # pragma: no cover - non-blocking
        # Non-blocking: log the error or pass
        pass
