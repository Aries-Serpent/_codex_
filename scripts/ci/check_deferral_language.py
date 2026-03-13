#!/usr/bin/env python3
"""
scripts/ci/check_deferral_language.py
──────────────────────────────────────
Deferral-Language Enforcement Gate
Enforces the AI Codebase Agency Policy (`.codex/CODEBASE_AGENCY_POLICY.md`).

TRIGGER RULE (mandatory for ALL agents):
  Any phrase in DEFERRAL_TRIGGERS found in a PR body, commit message, or
  agent session log is a policy violation.  The gate FAILS and the agent
  MUST:
    1. Load `.codex/CODEBASE_AGENCY_POLICY.md`
    2. Load the latest `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
    3. Fix the issue immediately — no exceptions for branch/PR/agent origin

Usage:
  python scripts/ci/check_deferral_language.py --pr-body FILE
  python scripts/ci/check_deferral_language.py --commit-msg FILE
  python scripts/ci/check_deferral_language.py --session-log FILE
  python scripts/ci/check_deferral_language.py --text "raw text to scan"

ML enhancement (optional, feature-flagged):
  DEFERRAL_SCANNER_ML=1 python scripts/ci/check_deferral_language.py ...
  Enables TF-IDF + LogisticRegression classifier trained on labeled examples in
  .codex/training_data/deferral_examples.jsonl.
  Regex patterns always run first; ML adds a second pass for uncaught intent.

Exit codes:
  0  — no deferral language found
  1  — deferral language detected (policy violation)
  2  — usage / file-not-found error
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Canonical deferral trigger phrases ────────────────────────────────────────
# These are the exact patterns that constitute policy violations.
# Edit only via PR with AGENT_ACCOUNTABILITY_REPORT update.
DEFERRAL_TRIGGERS: list[tuple[str, str]] = [
    # Attribution-based deferrals
    (r"this was from (?:a )?different (?:branch|agent|pr|pull request|task|session)",
     "Attribution deferral: blaming origin instead of fixing"),
    (r"not (?:from|in) (?:our|the) current (?:pr|branch|feature|task)",
     "Attribution deferral: scoping out current responsibility"),
    (r"(?:pre-?existing|pre-existing) (?:issue|code|problem|bug|error|concern)",
     "Pre-existing deferral: refusing pre-existing issues"),
    (r"(?:introduced|added|created) by (?:a )?(?:different|another|previous|other) (?:agent|pr|session|task|commit)",
     "Origin deferral: deflecting to another agent/session"),
    (r"not introduced by (?:this|my|our)",
     "Origin deferral: deflecting to another source"),
    # Scope-based deferrals
    (r"(?:not|out of|outside)(?: the)? scope(?: of this| of my)?",
     "Scope deferral: scoping out responsibility"),
    (r"not related to (?:this|my|our|the current) (?:pr|task|branch|change)",
     "Scope deferral: claiming issue is unrelated"),
    (r"not (?:directly )?related to (?:my|our|this) (?:change|work|fix|commit)",
     "Scope deferral: claiming issue is unrelated"),
    (r"(?:is|are|was|were) not (?:my|our) (?:problem|responsibility|concern|task)",
     "Responsibility deferral: refusing ownership"),
    # Future-based deferrals
    (r"(?:will|can|could|should|may)(?: be)? (?:address|fix|resolve|handle)(?:ed|d)? in (?:a )?future",
     "Future deferral: punting to future work without documented justification"),
    (r"future (?:pr\b|task\b|session\b|iteration\b|sprint\b|phase\b|work\b|fix\b|improvement\b)",
     "Future deferral: punting to future work"),
    (r"address(?:ed)? (?:incrementally|later|separately|in a follow[-\s]?up)",
     "Incremental deferral: incrementalism as avoidance"),
    (r"follow[-\s]?up (?:pr\b|task\b|issue\b|ticket\b)",
     "Follow-up deferral: creating follow-up instead of fixing"),
    (r"(?:can|will) be (?:addressed|fixed|resolved) (?:separately|later|next)",
     "Deferred fix: explicit future-assignment"),
    # "Residual" deferral without documented mitigation
    (r"residual (?:risk|issue|concern|problem)(?! — | - |\. Mitigation)",
     "Residual risk: documented without mitigation"),
    # Deprecation without tombstone
    (r"not actionable in this (?:pr|task|session|iteration)",
     "Non-actionable claim: must provide documented mitigation"),
    (r"(?:too|very) broad (?:for|to|in) (?:this|the current)",
     "Broad-scope deferral: claiming scope is too broad to fix"),
    (r"pre-?existing and safe",
     "Safety assumption without verification"),
    (r"(?:another|a different|the previous) (?:session|agent|team|pr) (?:should|will|can|must)",
     "Responsibility delegation to another agent/session"),
]

# ── Allowed exemptions (phrases that appear in policy/accountability docs themselves) ──
EXEMPTION_PATTERNS: list[str] = [
    r"DEFERRAL_TRIGGERS",           # this script's own source
    r"check_deferral_language",     # this script name
    r"deferral.language.gate",      # workflow name
    r"Prohibited Statements",       # policy itself listing what's prohibited
    r"#\s*noqa:\s*deferral",        # explicit per-line suppression
    r"noqa.*deferral",
]


# ── ML Classifier (optional — enabled by DEFERRAL_SCANNER_ML=1) ───────────────
# Uses scikit-learn TF-IDF + LinearSVC for intent detection.
# Falls back gracefully when scikit-learn is unavailable or training data is
# missing.  Runs OFFLINE (no network calls at any point).

_TRAINING_DATA_PATH = Path(__file__).parent.parent.parent / ".codex" / "training_data" / "deferral_examples.jsonl"

# Minimum precision/recall thresholds for model acceptance
_MIN_PRECISION = 0.95
_MIN_RECALL = 0.90


class DeferralMLClassifier:
    """Lightweight TF-IDF + LinearSVC classifier for intent detection.

    Falls back to regex patterns if scikit-learn is unavailable or training
    data is missing.  Trained on labeled examples in
    ``.codex/training_data/deferral_examples.jsonl``.

    Runs entirely offline — no network requests at any point.

    Feature flag: set environment variable ``DEFERRAL_SCANNER_ML=1`` to enable.
    """

    def __init__(self, training_data_path: Path | None = None) -> None:
        self._pipeline: Any = None
        self._available = False
        self._training_data_path = training_data_path or _TRAINING_DATA_PATH

    def _load_training_data(self) -> tuple[list[str], list[int]]:
        """Load labeled training examples from JSONL file."""
        texts: list[str] = []
        labels: list[int] = []
        path = self._training_data_path
        if not path.exists():
            raise FileNotFoundError(f"Training data not found: {path}")
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                texts.append(record["text"])
                labels.append(int(record["label"]))
        return texts, labels

    def train(self) -> dict[str, float]:
        """Train the classifier and return evaluation metrics.

        Returns:
            Dict with 'precision', 'recall', 'f1', 'n_train', 'n_test'.

        Raises:
            ImportError: If scikit-learn is not installed.
            FileNotFoundError: If training data is missing.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: PLC0415
        from sklearn.linear_model import LogisticRegression  # noqa: PLC0415
        from sklearn.metrics import precision_recall_fscore_support  # noqa: PLC0415
        from sklearn.model_selection import train_test_split  # noqa: PLC0415
        from sklearn.pipeline import Pipeline  # noqa: PLC0415

        texts, labels = self._load_training_data()
        x_train, x_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.20, random_state=42, stratify=labels
        )

        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                analyzer="word",
                ngram_range=(1, 3),
                min_df=1,
                max_features=5000,
                sublinear_tf=True,
            )),
            # LogisticRegression: fast, interpretable, calibrated probabilities
            ("clf", LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
        ])
        self._pipeline.fit(x_train, y_train)

        preds = self._pipeline.predict(x_test)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, preds, average="binary", pos_label=1
        )
        self._available = True
        return {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "n_train": len(x_train),
            "n_test": len(x_test),
        }

    def is_available(self) -> bool:
        """Return True if the classifier is trained and ready."""
        return self._available and self._pipeline is not None

    def predict(self, text: str) -> bool:
        """Return True if *text* is classified as deferral language.

        Always returns False if the classifier is not available.
        """
        if not self.is_available() or self._pipeline is None:
            return False
        result: int = self._pipeline.predict([text])[0]
        return bool(result)


