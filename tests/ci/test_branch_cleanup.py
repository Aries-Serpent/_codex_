from __future__ import annotations

from datetime import datetime, timezone

from scripts.ci import branch_cleanup


def test_classify_uses_explicit_integration_base(monkeypatch) -> None:
    def is_branch_merged(repo: str, token: str, branch: str, base: str) -> bool:
        assert repo == "Aries-Serpent/_codex_"
        assert branch == "copilot/merged-work"
        assert base == "0D_base_"
        return True

    monkeypatch.setattr(branch_cleanup, "is_branch_merged", is_branch_merged)
    monkeypatch.setattr(branch_cleanup, "find_open_pr", lambda *_: None)
    monkeypatch.setattr(
        branch_cleanup,
        "get_branch_last_commit_date",
        lambda *_: datetime(2026, 11, 25, tzinfo=timezone.utc),
    )

    result = branch_cleanup.classify_branches(
        repo="Aries-Serpent/_codex_",
        token="token",
        default_branch="main",
        branches=[{"name": "copilot/merged-work"}],
        stale_days=30,
        very_stale_days=90,
        target_prefixes=["copilot/"],
        delete_merged=True,
        delete_stale=False,
        delete_by_prefix=False,
        force_prefix=False,
        base_branch="0D_base_",
    )

    assert [branch["name"] for branch in result["to_delete"]] == ["copilot/merged-work"]
    assert result["to_delete"][0]["reason"] == ("fully merged into integration branch '0D_base_'")


def test_classify_preserves_branch_with_open_pr(monkeypatch) -> None:
    monkeypatch.setattr(branch_cleanup, "is_branch_merged", lambda *_: True)
    monkeypatch.setattr(branch_cleanup, "find_open_pr", lambda *_: 5855)
    monkeypatch.setattr(
        branch_cleanup,
        "get_branch_last_commit_date",
        lambda *_: datetime(2026, 11, 25, tzinfo=timezone.utc),
    )

    result = branch_cleanup.classify_branches(
        repo="Aries-Serpent/_codex_",
        token="token",
        default_branch="main",
        branches=[{"name": "copilot/active-pr"}],
        stale_days=30,
        very_stale_days=90,
        target_prefixes=["copilot/"],
        delete_merged=True,
        delete_stale=False,
        delete_by_prefix=False,
        force_prefix=False,
        base_branch="0D_base_",
    )

    assert result["to_delete"] == []
    assert result["protected"] == [
        {
            "name": "copilot/active-pr",
            "reason": "open PR #5855",
            "merged": True,
            "days_since_commit": 1,
            "has_target_prefix": True,
            "pr_number": 5855,
        }
    ]


def test_execute_cleanup_refuses_branch_with_open_pr(monkeypatch) -> None:
    monkeypatch.setattr(
        branch_cleanup,
        "close_pr",
        lambda *_: (_ for _ in ()).throw(AssertionError("must not close active PR")),
    )
    monkeypatch.setattr(
        branch_cleanup,
        "delete_branch",
        lambda *_: (_ for _ in ()).throw(AssertionError("must not delete active branch")),
    )

    deleted, errors = branch_cleanup.execute_cleanup(
        repo="Aries-Serpent/_codex_",
        token="token",
        to_delete=[
            {
                "name": "copilot/active-pr",
                "pr_number": 5855,
                "reason": "supplied by caller",
            }
        ],
        dry_run=False,
    )

    assert deleted == 0
    assert errors == 1


def test_classify_preserves_branch_when_pr_state_is_unknown(monkeypatch) -> None:
    monkeypatch.setattr(branch_cleanup, "is_branch_merged", lambda *_: True)
    monkeypatch.setattr(
        branch_cleanup,
        "find_open_pr",
        lambda *_: (_ for _ in ()).throw(RuntimeError("rate limited")),
    )
    monkeypatch.setattr(
        branch_cleanup,
        "get_branch_last_commit_date",
        lambda *_: datetime(2026, 11, 25, tzinfo=timezone.utc),
    )

    result = branch_cleanup.classify_branches(
        repo="Aries-Serpent/_codex_",
        token="token",
        default_branch="main",
        branches=[{"name": "copilot/unknown-pr"}],
        stale_days=30,
        very_stale_days=90,
        target_prefixes=["copilot/"],
        delete_merged=True,
        delete_stale=False,
        delete_by_prefix=False,
        force_prefix=False,
        base_branch="0D_base_",
    )

    assert result["to_delete"] == []
    assert result["protected"][0]["reason"] == "open PR state unknown"


