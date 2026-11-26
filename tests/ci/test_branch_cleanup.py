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
