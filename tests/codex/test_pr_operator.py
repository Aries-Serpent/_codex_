"""Tests for src/codex/cli/pr_operator.py — Phase 2 coverage gap-fill.

Covers _sanitize_branch_name, _generate_pr_body, PRConfig, PRContent,
PRResult, and PROperator (generate_pr_content, create_pr, save_pr_content).

Note: This module does NOT require omegaconf/hydra; it tests pure-Python
      PR pipeline logic only.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.cli.pr_operator import (  # pragma: allowlist secret
    DEFAULT_LABELS,
    PRConfig,
    PRContent,
    PROperator,  # pragma: allowlist secret
    PRResult,
    _generate_pr_body,
    _sanitize_branch_name,
)

# ---------------------------------------------------------------------------
# _sanitize_branch_name
# ---------------------------------------------------------------------------


class TestSanitizeBranchName:
    def test_clean_name_unchanged(self) -> None:
        assert _sanitize_branch_name("feature/my-branch") == "feature/my-branch"

    def test_spaces_replaced(self) -> None:
        result = _sanitize_branch_name("my branch name")
        assert " " not in result

    def test_special_chars_replaced(self) -> None:
        result = _sanitize_branch_name("fix: typo in README!")
        assert ":" not in result
        assert "!" not in result

    def test_consecutive_dashes_collapsed(self) -> None:
        result = _sanitize_branch_name("fix---multiple---dashes")
        assert "--" not in result

    def test_leading_trailing_dashes_stripped(self) -> None:
        result = _sanitize_branch_name("--my-branch--")
        assert not result.startswith("-")
        assert not result.endswith("-")

    def test_length_capped_at_100(self) -> None:
        long_name = "a" * 200
        result = _sanitize_branch_name(long_name)
        assert len(result) <= 100

    def test_empty_string(self) -> None:
        result = _sanitize_branch_name("")
        assert isinstance(result, str)

    def test_alphanumeric_unchanged(self) -> None:
        assert _sanitize_branch_name("abc123") == "abc123"

    def test_forward_slash_preserved(self) -> None:
        result = _sanitize_branch_name("codex/refactor-abc")
        assert "/" in result

    def test_unicode_replaced(self) -> None:
        result = _sanitize_branch_name("fix-cëñtral")
        # Characters outside a-zA-Z0-9/_- must not remain
        for ch in result:
            assert ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_-"


# ---------------------------------------------------------------------------
# _generate_pr_body
# ---------------------------------------------------------------------------


class TestGeneratePRBody:
    @pytest.fixture()
    def body(self) -> str:
        return _generate_pr_body(
            snapshot_id="snap-001",
            intent_summary="Improve type annotations",
            confidence=0.92,
            tier_a_count=5,
            tier_b_count=3,
            tier_c_count=2,
            verification_result="pass",
            security_issues=0,
        )

    def test_contains_snapshot_id(self, body: str) -> None:
        assert "snap-001" in body

    def test_contains_intent_summary(self, body: str) -> None:
        assert "Improve type annotations" in body

    def test_confidence_formatted_as_percentage(self, body: str) -> None:
        assert "92%" in body

    def test_tier_counts_present(self, body: str) -> None:
        assert "5" in body
        assert "3" in body
        assert "2" in body

    def test_pass_verification_shows_checkmark(self, body: str) -> None:
        assert "✅" in body

    def test_fail_verification_shows_cross(self) -> None:
        body = _generate_pr_body(
            snapshot_id="s",
            intent_summary="x",
            confidence=0.5,
            tier_a_count=0,
            tier_b_count=0,
            tier_c_count=0,
            verification_result="fail",
            security_issues=0,
        )
        assert "❌" in body

    def test_no_security_issues_shows_ok(self, body: str) -> None:
        # 0 security issues → ✅ icon in the security row
        assert "0 finding(s)" in body

    def test_many_security_issues_shows_critical_icon(self) -> None:
        body = _generate_pr_body(
            snapshot_id="s",
            intent_summary="x",
            confidence=0.5,
            tier_a_count=0,
            tier_b_count=0,
            tier_c_count=0,
            verification_result="pass",
            security_issues=5,
        )
        assert "❌" in body

    def test_returns_string(self, body: str) -> None:
        assert isinstance(body, str)
        assert len(body) > 50


# ---------------------------------------------------------------------------
# PRConfig
# ---------------------------------------------------------------------------


class TestPRConfig:
    def test_defaults(self) -> None:
        cfg = PRConfig(owner="org", repo="myrepo")
        assert cfg.base_branch == "main"
        assert cfg.draft is True
        assert cfg.labels == DEFAULT_LABELS
        assert cfg.assignees == []

    def test_custom_values(self) -> None:
        cfg = PRConfig(
            owner="acme",
            repo="proj",
            base_branch="develop",
            draft=False,
            labels=["bugfix"],
            assignees=["alice"],
        )
        assert cfg.base_branch == "develop"
        assert cfg.draft is False
        assert cfg.labels == ["bugfix"]
        assert cfg.assignees == ["alice"]


# ---------------------------------------------------------------------------
# PRContent
# ---------------------------------------------------------------------------


class TestPRContent:
    def test_construction(self) -> None:
        content = PRContent(
            title="Fix typos",
            body="## Summary\nFixed.",
            branch_name="codex/fix-typos",
        )
        assert content.title == "Fix typos"
        assert content.files_changed == []
        assert content.snapshot_id is None

    def test_with_snapshot(self) -> None:
        content = PRContent(
            title="Refactor",
            body="body",
            branch_name="codex/refactor",
            snapshot_id="snap-xyz",
            files_changed=["src/main.py"],
        )
        assert content.snapshot_id == "snap-xyz"
        assert len(content.files_changed) == 1


# ---------------------------------------------------------------------------
# PRResult
# ---------------------------------------------------------------------------


class TestPRResult:
    def test_success_result(self) -> None:
        result = PRResult(success=True, pr_number=42, pr_url="https://github.com/o/r/pull/42")
        assert result.success is True
        assert result.pr_number == 42
        assert result.errors == []

    def test_failure_result(self) -> None:
        result = PRResult(success=False, errors=["GitHub client not available."])
        assert result.success is False
        assert result.pr_number is None
        assert len(result.errors) == 1


# ---------------------------------------------------------------------------
# PROperator
# ---------------------------------------------------------------------------


class TestPROperatorGeneratePRContent:
    @pytest.fixture()
    def operator(self) -> PROperator:
        return PROperator(PRConfig(owner="org", repo="repo"))

    def test_returns_pr_content(self, operator: PROperator) -> None:
        content = operator.generate_pr_content(
            snapshot_id="snap-abc",
            intent_summary="Improve coverage",
            confidence=0.88,
        )
        assert isinstance(content, PRContent)

    def test_branch_name_contains_snapshot(self, operator: PROperator) -> None:
        content = operator.generate_pr_content(
            snapshot_id="snap-abc",
            intent_summary="Fix",
            confidence=0.9,
        )
        assert "snap-abc" in content.branch_name

    def test_title_uses_intent(self, operator: PROperator) -> None:
        content = operator.generate_pr_content(
            snapshot_id="snap-def",
            intent_summary="Reduce cyclomatic complexity",
            confidence=0.75,
        )
        assert "Reduce cyclomatic complexity" in content.title

    def test_long_intent_truncated_in_title(self, operator: PROperator) -> None:
        long_intent = "A" * 100
        content = operator.generate_pr_content(
            snapshot_id="snap-long",
            intent_summary=long_intent,
            confidence=0.7,
        )
        # Title must be reasonable length
        assert len(content.title) < 200

    def test_body_is_non_empty(self, operator: PROperator) -> None:
        content = operator.generate_pr_content(
            snapshot_id="snap-xyz",
            intent_summary="Test",
            confidence=0.5,
            tier_a_count=1,
            tier_b_count=2,
            tier_c_count=3,
        )
        assert len(content.body) > 10

    def test_snapshot_id_stored(self, operator: PROperator) -> None:
        content = operator.generate_pr_content(
            snapshot_id="snap-stored",
            intent_summary="Fix",
            confidence=0.9,
        )
        assert content.snapshot_id == "snap-stored"


class TestPROperatorCreatePRWithoutGitHub:
    """create_pr returns a failure gracefully when no GitHub token is set."""

    @pytest.fixture()
    def operator(self, monkeypatch) -> PROperator:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        return PROperator(PRConfig(owner="org", repo="repo"))

    def test_create_pr_fails_gracefully(self, operator: PROperator) -> None:
        content = PRContent(
            title="Test PR",
            body="body",
            branch_name="codex/test-pr",
        )
        result = operator.create_pr(content)
        assert isinstance(result, PRResult)
        assert result.success is False
        assert len(result.errors) >= 1


class TestPROperatorSavePRContent:
    @pytest.fixture()
    def operator(self) -> PROperator:
        return PROperator(PRConfig(owner="org", repo="repo"))

    def test_saves_pr_description_file(self, operator: PROperator, tmp_path: Path) -> None:
        content = PRContent(
            title="My PR",
            body="## Body",
            branch_name="codex/save-test",
            snapshot_id="snap-save",
        )
        result_path = operator.save_pr_content(content, tmp_path / "out")
        assert result_path.exists()
        assert result_path.name == "pr-description.md"

    def test_saved_description_contains_title(
        self, operator: PROperator, tmp_path: Path
    ) -> None:
        content = PRContent(
            title="Coverage Improvements",
            body="body",
            branch_name="codex/cov",
            snapshot_id="snap-001",
        )
        result_path = operator.save_pr_content(content, tmp_path / "out")
        text = result_path.read_text(encoding="utf-8")
        assert "Coverage Improvements" in text

    def test_saves_metadata_json(self, operator: PROperator, tmp_path: Path) -> None:
        out_dir = tmp_path / "out"
        content = PRContent(
            title="Refactor",
            body="body",
            branch_name="codex/refactor",
            snapshot_id="snap-meta",
        )
        operator.save_pr_content(content, out_dir)
        meta_file = out_dir / "pr-metadata.json"
        assert meta_file.exists()
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        assert meta["title"] == "Refactor"
        assert meta["snapshot_id"] == "snap-meta"
