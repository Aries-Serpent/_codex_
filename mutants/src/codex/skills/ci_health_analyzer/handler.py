"""Handler for the ci.health.analyzer built-in skill.

Analyses CI run log text and classifies the failure into a root-cause category
with a confidence score, suggested fix commands, and a known pattern ID.

Categories
----------
transient-infra    GitHub runner shutdown / API 503 — retry, no code fix
code-fix-required  Import error, type error, lint, test assertion failure
pre-flight-gate    CHANGELOG / accountability report / sync-tracked-files gate
flaky              Non-deterministic pass/fail pattern (timing, network)
workflow-config    actionlint, YAML parse, workflow logic error
supply-chain       Dependency submission, detect-secrets baseline mismatch
unknown            Cannot be classified with confidence ≥ 0.5
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Classification rules — ordered by priority (first match wins if confidence
# is above threshold)
# ---------------------------------------------------------------------------

_RULES: list[dict[str, Any]] = [
    # ── Transient infrastructure ─────────────────────────────────────────────
    {
        "pattern_id": "RP-TRANSIENT-SHUTDOWN",
        "category": "transient-infra",
        "confidence": 0.95,
        "regex": re.compile(
            r"runner has received a shutdown signal"
            r"|The job was canceled"
            r"|Lost communication with the server",
            re.I,
        ),
        "fix_commands": [
            "Re-run the workflow — transient GitHub runner failure; no code change needed."
        ],
        "triage_note": "High-frequency pattern; safe to auto-retry without investigation.",
    },
    {
        "pattern_id": "RP-TRANSIENT-API503",
        "category": "transient-infra",
        "confidence": 0.93,
        "regex": re.compile(
            r"An error occurred while processing your request\. Please try again later"
            r"|HTTP 503"
            r"|submit-dependency-snapshot.*error",
            re.I,
        ),
        "fix_commands": [
            "Re-run workflow — GitHub API 503 (dependency graph submission transient failure).",
            "If persists >3 retries: check pyproject.toml / requirements*.txt for parse errors.",
        ],
        "triage_note": "submit-pypi 503 is the single highest-volume transient failure; auto-retry is safe.",  # noqa: E501
    },
    # ── Supply-chain / secrets baseline ─────────────────────────────────────
    {
        "pattern_id": "RP-P23",
        "category": "supply-chain",
        "confidence": 0.97,
        "regex": re.compile(r"TypeError: No such \w+Detector", re.I),
        "fix_commands": ["python scripts/ci/auto_fix_common_issues.py --pattern 23"],
        "triage_note": "detect-secrets plugin mismatch; single command fixes.",
    },
    # ── Pre-flight gates ─────────────────────────────────────────────────────
    {
        "pattern_id": "RP-CHANGELOG-GATE",
        "category": "pre-flight-gate",
        "confidence": 0.96,
        "regex": re.compile(
            r"CHANGELOG\.md.*not updated"
            r"|Verify CHANGELOG.md updated"
            r"|No entry found for session",
            re.I,
        ),
        "fix_commands": [
            "Add '### Fixed (SN)' entry under '## [Unreleased]' in CHANGELOG.md",
            "Update docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md",
        ],
        "triage_note": "agent-auth pre-flight gate; Copilot agent must update CHANGELOG + accountability before pushing.",  # noqa: E501
    },
    {
        "pattern_id": "RP-P22",
        "category": "pre-flight-gate",
        "confidence": 0.95,
        "regex": re.compile(r"files were modified by hook.*sync-tracked-files", re.I),
        "fix_commands": [
            "python scripts/ci/sync_tracked_files.py --fix",
            "git add -A && git commit -m 'chore: sync tracked files'",
        ],
        "triage_note": "CODEX_MANIFEST / tracked-file drift — P22.",
    },
    {
        "pattern_id": "RP-COMMENT-GATE",
        "category": "pre-flight-gate",
        "confidence": 0.92,
        "regex": re.compile(
            r"blocking comment.*unaddressed"
            r"|PR Comment Review Gate.*failed"
            r"|BLOCKING.*mbaetiong",
            re.I,
        ),
        "fix_commands": [
            "Reply to every BLOCKING comment in the PR with resolution details.",
            "Push a new commit — the gate re-scans automatically on every push.",
        ],
        "triage_note": "Highest-frequency CI gate failure (20 occurrences in triage 2026-04-02). Reply to comments first.",  # noqa: E501
    },
    # ── Import errors ────────────────────────────────────────────────────────
    {
        "pattern_id": "RP-019",
        "category": "code-fix-required",
        "confidence": 0.94,
        "regex": re.compile(r"ModuleNotFoundError: No module named '([^']+)'", re.I),
        "fix_commands": [
            "Check for src. absolute import regression — run P19-BATCH-001.",
            "python scripts/ci/auto_fix_common_issues.py --pattern 19",
        ],
        "triage_note": "P19 src-import regression; often introduced by auto-refactors stripping 'src.' prefix.",  # noqa: E501
    },
    # ── mypy regression ──────────────────────────────────────────────────────
    {
        "pattern_id": "RP-009",
        "category": "code-fix-required",
        "confidence": 0.95,
        "regex": re.compile(r"(\d+) error.*?>\s*(\d+)", re.I),
        "fix_commands": [
            "Fix new type errors: python scripts/ci/mypy_baseline.py",
            "Or update baseline (if intentional): python scripts/ci/mypy_baseline.py --update",
            "Always use CI isolated venv to set baseline — NOT local full-install.",
        ],
        "triage_note": "mypy baseline mismatch; most common after adding new modules without type stubs.",  # noqa: E501
    },
    # ── Lint / ruff ──────────────────────────────────────────────────────────
    {
        "pattern_id": "RP-RUFF",
        "category": "code-fix-required",
        "confidence": 0.90,
        "regex": re.compile(r"[^\s:]+\.py:\d+:\d+: [EFW]\d{3,4}", re.I),
        "fix_commands": [
            "python -m ruff check --fix src/ tests/",
            "python scripts/ci/auto_fix_common_issues.py",
        ],
        "triage_note": "Ruff lint violation; auto-fixable in most cases.",
    },
    # ── Workflow / actionlint ────────────────────────────────────────────────
    {
        "pattern_id": "RP-ACTIONLINT",
        "category": "workflow-config",
        "confidence": 0.92,
        "regex": re.compile(
            r"actionlint.*\.github/workflows/[^\s:]+:\d+"
            r"|SC2288.*backtick"
            r"|shellcheck.*error",
            re.I,
        ),
        "fix_commands": [
            "Fix YAML/shell issue in the reported workflow file.",
            "Replace backtick-based string concat with f-string or printf pipeline.",
            "See .codex/ci_failure_patterns/CI_FAILURE_PATTERN_ANALYSIS_2026-03-25.md §P-C",
        ],
        "triage_note": "actionlint/shellcheck violation; fix reported line in workflow file.",
    },
    # ── RAG test (chronic) ───────────────────────────────────────────────────
    {
        "pattern_id": "RP-RAG-CHRONIC",
        "category": "code-fix-required",
        "confidence": 0.88,
        "regex": re.compile(
            r"FAILED tests/rag/.*"
            r"|test-rag.*Run RAG tests.*failed"
            r"|tests/rag/.*AssertionError",
            re.I,
        ),
        "fix_commands": [
            "Check tests/rag/ for MagicMock fixture gaps (mock_model.to.return_value = mock_model).",  # noqa: E501
            "Verify tests/rag/.coveragerc omits cache/, _model_utils.py, embeddings.py.",
            "Run: python -m pytest tests/rag/ -v --tb=short",
        ],
        "triage_note": "RAG Module Tests chronic failure (13 occurrences in triage 2026-04-02). "
        "Usually fixture isolation or coverage threshold issue.",
    },
    # ── Coverage gate drop ───────────────────────────────────────────────────
    {
        "pattern_id": "RP-COVERAGE-DROP",
        "category": "code-fix-required",
        "confidence": 0.87,
        "regex": re.compile(
            r"coverage.*below.*threshold"
            r"|CoverageException"
            r"|FAIL Required test coverage of \d+%",
            re.I,
        ),
        "fix_commands": [
            "Run: python -m pytest --cov=src --cov-report=term-missing to identify gaps.",
            "Add tests for newly uncovered lines or lower threshold if justified.",
            "Check tests/unit/test_coverage_toml_floor.py for floor configuration.",
        ],
        "triage_note": "Coverage threshold gate failed — new code paths lack tests.",
    },
    # ── Docker / container build ─────────────────────────────────────────────
    {
        "pattern_id": "RP-DOCKER-BUILD",
        "category": "workflow-config",
        "confidence": 0.89,
        "regex": re.compile(
            r"ERROR \[.*\] RUN pip install"
            r"|failed to solve.*dockerfile"
            r"|docker build.*exit code [1-9]"
            r"|OCI runtime.*container_linux",
            re.I,
        ),
        "fix_commands": [
            "Check Dockerfile for editable-install pip errors in multi-stage build.",
            "Ensure src-layout packages use 'pip install -e . --no-build-isolation'.",
            "Verify .dockerignore does not exclude required source files.",
        ],
        "triage_note": "Docker build failure — often caused by src-layout editable install in CI.",
    },
    # ── Timeout / hung job ───────────────────────────────────────────────────
    {
        "pattern_id": "RP-TIMEOUT",
        "category": "transient-infra",
        "confidence": 0.86,
        "regex": re.compile(
            r"The job running on runner.*has exceeded the maximum execution time"
            r"|exceeded.*timeout.*minutes"
            r"|timed.?out after \d+",
            re.I,
        ),
        "fix_commands": [
            "Check 'timeout-minutes:' in the workflow job — increase if legitimate.",
            "Profile which step is slow: add timing annotations or split into stages.",
            "If consistently timing out, consider caching expensive setup steps.",
        ],
        "triage_note": "Job exceeded maximum execution time. May be flaky or need timeout increase.",  # noqa: E501
    },
    # ── Rust / Cargo build failure ────────────────────────────────────────────
    {
        "pattern_id": "RP-RUST-BUILD",
        "category": "code-fix-required",
        "confidence": 0.88,
        "regex": re.compile(
            r"error\[E\d+\]:.*-->" r"|cargo build.*error" r"|error: could not compile",
            re.I,
        ),
        "fix_commands": [
            "Run: cargo build 2>&1 | head -50 to see full error.",
            "Check deny.toml for banned dependency versions that trigger compile errors.",
            "Ensure Cargo.lock is committed and not stale.",
        ],
        "triage_note": "Rust compilation error — check E#### codes in cargo output.",
    },
    # ── Secret / credential leak ──────────────────────────────────────────────
    {
        "pattern_id": "RP-SECRET-LEAK",
        "category": "supply-chain",
        "confidence": 0.96,
        "regex": re.compile(
            r"detect-secrets.*Potential secret found"
            r"|secret.*scanning.*alert"
            r"|baseline.*out of date",
            re.I,
        ),
        "fix_commands": [
            "Run: detect-secrets scan --baseline .secrets.baseline to update baseline.",
            "Review flagged lines; revoke any real credentials immediately.",
            "If false positive: add `# pragma: allowlist secret` inline.",
        ],
        "triage_note": "Potential secret detected by detect-secrets or GitHub secret scanning.",
    },
]

_CONFIDENCE_THRESHOLD = 0.5


def _trend_summary(history: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute a trend window summary from a list of prior run results.

    Parameters
    ----------
    history:
        List of previous ``run()`` outputs (most-recent-last ordering
        preferred but not required).  Empty list → no trend data.

    Returns
    -------
    dict
        ``{"run_count", "category_counts", "dominant_category",
           "recurring_pattern_ids", "flap_rate", "trend_label"}``.
    """
    if not history:
        return {
            "run_count": 0,
            "category_counts": {},
            "dominant_category": None,
            "recurring_pattern_ids": [],
            "flap_rate": 0.0,
            "trend_label": "no-history",
        }

    category_counts: dict[str, int] = {}
    pattern_counts: dict[str, int] = {}
    flaps = 0
    prev_category: str | None = None

    for entry in history:
        cat = entry.get("category", "unknown")
        pid = entry.get("pattern_id", "RP-UNKNOWN")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        pattern_counts[pid] = pattern_counts.get(pid, 0) + 1
        if prev_category is not None and prev_category != cat:
            flaps += 1
        prev_category = cat

    total = len(history)
    flap_rate = round(flaps / max(total - 1, 1), 3) if total > 1 else 0.0

    dominant_category = max(category_counts, key=lambda k: category_counts[k])
    recurring_pattern_ids = [pid for pid, cnt in pattern_counts.items() if cnt > 1]

    dominant_frac = category_counts[dominant_category] / total
    if dominant_frac >= 0.8:
        trend_label = f"chronic:{dominant_category}"
    elif flap_rate >= 0.5:
        trend_label = "flapping"
    elif dominant_frac >= 0.5:
        trend_label = f"trending:{dominant_category}"
    else:
        trend_label = "mixed"

    return {
        "run_count": total,
        "category_counts": category_counts,
        "dominant_category": dominant_category,
        "recurring_pattern_ids": recurring_pattern_ids,
        "flap_rate": flap_rate,
        "trend_label": trend_label,
    }


