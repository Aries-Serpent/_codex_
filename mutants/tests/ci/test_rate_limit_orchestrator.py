from __future__ import annotations

from scripts.ci import rate_limit_orchestrator as orchestrator


def test_parse_args_keep_latest_defaults_true():
    args = orchestrator._parse_args(
        ["--deduplicate", "--workflow", "validate.yml", "--branch", "main"]
    )
    assert args.keep_latest is True, "keep_latest is not valid"


def test_cancel_superseded_runs_delegates(monkeypatch):
    captured = {}

    def fake_deduplicate(workflow_file, branch, repo, tokens, *, keep_latest=True, dry_run=False):
        captured.update(
            {
                "workflow_file": workflow_file,
                "branch": branch,
                "repo": repo,
                "tokens": tokens,
                "keep_latest": keep_latest,
                "dry_run": dry_run,
            }
        )
        return 3

    monkeypatch.setattr(orchestrator, "deduplicate_workflow", fake_deduplicate)
    cancelled = orchestrator.cancel_superseded_runs(
        "validate.yml",
        "main",
        "owner/repo",
        ["token"],
    )
    assert cancelled == 3, "cancelled is not valid"
    assert captured["keep_latest"] is True, "Condition must be true"
    assert captured["dry_run"] is False, "Condition must be true"