def _get_ml_classifier() -> DeferralMLClassifier | None:
    """Return a trained ML classifier if DEFERRAL_SCANNER_ML=1, else None."""
    if os.environ.get("DEFERRAL_SCANNER_ML", "0") != "1":
        return None
    classifier = DeferralMLClassifier()
    try:
        metrics = classifier.train()
        logger.info(
            "ML classifier trained: precision=%.3f recall=%.3f f1=%.3f "
            "(n_train=%d n_test=%d)",
            metrics["precision"],
            metrics["recall"],
            metrics["f1"],
            metrics["n_train"],
            metrics["n_test"],
        )
        if metrics["precision"] < _MIN_PRECISION or metrics["recall"] < _MIN_RECALL:
            logger.warning(
                "ML classifier below quality threshold "
                "(precision≥%.2f recall≥%.2f required). "
                "Disabling ML enhancement.",
                _MIN_PRECISION,
                _MIN_RECALL,
            )
            return None
        return classifier
    except ImportError:
        logger.warning(
            "scikit-learn not available — ML classifier disabled. "
            "Install with: pip install scikit-learn"
        )
        return None
    except FileNotFoundError as exc:
        logger.warning("ML classifier disabled: %s", exc)
        return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("ML classifier training failed (%s) — using regex only.", exc)
        return None


def _load_text(source: str | Path) -> str:
    """Load text from a file path or return the string directly."""
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return str(source)


def _line_is_exempt(line: str) -> bool:
    """Return True if the line is covered by an exemption pattern."""
    return any(re.search(p, line, re.IGNORECASE) for p in EXEMPTION_PATTERNS)