def run(payload: dict[str, Any]) -> dict[str, Any]:
    """Analyse CI run logs and return a health classification with trend window.

    Parameters
    ----------
    payload : dict
        Expected keys:

        - ``run_logs`` (str, required): raw CI log text.
        - ``workflow_name`` (str, optional): workflow display name for context.
        - ``commit_sha`` (str, optional): commit SHA for cross-reference.
        - ``history`` (list[dict], optional): list of previous ``run()`` output
          dicts (most-recent-last).  When provided, a ``trend`` field is
          included in the result summarising the pattern across the window.

    Returns
    -------
    dict
        ``{"category", "pattern_id", "confidence", "fix_commands", "triage_note",
            "all_matches", "workflow_name", "commit_sha", "trend"}``.
        ``trend`` is ``None`` when no ``history`` is supplied.
    """
    logs: str = str(payload.get("run_logs", "")).strip()
    history: list[dict[str, Any]] = list[Any](payload.get("history") or [])
    if not logs:
        return {
            "category": "unknown",
            "pattern_id": "RP-UNKNOWN",
            "confidence": 0.0,
            "fix_commands": ["No logs provided — cannot analyze."],
            "triage_note": "",
            "all_matches": [],
            "workflow_name": payload.get("workflow_name", ""),
            "commit_sha": payload.get("commit_sha", ""),
            "trend": _trend_summary(history) if history else None,
        }

    workflow_name: str = str(payload.get("workflow_name", ""))
    commit_sha: str = str(payload.get("commit_sha", ""))

    all_matches: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None

    for rule in _RULES:
        if rule["regex"].search(logs):
            match_info = {
                "pattern_id": rule["pattern_id"],
                "category": rule["category"],
                "confidence": rule["confidence"],
                "fix_commands": rule["fix_commands"],
                "triage_note": rule["triage_note"],
            }
            all_matches.append(match_info)
            if best is None or rule["confidence"] > best["confidence"]:
                best = match_info

    if best is None or best["confidence"] < _CONFIDENCE_THRESHOLD:
        best = {
            "pattern_id": "RP-UNKNOWN",
            "category": "unknown",
            "confidence": 0.0,
            "fix_commands": [
                "Inspect full logs manually.",
                "Check GitHub Actions run URL for step-level error.",
                "Post RCA comment to PR with gathered details.",
            ],
            "triage_note": "No known pattern matched — manual triage required.",
        }

    # Build trend from history + current run
    trend: dict[str, Any] | None = None
    if history:
        current_result = {
            "category": best["category"],
            "pattern_id": best["pattern_id"],
        }
        trend = _trend_summary(history + [current_result])

    return {
        "category": best["category"],
        "pattern_id": best["pattern_id"],
        "confidence": best["confidence"],
        "fix_commands": best["fix_commands"],
        "triage_note": best["triage_note"],
        "all_matches": all_matches,
        "workflow_name": workflow_name,
        "commit_sha": commit_sha,
        "trend": trend,
    }
