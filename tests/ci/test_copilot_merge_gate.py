"""Focused tests for the read-only Copilot merge gate."""

from __future__ import annotations

import importlib

from scripts.ci import copilot_merge_gate as gate


def _pr(*, sha: str = "a" * 40, base: str = "main", head: str = "0D_base_") -> dict:
    return {
        "state": "open",
        "draft": False,
        "mergeable": True,
        "mergeable_state": "clean",
        "head": {"sha": sha, "ref": head},
        "base": {"ref": base, "sha": "b" * 40},
    }


def _ai_review(sha: str, login: str = "github-copilot[bot]") -> dict:
    return {
        "commit_id": sha,
        "state": "APPROVED",
        "user": {"login": login},
    }


def _passing_checks() -> list[dict]:
    return [
        {
            "name": "premerge-triage-gate / triage-gate",
            "status": "completed",
            "conclusion": "success",
        },
        {
            "name": "agentic-diff-guard / deterministic-diff-guard",
            "status": "completed",
            "conclusion": "success",
        },
    ]


def test_exact_sha_ai_review_accepts_only_bound_copilot_approval() -> None:
    sha = "c" * 40
    pr = _pr(sha=sha)

    assert gate.check_current_sha_ai_review(pr, [_ai_review(sha)], sha)["pass"]

    stale = _ai_review("d" * 40)
    stale_result = gate.check_current_sha_ai_review(pr, [stale], sha)
    assert stale_result["pass"] is False

    human = _ai_review(sha, login="mbaetiong")
    human_result = gate.check_current_sha_ai_review(pr, [human], sha)
    assert human_result["pass"] is False


def test_required_checks_fail_closed_for_pending_missing_or_failure() -> None:
    checks = _passing_checks()
    required = [check["name"] for check in checks]

    assert gate.check_required_checks(checks, required)["pass"] is True

    pending = [{**checks[0], "conclusion": None, "status": "in_progress"}, checks[1]]
    assert gate.check_required_checks(pending, required)["pass"] is False

    missing = gate.check_required_checks([checks[0]], required)
    assert missing["pass"] is False
    assert missing["missing"] == [required[1]]


def test_branch_freshness_rejects_behind_or_unknown() -> None:
    pr = _pr()

    assert gate.check_branch_freshness(pr, {"status": "identical", "behind_by": 0})["pass"]
    assert gate.check_branch_freshness(pr, {"status": "ahead", "behind_by": 0})["pass"]
    assert gate.check_branch_freshness(pr, {"status": "behind", "behind_by": 3})["pass"] is False
    assert gate.check_branch_freshness(pr, None)["pass"] is False


def test_merge_method_validation_is_allowlisted_and_repo_aware() -> None:
    assert gate.validate_merge_method("squash")["pass"]
    assert gate.validate_merge_method("merge")["pass"]
    assert gate.validate_merge_method("rebase")["pass"]
    assert gate.validate_merge_method("octopus")["pass"] is False
    assert gate.validate_merge_method("squash", {"allow_squash_merge": False})["pass"] is False


def test_sub_pr_and_promotion_readiness_use_branch_contract() -> None:
    sub_pr = _pr(base="0D_base_", head="copilot/sub-pr-123")
    assert gate.check_sub_pr_promotion_readiness(sub_pr, "sub_pr")["pass"]

    wrong_sub_pr = _pr(base="main", head="copilot/sub-pr-123")
    assert gate.check_sub_pr_promotion_readiness(wrong_sub_pr, "sub_pr")["pass"] is False

    promotion = _pr(base="main", head="0D_base_")
    assert gate.check_sub_pr_promotion_readiness(promotion, "promotion")["pass"]


def test_evaluate_merge_gate_is_read_only_and_fail_closed() -> None:
    sha = "e" * 40
    pr = _pr(sha=sha, base="main", head="0D_base_")
    report = gate.evaluate_merge_gate(
        pr,
        reviews=[_ai_review(sha)],
        check_rollup=_passing_checks(),
        compare={"status": "identical", "behind_by": 0, "ahead_by": 0},
        merge_method="squash",
        mode="promotion",
        sha=sha,
        required_checks=[check["name"] for check in _passing_checks()],
        execute=True,
    )

    assert report["ready"] is True
    assert report["execute_requested"] is True
    assert report["mode"] == "execute-read-only"
    assert report["mutations_attempted"] == []


def test_execute_mode_collector_never_calls_mutating_http_verb() -> None:
    sha = "f" * 40
    pr = _pr(sha=sha, base="main", head="0D_base_")
    calls: list[tuple[str, str, str]] = []

    def fake_get(repo: str, path: str, token: str) -> object:
        calls.append((repo, path, token))
        if "/pulls/42/reviews" in path:
            return [_ai_review(sha)]
        if "/commits/" in path and path.endswith("/check-runs?per_page=100"):
            return {"check_runs": _passing_checks()}
        if "/commits/" in path and path.endswith("/status"):
            return {"statuses": []}
        if "/compare/" in path:
            return {"status": "identical", "behind_by": 0, "ahead_by": 0}
        if "/pulls/42" in path:
            return pr
        return {}

    merge_gate = gate.CopilotMergeGate(
        repo="Aries-Serpent/_codex_",
        pr=42,
        token="test-token",
        merge_method="squash",
        mode="promotion",
        required_checks=[check["name"] for check in _passing_checks()],
        execute=True,
        http_get=fake_get,
    )
    report = merge_gate.evaluate()

    assert report["ready"] is True
    assert report["mutations_attempted"] == []
    assert all("/merge" not in path for _, path, _ in calls)


def test_module_reload_does_not_create_mutation_side_effects() -> None:
    reloaded = importlib.reload(gate)
    assert callable(reloaded.evaluate_merge_gate)
    assert reloaded.MERGE_METHODS == gate.MERGE_METHODS
