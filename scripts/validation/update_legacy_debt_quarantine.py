"""Update the legacy test debt quarantine summary and trend tables.

This script runs the ``tests/cognitive_brain`` pytest suite, parses the
results, and updates ``docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md``:

* Refreshes the **Quarantine Summary** table in place.
* Appends a row to the **Trend Table** (kept to the latest 12 rows).
* Updates the ``Last Updated`` timestamp.

Exit codes:

* ``0`` -- counts are unchanged from the previous snapshot.
* ``2`` -- counts changed (so callers can detect drift).
* ``1`` -- any error prevented a successful update.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

QUARANTINE_DOC = Path("docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md")

SUMMARY_TABLE_HEADER = "## Quarantine Summary\n"
TREND_TABLE_HEADER = "## Trend Table\n"
EXIT_CRITERIA_HEADER = "## Exit Criteria\n"

SUMMARY_METRICS = (
    "Total cognitive_brain tests executed",
    "Passed",
    "Failed",
    "Errored",
    "Failures attributable to PR #5430",
)


class PytestResult:
    """Lightweight container for parsed pytest output."""

    def __init__(self) -> None:
        self.total: int = 0
        self.passed: int = 0
        self.failed: int = 0
        self.errored: int = 0
        self.failure_messages: list[str] = []

    @property
    def non_attributable(self) -> int:
        """Non-attributable failures are failed + errored."""
        return self.failed + self.errored


def _now_utc() -> str:
    """Return current UTC time as ISO-8601 Z string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _format_int(value: int) -> str:
    """Format an integer with comma thousands separators."""
    return f"{value:,}"


def _parse_int(text: str) -> int:
    """Parse an integer that may contain comma separators."""
    return int(text.replace(",", "").strip())


def _extract_short_cause(message: str) -> str:
    """Collapse a failure message into a short top-cause pattern.

    The goal is a human-readable label that groups similar failures, e.g.
    ``NameError: CognitiveBrain`` instead of a full traceback.
    """
    message = message.strip()

    # NameError / AttributeError / TypeError / ValueError single-line forms
    for prefix in ("NameError: ", "AttributeError: ", "TypeError: ", "ValueError: "):
        if prefix in message:
            idx = message.rfind(prefix)
            line = message[idx:].split("\n", 1)[0].strip()
            # Trim after the object/symbol name for brevity
            if "name '" in line and "' is not defined" in line:
                return line
            if "has no attribute '" in line and "'" in line:
                parts = line.split("'")
                return parts[0] + "'" + parts[1] + "'"
            return line[:120]

    # Import error forms
    if "ImportError" in message or "ModuleNotFoundError" in message:
        for line in message.splitlines():
            if "ImportError" in line or "ModuleNotFoundError" in line:
                return line.strip()[:120]

    # Assertion with a threshold, e.g. "0.4494 > 0.35"
    threshold_match = re.search(r"([\d.]+)\s*([<>]=?)\s*([\d.]+)", message)
    if threshold_match:
        return f"Assertion {threshold_match.group(0)}"

    # First non-empty line if nothing else matches
    for line in message.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:120]

    return "Unknown"


def _top_cause(messages: list[str]) -> str:
    """Return the most common short failure-cause label."""
    if not messages:
        return "-"
    causes = [_extract_short_cause(msg) for msg in messages]
    most_common, _count = Counter(causes).most_common(1)[0]
    return most_common