def test_classify_never_deletes_unmerged_stale_branch(monkeypatch) -> None:
    monkeypatch.setattr(branch_cleanup, "is_branch_merged", lambda *_: False)
    monkeypatch.setattr(branch_cleanup, "find_open_pr", lambda *_: None)
    monkeypatch.setattr(
        branch_cleanup,
        "get_branch_last_commit_date",
        lambda *_: datetime(2020, 1, 1, tzinfo=timezone.utc),
    )

    result = branch_cleanup.classify_branches(
        repo="Aries-Serpent/_codex_",
        token="token",
        default_branch="main",
        branches=[{"name": "copilot/old-work"}],
        stale_days=30,
        very_stale_days=90,
        target_prefixes=["copilot/"],
        delete_merged=False,
        delete_stale=True,
        delete_by_prefix=False,
        force_prefix=False,
        base_branch="0D_base_",
    )

    assert result["to_delete"] == []
    assert result["stale_warn"][0]["name"] == "copilot/old-work"


def test_execute_cleanup_rechecks_open_pr_state(monkeypatch) -> None:
    monkeypatch.setattr(branch_cleanup, "find_open_pr", lambda *_: 5867)
    monkeypatch.setattr(
        branch_cleanup,
        "delete_branch",
        lambda *_: (_ for _ in ()).throw(AssertionError("must recheck active PR")),
    )

    deleted, errors = branch_cleanup.execute_cleanup(
        repo="Aries-Serpent/_codex_",
        token="token",
        to_delete=[{"name": "copilot/new-pr", "pr_number": None}],
        dry_run=False,
    )

    assert deleted == 0
    assert errors == 1


def test_classify_preserves_branch_when_compare_state_is_unknown(monkeypatch) -> None:
    monkeypatch.setattr(
        branch_cleanup,
        "is_branch_merged",
        lambda *_: (_ for _ in ()).throw(branch_cleanup.BranchCleanupLookupError("403")),
    )
    monkeypatch.setattr(
        branch_cleanup,
        "get_branch_last_commit_date",
        lambda *_: datetime(2026, 11, 25, tzinfo=timezone.utc),
    )

    result = branch_cleanup.classify_branches(
        repo="Aries-Serpent/_codex_",
        token="token",
        default_branch="main",
        branches=[{"name": "copilot/unknown-merge"}],
        stale_days=30,
        very_stale_days=90,
        target_prefixes=["copilot/"],
        delete_merged=True,
        delete_stale=False,
        delete_by_prefix=False,
        force_prefix=False,
        base_branch="0D_base_",
    )

    assert result["to_delete"] == []
    assert result["protected"][0]["reason"] == "merge state unknown"


def test_validate_integration_branch_requires_fetched_ref() -> None:
    assert branch_cleanup.validate_integration_branch(
        [{"name": "main"}, {"name": "0D_base_"}], "0D_base_"
    )
    assert not branch_cleanup.validate_integration_branch([{"name": "main"}], "0D_base_")


def test_compare_lookup_failure_is_not_treated_as_unmerged(monkeypatch) -> None:
    monkeypatch.setattr(branch_cleanup, "gh_api", lambda *_: None)

    try:
        branch_cleanup.is_branch_merged(
            "Aries-Serpent/_codex_", "token", "copilot/work", "0D_base_"
        )
    except branch_cleanup.BranchCleanupLookupError:
        pass
    else:
        raise AssertionError("unavailable compare state must raise")


def test_open_pr_lookup_failure_is_not_treated_as_empty(monkeypatch) -> None:
    monkeypatch.setattr(branch_cleanup, "gh_api", lambda *_: {"message": "rate limited"})

    try:
        branch_cleanup.find_open_pr("Aries-Serpent/_codex_", "token", "copilot/work")
    except branch_cleanup.BranchCleanupLookupError:
        pass
    else:
        raise AssertionError("unavailable PR state must raise")
