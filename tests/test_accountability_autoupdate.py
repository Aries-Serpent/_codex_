"""
Tests for the accountability report & CHANGELOG auto-update feature.

Covers:
- Significance scoring (deterministic, bounded)
- Narrative tokenisation & weighting
- Markdown entry generation (template compliance, SessionID presence)
- Idempotency (duplicate session IDs are skipped)
- CHANGELOG update (entry inserted under [Unreleased])
- Integration: end-to-end simulated session close
"""

from __future__ import annotations

import json

import pytest
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
from codex.session.accountability_autoupdate import (
    append_to_report,
    collect_metadata,
    compute_score,
    generate_changelog_entry,
    generate_markdown_entry,
    run,
    session_exists_in_changelog,
    session_exists_in_report,
    tokenize_narrative,
    update_changelog,
    write_session_artifact,
)

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


class TestComputeScore:

    def test_zero_input_returns_zero(self):
        score = compute_score(0, 0, 0, False, False, "")
        assert score == 0.0

    def test_max_input_capped_at_one(self):
        score = compute_score(100, 100_000, 100, True, True, "hotfix critical")
        assert score <= 1.0

    def test_score_increases_with_files(self):
        low = compute_score(1, 0, 0, False, False, "")
        high = compute_score(10, 0, 0, False, False, "")
        assert high > low

    def test_score_increases_with_lines(self):
        low = compute_score(0, 10, 0, False, False, "")
        high = compute_score(0, 500, 0, False, False, "")
        assert high > low

    def test_hotfix_keyword_boosts_score(self):
        without = compute_score(5, 200, 5, False, False, "update feature")
        with_fix = compute_score(5, 200, 5, False, False, "fix: broken login")
        assert with_fix > without

    def test_security_findings_boost(self):
        without = compute_score(5, 200, 5, False, False, "chore")
        with_sec = compute_score(5, 200, 5, True, False, "chore")
        assert with_sec > without

    def test_docs_boost(self):
        without = compute_score(5, 200, 5, False, False, "chore")
        with_doc = compute_score(5, 200, 5, False, True, "chore")
        assert with_doc > without

    def test_deterministic(self):
        """Same inputs always produce the same score."""
        a = compute_score(3, 150, 2, False, True, "fix: minor")
        b = compute_score(3, 150, 2, False, True, "fix: minor")
        assert a == b

    def test_score_in_range(self):
        """Score is always in [0, 1]."""
        for files in (0, 5, 50):
            for lines in (0, 100, 10000):
                for tests in (0, 10, 100):
                    s = compute_score(files, lines, tests, True, True, "hotfix")
                    assert 0.0 <= s <= 1.0


# ---------------------------------------------------------------------------
# Tokenisation
# ---------------------------------------------------------------------------


class TestTokenizeNarrative:

    def test_basic_tokenisation(self):
        tokens = tokenize_narrative("Fixed the login bug. Updated tests.")
        names = [t["token"] for t in tokens]
        assert "fixed" in names
        assert "login" in names
        assert "bug" in names

    def test_stopwords_removed(self):
        tokens = tokenize_narrative("The quick brown fox is a test of the module.")
        names = [t["token"] for t in tokens]
        assert "the" not in names
        assert "is" not in names
        assert "a" not in names

    def test_weights_sum_to_one(self):
        tokens = tokenize_narrative("Auth module refactored. MFA tests added.")
        if tokens:
            total = sum(t["weight"] for t in tokens)
            assert abs(total - 1.0) < 0.01

    def test_filename_boost(self):
        tokens_without = tokenize_narrative("Updated auth module", modified_filenames=[])
        tokens_with = tokenize_narrative(
            "Updated auth module", modified_filenames=["src/auth/module.py"]
        )
        # 'auth' should have a higher weight when it's in filenames
        w_without = {t["token"]: t["weight"] for t in tokens_without}
        w_with = {t["token"]: t["weight"] for t in tokens_with}
        assert w_with.get("auth", 0) >= w_without.get("auth", 0)

    def test_empty_narrative(self):
        assert tokenize_narrative("") == []

    def test_sorted_by_weight_descending(self):
        tokens = tokenize_narrative("One two three four. Five six seven eight.")
        weights = [t["weight"] for t in tokens]
        assert weights == sorted(weights, reverse=True)


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------