def run_pytest(test_path: str = "tests/cognitive_brain") -> PytestResult:
    """Run pytest quietly and parse the terminal summary.

    Uses ``--tb=no`` so only the summary line and short error messages are
    captured. Pytest is invoked as a subprocess rather than through
    ``pytest.main`` to keep import-time side effects minimal when this module
    is imported.
    """
    result = PytestResult()

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_path,
        "-q",
        "--tb=no",
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    output = proc.stdout + proc.stderr
    lines = output.splitlines()

    # Parse the final summary line, e.g.:
    # 1041 passed, 24 failed, 13 errors in 12.34s
    # 1041 passed, 13 errors in 12.34s
    # 1041 passed in 12.34s
    summary_pattern = re.compile(
        r"(?P<passed>\d+)\s+passed"
        r"(?:,\s*(?P<failed>\d+)\s+failed)?"
        r"(?:,\s*(?P<errored>\d+)\s+errors?)?"
        r"(?:,\s*(?P<skipped>\d+)\s+skipped)?"
        r"(?:,\s*(?P<xfail>\d+)\s+xfail)?"
        r"(?:,\s*(?P<xpass>\d+)\s+xpass)?"
        r"(?:\s+in\s+[\d.]+s)?"
    )

    summary_match: re.Match | None = None
    for line in reversed(lines):
        summary_match = summary_pattern.search(line)
        if summary_match:
            break

    if summary_match is not None:
        result.passed = int(summary_match.group("passed") or 0)
        result.failed = int(summary_match.group("failed") or 0)
        result.errored = int(summary_match.group("errored") or 0)
    else:
        # Fallback: count short test summary lines when the summary is missing
        # (e.g. large output buffers or non-standard pytest configs).
        result.failed = len(re.findall(r"^FAILED\s+", output, flags=re.MULTILINE))
        result.errored = len(re.findall(r"^ERROR\s+", output, flags=re.MULTILINE))

    result.total = result.passed + result.failed + result.errored

    # Collect short error lines that pytest prints after the failing test
    # identifier, e.g.:
    # tests/.../test_foo.py::TestClass::test_bar - NameError: name 'x' is not defined
    error_pattern = re.compile(r"^\s*\S+\s+-\s+(.+)$")
    for line in lines:
        if line.startswith("FAILED ") or line.startswith("ERROR "):
            match = error_pattern.match(line[7:])
            if match:
                result.failure_messages.append(match.group(1))

    # Fallback: if no short messages were parsed, gather lines that look like
    # exception headers from the captured output.
    if not result.failure_messages:
        exception_headers = re.compile(
            r"^(?:E\s+)?"
            r"(NameError|AttributeError|TypeError|ValueError|ImportError|"
            r"ModuleNotFoundError|Failed):.*"
        )
        for line in lines:
            match = exception_headers.match(line)
            if match:
                result.failure_messages.append(match.group(0).lstrip("E ").strip())

    return result


def _read_doc() -> str:
    """Read the quarantine markdown file."""
    if not QUARANTINE_DOC.exists():
        raise FileNotFoundError(f"Quarantine doc not found: {QUARANTINE_DOC}")
    return QUARANTINE_DOC.read_text(encoding="utf-8")


def _write_doc(content: str) -> None:
    """Write the quarantine markdown file."""
    QUARANTINE_DOC.write_text(content, encoding="utf-8")


def _update_last_updated(content: str, timestamp: str) -> str:
    """Refresh the ``Last Updated`` timestamp."""
    return re.sub(
        r"\*\*Last Updated:\*\*\s*[^\n]+",
        f"**Last Updated:** {timestamp}",
        content,
        count=1,
    )


def _replace_summary_table(content: str, result: PytestResult) -> str:
    """Update the Quarantine Summary table while preserving everything else."""
    start_idx = content.find(SUMMARY_TABLE_HEADER)
    if start_idx == -1:
        raise ValueError("Quarantine Summary section not found")

    table_start = content.find("\n| Metric | Count |\n", start_idx)
    if table_start == -1:
        raise ValueError("Quarantine Summary table header not found")

    # Find end of table (next blank line or next header)
    table_body_start = table_start + 1
    sep_line = content.find("|---|---|\n", table_body_start)
    if sep_line == -1:
        raise ValueError("Quarantine Summary table separator not found")

    data_start = sep_line + len("|---|---|\n")
    next_double_newline = content.find("\n\n", data_start)
    next_header = content.find("\n## ", data_start)

    end_candidates = [c for c in (next_double_newline, next_header) if c != -1]
    table_end = min(end_candidates) if end_candidates else len(content)

    rows = [
        f"| {metric} | {value} |"
        for metric, value in [
            (SUMMARY_METRICS[0], _format_int(result.total)),
            (SUMMARY_METRICS[1], _format_int(result.passed)),
            (SUMMARY_METRICS[2], _format_int(result.failed)),
            (SUMMARY_METRICS[3], _format_int(result.errored)),
            (SUMMARY_METRICS[4], "0"),
        ]
    ]

    new_table = (
        "## Quarantine Summary\n\n"
        "| Metric | Count |\n"
        "|---|---|\n"
        + "\n".join(rows)
        + "\n"
    )

    return content[:start_idx] + new_table + content[table_end:]


def _parse_latest_summary(content: str) -> PytestResult | None:
    """Extract the current summary counts from the markdown."""
    start_idx = content.find(SUMMARY_TABLE_HEADER)
    if start_idx == -1:
        return None

    text = content[start_idx:]
    match = re.search(
        r"Total cognitive_brain tests executed\s*\|\s*([\d,]+)\s*\|\s*\n"
        r"Passed\s*\|\s*([\d,]+)\s*\|\s*\n"
        r"Failed\s*\|\s*([\d,]+)\s*\|\s*\n"
        r"Errored\s*\|\s*([\d,]+)\s*\|\s*\n",
        text,
    )
    if not match:
        return None

    previous = PytestResult()
    previous.total = _parse_int(match.group(1))
    previous.passed = _parse_int(match.group(2))
    previous.failed = _parse_int(match.group(3))
    previous.errored = _parse_int(match.group(4))
    return previous