def scan(
    text: str,
    source_label: str = "<input>",
    ml_classifier: "DeferralMLClassifier | None" = None,
) -> list[dict]:
    """
    Scan *text* for deferral language.

    Regex patterns always run first.  If *ml_classifier* is provided and
    the line was not already flagged by regex, the ML classifier provides a
    second pass to catch semantically similar deferral intent.

    Returns a list of violation dicts with keys: line_no, line, pattern, reason.
    """
    violations: list[dict] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _line_is_exempt(line):
            continue
        flagged = False
        for pattern, reason in DEFERRAL_TRIGGERS:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(
                    {
                        "source": source_label,
                        "line_no": line_no,
                        "line": line.strip(),
                        "pattern": pattern,
                        "reason": reason,
                        "detector": "regex",
                    }
                )
                flagged = True
                break  # one violation per line is enough
        if not flagged and ml_classifier is not None and ml_classifier.predict(line.strip()):
            violations.append(
                {
                    "source": source_label,
                    "line_no": line_no,
                    "line": line.strip(),
                    "pattern": "<ml-classifier>",
                    "reason": "ML classifier detected deferral intent",
                    "detector": "ml",
                }
            )
    return violations


def _format_violation(v: dict) -> str:
    return (
        f"  {v['source']}:{v['line_no']}: {v['reason']}\n"
        f"    TEXT: {v['line'][:120]}\n"
    )


def _print_policy_reminder() -> None:
    print(
        "\n"
        "═══════════════════════════════════════════════════════════════════\n"
        "  🚨 CODEBASE AGENCY POLICY VIOLATION — DEFERRAL LANGUAGE DETECTED\n"
        "═══════════════════════════════════════════════════════════════════\n"
        "\n"
        "  MANDATORY IMMEDIATE ACTIONS (no exceptions):\n"
        "\n"
        "  1. 🔃 LOAD: .codex/CODEBASE_AGENCY_POLICY.md\n"
        "  2. 🔃 LOAD: docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md\n"
        "  3. 🔃 LOAD: All stored memories from previous sessions\n"
        "  4. FIX the deferred issue NOW — branch/PR/agent origin is irrelevant\n"
        "\n"
        "  PROHIBITED (per policy §2 'Comprehensive Issue Resolution'):\n"
        "    ❌ 'This was from a different branch'\n"
        "    ❌ 'This is a pre-existing issue'\n"
        "    ❌ 'Not related to my PR'\n"
        "    ❌ 'Will address in a future PR/session'\n"
        "    ❌ 'Out of scope'\n"
        "\n"
        "  Full policy: .codex/CODEBASE_AGENCY_POLICY.md\n"
        "═══════════════════════════════════════════════════════════════════\n",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan text for deferral language (Codebase Agency Policy enforcement)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pr-body", metavar="FILE", help="Path to PR body text file")
    group.add_argument("--commit-msg", metavar="FILE", help="Path to commit message file")
    group.add_argument("--session-log", metavar="FILE", help="Path to agent session log")
    group.add_argument("--text", metavar="TEXT", help="Raw text string to scan")
    group.add_argument(
        "--git-log",
        action="store_true",
        help="Scan last 10 commit messages via git log",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Exit 1 on any violation (default: True)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Print violations but exit 0 (informational mode)",
    )
    args = parser.parse_args(argv)

    # Initialise ML classifier (no-op if DEFERRAL_SCANNER_ML != "1")
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    ml_classifier = _get_ml_classifier()
    if ml_classifier is not None:
        print("🤖 ML classifier enabled (DEFERRAL_SCANNER_ML=1)", file=sys.stderr)

    all_violations: list[dict] = []

    if args.pr_body:
        path = Path(args.pr_body)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 2
        all_violations += scan(
            path.read_text(encoding="utf-8"),
            f"PR body ({path.name})",
            ml_classifier,
        )

    elif args.commit_msg:
        path = Path(args.commit_msg)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 2
        all_violations += scan(
            path.read_text(encoding="utf-8"),
            f"commit msg ({path.name})",
            ml_classifier,
        )

    elif args.session_log:
        path = Path(args.session_log)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 2
        all_violations += scan(
            path.read_text(encoding="utf-8"),
            f"session log ({path.name})",
            ml_classifier,
        )

    elif args.text:
        all_violations += scan(args.text, "<inline>", ml_classifier)

    elif args.git_log:
        import subprocess  # noqa: PLC0415
        try:
            result = subprocess.run(  # noqa: S603
                ["git", "log", "--format=%B", "-n", "10"],  # noqa: S607
                capture_output=True, text=True, check=True,
            )
            all_violations += scan(result.stdout, "git log (last 10 commits)", ml_classifier)
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: git log failed: {exc}", file=sys.stderr)
            return 2

    if all_violations:
        _print_policy_reminder()
        print(f"Found {len(all_violations)} deferral language violation(s):\n")
        for v in all_violations:
            print(_format_violation(v))
        if args.warn_only:
            print("⚠️  warn-only mode: exiting 0 despite violations", file=sys.stderr)
            return 0
        return 1

    print("✅ No deferral language detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
