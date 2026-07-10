"""
Accountability Report & CHANGELOG Auto-Update — Session Entry Generator.

On Copilot session close, this script:
1. Collects session metadata (commit SHA, files changed, lines ±, test results).
2. Computes a normalised significance score (0–1).
3. Tokenises the session narrative and assigns TF-based weights with boosts.
4. Generates a structured markdown entry.
5. Appends idempotently to ``docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md``.
6. Inserts a Keep-a-Changelog entry under ``## [Unreleased]`` in ``CHANGELOG.md``.
7. Writes a machine-readable JSON artifact to ``.codex/sessions/<session_id>.json``.

Usage::

    # Dry-run (stdout only, no file changes)
    python -m src.codex.session.accountability_autoupdate --dry-run

    # Commit mode (appends to report + writes JSON artifact)
    python -m src.codex.session.accountability_autoupdate --commit

    # Override session ID
    CODEX_SESSION_ID=my-session python -m src.codex.session.accountability_autoupdate --dry-run

Environment variables:
    CODEX_SESSION_ID        — explicit session identifier (fallback: SHA-1 hash).
    CODEX_SESSION_LOG_DIR   — path to session log directory.
    CODEX_SESSION_AUTHOR    — author login (fallback: ``git config user.name``).
    GITHUB_RUN_ID           — CI run identifier (optional).
    GITHUB_REPOSITORY       — owner/repo string (optional).
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import logging
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from typing import Any, Optional

from codex.logging.structured_logger import logger

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
REPORT_PATH = REPO_ROOT / "docs" / "accountability" / ".codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md"
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
SESSIONS_DIR = REPO_ROOT / ".codex" / "sessions"

# Minimal English stopword list (no external deps).
_STOPWORDS = frozenset(
    [
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "shall",
        "should",
        "may",
        "might",
        "can",
        "could",
        "of",
        "in",
        "to",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "not",
        "no",
        "nor",
        "so",
        "if",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "only",
        "own",
        "same",
        "than",
        "too",
        "very",
        "just",
        "don",
        "about",
        "up",
        "also",
        "how",
        "what",
        "which",
        "who",
        "whom",
        "when",
        "where",
        "why",
    ]
)


# ---------------------------------------------------------------------------
# Metadata collection
# ---------------------------------------------------------------------------


def _run_git(args: list[str], fallback: str = "") -> str:
    """Run a git command and return stripped stdout, or *fallback* on error."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=15,
        )
        return result.stdout.strip() if result.returncode == 0 else fallback
    except (ValueError, TypeError, RuntimeError) as exc:
        logger.debug("Git command %s failed: %s", args, exc)
        return fallback