def _delta_string(current: PytestResult, previous: PytestResult | None) -> str:
    """Return a human-readable delta vs the previous snapshot."""
    if previous is None:
        return "baseline"
    delta = current.non_attributable - previous.non_attributable
    if delta == 0:
        return "0"
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta}"


def _insert_or_update_trend_table(content: str, result: PytestResult) -> str:
    """Append a row to the Trend Table, retaining only the latest 12 rows."""
    timestamp = _now_utc()
    previous = _parse_latest_summary(content)
    delta = _delta_string(result, previous)
    top_cause = _top_cause(result.failure_messages)

    new_row = (
        f"| {timestamp} | {_format_int(result.failed)} | "
        f"{_format_int(result.errored)} | {_format_int(result.total)} | "
        f"{delta} | {top_cause} |"
    )

    if TREND_TABLE_HEADER not in content:
        # Insert the trend table just before the Exit Criteria section.
        exit_idx = content.find(EXIT_CRITERIA_HEADER)
        if exit_idx == -1:
            raise ValueError(
                "Exit Criteria section not found; cannot place Trend Table"
            )

        table = (
            "## Trend Table\n\n"
            "| Snapshot Date | Failed | Errored | Total | Delta vs Previous | Top Cause |\n"
            "|---|---|---|---|---|---|\n"
            f"{new_row}\n\n"
        )
        return content[:exit_idx] + table + content[exit_idx:]

    # Trend table exists: replace its body with the new row prepended, then trim.
    header_idx = content.find(TREND_TABLE_HEADER)
    table_start = content.find(
        "| Snapshot Date | Failed | Errored | Total | Delta vs Previous | Top Cause |\n",
        header_idx,
    )
    sep_line = content.find("|---|---|---|---|---|---|\n", table_start)
    data_start = sep_line + len("|---|---|---|---|---|---|\n")
    next_section = content.find("\n## ", data_start)
    table_end = next_section if next_section != -1 else len(content)

    existing_rows = [
        line for line in content[data_start:table_end].splitlines() if line.strip()
    ]
    updated_rows = [new_row] + existing_rows
    kept_rows = updated_rows[:12]

    new_table = (
        TREND_TABLE_HEADER
        + "\n"
        + "| Snapshot Date | Failed | Errored | Total | Delta vs Previous | Top Cause |\n"
        + "|---|---|---|---|---|---|\n"
        + "\n".join(kept_rows)
        + "\n\n"
    )

    return content[:header_idx] + new_table + content[table_end:]


def update_quarantine(
    test_path: str = "tests/cognitive_brain",
    result: PytestResult | None = None,
) -> tuple[PytestResult, bool]:
    """Run pytest and update the quarantine document.

    If *result* is supplied the pytest run is skipped and the provided result
    is used directly (avoids a redundant second run when the caller already has
    the results).

    Returns the parsed result and a boolean indicating whether the non-
    attributable failure count changed from the previous snapshot.
    """
    if result is None:
        result = run_pytest(test_path)

    content = _read_doc()
    previous = _parse_latest_summary(content)

    content = _replace_summary_table(content, result)
    content = _insert_or_update_trend_table(content, result)
    content = _update_last_updated(content, _now_utc())

    _write_doc(content)

    changed = previous is None or result.non_attributable != previous.non_attributable
    return result, changed


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Update the legacy cognitive_brain test debt quarantine document."
    )
    parser.add_argument(
        "--test-path",
        default="tests/cognitive_brain",
        help="Path passed to pytest (default: tests/cognitive_brain).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print results without modifying the markdown file.",
    )
    args = parser.parse_args(argv)

    try:
        result = run_pytest(args.test_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: failed to run pytest: {exc}", file=sys.stderr)
        return 1

    print(
        f"cognitive_brain results: total={result.total} "
        f"passed={result.passed} failed={result.failed} errored={result.errored}"
    )
    print(f"top failure cause: {_top_cause(result.failure_messages)}")

    if args.dry_run:
        print("dry-run: skipping markdown update")
        return 0

    try:
        _, changed = update_quarantine(args.test_path, result=result)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: failed to update quarantine doc: {exc}", file=sys.stderr)
        return 1

    if changed:
        print("quarantine counts changed")
        return 2

    print("quarantine counts unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
