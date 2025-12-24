#!/usr/bin/env python3
"""Validate 3.5% coverage gate enforcement across all test contexts.

This script ensures ``--cov-fail-under=3.5`` is present in the key surfaces that
document or execute our test suite:

* ``README.md``
* ``docs/governance/CONTRIBUTING.md``
* ``configs/development/pytest.ini``
* ``configs/development/Makefile``
* ``configs/development/noxfile.py``
* ``.github/workflows/*.yml`` and ``.github/workflows/*.yaml``

When a location is missing the flag the script prints a clear failure message
and exits with status ``1`` so CI can gate the change.
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

COVERAGE_PATTERN = r"--cov-fail-under=3\.5"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _colour(message: str, colour: str) -> str:
    """Wrap ``message`` in ANSI colour codes when stdout is a TTY."""

    if not sys.stdout.isatty():  # pragma: no cover - branch depends on runtime
        return message
    return f"{colour}{message}{RESET}"


def _read_text(path: Path) -> str | None:
    """Best-effort helper that returns the file contents or ``None``."""

    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.debug(f"FileNotFoundError: {e}")
        logger.warning(f"FileNotFoundError: {e}", exc_info=True)
        return None
    except OSError as exc:  # pragma: no cover - filesystem errors are uncommon
        return f"<error: {exc}>"


def check_file(filepath: Path, pattern: str = COVERAGE_PATTERN) -> Tuple[bool, str]:
    """Check if ``filepath`` contains the coverage gate pattern.

    Returns a tuple ``(found, snippet_or_error)``.  When the pattern is missing
    the second element holds either ``"<missing>"`` or an error detail if the
    file could not be read.
    """

    content = _read_text(filepath)
    if content is None:
        return False, f"File not found: {filepath.as_posix()}"
    if content.startswith("<error:"):
        return False, content

    matches = list(re.finditer(pattern, content))
    if not matches:
        return False, "<missing>"

    match = matches[0]
    start = max(0, match.start() - 40)
    end = min(len(content), match.end() + 40)
    snippet = content[start:end].strip()
    return True, snippet


def _gather_workflow_files(workflow_dir: Path) -> List[Path]:
    if not workflow_dir.exists():
        return []
    files: List[Path] = []
    for pattern in ("*.yml", "*.yaml"):
        files.extend(sorted(workflow_dir.glob(pattern)))
    return files


def validate_coverage_gates() -> int:
    """Validate coverage gates in all required files.

    Returns:
        0 if all checks pass, 1 if any fail
    """

    files_to_check: List[Path] = [
        Path("README.md"),
        Path("docs/governance/CONTRIBUTING.md"),
        Path("configs/development/pytest.ini"),
        Path("configs/development/Makefile"),
        Path("configs/development/noxfile.py"),
    ]

    workflow_dir = Path(".github/workflows")
    files_to_check.extend(_gather_workflow_files(workflow_dir))

    results: List[Dict[str, object]] = []
    failures: List[Path] = []

    for filepath in files_to_check:
        found, snippet = check_file(filepath)
        if not found and filepath.suffix in {".yml", ".yaml"}:
            text = _read_text(filepath)
            if text is None:
                snippet = f"File not found: {filepath.as_posix()}"
            elif text.startswith("<error:"):
                snippet = text
            elif "pytest" not in text:
                found = True
                snippet = "<not-applicable>"
        results.append(
            {
                "file": filepath.as_posix(),
                "found": found,
                "snippet": snippet,
            }
        )

        if found:
            snippet_preview = snippet.replace("\n", " ")[:80]
            print(
                _colour(
                    f"✅ {filepath.as_posix()}\n   Found: {snippet_preview}",
                    GREEN,
                )
            )
        else:
            detail = snippet if snippet != "<missing>" else "Add --cov-fail-under=3.5"
            print(
                _colour(
                    f"❌ {filepath.as_posix()}\n   {detail}",
                    RED,
                )
            )
            failures.append(filepath)

    print("\n" + "=" * 60)
    print("Coverage Gate Validation Summary")
    print("=" * 60)
    print(f"Files checked: {len(results)}")
    print(
        _colour(
            f"✅ Passed: {len(results) - len(failures)}",
            GREEN if not failures else YELLOW,
        )
    )
    print(_colour(f"❌ Failed: {len(failures)}", RED if failures else GREEN))

    if failures:
        print("\nFailed files:")
        for missing in failures:
            print(f"  - {missing.as_posix()}")
        print(
            _colour(
                "\nTip: add '--cov-fail-under=3.5' to the pytest invocation in the files above.",
                YELLOW,
            )
        )
        return 1

    print(_colour("\n✅ All coverage gates validated!", GREEN))
    return 0


if __name__ == "__main__":
    sys.exit(validate_coverage_gates())