class TestGenerateMarkdownEntry:

    @pytest.fixture()
    def sample_metadata(self):
        return {
            "session_id": "test-session-123",
            "author": "copilot-agent",
            "commit_sha": "abc1234567890",
            "timestamp": "2026-03-13T04:00:00+00:00",
            "files_changed": ["src/auth/routes.py", "tests/test_auth.py"],
            "files_changed_count": 2,
            "lines_added": 150,
            "lines_removed": 30,
            "tests_touched_count": 1,
            "narrative": "Added auth endpoints and rate limiting.",
            "docs_changed": False,
            "security_findings": False,
            "commit_message": "feat: add auth endpoints",
            "run_id": None,
            "repo": "Aries-Serpent/_codex_",
        }

    def test_contains_session_id(self, sample_metadata):
        tokens = [{"token": "auth", "weight": 0.7}, {"token": "rate", "weight": 0.3}]
        entry = generate_markdown_entry(sample_metadata, 0.45, tokens)
        assert "SessionID: test-session-123" in entry

    def test_contains_commit_sha(self, sample_metadata):
        tokens = [{"token": "auth", "weight": 1.0}]
        entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
        assert "abc1234567" in entry

    def test_contains_metrics_table(self, sample_metadata):
        tokens = [{"token": "auth", "weight": 1.0}]
        entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
        assert "| Files changed | 2 |" in entry
        assert "| Lines added | +150 |" in entry
        assert "| Lines removed | -30 |" in entry

    def test_contains_significance_score(self, sample_metadata):
        tokens = [{"token": "auth", "weight": 1.0}]
        entry = generate_markdown_entry(sample_metadata, 0.72, tokens)
        assert "0.72" in entry

    def test_ends_with_separator(self, sample_metadata):
        tokens = [{"token": "auth", "weight": 1.0}]
        entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
        assert entry.strip().endswith("---")

    def test_contains_tokenized_narrative_json(self, sample_metadata):
        tokens = [{"token": "auth", "weight": 0.8}, {"token": "rate", "weight": 0.2}]
        entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
        assert "```json" in entry

    def test_lists_modified_files(self, sample_metadata):
        tokens = [{"token": "auth", "weight": 1.0}]
        entry = generate_markdown_entry(sample_metadata, 0.5, tokens)
        assert "src/auth/routes.py" in entry
        assert "tests/test_auth.py" in entry


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


class TestIdempotency:

    def test_session_exists_returns_false_for_missing_file(self, tmp_path):
        assert session_exists_in_report("xyz", tmp_path / "missing.md") is False

    def test_session_exists_returns_false_when_not_present(self, tmp_path):
        report = tmp_path / "report.md"
        report.write_text("# Report\nSome content\n", encoding="utf-8")
        assert session_exists_in_report("new-session", report) is False

    def test_session_exists_returns_true_when_present(self, tmp_path):
        report = tmp_path / "report.md"
        report.write_text(
            "# Report\n> SessionID: existing-session\n",
            encoding="utf-8",
        )
        assert session_exists_in_report("existing-session", report) is True

    def test_duplicate_append_skipped(self, tmp_path):
        """Running twice with the same session ID should not duplicate."""
        report = tmp_path / "report.md"
        sessions = tmp_path / "sessions"
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## [Unreleased]\n\n## [1.0.0]\n", encoding="utf-8")

        result1 = run(
            session_id="idempotent-test",
            narrative="First run.",
            dry_run=False,
            report_path=report,
            changelog_path=changelog,
            sessions_dir=sessions,
        )
        assert result1.get("session_id") == "idempotent-test"

        result2 = run(
            session_id="idempotent-test",
            narrative="Second run.",
            dry_run=False,
            report_path=report,
            changelog_path=changelog,
            sessions_dir=sessions,
        )
        assert result2.get("skipped") is True

        # Verify only one occurrence
        content = report.read_text(encoding="utf-8")
        assert content.count("SessionID: idempotent-test") == 1