def collect_metadata(
    session_id: Optional[str] = None,
    narrative: Optional[str] = None,
) -> dict[str, Any]:
    """Gather session metadata from git and environment.

    Parameters
    ----------
    session_id:
        Explicit session ID.  When *None*, derived from ``CODEX_SESSION_ID``
        env-var or a SHA-256 hash of ``commit_sha + timestamp``.
    narrative:
        Free-form session description.  Falls back to the last commit message.

    Returns
    -------
    dict
        Metadata dictionary with all fields needed for scoring, tokenisation,
        markdown generation, and the JSON artifact.
    """
    commit_sha = _run_git(["rev-parse", "HEAD"], fallback="0" * 40)
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Session ID -----------------------------------------------------------
    if session_id is None:
        session_id = os.environ.get("CODEX_SESSION_ID")
    if not session_id:
        raw = f"{commit_sha}:{timestamp}".encode()
        session_id = hashlib.sha256(raw).hexdigest()[:12]

    # Author ---------------------------------------------------------------
    author = (
        os.environ.get("CODEX_SESSION_AUTHOR")
        or os.environ.get("GIT_USER")
        or _run_git(["config", "user.name"], fallback="copilot-agent")
    )

    # Files changed --------------------------------------------------------
    files_changed_raw = _run_git(["diff", "--name-only", "HEAD~1", "HEAD"])
    files_changed = [f for f in files_changed_raw.splitlines() if f]

    # Lines added / removed ------------------------------------------------
    numstat_raw = _run_git(["diff", "--numstat", "HEAD~1", "HEAD"])
    lines_added = 0
    lines_removed = 0
    for line in numstat_raw.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            try:
                lines_added += int(parts[0])
            except ValueError:
                logger.debug("Skipping non-numeric added count in: %s", line)
            try:
                lines_removed += int(parts[1])
            except ValueError:
                logger.debug("Skipping non-numeric removed count in: %s", line)

    # Commit message -------------------------------------------------------
    commit_message = _run_git(["log", "-1", "--pretty=%B"])

    # Narrative fallback ---------------------------------------------------
    if not narrative:
        narrative = commit_message or f"Session {session_id}"

    # Tests ----------------------------------------------------------------
    tests_touched = [f for f in files_changed if "test" in f.lower()]
    docs_changed = any(f.endswith(".md") or f.startswith("docs/") for f in files_changed)
    security_findings = any("security" in f.lower() or "cve" in f.lower() for f in files_changed)

    # CI references --------------------------------------------------------
    run_id = os.environ.get("GITHUB_RUN_ID")
    repo = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
    log_dir = os.environ.get("CODEX_SESSION_LOG_DIR")

    return {
        "session_id": session_id,
        "author": author,
        "commit_sha": commit_sha,
        "timestamp": timestamp,
        "files_changed": files_changed,
        "files_changed_count": len(files_changed),
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "lines_changed": lines_added + lines_removed,
        "tests_touched": tests_touched,
        "tests_touched_count": len(tests_touched),
        "commit_message": commit_message,
        "narrative": narrative,
        "docs_changed": docs_changed,
        "security_findings": security_findings,
        "run_id": run_id,
        "repo": repo,
        "log_dir": log_dir,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def compute_score(
    files_changed_count: int,
    lines_changed: int,
    tests_touched_count: int,
    security_findings: bool,
    docs_changed: bool,
    commit_message: str,
) -> float:
    """Return a normalised significance score in ``[0, 1]``.

    Components (with weights):
        * ``m_files``       (0.30) — min(1, files_changed_count / 10)
        * ``m_lines``       (0.25) — tanh(lines_changed / 500)
        * ``m_test_impact`` (0.20) — min(1, tests_touched_count / 20)
        * ``m_security``    (0.15) — 1 if security findings else 0
        * ``m_doc``         (0.05) — 0.5 if docs changed else 0
        * ``m_hotfix``      (0.05) — 1 if commit message matches ``fix|hotfix``
    """
    m_files = min(1.0, files_changed_count / 10)
    m_lines = math.tanh(lines_changed / 500)
    m_test_impact = min(1.0, tests_touched_count / 20)
    m_security = 1.0 if security_findings else 0.0
    m_doc = 0.5 if docs_changed else 0.0
    m_hotfix = 1.0 if re.search(r"\b(?:fix|hotfix)\b", commit_message, re.I) else 0.0

    score = (
        0.30 * m_files
        + 0.25 * m_lines
        + 0.20 * m_test_impact
        + 0.15 * m_security
        + 0.05 * m_doc
        + 0.05 * m_hotfix
    )
    return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# Tokenisation & weighting
# ---------------------------------------------------------------------------


def tokenize_narrative(
    narrative: str,
    modified_filenames: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """Tokenise *narrative* into weighted terms.

    Steps:
        1. Sentence-split on ``.``, ``!``, ``?``.
        2. Word-tokenise by splitting on non-alphanumeric, lower-case.
        3. Remove stopwords.
        4. Compute TF (term frequency).
        5. Boost tokens found in *modified_filenames* (+0.3).
        6. Normalise weights to sum to 1.

    Returns a list of ``{"token": str, "weight": float}`` dicts sorted by
    descending weight.
    """
    modified_filenames = modified_filenames or []
    # Tokenize filenames into individual path components / words so that
    # the substring check doesn't accidentally boost unrelated tokens
    # (e.g. "auth" matching "oauth", "py" matching ".py").
    filename_tokens: set[str] = set()
    for fname in modified_filenames:
        filename_tokens.update(re.findall(r"[a-zA-Z0-9]+", fname.lower()))

    # Sentence split → word tokenise
    sentences = re.split(r"[.!?]+", narrative)
    words: list[str] = []
    for sentence in sentences:
        tokens = re.findall(r"[a-zA-Z0-9]+", sentence.lower())
        words.extend(t for t in tokens if t not in _STOPWORDS and len(t) > 1)

    if not words:
        return []

    # TF
    counter = Counter(words)
    max_count = max(counter.values())

    # Build weighted list
    weighted: dict[str, float] = {}
    for token, count in counter.items():
        base_tf = count / max_count
        boost = 0.0
        if token in filename_tokens:
            boost += 0.3
        weighted[token] = base_tf + boost

    # Normalise to sum = 1
    total = sum(weighted.values())
    if total > 0:
        weighted = {k: v / total for k, v in weighted.items()}

    result = [{"token": k, "weight": round(v, 4)} for k, v in weighted.items()]
    result.sort(key=lambda x: x["weight"], reverse=True)  # type: ignore[arg-type,return-value]
    return result


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------


def generate_markdown_entry(
    metadata: dict[str, Any], score: float, tokens: list[dict[str, Any]]
) -> str:
    """Generate a structured markdown entry for the accountability report.

    Returns a single string ready to be appended (includes trailing ``---``).
    """
    session_id = metadata["session_id"]
    author = metadata["author"]
    timestamp = metadata["timestamp"]
    commit_sha = metadata["commit_sha"]
    files_changed = metadata["files_changed"]
    narrative = metadata["narrative"]

    # Derive primary topic from top-weighted token
    primary_topic = tokens[0]["token"].title() if tokens else "Session"
    summary = narrative[:120]

    # CI reference — presence of a run_id only means a CI run exists, not that it
    # passed.  Label it as a reference rather than implying success.
    ci_status = "ci-ref" if metadata.get("run_id") else "no-ci-run"

    # Build entry
    lines = [
        f"# [Session]: {primary_topic}",
        f"> Generated: {timestamp} | Author: {author} | SessionID: {session_id}",
        "",
        "## Summary",
        f"- {summary}",
        "",
        "## Metrics",
        "| Metric | Value |",
        "|---|---|",
        f"| Commit SHA | `{commit_sha[:10]}` |",
        f"| Files changed | {metadata['files_changed_count']} |",
        f"| Lines added | +{metadata['lines_added']} |",
        f"| Lines removed | -{metadata['lines_removed']} |",
        f"| Tests affected | {metadata['tests_touched_count']} |",
        f"| CI status | {ci_status} |",
        f"| Significance score | {score:.2f} |",
        "",
        "## Tokenized Narrative",
        "```json",
        json.dumps(tokens[:10], indent=2),
        "```",
        "",
        "## Details",
        f"- Commit: `{commit_sha}`",
    ]

    if files_changed:
        lines.append("- Modified files:")
        for f in files_changed[:20]:
            lines.append(f"  - `{f}`")

    if metadata.get("run_id"):
        repo = metadata.get("repo", "Aries-Serpent/_codex_")
        lines.append(f"- CI run: https://github.com/{repo}/actions/runs/{metadata['run_id']}")

    lines.extend(["", "---", ""])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report manipulation
# ---------------------------------------------------------------------------


def session_exists_in_report(session_id: str, report_path: pathlib.Path = REPORT_PATH) -> bool:
    """Return *True* if *session_id* is already recorded in the report."""
    if not report_path.exists():
        return False
    content = report_path.read_text(encoding="utf-8")
    return f"SessionID: {session_id}" in content


def append_to_report(
    entry: str,
    report_path: pathlib.Path = REPORT_PATH,
) -> None:
    """Append *entry* to the accountability report atomically.

    Creates the file and parent directories if they don't exist.
    Uses a temporary file + rename for safety.
    """
    report_path.parent.mkdir(parents=True, exist_ok=True)

    if report_path.exists():
        existing = report_path.read_text(encoding="utf-8")
    else:
        existing = "# Agent Accountability Report\n\n"

    updated = existing.rstrip("\n") + "\n\n" + entry

    # Atomic write via temp file
    fd, tmp_path = tempfile.mkstemp(dir=str(report_path.parent), suffix=".md.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(updated)
        shutil.move(tmp_path, str(report_path))
    except (IOError, OSError) as exc:
        logger.error("Failed to write accountability report: %s", exc)
        # Best-effort cleanup: ignore failure to remove temporary report file.
        try:
            os.unlink(tmp_path)
        except OSError:
            logger.debug("Failed to remove temp file %s", tmp_path, exc_info=True)
        raise


# ---------------------------------------------------------------------------
# CHANGELOG update
# ---------------------------------------------------------------------------


def generate_changelog_entry(metadata: dict[str, Any], score: float) -> str:
    """Generate a Keep-a-Changelog entry for the ``[Unreleased]`` section.

    Returns a markdown string suitable for insertion right after the
    ``## [Unreleased]`` header line.
    """
    session_id = metadata["session_id"]
    timestamp = metadata["timestamp"][:10]  # YYYY-MM-DD
    narrative = metadata["narrative"][:120]
    files = metadata["files_changed"]

    # Determine category from commit message
    msg = metadata.get("commit_message", "")
    if re.search(r"\bfix\b", msg, re.I):
        category = "Fixed"
    elif re.search(r"\bfeat\b", msg, re.I):
        category = "Added"
    else:
        category = "Changed"

    lines = [
        f"\n### {category} (session {session_id[:8]} — {timestamp}, score={score:.2f})",
        f"- {narrative}",
    ]
    if files:
        for f in files[:5]:
            lines.append(f"  - `{f}`")
        if len(files) > 5:
            lines.append(f"  - … and {len(files) - 5} more files")

    return "\n".join(lines) + "\n"


def session_exists_in_changelog(
    session_id: str,
    changelog_path: pathlib.Path = CHANGELOG_PATH,
) -> bool:
    """Return *True* if *session_id* is already mentioned in the CHANGELOG."""
    if not changelog_path.exists():
        return False
    content = changelog_path.read_text(encoding="utf-8")
    return f"session {session_id[:8]}" in content


def update_changelog(
    entry: str,
    changelog_path: pathlib.Path = CHANGELOG_PATH,
) -> bool:
    """Insert *entry* into CHANGELOG.md right after ``## [Unreleased]``.

    Returns *True* if the file was updated, *False* if the marker was not found.
    """
    if not changelog_path.exists():
        return False

    content = changelog_path.read_text(encoding="utf-8")
    marker = "## [Unreleased]"
    idx = content.find(marker)
    if idx == -1:
        logger.warning("CHANGELOG.md has no [Unreleased] section — skipping.")
        return False

    insert_pos = idx + len(marker)
    # Skip to end of the marker line
    newline_pos = content.find("\n", insert_pos)
    if newline_pos == -1:
        newline_pos = len(content)

    updated = content[:newline_pos] + "\n" + entry + content[newline_pos:]

    # Atomic write
    fd, tmp_path = tempfile.mkstemp(dir=str(changelog_path.parent), suffix=".md.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(updated)
        shutil.move(tmp_path, str(changelog_path))
    except (IOError, OSError) as exc:
        logger.error("Failed to write changelog: %s", exc)
        # Best-effort cleanup: ignore failure to remove temporary changelog file.
        try:
            os.unlink(tmp_path)
        except OSError:
            logger.debug("Failed to remove temp file %s", tmp_path, exc_info=True)
        raise

    return True


# ---------------------------------------------------------------------------
# JSON artifact
# ---------------------------------------------------------------------------


def write_session_artifact(
    metadata: dict[str, Any],
    score: float,
    tokens: list[dict[str, Any]],
    sessions_dir: pathlib.Path = SESSIONS_DIR,
) -> pathlib.Path:
    """Write a JSON artifact to ``.codex/sessions/<session_id>.json``.

    Returns the path to the written file.
    """
    sessions_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "session_id": metadata["session_id"],
        "author": metadata["author"],
        "commit_sha": metadata["commit_sha"],
        "timestamp": metadata["timestamp"],
        "files_changed": metadata["files_changed"],
        "lines_added": metadata["lines_added"],
        "lines_removed": metadata["lines_removed"],
        "tests_touched_count": metadata["tests_touched_count"],
        "score": round(score, 4),
        "tokens": tokens[:20],
        "narrative": metadata["narrative"],
        "repo": metadata.get("repo", ""),
        "run_id": metadata.get("run_id"),
    }
    out = sessions_dir / f"{metadata['session_id']}.json"
    out.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def run(
    *,
    session_id: Optional[str] = None,
    narrative: Optional[str] = None,
    dry_run: bool = False,
    report_path: pathlib.Path = REPORT_PATH,
    changelog_path: Optional[pathlib.Path] = CHANGELOG_PATH,
    sessions_dir: pathlib.Path = SESSIONS_DIR,
) -> dict[str, Any]:
    """Execute the full accountability auto-update pipeline.

    Updates both the accountability report **and** the CHANGELOG
    (``[Unreleased]`` section).  Returns the generated artifact dict.

    Idempotency is checked **per-output**: if the report entry already
    exists but the CHANGELOG or artifact is missing (e.g. a previous run
    failed mid-way), rerunning will repair the missing outputs.
    """
    metadata = collect_metadata(session_id=session_id, narrative=narrative)
    sid = metadata["session_id"]

    # Per-output idempotency checks
    report_exists = session_exists_in_report(sid, report_path)
    changelog_exists = (
        session_exists_in_changelog(sid, changelog_path) if changelog_path is not None else True
    )
    artifact_exists = (sessions_dir / f"{sid}.json").exists()

    if report_exists and changelog_exists and artifact_exists:
        logger.info("Session %s already in all outputs — skipping.", sid)
        return {"skipped": True, "session_id": sid}

    # Score
    score = compute_score(
        files_changed_count=metadata["files_changed_count"],
        lines_changed=metadata["lines_changed"],
        tests_touched_count=metadata["tests_touched_count"],
        security_findings=metadata["security_findings"],
        docs_changed=metadata["docs_changed"],
        commit_message=metadata["commit_message"],
    )

    # Tokenise
    tokens = tokenize_narrative(
        metadata["narrative"],
        modified_filenames=metadata["files_changed"],
    )

    # Markdown for accountability report
    entry = generate_markdown_entry(metadata, score, tokens)

    # Changelog entry
    changelog_entry = generate_changelog_entry(metadata, score)

    if dry_run:
        logger.info("--- DRY RUN: Generated accountability entry ---")
        logger.info(entry)
        logger.info("--- DRY RUN: Generated changelog entry ---")
        logger.info(changelog_entry)
        logger.info(f"--- Score: {score:.4f} | Tokens: {len(tokens)} ---")
        return {
            "dry_run": True,
            "session_id": sid,
            "score": score,
            "tokens": tokens,
            "entry": entry,
            "changelog_entry": changelog_entry,
            "metadata": metadata,
        }

    # Persist accountability report (skip if already present)
    if not report_exists:
        append_to_report(entry, report_path)

    # Persist CHANGELOG (skip if already present)
    changelog_updated = False
    if changelog_path is not None and not changelog_exists:
        changelog_updated = update_changelog(changelog_entry, changelog_path)

    # Persist JSON artifact (skip if already present)
    if not artifact_exists:
        artifact_path = write_session_artifact(metadata, score, tokens, sessions_dir)
    else:
        artifact_path = sessions_dir / f"{sid}.json"

    logger.info(
        "Session %s appended to report%s, artifact at %s (score=%.2f)",
        sid,
        " + CHANGELOG" if changelog_updated else "",
        artifact_path,
        score,
    )
    return {
        "session_id": sid,
        "score": score,
        "tokens": tokens,
        "artifact_path": str(artifact_path),
        "changelog_updated": changelog_updated,
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry-point for the accountability auto-update script."""
    parser = argparse.ArgumentParser(
        description="Append a scored session entry to the accountability report.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated entry without modifying any files.",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Write the entry to disk (report + JSON artifact).",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Explicit session ID (overrides CODEX_SESSION_ID).",
    )
    parser.add_argument(
        "--narrative",
        default=None,
        help="Session narrative / summary text.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    dry_run = args.dry_run or not args.commit

    try:
        result = run(
            session_id=args.session_id,
            narrative=args.narrative,
            dry_run=dry_run,
        )
    except (IOError, OSError):
        logger.exception("Accountability auto-update failed")
        return 1

    if result.get("skipped"):
        logger.info(f"Skipped: session {result['session_id']} already in report.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
