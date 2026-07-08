"""Handler for the test.failure.matcher built-in skill.

Parses pytest / CI test failure output and returns structured failure records
classified by known pattern IDs (RP-019, RP-009, RP-XDIST-WORKER, etc.).
All pattern_id values use the ``RP-...`` format.  Pure text heuristics —
no model inference, fully deterministic.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Pattern catalogue  (pattern_id → regex, category, suggested_fix)
# ---------------------------------------------------------------------------

_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "RP-019",
        "category": "import-error",
        "regex": re.compile(r"ModuleNotFoundError: No module named '(?P<module>[^']+)'", re.M),
        "fix": "Check for src. absolute import regression — run P19-BATCH-001",
    },
    {
        "id": "RP-009",
        "category": "mypy-regression",
        "regex": re.compile(r"mypy.*?(?P<count>\d+) error.*?>\s*(?P<baseline>\d+)", re.M),
        "fix": "Fix new type errors or update baseline with CI isolated venv",
    },
    {
        "id": "RP-ASSERT",
        "category": "assertion-error",
        "regex": re.compile(r"AssertionError(?:: (?P<msg>.+))?", re.M),
        "fix": "Review failing assertion; check test fixture state",
    },
    {
        "id": "RP-TIMEOUT",
        "category": "timeout",
        "regex": re.compile(
            r"(?:FAILED|ERROR).*Timeout|TimeoutExpired|timeout.*exceeded", re.I | re.M
        ),
        "fix": "Increase pytest --timeout or mock slow external calls",
    },
    {
        "id": "RP-COLLECT",
        "category": "collection-error",
        "regex": re.compile(r"ERROR collecting (?P<file>\S+)", re.M),
        "fix": "Fix syntax or import error in the reported collection path",
    },
    {
        "id": "RP-TRANSIENT",
        "category": "transient-infra",
        "regex": re.compile(
            r"(?:runner has received a shutdown signal"
            r"|An error occurred while processing your request"
            r"|HTTP 503|Connection reset by peer)",
            re.I | re.M,
        ),
        "fix": "Re-run workflow — transient GitHub infrastructure failure",
    },
    {
        "id": "RP-P23",
        "category": "secrets-baseline",
        "regex": re.compile(r"TypeError: No such (?P<plugin>\S+Detector)", re.M),
        "fix": "Run: python scripts/ci/auto_fix_common_issues.py --pattern 23",
    },
    {
        "id": "RP-P22",
        "category": "tracked-file-drift",
        "regex": re.compile(r"files were modified by hook.*sync-tracked-files", re.M),
        "fix": "Run: python scripts/ci/sync_tracked_files.py --fix && git add -A && git commit",
    },
    {
        "id": "RP-RUFF",
        "category": "lint-error",
        "regex": re.compile(
            r"(?P<file>[^\s:]+\.py):(?P<line>\d+):\d+: (?P<code>[EFW]\d{3,4})", re.M
        ),
        "fix": "Run: python -m ruff check --fix <file>",
    },
    {
        "id": "RP-CHANGELOG",
        "category": "pre-flight-gate",
        "regex": re.compile(r"CHANGELOG\.md.*not updated|Verify CHANGELOG.md updated", re.I | re.M),
        "fix": "Add ### Fixed (SN) entry to ## [Unreleased] in CHANGELOG.md",
    },
    {
        "id": "RP-ACTIONLINT",
        "category": "workflow-lint",
        "regex": re.compile(r"actionlint.*(?P<file>\.github/workflows/[^\s]+):(?P<line>\d+)", re.M),
        "fix": "Fix YAML/shell issue in the reported workflow file at the reported line",
    },
    # pytest-xdist distributed test failures
    {
        "id": "RP-XDIST-WORKER",
        "category": "xdist-worker-crash",
        "regex": re.compile(
            r"(?:Worker\s+\w+\s+crashed|pytest-xdist.*worker.*(?:crash|died|lost)|"
            r"INTERNALERROR.*xdist|gw\d+.*(?:CRASHED|DOWN))",
            re.I | re.M,
        ),
        "fix": "xdist worker crash — check for forking issues, add --forked or reduce -n; "
        "inspect worker stderr with -v -s",
    },
    {
        "id": "RP-XDIST-COLLECT",
        "category": "xdist-collection-error",
        "regex": re.compile(
            r"(?:distributed testing.*collect|collecting.*-n\s*\d+.*ERROR|"
            r"xdist.*could not load.*conftest)",
            re.I | re.M,
        ),
        "fix": "xdist collection error — ensure conftest.py is importable in all workers; "
        "use --import-mode=importlib if needed",
    },
    # Flaky test markers
    {
        "id": "RP-FLAKY",
        "category": "flaky-test",
        "regex": re.compile(
            r"(?:@pytest\.mark\.flaky|Flaky test.*(?:passed|failed) on retry "
            r"(?P<n>\d+)/(?P<total>\d+)|RerunTestCase.*FAILED|rerun.*flaky)",
            re.I | re.M,
        ),
        "fix": "Flaky test detected — investigate root cause (timing, ordering, external I/O). "
        "Add @pytest.mark.flaky(reruns=3) as a temporary measure; file a stability bug.",
    },
]

# File + line extractor for generic failures
_LOCATION_RE = re.compile(
    r"(?P<file>[^\s()]+\.py)[:\(](?P<line>\d+)(?::(?P<col>\d+))?",
    re.M,
)
# FAILED / ERROR sentinel
_TEST_SENTINEL_RE = re.compile(
    r"^(?:FAILED|ERROR)\s+(?P<path>[^\s]+?)(?:\s*-\s*(?P<reason>.+))?$", re.M
)


def run(payload: dict[str, Any]) -> dict[str, Any]:
    """Parse CI/pytest output and return classified failure records.

    Parameters
    ----------
    payload : dict
        Expected keys:

        - ``test_output`` (str, required): raw pytest or CI log text.
        - ``max_failures`` (int, optional): cap on returned records (default 50).

    Returns
    -------
    dict
        ``{"failures": [...], "summary": {...}}``.
        Each failure has ``{test_name, pattern_id, category, message, fix, file, line}``.
    """
    raw: str = str(payload.get("test_output", "")).strip()
    if not raw:
        return {"failures": [], "summary": {"total": 0, "categories": {}}}

    max_failures: int = int(payload.get("max_failures", 50))
    failures: list[dict[str, Any]] = []
    seen: set[str] = set()

    # ── Classify by known patterns ───────────────────────────────────────────
    for pat in _PATTERNS:
        for m in pat["regex"].finditer(raw):
            msg = m.group(0)[:200]
            key = f"{pat['id']}:{msg[:80]}"
            if key in seen:
                continue
            seen.add(key)

            # Best-effort file + line from match or surrounding context
            start = max(0, m.start() - 200)
            ctx = raw[start : m.end() + 100]
            loc = _LOCATION_RE.search(ctx)
            file_ = loc.group("file") if loc else ""
            line_ = loc.group("line") if loc else ""

            failures.append(
                {
                    "test_name": _extract_test_name(raw, m.start()),
                    "pattern_id": pat["id"],
                    "category": pat["category"],
                    "message": msg,
                    "fix": pat["fix"],
                    "file": file_,
                    "line": int(line_) if line_ else None,
                }
            )
            if len(failures) >= max_failures:
                break
        if len(failures) >= max_failures:
            break

    # ── Collect unclassified FAILED / ERROR lines ────────────────────────────
    for m in _TEST_SENTINEL_RE.finditer(raw):
        if len(failures) >= max_failures:
            break
        path = m.group("path")
        reason = (m.group("reason") or "")[:200]
        key = f"unclassified:{path}"
        if key in seen:
            continue
        seen.add(key)
        failures.append(
            {
                "test_name": path,
                "pattern_id": "RP-UNKNOWN",
                "category": "unclassified",
                "message": reason or path,
                "fix": "Inspect logs manually; check for missing fixture or import",
                "file": _py_path_from_test(path),
                "line": None,
            }
        )

    # ── Summary ──────────────────────────────────────────────────────────────
    categories: dict[str, int] = {}
    for f in failures:
        categories[f["category"]] = categories.get(f["category"], 0) + 1

    return {
        "failures": failures,
        "summary": {
            "total": len(failures),
            "categories": categories,
        },
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_test_name(text: str, pos: int) -> str:
    """Return nearest FAILED/ERROR test name before *pos*, or empty string."""
    snippet = text[max(0, pos - 500) : pos]
    matches = list(_TEST_SENTINEL_RE.finditer(snippet))
    if matches:
        return matches[-1].group("path")
    return ""


def _py_path_from_test(test_path: str) -> str:
    """Convert ``tests/foo/test_bar.py::TestClass::test_x`` → ``tests/foo/test_bar.py``."""
    if "::" in test_path:
        return test_path.split("::")[0]
    return test_path