# ---------------------------------------------------------------------------
# Append & artifact write
# ---------------------------------------------------------------------------


class TestAppendToReport:

    def test_creates_file_if_missing(self, tmp_path):
        report = tmp_path / "subdir" / "report.md"
        append_to_report("## New entry\n---\n", report)
        assert report.exists()
        content = report.read_text(encoding="utf-8")
        assert "New entry" in content

    def test_appends_to_existing(self, tmp_path):
        report = tmp_path / "report.md"
        report.write_text("# Header\n\nExisting content\n", encoding="utf-8")
        append_to_report("## Appended\n---\n", report)
        content = report.read_text(encoding="utf-8")
        assert "Existing content" in content
        assert "Appended" in content


class TestWriteSessionArtifact:

    def test_creates_json_file(self, tmp_path):
        metadata = {
            "session_id": "art-test",
            "author": "agent",
            "commit_sha": "abc123",
            "timestamp": "2026-03-13T00:00:00Z",
            "files_changed": ["a.py"],
            "lines_added": 10,
            "lines_removed": 2,
            "tests_touched_count": 1,
            "narrative": "test narrative",
            "repo": "test/repo",
            "run_id": None,
        }
        tokens = [{"token": "test", "weight": 1.0}]
        path = write_session_artifact(metadata, 0.5, tokens, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["session_id"] == "art-test"
        assert data["score"] == 0.5
        assert len(data["tokens"]) == 1


# ---------------------------------------------------------------------------
# Integration: full run
# ---------------------------------------------------------------------------


class TestIntegrationRun:

    def test_dry_run_returns_entry(self):
        result = run(
            session_id="dry-test",
            narrative="Integration test dry run.",
            dry_run=True,
        )
        assert result.get("dry_run") is True
        assert "dry-test" in result["entry"]
        assert result["score"] >= 0.0

    def test_full_run_creates_files(self, tmp_path):
        report = tmp_path / "report.md"
        sessions = tmp_path / "sessions"

        result = run(
            session_id="full-test",
            narrative="Full integration test.",
            dry_run=False,
            report_path=report,
            changelog_path=None,
            sessions_dir=sessions,
        )
        assert result["session_id"] == "full-test"
        assert report.exists()
        assert (sessions / "full-test.json").exists()

        # Verify report content
        content = report.read_text(encoding="utf-8")
        assert "SessionID: full-test" in content
        assert "Significance score" in content

        # Verify JSON artifact
        artifact = json.loads((sessions / "full-test.json").read_text(encoding="utf-8"))
        assert artifact["session_id"] == "full-test"
        assert 0.0 <= artifact["score"] <= 1.0

    def test_full_run_updates_changelog(self, tmp_path):
        """Full run should also insert an entry under [Unreleased] in CHANGELOG."""
        report = tmp_path / "report.md"
        sessions = tmp_path / "sessions"
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n## [1.0.0]\n- old entry\n",
            encoding="utf-8",
        )

        result = run(
            session_id="cl-test",
            narrative="feat: add auth module",
            dry_run=False,
            report_path=report,
            changelog_path=changelog,
            sessions_dir=sessions,
        )
        assert result["changelog_updated"] is True

        cl_content = changelog.read_text(encoding="utf-8")
        assert "session cl-test" in cl_content
        assert "## [Unreleased]" in cl_content
        # Old entry should still be there
        assert "old entry" in cl_content

    def test_dry_run_includes_changelog_preview(self):
        result = run(
            session_id="dry-cl",
            narrative="feat: preview test",
            dry_run=True,
        )
        assert result.get("dry_run") is True
        assert "changelog_entry" in result
        assert "session dry-cl" in result["changelog_entry"]

    def test_metadata_collection(self):
        meta = collect_metadata(session_id="meta-test", narrative="Test narrative.")
        assert meta["session_id"] == "meta-test"
        assert meta["narrative"] == "Test narrative."
        assert isinstance(meta["files_changed"], list)
        assert isinstance(meta["lines_added"], int)


