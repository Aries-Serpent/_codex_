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
        "fix_commands": ["Re-run the workflow — transient GitHub runner failure; no code change needed."],
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
        "triage_note": "submit-pypi 503 is the single highest-volume transient failure; auto-retry is safe.",
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
            "Update docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md",
        ],
        "triage_note": "agent-auth pre-flight gate; Copilot agent must update CHANGELOG + accountability before pushing.",
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
        "triage_note": "Highest-frequency CI gate failure (20 occurrences in triage 2026-04-02). Reply to comments first.",
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
        "triage_note": "P19 src-import regression; often introduced by auto-refactors stripping 'src.' prefix.",
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
        "triage_note": "mypy baseline mismatch; most common after adding new modules without type stubs.",
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
            "Check tests/rag/ for MagicMock fixture gaps (mock_model.to.return_value = mock_model).",
            "Verify tests/rag/.coveragerc omits cache/, _model_utils.py, embeddings.py.",
            "Run: python -m pytest tests/rag/ -v --tb=short",
        ],
        "triage_note": "RAG Module Tests chronic failure (13 occurrences in triage 2026-04-02). "
        "Usually fixture isolation or coverage threshold issue.",
    },
]

_CONFIDENCE_THRESHOLD = 0.5


def run(payload: dict) -> dict:
    """Analyse CI run logs and return a health classification.

    Parameters
    ----------
    payload : dict
        Expected keys:

        - ``run_logs`` (str, required): raw CI log text.
        - ``workflow_name`` (str, optional): workflow display name for context.
        - ``commit_sha`` (str, optional): commit SHA for cross-reference.

    Returns
    -------
    dict
        ``{"category", "pattern_id", "confidence", "fix_commands", "triage_note",
            "all_matches", "workflow_name", "commit_sha"}``.
    """
    logs: str = str(payload.get("run_logs", "")).strip()
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
        }

    workflow_name: str = str(payload.get("workflow_name", ""))
    commit_sha: str = str(payload.get("commit_sha", ""))

    all_matches: list[dict] = []
    best: dict | None = None

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

    return {
        "category": best["category"],
        "pattern_id": best["pattern_id"],
        "confidence": best["confidence"],
        "fix_commands": best["fix_commands"],
        "triage_note": best["triage_note"],
        "all_matches": all_matches,
        "workflow_name": workflow_name,
        "commit_sha": commit_sha,
    }