# ---------------------------------------------------------------------------
# CHANGELOG
# ---------------------------------------------------------------------------


class TestChangelogGeneration:

    @pytest.fixture()
    def sample_metadata(self):
        return {
            "session_id": "cl-gen-test",
            "author": "copilot-agent",
            "commit_sha": "abc1234567890",
            "timestamp": "2026-03-13T04:00:00+00:00",
            "files_changed": ["src/auth/routes.py", "tests/test_auth.py"],
            "files_changed_count": 2,
            "lines_added": 150,
            "lines_removed": 30,
            "tests_touched_count": 1,
            "narrative": "Added auth endpoints and rate limiting.",
            "docs_changed": False,
            "security_findings": False,
            "commit_message": "feat: add auth endpoints",
        }

    def test_generate_changelog_entry_contains_session_id(self, sample_metadata):
        entry = generate_changelog_entry(sample_metadata, 0.45)
        assert "cl-gen-t" in entry  # first 8 chars

    def test_generate_changelog_entry_has_category(self, sample_metadata):
        entry = generate_changelog_entry(sample_metadata, 0.45)
        # commit message starts with 'feat' → Added
        assert "### Added" in entry

    def test_fix_commit_produces_fixed_category(self, sample_metadata):
        sample_metadata["commit_message"] = "fix: broken login"
        entry = generate_changelog_entry(sample_metadata, 0.45)
        assert "### Fixed" in entry

    def test_generic_commit_produces_changed_category(self, sample_metadata):
        sample_metadata["commit_message"] = "chore: update deps"
        entry = generate_changelog_entry(sample_metadata, 0.45)
        assert "### Changed" in entry

    def test_lists_modified_files(self, sample_metadata):
        entry = generate_changelog_entry(sample_metadata, 0.45)
        assert "src/auth/routes.py" in entry

    def test_truncates_long_file_lists(self, sample_metadata):
        sample_metadata["files_changed"] = [f"file{i}.py" for i in range(10)]
        entry = generate_changelog_entry(sample_metadata, 0.45)
        assert "… and 5 more files" in entry


class TestChangelogUpdate:

    def test_insert_after_unreleased_marker(self, tmp_path):
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n## [1.0.0]\n- old\n",
            encoding="utf-8",
        )
        result = update_changelog(
            "\n### Added (session abc — 2026-03-13)\n- new feature\n",
            changelog,
        )
        assert result is True
        content = changelog.read_text(encoding="utf-8")
        assert "new feature" in content
        assert content.index("new feature") < content.index("## [1.0.0]")

    def test_returns_false_when_no_unreleased(self, tmp_path):
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## [1.0.0]\n", encoding="utf-8")
        result = update_changelog("### Added\n- entry\n", changelog)
        assert result is False

    def test_returns_false_when_file_missing(self, tmp_path):
        result = update_changelog("### Added\n", tmp_path / "missing.md")
        assert result is False

    def test_session_exists_in_changelog(self, tmp_path):
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added (session abcdef12)\n- entry\n",
            encoding="utf-8",
        )
        assert session_exists_in_changelog("abcdef1234567890", changelog) is True
        assert session_exists_in_changelog("zzzzzzzzz", changelog) is False

    def test_preserves_existing_content(self, tmp_path):
        changelog = tmp_path / "CHANGELOG.md"
        original = (
            "# Changelog\n\n## [Unreleased]\n\n"
            "### Fixed\n- existing fix\n\n## [1.0.0]\n- v1 entry\n"
        )
        changelog.write_text(original, encoding="utf-8")
        update_changelog("\n### Added (session test)\n- new\n", changelog)
        content = changelog.read_text(encoding="utf-8")
        assert "existing fix" in content
        assert "v1 entry" in content
        assert "new" in content
